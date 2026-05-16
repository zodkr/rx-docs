# message (오류 표시)

## 개요

- **카테고리**: system
- **역할**: 오류/시스템 메시지를 사용자에게 표시. `MessageView`가 다른 모듈의 에러 처리 폴백.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Message` | `message.class.php` |
| `MessageView` | `message.view.php` |
| `MessageMobile` | `message.mobile.php` |
| `MessageAdminController` | `message.admin.controller.php` |
| `MessageAdminModel` | `message.admin.model.php` |
| `MessageAdminView` | `message.admin.view.php` |

(`message.controller.php`/`message.model.php`/`message.api.php`는 없다 — 메시지 표시는 View가 처리하고, 별도 처리 액션이 없다.)

## 주요 액션 (4개)

| 액션 | 비고 |
|---|---|
| `dispMessage` | 메시지 표시 (기본 메시지 보드) |
| `dispMessageAdminConfig` | 메시지 스킨/색상 관리자 진입 (admin_index) |
| `procMessageAdminInsertConfig` | 설정 저장 |
| `getMessageAdminColorset` | 컬러셋 조회 |

## 동작

`ModuleHandler::_createErrorMessage()`가 에러 발생 시 `MessageView` 인스턴스를 만들어 반환. 기본 템플릿은 `modules/message/skins/default/`.

## 템플릿

- `msg.html` — 일반 메시지.
- `http_status_code.html` — 404/403/500 등.
- `refresh.html` — 리다이렉트 자동 새로고침.

## 관련

- ModuleHandler 라이프사이클: [../06-module-handler-lifecycle.md](../06-module-handler-lifecycle.md)
- Display: [../08-display-and-response.md](../08-display-and-response.md)
