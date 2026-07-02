# 10. Rhymix\Framework\* 인덱스

`common/framework/` 하위 모든 클래스는 `Rhymix\Framework\` 네임스페이스를 사용한다. 신규 코드는 가능하면 이쪽에 작성한다.

## 핵심 클래스

| 클래스 | 파일 | 한 줄 요약 |
|---|---|---|
| `Cache` | `Cache.php` (434줄) | 정적 캐시 API + 드라이버 자동 폴백 + 그룹 무효화. 상세 → [17-cache-and-queue.md](17-cache-and-queue.md) |
| `Calendar` | `Calendar.php` (129줄) | 그레고리력 보조 유틸 — 월 이름, 월 시작 요일, 월 일수, 달력 그리드 생성. |
| `Config` | `Config.php` (209줄) | dot-notation 설정 get/set, `files/config/config.php` 직렬화. 상세 → [25-config-system.md](25-config-system.md) |
| `Cookie` | `Cookie.php` (115줄) | `setcookie()` wrapper, SameSite/HttpOnly/Secure 정책. |
| `DB` | `DB.php` (1603줄) | PDO 기반, prefix 자동, 트랜잭션 카운팅. 상세 → [14-database-and-queries.md](14-database-and-queries.md) |
| `DateTime` | `DateTime.php` (247줄) | 타임존 변환, formatting, `i18n.php`와 함께 사용. |
| `Debug` | `Debug.php` (996줄) | 에러/예외 핸들러, 슬로우 쿼리/트리거/위젯 로깅. 상세 → [24-debug-and-logging.md](24-debug-and-logging.md) |
| `Exception` | `Exception.php` (38줄) | 사용자 메시지 + `getUserFileAndLine()`. 모든 도메인 예외의 부모. |
| `Formatter` | `Formatter.php` (572줄) | `text2html`, `html2text`, `markdown2html`, `bbcode`, `compileLESS`, `compileSCSS`, `minifyCSS`/`JS`, `concat*`, `convertIECondition`. |
| `HTTP` | `HTTP.php` (336줄) | Guzzle 래퍼, 프록시/타임아웃 추상화. |
| `Image` | `Image.php` (101줄) | 이미지 메타, animated WebP/GIF 판정. |
| `Korea` | `Korea.php` (465줄) | 한국 IP 대역, 휴대전화/이메일 검증, 주민·법인·사업자등록번호 검증. |
| `Lang` | `Lang.php` (417줄) | `lang_*.php` 로딩, ArrayObject 인터폴레이션. 상세 → [16-i18n-and-lang.md](16-i18n-and-lang.md) |
| `MIME` | `MIME.php` (208줄) | 확장자 ↔ MIME 타입 매핑. |
| `Mail` | `Mail.php` (693줄) | SwiftMailer 기반 메일 발송. 상세 → [18-mail-sms-push.md](18-mail-sms-push.md) |
| `Pagination` | `Pagination.php` (155줄) | 페이지 계산기 (XE 호환은 `classes/page/PageHandler.class.php`). |
| `Password` | `Password.php` (587줄) | bcrypt + phpass 호환. 상세 → [19-security.md](19-security.md) |
| `Push` | `Push.php` (641줄) | APNS/FCM/FCMv1, 토픽, 토큰 관리. |
| `Queue` | `Queue.php` (535줄) | DB/Redis 백업드 작업 큐, cron 처리. 상세 → [17-cache-and-queue.md](17-cache-and-queue.md) |
| `Request` | `Request.php` (226줄) | HTTP 메서드/호스트/라우팅 결과 보관. |
| `Router` | `Router.php` (645줄) | URL ↔ 변수 변환. 상세 → [07-router.md](07-router.md) |
| `SMS` | `SMS.php` (843줄) | SMS 발송 추상화. |
| `Security` | `Security.php` (430줄) | 입력 sanitize, 암호화/서명, 난수 생성, CSRF 검사, hash_equals 상수시간 비교, XXE 방어. |
| `Session` | `Session.php` (1147줄) | PHP 세션 + 자체 토큰/refresh/SSL 분리 쿠키. 상세 → [15-session-and-auth.md](15-session-and-auth.md) |
| `Storage` | `Storage.php` (1058줄) | atomic 파일 쓰기, umask 관리, 파일 잠금. 상세 → [20-storage-and-files.md](20-storage-and-files.md) |
| `Template` | `Template.php` (998줄) | 템플릿 엔진 인스턴스. 상세 → [09-templates-and-skins.md](09-templates-and-skins.md) |
| `Timer` | `Timer.php` (109줄) | `RX_MICROTIME` 기반 시간 측정. |
| `UA` | `UA.php` (480줄) | User-Agent 파싱 (모바일/태블릿/봇). |
| `URL` | `URL.php` (286줄) | `getCurrentURL`, `getCurrentDomain`, `modifyURL`, `isInternalURL`, `getCanonicalURL`. |
| `i18n` | `i18n.php` (185줄) | 다국어 날짜/숫자 포맷. |

## 드라이버 (`drivers/`)

각 카테고리에 하나의 인터페이스와 다수의 구현이 있다.

### CacheInterface (`drivers/CacheInterface.php`)

구현: `apc.php`, `dummy.php`, `file.php`, `memcached.php`, `redis.php`, `sqlite.php`.

### MailInterface

구현: `base.php`(추상), `brevo.php`, `dummy.php`, `mailfunction.php`, `mailgun.php`, `mandrill.php`, `ncloud_mailer.php`, `postmark.php`, `sendgrid.php`, `ses.php`, `smtp.php`, `sparkpost.php`, `woorimail.php`.

### SMSInterface

구현: `base.php`, `coolsms.php`, `dummy.php`, `iwinv.php`, `ncloud_sens.php`, `ppurio.php`, `solapi.php`, `twilio.php`.

### PushInterface

구현: `base.php`, `apns.php`, `fcm.php`, `fcmv1.php`.

### QueueInterface

구현: `db.php`, `dummy.php`, `redis.php`.

## 파서 (`parsers/`)

XML/구성 파일을 PHP 객체로 변환한다.

| 파서 | 입력 | 출력 |
|---|---|---|
| `AddonInfoParser` | `addons/<n>/conf/info.xml` | 애드온 메타 + extra_vars |
| `BaseParser` | (추상) | 공통 메타/multi-lang 처리 |
| `ConfigParser` | (legacy) `config.inc.php` | 신형 `config.php` 변환 |
| `DBQueryParser` | `modules/<n>/queries/*.xml` | SQL 빌드 |
| `DBTableParser` | `modules/<n>/schemas/*.xml` | CREATE TABLE 빌드 |
| `EditorComponentParser` | `modules/editor/components/<n>/info.xml` | 컴포넌트 메타 |
| `LangParser` | `lang/*.xml` (XE legacy) | PHP 다국어 |
| `LayoutInfoParser` | `layouts/<n>/conf/info.xml` | 레이아웃 메타 + menus + extra_vars |
| `ModuleActionParser` | `modules/<n>/conf/module.xml` | actions/grants/menus/routes/triggers |
| `ModuleInfoParser` | `modules/<n>/conf/info.xml` | 모듈 메타 |
| `RulesetParser` | `modules/<n>/ruleset/*.xml` | 검증 규칙 (JS+PHP) |
| `SkinInfoParser` | `modules/<n>/skins/<s>/skin.xml` | 스킨 메타 + extra_vars + colorset |
| `WidgetInfoParser` | `widgets/<n>/conf/info.xml` | 위젯 메타 + extra_vars |
| `WidgetStyleInfoParser` | `widgetstyles/<n>/skin.xml` | 위젯스타일 메타 |
| `XEXMLParser` | XE 호환 XML | (low-level) |
| `XMLRPCParser` | XML-RPC 요청 | 메서드/파라미터 |

## 헬퍼 (`helpers/`)

- `CacheItemHelper`, `CacheItemPoolHelper` — PSR-6 어댑터.
- `ConfigHelper` — 단일 키 설정 객체.
- `DBHelper`, `DBResultHelper`, `DBStmtHelper` — DB 결과 객체.
- `HTTPHelper` — HTTP 응답 객체.
- `SessionHelper` — 현재 회원 정보 + `isAdmin`/`isMember`/`can`.

## 필터 (`filters/`)

| 필터 | 역할 |
|---|---|
| `FileContentFilter` | 업로드 파일 매직바이트/PHP 코드 검사 |
| `FilenameFilter` | 위험 확장자/이중 확장자 차단 |
| `HTMLFilter` | htmlpurifier 기반 XSS 정화 |
| `IpFilter` | CIDR/와일드카드 IP 매칭, CloudFlare 실제 IP |
| `MediaFilter` | iframe/embed 화이트리스트 (YouTube/Vimeo 등) |

## 예외 (`exceptions/`)

모두 `Rhymix\Framework\Exception` 상속. 사용자에게 표시되는 메시지.

아래 표의 `HTTP` 열은 **의미상 권장 코드**이며 예외 객체가 실제로 담는 값이 아니다. 예외 클래스는 기본 메시지만 설정하고 HTTP 상태 코드를 갖지 않는다 (`common/framework/exceptions/*.php`). `ModuleObject::init()`/`proc()`가 예외를 잡아 `stop()` 또는 `BaseObject(-2, getMessage())`로 변환하며 (`classes/module/ModuleObject.class.php:246-249,876-880`), message 모듈이 상태 코드가 200이면 일괄적으로 403으로 렌더링한다 (`modules/message/message.view.php:92-96`). 즉 실제 응답은 대부분 403이다.

| 예외 | 의미 | HTTP(권장) |
|---|---|---|
| `DBError` | DB 오류 | 500 |
| `FeatureDisabled` | 기능 비활성 | 403 |
| `InvalidRequest` | 잘못된 요청 | 400 |
| `MustLogin` | 로그인 필요 | 401 |
| `NotPermitted` | 권한 없음 | 403 |
| `QueryError` | 쿼리 오류 | 500 |
| `SecurityViolation` | 보안 위반 | 403 |
| `TargetNotFound` | 대상 없음 | 404 |

사용 예:

```php
throw new Rhymix\Framework\Exceptions\MustLogin;
throw new Rhymix\Framework\Exceptions\TargetNotFound;
throw new Rhymix\Framework\Exceptions\NotPermitted('관리자만 접근 가능');
throw new Rhymix\Framework\Exception('일반 오류 메시지');
```

`ModuleObject::proc()`이 `try-catch`로 잡아 `BaseObject(-2, getMessage())`로 변환한다.

## 다음 문서

- 레거시 클래스 wrapper: [11-legacy-classes.md](11-legacy-classes.md)
- 전역 함수/상수: [12-helpers-and-globals.md](12-helpers-and-globals.md)
