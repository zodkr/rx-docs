# spamfilter (스팸 필터)

## 개요

- **카테고리**: accessory
- **역할**: 스팸 IP/단어 차단 및 작성 간격 제한, CAPTCHA(reCAPTCHA/Cloudflare Turnstile) 검증. IP/단어/간격 검사는 글·댓글·쪽지 작성과 추천·신고 시 트리거로 동작하고, CAPTCHA는 가입·로그인·계정복구·글·댓글 작성 시 검증한다. (도메인 차단은 별도 기능·스키마가 없고, 단어 필터의 정규식으로 처리한다.)

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Spamfilter` | `spamfilter.class.php` |
| `SpamfilterController` | `spamfilter.controller.php` |
| `SpamfilterModel` | `spamfilter.model.php` |
| `SpamfilterAdminController` | `spamfilter.admin.controller.php` |
| `SpamfilterAdminView` | `spamfilter.admin.view.php` |

(`spamfilter.view.php`/`spamfilter.admin.model.php`/`spamfilter.mobile.php`/`spamfilter.api.php`는 없다.)

## 주요 액션 (14개)

view 5개 + controller 9개. 액션명은 `Config`/`Ip`/`Word`가 아니라 `ConfigBlock`/`ConfigCaptcha`, `DeniedIP`, `DeniedWord` 형태다 (`conf/module.xml:5-19`).

| 액션 | 비고 |
|---|---|
| `dispSpamfilterAdminDeniedIPList` | IP 차단 목록 (view, admin_index) |
| `dispSpamfilterAdminDeniedWordList` | 금지어 목록 (view) |
| `dispSpamfilterAdminConfigBlock` | 자동 차단 설정 화면 (view) |
| `dispSpamfilterAdminConfigCaptcha` | 캡차 설정 화면 (view) |
| `dispSpamfilterAdminConfigCaptchaTest` | 캡차 테스트 화면 (view) |
| `procSpamfilterAdminInsertDeniedIP` | IP 차단 추가 (controller) |
| `procSpamfilterAdminUpdateDeniedIP` | IP 차단 수정 |
| `procSpamfilterAdminDeleteDeniedIP` | IP 차단 삭제 |
| `procSpamfilterAdminInsertDeniedWord` | 금지어 추가 |
| `procSpamfilterAdminUpdateDeniedWord` | 금지어 수정 |
| `procSpamfilterAdminDeleteDeniedWord` | 금지어 삭제 |
| `procSpamfilterAdminInsertConfig` | 자동 차단 설정 저장 |
| `procSpamfilterAdminInsertConfigCaptcha` | 캡차 설정 저장 |
| `procSpamfilterAdminSubmitCaptchaTest` | 캡차 테스트 제출 |

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
- 동일 IP가 단시간에 다수 작성하는가 (간격 제한, IP 주소 기준). `checkLimited()`는 회원이 아니라 `RX_CLIENT_IP` 기준으로 `spamfilter_log`를 집계한다 (`spamfilter.model.php:157`, `getLogCount()` `spamfilter.model.php:323`; `queries/getLogCount.xml`은 `ipaddress`와 `regdate`(시간창)만 조건으로 쓰고 회원 식별자는 참조하지 않는다).

## CAPTCHA (reCAPTCHA / Cloudflare Turnstile)

IP/단어/간격 검사와 별개로 CAPTCHA 서브시스템을 핵심 기능으로 갖는다. 제공자 클래스는 `captcha/recaptcha.php`·`captcha/turnstile.php` (`Rhymix\Modules\Spamfilter\Captcha\*`), 관리는 `dispSpamfilterAdminConfigCaptcha`(설정)·`dispSpamfilterAdminConfigCaptchaTest`(동작 테스트) 화면이 담당한다.

모델 API (`spamfilter.model.php`):

- `isCaptchaEnabled($target_action)` — 설정 유무·대상 사용자(비로그인/전체)·빈도·기기(PC/모바일)·대상 액션 조건을 종합해 노출 여부 판정 (`spamfilter.model.php:217`).
- `getCaptcha($target_action)` — 제공자 인스턴스 생성 및 스크립트 삽입 (`spamfilter.model.php:253`).
- `checkCaptchaResponse($response)` — 응답 검증, 실패 시 예외 throw (`spamfilter.model.php:285`).

검증 대상 액션(`target_actions`)은 가입(`signup`)·로그인(`login`)·계정복구(`recovery`)·글 작성(`document`)·댓글 작성(`comment`)이다. `moduleObject.proc` (before) 트리거의 `triggerCheckCaptcha`가 이를 검사한다.

## 관련

- IpFilter: [../19-security.md](../19-security.md)
