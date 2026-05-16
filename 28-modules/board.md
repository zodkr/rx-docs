# board (게시판)

## 개요

- **카테고리**: service
- **역할**: 게시판 운영 — 글 목록/상세/쓰기/댓글/카테고리 관리.
- 가장 많이 쓰이는 모듈. `document` + `comment` + `file` 모듈을 결합해 게시판 UX를 구성.

## 주요 클래스

| 클래스 | 파일 | 역할 |
|---|---|---|
| `Board` | `board.class.php` | ModuleObject. 설치/업데이트 hook. |
| `BoardController` | `board.controller.php` | 글/댓글 처리 (`procBoardInsertDocument` 등). |
| `BoardModel` | `board.model.php` | 게시판 메타 조회. |
| `BoardView` | `board.view.php` | HTML 렌더 (`dispBoardContent`, `dispBoardWrite`). |
| `BoardApi` | `board.api.php` | JSON/API. |
| `BoardMobile` | `board.mobile.php` | 모바일 분기. |
| `BoardAdminController` | `board.admin.controller.php` | 게시판 관리 액션. |
| `BoardAdminModel` | `board.admin.model.php` | 관리자 조회. |
| `BoardAdminView` | `board.admin.view.php` | 관리자 UI. |

## 주요 액션

총 46개 액션 (`modules/board/conf/module.xml`). 일부만 발췌.

### 사용자 (disp/proc)

| 액션 | 권한 | 라우트 |
|---|---|---|
| `dispBoardContent` | `list` | `/<mid>` (인덱스), `/<mid>/$document_srl`, `/<mid>/category/$cat` |
| `dispBoardWrite` | `write_document` | `/<mid>/write`, `/<mid>/$document_srl/edit` |
| `dispBoardDelete` | `write_document` | `/<mid>/$document_srl/delete` |
| `dispBoardWriteComment` | `write_comment` | `/<mid>/$document_srl/comment` |
| `dispBoardReplyComment` | `write_comment` | `/<mid>/comment/$comment_srl/reply` |
| `dispBoardModifyComment` / `dispBoardDeleteComment` | `write_comment` | `/<mid>/comment/$comment_srl/edit`/`/delete` |
| `procBoardInsertDocument` / `procBoardDeleteDocument` / `procBoardRevertDocument` | `write_document` / `update_view` | (POST) |
| `procBoardInsertComment` / `procBoardDeleteComment` | `write_comment` | (POST) |
| `procBoardVoteDocument` | `view` | (POST) — 추천/비추천 통합 |
| `procBoardVerificationPassword` | `view` | (POST) — 비밀글 비밀번호 |

### 관리자 (Admin)

- `dispBoardAdminContent` — 게시판 관리 진입(admin_index).
- `dispBoardAdminInsertBoard` / `dispBoardAdminDeleteBoard` — 게시판 생성/삭제.
- `dispBoardAdminBoardInfo` / `dispBoardAdminCategoryInfo` / `dispBoardAdminExtraVars` / `dispBoardAdminGrantInfo` / `dispBoardAdminBoardAdditionSetup` — 게시판 설정 화면.
- `dispBoardAdminSkinInfo` / `dispBoardAdminMobileSkinInfo` — 스킨 설정.
- `procBoardAdminInsertBoard` / `procBoardAdminDeleteBoard` / `procBoardAdminUpdateBoard` / `procBoardAdminInsertCombinedConfig` / `procBoardAdminSaveCategorySettings` — 처리.
- `getBoardAdminSimpleSetup` — 간이 설정 진입.

## 권한 (grants)

| grant | 기본 | 의미 |
|---|---|---|
| `list` | guest | 목록 보기 |
| `view` | guest | 상세 보기 |
| `write_document` | guest | 글 쓰기 |
| `write_comment` | guest | 댓글 쓰기 |
| `vote_log_view` | member | 추천인 보기 |
| `update_view` | member | 수정 이력 보기 |
| `consultation_read` | manager | 상담글 열람 |

## DB 스키마

board 모듈은 **자체 스키마 테이블이 전혀 없다** (`modules/board/schemas/`는 비어 있음). 모든 데이터는 `document`/`comment`/`file`/`document_categories` 등 다른 모듈 테이블을 그대로 사용한다.

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `member.getMemberMenu` (after) | `triggerMemberMenu` (controller) | 회원 메뉴(글/댓글 보기 등)에 게시판 항목 추가 |
| `menu.getModuleListInSitemap` (after) | `triggerModuleListInSitemap` (model) | 메뉴 관리 사이트맵에 board 인스턴스 노출 |
| `module.procModuleAdminCopyModule` (after) | `triggerCopyModule` (controller) | 게시판 복사 시 board 고유 설정 복사 |

## 이 모듈이 정의하는 트리거

자체 도메인 트리거는 없다. board 모듈은 `module.dispAdditionSetup` (before/after)을 `BoardAdminView`(`board.admin.view.php:215-216`)에서 호출하지만, 그 트리거 자체는 module 모듈이 정의하는 것이다. board 액션의 표준 act 트리거(`act:board.<액션>.before/after`)는 코어 ModuleObject가 모든 액션에서 자동 발사한다.

## 관련 모듈

- `document` — 글 데이터.
- `comment` — 댓글.
- `file` — 첨부.
- `point` — 글/댓글 작성 시 포인트 지급.
- `tag` — 태그 처리.
- `trash` — 삭제 시 휴지통.
- `ncenterlite` — 알림 발송.

## 확장 포인트

- **스킨**: `modules/board/skins/<skin>/` (PC), `m.skins/<mskin>/` (모바일). 표준 진입 템플릿: `list.html`, `view.html`, `write_form.html`, `comment_form.html`, `delete_form.html`, ...
- **카테고리**: 관리자 UI로 트리 구조 관리.
- **상담형 게시판**: `consultation_read` grant + 별도 템플릿.

## 다음 문서

- 문서: [document.md](document.md)
- 댓글: [comment.md](comment.md)
- 첨부: [file.md](file.md)
- 모듈 스킨 작성: [../27-extension-points/module-skin.md](../27-extension-points/module-skin.md)
