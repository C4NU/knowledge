---
room: xcode
tags: [swiftpm, local-package, folder-move, case-sensitivity]
verified: 2026-09-05
severity: high
---

# 폴더를 옮기면 로컬 패키지 참조가 조용히 깨진다

**증상** — `xcodebuild`가 코드를 컴파일하기도 전에 멈춘다.

```
xcodebuild: error: Could not resolve package dependencies:
  the package at '/Users/canu/Development/products/ArtifaktCore' cannot be accessed
  (doesn't exist in file system)
```

**원인** — `XCLocalSwiftPackageReference`의 `relativePath`는 `pbxproj`에 문자열로 박힌다.
저장소 폴더를 옮겨도 Xcode가 고쳐주지 않고, **Xcode를 열지 않으면 아무도 모른다.**

2026-09 폴더 재편(`Xcode/<앱>` → `products/<앱>`)에서 네 앱 중 셋이 깨졌다.

| 앱 | 참조 | 실제 | 결과 |
|---|---|---|---|
| Rollie | `../Paddie/Packages/PaddieRenderingCore` | `../paddie/ios/Packages/…` | 빌드 실패 |
| Nottie | `../ArtifaktCore` | `../../libraries/artifakt-core` | 빌드 실패 |
| Tappie | `../Paddie/ios/Packages/…` | `../paddie/ios/Packages/…` | **우연히 동작** |

🔴 **Tappie가 더 위험한 경우다.** 대문자 `Paddie`로 참조하는데 macOS 기본 파일시스템이
대소문자를 무시해서 빌드가 통과한다. 대소문자를 구분하는 환경(Linux CI, 케이스 센시티브
APFS 볼륨)에서만 깨지므로, 옮긴 지 한참 뒤 남의 기계에서 터진다.

**대응** — 네 참조를 실제 경로로 고쳤다. 빌드 통과를 확인했다.

**재발 방지** — 저장소를 옮긴 뒤 **반드시 각 앱을 한 번 빌드한다.** 문서 링크나 스크립트
경로와 달리 이건 `grep`으로 티가 나지 않는다. 참조 목록은 이 명령으로 뽑는다.

```bash
grep -n "relativePath" <앱>.xcodeproj/project.pbxproj
```

경로는 **실제 디스크 이름과 대소문자까지 같게** 적는다. macOS에서 통과했다는 것은
경로가 맞다는 증거가 못 된다.

관련: [[xcode/xcconfig-precedence]]
