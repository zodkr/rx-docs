# 05. Context 클래스

`classes/context/Context.class.php` (3000줄 이상)는 요청/응답 전반의 상태를 보관하는 **전역 싱글톤**이다. 모든 모듈/위젯/템플릿에서 `Context::get()` / `Context::set()` 형태로 사용된다.

## 디자인 특징

- 싱글톤. `Context::getInstance()`가 인스턴스를 반환하지만, 거의 모든 사용은 **정적 메서드**로 한다.
- 변수 분류:
  - **공개 인스턴스 속성** — 응답/요청 상태 (browser_title, html_header, ...).
  - **사용자 변수** — `Context::set/get`로 액세스. 내부 `_user_vars` 보관.
  - **요청 변수** — `$_GET`/`$_POST`/`$_FILES` 정리 후 사용자 변수에 병합.

## 공개 인스턴스 속성 (자주 쓰이는 것)

| 속성 | 타입 | 의미 |
|---|---|---|
| `request_method` | string | `GET`/`POST`/`XMLRPC`/`JSON`/`JS_CALLBACK`/`RAW` |
| `response_method` | string | 응답 포맷 (기본 빈 문자열 → `request_method` 따라 결정) |
| `js_callback_func` | string | JSONP 콜백 함수명 |
| `db_info` | object | DB/URL/세션 설정의 통합 객체 (`loadDBInfo` 결과) |
| `ftp_info` | object | FTP 설정 |
| `browser_title` | string | `<title>` |
| `html_header` | string | `</head>` 직전 삽입할 HTML |
| `html_footer` | string | `</body>` 직전 |
| `body_header` | string | `<body>` 직후 |
| `body_class` | array | `<body class="...">` 클래스 목록 |
| `link_rels` | array | `<link rel="...">` 목록 |
| `meta_tags` | array | `<meta>` 태그 |
| `meta_images` | array | OpenGraph 이미지 |
| `opengraph_metadata` | array | `og:*` 메타 |
| `canonical_url` | string | `<link rel="canonical">` |
| `lang_type` | string | 현재 언어 코드 |
| `lang` | object | 다국어 객체 (`Lang::getInstance(...)`) |
| `is_uploaded` | bool | 업로드 파일 존재 여부 |
| `is_site_locked` | bool | 사이트 잠금 상태 |
| `security_check` | string | `OK`/`ALLOW ADMIN ONLY`/`DENY ALL` |
| `security_check_detail` | string | 위 결정의 사유 문자열 |

## 자주 쓰이는 정적 메서드 (API 카테고리별)

### 사용자 변수 (모듈/템플릿 공유)

```php
Context::set('key', $value);
Context::set('key', $value, true);     // 세 번째 인자로 request 변수 동시 갱신
$value = Context::get('key');
$arr = Context::gets('key1', 'key2');  // 여러 키 동시 조회
$all = Context::getAll();              // 전체
```

### 요청 정보

| 메서드 | 반환 |
|---|---|
| `getRequestMethod()` | `GET`/`POST`/`JSON`/`XMLRPC`/`JS_CALLBACK` |
| `getResponseMethod()` | 응답 포맷 |
| `getRequestVars()` | stdClass — 사용자 변수만 추린 객체 |
| `getCurrentRequest()` | `Rhymix\Framework\Request` 인스턴스 |
| `getRequestUrl()` | 현재 요청 전체 URL |
| `getRequestUri()` | 사이트 base URI |

### URL 생성

```php
Context::getUrl();                                  // 현재 URL
Context::getUrl(0);                                 // base URL
Context::getUrl(2, 'mid', 'foo', 'act', 'bar');     // 변수 (개수, key, val, key, val, ...)
Context::getDefaultUrl();                           // 사이트 기본 URL
Context::pathToUrl($path);                          // 경로 → URL
```

### 언어

```php
Context::loadLang($dir);                  // <dir>/<langtype>.php 로드
Context::loadLang($dir, 'plugin');        // namespace 지정
Context::setLangType('ko');
Context::getLangType();
$text = Context::getLang('key');          // 또는 lang('key')
Context::setLang('key', 'value');
Context::replaceUserLang($str);           // {$user_lang->key} 치환
```

다국어 시스템: [16-i18n-and-lang.md](16-i18n-and-lang.md).

### HTML 출력 조작 (View 계열에서 자주)

```php
Context::addHtmlHeader('<script>...</script>');
Context::addBodyHeader('<div>...</div>');
Context::addHtmlFooter('<script>...</script>');
Context::addLink(['rel' => 'preload', 'href' => '...']);
Context::addBodyClass('full-width');
Context::removeBodyClass('full-width');
```

### SEO

```php
Context::setBrowserTitle('제목');
Context::addBrowserTitle('서브 - ');     // prepend
Context::getSiteTitle();
Context::addMetaTag('description', '...');
Context::addMetaImage('https://.../og.png');
Context::addOpenGraphData('og:type', 'article');
Context::setCanonicalURL('https://...');
```

### 자원 로딩

```php
Context::loadFile([$path, 'head'|'body', $targetie, $index]);
Context::addJsFile('./common/js/foo.js');
Context::addCSSFile('./common/css/foo.css');
Context::loadJavascriptPlugin('jquery.fileupload');
$list = Context::getJsFile('head');
$list = Context::getCSSFile();
```

`loadJavascriptPlugin`은 `common/js/plugins/<name>/plugin.load` 매니페스트를 읽어 한꺼번에 로드한다. 외부 라이브러리 목록은 [34-external-libraries.md](34-external-libraries.md).

### 응답 모드 제어

```php
Context::setResponseMethod('JSON');
Context::setCacheControl(0);                                // no-cache
Context::setCacheControl(3600);                             // max-age=3600
Context::setCorsPolicy('*', ['Content-Type'], 'GET,POST');
Context::redirect($url, 302);
```

### 사이트/DB

```php
Context::loadDBInfo();         // 자체 호출 — config 로드
Context::getDBType();          // 'mysql'
Context::getDBInfo();          // stdClass (db 설정)
Context::isInstalled();        // bool
Context::isLocked();           // bool — 점검 모드
```

### 인코딩 / IDN

```php
Context::convertEncoding($str);                          // 자동 감지 → UTF-8
Context::convertEncodingStr($str, 'CP949');              // CP949 → UTF-8
Context::encodeIdna('한글도메인.kr');                     // punycode
Context::decodeIdna('xn--...');
```

## 보안 체크 패턴 (`_check_patterns`)

`Context::init()`이 입력 변수를 다음 패턴으로 검사한다(예시):

- `<?` — PHP 태그.
- `<%` — ASP 태그.
- `<script ...language=...>` — 스크립트.
- `</?script` — `<script>`/`</script>`.

발견 시 `security_check`를 `DENY ALL` 또는 `ALLOW ADMIN ONLY`로 설정해 이후 `ModuleHandler` 생성자가 거부 처리한다.

## 예약어

`common/defaults/reserved.php`는 mid/모듈명/액션명으로 사용할 수 없는 키워드 목록을 정의한다. `module` 모듈의 mid 검증 시 참조된다.

## 컨텍스트에 미리 주입되는 키들

요청 처리 중 다음 키들이 자동 설정된다. 템플릿/모듈에서 즉시 사용 가능.

| 키 | 의미 |
|---|---|
| `logged_info` | 로그인 회원 정보 (`SessionHelper` 인스턴스 또는 false) |
| `is_logged` | 로그인 여부 |
| `site_module_info` | 현재 도메인의 루트 모듈 정보 |
| `current_module_info` | 현재 처리 중 모듈 정보 |
| `module_info` | 모듈 인스턴스에 주입된 정보 |
| `layout_info` | 현재 레이아웃 정보 (extra_vars 포함) |
| `mid` | 현재 모듈 인스턴스 mid |
| `act` | 현재 액션명 |
| `lang_type` | 현재 언어 |
| `current_url` | 현재 전체 URL |
| `request_uri` | 사이트 base URI |
| `_default_url` | 사이트 기본 URL |
| `http_status_code` | 응답 HTTP 상태 |
| `body_class` | body 클래스 목록 |

## `Context::close()`

`classes/context/Context.class.php:439-452`. 요청 종료 시:

1. `DisplayHandler::$debug_printed`가 false면 `DisplayHandler::getDebugInfo()` 호출 — Debug 정보를 출력/기록한다 (별도의 도메인 트리거는 호출하지 않으며, Debug 클래스가 직접 처리).
2. `Session::checkStart()`이 true면 `Session::close()`로 세션 저장.

## 자주 보게 될 패턴

```php
// View 계열 액션
public function dispBoardContent()
{
    $logged_info = Context::get('logged_info');
    if (!$logged_info) {
        throw new Rhymix\Framework\Exceptions\MustLogin;
    }
    $document_srl = Context::get('document_srl');
    $oDocument = DocumentModel::getDocument($document_srl);
    Context::set('document', $oDocument);
    Context::set('mid', $this->module_info->mid);
    $this->setTemplateFile('content');
}
```

```php
// JSON 응답 액션
public function procBoardInsertDocument()
{
    Context::setResponseMethod('JSON');
    // ... 처리 ...
    $this->add('document_srl', $document_srl);
    $this->add('url', getUrl('', 'mid', $mid, 'document_srl', $document_srl));
}
```

## 다음 문서

- ModuleHandler 라이프사이클: [06-module-handler-lifecycle.md](06-module-handler-lifecycle.md)
- 라우터: [07-router.md](07-router.md)
- 응답 출력: [08-display-and-response.md](08-display-and-response.md)
