# 16. 다국어 (i18n / Lang)

`Rhymix\Framework\Lang` (`common/framework/Lang.php`, 417줄)이 다국어를 담당한다.

## 지원 언어

코어 다국어 디렉토리: `common/lang/`. 12종 이상.

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

`$lang`은 매직 `__set`을 통해 내부 ArrayObject에 채워진다.

### 모듈 namespace로 접근

위 예시는 `lang('board.board_title')` 또는 템플릿에서 `{$lang->board_title}` (모듈 컨텍스트일 때).

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
$text = lang('cmd_write_document');         // 현재 모듈 namespace
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

`Lang` 인스턴스는 ArrayObject를 래핑하며 다음 매직 메서드를 갖는다.

```php
$lang->key = '값';        // __set
echo $lang->key;          // __get
isset($lang->key);        // __isset
unset($lang->key);        // __unset
$lang->arrayKey('a','b'); // __call → 임의 키
```

존재하지 않는 키는 키 자체를 반환(에러 X) — 누락 키 감지를 위해 `$lang->{key} ?? null` 패턴 활용.

## 기본 언어 폴백

특정 언어 파일에 키가 없으면 기본 언어(`config('locale.default_lang')`, 보통 `'ko'`)로 폴백:

```php
$text = $lang->getFromDefaultLang('key');
```

`$lang->get($key)`는 자동으로 폴백한다.

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

쿠키 `lang_type`이 있으면 우선. URL prefix(`config('url.lang_in_url')`)도 우선순위가 높다.

## 시간대 (Timezone)

`Rhymix\Framework\DateTime`와 분리되지만 i18n의 일부.

- `config('locale.internal_timezone')` — DB/서버 내부 시간대 (보통 +9 또는 0).
- `config('locale.default_timezone')` — 사용자에게 보여줄 시간대.

```php
$dt = new Rhymix\Framework\DateTime(time());
echo $dt->format('Y-m-d H:i:s');     // 사용자 timezone
echo $dt->formatInternal('Y-m-d');   // 내부 timezone
```

XE 호환 `zgap()`/`ztime()`도 동일 동작.

## 번역 캐시

다국어 파일은 `files/cache/translations/` 등에 캐싱된다. lang 파일 mtime 비교로 자동 무효화.

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
$message = lang($lang_key) ?: '기본 메시지';
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
