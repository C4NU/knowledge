"""공통 지침의 결정적 생성과 소유 파일만 갱신하는 로컬 동기화."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
import subprocess
import tempfile

BEGIN = '<!-- knowledge:begin -->'
END = '<!-- knowledge:end -->'
DEST = '.agent-instructions/knowledge'
STATE = f'{DEST}/state.json'
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
LINK = re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^)\n]+)\)')
REPO = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
SHA = re.compile(r'[a-f0-9]{64}\Z')


class SyncError(Exception):
    """입력 오류 또는 소유권 충돌. 쓰기를 진행하지 않는다."""


@dataclass(frozen=True)
class Bundle:
    target_id: str
    source_repository: str
    source_sha256: str
    block: bytes
    files: dict


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def relative_path(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise SyncError('유효하지 않은 상대 경로')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')):
        raise SyncError(f'경로 탈출 또는 모호한 경로: {value}')
    return value


def safe_file(root, relative):
    relative_path(relative)
    path = root
    for part in PurePosixPath(relative).parts:
        path = path / part
        if path.is_symlink():
            raise SyncError(f'심볼릭 링크는 수정하지 않음: {path}')
    if path.exists() and not path.is_file():
        raise SyncError(f'일반 파일이 아님: {path}')
    return path


def validate_profile(profile):
    if not isinstance(profile, dict) or set(profile) != {'blocks', 'files'}:
        raise SyncError('프로필은 blocks와 files가 필요함')
    paths = []
    for field in ('blocks', 'files'):
        if not isinstance(profile[field], list):
            raise SyncError(f'프로필 {field}는 목록이어야 함')
        for value in profile[field]:
            relative_path(value)
            if not value.endswith('.md') or value == 'instructions/local-workspace.md':
                raise SyncError(f'배포할 수 없는 원본: {value}')
            paths.append(value)
    if not profile['blocks'] or len(paths) != len(set(paths)):
        raise SyncError('프로필 원본 중복 또는 blocks 없음')


def validate_target(target, profiles):
    required = {'id', 'path', 'repository', 'default_branch', 'profile', 'ci'}
    if not isinstance(target, dict) or not required <= target.keys():
        raise SyncError('대상 필수 항목 누락')
    if not isinstance(target['id'], str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', target['id']):
        raise SyncError('유효하지 않은 대상 ID')
    relative_path(target['path'])
    if target['profile'] not in profiles or type(target['ci']) is not bool:
        raise SyncError('유효하지 않은 프로필 또는 CI 값')
    repo, branch = target['repository'], target['default_branch']
    if repo is not None and (not isinstance(repo, str) or not REPO.fullmatch(repo)):
        raise SyncError('유효하지 않은 GitHub 저장소 이름')
    if branch is not None:
        result = subprocess.run(['git', 'check-ref-format', '--branch', branch], capture_output=True)
        if result.returncode or branch.startswith('-'):
            raise SyncError('유효하지 않은 기본 브랜치')
    if target['ci'] and (not repo or not branch):
        raise SyncError('CI 대상에는 원격 저장소와 기본 브랜치가 필요함')
    if 'project_rule' in target and not isinstance(target['project_rule'], str):
        raise SyncError('프로젝트 규칙은 문자열이어야 함')


def load_manifest(path):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise SyncError('manifest를 읽을 수 없음') from error
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise SyncError('지원하지 않는 manifest 버전')
    if not REPO.fullmatch(data.get('source_repository', '')):
        raise SyncError('유효하지 않은 원본 저장소')
    profiles, targets = data.get('profiles'), data.get('targets')
    if not isinstance(profiles, dict) or not isinstance(targets, list) or not targets:
        raise SyncError('프로필 또는 대상 목록 없음')
    for profile in profiles.values():
        validate_profile(profile)
    ids, paths, repos = set(), set(), set()
    for target in targets:
        validate_target(target, profiles)
        if target['id'] in ids or target['path'] in paths:
            raise SyncError('중복 대상 ID 또는 경로')
        if target['repository'] and target['repository'].lower() in repos:
            raise SyncError('중복 원격 저장소')
        ids.add(target['id']); paths.add(target['path'])
        if target['repository']:
            repos.add(target['repository'].lower())
    return data


def markdown_lines(text):
    """코드 fence 자체와 내부를 구분한다. 제목이나 예시는 파싱하지 않는다."""
    fence = None
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line.rstrip('\r\n'))
        if match:
            marker, rest = match.groups()
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not rest.strip():
                fence = None
            yield line, False
        else:
            yield line, fence is None
    if fence is not None:
        raise SyncError('닫히지 않은 Markdown 코드 fence')


def linked_source(filename, raw):
    target = raw.split('#', 1)[0]
    if not target or target.startswith(('https://', 'http://')):
        return None
    if target.startswith(('/', '~')) or '\\' in target or re.match(r'^[A-Za-z]+:', target):
        raise SyncError(f'이식할 수 없는 링크: {filename} -> {raw}')
    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(filename), target))
    relative_path(normalized)
    return normalized


def validate_links(filename, text, available):
    for line, active in markdown_lines(text):
        if not active:
            continue
        if '/Users/' in line or '~/Development/' in line:
            raise SyncError(f'개인 로컬 경로가 배포 원본에 있음: {filename}')
        for match in LINK.finditer(line):
            linked = linked_source(filename, match[2])
            if linked is not None and linked not in available:
                raise SyncError(f'배포 목록에 없는 참조: {filename} -> {linked}')
        if re.search(r'\[\[[^\]]+\]\]', line):
            raise SyncError(f'배포 원본의 wiki 링크를 상대 Markdown 링크로 바꿔야 함: {filename}')


def inline_block(filename, text):
    def rewrite(match):
        linked = linked_source(filename, match[2])
        if linked is None:
            return match[0]
        fragment = '#' + match[2].split('#', 1)[1] if '#' in match[2] else ''
        return f'[{match[1]}]({DEST}/{linked}{fragment})'
    return ''.join(LINK.sub(rewrite, line) if active else line
                   for line, active in markdown_lines(text)).rstrip()


def build_bundle(source, manifest, target):
    source = source.resolve()
    profile = manifest['profiles'][target['profile']]
    paths = profile['blocks'] + profile['files']
    texts = {}
    for relative in paths:
        try:
            texts[relative] = safe_file(source, relative).read_text(encoding='utf-8')
        except (OSError, UnicodeError) as error:
            raise SyncError(f'원본을 읽을 수 없음: {relative}') from error
    for relative, text in texts.items():
        validate_links(relative, text, set(profile['files']))
    identity = {'source': manifest['source_repository'], 'target': target['id'],
                'profile': target['profile'], 'project_rule': target.get('project_rule'),
                'sources': {p: digest(texts[p].encode()) for p in paths}}
    source_hash = digest(json_bytes(identity))
    pieces = [BEGIN, '공통 규칙은 여기 심어져 있다. 관리 블록은 직접 편집하지 않는다.',
              f'<!-- source: {manifest["source_repository"]}; sha256: {source_hash} -->']
    pieces += [inline_block(p, texts[p]) for p in profile['blocks']]
    if target.get('project_rule'):
        pieces.append('## 이 저장소 버전 정본\n\n' + target['project_rule'])
    pieces.append(END)
    block = ('\n\n'.join(pieces) + '\n').encode()
    files = {p: texts[p].encode() for p in profile['files']}
    return Bundle(target['id'], manifest['source_repository'], source_hash, block, files)


def block_span(content):
    positions = {BEGIN: [], END: []}
    offset = 0
    for line, active in markdown_lines(content.decode('utf-8')):
        encoded = line.encode()
        if active and line.strip() in positions:
            positions[line.strip()].append((offset, offset + len(encoded)))
        offset += len(encoded)
    if not positions[BEGIN] and not positions[END]:
        return None
    if len(positions[BEGIN]) != 1 or len(positions[END]) != 1:
        raise SyncError('표시 블록 중복 또는 짝 누락')
    start, end = positions[BEGIN][0][0], positions[END][0][1]
    if start >= positions[END][0][0]:
        raise SyncError('표시 블록 순서 역전')
    return start, end


def migrate_intro(content):
    """첫 설치에서 이미 알려진 상위 링크 안내만 바꾼다."""
    output = []
    for line, active in markdown_lines(content.decode()):
        if active and line.startswith('공통 규칙은 ') and re.search(r'\]\((?:\.\./)+AGENTS\.md\)', line):
            ending = '\r\n' if line.endswith('\r\n') else '\n'
            line = '공통 규칙은 위 관리 블록에 심어져 있다. 그 밖의 본문은 프로젝트 고유 규칙이다.' + ending
        output.append(line)
    return ''.join(output).encode()


def desired_agents(original, bundle, span):
    if span:
        return original[:span[0]] + bundle.block + original[span[1]:]
    if original is None:
        return f'# AGENTS.md — {bundle.target_id}\n\n'.encode() + bundle.block
    migrated = migrate_intro(original)
    first, separator, rest = migrated.partition(b'\n')
    if first.startswith(b'# ') and separator:
        return first + separator + b'\n' + bundle.block + rest
    return bundle.block + b'\n' + migrated


def read_file(root, relative):
    p = safe_file(root, relative)
    return p.read_bytes() if p.exists() else None


def read_state(root, bundle):
    raw = read_file(root, STATE)
    if raw is None:
        return None
    try:
        state = json.loads(raw)
        if (state['schema_version'] != 1 or state['target_id'] != bundle.target_id
                or state['source_repository'] != bundle.source_repository):
            raise ValueError('identity')
        if not SHA.fullmatch(state['block_sha256']) or not isinstance(state['files'], dict):
            raise ValueError('hashes')
        for path, sha in state['files'].items():
            relative_path(path)
            if path == 'state.json' or not SHA.fullmatch(sha):
                raise ValueError('file hash')
        return state
    except (KeyError, TypeError, ValueError) as error:
        raise SyncError('생성 파일 소유 상태가 잘못됨') from error


def git_directory(root):
    result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel', '--absolute-git-dir'],
                            capture_output=True, text=True)
    if result.returncode or len(result.stdout.splitlines()) != 2:
        raise SyncError(f'Git 저장소가 아님: {root}')
    top, directory = result.stdout.splitlines()
    if Path(top).resolve() != root:
        raise SyncError('대상 경로가 저장소 루트가 아님')
    return Path(directory)


def require_clean_initial(root, relative, desired):
    old = read_file(root, relative)
    if old is None or old == desired:
        return
    result = subprocess.run(['git', '-C', str(root), 'status', '--porcelain', '--', relative],
                            capture_output=True, text=True, check=True)
    if result.stdout.strip():
        raise SyncError(f'첫 설치 파일에 다른 작업의 변경이 있음: {relative}')


def plan_target(root, bundle):
    state = read_state(root, bundle)
    original = read_file(root, 'AGENTS.md')
    span = block_span(original) if original is not None else None
    if span and state is None:
        raise SyncError('소유 상태 없는 표시 블록은 인수하지 않음')
    if state:
        current_hash = digest(original[span[0]:span[1]]) if span else None
        if current_hash not in (state['block_sha256'], digest(bundle.block)):
            raise SyncError('관리 블록에 다른 작업의 변경이 있음')
    desired = {'AGENTS.md': desired_agents(original, bundle, span)}
    claude = read_file(root, 'CLAUDE.md')
    imports = any(active and re.search(r'(?<!\S)@(?:\./)?AGENTS\.md(?=\s|$)', line)
                  for line, active in markdown_lines((claude or b'').decode()))
    desired['CLAUDE.md'] = claude if imports else b'@AGENTS.md\n' + (b'\n' + claude if claude else b'')
    if state is None:
        for name in ('AGENTS.md', 'CLAUDE.md'):
            require_clean_initial(root, name, desired[name])
    old_files = state['files'] if state else {}
    for path in sorted(set(old_files) | set(bundle.files)):
        relative, new = f'{DEST}/{path}', bundle.files.get(path)
        old = read_file(root, relative)
        if old is not None and digest(old) != old_files.get(path) and old != new:
            raise SyncError(f'생성 파일에 다른 작업의 변경이 있음: {relative}')
        if old is not None and path not in old_files and state is None:
            raise SyncError(f'기존 파일 소유권을 인수하지 않음: {relative}')
        desired[relative] = new
    desired[STATE] = json_bytes({'schema_version': 1, 'target_id': bundle.target_id,
                                'source_repository': bundle.source_repository,
                                'source_sha256': bundle.source_sha256,
                                'block_sha256': digest(bundle.block),
                                'files': {p: digest(v) for p, v in bundle.files.items()}})
    return {p: (read_file(root, p), new) for p, new in desired.items() if read_file(root, p) != new}


def atomic_write(root, relative, data):
    path = safe_file(root, relative)
    if data is None:
        path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temp = tempfile.mkstemp(prefix='.knowledge-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), mode)
        safe_file(root, relative)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def rollback(root, changes, written, backup):
    conflicts = []
    for relative in reversed(written):
        before, after = changes[relative]
        if read_file(root, relative) != after:
            conflicts.append(relative)
            continue
        atomic_write(root, relative, before)
        if before is not None:
            shutil.copystat(backup / relative, root / relative)
    return conflicts


def apply_transaction(root, changes, backup_root, git_dir):
    lock = git_dir / 'knowledge-sync.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise SyncError(f'진행 중이거나 복구가 필요한 동기화: {lock}') from error
    os.close(fd)
    written, backup = [], None
    try:
        for relative, (before, _) in changes.items():
            if read_file(root, relative) != before:
                raise SyncError(f'계획 후 파일이 변경됨: {relative}')
        backup_root.mkdir(parents=True, exist_ok=True)
        backup = Path(tempfile.mkdtemp(prefix=root.name + '-', dir=backup_root))
        for relative, (before, _) in changes.items():
            if before is not None:
                dest = backup / relative; dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / relative, dest)
        journal = {'target': str(root), 'status': 'prepared', 'files': list(changes),
                   'created': [p for p, (old, _) in changes.items() if old is None]}
        (backup / 'transaction.json').write_bytes(json_bytes(journal))
        for relative, (before, after) in changes.items():
            if read_file(root, relative) != before:
                raise SyncError(f'쓰기 직전 파일이 변경됨: {relative}')
            atomic_write(root, relative, after); written.append(relative)
        journal['status'] = 'complete'
        (backup / 'transaction.json').write_bytes(json_bytes(journal))
        return str(backup)
    except (OSError, SyncError) as error:
        conflicts = rollback(root, changes, written, backup) if backup else []
        if backup:
            (backup / 'transaction.json').write_bytes(json_bytes({
                'target': str(root), 'status': 'recovery-required' if conflicts else 'rolled-back',
                'conflicts': conflicts, 'files': list(changes)}))
        raise SyncError(f'동기화 중단; 백업 {backup}; {error}') from error
    finally:
        lock.unlink(missing_ok=True)


def sync_target(root, bundle, *, check=False, backup_root=None):
    root = root.resolve()
    git_dir = git_directory(root)
    changes = plan_target(root, bundle)
    backup = None
    if changes and not check:
        backup = apply_transaction(root, changes,
                                   backup_root or git_dir / 'knowledge-sync-backups', git_dir)
    return {'id': bundle.target_id, 'changed': list(changes), 'backup': backup}
