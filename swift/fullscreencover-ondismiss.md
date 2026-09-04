---
room: swift
tags: [swiftui, onboarding, main-thread, realitykit, presentation]
verified: 2026-09-03
severity: high
---

# 표시가 걷히기 전에 다음 화면을 열면 주 스레드가 잠긴다

**증상** — *"단계 끝나니까 크래시"*. 온보딩 마지막에서 앱이 얼어붙었다.
`.ips`를 보니 주 스레드가 `re::RenderThread::waitForFramePacing()`에서 잠겼고,
**우리 코드는 역추적에 한 줄도 없었다.**

**원인** — `showOnboarding = false`가 되는 **그 순간** 카메라를 열고 있었다.
그런데 그때 온보딩의 3D 무대(RealityKit)는 아직 걷히는 중이다. 두 무거운 자원이
같은 프레임에서 겹쳤다.

**대응** — `.onChange(of: showOnboarding)`에서 열던 것을
`fullScreenCover(onDismiss:)`로 옮겼다. **표시가 완전히 걷힌 뒤**에 콜백이 온다.
`.onChange`는 backstop으로 남기되 `didStart` 가드를 뒀다.

**재발 방지** — 화면 전환과 무거운 자원 초기화가 겹치면 `onDismiss`를 쓴다.
플래그가 바뀌는 시점 ≠ 화면이 걷히는 시점이다.

🔴 첫 화면에서 이런 크래시가 나면 피해가 크다. 여기서 죽으면
`hasSeenOnboarding`이 저장되지 않아 **다음에도 또 온보딩이 뜬다.**
처음 켠 사람은 영원히 온보딩을 넘기지 못한다.

관련: [[swift/cached-state-lies]]
