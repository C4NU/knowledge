---
room: asc
tags: [dsym, crash-report, symbolication, archive]
verified: 2026-09-04
severity: high
---

# ASC는 dSYM을 되돌려주지 않는다

**증상** — `asc builds dsyms --build-id …`가 최근 빌드 8개에서 모두
`No dSYM files available for this build`를 반환했다.

**원인** — ASC의 dSYM 다운로드는 **Bitcode 재컴파일 빌드용** 기능이었다. Apple이 재컴파일할
때 새 바이너리의 dSYM을 만들어 제공하던 것이다. Xcode 14에서 Bitcode가 폐기된 뒤로는
올린 바이너리를 그대로 배포하므로 **내려줄 dSYM이 생기지 않는다.**

`uploadSymbols`는 무관하다. `xcodebuild -help`가 말하듯 기본값이 `YES`라 심볼은
올라가지만, 그건 Apple의 크래시 집계용이지 다운로드 제공용이 아니다.

**대응** — 출시·심사 버전의 dSYM은 **로컬이 유일한 사본**이다. 아카이브를 정리할 때
dSYM만 뽑아 zip으로 보관한다(884MB → 227MB로 줄었다).

**재발 방지** — 아카이브를 지우기 전에 dSYM을 먼저 빼낸다. 지우고 나면 그 빌드의
크래시 로그는 영원히 16진수 주소로만 남는다.

관련: [[xcode/archive-retention]]
