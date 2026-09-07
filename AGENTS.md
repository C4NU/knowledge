# AGENTS.md — 공통 지침 원본

공통 규칙은 knowledge가 관리하고 각 저장소의 AGENTS.md 관리 블록과 참조 파일에 배포한다.
상대 링크는 이 파일의 실제 위치 기준이다. 심볼릭 링크로 열었다면 대상 파일 기준으로 읽는다.
배포된 저장소를 작업할 때는 그 저장소의 지침을 우선하며 이 원본을 중복 로드하지 않는다.

## 공통

이 knowledge 저장소 또는 Development 최상위에서 작업할 때 [공통 규칙](instructions/common.md)을 읽고 적용한다.
문서 작성·작업 완료 시 [문서 규칙](instructions/documentation.md)을 필요한 범위에서 읽는다.

## 앱

출시 앱을 작업할 때만 [앱 규칙](instructions/app.md)을 적용한다.
Apple 앱의 버전·빌드·서명·ASC 작업에는 [Apple 진입점](instructions/apple.md)과
[Xcode·배포 규칙](instructions/xcode-release.md)을 읽는다. 각 제품의 정본·예외는 제품 AGENTS.md에 둔다.

## 로컬 전용

Development 폴더를 찾거나 정리할 때만 [저장소 지도·Obsidian 연결](instructions/local-workspace.md)을 읽는다.
이 내용은 제품 저장소에 배포하지 않는다. 새 기기는 devkit 설치 후 해당 저장소 내부의 지침을 읽는다.
