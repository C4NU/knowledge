# knowledge — 프로젝트를 가로지르는 지식

> 🔴 **2026-11-15 종료(보관).** 더 고치지 않는다.
> 공통 규칙·기술 문서의 정본은 workprint. 보드의 문서(「에이전트 공통 규칙」·「배포 규칙」 등)로 옮겼고,
> 각 저장소 `AGENTS.md`는 그 문서를 가리키는 짧은 「최소 규칙」 절을 직접 갖는다(OPS-274·329).
> 지침 동기화 워크플로(`sync-agents.yml`)는 한 번도 동기화에 성공하지 못해(SYNC_TOKEN 미설정) 지웠다.

> **이 폴더는 AI가 읽는다.** 사람이 읽는 체크리스트는 각 저장소의 `docs/plan/`에 있다.

한 번 밟은 함정을 다시 밟지 않기 위한 장기 기억이다. 여기 있는 것은 **어느 앱에서나
유효한 지식**이고, 그 앱에서만 통하는 것은 해당 저장소의 `docs/tech-docs/`에 둔다.

판단 기준은 한 문장이다 — **"이 지식이 다른 앱에서도 유효한가?"**

## 방 목록

| 방 | 담는 것 |
|---|---|
| [`swift/`](swift/) | Swift·SwiftUI 언어와 프레임워크의 함정 |
| [`xcode/`](xcode/) | 빌드·서명·아카이브·시뮬레이터 |
| [`asc/`](asc/) | App Store Connect·심사·메타데이터 |
| [`revenuecat/`](revenuecat/) | 과금·구독·entitlement |
| [`platform/`](platform/) | 앱 확장·Catalyst·OS 버전 분기 |

## 쓰는 법

작업하다 함정을 밟았거나 되돌릴 수 없는 결정을 내렸으면 해당 방에 파일 하나를 만든다.
한 문서는 한 주제만 담는다.

```markdown
---
room: platform
tags: [app-extension, activitykit]
verified: 2026-09-04
severity: high
---

# 제목 — 무엇이 사실인지 한 줄로

**증상** — 무엇을 보았나.
**원인** — 왜 그런가.
**대응** — 어떻게 했나.
**재발 방지** — 다음에 무엇을 먼저 보나.

관련: [[swift/cached-state-lies]]
```

`verified`는 마지막으로 확인한 날짜다. 오래된 문서를 만나면 지금도 사실인지 다시 잰다.
플랫폼은 바뀌고, 여기 적힌 제약이 풀렸을 수 있다.

`severity`는 `high`(제품을 못 내보낸다) · `medium`(고쳐야 한다) · `low`(알아두면 낫다).

## 읽는 법

작업을 시작하기 전에 건드릴 영역의 방을 먼저 훑는다. 특히 `severity: high`는 그 자리에서
막히는 것들이라 미리 읽는 값이 크다.

---

## 공통 지침 배포

`AGENTS.md`와 `instructions/`는 **다른 저장소로 배포되는 원본**이다.
각 저장소의 `AGENTS.md`에 관리 블록으로 심기고 참조 문서는 `.agent-instructions/`로 간다.

```
instructions/common.md    ─┐
instructions/app.md        ├─ 블록으로 심긴다 (프로필에 따라)
instructions/apple.md     ─┘
instructions/documentation.md ─┐
instructions/xcode-release.md   ├─ .agent-instructions/ 로 배포된다
xcode/xcconfig-precedence.md   ─┘
instructions/local-workspace.md  ← 배포하지 않는다 (이 기기 전용)
```

| 프로필 | 심는 것 | 대상 |
|---|---|---|
| `common` | common | 모든 저장소 |
| `app` | + app | 출시 앱 |
| `apple` | + apple | Xcode·ASC를 쓰는 앱 |

대상과 프로필은 [`sync-targets.json`](sync-targets.json)에 있다.

```bash
python3 -m unittest discover          # 22개
python3 bin/sync-agents.py --validate # 원본·참조 검증
python3 bin/sync-agents.py --check    # 어긋난 대상만 보고. 쓰지 않는다
python3 bin/sync-agents.py            # 전체 적용
python3 bin/sync-agents.py --target tappie
```

🔴 **각 저장소의 관리 블록과 `.agent-instructions/`는 생성물이다.**
직접 고치면 다음 동기화가 충돌로 멈춘다. 고칠 것은 여기서 고친다.
관리 블록 **바깥**의 본문은 그 저장소 고유 규칙이라 동기화가 건드리지 않는다.

### CI

`main`에 지침이 바뀌면 [워크플로](.github/workflows/sync-agents.yml)가 12개 저장소에
`chore/knowledge-sync` 브랜치로 PR을 연다. 한 저장소가 막혀도 나머지는 계속한다.

🔴 **저장소 시크릿 `SYNC_TOKEN`이 필요하다.** 기본 `GITHUB_TOKEN`은 자기 저장소에만
쓸 수 있다. 대상 저장소의 `contents: write` · `pull-requests: write` 권한을 가진
토큰(fine-grained PAT 권장)을 넣는다. 없으면 「대상 받기」 단계에서 실패한다.

`ci: false`인 대상(`devkit` · `ghost-theme-dope` · `toolkits` · `paddie-legacy`)은
로컬에서 직접 돌린다.
