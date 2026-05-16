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
| `procSessionAdminClear` | 모든 세션 강제 만료 |

세션 저장소 관련 read/write/destroy/gc는 메서드(인스턴스)로만 제공되며 module.xml 액션이 아니다 (`SessionController`/`SessionModel`이 PHP `session_set_save_handler`로 등록됨, `Context::init` 단계).

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `session` | `schemas/session.xml` — DB 세션 저장 (활성 시, 단수) |

## 관련

- 세션/인증: [../15-session-and-auth.md](../15-session-and-auth.md)
- `Rhymix\Framework\Session`: [../15-session-and-auth.md](../15-session-and-auth.md)
