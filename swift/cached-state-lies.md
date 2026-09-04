---
room: swift
tags: [state, avfoundation, activitykit, scenephase, debugging]
verified: 2026-09-03
severity: high
---

# 캐시된 상태를 믿지 마라 — 시스템에 직접 물어라

**증상** — 한 사이클에 같은 종류의 버그를 **세 번** 만났다. 전부 "우리가 적어둔 상태"와
"시스템의 실제 상태"가 어긋난 경우였다.

| 우리가 믿은 것 | 실제 |
|---|---|
| `scenePhase` | 앱 확장에서는 늘 `background`. 전환이 오지 않는다 |
| `Activity.activities` | 방금 만든 액티비티가 목록에 없다 |
| `SoundEngine.started` (자체 플래그) | 엔진은 이미 멈췄는데 플래그는 `true`로 남아 있다 |

**원인** — 셋 다 **시스템이 밖에서 상태를 바꿀 수 있는 자원**이다. `AVAudioEngine`은
다른 프로세스가 오디오 세션을 가져가면 멈춘다(잠금화면 확장이 정확히 그렇게 한다).
그런데 우리 플래그는 그 사실을 모른다. 죽은 엔진에 계속 버퍼를 꽂고 있었고,
소리는 한 번 끊기면 영영 나지 않았다.

**대응** — 자체 플래그를 지우고 **엔진에게 직접 묻는다**.

```swift
// 잘못된 방법: 우리가 적어둔 것을 믿는다
if started { engine.play(buffer) }

// 올바른 방법: 시스템에 묻는다
if engine.isRunning { engine.play(buffer) }
```

**재발 방지** — 상태 플래그를 만들기 전에 묻는다. **"이 자원을 시스템이 밖에서 바꿀 수
있는가?"** 그렇다면 플래그를 두지 않고 매번 조회한다. 오디오·카메라·액티비티·네트워크가
모두 여기 해당한다.

버그를 조사할 때도 순서가 있다. 값이 이상하면 **계산이 틀렸는지 보기 전에 그 값이 어디서
왔는지** 본다. 캐시된 값이면 원본과 대조한다.

관련: [[swift/scenephase-dead-in-extension]] · [[platform/app-extension-walls]]
