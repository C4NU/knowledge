---
room: swift
tags: [scenephase, app-extension, lifecycle, swiftui]
verified: 2026-09-03
severity: high
---

# `scenePhase`는 앱 확장에서 죽은 신호다

**증상** — 확장에서 자원을 놓는(release) 코드가 **한 번도 실행되지 않았다.**
`.onChange(of: scenePhase)`에 걸어뒀는데 크래시만 계속 났다.

**원인** — 확장에서 `scenePhase`는 늘 `background`이고 전환이 발생하지 않는다.
`.onChange`는 값이 **바뀔 때** 도는데, 바뀌지 않으므로 영원히 돌지 않는다.

코드 자체는 옳았다. **자리가 틀렸다.**

**대응** — UIKit 알림(`willResignActive` 등)으로 옮기고, 배경에 400ms 이상 머물 때만
자원을 놓게 했다. 잠깐 지나가는 전환에서 놓아버리면 다시 열 때 비용이 크다.

**재발 방지** — 고치기 전에 **그 줄이 도는지부터** 확인한다. 로그 한 줄이면 된다.
"코드가 맞는데 왜 안 되지"를 오래 붙들었다면, 대개 그 코드가 실행되지 않고 있다.

관련: [[swift/cached-state-lies]] · [[platform/app-extension-walls]]
