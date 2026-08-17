---
type: dev-task
date: 2026-08-14
status: active
owner: 원장
source: 세션 9289d822 (2026-08-14) · exam_server.py `_crm_*` 함수군 · 원장이 브라우저에서 복사해 준 cURL
---

# 본사 CRM 연동 구조 (읽기 전용 API)

## Summary
본사 CRM(`crm.adotenglish.com`)에서 **출결·수강등록·강의수강 진도**를 관제로 실시간 당겨오는 구조. 공식 API가 아니라 **본사 화면이 쓰는 내부 JSON 주소를 그대로 호출**한다. 서버가 자동 로그인(OTP 자체 계산)해서 세션을 유지하고, 캐시를 두고, 세션이 끊기면 재로그인한다.

구현 위치: `exam_server.py` `_crm_login` / `_crm_attendance` / `_crm_week` / `_crm_sched` / `_crm_codes` / `_crm_lecture`
관련: [[관제_VPS이전_조교운영_2026-08]] · [[관제대시보드_2026-07확장]]

## 1. 인증

```
POST /inc/login.php?m=login&debugx=1
     ttype=2 · uid · passwd · otp        → PHPSESSID (requests.Session 보관)
```

- **OTP를 서버가 직접 계산한다**(TOTP 30초, `_totp(otp_secret)`). 사람이 앱을 볼 필요 없음.
- 로그인 실패가 반복돼 계정이 잠기지 않도록 **실패 후 30초 백오프**.
- 비밀·시크릿은 파일에만: `/opt/adot-grade/_crm_secrets.json` · `_crm_passwd.txt` (본문에 값 기재 금지)

### ★세션 만료 판정 — 상태코드로는 못 한다
본사는 세션이 끊겨도 **200 OK + 로그인 HTML**을 준다. 그래서 모든 조회는 **응답 첫 글자가 `{` 인지**로 판정하고, 아니면 재로그인 1회 후 재시도한다. 이 패턴을 빠뜨리면 "왜 조용히 빈 값이 오나"로 헤맨다.

## 2. 엔드포인트 (2계열 5개)

| 계열 | 경로 | 주는 것 | 캐시 |
|---|---|---|---|
| attendancebook | `attendance?jijum` | 오늘 등원·하원 | 2초 |
| | `week?jijum&page=N` | 날짜별 출결·지각·결석 | 5분 |
| | `manage?jijum` | 반 요일·시각(예정), 담당T, 반이름 | 조회 시 |
| studentClassManage | `studentList.php` | 학생별 **st_code** + 이름·학년·담당T | 10분 |
| | `getStudentsLatestLectureProgress.php?st_code=` | **최근 7일 강의 진도** | 3분 |

### 호출 규칙에서 실제로 막혔던 지점

- `week`의 `page`는 날짜가 아니라 **2026-06-30을 1주차로 세는 번호**. 최근 N주는 page를 여러 개 돌려 병합.
- `studentList.php`는 **`sort=not_set`이 필수**. 비우면 400(본문 없이). `st_tid`(담당 선생님)는 **비워도 되고, 비워야 지점 전체가 나온다.**
  - ★처음에 "st_tid 필수"로 잘못 판단해 선생님별로 나눠 호출했다 → `teacher_list`가 **403**이라 원장 담당 44명만 들어가고 **정국쌤반 22명이 통째로 누락**(2026-08-14 강채원 "본사 학생 코드를 찾지 못했습니다"). st_tid 없이 한 번 호출 = 66명 전원.
- `st_code`는 학생 로그인 아이디가 **아닌** 본사 내부 코드(예: 정지윤 `20261417641`). 진도 조회 전에 목록 조회가 항상 선행된다.
- `/inc/studentManage/common/teacher_list` = **403**(원장 권한으로도). 쓰지 말 것.
- `/inc/studentManage/authorization` = 200으로 권한 확인 가능(`jik: 원장`, `week: Y`). 진단에 유용.

### 강의 진도 응답 필드 매핑

| 본사 필드 | 우리 이름 | 화면 표기 |
|---|---|---|
| `lec_title` | course | 강좌명 |
| `title` / `movie_sort` | lecture / no | 강의명 / N강 |
| `view_date` | start | 최초 접속 시간 |
| `lm_finish_wdate` | last | 최종 진도 저장 시간 |
| `ltime` | studied | 총 학습 시간 |
| `time` | runtime | 강의 시간(분) |
| `view_type` | device | 시청 기기(android 등) |

## 3. 화면까지 오는 길 (비밀은 서버에 갇힌다)

```
브라우저(hawecontrol.com) — adot_sess 쿠키만. CRM 주소·토큰 모름
   ↓ /api/crm_week · /api/crm_lecture …
dash_server — 로그인 게이트 · 권한 필터 · GRADE_PATHS 프록시
   ↓
exam_server(8097, 내부망 전용) — CRM 세션 · 캐시 · 재로그인
   ↓
crm.adotenglish.com
```

새 CRM 경로를 추가하면 **`server_5173.py`의 `GRADE_PATHS`에도 등록**해야 프록시된다(빠뜨리면 404·"not found").

## 4. 쓰기는 한 곳뿐

결석 자동처리(`attendancecheck/…`)만 본사에 **쓴다**. 나머지는 전부 읽기 전용이라 실수로 본사 데이터를 바꿀 경로가 없다.

## 5. 구조적 리스크 (추측 아님, 설계상 사실)

- 공식 API가 아니라 화면 내부 주소를 빌려 쓰므로 **본사가 화면을 개편하면 조용히 깨진다.** 깨지면 화면에 "조회 실패"로 표시되게 해뒀다.
- 근본 해결 = 본사에서 **읽기 전용 API 계정**을 정식으로 받는 것. 본사 방문·기술 협상 자리에서 요청할 근거로 이 문서를 쓴다(이미 3초 단위로 붙여 운영 중인 실적).

## Links
- [[관제_VPS이전_조교운영_2026-08]]
- [[판정로직_센티널·타이밍_함정]]
