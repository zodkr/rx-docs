# 09. 템플릿과 스킨

Rhymix는 **두 종류의 템플릿 엔진**을 동시에 지원한다.

- **v1 (XE 스타일)** — `common/framework/parsers/template/TemplateParser_v1.php`. `.html` 확장자.
- **v2 (Blade 스타일)** — `common/framework/parsers/template/TemplateParser_v2.php`. `.blade.php` 확장자.

엔진 클래스는 `common/framework/Template.php` (`Rhymix\Framework\Template`). 컴파일 결과는 `files/cache/template/`에 PHP 파일로 저장된다.

## 엔진 선택 규칙

엔진은 **템플릿 파일 단위**로 결정된다 — 스킨/모듈 메타(skin.xml/info.xml 등)에는 엔진 버전을 명시하는 필드가 없다. 결정 흐름 (`Template.php:188-192`, `:432-442`):

1. **`.blade.php` 확장자** — `_setSourcePath`가 `config->version = 2` + `config->autoescape = true`를 초기화한다. 본문에 `<config version="1" />` 또는 `@version(1)`을 넣으면 `parse()`가 `config->version`을 1로 갱신해 v1 파서가 선택되긴 한다(메커니즘상 가능). 단 `_setSourcePath`가 객체 속성으로 켜둔 `autoescape=true`가 런타임에 남아 있어, v1의 **`|auto` 필터**(`TemplateParser_v1.php:806-808`)는 동일 소스를 `.html`로 새로 만들었을 때(`autoescape=false`)와 다르게 동작한다(전자는 escape, 후자는 raw). 기본 `{$v}` 출력은 v1의 `autoescape_config_exists` 검사가 객체 속성이 아닌 본문 텍스트만 보기 때문에 양쪽 모두 `'noescape'`로 동일하지만, `|auto`를 쓰는 코드라면 회귀가 발생한다. 따라서 권장되지 않으며, 사용하려는 엔진의 확장자를 처음부터 선택하는 것이 안전하다.
2. **`.html` 확장자** — 기본값 v1 (`_initConfig`의 `version = 1`, `autoescape = false`).
3. **`.html`에서 v2로 옵트인** — 파일 본문 시작 부분에 `<config version="2" />` 또는 `@version(2)`를 **줄 시작(BOL `(?<=^|\n)`)에 위치**시키면 `parse()`가 `config->version`을 갱신한 뒤 v2 파서를 선택한다.
4. **명시적 생성자 인자** — `new Template($dir, $name, 'blade.php')` 또는 `'html'`로 PHP 코드에서 강제 가능.

### 새 템플릿 작성/마이그레이션 정책

- **새로 만드는 템플릿은 무조건 v2(.blade.php)로 작성**한다. 신규 모듈/스킨/레이아웃/위젯의 진입 템플릿과 부분 템플릿 모두 동일.
- **이미 v1으로 작성된 템플릿은 사용자의 명시적 요청이 없는 한 v2로 변환하지 않는다**. v1과 v2는 한 디렉토리 안에 혼재 가능하므로 동작에 문제가 없으면 그대로 둔다. 변환은 호환 미묘한 차이(예: `cond=""` deprecated, `{$v}` CSS/JS 컨텍스트 경고, 변수 스코프 자동 변환, `@end` 매칭, 이중 escape 정책)에서 회귀를 유발할 수 있어 충분한 테스트 없이 일괄 변환은 위험하다.
- 코어/외부 호환 모듈의 v1 템플릿을 변환할 때는 PR 단위로 1개씩 + 모든 액션 회귀 테스트 후 머지.

## v1 (XE 스타일) 문법

### 변수 출력

```html
{$variable}
{$obj->property}
{$arr['key']}
```

**v1의 기본 escape 동작 — 자동 escape되지 않는다**:

- 기본 `escape_option`은 `autoescape_config_exists ? 'auto' : 'noescape'` (`TemplateParser_v1.php:428`).
- 소스에 `<config autoescape="on" />`가 **없으면** 기본값이 `'noescape'`라 `{$variable}`은 그대로 출력된다 (XSS 가능).
- 예외: `{$lang->key}` / `{lang(...)}`는 다국어 문자열이라 항상 `'noescape'`로 처리.

명시적 escape 필터:

```html
{$variable|escape}        <!-- htmlspecialchars (이중 escape 포함) -->
{$variable|autoescape}    <!-- htmlspecialchars (이중 escape 안 함) -->
{$variable|noescape}      <!-- 그대로 출력 (기본값과 동일) -->
{$variable|escapejs}      <!-- escape_js -->
```

또는 파일 상단에 `<config autoescape="on" />`를 두면 기본값이 `'auto'`(runtime `$this->config->autoescape` 평가)로 바뀐다.

### 조건문

```html
<!--@if($condition)-->
  ...
<!--@elseif($cond2)-->
  ...
<!--@else-->
  ...
<!--@end-->
```

또는 인라인:

```html
<div cond="$is_admin">관리자 영역</div>
```

### 반복문

```html
<!--@foreach($list as $item)-->
  {$item->title}
<!--@end-->
```

또는 인라인:

```html
<li loop="$list=>$key,$value">{$value}</li>
```

### include

```html
<include target="header.html" />
<load target="default.layout.css" media="screen" />
<load target="default.layout.js" type="body" />
```

### 함수 호출

```html
{getUrl('', 'mid', 'free')}
{$lang->key_name}
{Context::getRequestUri()}
{config('view.theme')}
```

### 캐시 무효화 인자

```html
<load target="./common/js/app.js" />     <!-- 자동 ?{filemtime} 부여 -->
```

## v2 (Blade 호환) 엔진

`common/framework/parsers/template/TemplateParser_v2.php` (1232줄). 이름은 "Blade 호환"이지만 **Laravel Blade의 단순 포팅이 아니다**. 자체 컴파일 파이프라인을 가지며, v1의 핵심 기능(상대 경로 자동 변환, 자원 로더, 컨텍스트 인식 escape, fragment, XE-style HTML 주석 디렉티브) 위에 Blade 문법을 얹은 형태다.

### v2 활성화 방법

v2로 만드는 정상 경로는 다음 3가지뿐 (`Template.php:188-192`, `:432-442`):

| 방법 | 위치 |
|---|---|
| `.blade.php` 확장자 사용 | 파일명 자체. `_setSourcePath`가 `version=2` + `autoescape=true` 강제. **권장**. |
| `<config version="2" />` | `.html` 파일 본문 — **줄 시작**(BOL `(?<=^|\n)`)에 위치 |
| `@version(2)` | 위와 같음 (대안 표기) |

명시적으로 `new Template($dir, $name, 'blade.php')`처럼 생성자 인자로 확장자를 줘서 강제하는 것도 가능하지만, 거의 쓰이지 않는다.

#### v2 → v1 opt-out은 권장하지 않음

`.blade.php` 파일에 `<config version="1" />`(또는 `@version(1)`)을 넣어 v1 파서로 보내는 것은 메커니즘상 가능하지만 권장되지 않는다. **정확한 동작 차이**:

- `_setSourcePath`가 `$this->config->autoescape = true`를 객체 속성으로 설정한 상태에서 v1 파서가 실행된다.
- v1 파서는 컴파일 시점에 `str_contains($content, '$this->config->autoescape = ')` (`TemplateParser_v1.php:40`)로 본문 내 `<config autoescape>` 태그 존재 여부만 검사한다. `.blade.php`의 `autoescape=true`는 본문 텍스트가 아닌 객체 속성이라 이 검사에 포착되지 않는다. → **기본 `{$v}`의 default escape_option은 양쪽 모두 `'noescape'`로 동일**.
- **차이가 발생하는 곳은 `|auto` 필터를 명시한 출력 단**이다 — `TemplateParser_v1.php:806-808`의 runtime 분기 `($this->config->autoescape ? htmlspecialchars(...) : (...))`가 `.blade.php`에서는 escape, 같은 코드를 `.html`로 옮기면 raw로 출력된다.
- `|auto` 필터를 안 쓰는 단순 v1 템플릿이라면 결과적으로 동일하게 동작하지만, 테스트 픽스처(`tests/_data/template/`)에도 이 패턴이 없어 보장된 사용법은 아니다.

v1으로 작성하고 싶다면 처음부터 `.html` 확장자를 사용한다.

> 참고 — v2 파서는 런타임 `$this->config->autoescape` 값을 출력 분기에 **사용하지 않는다**. v2의 `_applyEscapeOption`(`TemplateParser_v2.php:1002-1024`)에서 `'autoescape'` 옵션은 무조건 `htmlspecialchars(...)`를 반환하고, default `'autocontext'`는 컨텍스트만 분기하지 `config->autoescape`를 참조하지 않는다. 따라서 `.blade.php`의 `autoescape=true` 초기화는 v2 출력 동작에 영향이 없고, 위에서처럼 v1 파서로 되돌릴 때만 관찰 가능하다.

**스킨/모듈 메타(skin.xml/info.xml)에는 엔진 버전을 명시하는 필드가 없다** — 이전 문서나 외부 자료에서 `<template version="2">` 식의 표기를 본 적이 있다면 그것은 미지원 사항이다.

### 컴파일 파이프라인 (`convert()`의 16단계)

`TemplateParser_v2::convert()` (`:130-158`)는 다음 순서로 16개의 변환 메서드를 적용한다.

| 순서 | 메서드 | 역할 |
|---|---|---|
| 1 | `_preprocess` | 행 끝 공백 제거 |
| 2 | `_addContextSwitches` | HTML / JS / CSS 컨텍스트 마커 자동 주입 |
| 3 | `_removeComments` | `<!--// ... -->`, `{{-- ... --}}` 제거 |
| 4 | `_convertVerbatimSections` | `@verbatim ... @endverbatim` 내부 보존 |
| 5 | `_convertRelativePaths` | `src`/`srcset`/`url()` 자동 절대화 |
| 6 | `_convertPHPSections` | `<?php`/`<?`/`{@ }`/`@php` 변환 + 변수 스코프 |
| 7 | `_convertFragments` | `<fragment>` / `@fragment` |
| 8 | `_convertClassAliases` | `<use>` / `@use` (PSR-4 별칭) |
| 9 | `_convertIncludes` | `<include>` / `@include` / `@each` |
| 10 | `_convertResource` | `<load>` / `@load` / `@unload` |
| 11 | `_convertLoopDirectives` | `@if`/`@foreach` 등 32종 |
| 12 | `_convertInlineDirectives` | `@checked` / `@selected` / `@class` 등 |
| 13 | `_convertMiscDirectives` | `@csrf` / `@json` / `@lang` / `@dump` 등 |
| 14 | `_convertEchoStatements` | `{{ }}`, `{!! !!}`, `{$var}` |
| 15 | `_addDeprecationMessages` | v1 전용 구문 경고 |
| 16 | `_postprocess` | `RX_VERSION` 가드, 버전 마커 prepend |

### 컴파일 캐시

- 출력: `files/cache/template/<relative_path>.compiled.php`.
- 첫 줄: `<?php if (!defined("RX_VERSION")) exit(); ?>` — 직접 호출 차단.
- 캐시 키 = 소스 파일 mtime + `Template.php` 자체 mtime (`Template.php:354-363`). 코어 업데이트 시 자동 재컴파일.
- `config('view.delay_compile')`(초)가 0이 아니면, 최근 변경된 파일은 일정 시간 동안 컨버터 mtime만 비교 → 빠르게 작성 중인 파일의 캐시 회전을 줄임.
- `$template->disableCache()`로 인스턴스별 캐시 끄기 가능.
- 디버그: 컴파일 결과 PHP를 `files/cache/template/`에서 직접 열어 검증.

### Blade와 가장 큰 차이 — 변수 스코프 자동 변환

**모든 `$var`를 `$__Context->var`로 자동 치환**한다 (`_convertVariableScope`, `:1102-1157`). PHP 코드 블록(`<?php ... ?>`, `{@ ... }`, `@php ... @endphp`) **내부에서도 적용**된다 — Laravel Blade와의 가장 큰 차이.

```blade
{{ $title }}        {{-- → htmlspecialchars($__Context->title, ...) --}}

@php
    $count = count($items);   {{-- $items → $__Context->items, $count → $__Context->count --}}
@endphp
```

#### 변환 제외 변수명

다음 변수만 그대로 유지된다.

- `$GLOBALS`, `$_SERVER`, `$_COOKIE`, `$_ENV`, `$_GET`, `$_POST`, `$_REQUEST`, `$_SESSION`
- `$__Context` (자동 주입된 컨텍스트 객체)
- `$this` (Template 인스턴스)
- `$loop` — 자동으로 `end(self::$_loopvars)`로 치환 (현재 반복문의 메타 객체)

#### 함수/클로저 내부

`function (...) use ($foo) { ... }` 같은 익명 함수의 시그니처와 본문은 자동 변환 대상에서 제외된다 (`_convertVariableScope`의 함수 감지 로직). `use ($foo)`로 캡처한 변수는 함수 진입 시점에 `$foo = &$__Context->foo;` 형태로 바인딩되어 양방향 동기화.

#### 진짜 로컬 변수가 필요할 때

스코프 변환을 피하려면 위 예외 변수명을 활용하거나, `_v2_*` 헬퍼처럼 익명 함수로 감싸야 한다. 일반 변수명을 그대로 두면 무조건 Context 속성으로 변환된다.

### 컨텍스트 인식 escape

`_addContextSwitches`가 HTML/JS/CSS 영역을 감지해 컴파일된 PHP에 컨텍스트 마커(`$this->config->context = 'JS';` 등)를 주입한다. `{{ }}` 출력은 `_applyEscapeOption`의 `autocontext` 분기 + `Template::_v2_escape`(`:968-975`) 조합으로 분기한다.

| 위치 | context 값 | 실제 적용 escape |
|---|---|---|
| 평문 HTML | `HTML` | `htmlspecialchars($v, ENT_QUOTES, 'UTF-8', false)` |
| `<script>` 본문 (단 `src=""` 있는 외부 스크립트는 제외) | `JS` | `escape_js($v)` |
| `on*=""`, `href="javascript:"`, `pattern=""` 속성 값 | `JS` | `escape_js($v)` |
| `<style>` 본문, 인라인 `style=""` | `CSS` | **`escape($v)` = htmlspecialchars** (CSS 전용 escape 없음 — `_v2_escape`가 `default` 분기로 떨어짐) |
| 그 외 알 수 없는 context | (없음) | htmlspecialchars (동일) |

```blade
<div class="{{ $name }}">{{ $name }}</div>     {{-- HTML escape --}}
<script>var x = {{ $name }};</script>           {{-- escape_js --}}
<a href="javascript:foo({{ $arg }})">...</a>   {{-- escape_js --}}
<style>.x { color: {{ $color }}; }</style>       {{-- htmlspecialchars (CSS escape는 자동 적용되지 않음) --}}
```

#### CSS 컨텍스트의 한계

`Template::_v2_escape`는 `JS` 케이스만 분기하고 나머지는 `default: return escape(...)`로 떨어진다 (`Template.php:968-975`). 따라서 CSS 컨텍스트 마커가 주입되어 있어도 `{{ $v }}`에 자동으로 `escape_css()`가 호출되지 않는다.

CSS 인젝션이 우려되는 값(예: `url(...)`/`expression(...)` 회피)에는 직접 `{!! escape_css($v) !!}` 또는 화이트리스트 검증 후 출력한다.

#### 그 외 차이

Blade는 항상 HTML escape만 한다 — Rhymix v2는 컨텍스트 정보를 컴파일된 PHP에 보존해 **JS만큼은 별도 escape**를 적용한다.

### 출력 구문과 필터 체인

| 구문 | 동작 |
|---|---|
| `{{ $var }}` | 컨텍스트 escape (autocontext) |
| `{!! $var !!}` | escape 없음 (`noescape`) |
| `{$var}` | v1 호환. HTML 컨텍스트에서만 동작. CSS/JS에선 PHP `E_USER_WARNING` 발생 |
| `{$var|filter1|filter2:option}` | 필터 체인 |

#### null safety

단일 변수 출력(`{{ $foo }}`, `{$foo}`, `{{ $foo->bar }}`)은 자동으로 `?? ''`가 부착되어 `undefined property` 경고를 막는다 (`_arrangeOutputFilters` `:883-886`). 표현식 출력(`{{ $a + $b }}`)에는 부착되지 않는다.

#### `$lang->` 특수 처리

`$lang->key` / `$user_lang->key` 단일 출력은 `autocontext_lang`이 적용되어 이미 escape된 다국어 문자열에 이중 escape하지 않는다 (`:872-880`, `:1011-1012`).

#### 필터 일람 (`_arrangeOutputFilters` `:921-988`)

| 필터 | PHP 변환 |
|---|---|
| `autoescape` | `htmlspecialchars(...)` 강제 |
| `autolang` | `$lang->`만 raw, 나머지 escape |
| `escape` | `htmlspecialchars(..., true)` (이미 escape된 것도 이중) |
| `noescape` | 그대로 출력 |
| `escapejs` / `js` | `escape_js(...)` |
| `json` | `json_encode($v, JSON_HEX_TAG|JSON_HEX_AMP|...)` + 컨텍스트 인식 |
| `strip` / `strip_tags[:tags]` | `strip_tags($v, $tags)` |
| `trim` | `trim($v)` |
| `urlencode` | `rawurlencode($v)` |
| `lower` | `strtolower($v)` |
| `upper` | `strtoupper($v)` |
| `nl2br` | `nl2br(escaped $v)` |
| `join[:delim]` | `implode($delim, $v)` (기본 `, `) |
| `date[:format]` | `getDisplayDateTime(ztime($v), $format)` (기본 `Y-m-d H:i:s`) |
| `format` / `number_format[:decimals]` | `number_format($v, $decimals)` |
| `shorten` / `number_shorten[:digits]` | `number_shorten($v, $digits)` |
| `link[:url]` | `<a href="$url">$v</a>` 또는 자체가 링크 |

인식 안 되는 필터는 컴파일된 PHP에 `'INVALID FILTER (...)'` 문자열로 남는다.

### 디렉티브 일람

#### 블록 디렉티브 (paired — `@end<name>` 또는 `@end` 필요)

| 디렉티브 | 변환 |
|---|---|
| `@if(...)` ... `@elseif(...)` ... `@else` ... `@endif` | `if/elseif/else/endif` |
| `@unless(...)` ... `@endunless` | `if (!(...))` ... `endif` |
| `@for(...)` ... `@endfor` | `for/endfor` |
| `@while(...)` ... `@endwhile` | `while/endwhile` |
| `@switch(...)` ... `@case(...)` ... `@default` ... `@break` ... `@endswitch` | `switch/case/default/break/endswitch` |
| `@foreach($arr as $v)` ... `@endforeach` | `foreach` + `$loop` 메타 객체 자동 |
| `@forelse($arr as $v)` ... `@empty` ... `@endforelse` | `foreach` + 빈 배열 처리 |
| `@once` ... `@endonce` | 첫 호출만 실행 (전역 `$GLOBALS['tplv2_once']` 키로 관리) |
| `@fragment('name')` ... `@endfragment` | ob_start + `$this->_fragments[$name] = ob_get_flush()` |
| `@push('name')` ... `@endpush` | 스택에 append |
| `@pushif($cond, 'name')` ... `@endpushif` | 조건부 push |
| `@pushonce('name')` ... `@endpushonce` | 중복 제거 push |
| `@prepend('name')` ... `@endprepend` | 스택 앞에 |
| `@prependif`, `@prependonce` | 위와 동일 (앞) |
| `@isset($v)` ... `@endisset` | `isset` 가드 |
| `@unset($v)` ... `@endunset` | `!isset` 가드 |
| `@empty($v)` ... `@endempty` | `empty` 가드 |
| `@admin` ... `@endadmin` | `is_admin === 'Y'` 회원만 |
| `@auth('type')` ... `@endauth` | `member`/`manager`/`admin` |
| `@guest` ... `@endguest` | 비로그인만 |
| `@can('cap')` / `@cannot` / `@canany(['a','b'])` ... `@end*` | `Rhymix\Modules\Module\Models\Permission`의 `can()` 호출 |
| `@desktop` / `@mobile` ... `@end*` | `UA::isMobile()` 직접 호출 + 태블릿은 `config('mobile.tablets')` 기준. **`Mobile::isFromMobilePhone()`을 거치지 않으므로** 사용자의 `m=0/1` 파라미터/`FullBrowse` 쿠키/`config('mobile.enabled')` 토글이 반영되지 않는다 (`Template::_v2_isMobile` `:957-960`). 사용자 토글까지 따라야 하면 `@if(\Mobile::isFromMobilePhone())` 사용 |
| `@env('APP_ENV')` ... `@endenv` | `$_ENV[$key]` 존재 |
| `@error('field_id?')` ... `@enderror` | Validator 에러 검사 (`XE_VALIDATOR_ID`) |

#### 단일 디렉티브

`@else`, `@elseif`, `@case`, `@default`, `@continue`, `@break`.

#### 종료 디렉티브의 자동 매칭

`@end`만 써도 가장 안쪽 스택의 디렉티브를 종료한다 (`:651-655`). v1과의 호환을 위함. 단 균형이 맞지 않으면 컴파일된 PHP에서 "unexpected end of file" 발생.

권장 — `@endif`/`@endforeach`처럼 명시적 종료. `@end`는 v1에서 옮긴 템플릿에만.

#### 대소문자 변형

`_convertLoopDirectives` (`:625-637`)이 디렉티브 정규식을 빌드할 때 단어 끝 `if`/`once`에 한해 대소문자 양쪽을 허용한다.

- **시작 디렉티브 `@if` / `@once`** — 단어 시작 위치이므로 `(?<=\w)` lookbehind에 걸리지 않아 **소문자만** 인식. `@If`/`@Once`는 매칭되지 않는다.
- **시작 디렉티브 `@pushif` / `@pushonce` / `@pushIf` / `@pushOnce`** — `if`/`once` 직전에 단어 문자가 있으므로 양쪽 인식.
- **종료 디렉티브 `@end<name>`** — 종료 디렉티브 빌드 코드가 첫 글자를 `[xX]` 형식으로 만든다. 따라서 `@endif`/`@endIf`, `@endonce`/`@endOnce`, `@endpush`/`@endPush` 등이 모두 매칭된다.

추천 — 항상 소문자로 통일.

#### XE-style HTML 주석 형태

모든 블록 디렉티브는 `<!--@directive(...)-->` 형식으로도 인식된다. v1 템플릿 마이그레이션 편의.

```blade
<!--@if($cond)-->
    ...
<!--@end-->
```

위 두 줄은 v1과 v2 모두에서 동작한다.

### 인라인 디렉티브

#### `@checked` / `@selected` / `@disabled` / `@readonly` / `@required`

조건 만족 시 동명 속성 출력. Blade와 동일.

```blade
<input type="checkbox" @checked($subscribed) />
<option value="A" @selected($value === 'A')>A</option>
```

XE-style 변형:

```html
<input type="checkbox" checked="checked"|if="$subscribed" />
<option value="A" selected="selected"|if="$value === 'A'">A</option>
```

`|if=""`, `|when=""`, `|cond=""` (3개 동일), `|unless=""` (역).

#### `@class` / `@style`

```blade
<div @class([
    'btn',                            {{-- 항상 --}}
    'btn-primary' => $isPrimary,      {{-- 조건부 --}}
    'btn-disabled' => $disabled,
])>...</div>

<div @style(['color: red' => $danger, 'font-weight: bold'])>...</div>
```

`_v2_buildAttribute`가 배열을 평가해 단일 속성 문자열로 (`Template.php:848-876`).

### include 시스템

| 디렉티브 | 동작 |
|---|---|
| `@include('view')` | 단순 |
| `@include('view', $vars)` | 자식에 `$vars`만 노출 (전역 변수는 차단) |
| `@includeIf('view')` | 파일 없으면 무시 |
| `@includeWhen($cond, 'view', $vars?)` | 조건 만족 시만 |
| `@includeUnless($cond, 'view', $vars?)` | 역 |
| `@each('view', $items, 'item', 'empty_view')` | 각 항목마다 include + 비었을 때 |
| `<include src="view" if="$cond" unless="$cond" vars="$vars" />` | XE-style |

#### 경로 규칙

- 단순 이름(`'view'`) — 같은 디렉토리 기준 + 확장자 자동.
- `'partials/box'` — 서브디렉토리.
- `'^/common/tpl/header'` — `RX_BASEDIR` 기준 절대.

#### 자식 템플릿의 변수 스코프

분기 로직은 `_v2_include` (`Template.php:640-649`) + `execute` (`:457-485`):

```php
// _v2_include
if ($this->vars)        { $template->setVars($this->vars); }
if ($vars !== null)     { $template->addVars($vars); }

// execute
$__Context = $this->vars ?: \Context::getAll();
```

| 부모 vars 상태 | `$vars` 인자 | 자식 `$__Context`의 출처 |
|---|---|---|
| 미설정 (대부분의 진입 템플릿) | 없음 | `Context::getAll()` 폴백 — 부모와 같은 글로벌 컨텍스트 |
| 미설정 | 지정 | `$vars`만. `Context::getAll()` 폴백 차단됨 |
| 설정됨 (이미 include로 들어왔거나 외부에서 `setVars`) | 없음 | 부모의 vars 그대로 전달 |
| 설정됨 | 지정 | 부모 vars + `$vars` 병합 (`addVars`) |

```blade
{{-- 진입 템플릿에서 호출 → 자식이 글로벌 Context 그대로 상속 --}}
@include('child')

{{-- $vars를 주면 해당 키만, Context::getAll() 폴백 차단 --}}
@include('child', ['name' => $user->name, 'role' => 'admin'])
```

이는 Laravel Blade와 다르다 — Blade의 `@include('view', $vars)`는 부모 컨텍스트에 추가만 한다. Rhymix는 vars 인자를 주면 자식 `execute()`가 `Context::getAll()` 폴백 대신 명시 vars만 사용한다.

### 자원 로더 — `@load` / `<load>`

`_v2_loadResource` (`Template.php:669-780`)가 경로/확장자/위치를 추론해 적절한 `Context::loadFile()` / `Context::loadJavascriptPlugin()` / `Context::loadLang()`을 호출.

```blade
@load('script.js')                                  {{-- JS, head --}}
@load('script.js', 'body', 10)                      {{-- 위치 body, index 10 --}}
@load('style.css', 'screen')                        {{-- media query --}}
@load('style.scss', ['primary' => '#f00'])          {{-- SCSS 변수 --}}
@load('^/common/js/plugins/ckeditor')               {{-- JS 플러그인 (plugin.load 처리) --}}
@load('^/modules/myboard/lang')                     {{-- 다국어 디렉토리 --}}
@unload('./old.js')                                  {{-- 자원 해제 --}}
```

#### 자동 추론

| 패턴 | 처리 |
|---|---|
| `^/common/js/plugins/<name>` | `Context::loadJavascriptPlugin($name)` — plugin.load 매니페스트 |
| 경로에 `/lang` 또는 `/lang.xml` | `Context::loadLang(...)` |
| `.js` | JS |
| `.css`, `.scss`, `.less` | CSS (SCSS/LESS는 자동 컴파일) |
| `/css?...` | CSS |
| `css:` / `js:` prefix | type 강제 |
| 기타 | 경고 + 무시 |

XE-style 속성은 **`target`/`src`/`type`/`media`/`index`/`vars` 6개만** 인식된다 (`_convertResource:558`의 정규식). 도크블록 주석에 보이는 `<load lang="...">`는 실제 정규식 대상에 포함되지 않으므로 동작하지 않는다 — 대신 `<load src="./lang" />`처럼 경로 자동 추론(`/lang` 또는 `/lang.xml`로 끝나는 경로)을 사용한다.

```html
<load src="script.js" type="body" index="10" />
<load src="^/common/js/plugins/ckeditor" />
<load src="./lang" />                <!-- 경로에 /lang 포함 → lang 디렉토리 로드 -->
```

상대 경로 `script.js`는 현재 템플릿 디렉토리 기준. `^/...`는 `RX_BASEURL` 기준.

### 상대 경로 자동 변환 (Blade에 없음)

`_convertRelativePaths` (`TemplateParser_v2.php:274-313`)가 다음을 자동으로 절대 경로로 변환.

| 위치 | 변환되는 속성 |
|---|---|
| `<img>`/`<audio>`/`<video>`/`<script>`/`<input>`/`<source>`/`<link>` 태그 | **`src`/`srcset`/`poster` 만** (`<link href="...">`의 `href`는 정규식 대상에서 빠져 있어 변환되지 않음) |
| 모든 태그 인라인 | `style="..."` 내 `url(...)` |
| `<style>` 블록 | 내부 `url(...)` |

변환 제외 — `Template::isRelativePath` (`Template.php:529-532`)가 false인 경로: **첫 토큰이 `http(s)://`/`file:`/`data:`** 이거나, **첫 글자가 `/`(절대 경로)/`{`/`\`/`<`/`$`/`#`/`@`** 이거나, escape sentinel(`&#x1B;`)로 시작.

`^/path`는 isRelativePath() 검사에서 `^`로 시작해 위 제외 목록에 들지 않아 **상대 경로로 분류**된 뒤, `Template::convertPath`가 `^/`를 `RX_BASEURL` prefix로 치환한다.

```blade
<img src="logo.png" />
{{-- → <img src="/modules/myboard/skins/default/logo.png" /> --}}

<img src="^/files/attach/logo.png" />
{{-- → <img src="/files/attach/logo.png" /> --}}

<img src="/files/attach/logo.png" />
{{-- 첫 글자 / → isRelativePath = false → 그대로 (이미 절대 경로) --}}

<img src="https://example.com/logo.png" />
{{-- 그대로 --}}

<link rel="stylesheet" href="style.css" />
{{-- href는 변환 대상이 아님. ^/... 명시 또는 @load 사용 권장 --}}
```

### 클래스 별칭 — `@use` / `<use>`

```blade
@use('Rhymix\Modules\MyBoard\Models\Post', 'Post')

{{-- 이후 짧게 사용 --}}
{{ Post::countByModule($module_srl) }}
```

XE-style:

```html
<use class="Rhymix\Modules\MyBoard\Models\Post" as="Post" />
```

PHP `use` 문과 달리 실제 import는 안 한다 — 단순 문자열 치환 (`_convertClassAliases` `:417-441`).

### Fragment

```blade
@fragment('header')
    <h1>{{ $title }}</h1>
@endfragment
```

XE-style:

```html
<fragment name="header">
    <h1>{$title}</h1>
</fragment>
```

본 출력에도 포함 + `$template->getFragment('header')`로 별도 조회 가능. AJAX 응답의 부분 렌더링, 레이아웃의 영역 추출 등에 활용.

### 스택 (push/prepend/stack)

여러 템플릿이 한 곳에 자원을 모을 때.

```blade
{{-- 자식 템플릿에서 --}}
@push('scripts')
    <script src="my-feature.js"></script>
@endpush

@pushonce('vendor-scripts')
    <script src="lodash.js"></script>      {{-- 같은 내용은 1번만 --}}
@endpushonce

{{-- 레이아웃에서 --}}
<body>
    ...
    @stack('scripts')
</body>
```

`@prepend(...)`/`@prependif`/`@prependonce`는 앞쪽에 누적.

### 기타 디렉티브

| 디렉티브 | 결과 |
|---|---|
| `@csrf` | `<input type="hidden" name="_rx_csrf_token" value="...">` |
| `@json($v)` | 컨텍스트 인식 JSON 출력. JS 컨텍스트면 raw, HTML이면 escape |
| `@lang('key')` | 다국어. `'this.key'`는 현재 모듈/스킨 네임스페이스로 해석 |
| `@dump($v, ...)` | `var_dump` 결과 출력 |
| `@dd($v, ...)` | `var_dump` 후 `exit()` |
| `@stack('name')` | `@push` 누적 출력 |
| `@url('', 'mid', $m, 'act', $a)` | 인자가 그대로 `getUrl(...)`에 전달된다 — `getUrl`은 **가변 인자**(key, val, key, val, ...)이므로 배열을 단일 인자로 넣으면 안 됨. HTML 컨텍스트에선 `getUrl()`, 그 외엔 `getNotEncodedUrl()` + 컨텍스트 escape |
| `@widget($args)` | `WidgetController::getInstance()->execute($args)` — 인자를 그대로 위임 |
| `@php ... @endphp` | PHP 블록 (변수 스코프 자동 변환 적용) |
| `{@ ... }` | 같은 PHP 블록의 단축 형태 |
| `<?php ... ?>` / `<? ... ?>` / `<?= ... ?>` | 동상 |
| `@verbatim ... @endverbatim` | 내부 모든 토큰을 변환 없이 출력 |
| `@@directive`, `@{{ ... }}` | 이스케이프된 디렉티브 (출력 시 `@` 1개 제거) |

### Laravel Blade와의 차이 (요약)

| 항목 | Laravel Blade | Rhymix v2 |
|---|---|---|
| 변수 스코프 | `$var` 그대로 | **자동으로 `$__Context->var`** (PHP 블록 포함) |
| escape | 항상 HTML | **컨텍스트 인식** (HTML/JS/CSS 자동) |
| 상대 경로 | 없음 | `<img src="x.png">` **자동 절대화** |
| 자원 로드 | 없음 (`<link>` 직접) | `@load` 통합 (CSS/JS/SCSS/플러그인/lang) |
| `@include($vars)` 변수 | 부모 + 추가 | **부모 차단** + 명시 변수만 |
| `@layouts`/`@extends`/`@yield`/`@section` | 지원 | **미지원** — `@fragment` + `@stack`로 대체 |
| `@component`/`@slot`/`@props`/`@inject` | 지원 | **미지원** |
| `@error` | session error bag 사용 | Validator (`XE_VALIDATOR_ID`) 사용 |
| `@can` | Policy/Gate | `Rhymix\Modules\Module\Models\Permission::can()` |
| `@end` 자동 매칭 | 안 됨 | **됨** (v1 호환) |
| XE-style `<!--@if-->` | 안 됨 | **인식** (v1 호환) |
| 단일 `{$var}` | 안 됨 | **HTML 컨텍스트에서만 됨** (v1 호환) |
| 필터 체인 `{$v|filter}` | 안 됨 | **됨** (16종 내장 + 옵션) |

### v1 ↔ v2 매핑

| v1 | v2 |
|---|---|
| `{$x}` | `{{ $x }}` (또는 `{$x}` 그대로 — HTML 컨텍스트만) |
| `{$x\|noescape}` | `{!! $x !!}` (또는 `{$x\|noescape}` 그대로) |
| `<!--@if(...)-->` | `@if(...)` (또는 `<!--@if(...)-->` 그대로) |
| `<!--@foreach(...)-->` | `@foreach(...)` |
| `<include target="..." />` | `@include('...')` (또는 그대로) |
| `cond="..."` 속성 | `|if="..."` (인라인) 또는 `@if` 블록 |
| `loop="$arr=>$k,$v"` | `@foreach($arr as $k => $v)` |
| `{getUrl(...)}` | `{{ getUrl(...) }}` |
| `<!--%import-->`, `<!--%load_js_plugin-->`, `<block>` | **deprecated** → `@load`/`@include` 사용 (사용 시 경고) |

### 유의점

1. **PHP 블록 안의 변수도 변환된다**. `@php $count = 0; @endphp`가 `$__Context->count = 0`이 된다 — 진짜 로컬 변수가 필요하면 익명 함수 / `$_GET` 등 예외 변수명 사용.
2. **`{$var}`는 CSS/JS 컨텍스트에서 동작하지 않는다**. 사용 시 `E_USER_WARNING`. 대신 `{{ }}` 또는 `@json()`.
3. **`@end` 자동 매칭은 가능하지만 권장 안 함**. 짝 불일치 시 컴파일된 PHP가 "unexpected end of file"로 실패. 가능하면 명시적 종료.
4. **`@include`의 두 번째 인자는 부모 변수를 차단**한다. 자식이 부모 변수를 사용해야 한다면 인자 생략.
5. **컴파일된 PHP를 직접 디버깅**할 수 있다. `files/cache/template/<path>.compiled.php`를 열어보면 실제 동작 확인 가능.
6. **`@verbatim`은 마크다운/Vue/Handlebars 같은 다른 템플릿 문법과 충돌**할 때 사용.
7. **상대 경로 자동 변환을 막으려면** `data:`/`http:`/`{...}` 등으로 시작하거나 `^/...`로 명시.
8. **v1과 v2 마이그레이션은 점진적으로 가능**. 같은 디렉토리에 `.html` (v1)과 `.blade.php` (v2)을 섞어도 동작.
9. **컨버터 파일(`Template.php`/`TemplateParser_v2.php`) mtime이 캐시 키에 포함**된다. 코어 업데이트 시 전체 템플릿 캐시가 무효화될 수 있음을 인지.

## 템플릿에서 사용 가능한 기본 변수

모듈 View가 컴파일하는 템플릿에서는 다음이 자동 주입된다 (`Context::set`된 값 포함).

| 변수 | 의미 |
|---|---|
| `$lang` | 다국어 객체 (`$lang->key`로 접근) |
| `$logged_info` | 로그인 회원 정보 또는 false |
| `$is_logged` | 로그인 여부 |
| `$module_info` | 현재 모듈 인스턴스 정보 |
| `$grant` | 권한 객체 (모듈 액션 내) |
| `$user` | 현재 사용자 (`SessionHelper`) |
| `$mid` | 현재 mid |
| `$site_module_info` | 현재 도메인 루트 모듈 |
| `$layout_info` | 현재 레이아웃 (레이아웃 내부) |
| `$content` | 본문 HTML (레이아웃 내부) |

## 스킨 디렉토리 구조

### 모듈 스킨

```
modules/<module>/
├── skins/<skin>/              # PC 스킨
│   ├── skin.xml               # 스킨 메타 + extra_vars + colorset
│   ├── list.html, view.html   # 진입 템플릿 (모듈마다 다름)
│   ├── _header.html, _footer.html
│   └── images/, css/, js/
└── m.skins/<mskin>/           # 모바일 스킨
    └── (동일 구조)
```

스킨 정보 파싱: `common/framework/parsers/SkinInfoParser.php`. 결과 캐싱: `ModuleModel::loadSkinInfo`.

`skin.xml` 작성법: [27-extension-points/module-skin.md](27-extension-points/module-skin.md).

### 레이아웃

```
layouts/<name>/                # PC 레이아웃
├── conf/info.xml              # 메타 + extra_vars + menus
├── layout.html                # 진입 템플릿 (필수)
├── <name>.layout.css
├── <name>.layout.js
└── thumbnail.png

m.layouts/<name>/              # 모바일 레이아웃 (동일 구조)
```

레이아웃 정보 파싱: `common/framework/parsers/LayoutInfoParser.php`.

상세: [27-extension-points/layout.md](27-extension-points/layout.md).

## 스킨 변수 (`$skin_vars`)

`skin.xml`의 `<extra_vars>`로 정의한 사용자 입력값은 템플릿에서 `$module_info->{var_id}` 또는 `$skin_vars->{var_id}` 형식으로 접근.

```xml
<extra_vars>
    <var name="show_thumbnail" type="select" default="Y">
        <title xml:lang="ko">썸네일 표시</title>
        <options>
            <option value="Y" />
            <option value="N" />
        </options>
    </var>
</extra_vars>
```

```html
<!--@if($module_info->show_thumbnail == 'Y')-->
  <img src="..." />
<!--@end-->
```

## 컬러셋 (`colorset`)

`skin.xml`의 `<colorset>`으로 정의. 관리자가 색상 테마를 선택할 수 있다.

```xml
<colorset>
    <color name="white">
        <title xml:lang="ko">화이트</title>
    </color>
    <color name="black">
        <title xml:lang="ko">블랙</title>
    </color>
</colorset>
```

템플릿에서 `$module_info->colorset` 또는 `$colorset`으로 접근. CSS 파일명에 적용하는 패턴이 흔하다 (예: `xe_official.<colorset>.css`).

## 스킨 적용 알고리즘

`ModuleObject::setLayoutAndTemplatePaths()` (`ModuleObject.class.php:697`):

```
if PC:
    skin = config.skin or 'default'
    if skin == '/USE_DEFAULT/': use ModuleModel::getModuleDefaultSkin(module, 'P')
    template_path = "<module_path>/skins/<skin>/"
    if not exists: template_path = "<module_path>/skins/default/"

elif Mobile:
    mskin = config.mskin or 'default'
    if mskin == '/USE_DEFAULT/': use getModuleDefaultSkin(module, 'M')
    if mskin == '/USE_RESPONSIVE/': fallback to PC skin
    template_path = "<module_path>/m.skins/<mskin>/"
    if not exists: template_path = "<module_path>/m.skins/default/"
```

## 컴파일 캐시

- 위치: `files/cache/template/<hash>.php`.
- 캐시 키: 소스 파일 절대경로 + mtime + 파서 버전.
- `Config::get('cache.no_template_cache') === true`면 무효화 (개발용).
- 소스 변경 시 자동 무효화.

`Rhymix\Framework\Template::$_delay_compile` 플래그가 동시성 잠금 역할.

## Template 인스턴스 직접 사용

```php
$tpl = new Rhymix\Framework\Template('./modules/foo/tpl', 'index');
$tpl->vars = ['title' => '제목', 'list' => $list];
$html = $tpl->compile();
echo $html;
```

레거시 `TemplateHandler::getInstance()->compile($path, $file)`도 동일 결과를 반환한다 — 신형의 wrapper.

## 부분 페이지 렌더링 (Partial Page Rendering)

XHR로 일부 영역만 갱신할 때 사용. `Context::get('isLayoutDrop')` 또는 `HTMLDisplayHandler::isPartialPageRendering()`이 활성 신호.

활성 시 레이아웃을 `common/tpl/default_layout.html`로 대체해 본문만 출력한다.

## 다음 문서

- 새 모듈 스킨 만들기: [27-extension-points/module-skin.md](27-extension-points/module-skin.md)
- 새 레이아웃 만들기: [27-extension-points/layout.md](27-extension-points/layout.md)
- Template 클래스 상세: [10-framework.md](10-framework.md)
