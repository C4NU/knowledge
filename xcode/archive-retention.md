---
room: xcode
tags: [archive, dsym, disk, derived-data]
verified: 2026-09-04
severity: medium
---

# 빌드 산출물은 스스로 정리되지 않는다

**증상** — 926GB 디스크의 여유가 21GB까지 떨어졌다. 원인 대부분이 개발 잔여물이었다.

| 자리 | 크기 | 성격 |
|---|---|---|
| `~/Library/Developer/XCTestDevices` | 클론 87개 | 병렬 테스트가 만든 임시 시뮬레이터 |
| 프로젝트 `build/` 아래 커스텀 DerivedData | 20개 64GB | `-derivedDataPath`에 실험마다 새 이름을 준 결과 |
| `~/Library/Developer/Xcode/DerivedData` | 44GB | 표준 빌드 캐시 |
| `~/Library/Developer/XcodeBuildMCP/workspaces` | 25GB | 자동 정리 기능이 없다 |

**원인** — `xcodebuild test`가 정상 종료하면 클론 시뮬레이터를 지우지만, 타임아웃이나
중단으로 죽으면 그대로 남는다. scheme에 `parallelizable = "YES"`가 있으면 매 실행마다 쌓인다.

커스텀 `-derivedDataPath`는 표준 위치 밖이라 **Xcode의 Clean으로도, 디스크 정리 GUI로도
잡히지 않는다.**

**대응** — `~/.local/bin/xcode-cleanup.sh`를 launchd(`com.canu.xcode-cleanup`)로
매일 돌린다. XCTestDevices 전체, 14일 지난 MCP 워크스페이스, 30일 지난 DerivedData,
7일 지난 프로젝트 `build/` 하위를 정리하고 `xcodebuild` 실행 중에는 건너뛴다.

⚠️ `du`가 보고하는 XCTestDevices 크기는 실제 점유가 아니다. APFS 클론이라 런타임
이미지를 공유하므로 642GB로 보여도 실제 회수는 그보다 훨씬 적다.

**재발 방지** — 빌드 실험용 경로가 필요하면 프로젝트 `build/` 아래에 두고 재사용 가능한
이름을 쓴다. 그 폴더에 `.metadata_never_index`를 넣으면 Spotlight 오염도 막는다.

관련: [[asc/dsym-not-downloadable]]
