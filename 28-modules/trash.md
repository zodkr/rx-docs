# trash (휴지통)

## 개요

- **카테고리**: content
- **역할**: 문서/댓글 원본 행을 삭제하기 전에 직렬화 사본을 `trash` 테이블에 보관하여 관리자의 복구·영구 삭제(비우기)를 지원.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Trash` | `trash.class.php` |
| `TrashController` | `trash.controller.php` |
| `TrashModel` | `trash.model.php` |
| `TrashView` | `trash.view.php` |
| `TrashAdminController` | `trash.admin.controller.php` |
| `TrashAdminView` | `trash.admin.view.php` |
| `TrashVO` | `model/TrashVO.php` (휴지통 항목 VO, 네임스페이스 없는 전역 클래스. `trash.class.php:3`이 `require_once`로 로드하며 document/comment 컨트롤러도 사용 전 동일하게 require_once한다) |

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

## 상태 코드 (미사용)

휴지통 이동은 상태 플래그를 쓰지 않는다. 원본 문서/댓글은 해당 테이블에서 완전히 삭제되고(`document.controller.php:1657`의 `executeQuery('document.deleteDocument', ...)`, `comment.controller.php:1440`의 `executeQuery('comment.deleteComment', ...)`), 직렬화된 사본이 별도의 `trash` 테이블에 저장된다. `trash` 테이블에는 status 컬럼 자체가 없다 (`schemas/trash.xml`). 목록/검색에서 사라지는 것은 상태 필터 때문이 아니라 원본이 삭제되었기 때문이다.

`RX_STATUS_TRASH`(4)는 댓글의 숫자형 상태 코드이고, 문서의 대응 상태는 별도 문자열 `TRASH`다. 둘 다 `trash` 테이블 자체에는 적용되지 않는다.

## 트리거

`trash` 모듈은 자체 트리거를 발사하지 않고 `<eventHandlers>`도 등록하지 않는다 (`conf/module.xml` 확인). 휴지통 이동은 호출자(`document.moveDocumentToTrash`/`comment.moveCommentToTrash`)가 발사하는 트리거를 다른 모듈(point 등)이 hook해서 처리한다. trash 자체는 이벤트 없이 관리자 View/Controller와 Model로 저장·목록·비우기·복구를 수행한다 (`trash.admin.controller.php:18-28,36-67,76-128`).

## 관련

- document: [document.md](document.md)
- comment: [comment.md](comment.md)
- `RX_STATUS_*`: [../12-helpers-and-globals.md](../12-helpers-and-globals.md)
