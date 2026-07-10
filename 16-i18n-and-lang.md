# 16. 다국어 (i18n / Lang)

`Rhymix\Framework\Lang` (`common/framework/Lang.php`, 417줄)이 다국어를 담당한다.

## 지원 언어

지원 locale 목록은 `common/defaults/locales.php`에 13종이 등록되어 있다. 코어 번역 디렉토리 `common/lang/`에는 현재 12종의 번역 파일이 있으며, 별도 번역 파일이 없는 locale은 영어 폴백을 사용한다.

| 코드 | 언어 |
|---|---|
| `ko` | 한국어 (기본) |
| `en` | English |
| `zh-CN` | 简体中文 |
| `zh-TW` | 繁體中文 |
| `ja` | 日本語 |
| `vi` | Tiếng Việt |
| `ru` | Русский |
| `es` | Español |
| `fr` | Français |
| `de` | Deutsch |
| `mn` | Монгол |
| `tr` | Türkçe |
| `id` | Bahasa Indonesia (코어 `id.php`가 없으므로 누락 키는 영어 폴백) |

전체 목록은 `common/defaults/locales.php` 참고.

## 모듈별 lang 파일

`modules/<name>/lang/<langtype>.php`. autoloader가 모듈 클래스를 로드할 때 자동으로 lang도 로드한다 (`common/autoload.php:65-69, 82-85`).

```
modules/board/
└── lang/
    ├── ko.php
    ├── en.php
    └── ...
```

파일 내부 형식:

```php
<?php
// modules/board/lang/ko.php
$lang->board_title = '게시판 제목';
$lang->board_list  = '게시판 목록';
$lang->cmd_write_document = '글쓰기';
```

lang 파일의 `$lang`은 `loadDirectory()`가 생성한 `\stdClass`이며(`common/framework/Lang.php:119`) 프로퍼티 직접 할당으로 채워진다 (Lang 인스턴스의 매직 `__set`이 아니라 stdClass에 대한 직접 대입). 내부 저장 구조도 plugin별 `\stdClass`(`_loaded_plugins`, `Lang.php:154`)이고, `\ArrayObject`는 배열형 번역값을 `__get`으로 반환할 때만 래핑에 쓰인다 (`Lang.php:274`).

### 모듈 namespace로 접근

위 예시는 명시적 plugin 키인 `lang('board.board_title')`로 접근할 수 있다. 템플릿의 `{$lang->board_title}`처럼 prefix 없는 키는 현재까지 로드된 plugin들의 검색 우선순위에서 찾는다.

## API

### 인스턴스

```php
$lang = Rhymix\Framework\Lang::getInstance('ko');  // 싱글톤
$lang->loadDirectory(RX_BASEDIR . 'modules/board/lang', 'board');
echo $lang->get('board.board_title');
```

### 헬퍼 함수

```php
$text = lang('board.board_title');
$text = lang('cmd_write_document');         // 로드된 plugin들의 검색 우선순위에서 탐색
lang('custom_key', '동적으로 정의');        // 런타임 설정
```

### Context API

```php
Context::loadLang(RX_BASEDIR . 'addons/myaddon/lang', 'myaddon');
Context::setLangType('en');
$type = Context::getLangType();
$text = Context::getLang('board.board_title');
Context::setLang('board.runtime_key', '값');
$processed = Context::replaceUserLang($html);  // {$user_lang->key} → 실제 값
```

## 매직 메서드

`Lang` 인스턴스는 plugin별 `\stdClass`에 번역을 저장하며(배열값만 반환 시 `\ArrayObject`로 감쌈) 다음 매직 메서드를 갖는다.

```php
$lang->key = '값';        // __set
echo $lang->key;          // __get
isset($lang->key);        // __isset
unset($lang->key);        // __unset
$lang->arrayKey('a','b'); // __call → 임의 키
```

존재하지 않는 키는 키 자체를 반환한다(에러 없음). `$lang->{$key} ?? null`은 `__isset()`을 호출하지만, 현재 언어 인스턴스에 로드된 plugin의 **직접 프로퍼티**만 검사한다. dot-separated 키나 영어 폴백의 존재까지 판정하지 않으므로 범용 누락 키 검사로 사용하면 안 된다 (`common/framework/Lang.php:383-392`). 최종 폴백까지 거친 뒤에도 반환값이 요청한 키와 같으면 실제 번역이 없을 가능성이 높다.

## 기본 언어 폴백

특정 언어 파일에 키가 없으면 항상 영어(`'en'`)로 폴백한다. `getFromDefaultLang()`은 하드코딩된 영어 인스턴스를 사용하며 `config('locale.default_lang')`과 무관하다 (`config('locale.default_lang')`은 폴백 언어가 아니라 lang_type 미지정 시의 현재 언어 기본값):

```php
$text = $lang->getFromDefaultLang('key');  // 영어 번역으로 폴백
```

현재 언어가 en이면 키 자체를 반환하고, 아니면 `self::getInstance('en')->__get($key)`를 호출한다 (`common/framework/Lang.php:223-233`). `loadDirectory()`도 en이 아닐 때 같은 디렉토리를 en 인스턴스로 추가 로드해 폴백을 보장한다 (`Lang.php:156-160`). `$lang->get($key)`는 자동으로 이 폴백을 탄다.

## 인터폴레이션

`BaseObject::setError` 시 `vsprintf` 스타일로 동적 메시지 가능.

```php
$lang->msg_max_files = '최대 %d개까지 업로드 가능합니다.';
$oModule->setError(-1);
$oModule->setMessage(sprintf(lang('msg_max_files'), 10));
```

## 다국어 자동 감지

`config('locale.auto_select_lang')`:

- `true` — 브라우저 `Accept-Language` 헤더로 자동 선택.
- 명시적 설정 시 무시.

URL 기반 언어 선택은 `l` GET 파라미터(`?l=en`)로 이뤄지며 쿠키 `lang_type`보다 우선순위가 높다. 실제 선택 우선순위는 사이트 강제 언어 → `l` 파라미터 → 쿠키 `lang_type` → `auto_select_lang`(Accept-Language) 순이다 (`classes/context/Context.class.php:265-292`). (URL prefix 기반 언어 라우팅이나 `config('url.lang_in_url')` 설정 키는 코어에 존재하지 않는다.)

## 시간대 (Timezone)

`Rhymix\Framework\DateTime`와 분리되지만 i18n의 일부.

- `config('locale.internal_timezone')` — DB/서버 내부 시간대 (보통 +9 또는 0).
- `config('locale.default_timezone')` — 사용자에게 보여줄 시간대.

`Rhymix\Framework\DateTime`은 `\DateTime`을 상속하지 않는 독립 클래스로, 생성자 없이 정적 유틸리티 메서드만 제공한다 (`common/framework/DateTime.php:8`).

```php
echo Rhymix\Framework\DateTime::formatTimestampForCurrentUser('Y-m-d H:i:s', time());  // 사용자 timezone (DateTime.php:45)
echo Rhymix\Framework\DateTime::formatTimestamp('Y-m-d', time());                       // 내부 timezone (DateTime.php:27)
```

XE 호환 헬퍼로는 `zgap()`(사용자·내부 timezone 오프셋을 int로 반환, `common/legacy.php:569`)과 `ztime()`(타임스탬프 문자열을 Unix timestamp로 파싱, `legacy.php:588`)이 있으며, 위 format 메서드와 동작이 다르다.

## 번역 캐시

다국어 XML(`lang.xml`)은 `files/cache/lang/`에 PHP로 컴파일되어 캐싱된다 (신형 `LangParser::compileXMLtoPHP` `common/framework/parsers/LangParser.php:54`, 레거시 `XmlLangParser::$compiled_path` `classes/xml/XmlLangParser.class.php:17` 모두 동일 경로). 일반 `.php` lang 파일은 컴파일 캐시 없이 직접 include된다 (`Lang.php:143`). 캐시는 lang 파일 mtime 비교(`filemtime(cache) > filemtime(src)`)로 자동 무효화된다 (`LangParser.php:55`).

## 흔한 패턴

### 모듈에서 자체 키 정의

```php
// modules/foo/lang/ko.php
$lang->foo_title = 'Foo 제목';
$lang->cmd_action = '실행';

// modules/foo/foo.view.php
public function dispFooIndex()
{
    Context::setBrowserTitle(lang('foo.foo_title'));
    // ...
}
```

### 동적 키

```php
$lang_key = 'foo_' . $type;
$message = lang($lang_key);
if ($message === $lang_key) {
    $message = '기본 메시지';
}
```

### 다국어가 다른 위치에 있는 경우

```php
// 커스텀 위치
Context::loadLang('./plugins/myplugin/lang', 'myplugin');
echo lang('myplugin.greeting');
```

## 다국어 작성 가이드

- 항상 `'ko.php'`를 마스터로 작성하고 나머지를 번역.
- 키는 영문 snake_case (`cmd_login`, `msg_must_login`).
- 카테고리 prefix 권장: `cmd_*`(명령), `msg_*`(메시지), `unit_*`(단위), `about_*`(설명).
- 너무 길어지면 `_section` 같은 그루핑 prefix 사용.

## 다음 문서

- 설정: [25-config-system.md](25-config-system.md)
- Context API: [05-context.md](05-context.md)
