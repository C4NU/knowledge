# 로컬 전용 규칙

이 파일은 Development 작업 공간에서만 읽으며 제품 저장소에 배포하지 않는다.

## 저장소 지도

최상위는 **성격**으로 가른다. 플랫폼이나 언어로 나누지 않는다 —
그렇게 하면 한 제품이 여러 폴더로 흩어진다.

| 폴더 | 담는 것 |
|---|---|
| `products/` | 출시했거나 만들고 있는 제품 |
| `libraries/` | 여러 제품이 함께 쓰는 패키지 |
| `tools/` | 제품을 만들기 위한 내부 도구 |
| `templates/` | 새 프로젝트를 시작할 때 복사하는 골격 |
| `knowledge/` | **이 파일과 공통 지식.** AI가 읽는다 |
| `sandbox/` | 실험·습작 — 다시 손댈 생각이 있는 것 |
| `reference/` | 남의 코드와 문서. 참고용 |
| `archive/` | 끝난 것. 보관만 한다 |

### products

| 경로 | 내용 |
|---|---|
| `paddie/{ios,android,legacy}` | 사진 프레임 편집 — Creative Studio (2.3.0 심사 중) |
| `tappie` | 하루를 기록하는 비디오 카메라 (1.1 출시 · 1.2 준비) |
| `rollie` | 36컷 일회용 35mm 필름 카메라 (0.8.0 작업 중) |
| `nottie` | 창작자용 작업 노트 (미출시) |
| `hanavi/{app,schedule,yearbook,docs}` | 하나비 웹 프로젝트 묶음 |
| `tennysn` | AI 마켓 다이어리 (옛 이름 ai-market-diary) |

Paddie·Tappie·Rollie는 **Studio Artifakt** 제품군이다. 제품 철학과 가격 정책 등
앱을 가로지르는 문서는 `~/Obsidian/Vault/Studio Artifakt/`에 있다.

### 그 밖

| 경로 | 내용 |
|---|---|
| `libraries/artifakt-core` | 공용 Swift 패키지 |
| `tools/artifakt` | 내부 개발용 macOS 렌더링 테스트 앱 (외부 공개 안 함) |
| `tools/{toolkits,icon-composer,icon-scripts,ghost-theme-dope}` | 도구·스크립트 |
| `templates/docs-template` | 문서 골격 |

🔴 **`AGENTS.md`와 `CLAUDE.md`의 실체는 `knowledge/`에 있다.** 루트의 둘은 심볼릭 링크다.
`knowledge/`가 git 저장소(`studio-artifakt/knowledge`)라서 그렇게 뒀다 — git은 심볼릭
링크를 내용이 아니라 경로 문자열로 커밋하므로, 실체가 저장소 안에 있어야 백업된다.

---

### Obsidian과의 관계

`~/Obsidian/Vault/Projects/<앱>`은 각 저장소의 `docs/`를 가리키는 **심볼릭 링크**다.
Vault에서 편집하면 저장소 원본이 바뀐다. **사본이 아니다** — 어느 쪽에서 고쳐도 같은 파일이다.

---


네 앱의 전용 방은 이렇다.

| 앱 | 전용 방 |
|---|---|
| Paddie | `FRAME` · `EXPORT` · `LAYOUT` |
| Tappie | `EXTENSION` |
| Nottie | `WIDGET` |
| Rollie | 아직 없음 |

## 기존 프로젝트 버전 정본 참고

아래 값은 각 저장소의 지침으로 이전한다. 다른 프로젝트에 배포하지 않는다.

| 프로젝트 | 정본 |
|---|---|
| Paddie | `Paddie.xcodeproj/project.pbxproj` |
| Tappie · Rollie · Nottie | `Configs/Shared.xcconfig` |


## xcconfig의 기존 프로젝트 사례

## 곁들여 — 테스트 타겟은 xcconfig에서 빠져 있곤 하다

2026-09-04 Tappie에서 확인한 것:

```
Tappie(앱)·위젯·확장     xcconfig 연결 있음 → MARKETING_VERSION 1.2.0
TappieTests·TappieUITests xcconfig 연결 없음 → pbxproj의 0.2.0
```

Xcode가 프로젝트를 만들 때 테스트 타겟에 넣은 기본값이 그대로 남은 것이다.
테스트 타겟은 스토어에 올라가지 않으므로 피해는 없지만, **`pbxproj`의 버전을 보고
"버전이 밀렸다"고 판단하면 안 된다.** 정본은 xcconfig다.

관련: [[xcode/archive-retention]]
