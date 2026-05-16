# spamfilter (스팸 필터)

## 개요

- **카테고리**: accessory
- **역할**: 스팸 IP/단어/도메인 차단. 가입/글/댓글 시 검사.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Spamfilter` | `spamfilter.class.php` |
| `SpamfilterController` | `spamfilter.controller.php` |
| `SpamfilterModel` | `spamfilter.model.php` |
| `SpamfilterAdminController` | `spamfilter.admin.controller.php` |
| `SpamfilterAdminView` | `spamfilter.admin.view.php` |

(`spamfilter.admin.model.php`/`view.php`/`api.php`/`mobile.php`는 없다.)

## 주요 액션 (14개)

| 액션 | 비고 |
|---|---|
| `dispSpamfilterAdminConfig` | 설정 |
| `dispSpamfilterAdminIpList` | IP 차단 목록 |
| `procSpamfilterAdminInsertIp` | IP 차단 추가 |
| `dispSpamfilterAdminWordList` | 금지어 |
| `procSpamfilterAdminInsertWord` | 금지어 추가 |

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `spamfilter_denied_ip` | `schemas/spamfilter_denied_ip.xml` — 차단 IP/대역 |
| `spamfilter_denied_word` | `schemas/spamfilter_denied_word.xml` — 금지어 |
| `spamfilter_log` | `schemas/spamfilter_log.xml` — 차단 로그 |

(`spamfilter_ip`/`spamfilter_word`/`spamfilter_user` 같은 이름은 잘못 — 정확한 이름은 위와 같다.)

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

`SpamfilterController` 메서드로 11개 트리거에 hook:

| 트리거 | 메서드 | 용도 |
|---|---|---|
| `document.manage` (before) | `triggerManageDocument` | 문서 관리 액션 검사 |
| `document.insertDocument` (before) / `document.updateDocument` (before) | `triggerInsertDocument` | 글 작성/수정 차단 |
| `document.updateVotedCount` (before) | `triggerVote` | 추천 어뷰징 차단 |
| `document.declaredDocument` (before) | `triggerDeclare` | 신고 어뷰징 차단 |
| `comment.insertComment` (before) / `comment.updateComment` (before) | `triggerInsertComment` | 댓글 작성/수정 차단 |
| `comment.updateVotedCount` (before) | `triggerVote` | 댓글 추천 어뷰징 |
| `comment.declaredComment` (before) | `triggerDeclare` | 댓글 신고 어뷰징 |
| `communication.sendMessage` (before) | `triggerSendMessage` | 쪽지 발송 차단 |
| `moduleObject.proc` (before) | `triggerCheckCaptcha` | 모든 액션 전 캡차 검사 |

(`member.insertMember`는 hook하지 않는다 — 가입 차단은 member 모듈의 자체 정책으로 처리.)

## 검사 항목

- 클라이언트 IP가 차단 목록에 있는가.
- 본문/제목에 금지어가 있는가.
- 동일 회원이 단시간에 다수 작성하는가 (간격 제한).

## 관련

- IpFilter: [../19-security.md](../19-security.md)
