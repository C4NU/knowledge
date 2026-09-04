---
room: platform
tags: [backgroundtasks, bgprocessing, dasd, live-activity]
verified: 2026-09-04
severity: medium
---

# `BGProcessingTask`는 **놀고 있고 꽂혀 있을 때만** 돈다

**증상** — 자정 이후로 예약한 배경 작업이 안 돈다. 아침에 결과가 없는데,
**iOS가 안 부른 것인지 우리가 못 한 것인지 가릴 수가 없다.**

**원인** — `dasd`가 두 정책으로 막는다. sysdiagnose에 점수와 이유가 통째로 나온다:

```
bgProcessing-<식별자>:[
  {Device Activity Policy, 0.00, [{launchType == PROCESSING AND deviceActive == 1}]}
  {Battery Level Policy,   0.00, [{batteryLevel == 93 AND pluggedIn == 0}]}
], Decision: MNP
```

🔴 **`requiresExternalPower = false`로 못 우회한다.** 그건 「우리가 요구하지 않는다」일
뿐이고 dasd는 **자기 정책으로 따로 또 본다.**
⚠️ 관찰: 로그 전 구간에서 `pluggedIn`이 한 번도 1이 안 됐다 — 배터리가 오르는
구간에서도. **무선 충전은 「꽂혔다」로 안 세는 것으로 보인다.**

**대응** — 배경 작업에 **보이는 것**을 걸지 않는다. Tappie는 자정 표시를
`ActivityContent(staleDate:)`로 옮겼다 — 시스템이 그 시각에 위젯을 **저 혼자 다시
그리고**, 위젯은 `context.isStale`을 「하루가 끝났다」로 읽는다. 앱도 충전기도
배경 작업도 필요 없다. **무거운 일(병합)만** 배경에 남기고, 그건 앱을 열 때 어차피 한다.
👉 **보이는 것과 하는 일을 같은 순간에 묶을 이유가 없다.**

**재발 방지** — 배경 작업을 시험할 땐 **케이블로 꽂고 손대지 않는다.** 그러지 않으면
「안 돌았다」가 코드 탓인지 조건 탓인지 안 갈린다 — 한 판을 통째로 날린다.
그리고 그 길에 **계기를 먼저 단다**(등록·예약·깨어남·끝·회수를 각각).

관련: [[platform/activitykit-after-limit]] · [[platform/app-extension-walls]]
