# comment (댓글)

## 개요

- **카테고리**: content
- **역할**: 게시판/블로그/페이지의 **댓글 CRUD** 담당. document 모듈과 짝지어 동작.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Comment` | `comment.class.php` |
| `CommentController` | `comment.controller.php` |
| `CommentModel` | `comment.model.php` |
| `CommentView` | `comment.view.php` |
| `CommentItem` | `comment.item.php` (개별 댓글 객체) |
| `CommentAdminController` | `comment.admin.controller.php` |
| `CommentAdminView` | `comment.admin.view.php` |

(`comment.mobile.php`, `comment.api.php`, `comment.admin.model.php`는 모두 없다 — 모바일/API/관리자 모델은 기본 클래스가 처리.)

## 주요 액션 (20개)

`comment` 모듈의 module.xml에는 댓글 CRUD 자체 액션이 없다 — 댓글 등록/수정/삭제는 호스트 모듈(`board` 등)의 액션(`procBoardInsertComment` 등)이 `CommentController` 인스턴스 메서드를 호출하는 형태.

| 액션 | 비고 |
|---|---|
| `dispCommentDeclare` | 신고 폼 (member) |
| `getCommentMenu` | 댓글 메뉴(권한 기반) |
| `getCommentVotedMemberList` | 추천인 목록 (root) |
| `procCommentVoteUp` / `procCommentVoteUpCancel` | 추천/취소 |
| `procCommentVoteDown` / `procCommentVoteDownCancel` | 비추/취소 |
| `procCommentDeclare` / `procCommentDeclareCancel` | 신고/취소 (member) |
| `procCommentGetList` | 모더레이션 목록 |
| `procCommentInsertModuleConfig` | 댓글 모듈 설정 저장 (manager:config:comment) |
| `dispCommentAdminList` | 신고 댓글 관리 (admin_index) |
| `dispCommentAdminDeclared` / `dispCommentAdminDeclaredLogByCommentSrl` | 신고 관리 |
| `procCommentAdminChangeStatus` / `procCommentAdminChangePublishedStatusChecked` | 상태 변경 |
| `procCommentAdminCancelDeclare` | 신고 취소 |
| `procCommentAdminAddCart` / `procCommentAdminDeleteChecked` / `procCommentAdminMoveToTrash` | 일괄 처리 |

## CommentItem

`comment.item.php`의 실제 메서드 일부. 댓글에는 **제목/`getTitle()`이 없고**, depth/parent_srl/첨부 파일 같은 raw 컬럼은 전용 getter 없이 `BaseObject::get()`으로 접근한다.

```php
$oComment = CommentModel::getComment($comment_srl);
$oComment->isExists();
$oComment->getContent($add_popup_menu = true, $add_content_info = true, $add_xe_content_class = true);
$oComment->getContentPlainText($strlen = 0, $default_content = '');
$oComment->getSummary($str_size = 50, $tail = '...', $default_content = '');
$oComment->getNickName();
$oComment->getMemberSrl();
$oComment->getUserID();
$oComment->getUserName();
$oComment->getRegdate($format = 'Y.m.d H:i:s', $conversion = true);
$oComment->getUpdate($format = 'Y.m.d H:i:s', $conversion = true);
$oComment->getIpAddress();
$oComment->isGranted();          // 작성자 또는 관리자
$oComment->isAccessible($strict = false);
$oComment->isEditable();
$oComment->isSecret();
$oComment->isDeleted();
$oComment->isDeletedByAdmin();
$oComment->getStatus();          // RX_STATUS_*
$oComment->getStatusText();
$oComment->getVote();
$oComment->getMyVote();
$oComment->getDeclared();
$oComment->getThumbnail($width, $height, $thumbnail_type = '');

// 전용 getter가 없는 컬럼은 BaseObject::get()으로 접근
$depth      = $oComment->get('depth');
$parent_srl = $oComment->get('parent_srl');
$module_srl = $oComment->get('module_srl');
$document_srl = $oComment->get('document_srl');

// 첨부 파일은 file 모듈을 직접 호출
$files = FileModel::getFiles($oComment->get('comment_srl'));
```

(`getDepth()`/`getParentSrl()`/`getAttachedFiles()`/`getTitle()` 같은 메서드는 `CommentItem`에 정의되어 있지 않다.)

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `comments` | `schemas/comments.xml` — 댓글 본문 + 메타 |
| `comments_list` | 트리 정렬 인덱스 |
| `comment_voted_log` | 추천 로그 |
| `comment_declared` | 신고 합계 |
| `comment_declared_log` | 신고 로그 |

## 트리

`comments`는 평면 저장. `comment_list`가 트리 정렬을 위한 별도 인덱스 (depth, head, arrange).

`getCommentList($document_srl, $sort='oldest')` 호출 시 join + sort.

## 이 모듈이 정의하는 트리거

| 이름 | 시점 | 호출 위치 |
|---|---|---|
| `comment.insertComment` | before/after | `CommentController::insertComment` (`comment.controller.php:604, 818`) |
| `comment.updateComment` | before/after | `CommentController::updateComment` (`comment.controller.php:1001, 1085`) |
| `comment.deleteComment` | before/after | `CommentController::deleteComment` (`comment.controller.php:1120, 1163`, `:1256, 1352`, `:1541, 1548`) |
| `comment.moveCommentToTrash` | before/after (단수) | `comment.controller.php:1410, 1484` (+`comment.admin.controller.php:370`) |
| `comment.updateVotedCount` | before/after | `comment.controller.php:1689, 1720` |
| `comment.updateVotedCountCancel` | before/after | `comment.controller.php:299, 330` |
| `comment.declaredComment` | before/after | `comment.controller.php:1777, 1893` |
| `comment.declaredCommentCancel` | before/after | `comment.controller.php:1957, 2017` |
| `comment.copyCommentByDocument` | add | `comment.controller.php:2262` |
| `comment.copyCommentByDocument.each` | before/after (한 댓글마다) | `comment.controller.php:2263, 2268` |
| `comment.getCommentMenu` | before/after | `CommentModel::getCommentMenu` (`comment.model.php:39, 96`) |
| `comment.getCommentList` | before/after | `CommentModel::getCommentList` (`comment.model.php:566, 600`) |
| `comment.getTotalCommentList` | before/after | `CommentModel::getTotalCommentList` (`comment.model.php:954, 1027`) |
| `comment.getThumbnail` | before | `CommentItem::getThumbnail` (`comment.item.php:841`) |
| `comment.procCommentAdminChangeStatus` | after | `CommentAdminController::procCommentAdminChangeStatus` (`comment.admin.controller.php:147`) |
| `comment.sendEmailToAdminAfterInsertComment` | after | `CommentController` 내부 (`comment.controller.php:943`) |

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `document.deleteDocument` (after) | `triggerDeleteDocumentComments` (controller) | 문서 삭제 시 댓글 일괄 삭제 |
| `module.deleteModule` (after) | `triggerDeleteModuleComments` (controller) | 모듈 삭제 시 댓글/추천/신고 데이터 삭제 |
| `module.procModuleAdminCopyModule` (after) | `triggerCopyModule` (controller) | 모듈 복사 시 댓글 설정 복사 |
| `document.moveDocumentModule` (after) | `triggerMoveDocument` (controller) | 문서 이동 시 댓글 `module_srl` 갱신 |
| `document.copyDocumentModule.each` (before) | `triggerAddCopyDocument` (controller) | 문서 복사 시 댓글 복제 |
| `module.dispAdditionSetup` (before) | `triggerDispCommentAdditionSetup` (view) | 관리자 모듈 설정 UI에 댓글 옵션 추가 |

## 권한

- `comment_write` — 댓글 쓰기.
- `comment_view` — 보기.

상위 모듈(board 등)의 grant에서 위임됨.

## 상태 (status)

- `RX_STATUS_PUBLIC` — 공개.
- `RX_STATUS_SECRET` — 비밀 댓글.
- `RX_STATUS_TRASH` — 휴지통.

## 관련 모듈

- `document` — 부모 문서.
- `board` — 사용자 UI.
- `file` — 첨부.
- `point` — 댓글 작성 포인트.
- `ncenterlite` — 댓글 알림.
- `trash` — 휴지통.

## 다음 문서

- 문서: [document.md](document.md)
- 게시판: [board.md](board.md)
