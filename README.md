# knowledge — 프로젝트를 가로지르는 지식

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
