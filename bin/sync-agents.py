#!/usr/bin/env python3
"""AGENTS 관리 블록과 참조 파일을 동기화한다. --check는 쓰지 않는다."""
import argparse
import json
from pathlib import Path
import sys

from agent_sync import SyncError, build_bundle, load_manifest, sync_target


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    result.add_argument('--workspace', type=Path, help='manifest 로컬 경로의 기준 폴더')
    result.add_argument('--target', action='append', help='대상 ID; 반복 가능')
    result.add_argument('--target-root', type=Path, help='한 대상의 독립 clone 위치')
    result.add_argument('--backup-dir', type=Path)
    result.add_argument('--check', action='store_true')
    result.add_argument('--validate', action='store_true', help='원본과 참조만 검증')
    result.add_argument('--ci-matrix', action='store_true', help='원격 CI 대상 JSON 출력')
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        source = args.source.resolve()
        manifest = load_manifest(source / 'sync-targets.json')
        targets = manifest['targets']
        if args.target:
            unknown = set(args.target) - {t['id'] for t in targets}
            if unknown:
                raise SyncError('알 수 없는 대상: ' + ', '.join(sorted(unknown)))
            targets = [t for t in targets if t['id'] in args.target]
        if args.target_root and len(targets) != 1:
            raise SyncError('--target-root에는 --target 하나가 필요함')
        bundles = {t['id']: build_bundle(source, manifest, t) for t in targets}
        if args.ci_matrix:
            print(json.dumps({'include': [{**t, 'owner': t['repository'].split('/')[0],
                                          'repo': t['repository'].split('/')[1]}
                                         for t in targets if t['ci']]}))
            return 0
        if args.validate:
            print(f'원본·참조 검증: {len(bundles)}개 대상 통과')
            return 0
        result = 0
        workspace = (args.workspace or source.parent).resolve()
        for target in targets:
            root = args.target_root or workspace / target['path']
            try:
                item = sync_target(root, bundles[target['id']], check=args.check,
                                   backup_root=args.backup_dir)
                print(json.dumps(item, ensure_ascii=False))
                if args.check and item['changed']:
                    result = max(result, 1)
            except (SyncError, OSError, UnicodeError) as error:
                print(f'{target["id"]}: {error}', file=sys.stderr)
                result = 2
        return result
    except (SyncError, OSError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
