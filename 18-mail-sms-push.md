# 18. 메일 / SMS / 푸시

세 시스템 모두 **드라이버 추상화 + 정적 발송 API + 발송 트리거** 구조를 공유한다. 관리는 `modules/advanced_mailer/`가 담당.

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

$success = $mail->send(bool $sync = false);
if (!$success) {
    $errors = $mail->getErrors();
}
```

### 드라이버 등록 (커스텀)

```php
// addDriver는 인스턴스 인자만 받는다. 드라이버의 getName()이 식별자
Rhymix\Framework\Mail::addDriver(new MyMailDriver());
Rhymix\Framework\Mail::setDefaultDriver(new MyMailDriver());
```

### 트리거

- `mail.send.before` — 발송 직전 (Mail 객체 수정 가능).
- `mail.send.after` — 발송 직후 (성공/실패 로깅).

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
| `solapi` | SOLAPI (구 NCloud SENS) |
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
$success = $sms->send(bool $sync = false);
```

SMS/LMS/MMS는 본문 길이 자동 판별.

### 발신번호 허용 목록

국내 통신사 정책상 발신번호는 사전 등록되어야 한다. `advanced_mailer` 관리 UI에서 추가.

### 트리거

- `sms.send.before` / `sms.send.after`.

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
$success = $push->send(bool $sync = false);

// 발송 결과 (member_srl 단위 분류 아님 — 토큰 단위)
$successful = $push->getSuccessTokens();       // 발송 성공 토큰
$deleted    = $push->getDeletedTokens();       // 무효 토큰 (DB에서 제거 권장)
$updated    = $push->getUpdatedTokens();       // 토큰 갱신됨 (대체 권장)
```

### 토픽 발송

```php
$push->addTopic('news');       // 'news' 토픽 구독자 전체에
$push->send();
```

수신자는 `addTo`(member_srl) 또는 `addTopic`(토픽 이름) — Push 클래스가 내부에서 등록된 디바이스 토큰을 조회해 발송한다.

### 트리거

- `push.send.before` / `push.send.after`.

### 키/인증서

- APNS: p8 키 파일 + Team ID + Key ID + Bundle ID. `config('push.apns.*')`.
- FCM v1: Service Account JSON. `config('push.fcm.*')`.

설정 위치: `files/config/push/`.

## advanced_mailer 모듈

`modules/advanced_mailer/`. 위 3종을 관리자 UI에서 설정한다.

- 드라이버 선택 / 인증 정보 입력.
- 발신 정보 (기본 from, 이름, 발신번호).
- 발송 로그.
- 자체 드라이버 추가 등록.

[28-modules/advanced_mailer.md](28-modules/advanced_mailer.md) 참고.

## 새 드라이버 추가

1. `common/framework/drivers/<kind>/mydriver.php`에 `<Kind>Interface` 구현 클래스 작성.
2. `advanced_mailer` 관리 UI에서 등록 또는 코드:
   ```php
   // Mail/SMS는 인스턴스만, Push는 이름+인스턴스
   Rhymix\Framework\Mail::addDriver(new MyMailDriver(...));
   Rhymix\Framework\SMS::addDriver(new MySMSDriver(...));
   Rhymix\Framework\Push::addDriver('mydriver', new MyPushDriver(...));
   ```
3. 설정 저장 → 자동 선택.

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

    // 만료된 토큰 정리 (Push가 등록된 device_token 목록 단위로 반환)
    foreach ($push->getDeletedTokens() as $token) {
        MemberController::deletePushToken($token);
    }
}
```

## 다음 문서

- 큐: [17-cache-and-queue.md](17-cache-and-queue.md)
- 트리거: [13-event-and-trigger-system.md](13-event-and-trigger-system.md)
- 회원 모듈: [28-modules/member.md](28-modules/member.md)
- advanced_mailer: [28-modules/advanced_mailer.md](28-modules/advanced_mailer.md)
