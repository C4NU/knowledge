# Codex·Claude 지침 점검 — 2026-09-06

현재 작업 디렉터리는 Development이며 Git 저장소가 아니다. 직접 상속되는 Codex 파일은 ~/.codex/AGENTS.md와 Development/AGENTS.md다. 제품별 파일은 링크·진입점만 조사했고 본문 최적화 대상으로 확대하지 않았다. knowledge와 tools/devkit은 작업 전 git status가 깨끗했다.

## 구성 결과

- 실제 사용자 구성: /Users/canu/.codex/config.toml. CODEX_HOME 환경변수는 없으며 내장 app-server config/read가 이 사용자 레이어를 확인했다.
- ChatGPT.app 내장 Codex 0.153.4: features.context_management.experimental_mode=true. features list와 config/read 모두 통과했다.
- PATH의 독립 CLI 0.147.0: 같은 중첩 테이블에 invalid type: map, expected a boolean 오류. 업데이트 전에는 내장 바이너리를 사용해야 한다. CLI 업데이트는 수행하지 않았다.
- ChatGPT 로그인 확인. 공식 지원 요금제는 Plus·Pro·Pro Lite이며 실제 계정 요금제는 미확인이다.
- 설정 작성과 새 프로세스의 읽기는 확인했다. 현재 작업의 창 초과 후 노트·과거 메시지 검색·도구 결과 보존은 미시험이다. 모든 다른 대화의 자동 검색을 의미하지 않는다.
- 새 작업으로 지침과 기능을 로드하는 것을 권장한다. 기존 앱 서버가 설정을 언제 다시 읽는지는 미확인이다. 반영되지 않으면 앱을 재시작한다. 현재 작업이나 앱을 임의 종료하지 않았다.

## 배치 계획과 현재 경로

- Codex 전역: /Users/canu/.codex/AGENTS.md (일반 파일). AGENTS.override.md는 없다.
- Claude 전역: /Users/canu/.claude/CLAUDE.md는 없다. ~/.claude/rules의 8개 사용자 규칙은 tools/devkit/rules 원본으로 연결된다. 이번에는 변경하지 않았다.
- Development/AGENTS.md → knowledge/AGENTS.md, Development/CLAUDE.md → knowledge/CLAUDE.md. 후자는 @AGENTS.md 어댑터다. 두 심볼릭 링크를 유지했다.
- Claude는 상위 디렉터리 CLAUDE.md를 읽고 @ import를 확장한다. Codex는 보통 Git 루트 위를 자동 탐색하지 않는다. 프로젝트의 일반 Markdown 링크는 자동 주입이 아니다.
- Codex 전역에 Development 대상일 때 공통 원본을 읽는 조건부 규칙을 추가했다. 이는 모델에 대한 읽기 지시이며 클라이언트의 자동 주입 기능 변경은 아니다.
- Development에만 파일 한 벌을 두지 않는다. 공통 원본 1개 + 각 프로젝트 AGENTS.md + CLAUDE.md 어댑터를 유지한다. 공유 규칙의 필요 시 참조는 일반 링크로 남겨 Claude @ import가 모든 장문을 시작 시 읽지 않게 한다.
- 다른 위치로 clone하거나 worktree를 만들 때 현재 상대 경로 링크는 깨질 수 있다. 그 환경에서는 공통 규칙의 설치 경로를 별도로 제공해야 한다. 이번에는 폴더 이동을 하지 않았다.

| 프로젝트 AGENTS.md | 공통 링크 | Claude 어댑터 |
|---|---|---|
| `products/tappie/AGENTS.md` | 정상 | `@AGENTS.md` 정상 |
| `products/nottie/AGENTS.md` | 정상 | `@AGENTS.md` 정상 |
| `products/rollie/AGENTS.md` | 정상 | `@AGENTS.md` 정상 |
| `products/hanavi/schedule/AGENTS.md` | 정상 | `@AGENTS.md` 정상 |
| `products/hanavi/app/AGENTS.md` | 정상 | `@AGENTS.md` 정상 |
| `products/paddie/ios/AGENTS.md` | 정상 | `@AGENTS.md` 정상 |
| `products/paddie/android/AGENTS.md` | 정상 | 없음 |
| `tools/artifakt/AGENTS.md` | 정상 | `@AGENTS.md` 정상 |

Paddie Android의 CLAUDE.md 추가는 해당 프로젝트의 별도 작업으로 남겼다. 프로젝트별 문서 삭제·재배치는 하지 않았다.

## 변경과 문자 통계

문자 수는 Python len(UTF-8로 읽은 문자열)이다. 참조 파일로 이동한 분량을 삭제량으로 세지 않는다. 토큰·요금·할당량 실측은 하지 않았다.

| 파일 | 전 | 후 |
|---|---:|---:|
| `/Users/canu/Development/knowledge/instructions/documentation.md` | 0 | 5,077 |
| `/Users/canu/Development/knowledge/instructions/xcode-release.md` | 0 | 3,771 |
| `/Users/canu/Development/knowledge/AGENTS.md` | 13,201 | 4,757 |
| `/Users/canu/Development/tools/devkit/skills/codebase-memory/SKILL.md` | 3,134 | 2,738 |
| `/Users/canu/Development/tools/devkit/skills/app-store-screenshots/migration-workflow.md` | 0 | 11,842 |
| `/Users/canu/Development/tools/devkit/skills/app-store-screenshots/SKILL.md` | 42,444 | 13,797 |
| `/Users/canu/.codex/config.toml` | 6,639 | 6,695 |
| `/Users/canu/.codex/AGENTS.md` | 3,385 | 1,014 |
| `/Users/canu/Development/tools/devkit/skills/app-store-screenshots/scaffold-workflow.md` | 0 | 5,956 |
| `/Users/canu/Development/tools/devkit/skills/app-store-screenshots/design-workflow.md` | 0 | 9,174 |
| `/Users/canu/Development/tools/devkit/skills/app-store-screenshots/template-reference.md` | 0 | 1,944 |

- 반복 규칙을 합치고 불확실성 전부를 질문하던 전역 문구를 결정이 필요한 경우로 좁혔다. 승인 범위·실패 보고·소유권 보호는 유지했다.
- 문서 규칙의 '딱 넷/다섯 번째 금지'와 실제 revenue 포함 다섯 파일 목록의 모순을 바로잡았다.
- 문서·Xcode 상세 절차를 참조로 분리했다. 기존 버전·빌드·검증·승인 규칙은 참조에 보존했다.
- 스크린샷의 마이그레이션·scaffold·디자인·템플릿을 각각 필요 시 읽는 파일로 분리했다. 템플릿 사용, 수량, 내보내기 QA, hand-off는 유지했다. 이미 승인된 마이그레이션은 반복 질문하지 않는다.
- codebase-memory의 광범위 트리거와 미측정 토큰 비교를 제거했다. 구조 질의의 그래프 우선은 유지하고 미제공 때 rg 대체를 명시했다. 기본 출력 수량은 변경하지 않았다.
- 스킬 설치·제거·캐시 편집은 하지 않았다. 라이선스·메타데이터·심볼릭 링크를 유지했다.
- 공식 메모리는 읽기 검색만 했고 쓰지 않았다. 따라서 메모리 트랜잭션을 열거나 정본을 수정하지 않았다.

## 검증

- TOML 파싱, 기존 설정과의 구조 비교: 요청한 context_management 항목만 추가됨.
- 내장 런타임 features list 및 config/read: true, 사용자 파일 출처 확인.
- 변경 파일 다시 읽기, 길이 일치, 참조 파일 존재, 세 사용자 스킬 경로의 심볼릭 링크 검사 완료.
- git diff --check 통과. 실행 코드나 템플릿 코드는 변경하지 않아 앱 빌드는 수행하지 않았다.
- 신규 런타임의 실제 긴 작업 동작, 새 작업의 지침 준수, Claude /memory 로드 목록은 미검증이다.

활성 참조의 깨진 링크는 없다. documentation.md의 cr-61 링크는 코드 블록 안의 문서 형식 예시이며 실제 대상 파일을 요구하는 링크가 아니다.

## 사용자 스킬 발견 목록

34개 원본의 메타데이터·길이를 먼저 확인했다. 관련성이 높은 두 스킬을 수정했으며 나머지 본문을 일괄 로드하거나 기계적으로 축약하지 않았다. 시스템·플러그인 캐시는 제외했다. 세 사용자 스킬 폴더는 같은 원본을 공유하며 config의 비활성 항목은 레거시 spreadsheets 및 browser 캐시 경로였다.

| 스킬 | 진입점 문자 | 설명 문자 |
|---|---:|---:|
| `app-store-screenshots` | 13,797 | 65 |
| `asc-app-create-ui` | 6,138 | 163 |
| `asc-aso-audit` | 11,392 | 170 |
| `asc-build-lifecycle` | 1,724 | 137 |
| `asc-cli-usage` | 5,404 | 190 |
| `asc-crash-triage` | 3,348 | 258 |
| `asc-id-resolver` | 3,255 | 161 |
| `asc-localize-metadata` | 11,389 | 280 |
| `asc-metadata-sync` | 7,924 | 186 |
| `asc-notarization` | 6,428 | 196 |
| `asc-ppp-pricing` | 16,881 | 233 |
| `asc-release-flow` | 7,428 | 360 |
| `asc-revenuecat-catalog-sync` | 14,766 | 236 |
| `asc-screenshot-resize` | 3,708 | 170 |
| `asc-shots-pipeline` | 11,155 | 358 |
| `asc-signing-setup` | 9,143 | 209 |
| `asc-submission-health` | 7,869 | 408 |
| `asc-subscription-localization` | 9,981 | 270 |
| `asc-testflight-orchestration` | 2,169 | 115 |
| `asc-wall-submit` | 1,686 | 201 |
| `asc-whats-new-writer` | 7,120 | 200 |
| `asc-workflow` | 6,911 | 190 |
| `asc-xcode-build` | 8,231 | 236 |
| `backend-patterns` | 12,082 | 84 |
| `clickhouse-io` | 8,625 | 66 |
| `codebase-memory` | 2,738 | 42 |
| `coding-standards` | 9,276 | 66 |
| `find-skills` | 5,456 | 303 |
| `frontend-patterns` | 13,598 | 56 |
| `security-review` | 9,636 | 93 |
| `swift-concurrency-pro` | 5,999 | 162 |
| `swiftdata-pro` | 3,718 | 151 |
| `swiftui-pro` | 4,531 | 163 |
| `tdd-workflow` | 7,509 | 88 |

## 백업과 복구

백업: `/Users/canu/Development/instruction-audit-backups/20260906-195259-74c85c37`. manifest.json에 변경 전후 길이와 파일 경로가 있다. 원본 경로를 그대로 하위 경로로 보관했고 copy2로 메타데이터를 복사했다. 기존 백업을 덮어쓰지 않았다. 복구 시 해당 원본의 이후 편집 여부를 확인한 뒤 개별 파일만 복원한다. 커밋·푸시는 수행하지 않았다.

## 근거

- https://learn.chatgpt.com/docs/config-file/config-reference
- https://learn.chatgpt.com/docs/agent-configuration/agents-md
- https://code.claude.com/docs/en/memory
- 사용자 첨부 pasted-text.txt: 짧은 트리거와 단계적 로딩 원칙을 적용했다. 모델별 성능 주장은 검증 사실로 사용하지 않았다.
