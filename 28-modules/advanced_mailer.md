# advanced_mailer (메일/SMS/푸시 통합 관리)

## 개요

- **카테고리**: (info.xml에 미지정 — 기본 `service`)
- **역할**: 메일/SMS/푸시 드라이버 설정 + 발송 로깅을 관리.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Advanced_mailer` | `advanced_mailer.class.php` |
| `Advanced_mailerController` | `advanced_mailer.controller.php` |
| `Advanced_mailerModel` | `advanced_mailer.model.php` |
| `Advanced_mailerAdminController` | `advanced_mailer.admin.controller.php` |
| `Advanced_mailerAdminView` | `advanced_mailer.admin.view.php` |

(`advanced_mailer.view.php`/`admin.model.php`/`mobile.php`/`api.php`는 없다.)

## 주요 액션 (18개)

| 액션 | 비고 |
|---|---|
| `dispAdvanced_mailerAdminConfig` | 메일/SMS/푸시 통합 설정 진입 (admin_index, menu_name=advanced_mailer) |
| `dispAdvanced_mailerAdminExceptions` | 예외 도메인/주소 |
| `dispAdvanced_mailerAdminSpfDkim` | SPF/DKIM 점검 |
| `dispAdvanced_mailerAdminMailTest` / `dispAdvanced_mailerAdminMailLog` | 메일 테스트/로그 |
| `dispAdvanced_mailerAdminSMSTest` / `dispAdvanced_mailerAdminSMSLog` | SMS 테스트/로그 |
| `dispAdvanced_mailerAdminPushTest` / `dispAdvanced_mailerAdminPushLog` | 푸시 테스트/로그 |
| `procAdvanced_mailerAdminInsertConfig` | 설정 저장 |
| `procAdvanced_mailerAdminInsertExceptions` | 예외 저장 |
| `procAdvanced_mailerAdminCheckDNSRecord` | DNS 레코드 점검 |
| `procAdvanced_mailerAdminClearSentMail` / `procAdvanced_mailerAdminClearSentSMS` / `procAdvanced_mailerAdminClearSentPush` | 로그 정리 |
| `procAdvanced_mailerAdminTestSendMail` / `procAdvanced_mailerAdminTestSendSMS` / `procAdvanced_mailerAdminTestSendPush` | 테스트 전송 |

## DB 스키마

| 테이블 | 용도 |
|---|---|
| `advanced_mailer_log` | 메일 발송 로그 (`schemas/advanced_mailer_log.xml`) |
| `advanced_mailer_sms_log` | SMS 발송 로그 |
| `advanced_mailer_push_log` | 푸시 발송 로그 |

(`advanced_mailer_sms_caller_id` 같은 별도 발신번호 테이블은 없다 — SMS 발신번호 정책은 설정 또는 외부 솔루션으로 관리.)

## 드라이버 등록

설정값은 `config('mail.*')`, `config('sms.*')`, `config('push.*')`로 저장. 

각 드라이버의 인증 정보(API 키, SMTP 비밀번호 등)는 `files/config/`에 별도 저장 + 암호화.

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `mail.send` (before) | `triggerBeforeMailSend` (controller) | 발신자/예외 도메인/SPF 정책 등 적용 |
| `mail.send` (after) | `triggerAfterMailSend` (controller) | 발송 로그 기록 |
| `sms.send` (after) | `triggerAfterSMSSend` (controller) | SMS 로그 기록 |
| `push.send` (after) | `triggerAfterPushSend` (controller) | 푸시 로그 기록 |

(`mail.send`/`sms.send`/`push.send` 트리거는 `Rhymix\Framework\Mail`/`SMS`/`Push` 코어가 발사한다.)

## 발신번호 허용 목록 (SMS)

국내 통신사 정책상 SMS 발신번호는 사전 등록 필수이며, 일반적으로 SMS 게이트웨이 측 콘솔에서 관리한다. Rhymix는 이를 위한 별도 테이블을 두지 않는다.

## 관련

- Mail/SMS/Push: [../18-mail-sms-push.md](../18-mail-sms-push.md)
- 큐: [../17-cache-and-queue.md](../17-cache-and-queue.md)
