# poll (설문)

## 개요

- **카테고리**: content
- **역할**: 설문조사 생성/투표/결과 표시.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Poll` | `poll.class.php` |
| `PollController` | `poll.controller.php` |
| `PollModel` | `poll.model.php` |
| `PollAdminController` | `poll.admin.controller.php` |
| `PollAdminModel` | `poll.admin.model.php` |
| `PollAdminView` | `poll.admin.view.php` |

(`poll.view.php`, `poll.mobile.php`, `poll.api.php`는 없다.)

## 주요 액션 (17개)

| 액션 | 비고 |
|---|---|
| `getPollstatus` / `getPollinfo` / `getPollitemInfo` | 설문/항목 정보 모델 |
| `getPollGetColorsetList` | 컬러셋 |
| `procPollInsert` | 설문 등록 (이미 본문에 마커 형태로) |
| `procPollInsertItem` / `procPollDeleteItem` | 항목 추가/삭제 (member) |
| `procPoll` | 투표 처리 (ruleset=poll) |
| `procPollViewResult` | 결과 보기 처리 |
| `procPollGetList` | 결과 목록 (root) |
| `dispPollAdminList` | 관리자 목록 (admin_index) |
| `dispPollAdminResult` / `dispPollAdminConfig` | 결과/설정 화면 |
| `getPollAdminTarget` | 관리자 대상 조회 |
| `procPollAdminAddCart` / `procPollAdminDeleteChecked` | 일괄 처리 (ruleset=deleteChecked) |
| `procPollAdminInsertConfig` | 설정 저장 (ruleset=insertConfig) |

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `poll` | `schemas/poll.xml` — 설문 마스터 (단수) |
| `poll_title` | `schemas/poll_title.xml` — 설문 제목 |
| `poll_item` | `schemas/poll_item.xml` — 설문 항목 (단수) |
| `poll_log` | `schemas/poll_log.xml` — 투표 로그 (단수) |

## 위젯/에디터 컴포넌트

- 위젯: `widgets/pollWidget/` — 사이트에 설문 표시.
- 에디터 컴포넌트: `modules/editor/components/poll_maker/` — 본문에 설문 삽입.

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

자체적으로 정의하는 트리거는 없다. document/comment 라이프사이클에 hook해서 본문 안에 삽입된 설문 마커를 처리한다.

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `document.insertDocument` (after) | `triggerInsertDocumentPoll` (controller) | 본문의 설문 마커를 등록하고 `document_srl`과 연결 |
| `document.updateDocument` (after) | `triggerUpdateDocumentPoll` (controller) | 본문 수정 시 설문 동기화 |
| `document.deleteDocument` (after) | `triggerDeleteDocumentPoll` (controller) | 문서 삭제 시 설문 정리 |
| `comment.insertComment` (after) | `triggerInsertCommentPoll` (controller) | 댓글 내 설문 처리 |
| `comment.updateComment` (after) | `triggerUpdateCommentPoll` (controller) | 댓글 수정 시 설문 동기화 |
| `comment.deleteComment` (after) | `triggerDeleteCommentPoll` (controller) | 댓글 삭제 시 설문 정리 |

## 관련

- 위젯: [../30-widgets/pollWidget.md](../30-widgets/pollWidget.md)
- 에디터 컴포넌트: [../33-editor-components/poll_maker.md](../33-editor-components/poll_maker.md)
