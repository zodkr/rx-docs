# 19. 보안

Rhymix가 제공하는 보안 메커니즘 일람. **보안 취약점 보고는 `devops@rhymix.org`로** (`SECURITY.md`) — GitHub 이슈 금지.

## CSRF (Cross-Site Request Forgery)

### 자동 보호

- POST/PUT/DELETE 등 비-안전 메서드는 자동 CSRF 검증.
- 면제: `ModuleHandler::$_nocsrf_methods` = `['GET', 'HEAD', 'OPTIONS']`.
- `_rx_csrf_token` 파라미터 또는 헤더, Origin/Referer 검증.

### 액션별 비활성

```xml
<action name="procExternalWebhook" type="controller" check-csrf="false" />
```

외부 콜백 처리 시에만 사용 — 다른 보호(서명 검증 등) 필수.

### 수동 토큰 사용

```php
$token = Rhymix\Framework\Session::createToken('mymodule.deleteItem');
// 폼에 hidden으로 포함
$ok = Rhymix\Framework\Session::verifyToken('mymodule.deleteItem', $_POST['token']);
Rhymix\Framework\Session::invalidateToken('mymodule.deleteItem');
```

## XSS (Cross-Site Scripting)

### 출력 이스케이프

- **템플릿 v1 (`.html`)**: `{$var}` 기본 `'noescape'`(소스에 `<config autoescape="on" />`가 있어야만 `'auto'`로 escape됨). `{$var|escape}`/`{$var|autoescape}`/`|escapejs`로 명시 가능. 자세히는 [09-templates-and-skins.md](09-templates-and-skins.md).
- **템플릿 v2 (`.blade.php`)**: `{{ $var }}`는 항상 컨텍스트 인식 escape(HTML/JS는 자동, CSS는 별도 escape 미적용). `{!! $var !!}`는 raw.
- **PHP**: `escape($str)`, `escape_js($str)`, `escape_css($str)`.

### HTML 정화

`Rhymix\Framework\Filters\HTMLFilter` — HTMLPurifier 기반.

```php
$safe_html = Rhymix\Framework\Filters\HTMLFilter::clean(
    string $input,
    $allow_classes = false,
    bool $allow_editor_components = true,
    bool $allow_widgets = false
): string;
```

- WYSIWYG 에디터 본문은 자동으로 이 필터를 거친다.
- `$allow_classes`, `$allow_editor_components`, `$allow_widgets`로 정책 조정.

### 보안 헤더

`DisplayHandler::printContent`가 출력 (`classes/display/DisplayHandler.class.php:118-125`):

| 헤더 | 기본값 | 설정 키 |
|---|---|---|
| `X-Frame-Options` | `SAMEORIGIN` | `config('security.x_frame_options')` |
| `X-Content-Type-Options` | `nosniff` | `config('security.x_content_type_options')` |
| `X-Robots-Tag` | 모듈별 `robots_tag === 'noindex'` 시 출력 | — |

### Content Security Policy

기본 CSP 헤더는 출력되지 않음. 필요 시 애드온 또는 nginx/Apache에서 추가.

## 비밀번호 — `Rhymix\Framework\Password`

`common/framework/Password.php`.

### 기본 정책

- 회원 모듈 설정(`MemberModel::getMemberConfig()->password_hashing_algorithm`)이 우선. 미설정 시 `Password::getBestSupportedAlgorithm()` — `getSupportedAlgorithms()` 순서(`argon2id`/`bcrypt`/`pbkdf2`/`sha512`/`sha256`/`sha1`/`md5`)에서 **argon2id를 제외한 첫 항목**. 보통 **bcrypt**.
- Work factor는 회원 설정(`password_hashing_work_factor`). `Password::getWorkFactor()`의 런타임 검증 범위는 **4-31**(포함). 그 외 값(0, 미설정, <4, >31)이면 **기본 10**(`Password.php:178-187`).
- 관리자 UI(회원 설정 저장)는 더 좁은 **4-16** 범위로 자동 clamp한다 (`modules/member/member.admin.controller.php:340-348` — 4 미만은 4, 16 초과는 16). 즉 UI를 거치면 항상 4-16, 외부에서 DB를 직접 수정하면 4-31까지 가능.
- 옛 XE의 **phpass**(`$P$` 시그니처)는 `portable` 알고리즘으로 자동 인식 → `\Hautelook\Phpass\PasswordHash`로 검증.
- 그 외 인식 가능한 시그니처(`_algorithm_signatures`, `:14-34`): `argon2id`/`bcrypt`/`pbkdf2`/`md5`/`md5,sha1,md5`/`sha1`/`sha256`/`sha384`/`sha512`/`ripemd160`/`whirlpool`/`mssql_pwdencrypt`/`mysql_old_password`/`mysql_new_password`/`portable`/`drupal`/`joomla`/`kimsqrb`/`crypt`.

### API

시그니처:

- `Password::hashPassword(string $password, $algos = null, ?string $salt = null): string`
  — `$algos`는 단일 알고리즘 또는 콤마 구분/배열(체인). `null`이면 default 알고리즘.
- `Password::checkPassword(string $password, string $hash, $algos = null): bool`
  — `$algos`가 `null`이면 hash 시그니처에서 자동 식별(`checkAlgorithm`)해 후보를 모두 시도.

사용:

```php
$hash = Rhymix\Framework\Password::hashPassword($password);
$ok   = Rhymix\Framework\Password::checkPassword($password, $hash);
```

`hashPassword`의 `$algos`는 콤마 구분 문자열(예: `'md5,sha1,md5'`) 또는 배열을 받아 chain hash를 만든다 (`:238-358`). argon2id/bcrypt/portable/pbkdf2/drupal/joomla/kimsqrb/crypt 등은 체인에서 마지막에 와야 한다.

### 랜덤 비밀번호

```php
$temp = Rhymix\Framework\Password::getRandomPassword(16);   // 16자 (기본)
```

랜덤 토큰/문자열은 `Security::getRandom(32, 'alnum')`, `Security::getRandomNumber($min, $max)`, `Security::getRandomUUID()`.

### 알고리즘 점검 / 작업 강도 API

| 메서드 | 의미 |
|---|---|
| `Password::getSupportedAlgorithms()` | 이 PHP에서 사용 가능한 알고리즘 목록 (순서 보존) |
| `Password::getDefaultAlgorithm()` | 회원 설정 우선, 미설정 시 `getBestSupportedAlgorithm()` |
| `Password::getBestSupportedAlgorithm()` | `getSupportedAlgorithms()`에서 argon2id 제외 첫 항목 |
| `Password::getBackwardCompatibleAlgorithm()` | 60자 이하 해시를 만드는 알고리즘(bcrypt/pbkdf2/sha1/md5)으로 폴백 |
| `Password::getWorkFactor()` | `member` 설정 또는 기본 10 (4-31 외 값은 10으로 리셋) |
| `Password::checkAlgorithm($hash)` | 해시 시그니처로 후보 알고리즘 배열 추출 |
| `Password::checkWorkFactor($hash)` | 해시에 사용된 work factor 추출 |
| `Password::isValidAlgorithm($algos)` | 알고리즘 이름이 유효한지 |
| `Password::addAlgorithm($name, $signature, $callback)` | 사용자 정의 알고리즘 등록 |

알고리즘 직접 호출: `Password::argon2id($pw, $work_factor=10)`, `Password::bcrypt($pw, $salt=null, $work_factor=10)`, `Password::pbkdf2($pw, $salt=null, $algorithm='sha512', $iterations=16384, $length=24, $iterations_padding=7)`.

### 설정 위치

비밀번호 정책은 `config('security.*')`가 아니라 **`member` 모듈 설정**에 저장된다 — 관리자 → 회원 → 설정 화면, 또는 `module_config` 테이블의 member 모듈 설정 객체.

## 파일 업로드

### `Rhymix\Framework\Filters\FilenameFilter`

- 위험 확장자 차단: `.php`, `.phtml`, `.pl`, `.cgi`, `.asp`, `.jsp`, `.html`, ...
- 이중 확장자 검사: `file.php.jpg` 같은 패턴.
- 허용 확장자 화이트리스트 (`config('file.allowed_extensions')`).

### `Rhymix\Framework\Filters\FileContentFilter`

- 매직 바이트 (file signature) 검사.
- PHP 코드 패턴 검출 (`<?php`, `<?=`).
- SVG는 `enshrined/svg-sanitize`로 정화.

### `UploadFileFilter` (legacy)

위 둘을 종합한 진입점.

```php
$ok = UploadFileFilter::check($tmp_path, $filename);
```

### 첨부 파일 경로 정책

- 업로드 경로 (`files/attach/binaries/`, `files/attach/images/`)에는 `.htaccess`/nginx로 PHP 실행 차단.
- 다운로드는 `files/download/<srl>/<key>/<filename>` 라우트로 모듈을 거침 — 권한 검증.

## IP 차단 — `Rhymix\Framework\Filters\IpFilter`

### CIDR / 와일드카드

```php
$ranges = ['192.168.0.0/24', '10.*.*.*', '203.0.113.5'];
$blocked = Rhymix\Framework\Filters\IpFilter::inRanges(RX_CLIENT_IP, $ranges);
```

### 기본 차단 목록

`common/defaults/blacklist.php` — 알려진 악성 IP 대역.

### 한국 IP 대역

`common/defaults/korea.ipv4.php`, `korea.ipv6.php` — 국내 IP 판별용.

```php
$is_korea = Rhymix\Framework\Korea::isKoreanIP(RX_CLIENT_IP);
```

### CloudFlare 실제 IP

`HTTP_CF_CONNECTING_IP` 헤더가 있고, 요청이 CloudFlare 대역에서 온 경우에만 신뢰하고 `RX_CLIENT_IP`로 사용 (`common/constants.php:59-63`, `IpFilter::getCloudFlareRealIP()`).

`common/defaults/cloudflare.php`에 CloudFlare IP 대역 보관.

## 임베드 / 미디어 필터

### `Rhymix\Framework\Filters\MediaFilter`

- YouTube/Vimeo/SoundCloud 등 화이트리스트 도메인의 iframe만 허용.
- 본문 콘텐츠에서 `<iframe src="...">` 자동 검사.

설정: `config('mediafilter.iframe')`, `config('mediafilter.object')`.

### `EmbedFilter` (classes/security/)

XE 호환. iframe/object/embed/applet 화이트리스트.

## 관리자 보호

### IP 화이트/블랙리스트

```php
'admin' => [
    'allow' => ['192.168.0.0/16', '203.0.113.10'],     // 허용 IP만
    'deny'  => ['1.2.3.4'],                            // 차단
]
```

`allow`가 비어 있으면 모든 IP 허용. 비어 있지 않으면 화이트리스트 모드.

### root vs manager

- `is_admin === 'Y'` 회원만 root.
- root는 모든 모듈의 매니저 권한 보유.
- `config('admin.deny_root_in_admin')` — 일반 관리자 페이지에서 root 차단.

## 사이트 잠금 (점검 모드)

```php
'lock' => [
    'locked' => true,
    'message' => '서비스 점검 중입니다.',
    'allow' => ['관리자 IP 대역'],
]
```

- 점검 중 메시지 표시.
- 화이트리스트 IP는 정상 접근.

## 로봇 / SEO

### 로봇 차단

`config('security.robot_user_agents')` — UA 패턴 차단.

기본 차단 봇은 거의 없음. 어뷰징 봇 추가 시 사용.

### 외부 링크 nofollow

`config('security.nofollow') = true`면 본문의 외부 링크에 자동 `rel="nofollow"`.

## 암호화 키

자동 생성 후 `files/config/`에 저장된다.

| 키 | 용도 |
|---|---|
| `crypto.encryption_key` | 대칭 암호화 |
| `crypto.authentication_key` | HMAC |
| `crypto.session_key` | 세션 토큰 서명 |

분실 시: 세션 모두 만료 / 기존 암호화 데이터 복호화 불가. 신중히 백업.

### 사용

```php
$cipher = Rhymix\Framework\Security::encrypt($plaintext);
$plain  = Rhymix\Framework\Security::decrypt($cipher);
```

내부적으로 OpenSSL AES-256-GCM 사용.

## JWT

`firebase/php-jwt` 패키지 사용. 자체 토큰 발급 시 활용 가능.

```php
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

$token = JWT::encode($payload, $key, 'HS256');
$decoded = JWT::decode($token, new Key($key, 'HS256'));
```

## SQL Injection

- 모든 XML 쿼리는 PDO prepared statement로 실행 — 자동 보호.
- 동적 SQL이 필요하면 `DB::addQuotes()` 또는 `escape_sqstr()` 사용.

## Open Redirect

- `success_return_url`/`error_return_url`은 `ModuleHandler::init`이 `URL::isInternalURL()`로 검증.
- 외부 URL이면 제거되어 기본 페이지로 리다이렉트.

## 디렉토리 보호

```php
Rhymix\Framework\Storage::protectDirectory($path);
// .htaccess (Deny from all) + index.html (빈 파일) 생성
```

## 보안 체크 패턴 (`Context::_check_patterns`)

요청 변수에서 다음 패턴 발견 시 차단:

- `<?` (PHP 태그).
- `<%` (ASP 태그).
- `<script ...language=...>`.
- `</?script`.

발견 시 `security_check`를 `DENY ALL`로 설정 → 모든 처리 거부.

## 다음 문서

- 세션/CSRF 상세: [15-session-and-auth.md](15-session-and-auth.md)
- 파일 스토리지: [20-storage-and-files.md](20-storage-and-files.md)
- IP 차단 모듈: [28-modules/spamfilter.md](28-modules/spamfilter.md)
- nginx/.htaccess 설정: [02-infrastructure.md](02-infrastructure.md)
