# member (회원)

## 개요

- **카테고리**: member
- **역할**: 회원 가입/로그인/정보/그룹/권한/소셜 연동. 98개 액션으로 가장 큰 모듈 (`modules/member/conf/module.xml`).

## 주요 클래스

| 클래스 | 파일 | 역할 |
|---|---|---|
| `Member` | `member.class.php` | ModuleObject. |
| `MemberController` | `member.controller.php` | 로그인/가입/탈퇴/정보 변경. `doLogin($id, $pw)` 등 헬퍼. |
| `MemberModel` | `member.model.php` | 회원 정보 조회. `getMemberInfo($srl)` 등. |
| `MemberView` | `member.view.php` | 로그인 폼/회원 정보 페이지. |
| `MemberMobile` | `member.mobile.php` | 모바일. |
| `MemberAPI` | `member.api.php` | API. |
| `MemberAdminController/Model/View` | `member.admin.*.php` | 관리자 UI. |

## 주요 액션

98개. 중요한 것:

### 사용자

| 액션 | 비고 |
|---|---|
| `dispMemberLoginForm` | 로그인 폼 |
| `procMemberLogin` | 로그인 처리 |
| `procMemberLogout` | 로그아웃 |
| `dispMemberSignUpForm` | 가입 폼 |
| `procMemberInsert` | 가입 처리 (route=signup) |
| `procMemberCheckValue` | 가입 폼 값 중복 검사 (user_id/email 등 공용) |
| `dispMemberInfo` | 회원 정보 |
| `dispMemberModifyInfo` | 정보 수정 폼 |
| `procMemberModifyInfoBefore` | 비밀번호 재확인 (신뢰 세션 진입) |
| `procMemberModifyInfo` | 정보 수정 처리 |
| `procMemberModifyPassword` | 비밀번호 변경 (ruleset=modifyPassword) |
| `procMemberModifyEmailAddress` | 이메일 변경 (ruleset=modifyEmailAddress) |
| `dispMemberFindAccount` | 계정 찾기 |
| `procMemberFindAccount` / `procMemberFindAccountByQuestion` | 이메일/질문으로 계정 찾기 |
| `procMemberLeave` | 탈퇴 처리 |
| `procMemberInsertProfileImage` / `procMemberInsertImageName` / `procMemberInsertImageMark` | 프로필/이름/마크 이미지 업로드 |

### 관리자

- 회원 조회/검색/일괄 처리.
- 그룹 생성/회원 그룹 할당.
- 사이트 회원 정책 설정 (가입 승인/이메일 인증 등).

## 권한 (grants)

| grant | 기본 | 의미 |
|---|---|---|
| `access` | guest | 모듈 접근 |

회원 모듈은 grant보다 sessions 기반 권한이 더 중요. `MemberController::doLogin()` 내부에서 `Session::login($member_info->member_srl)`로 세션 로그인 처리.

## DB 스키마

실제 `modules/member/schemas/` 17개 테이블:

| 테이블 | 용도 |
|---|---|
| `member` | 회원 기본 정보 |
| `member_group` | 그룹 정의 |
| `member_group_member` | 그룹 ↔ 회원 매핑 |
| `member_agreed` | 약관 동의 기록 |
| `member_auth_mail` | 이메일 인증 토큰 |
| `member_auth_sms` | SMS 인증 토큰 |
| `member_autologin` | 자동 로그인 토큰 |
| `member_count_history` | 회원 수 히스토리 |
| `member_denied_nick_name` | 차단 닉네임 |
| `member_denied_user_id` | 차단 ID |
| `member_devices` | 모바일 디바이스 등록 |
| `member_join_form` | 가입 폼 동적 필드 정의 |
| `member_login_count` | 회원별 로그인 횟수 |
| `member_managed_email_hosts` | 도메인별 가입 정책 |
| `member_nickname_log` | 닉네임 변경 로그 |
| `member_scrap` | 스크랩 |
| `member_scrap_folders` | 스크랩 폴더 |

(`member_extra_info`/`member_password_modified_logs`/`autologin`(prefix 없는) 같은 테이블은 없다. 확장 정보는 `member` 테이블 자체의 컬럼, 자동 로그인은 `member_autologin`.)

## 이 모듈이 정의하는 트리거

| 이름 | 시점 | 호출 위치 |
|---|---|---|
| `member.insertMember` | before/after | `MemberController::insertMember` (`member.controller.php:2868, 3147`) |
| `member.updateMember` | before/after | `MemberController::updateMember` (`member.controller.php:3166, 3462`) |
| `member.deleteMember` | before/after | `MemberController::deleteMember` (`member.controller.php:3548, 3614`) |
| `member.updateMemberEmailAddress` | **after만** | `member.controller.php:3789` (before는 호출되지 않음) |
| `member.doLogin` | before/after | `MemberController::doLogin` (`member.controller.php:2578, 2752`) |
| `member.doLogout` | before/after | `member.controller.php:124, 132` |
| `member.doAutoLogin` | before/after | `member.controller.php:2510, 2551` |
| `member.dispMemberSignUpForm` | **before만** | `MemberView::dispMemberSignUpForm` (`member.view.php:319`) |
| `member.procMemberInsert` | before/after | `member.controller.php:691, 934` |
| `member.procMemberModifyInfo` | before/after | `member.controller.php:1039, 1230` |
| `member.procMemberAuthAccount` | before/after | `member.controller.php:1974, 2053` |
| `member.procMemberCheckValue` | before/after | `member.controller.php:621, 673` |
| `member.procMemberScrapDocument` | before/after | `member.controller.php:244, 258` |
| `member.deleteScrapDocument` | before/after | `member.controller.php:287, 301` |
| `member.addMemberToGroup` | before/after | `member.controller.php:2333, 2353` |
| `member.removeMemberFromGroup` | before/after | `member.controller.php:2379, 2393` |
| `member.insertMemberDevice` | before/after | `Device::procMemberRegisterDevice` (`controllers/Device.php:157, 176`) |
| `member.insertGroup` | before/after | `MemberAdminController` (`member.admin.controller.php:1402, 1436`) |
| `member.updateGroup` | before/after | `member.admin.controller.php:1455, 1487` |
| `member.deleteGroup` | before/after | `member.admin.controller.php:1510, 1533` |
| `member.getMemberMenu` | before/after | `MemberModel::getMemberMenu` (`member.model.php:248, 321`) |

(`member.updateMemberEmailAddress` before는 코드에 없다 — after만 호출된다.)

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `document.getDocumentMenu` (after) | `triggerGetDocumentMenu` (controller) | 문서 메뉴에 회원 관련 항목 추가 (신고/스크랩 등) |
| `comment.getCommentMenu` (after) | `triggerGetCommentMenu` (controller) | 댓글 메뉴에 회원 관련 항목 추가 |
| `document.deleteDocument` (after) | `triggerDeleteDocument` (controller) | 문서 삭제 시 회원 스크랩 정리 |

## 확장 변수

회원 확장 변수(가입 폼 커스텀 필드)는 `member` 테이블의 `extra_vars` 컬럼에 serialize 되어 저장되고, 필드 정의는 `member_join_form` 테이블에 있다. 관리자 → 회원 설정 → 가입 폼에서 필드를 추가한다. (`member_extra_info`는 프로필 이미지/서명 등을 저장하는 files 디렉토리이며 DB 테이블이 아니다.)

## 회원 그룹과 권한

- **그룹** — 사이트 회원 분류 (준회원/정회원/관리자/...).
- **권한** — 각 모듈의 grant에 `:group_srl` 형식으로 부여.

기본 그룹:

- 관리그룹 (`admin_group`, `is_admin = 'Y'`).
- 준회원 (`default_group_1`, 기본 그룹).
- 정회원 (`default_group_2`).

## 이메일/SMS 인증

회원 설정의 `enable_confirm`(이메일 인증 사용)이 'Y'이면 가입 시 이메일 인증 메일 발송. `member_auth_mail` 토큰 검증 후 활성화.

## 소셜 로그인

소셜 로그인은 별도 플러그인 또는 외부 모듈에서 제공. `MemberController::doLogin($id, $pw)`로 자체 회원 매핑.

## 관련 모듈

- `communication` — 쪽지/친구.
- `point` — 포인트.
- `ncenterlite` — 알림.
- `session` — 세션 관리.
- `spamfilter` — 가입 차단.
- `advanced_mailer` — 인증 메일 발송.

## 다음 문서

- 세션/인증: [../15-session-and-auth.md](../15-session-and-auth.md)
- 보안 (비밀번호 등): [../19-security.md](../19-security.md)
- 포인트: [point.md](point.md)
- 커뮤니케이션: [communication.md](communication.md)
