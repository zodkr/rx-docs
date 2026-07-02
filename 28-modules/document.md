# document (문서)

## 개요

- **카테고리**: content
- **역할**: 게시판/블로그/페이지 등 모든 콘텐츠의 **문서 데이터 저장과 조회**. board/blog/page 등 거의 모든 콘텐츠 모듈이 의존.

## 주요 클래스

| 클래스 | 파일 | 역할 |
|---|---|---|
| `Document` | `document.class.php` | ModuleObject. 설치/업데이트. |
| `DocumentController` | `document.controller.php` | `insertDocument`/`updateDocument`/`deleteDocument` 등 CRUD. |
| `DocumentModel` | `document.model.php` | 조회, 알리아스 변환, 권한 검사. |
| `DocumentView` | `document.view.php` | 관리자 외 HTML 액션. |
| `DocumentItem` | `document.item.php` | **개별 문서 객체** — 템플릿/뷰에서 자주 사용. |
| `DocumentAdminController` | `document.admin.controller.php` | 관리자 처리. |
| `DocumentAdminModel` | `document.admin.model.php` | 관리자 조회. |
| `DocumentAdminView` | `document.admin.view.php` | 관리자 UI. |

(`document.mobile.php`, `document.api.php`는 없다 — 모바일/API 요청도 기본 View/Controller가 응답.)

## DocumentItem (자주 사용)

```php
$oDoc = DocumentModel::getDocument($document_srl);
$oDoc->isExists();
$oDoc->getTitle($cut_size = 0, $tail = '...');
$oDoc->getContent($add_popup_menu=true, $add_content_info=true, ...);
$oDoc->getContentPlainText($strlen = 0);
$oDoc->getSummary($str_size = 50, $tail = '...');
$oDoc->getNickName();
$oDoc->getMemberSrl();
$oDoc->getRegdate($format = 'Y.m.d H:i:s', $conversion = true);
$oDoc->getStatus();             // RX_STATUS_*
$oDoc->isAccessible($strict = false);
$oDoc->isGranted();             // 작성자 또는 관리자
$oDoc->getThumbnail($width = 80, $height = 0, $thumbnail_type = '');
$oDoc->getCommentCount();
$oDoc->getComments(?int $page = null);   // 댓글 트리 (getCommentList 아님)
$oDoc->getExtraValue($idx);     // 확장 변수
$oDoc->getExtraVars();          // 전체 (extravar Value 객체 배열)
$oDoc->getUrl();
$oDoc->getPermanentUrl();
$oDoc->getTags();
```

> 첨부 파일은 `$oDoc->hasUploadedFiles()`, `$oDoc->getUploadedFiles($sortIndex = 'file_srl')`로 조회한다(내부적으로 `FileModel::getFiles(..., 'doc', ...)` 호출).

## 주요 액션

총 45개 (`modules/document/conf/module.xml`). 일부:

| 액션 | 비고 |
|---|---|
| `dispDocumentPrint` / `dispDocumentPreview` | 인쇄/미리보기 |
| `dispDocumentDeclare` | 신고 폼 (member) |
| `dispTempSavedList` / `procDocumentTempSave` / `procDocumentDeleteTempSaved` | 임시저장 (member) |
| `procDocumentVoteUp` / `procDocumentVoteUpCancel` / `procDocumentVoteDown` / `procDocumentVoteDownCancel` | 추천/비추 +취소 |
| `procDocumentDeclare` / `procDocumentDeclareCancel` | 신고/취소 |
| `getDocumentMenu` | 메뉴 데이터 (모든 모듈에서 호출) |
| `getDocumentCategories` / `getDocumentCategoryTree` | (all-managers) 카테고리 |
| `procDocumentInsertModuleConfig` / `procDocumentInsertCategory` / `procDocumentDeleteCategory` / `procDocumentMoveCategory` | 모듈/카테고리 설정 |
| `dispDocumentAdminList` 등 6개 disp Admin / `procDocumentAdmin*` 13개 | 관리자 |

> 문서 등록/수정/삭제(`procDocument*Document`)는 module.xml에 **액션으로 등록되지 않음** — `DocumentController` 인스턴스 메서드로 다른 모듈(board 등)이 직접 호출한다.

## 권한 (grants)

document 모듈은 `conf/module.xml`에 `<grants />`(비어 있음)만 두어 자체 권한을 정의하지 않는다. 목록/열람/글·댓글 작성/추천인 보기 등의 권한은 document를 사용하는 board(`modules/board/conf/module.xml`) 같은 콘텐츠 모듈이 정의한다.

## DB 스키마

| 테이블 | 용도 |
|---|---|
| `documents` | 문서 본문 + 메타. |
| `document_extra_keys` | 확장 변수 정의. |
| `document_extra_vars` | 확장 변수 값. |
| `document_categories` | 카테고리 정의 (게시판별). |
| `document_voted_log` | 추천 로그. |
| `document_declared` | 신고 합계. |
| `document_declared_log` | 신고 로그. |
| `document_histories` | 수정 이력 (복수형). |
| `document_update_log` | 수정 변경 사항 (어드민 모더레이션용). |
| `document_aliases` | URL alias → document_srl. |
| `document_readed_log` | 조회 로그. |
| `document_trash` | 삭제 대기 (단수). |

## 이 모듈이 정의하는 트리거

| 이름 | 시점 | 호출 위치 |
|---|---|---|
| `document.insertDocument` | before/after | `DocumentController::insertDocument` (`document.controller.php:723, 948`) |
| `document.publishDocument` | before/after | `insertDocument`/`updateDocument` 내부 (TEMP→PUBLIC 전환 시) |
| `document.updateDocument` | before/after | `DocumentController::updateDocument` (`document.controller.php:1044, 1414`) |
| `document.deleteDocument` | before/after | `DocumentController::deleteDocument` (`document.controller.php:1488, 1544`) |
| `document.moveDocumentToTrash` | before/after (단수) | `document.controller.php:1630, 1687` |
| `document.restoreTrash` | after | `DocumentAdminController::procDocumentAdminRestoreTrash` (`document.admin.controller.php:888`) |
| `document.moveDocumentModule` | before/after | `document.admin.controller.php:659, 703` |
| `document.copyDocumentModule` | before/after/add | `document.admin.controller.php:756, 792, 818` |
| `document.copyDocumentModule.each` | before/after (한 문서마다) | `document.admin.controller.php:793, 812` |
| `document.getDocumentList` | before/after | `DocumentModel::getDocumentList` (`document.model.php:264, 309`) |
| `document.getNoticeList` | before/after | `DocumentModel::getNoticeList` (`document.model.php:329, 366`) |
| `document.getDocumentMenu` | before/after | `DocumentModel::getDocumentMenu` (`document.model.php:537, 599`) |
| `document.updateReadedCount` | before/after | `document.controller.php:1714, 1779` |
| `document.updateVotedCount` | before/after | `document.controller.php:2137, 2177` |
| `document.updateVotedCountCancel` | before/after | `document.controller.php:321, 358` |
| `document.declaredDocument` | before/after | `document.controller.php:2238, 2354` |
| `document.declaredDocumentCancel` | before/after | `document.controller.php:2417, 2477` |
| `document.insertCategory` | before/after | `document.controller.php:2551, 2568` |
| `document.updateCategory` | before/after | `document.controller.php:2627, 2643` |
| `document.deleteCategory` | before/after | `document.controller.php:2670, 2703` |
| `document.manage` | before/after | `DocumentController::procDocumentManageCheckedDocument` (`document.controller.php:3517, 3611`) |
| `document.getComments` | after | `DocumentItem::getComments` (`document.item.php:1070`) |
| `document.getThumbnail` | before | `DocumentItem::getThumbnail` (`document.item.php:1164`) |

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `module.deleteModule` (after) | `triggerDeleteModuleDocuments` (controller) | 모듈 삭제 시 모든 문서/카테고리/확장변수 삭제 |
| `module.procModuleAdminCopyModule` (after) | `triggerCopyModuleExtraKeys` (controller) | 모듈 복사 시 확장 변수 키 복사 |
| `module.procModuleAdminCopyModule` (after) | `triggerCopyModule` (controller) | 모듈 복사 시 문서 데이터 복사 |
| `file.deleteFile` (after) | `triggerAfterDeleteFile` (controller) | 첨부 삭제 후 본문 내 파일 마커 정리 |
| `module.dispAdditionSetup` (before) | `triggerDispDocumentAdditionSetup` (view) | 관리자 모듈 설정 UI에 문서 옵션 추가 |

## 확장 변수 (extra_vars)

게시판마다 다른 사용자 정의 필드. `document_extra_keys`에 정의, `document_extra_vars`에 값.

```php
$value = $oDoc->getExtraValue('my_field');
$all = $oDoc->getExtraVars();   // extravar Value 객체 배열
```

## status

문서 상태는 `RX_STATUS_*` 상수 사용.

| 상수 | 값 | 의미 |
|---|---|---|
| `RX_STATUS_PUBLIC` | 1 | 공개 |
| `RX_STATUS_SECRET` | 2 | 비밀글 |
| `RX_STATUS_TEMP` | 0 | 임시 저장 |
| `RX_STATUS_TRASH` | 4 | 휴지통 |
| `RX_STATUS_DELETED` | 7 | 삭제 |

## 관련 모듈

- `board`, `blog`(3rd party) — 사용자 UI.
- `comment` — 댓글.
- `file` — 첨부.
- `tag` — 태그.
- `point` — 작성 시 포인트.
- `trash` — 휴지통.
- `extravar` — 확장 변수 관리.

## 다음 문서

- 게시판: [board.md](board.md)
- 댓글: [comment.md](comment.md)
- 첨부: [file.md](file.md)
- 확장 변수: [extravar.md](extravar.md)
