# ncenterlite (알림 센터)

## 개요

- **카테고리**: service
- **역할**: 사용자간 활동 알림 (댓글/추천/쪽지/멘션 등). 헤더 알림 벨, 알림함, 푸시 발송 통합.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Ncenterlite` | `ncenterlite.class.php` |
| `NcenterliteController` | `ncenterlite.controller.php` |
| `NcenterliteModel` | `ncenterlite.model.php` |
| `NcenterliteView` | `ncenterlite.view.php` |
| `NcenterliteMobile` | `ncenterlite.mobile.php` |
| `NcenterliteAdminController/Model/View` | `ncenterlite.admin.*.php` |

(`ncenterlite.api.php`는 없다.)

## 주요 액션 (23개)

| 액션 | 비고 |
|---|---|
| `dispNcenterliteNotifyList` | 알림함 (route=notifications) |
| `dispNcenterliteUserConfig` | 사용자 알림 설정 |
| `dispNcenterliteUnsubscribeList` | 구독 해제 목록 |
| `dispNcenterliteInsertUnsubscribe` | 구독 해제 추가 |
| `procNcenterliteUserConfig` | 사용자 설정 저장 |
| `procNcenterliteNotifyReadAll` | 모두 읽음 처리 |
| `procNcenterliteRedirect` | 알림 클릭 → 대상 URL 리다이렉트 |
| `procNcenterliteInsertUnsubscribe` | 구독 해제 처리 |
| `getMyNotifyListTpl` | 알림 목록 ajax 템플릿 |
| `getColorsetList` | (root) 컬러셋 |
| `dispNcenterliteAdminConfig` 외 7개 Admin disp | 관리자 설정 화면 (Advanced/Seletedmid/Skinsetting/Test/List/CustomList/OtherComment) |
| `procNcenterliteAdminInsertConfig` / `InsertDummyData` / `InsertPushData` / `DeleteNofity` / `DeleteCustom` | 관리자 처리 |

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `ncenterlite_notify` | `schemas/ncenterlite_notify.xml` — 알림 |
| `ncenterlite_notify_type` | 알림 유형 정의 |
| `ncenterlite_user_set` | 사용자별 알림 설정 |
| `ncenterlite_unsubscribe` | 구독 해제 목록 |

(`ncenterlite_alarm`/`ncenterlite_log`/`ncenterlite_user_config`/`ncenterlite_admin_config`/`ncenterlite_token` 같은 테이블은 없다 — 푸시 디바이스 토큰은 `member_devices` 테이블에 저장.)

## 이 모듈이 정의하는 트리거

| 이름 | 시점 |
|---|---|
| `ncenterlite._insertNotify` | before/after — 알림이 DB에 기록되기 직전/직후. 외부 모듈이 hook해서 알림 가공/추가 발송 가능 |

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

`NcenterliteController` 메서드로 19개 트리거에 hook:

| 트리거 | 메서드 | 용도 |
|---|---|---|
| `comment.insertComment` (after) | `triggerAfterInsertComment` | 댓글 알림 |
| `comment.deleteComment` (after) | `triggerAfterDeleteComment` | 댓글 삭제 시 알림 회수 |
| `document.insertDocument` (after) | `triggerAfterInsertDocument` | 문서 알림 |
| `document.deleteDocument` (after) | `triggerAfterDeleteDocument` | 문서 삭제 시 알림 회수 |
| `document.moveDocumentToTrash` (after) | `triggerAfterMoveToTrash` | 휴지통 이동 처리 |
| `comment.moveCommentToTrash` (after) | `triggerAfterMoveToTrashComment` | 동상 |
| `document.updateVotedCount` (after) / `document.updateVotedCountCancel` (after) | `triggerAfterDocumentVotedUpdate` / `triggerAfterDocumentVotedCancel` | 추천/취소 알림 |
| `comment.updateVotedCount` (after) / `comment.updateVotedCountCancel` (after) | `triggerAfterCommentVotedCount` / `triggerAfterCommentVotedCancel` | 댓글 추천/취소 |
| `communication.sendMessage` (after) | `triggerAfterSendMessage` | 쪽지 알림 |
| `member.procMemberScrapDocument` (after) | `triggerAfterScrap` | 스크랩 알림 |
| `member.deleteMember` (after) | `triggerAfterDeleteMember` | 탈퇴 시 알림 정리 |
| `document.getComments` (after) | `triggerAfterGetComments` | 댓글 목록 hook |
| `document.getDocumentMenu` (after) / `comment.getCommentMenu` (after) | `triggerGetDocumentMenu` / `triggerGetCommentMenu` | 메뉴에 알림 항목 추가 |
| `display` (before) | `triggerBeforeDisplay` | 본문 렌더 직전 |
| `moduleHandler.proc` (after) | `triggerAfterModuleHandlerProc` | 액션 처리 후 |
| `moduleHandler.init` (after) | `triggerAddMemberMenu` | 회원 메뉴에 알림함 추가 |

## 발송 채널

각 알림은 사용자 설정에 따라:

- **사이트 내** — DB 알림.
- **메일** — `Mail::send`.
- **푸시** — `Push::send`.

## 관련

- 메일/푸시: [../18-mail-sms-push.md](../18-mail-sms-push.md)
- communication: [communication.md](communication.md)
- 큐: [../17-cache-and-queue.md](../17-cache-and-queue.md)
