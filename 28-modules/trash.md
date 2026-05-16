# trash (휴지통)

## 개요

- **카테고리**: content
- **역할**: 문서/댓글/파일을 즉시 삭제하지 않고 휴지통으로. 일정 기간 후 영구 삭제 또는 복구.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Trash` | `trash.class.php` |
| `TrashController` | `trash.controller.php` |
| `TrashModel` | `trash.model.php` |
| `TrashView` | `trash.view.php` |
| `TrashAdminController` | `trash.admin.controller.php` |
| `TrashAdminView` | `trash.admin.view.php` |
| `Rhymix\Modules\Trash\Model\TrashVO` | `model/TrashVO.php` (휴지통 항목 VO) |

(`trash.admin.model.php`, `trash.mobile.php`, `trash.api.php`는 없다.)

## 주요 액션 (5개)

| 액션 | 비고 |
|---|---|
| `dispTrashAdminList` | 휴지통 목록 (admin_index) |
| `dispTrashAdminView` | 휴지통 항목 상세 |
| `procTrashAdminEmptyTrash` | 비우기 (ruleset=emptyTrash) |
| `procTrashAdminRestore` | 복구 |
| `procTrashAdminGetList` | 목록 ajax |

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `trash` | `schemas/trash.xml` |

(`trash_module_srls`는 스키마에 없다.)

## 상태 코드

휴지통 항목은 `RX_STATUS_TRASH` (4). 검색/목록에서 자동 제외.

## 트리거

`trash` 모듈은 자체 트리거를 발사하지 않고 `<eventHandlers>`도 등록하지 않는다 (`conf/module.xml` 확인). 휴지통 이동은 호출자(`document.moveDocumentToTrash`/`comment.moveCommentToTrash`)가 발사하는 트리거를 다른 모듈(point 등)이 hook해서 처리한다. trash는 단순 관리자 UI + 모델만 제공.

## 관련

- document: [document.md](document.md)
- comment: [comment.md](comment.md)
- `RX_STATUS_*`: [../12-helpers-and-globals.md](../12-helpers-and-globals.md)
