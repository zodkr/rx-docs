# tag (태그)

## 개요

- **카테고리**: content
- **역할**: 문서 태그 관리.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Tag` | `tag.class.php` |
| `TagController` | `tag.controller.php` |
| `TagModel` | `tag.model.php` |
| `TagAdminController` | `tag.admin.controller.php` |
| `TagAdminView` | `tag.admin.view.php` |

(`tag.view.php`, `tag.admin.model.php`, `tag.mobile.php`, `tag.api.php`는 없다.)

## 주요 액션 (2개)

| 액션 | 비고 |
|---|---|
| `dispTagAdminConfig` | 태그 관리자 설정 (admin_index) |
| `procTagAdminInsertConfig` | 설정 저장 |

(태그 모듈은 사용자 진입 액션을 두지 않는다 — `dispTagIndex` 같은 페이지는 없음.)

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `tags` | `schemas/tags.xml` — 태그 ↔ 문서 매핑 (`tag_srl`(PK), `tag`, `document_srl`, `module_srl`, `regdate`) |

## 동작

- `document.insertDocument.after` 트리거로 문서의 `tags` 필드 파싱해서 `tags` 테이블에 등록.
- 태그 클릭 시 같은 태그의 다른 문서 목록 표시.

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

자체적으로 정의하는 트리거는 없다. 모두 다른 모듈 트리거에 hook해서 동작한다.

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `document.insertDocument` (before) | `triggerArrangeTag` (controller) | 입력된 태그 문자열 정규화 |
| `document.insertDocument` (after) | `triggerInsertTag` (controller) | 정규화된 태그를 `tags` 테이블에 등록 |
| `document.updateDocument` (before) | `triggerArrangeTag` (controller) | 수정 시 태그 정규화 |
| `document.updateDocument` (after) | `triggerInsertTag` (controller) | 수정 시 태그 재등록 |
| `document.deleteDocument` (after) | `triggerDeleteTag` (controller) | 문서 삭제 시 태그 매핑 정리 |
| `module.deleteModule` (after) | `triggerDeleteModuleTags` (controller) | 모듈 삭제 시 태그 일괄 정리 |
| `document.moveDocumentModule` (after) | `triggerMoveDocument` (controller) | 문서 이동 시 `module_srl` 갱신 |

## 관련

- document: [document.md](document.md)
