## 버전과 빌드 번호

**마케팅 버전**은 `MARKETING_VERSION`(`X.Y.Z`)이고 위로만 간다 — ASC가 하향을 거부한다.
프로젝트가 정한 버전 정본을 수정한다. `asc xcode version edit`만으로 마케팅 버전이 바뀐다고 가정하지 않는다.

**빌드 번호**(`CURRENT_PROJECT_VERSION`)는 용도에 따라 두 가지를 쓴다.

| 용도 | 형식 | 예 |
|---|---|---|
| 베타·내부 빌드 | 순번 | `1` · `2` · `3` |
| 실제 릴리즈 | 제출 날짜 `YYYYMMDD` | `20260904` |
| 같은 날 릴리즈가 둘 이상 | `YYYYMMDD.N` | `20260904.1` · `20260904.2` |

날짜를 쓰는 이유는 **빌드를 보면 언제 낸 것인지 바로 알기 위해서**다. 순번은 내부에서
빠르게 도는 빌드라 날짜가 의미 없을 때만 쓴다.

🔴 **한 프로젝트 안에서 두 형식을 섞지 않는다.** 릴리즈 트랙에 들어갔으면 그 버전이
끝날 때까지 날짜 형식을 유지한다.

### 정본이 어디인지 먼저 확인한다

🔴 **버전 정본은 프로젝트마다 다르다.** `Configs/*.xcconfig`에 `MARKETING_VERSION`이 있으면
**그것이 정본이고 `pbxproj` 값은 덮어써진다.** 없으면 `pbxproj`가 정본이다.

프로젝트별 정본과 플랫폼별 예외는 해당 저장소의 AGENTS.md를 따른다.

```bash
# 정본 찾기 — xcconfig에 있으면 그것, 없으면 pbxproj
grep -rE 'MARKETING_VERSION|CURRENT_PROJECT_VERSION' Configs/*.xcconfig
```

⚠️ xcconfig를 쓰는 프로젝트의 `pbxproj`에는 **옛 값이 남아 있을 수 있다**.
빌드에는 영향이 없지만, 그 값을 보고 "버전이 밀렸다"고 판단하면 안 된다.

**버전이나 빌드 번호를 올릴 때는 정본 파일의 두 값을 함께 고친다.**
`asc xcode version edit`나 빌드 스크립트로만 올리면 저장소에는 옛 번호가 남아
다음 빌드가 그것으로 나간다.

---

## xcconfig 구성

새 xcconfig 구성을 만들 때는 **버전과 빌드 설정을 `Configs/` 아래에 둔다.** 기존 프로젝트의 정본이 pbxproj라면 이번 작업 범위 밖에서 임의 이전하지 않는다.

```
Configs/
├── Shared.xcconfig     공통 — 번들 ID · 버전 · 앱 이름 · 팀   (필수)
├── Debug.xcconfig      개발 빌드                              (필수)
├── Release.xcconfig    출시 빌드                              (필수)
├── Beta.xcconfig       TestFlight 빌드                        (필요할 때)
└── Secrets.xcconfig    키·토큰. 🔴 커밋 금지                  (필요할 때)
```

`Debug` · `Beta` · `Release`는 각각 첫 줄에서 `#include "Shared.xcconfig"`를 하고,
**자기 구성에서 달라지는 것만** 적는다. `Shared`는 `#include? "Secrets.xcconfig"`로
비밀값을 선택적으로 당긴다 — **물음표가 핵심이다.** 파일이 없어도 빌드가 깨지지 않아
새로 클론한 사람도 일단 빌드는 된다.

🔴 **xcconfig를 쓰는 프로젝트에서는 Xcode UI로 빌드 설정을 바꾸지 않는다.**
UI에서 값을 한 번이라도 클릭해 바꾸면 그 값이 `pbxproj`의 **타겟 레벨**에 박히고,
그때부터 xcconfig를 고쳐도 반영되지 않는다. 우선순위가 이렇기 때문이다.

```
1. Target 설정 (pbxproj)   ← 가장 세다
2. Target xcconfig
3. Project 설정 (pbxproj)
4. Project xcconfig
```

값이 안 먹으면 문법을 의심하기 전에 `grep '<키>' <앱>.xcodeproj/project.pbxproj`부터 본다.
→ [xcconfig 우선순위](../xcode/xcconfig-precedence.md)

### Beta는 언제 만드나

**빌드 설정만 보면 Beta와 Release는 거의 같다.**

| | Debug | Beta | Release |
|---|---|---|---|
| 최적화 | 없음 (`-Onone`) | `-O` | `-O` |
| assertion | 켜짐 | 꺼짐 | 꺼짐 |
| 서명 | Development | Distribution | Distribution |
| 배포 | Xcode → 기기 | ASC → TestFlight | App Store |

**Beta가 따로 있는 이유는 최적화가 아니라 구분이다.** TestFlight 빌드와 출시본은 같은
번들 ID로 같은 자리에 설치되므로, 이름으로 가르지 않으면 지금 깔린 게 무엇인지 알 수 없다.

그래서 **TestFlight로 자주 확인하는 앱만 Beta를 둔다.**

| 이럴 때 | 판단 |
|---|---|
| 카메라·센서 등으로 **실기기 TestFlight가 일상**이다 | Beta를 만든다 |
| Xcode 로컬 빌드로 실기기를 확인한다 | Debug·Release로 충분하다 |

🔴 **Beta를 만들면 Release와 같은 최적화·검증으로 굽는다.** TestFlight로 나가는 것은
출시할 것과 같아야 한다. 다른 것은 **이름뿐**이다.

### 빌드를 홈 화면에서 구분한다

세 구성이 **같은 번들 ID**를 쓰면 서로 덮어쓴다. 이름까지 같으면 방금 지운 것이
무엇이었는지 알 수 없다. 그래서 **이름만 가른다.**

| 구성 | `APP_ID_SUFFIX` | `APP_NAME_SUFFIX` | 홈 화면 |
|---|---|---|---|
| Debug | 비움 | `$(EMPTY) (D)` | `Tappie (D)` |
| Beta | 비움 | `$(EMPTY) (B)` | `Tappie (B)` |
| Release | 비움 | 비움 | `Tappie` |

🔴 **번들 ID는 가르지 않는다.** `APP_ID_SUFFIX`를 켜면 ASC에 **새 앱 레코드와 새 IAP가
필요해져 결제 시험이 통째로 막힌다.** 정말 나란히 설치해야 할 때만 켜고, 켜는 순간
결제 관련 작업은 멈춘다는 것을 알고 켠다.

🔴 **`$(EMPTY)`로 앞 공백을 지킨다.** xcconfig는 `=` 바로 뒤의 공백을 잘라내서
`APP_NAME_SUFFIX = (D)`라고 쓰면 `Tappie(D)`로 붙는다. 빈 변수를 앞세우면 그 뒤의 공백이
값의 **안쪽**이 되어 살아남는다.

**Beta는 Release와 같은 최적화·검증으로 굽는다.** TestFlight로 나가는 것은 출시할 것과
같아야 한다. 다른 것은 이름뿐이다.

---

## 배포 — asc CLI 단독

**Fastlane은 폐기했다.** 모든 App Store Connect 작업은 `asc`로 한다.
프로젝트별 실제 명령은 각 저장소 `docs/guide/`에 있다.

🔴 **ASC는 버전 하향을 거부한다.** 마케팅 버전은 위로만 간다.

⚠️ **웹에서만 되는 것들** — 앱 기본 가격(첫 설정) · 연령 등급 · 심사 연락처 ·
판매 지역 · App Privacy. CLI에 명령이 없거나 공개 API로 확인조차 안 된다.

---

