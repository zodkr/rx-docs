# 19. 보안

Rhymix가 제공하는 보안 메커니즘 일람. **보안 취약점 보고는 `devops@rhymix.org`로** (`SECURITY.md`) — GitHub 이슈 금지.

## CSRF (Cross-Site Request Forgery)

### 자동 보호

- POST/PUT/DELETE 등 비-안전 메서드는 자동 CSRF 검증.
- 면제: `ModuleHandler::$_nocsrf_methods` = `['GET', 'HEAD', 'OPTIONS']`.
- 기본값 `security.check_csrf_token=false`에서는 토큰 검사를 생략하고 `Sec-Fetch-Site`·Origin·Referer로 same-origin을 검증한다. 이 설정을 `true`로 켜면 로그인 사용자의 `_rx_csrf_token` 파라미터 또는 `X-CSRF-Token` 헤더도 필수로 검증한다 (`common/framework/Security.php:327-380`).

### 액션별 비활성

```xml
<action name="procExternalWebhook" type="controller" check-csrf="false" />
```

외부 콜백 처리 시에만 사용 — 다른 보호(서명 검증 등) 필수.

### 수동 토큰 사용

```php
// createToken($key)은 랜덤 토큰을 반환하고, 그 토큰을 키로·인자($key)를 값으로 세션에 저장.
$token = Rhymix\Framework\Session::createToken('mymodule.deleteItem');
// createToken이 반환한 $token을 폼에 hidden으로 포함
// verifyToken($token, $key): 첫 인자가 토큰, 둘째가 키.
$ok = Rhymix\Framework\Session::verifyToken($_POST['token'], 'mymodule.deleteItem');
Rhymix\Framework\Session::invalidateToken($_POST['token']);
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

`DisplayHandler::printContent`가 출력 (`classes/display/DisplayHandler.class.php:118-131` — X-Robots-Tag는 128-131):

| 헤더 | 기본값 | 설정 키 |
|---|---|---|
| `X-Frame-Options` | `SAMEORIGIN` | `config('security.x_frame_options')` |
| `X-Content-Type-Options` | `nosniff` | `config('security.x_content_type_options')` |
| `X-Robots-Tag` | 모듈별 `robots_tag === 'noindex'` 시 출력 | — |

### Content Security Policy

기본 CSP 헤더는 출력되지 않음. 필요 시 애드온 또는 nginx/Apache에서 추가.

#### 신규 스킨/레이아웃 작성 규칙

향후 코어 업데이트시 CSP를 켜는 옵션을 제공할 예정이다. 나중에 `script-src`/`style-src`에서 `'unsafe-inline'`이 빠져도 화면이 깨지지 않도록, **새로 만드는 스킨·레이아웃은 처음부터 인라인 script/style 없이 작성한다.** 이미 v1으로 배포된 기존 스킨/레이아웃은 명시적 요청 없이 일괄 변환하지 않는다 (§ [09 - 새 템플릿 작성/마이그레이션 정책](09-templates-and-skins.md#새-템플릿-작성마이그레이션-정책)과 동일한 기준).

지양할 것 — 모두 `'unsafe-inline'`을 요구한다:

| 패턴 | 대체 |
|---|---|
| `<script> ... </script>` 본문 | 외부 `.js` 파일 + `@load('./js/skin.js', 'body')` |
| `<style> ... </style>` 블록 | 외부 `.css`/`.scss` 파일 + `@load('./css/skin.css')` |
| `onclick=""` 등 `on*` 속성 | JS 파일에서 `addEventListener`, 템플릿에는 `id`/`class`/`data-*` 훅만 남김 |
| `href="javascript:..."` | 실제 URL + JS에서 `preventDefault()` |
| `style="..."` 인라인 스타일 | CSS 클래스. 값이 동적이면 CSS 커스텀 속성 또는 `data-*` + JS |

부수 효과로 § [컨텍스트 인식 escape](09-templates-and-skins.md#컨텍스트-인식-escape)의 까다로운 부분(`escape_js`가 따옴표를 붙이지 않는 문제, CSS 컨텍스트에 자동 escape가 없는 문제)도 함께 사라진다. 인라인 JS/CSS가 없으면 escape 실수로 XSS가 생길 표면 자체가 없다.

#### 템플릿 → JS 파라미터 전달 (JSON 데이터 아일랜드)

템플릿의 값을 JS로 넘겨야 할 때 `<script>var config = ...;</script>`를 만들지 말고, **`type="application/json"` 스크립트 블록에 JSON으로 심고 JS 파일에서 `getElementById`로 읽는다.** `type`이 `application/json`인 `<script>`는 브라우저가 실행하지 않는 데이터 블록이므로 CSP의 `script-src`가 차단하지 않는다.

템플릿 (v2 `.blade.php` — 신규 작성 시 권장):

```blade
<script id="myBoardSkinConfig" type="application/json">@json([
    'mid' => $module_info->mid,
    'listCount' => (int) $module_info->list_count,
    'isLogged' => $is_logged,
])</script>

@load('./js/skin.js', 'body')
```

JS (`js/skin.js`):

```js
document.addEventListener('DOMContentLoaded', function() {
    var el = document.getElementById('myBoardSkinConfig');
    if (!el) {
        return;
    }
    var config = JSON.parse(el.textContent);
    // ...
});
```

규칙:

- **`@json()`으로만 출력한다.** `<script type="application/json">`은 `src` 속성이 없으므로 v2 파서가 JS 컨텍스트로 전환하고(`common/framework/parsers/template/TemplateParser_v2.php:208-223`), 이 컨텍스트의 `@json()`은 `JSON_HEX_TAG`를 포함한 옵션으로 인코딩한다(`TemplateParser_v2.php:794-801`, `common/framework/Template.php:100-107`). `<`가 `\u003C`가 되어 값 안의 `</script>`로 블록을 탈출할 수 없다. 문자열을 손으로 이어 붙이거나 `{!! !!}`로 raw 출력하지 않는다.
- **HTML escape 필터를 붙이지 않는다.** `<script>` 내부는 HTML raw text 영역이라 브라우저가 문자 참조를 디코드하지 않는다. `|escape`나 `htmlspecialchars`를 거친 JSON을 넣으면 `&quot;`가 그대로 남아 `JSON.parse`가 실패한다. JS 컨텍스트의 `@json()`은 이 경로를 타지 않는다.
- **JS 쪽은 `textContent`로 읽는다.** `innerText`는 렌더링에 영향을 받고, `innerHTML`은 마크업이 섞인다.
- **id는 페이지 전역에서 충돌하지 않게** 짓는다. 한 페이지에 레이아웃 + 여러 모듈 스킨 + 위젯이 동시에 렌더되므로 `{모듈/스킨}` prefix를 붙인 lowerCamelCase를 쓴다 — `myBoardSkinConfig`, `dailycheckWidgetParams`. 같은 스킨이 한 페이지에 두 번 이상 렌더될 수 있다면 id 대신 컨테이너 요소의 `data-*` 속성(예: `<div class="my-board" data-config="...">`)으로 인스턴스별 스코프를 잡는다.
- **요소가 없는 경우를 항상 방어한다.** JS 파일은 그 스킨이 렌더되지 않은 페이지에서도 로드될 수 있다.
- **비밀 값을 넣지 않는다.** 데이터 아일랜드는 페이지 소스에 그대로 노출된다. 세션 토큰·타인의 개인정보·권한 판단 근거를 담지 않으며, 권한은 항상 서버에서 다시 검사한다 (§ [관리자 보호](#관리자-보호)).

v1(`.html`) 템플릿에는 `@json()`이 없고 `{$v}`가 기본 noescape이므로 옵션을 직접 지정한다. 신규 스킨/레이아웃은 v2로 작성하는 것이 원칙이며, 기존 v1 스킨을 고칠 때만 사용한다:

```html
<script id="myBoardSkinConfig" type="application/json">{json_encode($config, JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT|JSON_UNESCAPED_UNICODE)}</script>
<load target="./js/skin.js" type="body" />
```

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

- `.php` 파일은 실행되지 않도록 `.phps`로 변환.
- 오인 유발 이중 확장자 제거: `php`/`jsp`/`asp(x)`/`exe`/`bat`/`msi`/`scr`/`com`/`zip`/`doc(x)`/`xls(x)`/`ppt(x)`/`hwp(x)` 등 뒤에 다른 확장자가 붙은 경우 앞쪽을 제거(예: `file.php.jpg` → `file.jpg`).
- 허용 확장자 화이트리스트는 FilenameFilter가 아니라 file 모듈 설정 `allowed_extensions`(file 모듈 업로드 흐름)에서 검사.

### `Rhymix\Framework\Filters\FileContentFilter`

- JPEG/PNG/GIF/WebP 및 지정된 audio/video 확장자는 `fileinfo`로 판별한 대분류가 선언 확장자와 맞는지 검사한다.
- SVG 또는 XML/HTML로 보이는 콘텐츠는 스크립트·이벤트 핸들러·외부 entity 등 위험 패턴을 정규식으로 탐지한다.
- PHP 태그 검출(`<?`, XML 선언 제외)은 HTML 또는 XML-like 콘텐츠에 적용되는 `_checkHTML()` 단계의 규칙이다. 임의 확장자의 모든 파일을 PHP 코드 스캐너처럼 검사하는 것은 아니다 (`common/framework/filters/FileContentFilter.php:36-96,138-155`).

(`enshrined/svg-sanitize` 기반 정화는 `Security::sanitize($str, 'svg')`에서 수행한다.)

### `UploadFileFilter` (legacy)

업로드된 임시 파일을 검사한 뒤 내부적으로 `FileContentFilter::check()`를 호출하는 진입점 (FilenameFilter는 호출하지 않음).

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

### 기본 IP 차단 목록

코어에는 알려진 악성 IP를 자동 차단하는 기본 목록이 없다. `IpFilter::inRanges()`에는 호출자가 설정한 범위를 전달해야 한다. 이름이 비슷한 `common/defaults/blacklist.php`는 IP 목록이 아니라 호환되지 않는 **deprecated addon/module/widget** 목록이다.

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

설정: `config('mediafilter.whitelist')`(허용 도메인 접두사 배열), `config('mediafilter.classes')`. (`mediafilter.iframe`/`mediafilter.object`는 하위 호환용 레거시 키)

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
- 관리자 페이지 접근 IP 제한은 위의 `config('admin.allow')`/`config('admin.deny')`로 수행한다(별도의 root 차단 설정 키는 없음).

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

### 로봇 판별

`config('security.robot_user_agents')`는 `UA::isRobot()`이 로봇으로 **분류**할 추가 부분 문자열 목록이다 (`common/framework/UA.php:156-190`). 이 설정만으로 요청을 차단하지는 않는다. 차단이 필요하면 웹서버, 애드온, 스팸필터 등에서 `UA::isRobot()` 결과나 별도 정책을 사용한다.

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

내부적으로 OpenSSL AES-128-CBC + HMAC-SHA256(Encrypt-then-MAC, defuse/php-encryption 1.x 호환 포맷) 사용. `encrypt`/`decrypt`는 키를 `sha256`의 앞 16바이트(128비트)로 잘라 `\CryptoCompat`에 넘긴다.

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
- 동적 SQL이 필요하면 `DB::query($sql, ...$args)`의 placeholder나 `prepare()`/bound parameter를 사용한다. `DB::addQuotes()`는 레거시 호환용이므로 prepared statement가 우선이다. `escape_sqstr()`는 **PHP의 single-quoted 문자열 리터럴**을 만들기 위한 함수이지 SQL 이스케이프 함수가 아니다 (`common/functions.php:228-238`).

## Open Redirect

- `Rhymix\Framework\URL::isInternalURL()`은 상대 경로를 내부 URL로 인정하고, 절대 URL은 현재 요청의 host(포트 포함) 또는 `domains` 테이블에 등록된 도메인과 일치해야 통과시킨다. 등록 도메인의 비표준 HTTP/HTTPS 포트도 해당 scheme의 설정 포트와 정확히 일치해야 한다. 역슬래시는 `/`로 정규화하며, `http`/`https` 외의 명시적 scheme(`javascript:`, `data:`, `file:`, `ftp:`, `mailto:` 등)은 거부한다 (`common/framework/URL.php:106-158`, `tests/unit/framework/URLTest.php:123-151`).
- `Context`의 요청 변수 필터링(`_filterRequestVar()`) 단계에서 `success_return_url`/`error_return_url`을 검증한다. 단, **이 검증은 GET이 아닌 요청(POST 등)에만 적용된다.** `_filterRequestVar()`의 `elseif` 체인에서 GET 요청은 앞선 분기(`classes/context/Context.class.php:1525`)에 먼저 걸려 값이 escape만 되고, `Rhymix\Framework\URL::isInternalURL()` 검증(`classes/context/Context.class.php:1533-1541`)까지 도달하지 못한다.
- 비(非)GET 요청에서 외부 URL이 감지되면 값을 null로 제거하고 `security_check`를 `DENY ALL`로 설정해 요청 전체를 차단한다.
- 따라서 `?success_return_url=https://...`처럼 **GET 파라미터로 전달된 리다이렉트 URL은 이 단계에서 내부 URL 여부가 검사되지 않으므로**, 그 값을 소비해 리다이렉트하는 쪽에서 별도로 내부 URL임을 보장해야 한다.

## 디렉토리 보호

```php
Rhymix\Framework\Storage::protectDirectory($path);
// .htaccess (Deny from all) + index.html (빈 파일) 생성
```

이는 Apache가 `.htaccess`를 허용하는 경우에만 효과가 있는 best-effort 보조 수단이다. nginx 등에서는 별도 서버 설정으로 민감한 디렉토리를 차단해야 한다 (`common/framework/Storage.php:876-913`).

## 보안 체크 패턴 (`Context::_check_patterns`)

요청 변수에서 다음 패턴 발견 시 차단:

- `<?` (PHP 태그).
- `<%` (ASP 태그).
- `<script ...language=...>`.
- `</?script`.

`<?`/`<%`, `<script ...language=...>`(javascript 제외) 패턴은 `security_check`를 `DENY ALL`로 설정 → 모든 처리 거부. `</?script`는 `ALLOW ADMIN ONLY`로 설정되어 관리자에게는 허용되고 비관리자 요청만 차단된다.

## 다음 문서

- 세션/CSRF 상세: [15-session-and-auth.md](15-session-and-auth.md)
- 파일 스토리지: [20-storage-and-files.md](20-storage-and-files.md)
- IP 차단 모듈: [28-modules/spamfilter.md](28-modules/spamfilter.md)
- nginx/.htaccess 설정: [02-infrastructure.md](02-infrastructure.md)
