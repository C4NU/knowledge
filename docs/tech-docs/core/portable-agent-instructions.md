---
room: core
tags: [agents, instructions, portability]
verified: 2026-09-06
severity: high
---

# 공통 지침은 참조 파일까지 저장소 안에 배포한다

**증상** — knowledge의 분리된 문서 진입점이 개인 절대 경로를 사용해 다른 위치에서는 열리지 않는다. 상위 AGENTS.md 링크만 있는 제품 저장소는 단독 clone으로 공통 규칙을 얻지 못한다.

**원인** — 지침의 로딩과 파일의 배포는 별개다. instructions 파일만 복사해도 xcode 문서 등 하위 참조가 빠지면 다시 끊어진다. 문서 분리는 본문에 남은 앱·로컬 규칙의 범위 분류를 대신하지 않는다.

**대응** — knowledge AGENTS.md의 문서·Xcode 진입점을 `instructions/` 상대 링크로, Xcode의 후속 참조를 `../xcode/xcconfig-precedence.md`로 수정했다. 심볼릭 링크로 읽을 때 상대 경로의 기준은 실제 대상 파일이다. 프로젝트 배포는 관리 블록과 명시적 참조 파일 목록을 함께 생성하도록 [계획](../../plan/roadmap.md)에 반영했다.

**검증** — 미커밋 작업 파일을 Development 밖 임시 디렉터리에 복사하여 실제 Markdown 링크 3개, CLAUDE.md의 @AGENTS.md, 기존 Development 심볼릭 링크의 대상 기준 경로를 확인했다. fenced code block의 예시 링크는 실제 의존성으로 세지 않았다. 현재 파일로 검증한 것이며 원격 clone·클라이언트 자동 로딩 검증은 아니다.

**재발 방지** — G2의 --check에 외부 경로·누락 참조·표시 블록 오류·프로젝트 본문 보존 검사를 포함한다. 공통 원본 및 참조 파일이 커밋된 뒤 대상 저장소만 별도로 clone한 환경에서 재검증한다. 실제 배포 전에는 “여기 심어져 있다”로 바꾸지 않는다.
