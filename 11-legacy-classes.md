# 11. 레거시 classes/* 인덱스

`classes/` 하위는 XpressEngine 시절의 전역(namespace 없음) 클래스들이다. 대부분이 `Rhymix\Framework\*`의 얇은 wrapper다.

## 디렉토리 구조

| 디렉토리 | 주 클래스 | 역할 |
|---|---|---|
| `cache/` | `CacheHandler` | `Rhymix\Framework\Cache` wrapper |
| `context/` | `Context` | 요청/응답 글로벌 상태 (별도 문서 → [05-context.md](05-context.md)) |
| `db/` | `DB` | `Rhymix\Framework\DB` 상속 |
| `display/` | `DisplayHandler`, `*DisplayHandler` | 응답 출력 (별도 문서 → [08-display-and-response.md](08-display-and-response.md)) |
| `editor/` | `EditorHandler` | 에디터 컴포넌트의 부모 |
| `extravar/` | `ExtraVar`, `ExtraItem` | `Rhymix\Modules\Extravar\Models\*`로의 `class_alias` |
| `file/` | `FileHandler`, `FileObject` | `Storage`/`Image` wrapper + XE 호환 |
| `frontendfile/` | `FrontEndFileHandler` | `<link>`/`<script>` 태그 관리 |
| `handler/` | `Handler` | 빈 추상 마커 클래스 |
| `httprequest/` | `XEHttpRequest` | XE 호환 Ajax helper |
| `mail/` | `Mail` | `Rhymix\Framework\Mail` wrapper |
| `mobile/` | `Mobile` | 모바일 감지 (별도 문서 → [23-mobile-detection.md](23-mobile-detection.md)) |
| `module/` | `ModuleHandler`, `ModuleObject` | 라이프사이클 (별도 문서 → [06-module-handler-lifecycle.md](06-module-handler-lifecycle.md)) |
| `object/` | `BaseObject` | 모든 모듈/위젯의 조상 |
| `page/` | `PageHandler` | XE 호환 페이지네이션 |
| `security/` | `EmbedFilter`, `Password`, `Security`, `UploadFileFilter`, `IpFilter`, `Purifier` | 보안 wrapper |
| `template/` | `TemplateHandler` | `Rhymix\Framework\Template` 상속 |
| `validator/` | `Validator` | ruleset XML 기반 입력 검증 |
| `widget/` | `WidgetHandler` | 모든 위젯의 부모 (빈 클래스, `$widget_path`만) |
| `xml/` | `GeneralXmlParser`, `XmlGenerator`, `XmlJsFilter`, `XmlLangParser`, `XmlParser` | XML 파싱/생성 |

## BaseObject

`classes/object/Object.class.php`. 모든 모듈/위젯의 조상.

```php
#[AllowDynamicProperties]
class BaseObject
{
    public $error = 0;
    public $message = 'success';
    public $variables = [];
    public $httpStatusCode = 200;

    public function __construct($error = 0, $message = 'success');
    // error != 0이면 호출지의 file:line을 'rx_error_location'에 add.

    public function setError($error);
    public function getError();
    public function setMessage($message = 'success', $type = null);  // $type=null이면 setMessageType() 미호출
    public function getMessage();
    public function setMessageType($type);
    public function getMessageType();

    public function set($key, $value);
    public function add($key, $value);          // set의 alias
    public function get($key);
    public function gets(...$keys);
    public function getVariables();
    public function getObjectVars();            // 객체 형태로 반환
    public function unset($key);

    public function setHttpStatusCode($code);
    public function getHttpStatusCode();

    public function toBool();                   // error === 0이면 true
    public function toBoolean();                // alias

    public static function __set_state(array $vars);  // var_export 복원
}
```

`toBool()`이 false면 트리거 호출자가 처리를 중단한다.

## Handler

`classes/handler/Handler.class.php`는 빈 클래스다. `ModuleHandler`/`DisplayHandler`/`PageHandler` 등이 이를 상속하지만 실제 기능은 자식 클래스에 있다.

## DB

```php
class DB extends Rhymix\Framework\DB {}
```

신형 클래스 그대로 사용 가능. `DB::getInstance()` 등 정적 메서드도 상속됨.

## CacheHandler

```php
class CacheHandler extends Handler {
    public static function getInstance($target = null, $info = null, $always_use_file = false) {
        // Rhymix\Framework\Cache 정적 메서드로 위임
    }
    // 모든 메서드가 Cache::xxx로 위임
}
```

신형 코드는 `Rhymix\Framework\Cache::get/set/delete`를 직접 사용한다.

## FileHandler (`classes/file/FileHandler.class.php`)

24KB로 비교적 큰 wrapper. `Storage`와 `Image`를 합쳐 XE 호환 API를 제공한다.

### 자주 쓰이는 정적 메서드

| 메서드 | 역할 |
|---|---|
| `getRealPath($source)` | `./` 또는 `~/` prefix를 `RX_BASEDIR` 기준 절대경로로 |
| `exists($filename)` | 파일/디렉토리 존재 |
| `readFile($filename)` | 파일 내용 읽기 |
| `writeFile($filename, $data, $mode='w')` | 파일 쓰기 |
| `copyFile($source, $target)` | 복사 |
| `moveFile($source, $target)` | 이동 |
| `removeFile($filename)` | 파일 삭제 |
| `removeFilesInDir($path)` | 디렉토리 내 파일 삭제 |
| `makeDir($path)` | mkdir -p |
| `removeDir($path)` | 디렉토리 재귀 삭제 |
| `readDir($path, $filter='', $to_lower=false, $concat_prefix=false)` | 디렉토리 리스트 (단일 깊이, 정규식 filter, 소문자/경로 접두사 옵션) |
| `createImageFile($source, $target, $w, $h, $type, $thumb_type)` | 이미지 리사이즈 |
| `getRemoteFile($url, $target_path, ...)` | 원격 파일 다운로드 |
| `getRemoteResource($url, ...)` | 원격 응답 본문 반환 |
| `returnBytes($val)` | `'2M'`/`'1G'` → bytes |
| `filesize($size)` | bytes → 사람 가독 ('1.2MB') |
| `checkImageRotation($filename)` | EXIF 기반 회전 |

상세 동작은 `Storage` 메서드로 위임. → [20-storage-and-files.md](20-storage-and-files.md).

## FileObject

`classes/file/FileObject.class.php`. `fopen`/`fread`/`fwrite`를 감싼 저수준 파일 I/O 추상화 클래스.

```php
class FileObject extends BaseObject {
    public $fp = null;    // 파일 디스크립터
    public $path = null;  // 파일 경로
    public $mode = 'r';   // 열기 모드

    public function __construct($path, $mode);   // $path != null이면 open() 호출
    public function open($path, $mode);          // fopen; 이미 열려 있으면 close 후 재열기
    public function read($size = 1024);          // fread
    public function write($str);                 // fwrite
    public function append($file_name);          // 대상 파일 내용을 현재 파일에 이어붙임
    public function feof();                       // feof
    public function getPath();                    // 현재 파일 경로
    public function close();                      // fclose
}
```

## FrontEndFileHandler

`classes/frontendfile/FrontEndFileHandler.class.php` (21KB). HTML head/body에 들어갈 `<script>`/`<link>` 태그를 관리한다.

- `loadFile([$path, 'head'|'body', $unused, $index])` — 자원 등록 (`$args[2]`는 미사용, 이전 targetIe 자리이며 index는 `$args[3]`).
- `unloadFile($path)` — 자원 해제.
- `unloadAllFiles()` — 전체 해제.
- `getJsFileList($type='head', $finalize=false)` / `getCssFileList($finalize=false)` — HTML 출력용 결과.

`common/js/plugins/<name>/plugin.load` 매니페스트 처리는 `Context::loadJavascriptPlugin($name)`에 있다(FrontEndFileHandler가 아님).

내부적으로:

- 자동 minify/concat (`config('view.minify_scripts')`, `config('view.concat_scripts')`).
- LESS/SCSS 자동 컴파일 → `files/cache/assets/`.

## XEHttpRequest

`classes/httprequest/XEHttpRequest.class.php`. XE 호환 HTTP 요청. 신형 코드는 `Rhymix\Framework\HTTP` 사용 권장.

## Mail (legacy)

`classes/mail/Mail.class.php`. `Rhymix\Framework\Mail`의 wrapper. XE 시절 인터페이스 유지.

```php
$oMail = new Mail();
$oMail->setSender('이름', 'addr@example.com');
$oMail->setReceiptor('수신자', 'to@example.com');
$oMail->setTitle('제목');
$oMail->setContent('<p>본문</p>');
$oMail->send();
```

## Security 계열 wrapper

- `Password` → `Rhymix\Framework\Password`.
- `Security` → `Rhymix\Framework\Security`.
- `IpFilter` → `Rhymix\Framework\Filters\IpFilter`.
- `EmbedFilter` → `@deprecated` 스텁. `check`/`checkIframeTag`/`checkObjectTag` 등은 no-op(필터링은 `HTMLFilter`로 이관), 화이트리스트 조회는 `Filters\MediaFilter`로 위임.
- `UploadFileFilter` → `Filters\FileContentFilter::check`로 위임 (업로드 파일 내용 검사).
- `Purifier` → `Filters\HTMLFilter` (HTMLPurifier wrapper).

## TemplateHandler

```php
class TemplateHandler extends Rhymix\Framework\Template {}
```

XE 호환 API:

```php
$oTemplate = TemplateHandler::getInstance();
$output = $oTemplate->compile($tpl_path, $tpl_file);
```

## Validator

`classes/validator/Validator.class.php`. 모듈의 `ruleset/*.xml`을 PHP/JS로 변환해 서버측+클라이언트측 검증을 한다.

```php
$oValidator = new Validator('./modules/board/ruleset/insert.xml');
if (!$oValidator->validate($_POST)) {
    $last_error = $oValidator->getLastError(); // array('field'=>..., 'msg'=>...)
}
```

JS 검증 스크립트는 `files/cache/ruleset/<md5해시>.<언어코드>.js`로 자동 컴파일된다(`md5($version.' '.$xml경로)`).

## WidgetHandler

`classes/widget/WidgetHandler.class.php`. 모든 위젯의 부모.

```php
class WidgetHandler {
    public $widget_path = '';
}
```

거의 비어 있고, `proc($args)` 메서드를 자식이 구현한다.

## XML 클래스

`classes/xml/` 디렉토리에는 다음 5개가 있다.

| 클래스 | 용도 |
|---|---|
| `XmlParser` | 범용 XML 파싱 (`@deprecated`, SimpleXML 기반 `XEXMLParser`로 위임) |
| `XmlGenerator` | XML 문자열 생성 |
| `XmlJsFilter` | ruleset XML → JavaScript 검증 코드 컴파일러 |
| `XmlLangParser` | XE legacy lang.xml → PHP |
| `GeneralXmlParser` | 일반 XML 파일 |

XE 호환 `XEXMLParser`는 legacy `classes/xml/`이 아니라 신형 `common/framework/parsers/XEXMLParser.php`에 있다. 신형 파서 전체 목록은 [10-framework.md](10-framework.md) 참고.

## ExtraVar / ExtraItem

`classes/extravar/Extravar.class.php`. 다음 두 줄로 정의된다.

```php
class_alias(Rhymix\Modules\Extravar\Models\ValueCollection::class, 'ExtraVar');
class_alias(Rhymix\Modules\Extravar\Models\Value::class, 'ExtraItem');
```

실제 코드는 `modules/extravar/models/`에 있다.

## Editor (`classes/editor/EditorHandler.class.php`)

모든 에디터 컴포넌트의 부모. **`BaseObject` 상속** — 클래스 본문에는 `setInfo($info)`만 정의되어 있다. 생성자나 `editor_sequence`/`component_path` 같은 속성 선언은 없고, BaseObject가 `#[AllowDynamicProperties]`라 자식이 동적 속성으로 추가한다.

```php
class EditorHandler extends BaseObject {
    public function setInfo($info);   // info->extra_vars의 var->value를 $this->{key}로 펼침

    // 자식이 직접 구현 (부모에 stub 없음)
    public function getPopupContent();
    public function transHTML($xml_obj);
}
```

각 코어 컴포넌트(`modules/editor/components/<name>/<name>.class.php`)는 자체 생성자 `__construct($editor_sequence, $component_path)`를 둬서 두 값을 동적 속성으로 저장한다.

상세: [27-extension-points/editor-component.md](27-extension-points/editor-component.md).

## Mobile

`classes/mobile/Mobile.class.php`. 모바일 감지 진입점. 상세: [23-mobile-detection.md](23-mobile-detection.md).

## 다음 문서

- 전역 함수/상수: [12-helpers-and-globals.md](12-helpers-and-globals.md)
- 신형 클래스: [10-framework.md](10-framework.md)
