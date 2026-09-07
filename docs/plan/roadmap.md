# roadmap — 공통 지침과 문서 인프라

> **M** = 문서 사이트(MkDocs) 작업 번호. 이 저장소 안에서만 쓴다.
> 끝난 G 지침 배포는 [`archive/roadmap-g-지침배포.md`](archive/roadmap-g-지침배포.md)에 있다.

---

## G 잔여 — 지침 배포를 마무리한다

- [ ] `SYNC_TOKEN`을 knowledge 시크릿에 넣는다. 이것 없이는 CI가 「대상 받기」에서 실패한다
      `gh secret set SYNC_TOKEN --repo studio-artifakt/knowledge`
      fine-grained PAT · 대상 저장소 `contents: write` · `pull-requests: write`
- [ ] 토큰 설정 후 CI를 한 대상으로 수동 실행해 PR이 열리는지 확인한다 (`workflow_dispatch` · `target: toolkits`)
- [ ] `docs-template`의 원격 연결을 다시 정한다. 지금 `C4NU/Docs`는 Tappie·Rollie 문서가
      각 저장소로 옮겨가기 전의 옛 공유 저장소라 로컬 골격과 이력이 갈라져 있다
- [ ] Codex가 전역 `~/.codex/AGENTS.md`와 저장소 `AGENTS.md`를 합치는지 실제 세션에서 확인한다.
      블록을 심었으므로 합치지 않아도 규칙은 닿지만, 전역의 역할이 달라진다

## M 문서 사이트 — 12개 저장소 문서를 한 곳에서 읽는다

**왜** — 앱마다 `docs/`를 따로 열어보고 있다. 저장소를 가로지르는 검색이 안 되고,
markdown 원문은 에이전트에게는 맞지만 사람이 훑기에는 불편하다.

**무엇** — 같은 파일을 두 갈래로 쓴다. **에이전트는 markdown 원문을, 사람은 사이트를 읽는다.**
문서를 복사하지 않는다. 사이트는 저장소의 `docs/`를 그대로 읽는 뷰다.

### M1 범위와 배치

- [ ] 어느 저장소의 `docs/`를 넣을지 정한다. `sync-targets.json`의 16곳이 출발점이지만
      문서가 없는 저장소는 뺀다
- [ ] 사이트 저장소 자리를 정한다 — `tools/` 아래 새 저장소가 유력하다
- [ ] 저장소별 `docs/`를 어떻게 모을지 정한다. 후보 둘
      - git submodule — 정확하지만 커밋 고정을 계속 올려야 한다
      - CI가 clone해 빌드 — 항상 최신이지만 빌드가 네트워크에 묶인다
- [ ] `knowledge/instructions/`를 한 섹션으로 넣는다. 오늘 만든 HTML 한 장이 그 자리를 대신하고 있다

### M2 골격

- [ ] MkDocs Material 도입. `mkdocs.yml` 하나로 시작한다
- [ ] 한국어 검색이 되는지 먼저 확인한다 — 형태소 분리가 안 되면 검색이 무용지물이다.
      안 되면 `search.separator` 조정 또는 다른 생성기를 다시 본다
- [ ] `mkdocs serve`로 로컬 실시간 미리보기. 저장하면 브라우저가 바로 갱신되는지 확인
- [ ] 네비게이션을 앱별로 가른다. `plan/` · `tech-docs/` · `guide/` 구분이 사이트에서도 보여야 한다

### M3 배포

- [ ] Cloudflare Pages에 올린다. **칸반(Phase C)과 같은 스택이라 배관을 두 번 만들지 않는다**
- [ ] 접근 제어를 정한다. 제품 문서에 미출시 정보와 가격 정책이 있어 공개하면 안 된다.
      Cloudflare Access 또는 비공개 배포
- [ ] 문서가 바뀌면 다시 빌드한다. 각 저장소 push → 사이트 빌드 트리거

### M4 링크 정합

- [ ] 저장소 안 상대 링크가 사이트에서도 닿는지 확인한다. `tech-docs/`끼리 거는 링크가 많다
- [ ] `[[wiki 링크]]`가 있으면 상대 링크로 바꾼다. 배포 원본에서는 이미 금지하고 있다
- [ ] `.agent-instructions/`는 생성물이라 사이트에서 뺀다. 원본이 이미 사이트에 있다

### M5 Obsidian과의 관계 정리

- [ ] `~/Obsidian/Vault/Projects/*`가 이미 각 저장소 `docs/`를 가리키는 심볼릭이다.
      **사이트와 역할을 가른다** — Vault는 쓰기, 사이트는 읽기
- [ ] 겹치면 하나를 접는다. 같은 것을 두 곳에서 관리하지 않는다

---

## 판단이 남은 것

- **MkDocs가 맞는지** — Quartz(Obsidian Vault를 그대로 웹으로, 백링크 유지)도 후보다.
  Vault를 이미 쓰고 있어 붙이기는 더 쉽지만, 저장소를 가로지르는 검색은 MkDocs가 낫다
- **문서를 모으는 방식** — submodule과 CI clone 중 어느 쪽도 결정하지 않았다
