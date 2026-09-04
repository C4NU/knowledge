---
room: xcode
tags: [xcconfig, build-settings, pbxproj, version]
verified: 2026-09-04
severity: high
---

# xcconfig를 고쳤는데 안 바뀌면 pbxproj를 본다

**증상** — `Configs/Shared.xcconfig`의 값을 고쳤는데 빌드에 반영되지 않는다.

**원인** — Xcode 빌드 설정에는 우선순위가 있고 **높은 쪽이 낮은 쪽을 덮어쓴다.**

```
1. Target 설정 (pbxproj)      ← 가장 세다
2. Target xcconfig
3. Project 설정 (pbxproj)
4. Project xcconfig
5. 플랫폼 기본값
```

**pbxproj의 타겟 설정이 xcconfig를 이긴다.** Xcode UI에서 빌드 설정을 한 번이라도
클릭해 바꾸면 그 값이 pbxproj 타겟 레벨에 박히고, 그때부터 xcconfig는 무시된다.

**대응** — xcconfig를 쓰는 프로젝트에서는 **Xcode UI에서 빌드 설정을 바꾸지 않는다.**
이미 박혀 있다면 pbxproj에서 해당 키를 지운다.

```bash
# 어느 타겟에 값이 박혀 있는지 찾기
grep -n 'MARKETING_VERSION' <앱>.xcodeproj/project.pbxproj
```

**재발 방지** — 값이 안 먹으면 계산이나 문법을 의심하기 전에 **같은 키가 pbxproj에
있는지부터** 본다. Xcode의 Build Settings 화면에서 값 옆의 출처 표시로도 확인할 수 있다.

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
