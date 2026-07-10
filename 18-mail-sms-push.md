# 18. 메일 / SMS / 푸시

세 시스템 모두 **드라이버 추상화 + 인스턴스 발송 API + 발송 트리거** 구조를 공유한다. 드라이버 선택·인증 정보·발신 정보는 **관리자 > 시스템 설정 > 알림**(`modules/admin/controllers/systemconfig/Notification.php`, `config_notification` 템플릿)에서 설정하며, `modules/advanced_mailer/`는 발송 로그·예외 발송·SPF/DKIM 확인·테스트 발송을 담당한다.

## `send()`의 동기/비동기 의미

Mail/SMS/Push의 `send(bool $sync = false)`는 모두 같은 규칙을 따른다.

- 큐가 꺼져 있거나 `$sync=true`이면 현재 요청에서 실제 발송하고 그 결과를 반환한다.
- `queue.enabled=true`, `$sync=false`, 큐 워커 밖이면 객체를 큐에 추가한 뒤 `true`를 반환한다. 이 `true`는 **큐 등록 성공**일 뿐 실제 전달 성공이 아니다.
- 비동기 경로에서는 before/after 발송 트리거와 드라이버 오류 처리도 워커가 실제 발송할 때 실행된다.

즉 즉시 드라이버 결과와 `getErrors()`가 필요하면 `send(true)`를 사용하고, 기본 `send()` 결과를 수신 성공으로 기록하지 않는다 (`common/framework/Mail.php:562-578`, `SMS.php:513-529`, `Push.php:404-420`).

## 메일 — `Rhymix\Framework\Mail`

`common/framework/Mail.php` (693줄). SwiftMailer 위에 드라이버 레이어를 얹은 형태.

### 드라이버

`common/framework/drivers/mail/`:

| 드라이버 | 설명 |
|---|---|
| `mailfunction` | PHP `mail()` 함수 |
| `smtp` | SwiftMailer SMTP |
| `sendgrid` | SendGrid API |
| `mailgun` | Mailgun API |
| `mandrill` | Mandrill API |
| `postmark` | Postmark API |
| `ses` | Amazon SES |
| `sparkpost` | SparkPost API |
| `brevo` | Brevo (구 Sendinblue) |
| `ncloud_mailer` | NAVER Cloud Mailer |
| `woorimail` | 우리메일 |
| `dummy` | 송신 안 함 (테스트) |

### 인스턴스 API

```php
$mail = new Rhymix\Framework\Mail();
$mail->setFrom('from@example.com', '발신자');
$mail->addTo('to@example.com', '수신자');
$mail->addCc('cc@example.com');
$mail->addBcc('bcc@example.com');
$mail->setReplyTo('reply@example.com');
$mail->setSubject('제목');
$mail->setBody('<p>HTML 본문</p>');              // 기본 content_type='text/html'
$mail->setBody('Plain text', 'text/plain');     // 또는 명시
$mail->setContent('<p>본문</p>');                 // setBody와 동등 (alias)
$mail->attach('/path/to/file.pdf', 'invoice.pdf');

$success = $mail->send();        // 큐 사용 시 enqueue 결과
// $success = $mail->send(true); // 현재 요청에서 동기 발송
if (!$success) {
    $errors = $mail->getErrors();
}
```

### 드라이버 등록 (커스텀)

```php
// addDriver는 인스턴스 인자만 받는다. 식별자는 클래스명 소문자(strtolower(class_basename($driver)))이고, getName()은 UI 표시용 이름이다
Rhymix\Framework\Mail::addDriver(new MyMailDriver());
Rhymix\Framework\Mail::setDefaultDriver(new MyMailDriver());
```

### 트리거

- 이름 `mail.send`, position `before` — 발송 직전 (Mail 객체 수정 가능).
- 이름 `mail.send`, position `after` — 발송 직후 (성공/실패 로깅).

### 기본 발신자

`config('mail.default_from')` / `config('mail.default_name')`.

### 메일 큐 활용

대량 발송은 큐로 (인자는 단일 객체):

```php
Rhymix\Framework\Queue::addTask(
    'My\\Class::sendBulkMail',
    (object)['user_srls' => $user_srls]
);
```

## SMS — `Rhymix\Framework\SMS`

`common/framework/SMS.php` (843줄).

### 드라이버

`common/framework/drivers/sms/`:

| 드라이버 | 비고 |
|---|---|
| `coolsms` | 국내, CoolSMS |
| `twilio` | 글로벌 |
| `solapi` | SOLAPI (Nurigo, 구 CoolSMS 계열) |
| `iwinv` | iwinv |
| `ncloud_sens` | NAVER Cloud SENS |
| `ppurio` | 뿌리오 |
| `dummy` | 비활성 |

### API

```php
$sms = new Rhymix\Framework\SMS();
$sms->setFrom('01012345678');
$sms->addTo('01098765432', '0');            // 두 번째 인자: country code ('0' = 국내)
$sms->setSubject('인증번호');                  // LMS/MMS만 사용
$sms->setBody('인증번호: 123456');             // setContent도 alias
$sms->attach('/path/to/img.jpg');           // MMS만
$success = $sms->send();        // 큐 사용 시 enqueue 결과
// $success = $sms->send(true); // 현재 요청에서 동기 발송
```

SMS/LMS/MMS는 본문 길이 자동 판별.

추가 제어 API:

- `setDelay($seconds_or_timestamp)` — 1년 이하 값은 현재 시각 기준 초, 더 큰 값은 Unix timestamp로 해석(드라이버별 지원 여부 확인).
- `forceSMS()` / `unforceSMS()` — LMS/MMS 대신 SMS로 강제/해제.
- `allowSplitSMS()` / `disallowSplitSMS()`, `allowSplitLMS()` / `disallowSplitLMS()` — 장문 분할 정책 제어.

### 발신번호 사전 등록

국내 통신사 정책상 발신번호는 이용하는 SMS 게이트웨이/통신사에 사전 등록해야 한다. Rhymix 관리자 UI에는 발신번호 **목록 등록 기능이 없고**, 기본값 `sms.default_from` 하나와 강제 사용 여부만 설정한다 (`modules/admin/tpl/config_notification.html:174-188`, `Notification.php:244-257`).

### 트리거

- 이름 `sms.send`, position `before` / `after`.

### 인증번호 발송 패턴

```php
$code = sprintf('%06d', random_int(0, 999999));
$_SESSION['sms_verification'] = [
    'code' => $code,
    'phone' => $phone,
    'expires' => time() + 180,
];

$sms = new Rhymix\Framework\SMS();
$sms->setFrom(config('sms.default_from'));
$sms->addTo($phone);
$sms->setBody("인증번호: {$code}");
$sms->send();
```

## 푸시 알림 — `Rhymix\Framework\Push`

`common/framework/Push.php` (641줄).

### 드라이버

`common/framework/drivers/push/`:

| 드라이버 | 비고 |
|---|---|
| `apns` | Apple Push Notification Service |
| `fcm` | Firebase Cloud Messaging (legacy HTTP API) |
| `fcmv1` | FCM HTTP v1 API (권장) |

### API

```php
$push = new Rhymix\Framework\Push();
$push->setFrom(int $member_srl);              // 발송자 회원 srl (옵션)
$push->addTo(int $member_srl);                // 수신자 회원 srl (디바이스 토큰이 아닌 member_srl)
$push->addTo($another_member_srl);
$push->setSubject('알림 제목');
$push->setContent('알림 본문');
$push->setURL('https://...');                  // 대문자 URL
$push->setImage('https://.../thumb.png');
$push->setData(['post_id' => 123]);           // 커스텀 데이터 (array)
$push->setBadge('1');                          // string
$push->setSound('default');
$success = $push->send();        // 큐 사용 시 enqueue 결과
// $success = $push->send(true); // 현재 요청에서 동기 발송

// 발송 결과 (member_srl 단위 분류 아님 — 토큰 단위)
$successful = $push->getSuccessTokens();       // 발송 성공 토큰
$deleted    = $push->getDeletedTokens();       // 무효 토큰 (send() 내부에서 이미 DB에서 삭제됨)
$updated    = $push->getUpdatedTokens();       // 토큰 갱신됨 (send() 내부에서 이미 DB 토큰이 교체됨)
```

### 토픽 발송

```php
$push->addTopic('news');       // 'news' 토픽 구독자 전체에
$push->send();
```

수신자는 `addTo`(member_srl) 또는 `addTopic`(토픽 이름) — Push 클래스가 내부에서 등록된 디바이스 토큰을 조회해 발송한다.

### 트리거

- 이름 `push.send`, position `before` / `after`.

### 키/인증서

- APNS: 인증서(.pem) 파일 + passphrase. `config('push.apns.certificate')` / `config('push.apns.passphrase')`. (레거시 바이너리 APNs 프로토콜 `ssl://gateway.push.apple.com:2195` 사용)
- FCM v1: Service Account JSON. `config('push.fcmv1.service_account')`.

설정 위치: `files/config/apns/` (APNs 인증서 `cert-*.pem`), `files/config/fcmv1/` (FCM v1 서비스 계정 `pkey-*.json`).

## advanced_mailer 모듈

`modules/advanced_mailer/`.

드라이버 선택 / 인증 정보 / 발신 정보(기본 from·이름, SMS 발신번호) 입력은 **관리자 > 시스템 설정 > 알림**(`modules/admin/controllers/systemconfig/Notification.php`, `config_notification` 템플릿)에서 이뤄지며 `mail.type`/`sms.type`/`push` 등을 시스템 config에 저장한다(`Config::set`).

advanced_mailer가 담당하는 것:

- 발송 로그 on/off 및 로그 조회/삭제 (메일/SMS/푸시 각각).
- 도메인별 예외 발송(exceptions).
- SPF/DKIM DNS 레코드 확인(`procAdvanced_mailerAdminCheckDNSRecord`).
- 테스트 발송(메일/SMS/푸시).

[28-modules/advanced_mailer.md](28-modules/advanced_mailer.md) 참고.

## 새 드라이버 추가

코어에 포함할 드라이버는 `common/framework/drivers/<kind>/mydriver.php`에 `<Kind>Interface` 구현 클래스로 추가한다. `getSupportedDrivers()`가 이 디렉토리를 스캔하므로 지원 환경과 설정 검증을 통과하면 **관리자 > 시스템 설정 > 알림** 선택 목록에 자동으로 나타난다.

외부 확장에서 요청 시점에 인스턴스를 등록할 수도 있다.

```php
// Mail/SMS: 목록 등록과 실제 기본 드라이버 지정은 별도
$mail_driver = new MyMailDriver(...);
Rhymix\Framework\Mail::addDriver($mail_driver);
Rhymix\Framework\Mail::setDefaultDriver($mail_driver);

$sms_driver = new MySMSDriver(...);
Rhymix\Framework\SMS::addDriver($sms_driver);
Rhymix\Framework\SMS::setDefaultDriver($sms_driver);

// Push: 이름+인스턴스로 등록하면 getDriver($name)에서도 조회 가능
Rhymix\Framework\Push::addDriver('mydriver', new MyPushDriver(...));
```

런타임 등록 배열은 요청마다 초기화되므로 확장 부트스트랩에서 매 요청 등록해야 한다. Mail/SMS의 `addDriver()`는 지원 드라이버 목록에 추가할 뿐 기본 발송 인스턴스를 자동 교체하지 않으므로 `setDefaultDriver()`도 필요하다 (`common/framework/Mail.php:33-70`, `SMS.php:40-77`).

기본 인터페이스 메서드는 `<Kind>Interface.php`(예: `MailInterface.php`)에서 확인.

## 흔한 패턴

### 회원 가입 환영 메일

```php
public function onAfterMemberInsert($member_info)
{
    Rhymix\Framework\Queue::addTask(
        'My\\Notify::welcome',
        (object)['member_srl' => $member_info->member_srl]
    );
}
```

### 새 댓글 푸시

```php
public function onAfterCommentInsert($comment)
{
    $push = new Rhymix\Framework\Push();
    $push->addTo($document_author_srl);    // member_srl
    $push->setSubject('새 댓글');
    $push->setContent($comment->content);
    $push->setURL(getNotEncodedFullUrl('', 'document_srl', $comment->document_srl));
    $push->send();

    // 무효/갱신 토큰은 send() 내부에서 member.deleteMemberDevice / member.updateMemberDevice
    // 쿼리로 자동 정리되므로 호출부에서 별도로 정리할 필요가 없다.
    // (디바이스 토큰 관리 로직은 Rhymix\Modules\Member\Controllers\Device 참고)
}
```

## 다음 문서

- 큐: [17-cache-and-queue.md](17-cache-and-queue.md)
- 트리거: [13-event-and-trigger-system.md](13-event-and-trigger-system.md)
- 회원 모듈: [28-modules/member.md](28-modules/member.md)
- advanced_mailer: [28-modules/advanced_mailer.md](28-modules/advanced_mailer.md)
