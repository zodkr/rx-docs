# login_info (위젯)

## 개요

- **목적**: 사이드바/헤더의 로그인 박스. 비로그인 시 로그인 폼(`login_form.html`), 로그인 시 환영 정보(`login_info.html`).

## proc() 인자 (`$args`)

`widgets/login_info/conf/info.xml`의 extra_vars는 **1개뿐**.

| 인자 | 타입 | 의미 |
|---|---|---|
| `ncenter_use` | `select` (`yes`/`no`, 기본 `no`) | 알림센터(ncenterlite) 패널을 함께 표시 |
| `$args->skin` | (자동) | 스킨 |
| `$args->colorset` | (자동) | 컬러셋 |

가입 링크/계정 찾기/환영 메시지 등은 모두 **스킨이 결정**한다.

## proc() 동작 (`login_info.class.php`)

순서대로:

1. `Context::set('colorset', $args->colorset)`.
2. `Context::get('is_logged')` 캐싱.
3. **`MemberModel::getMemberConfig()`로 회원 모듈 설정 로드** — 로그인/비로그인 상관없이 무조건 호출(`:28`).
4. **`getModel('ncenterlite')->getConfig()`로 알림센터 설정 로드** — 마찬가지로 무조건 호출(`:29-30`). 따라서 `ncenterlite` 모듈이 비활성/삭제된 상태에서는 `getModel('ncenterlite')`이 `null`을 반환하고 다음 `->getConfig()` 호출이 fatal error를 일으킨다. 코어에서는 항상 동봉되므로 정상 환경에서는 문제없음.
5. **로그인 상태** (`is_logged` truthy):
   - `$args->ncenter_use === 'yes'`이면:
     - `NcenterliteModel::getMyNotifyList($logged_info->member_srl)` 호출 → `data`/`page_navigation` 보관.
     - `_latest_notify_id` = 가장 최근 알림의 `notify` 값.
     - 회원 설정의 `profile_image == 'Y'`면 `MemberModel::getProfileImage($member_srl)`로 `profileImage` 주입.
     - `Context::set('ncenterlite_latest_notify_id', $_latest_notify_id)`.
     - **`_ncenterlite_hide_id` 쿠키가 `_latest_notify_id`와 일치하면 `return;` 즉시 종료** — 위젯이 아무 HTML도 반환하지 않는다 (이후의 컨텍스트 주입/스킨 컴파일/공통 ssl_mode 설정까지 모두 건너뜀). 일치하지 않으면:
     - `_ncenterlite_hide_id` 쿠키가 비어있지 않으면 `setcookie('_ncenterlite_hide_id', '', 0, '/')`로 정리.
     - `$ncenter_config->zindex`가 있으면 `ncenterlite_zindex` 인라인 style 문자열 주입.
     - `ncenterlite_list` / `ncenterlite_page_navigation` / `_ncenterlite_num` 주입.
   - 스킨 진입 파일: `login_info`.
6. **비로그인 상태**:
   - 스킨 진입 파일: `login_form`.
7. 공통(위 `return;`을 만나지 않은 경우): `useProfileImage` (`profile_image == 'Y'` boolean), `member_config`, `ssl_mode` 컨텍스트 주입.
   - `ssl_mode`는 `Context::getSslStatus() !== 'none'`이고 현재 요청 URI가 `https://`로 시작하면 `true`, 아니면 `false`.
8. `TemplateHandler::getInstance()->compile($tpl_path, $tpl_file)` 반환.

## 스킨

`widgets/login_info/skins/`:

- `default` — 표준 로그인 박스 (`login_form.html`/`login_info.html`).
- `ncenter_login` — 알림(ncenterlite) 정보 강조 변형.

## 관련

- member: [../28-modules/member.md](../28-modules/member.md)
- session: [../15-session-and-auth.md](../15-session-and-auth.md)
- ncenterlite: [../28-modules/ncenterlite.md](../28-modules/ncenterlite.md)
