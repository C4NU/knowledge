# current — 공통 지침과 문서 인프라

> **상태** G 지침 배포 완료 — 16곳 적용 · 동기화 어긋남 0 · 테스트 27개 통과
> 커밋·푸시 16/17. `studio-artifakt/devkit` 신설
> **막힌 것** `SYNC_TOKEN` 미설정이라 CI가 아직 안 돈다 (토큰 발급이 사람 손을 탄다)
> **다음** 토큰 설정 → CI 한 대상 시험 → M 문서 사이트 착수
>
> 계획은 [`roadmap.md`](roadmap.md), 끝난 G는 [`archive/`](archive/roadmap-g-지침배포.md).
> 설계 근거는 [`../tech-docs/core/portable-agent-instructions.md`](../tech-docs/core/portable-agent-instructions.md).

## 현재 진행중

- [ ] `SYNC_TOKEN` 발급·설정 — 이것만 되면 CI가 13곳에 PR을 연다

## 진행 예정

### G 잔여
- [ ] 토큰 설정 후 `workflow_dispatch`로 `toolkits` 하나만 시험 실행
- [ ] `docs-template` 원격 연결 재정의 — `C4NU/Docs`와 이력이 갈라져 푸시가 막혀 있다
- [ ] Codex 세션에서 전역·저장소 지침 병합 여부 확인

### M 문서 사이트
- [ ] M1 범위·배치 결정 — 어느 저장소를 넣고 어떻게 모을지
- [ ] M2 MkDocs Material 골격. **한국어 검색 확인이 선행**

### 밖에서 확인할 것
- [ ] 독립 Codex CLI 업데이트 후 구성 읽기 확인
- [ ] Claude `/memory`에서 상위 공통 지침과 프로젝트 어댑터 로딩 확인

## 진행 불가

- [ ] 컨텍스트 창 초과 후 노트·메시지 검색·도구 결과 보존 확인 — 장시간 검증이 필요하다
- [ ] `rollie` 브랜치를 `version/vX.Y.Z`로 되돌리기 — 0.8.0 브랜치를 팔 때 함께 한다.
      roadmap의 `rollie/vX.Y.Z` 접두 규정도 같이 고친다 (그 이유였던 docs 저장소 공유가 사라졌다)
