# archive — G 지침 배포 (완료 2026-09-07)

> 16개 저장소에 공통 지침 관리 블록을 심는 작업. G1~G6 완료.
> 결과와 설계 근거는 [tech-docs/core/portable-agent-instructions.md](../../tech-docs/core/portable-agent-instructions.md).

---

# roadmap — 공통 에이전트 지침 배포

> G1~G6는 이 계획의 지침 배포 작업 번호다. 사용자 제시안을 현재 파일 구조에 맞춰 개정했다.
> 별도의 기존 G 계획 파일은 Development와 Obsidian Vault의 Markdown 검색에서 찾지 못했다.
> 범위: 공통 원본은 knowledge, 개인 전역 지침은 devkit, 제품 규칙은 각 저장소가 소유한다.

## G1 공통·앱·로컬 범위 확정

- [ ] 파일 분리를 완료로 간주하지 않고 아래 범위로 원본을 정리한다.
  - 공통: 작업 원칙·코드·입력 검증·보안·언어·문서 관리·일반 Git 규칙.
  - 앱: `version/vX.Y.Z`, 새 버전의 번호 증가, Xcode·ASC 규칙. Xcode 규칙은 Apple 대상에만 포함한다.
  - 로컬 전용: 저장소 지도·Obsidian 연결·Development 심볼릭 링크 설명.
- [ ] 프로젝트별 버전 정본 표 등 Paddie·Tappie 고유 사실은 각 프로젝트 규칙으로 분리한다.
- [ ] `instructions/*.md`는 명시적 파일 목록으로 배포한다. 새 파일이 생겼다고 모든 저장소에 자동 포함하지 않는다.
- [ ] 절을 자동 분리할 경우 backtick·tilde fence와 그 길이를 추적한다. 예시 속 `#`·`##`는 절로 인식하지 않는 테스트를 둔다.
- [ ] 수락 기준: 앱 규칙이 웹·라이브러리에 강제되지 않고 로컬 지도·개인 절대 경로가 배포 결과에 없다.

## G2 저장소 내부 동기화

- [ ] `knowledge/bin/sync-agents.py`와 대상 manifest를 만든다. manifest에는 로컬 경로·원격 owner/repo·기본 브랜치·포함 프로필·배포 파일을 명시한다.
- [ ] 대상 `AGENTS.md`의 `<!-- knowledge:begin -->` / `<!-- knowledge:end -->` 안에 짧은 공통 규칙·필요 시 읽기 진입점을 생성한다. 블록 밖 프로젝트 본문은 바이트 단위로 보존한다.
- [ ] 상세 파일은 대상 `.agent-instructions/knowledge/`에 복사한다. `instructions/`와 필요한 `xcode/` 하위 구조를 유지하고 AGENTS.md의 링크를 저장소 내부 상대 경로로 생성한다.
- [ ] `instructions/xcode-release.md` → `xcode/xcconfig-precedence.md`처럼 이어지는 참조도 포함한다. 필요한 실제 문서 참조는 모두 같은 저장소 안에서 해결되게 한다. 코드 블록 속 형식 예시는 실제 의존성과 구분한다.
- [ ] `--check`는 읽기만 수행하고 차이 경로를 보고한다. 일치 0, 어긋남 1, 잘못된 입력·표시 블록·경로 오류 2로 종료한다. 파일·백업·타임스탬프를 생성하지 않는다.
- [ ] apply는 변경 파일만 고유 백업 후 원자적으로 교체한다. 생성 파일의 소유 목록과 원본 revision/hash를 기록한다. 재실행 결과가 같아야 한다.
- [ ] 중복·누락·역전 표시 블록, 경로 탈출, 예기치 않은 심볼릭 링크, 소유권 충돌은 해당 대상 쓰기를 중단한다. 무관한 dirty 파일은 보존하고 독립 대상은 계속한다.
- [ ] 수락 기준: 두 번 apply 후 차이 없음, check 읽기 전용, 프로젝트 본문 보존, Development 밖 임시 복사본의 모든 실제 링크 정상.

## G3 없는 저장소에 진입점 생성

- [ ] tennysn부터 G2를 시험한다. 기존 README·계획·CLAUDE 지침을 확인한 뒤 제품 사실을 추측하지 않고 생성한다.
- [ ] 아래 8곳의 포함 여부와 프로필을 manifest에 확정하고 순서대로 생성한다. legacy의 활성 동기화 여부도 명시한다.
- [ ] Claude를 사용할 대상은 `CLAUDE.md`의 `@AGENTS.md` 어댑터를 확인한다. 기존 Claude 전용 본문은 보존한다.

| AGENTS.md 없는 경로 | 조회된 origin |
|---|---|
| products/tennysn | C4NU/tennysn |
| products/hanavi/yearbook | C4NU/yearbook |
| products/paddie/legacy | C4NU/Paddie |
| libraries/artifakt-core | studio-artifakt/artifakt-core |
| tools/toolkits | C4NU/Toolkits |
| tools/devkit | 없음 |
| tools/ghost-theme-dope | C4NU/Dope-Custom |
| templates/docs-template | C4NU/Docs |

## G4 Codex 전역 지침을 devkit으로 관리

- [ ] 현재 `~/.codex/AGENTS.md`를 출발점으로 devkit 관리 원본을 만든다. 7월 29일의 일반 지침이라는 이전 전제는 폐기한다. 9월 6일에 축약과 Development 조건부 읽기 규칙이 적용됐지만 아직 일반 파일이다.
- [ ] install/doctor에 백업·심볼릭 링크·동등성 검사를 추가한다. config.toml 등 비소유 파일은 변경하지 않는다.
- [ ] 전역에는 개인 작업 원칙만 둔다. G2 배포가 완료된 저장소는 로컬 Development 원본을 다시 읽지 않게 하여 이중·낡은 규칙 적용을 막는다.
- [ ] 미배포 저장소용 조건부 읽기는 과도기로만 유지하고 이식 완료 후 제거한다. 외부 clone의 동작을 전역 파일 존재에 의존시키지 않는다.

## G5 기존 저장소 문구 교체

- [ ] G2 블록과 참조 파일이 실제 설치된 대상만 기존 상위 링크 문구를 바꾼다.
- [ ] 문구: “공통 규칙은 아래 관리 블록에 심어져 있다. 상세 규칙은 이 저장소의 `.agent-instructions/knowledge/`에서 필요할 때 읽는다. 그 밖의 본문은 프로젝트 고유 규칙이다.”
- [ ] 상대 상위 경로를 읽으라는 문구를 없애고 Codex AGENTS / Claude @AGENTS 경로를 각각 확인한다.

## G6 knowledge 변경 시 동기화 PR

- [ ] 대상 12개를 manifest로 먼저 확정한다. 현재 products/libraries/tools/templates의 Git 저장소는 16곳(AGENTS 있음 8, 없음 8)이며 12곳의 선택 근거는 미확인이다.
- [ ] AGENTS.md뿐 아니라 instructions/**, 포함된 참조 문서, manifest, 동기화 스크립트 변경도 CI 트리거에 포함한다.
- [ ] 원본 CI에서 검증·차이 생성을 먼저 수행하고 대상별 전용 브랜치의 PR만 생성/갱신한다. 자동 merge는 하지 않는다.
- [ ] source 기본 브랜치 반영 및 수동 실행으로 제한한다. 비신뢰 PR 코드에 쓰기 자격증명을 전달하지 않는다.
- [ ] 각 원격 저장소에 한정한 GitHub App 또는 토큰 권한을 준비한다. knowledge의 기본 GITHUB_TOKEN만으로 타 저장소에 쓸 수 있다고 가정하지 않는다.
- [ ] 같은 대상의 열린 동기화 PR은 갱신하고 중복 생성하지 않는다. 대상별 실패를 기록하고 성공한 다른 대상을 되돌리지 않는다.
- [ ] 수락 기준: 첫 PR diff에 표시 블록·배포 파일만 존재, 대상 CI 통과, 무변경 재실행 시 PR 없음. 원격 활성화는 대상과 권한이 확정된 뒤 진행한다.
