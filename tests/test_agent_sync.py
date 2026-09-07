"""지침 동기화의 외부 동작: 보존, 이식, 읽기 전용, 충돌 중단."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BIN = Path(__file__).resolve().parents[1] / 'bin'
sys.path.insert(0, str(BIN))
from agent_sync import SyncError, build_bundle, load_manifest, sync_target


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'instructions').mkdir()
        self.common = self.source / 'instructions/common.md'
        self.common.write_text('# 공통\n\n[문서](documentation.md)를 읽는다.\n')
        (self.source / 'instructions/documentation.md').write_text(
            '# 문서\n\n```markdown\n## 가짜 절\n[예시](missing.md)\n```\n'
            '~~~~markdown\n# 또 다른 예시\n[예시](another.md)\n~~~~\n')
        self.manifest_path = self.source / 'sync-targets.json'
        self.data = {
            'schema_version': 1, 'source_repository': 'example/knowledge',
            'profiles': {'common': {
                'blocks': ['instructions/common.md'],
                'files': ['instructions/documentation.md']}},
            'targets': [{'id': 'demo', 'path': 'demo', 'repository': 'example/demo',
                         'default_branch': 'main', 'profile': 'common', 'ci': True}]}
        self.write_manifest()
        self.target = self.root / 'demo'
        self.target.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        self.original = '# 프로젝트\r\n\r\n사용자 규칙은 그대로.\r\n'
        (self.target / 'AGENTS.md').write_bytes(self.original.encode())
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        self.backups = self.root / 'backups'

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.target), *args],
                              check=True, capture_output=True, text=True).stdout

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.data))

    def bundle(self):
        manifest = load_manifest(self.manifest_path)
        return build_bundle(self.source, manifest, manifest['targets'][0])

    def sync(self, check=False):
        return sync_target(self.target, self.bundle(), check=check, backup_root=self.backups)

    def snapshot(self):
        return {str(p.relative_to(self.target)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.target.rglob('*') if p.is_file() and '.git' not in p.parts}

    def test_check_is_read_only_and_reports_drift(self):
        before = self.snapshot()
        result = self.sync(check=True)
        self.assertIn('AGENTS.md', result['changed'])
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.backups.exists())

    def test_apply_preserves_body_modes_and_is_idempotent(self):
        os.chmod(self.target / 'AGENTS.md', 0o640)
        first = self.sync()
        text = (self.target / 'AGENTS.md').read_bytes()
        self.assertIn(self.original.split('\r\n', 1)[1].encode(), text)
        self.assertEqual(0o640, (self.target / 'AGENTS.md').stat().st_mode & 0o777)
        self.assertEqual('@AGENTS.md\n', (self.target / 'CLAUDE.md').read_text())
        self.assertTrue(Path(first['backup']).is_dir())
        before = self.snapshot()
        self.assertEqual([], self.sync()['changed'])
        self.assertEqual([], self.sync(check=True)['changed'])
        self.assertEqual(before, self.snapshot())

    def test_existing_claude_content_is_preserved(self):
        p = self.target / 'CLAUDE.md'
        p.write_text('# Claude\n특별 규칙\n')
        self.git('add', 'CLAUDE.md')
        self.git('commit', '-qm', 'claude')
        self.sync()
        self.assertEqual('@AGENTS.md\n\n# Claude\n특별 규칙\n', p.read_text())
        self.assertEqual([], self.sync()['changed'])

    def test_legacy_parent_link_is_replaced_only_once(self):
        p = self.target / 'AGENTS.md'
        p.write_text('# App\n\n공통 규칙은 [`../../AGENTS.md`](../../AGENTS.md)에 있다. 여기엔 App 고유 정보만 둔다.\n\n## 고유\n그대로\n')
        self.git('add', 'AGENTS.md'); self.git('commit', '-qm', 'legacy')
        self.sync()
        self.assertNotIn('../../AGENTS.md', p.read_text())
        self.assertIn('## 고유\n그대로\n', p.read_text())
        self.assertEqual([], self.sync()['changed'])

    def test_missing_agents_is_created(self):
        self.git('rm', 'AGENTS.md'); self.git('commit', '-qm', 'empty')
        self.sync()
        self.assertIn('knowledge:begin', (self.target / 'AGENTS.md').read_text())

    def test_unrelated_dirty_file_is_untouched(self):
        p = self.target / 'other.txt'; p.write_text('동시 작업')
        self.sync()
        self.assertEqual('동시 작업', p.read_text())

    def test_dirty_initial_agents_is_not_overwritten(self):
        p = self.target / 'AGENTS.md'; p.write_text('다른 작업')
        with self.assertRaises(SyncError): self.sync()
        self.assertEqual('다른 작업', p.read_text())
        self.assertFalse(self.backups.exists())

    def test_dirty_outside_managed_block_is_preserved(self):
        self.sync()
        p = self.target / 'AGENTS.md'; p.write_bytes(p.read_bytes() + b'\nuser edit\n')
        self.common.write_text('# 공통\n\n변경된 규칙\n')
        self.sync()
        self.assertTrue(p.read_bytes().endswith(b'\nuser edit\n'))

    def test_managed_edit_is_conflict(self):
        self.sync()
        p = self.target / 'AGENTS.md'; p.write_text(p.read_text().replace('# 공통', '# 편집'))
        before = self.snapshot()
        with self.assertRaises(SyncError): self.sync()
        self.assertEqual(before, self.snapshot())

    def test_generated_file_edit_is_conflict(self):
        self.sync()
        p = self.target / '.agent-instructions/knowledge/instructions/documentation.md'
        p.write_text('직접 편집')
        with self.assertRaises(SyncError): self.sync()
        self.assertEqual('직접 편집', p.read_text())

    def test_symlink_is_not_followed(self):
        outside = self.root / 'external'; outside.write_text('보존')
        (self.target / 'CLAUDE.md').symlink_to(outside)
        with self.assertRaises(SyncError): self.sync()
        self.assertEqual('보존', outside.read_text())

    def test_source_symlink_is_rejected(self):
        self.common.unlink(); self.common.symlink_to(self.target / 'AGENTS.md')
        with self.assertRaises(SyncError): self.bundle()

    def test_duplicate_markers_are_rejected_without_writes(self):
        p = self.target / 'AGENTS.md'
        p.write_text('<!-- knowledge:begin -->\n<!-- knowledge:begin -->\n<!-- knowledge:end -->\n')
        before = self.snapshot()
        with self.assertRaises(SyncError): self.sync()
        self.assertEqual(before, self.snapshot())

    def test_lone_reversed_and_unowned_markers_are_rejected(self):
        for content in ['<!-- knowledge:begin -->\n',
                        '<!-- knowledge:end -->\n<!-- knowledge:begin -->\n',
                        '<!-- knowledge:begin -->\ntext\n<!-- knowledge:end -->\n']:
            with self.subTest(content=content):
                (self.target / 'AGENTS.md').write_text(content)
                with self.assertRaises(SyncError): self.sync(check=True)

    def test_link_in_fence_is_not_a_dependency(self):
        self.sync()
        self.assertEqual([], self.sync(check=True)['changed'])

    def test_real_missing_link_and_absolute_link_are_rejected(self):
        for link in ['missing.md', '/Users/someone/file.md', '../../escape.md']:
            with self.subTest(link=link):
                self.common.write_text(f'# 공통\n[문서]({link})\n')
                with self.assertRaises(SyncError): self.bundle()

    def test_path_escape_and_duplicate_targets_are_rejected(self):
        self.data['targets'][0]['path'] = '../escape'; self.write_manifest()
        with self.assertRaises(SyncError): load_manifest(self.manifest_path)
        self.data['targets'][0]['path'] = 'demo'
        self.data['targets'].append(dict(self.data['targets'][0])); self.write_manifest()
        with self.assertRaises(SyncError): load_manifest(self.manifest_path)

    def test_local_only_source_is_not_distributable(self):
        self.data['profiles']['common']['files'].append('instructions/local-workspace.md')
        self.write_manifest()
        with self.assertRaises(SyncError): load_manifest(self.manifest_path)

    def test_state_cannot_delete_an_outside_file(self):
        self.sync()
        p = self.target / '.agent-instructions/knowledge/state.json'
        state = json.loads(p.read_text()); state['files']['../../AGENTS.md'] = '0' * 64
        p.write_text(json.dumps(state))
        with self.assertRaises(SyncError): self.sync()

    def test_stale_owned_file_is_removed_but_user_file_is_kept(self):
        self.sync()
        user = self.target / '.agent-instructions/knowledge/user.md'; user.write_text('사용자')
        self.common.write_text('# 공통\n')
        self.data['profiles']['common']['files'] = []; self.write_manifest()
        self.sync()
        self.assertFalse((self.target / '.agent-instructions/knowledge/instructions/documentation.md').exists())
        self.assertEqual('사용자', user.read_text())

    def test_rollback_on_replace_failure(self):
        from unittest.mock import patch
        import agent_sync
        real_replace = os.replace
        calls = []
        def replace(src, dst):
            calls.append(str(dst))
            if len(calls) == 2: raise OSError('fixture failure')
            return real_replace(src, dst)
        before = {k: v[0] for k, v in self.snapshot().items()}
        with patch.object(agent_sync.os, 'replace', side_effect=replace):
            with self.assertRaises(SyncError): self.sync()
        self.assertEqual(before, {k: v[0] for k, v in self.snapshot().items()})

    def test_cli_exit_codes_and_independent_targets(self):
        manifest = self.data
        manifest['targets'].append({**manifest['targets'][0], 'id': 'missing', 'path': 'absent', 'repository': None, 'default_branch': None, 'ci': False})
        self.write_manifest()
        proc = subprocess.run([sys.executable, str(BIN / 'sync-agents.py'),
                               '--source', str(self.source), '--workspace', str(self.root),
                               '--backup-dir', str(self.backups)], capture_output=True, text=True)
        self.assertEqual(2, proc.returncode)
        self.assertTrue((self.target / 'CLAUDE.md').exists())


if __name__ == '__main__': unittest.main()
