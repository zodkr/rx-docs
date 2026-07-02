# session (세션 관리)

## 개요

- **카테고리**: system
- **역할**: PHP 세션 저장소 관리. DB 세션 저장 시 `session` 테이블 관리.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Session` | `session.class.php` |
| `SessionController` | `session.controller.php` |
| `SessionModel` | `session.model.php` |
| `SessionAdminController` | `session.admin.controller.php` |
| `SessionAdminView` | `session.admin.view.php` |

(`session.view.php`, `session.admin.model.php`, `session.mobile.php`, `session.api.php`는 없다.)

## 주요 액션 (2개)

| 액션 | 비고 |
|---|---|
| `dispSessionAdminIndex` | 세션 관리자 화면 (admin_index) |
| `procSessionAdminClear` | 만료된 세션 정리 (`gc(0)` 호출 → `session.gcSession`이 `expired < curdate()`인 세션만 삭제; 활성 세션은 영향 없음) |

세션 저장소 관련 read/write/destroy/gc는 메서드(인스턴스)로만 제공되며 module.xml 액션이 아니다 (`SessionController`가 `SessionHandlerInterface`를 구현하여 read/write/open/close/destroy/gc를 제공하며, `Context::init` 단계에서 DB 세션 사용 시(비 CLI 요청) `session_set_save_handler(SessionController::getInstance(), true)`로 등록된다).

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `session` | `schemas/session.xml` — DB 세션 저장 (활성 시, 단수) |

## 관련

- 세션/인증: [../15-session-and-auth.md](../15-session-and-auth.md)
- `Rhymix\Framework\Session`: [../15-session-and-auth.md](../15-session-and-auth.md)
