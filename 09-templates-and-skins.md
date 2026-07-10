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
4. **명시적 생성자 인자** — `new Template($dir, $name, 'blade.php')` 또는 `'html'`로 확장자 자동 탐색 결과를 지정할 수 있다. 단, 파일 본문의 `@version(...)`/`<config version="..." />`이 파서 버전을 다시 바꿀 수 있으므로 엔진을 절대적으로 고정하는 옵션은 아니다.

확장자를 생략한 `new Template($dir, $name)`이나 모듈의 `setTemplateFile('list')`는 같은 basename에서 **`.html`을 먼저 찾고 그 다음 `.blade.php`를 찾는다** (`Template.php:149-168`). 따라서 마이그레이션 중 두 파일을 동시에 남겨 두면 기존 `.html`이 계속 선택된다. v2로 전환하려면 호출부에서 확장자를 명시하거나, 검증을 마친 뒤 중복 `.html`을 제거해야 한다.

### 새 템플릿 작성/마이그레이션 정책

- **새로 만드는 템플릿은 v2(`.blade.php`)를 강하게 권장**한다. v1도 호환을 위해 계속 동작하지만 파서 주석에서 신규 기능 추가가 없다고 명시하고 있다. 신규 모듈/스킨/레이아웃/위젯의 진입 템플릿과 부분 템플릿은 가능한 한 같은 엔진으로 맞춘다.
- **이미 v1으로 작성된 템플릿은 사용자의 명시적 요청이 없는 한 v2로 변환하지 않는다**. v1과 v2는 한 디렉토리 안에 둘 수 있지만 같은 basename의 `.html` 우선순위와 include의 부모 확장자 상속을 고려해야 한다. 변환은 호환 미묘한 차이(예: `cond=""` 미지원 경고, `{$v}` CSS/JS 컨텍스트 경고, 변수 스코프 자동 변환, `@end` 매칭, 이중 escape 정책)에서 회귀를 유발할 수 있어 충분한 테스트 없이 일괄 변환은 위험하다.
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
{$variable|auto}          <!-- config.autoescape 값에 따라 escape/raw -->
{$variable|noescape}      <!-- 그대로 출력 (기본값과 동일) -->
{$variable|escapejs}      <!-- escape_js -->
```

또는 `<config autoescape="on" />`를 **들여쓰기 없이 줄 첫 칸**에 두면 기본값이 `'auto'`(runtime `$this->config->autoescape` 평가)로 바뀐다. 공백이나 탭으로 들여쓰면 `Template::parse()`의 선행 감지가 실패한다. 이후 v1 파서가 태그를 runtime 설정문으로 바꿀 수는 있지만 기본 `{$value}`의 escape 방식은 이미 `'noescape'`로 결정된 뒤이며, `|auto` 같은 runtime 의존 필터만 영향을 받는 불완전한 상태가 된다. 하나의 `<config>`에 여러 속성을 합치지 말고 각 설정을 별도 줄 첫 칸에 작성한다.

`layouts/<name>/layout.html`의 단순 `{$content}`는 호환 특례로 raw 출력되지만, 모바일 레이아웃·다른 위치·향후 마이그레이션에서 같은 특례에 의존해서는 안 된다. 본문 HTML임이 확실한 레이아웃 콘텐츠는 `{$content|noescape}`처럼 의도를 명시한다.

v1은 출력 위치가 HTML인지 JS/CSS인지 자동 판별하지 않는다. autoescape를 켠 템플릿에서 JS 문자열을 출력할 때는 JS escape 결과가 다시 HTML escape되지 않도록 순서를 명시한다.

```html
<script>
const message = '{$message|escapejs|noescape}';
</script>
```

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

v1의 `cond`·`loop` 속성은 큰따옴표를 사용한다. `source`, `track`, `embed`, `wbr`처럼 오래된 v1 self-closing 목록에 없는 void element에 조건이나 반복을 붙일 때는 파서가 닫는 태그를 잘못 찾지 않도록 `<source ... />`처럼 `/>`를 명시한다. 주석형 디렉티브 이름도 소문자로 통일한다.

### include

```html
<include target="header.html" />
<load target="default.layout.css" media="screen" />
<load target="default.layout.js" type="body" />
```

`<include target>`과 `<load target>`의 경로는 **컴파일 시점의 정적 문자열**이다. `target="{$view}"`, `target="css/{$theme}.css"`, `target="{{ $view }}"`처럼 출력 표현식을 넣어도 파일명을 평가하거나 조합하지 않는다. 동적으로 대상을 선택해야 한다면 v2의 `@include($view)`/`@load($asset)`을 사용하거나 모듈 PHP 코드에서 허용 목록을 검사한 뒤 처리한다.

일반 HTML 자원 속성은 다르다. 예를 들어 v1의 `<img src="images/{$file}">`는 정적 `images/` 부분을 템플릿 디렉토리 기준으로 보정한 뒤 `$file`을 출력할 수 있다. 반면 `<img src="{$url}">`처럼 값 전체가 표현식이면 경로를 보정하지 않고 `$url`을 그대로 사용한다.

v1의 자동 경로 변환 범위는 제한적이다.

| 대상 | 자동 변환 |
|---|---|
| `img`/`input`/`script`의 `src="..."` | 지원 |
| `img`/`source`/`link`의 `srcset="..."` | 지원 |
| `href`, `poster`, CSS `url()`, `audio`/`video`/`source`의 `src` | 미지원 |
| 작은따옴표 속성 | 미지원 |

따라서 `<a href="./detail.html">`은 스킨 디렉토리가 아니라 현재 요청 URL을 기준으로 브라우저가 해석한다. 내부 링크는 `getUrl()`을 사용하고, 루트 자원은 `^/`를 사용한다. `srcset`은 쉼표로 단순 분리하므로 쉼표를 포함하는 data URI에는 사용하지 않는 것이 안전하다.

### 주석

```html
<!--// 이 내용은 컴파일 결과에서 제거된다 -->
<!--//
여러 줄도 v1에서는 제거된다.
-->
```

v1의 서버측 주석은 `<!--// ... -->`이며 여러 줄을 지원하지만 중첩은 지원하지 않는다 (`TemplateParser_v1.php:44-45`, dot-all 정규식). 일반 HTML 주석 `<!-- ... -->`은 브라우저로 전달되고, 그 안의 `{$value}`나 `<!--@if-->`도 템플릿 파서가 처리할 수 있다. 민감한 값이나 실행시키면 안 되는 코드를 일반 HTML 주석으로 감추지 않는다.

### v1 변수 스코프와 함수 호출

v1도 일반 `$변수`를 `$__Context->변수`로 변환한다. 따라서 `{@ $count = 1 }`은 독립 로컬 변수가 아니라 템플릿 Context의 `count`에 할당한다. 선택적 변수를 조건에 사용할 때는 `<!--@if(!empty($foo))-->` 또는 `isset()`처럼 존재 여부를 명시하는 것이 안전하다.

`{foo()}` 형태의 전역 함수 호출은 **템플릿을 컴파일하는 시점**에 `function_exists('foo')`가 참이어야 변환된다. 아직 로드되지 않은 함수는 원문으로 남을 수 있고 그 결과가 템플릿 캐시에 유지될 수 있으므로, 확실히 로드되는 코어 함수나 클래스 정적 메서드를 사용한다. 상수는 `{\RX_BASEDIR}`처럼 선행 백슬래시가 있어야 v1 출력식으로 확실히 인식된다.

### v1 폼 자동 보완

v1 파서는 `<form>`에 `act`, `mid`, `error_return_url` 등의 hidden input과 ruleset 처리를 자동으로 보완한다. 이 기능은 CSRF 토큰 추가와는 별개다. 자동 보완이 필요 없는 폼은 다음처럼 명시한다.

```html
<form rx-autoform="false">
```

return URL만 제외하려면 `no-error-return-url="true"` 또는 호환 별칭 `no-return-url="true"`를 사용한다.

이 자동 보완은 v1 파서 전용이다. v2 템플릿은 필요한 `act`·`mid`·return URL을 직접 작성하고, 상태 변경 폼에는 `@csrf`를 명시한다.

### 함수 호출

```html
{getUrl('', 'mid', 'free')}
{$lang->key_name}
{Context::getRequestUri()}
{config('view.theme')}
```

### 로컬 자원의 브라우저 캐시 무효화

```html
<load target="^/common/js/app.js" />     <!-- 루트 자원, 자동 ?t=<filemtime> 부여 -->
<load target="./js/skin.js" />           <!-- 현재 템플릿 디렉토리 기준 -->
```

로컬 CSS/JS는 최종 출력 단계에서 파일 mtime 쿼리스트링이 붙을 수 있다. 외부 URL이나 존재하지 않는 파일에는 동일하게 적용된다고 가정하지 않는다.

## v2 (Blade 호환) 엔진

`common/framework/parsers/template/TemplateParser_v2.php` (1232줄). 이름은 "Blade 호환"이지만 **Laravel Blade의 단순 포팅이 아니다**. v1의 상대 경로 변환·자원 로더·XE-style 디렉티브 일부를 계승하고, 컨텍스트 인식 escape·fragment·Blade-style 디렉티브를 추가한 독립 파서다. `<fragment>`는 XE와 비슷한 표기라는 뜻일 뿐 v1 파서에서 지원되는 문법은 아니다.

### v2 활성화 방법

v2로 만드는 정상 경로는 다음 3가지뿐 (`Template.php:188-192`, `:432-442`):

| 방법 | 위치 |
|---|---|
| `.blade.php` 확장자 사용 | 파일명 자체. `_setSourcePath`가 기본 `version=2` + `autoescape=true`로 초기화. **권장**. |
| `<config version="2" />` | `.html` 파일 본문 — **줄 시작**(BOL `(?<=^\|\n)`)에 위치 |
| `@version(2)` | 위와 같음 (대안 표기) |

명시적으로 `new Template($dir, $name, 'blade.php')`처럼 확장자 없는 파일명의 탐색 확장자를 지정할 수도 있지만, 거의 쓰이지 않는다.

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
| 11 | `_convertLoopDirectives` | `@if`/`@foreach` 등 블록·제어 디렉티브 |
| 12 | `_convertInlineDirectives` | `@checked` / `@selected` / `@class` 등 |
| 13 | `_convertMiscDirectives` | `@csrf` / `@json` / `@lang` / `@dump` 등 |
| 14 | `_convertEchoStatements` | `{{ }}`, `{!! !!}`, `{$var}` |
| 15 | `_addDeprecationMessages` | v1 전용 구문 경고 |
| 16 | `_postprocess` | `RX_VERSION` 가드, 버전 마커 prepend |

### 주석과 `@verbatim`의 실제 범위

v2가 출력에서 제거하는 주석은 아래 두 형식뿐이며, **여는 표식과 닫는 표식이 같은 물리적 줄에 있어야 하고 내용도 비어 있지 않아야 한다** (`TemplateParser_v2.php:260-265`).

```blade
{{-- 한 줄 Blade-style 주석 --}}
<!--// 한 줄 XE-style 주석 -->
```

다음과 같은 여러 줄 주석은 지원되지 않는다.

```blade
{{--
이 주석은 제거되지 않으며, {{ }} 출력식으로 오인되어
컴파일된 PHP 문법까지 깨뜨릴 수 있다.
--}}
```

여러 줄을 임시로 제외하려면 각 줄을 각각 한 줄 주석으로 감싼다. 일반 HTML 주석 `<!-- ... -->`은 서버측 주석이 아니므로 응답에 그대로 노출되며, 내부의 템플릿 표현식과 디렉티브도 파싱·실행될 수 있다.

`@verbatim ... @endverbatim`도 완전한 원문 보존 블록은 아니다. 변환 순서상 컨텍스트 마커 삽입과 한 줄 주석 제거는 `@verbatim`보다 먼저 실행되고, 상대 `src`·`url()` 경로 변환은 그 뒤에도 실행된다. `@verbatim`은 주로 `@`, `{{ }}`, `{$...}`, `$` 같은 템플릿 토큰을 문자 그대로 출력하기 위한 기능이며 중첩을 지원하지 않는다. 비밀 정보나 서버측 주석 용도로 사용하면 안 되며, 내부의 일반 HTML은 그대로 클라이언트에 전달된다.

### 컴파일 캐시

- 출력: `files/cache/template/<relative_path>.compiled.php`.
- 첫 줄: `<?php if (!defined("RX_VERSION")) exit(); ?>` — 직접 호출 차단.
- 재컴파일 판단 기준 = 소스 파일 mtime과 `Template.php` 자체 mtime 중 최신값 (`Template.php:354-366`). 경로 기반 캐시 파일명이 "키"이고, mtime은 신선도 판정에 사용된다.
- `config('view.delay_compile')`(초)가 0이 아니면, 최근 변경된 파일은 일정 시간 동안 컨버터 mtime만 비교 → 빠르게 작성 중인 파일의 캐시 회전을 줄임.
- `$template->disableCache()`는 매 호출 재컴파일을 강제하지만, 컴파일 결과를 같은 캐시 파일에 **쓰고 그 파일을 include하는 구조는 유지**된다. 쓰기 권한 문제를 우회하거나 디스크 캐시를 완전히 없애는 옵션이 아니다.
- 디버그: 컴파일 결과 PHP를 `files/cache/template/`에서 열어 검증할 수 있지만 생성 파일을 직접 수정하면 다음 컴파일에 덮어써진다.

`TemplateParser_v1.php`나 `TemplateParser_v2.php`의 mtime은 신선도 판정에 직접 포함되지 않는다. 파서만 수정한 개발 환경에서는 기존 템플릿 캐시를 삭제하거나 `Template.php`의 mtime도 갱신해야 새 파서 결과를 확실히 확인할 수 있다. 또한 `view.delay_compile`이 0보다 크면 최근 수정한 템플릿이 설정 시간 동안 이전 캐시로 보일 수 있으므로 개발 중에는 이 설정과 캐시 상태를 함께 확인한다.

### Blade와 가장 큰 차이 — 변수 스코프 자동 변환

일반적인 `$var`를 `$__Context->var`로 자동 치환한다 (`_convertVariableScope`, `:1102-1157`). PHP 코드 블록(`<?php ... ?>`, `{@ ... }`, `@php ... @endphp`) **내부에서도 적용**된다 — Laravel Blade와의 가장 큰 차이. 다만 아래 예약 변수와 명시적으로 escape한 `$`는 예외다.

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

#### 함수/클로저 내부의 한계

파서 정규식이 인식한 `function (...) use ($foo) { ... }`의 시그니처와 본문은 자동 변환 대상에서 제외된다. `use ($foo)`로 캡처한 변수는 함수 바깥에서 `$foo = &$__Context->foo;` 형태로 바인딩되어 양방향 동기화된다.

그러나 이 보호 로직은 `function` 문법과 제한적인 반환 타입 패턴만 인식한다. **화살표 함수 `fn($x) => ...`는 보호되지 않아 매개변수까지 `$__Context->x`로 바뀔 수 있고**, 복잡한 nullable·union·네임스페이스 반환 타입도 정규식 범위를 벗어날 수 있다. 템플릿 안에서 복잡한 콜백을 만들기보다 PHP 클래스의 메서드로 옮기는 것이 안전하다.

#### 진짜 로컬 변수가 필요할 때

PHP 코드에서 진짜 로컬 변수가 필요하면 달러 기호를 `\$local`처럼 escape할 수 있다. 후처리 단계가 백슬래시를 제거하므로 컴파일 결과에는 `$local`로 남는다.

```blade
@php
    \$localCount = 0;   {{-- 컴파일 결과의 로컬 $localCount --}}
    $sharedCount = 0;   {{-- $__Context->sharedCount --}}
@endphp
```

여기서 `\$local`은 **로컬 변수 표기**이지 문자 `$`를 출력하는 escape가 아니다. 문자 그대로 `$name`을 출력하려면 HTML의 `&#36;name`, `@verbatim`, 또는 PHP에서 변수 토큰이 생기지 않는 문자열 조합을 사용한다.

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
<script>const x = @json($name);</script>         {{-- 타입을 보존한 올바른 JS 값 --}}
<button onclick="foo('{{ $arg }}')">...</button> {{-- JS 문자열 내부 escape_js --}}
<style>.x { color: {{ $color }}; }</style>       {{-- HTML escape뿐이며 CSS 검증은 별도 --}}
```

`escape_js()`는 JavaScript **문자열 리터럴 내부 내용**을 escape할 뿐 따옴표를 붙이지 않는다. 따라서 `const x = {{ $name }};`은 `$name`이 문자열일 때 유효한 JS 값을 만들지 못한다. 타입을 보존하는 값은 `@json($name)`, 이미 따옴표 안에 있는 문자열 조각은 `'{{ $name }}'`을 사용한다.

컨텍스트 감지는 정규식 기반이다. `style="..."`, `on...="..."`, `href="javascript:..."`, `pattern="..."`처럼 **큰따옴표 속성만** 감지하므로 동적 JS/CSS 값이 있는 속성을 작은따옴표로 쓰지 않는다. `<script type="application/json">`도 JS 컨텍스트로 취급되므로 JSON 데이터에는 `@json()`을 사용한다.

#### CSS 컨텍스트의 한계

`Template::_v2_escape`는 `JS` 케이스만 분기하고 나머지는 `default: return escape(...)`로 떨어진다 (`Template.php:968-975`). 따라서 CSS 컨텍스트 마커가 주입되어 있어도 `{{ $v }}`에 자동으로 `escape_css()`가 호출되지 않는다.

`escape_css()`도 허용된 문자만 남기는 단순 필터일 뿐 값의 CSS 의미를 검증하지 않는다. 색상은 `#` + hex, 길이는 숫자 + 허용 단위처럼 **용도별 allowlist를 먼저 검사**하고, 필요한 경우에만 `{!! escape_css($v) !!}`로 출력한다. 사용자 입력으로 완전한 선언이나 `url(...)`을 조립하지 않는다.

#### 그 외 차이

Blade는 항상 HTML escape만 한다 — Rhymix v2는 컨텍스트 정보를 컴파일된 PHP에 보존해 **JS만큼은 별도 escape**를 적용한다.

`{{ }}`의 HTML escape는 URL scheme 검사가 아니다. `href="{{ $url }}"`이나 `src="{{ $url }}"`에 `javascript:`·위험한 `data:` URL이 들어오는 것을 막지 못하므로 외부 입력 URL은 허용 scheme과 호스트를 별도로 검증한다. `{!! !!}`는 아무 escape도 하지 않으므로 신뢰하거나 정화한 HTML에만 사용한다. `$lang->key`와 `@lang(...)`도 HTML 컨텍스트에서 raw로 처리되므로 번역 포맷 인자에 사용자 입력을 그대로 결합하지 않는다.

### 출력 구문과 필터 체인

| 구문 | 동작 |
|---|---|
| `{{ $var }}` | 컨텍스트 escape (autocontext) |
| `{!! $var !!}` | escape 없음 (`noescape`) |
| `{$var}` | v1 호환. HTML 컨텍스트에서만 동작. CSS/JS에선 PHP `E_USER_WARNING` 발생 |
| `{$var\|filter1\|filter2:option}` | 필터 체인 |

#### null safety

단일 변수 출력(`{{ $foo }}`, `{$foo}`, `{{ $foo->bar }}`)은 자동으로 `?? ''`가 부착되어 `undefined property` 경고를 막는다 (`_arrangeOutputFilters` `:883-886`). 표현식 출력(`{{ $a + $b }}`)에는 부착되지 않는다.

#### `$lang->` 특수 처리

`$lang->key` / `$user_lang->key` 단일 출력은 `autocontext_lang`이 적용되어 이미 escape된 다국어 문자열에 이중 escape하지 않는다 (`:872-880`, `:1011-1012`).

#### 필터 일람 (`_arrangeOutputFilters` `:921-988`)

| 필터 | PHP 변환 |
|---|---|
| `autoescape` | `htmlspecialchars(...)` 강제 |
| `autolang` | 결과 문자열이 `$lang->...`/`$user_lang->...` 패턴일 때만 raw, 그 외 HTML escape. 일반 `$lang->key` 자동 특례와는 별도 |
| `escape` | `htmlspecialchars(..., true)` (이미 escape된 것도 이중) |
| `noescape` | 그대로 출력 |
| `escapejs` / `js` | `escape_js(...)` |
| `json` | `json_encode($v, JSON_HEX_TAG\|JSON_HEX_AMP\|...)` + 컨텍스트 인식 |
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
| `link[:url]` | 옵션이 있으면 `<a href="$url">$v</a>`, 없으면 값 자체를 href와 본문에 모두 사용 |

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
| `@once` ... `@endonce` | 해당 디렉티브를 같은 PHP 요청에서 한 번만 실행 (`$GLOBALS['tplv2_once']` 키) |
| `@fragment('name')` ... `@endfragment` | ob_start + `$this->_fragments[$name] = ob_get_flush()` |
| `@push('name')` ... `@endpush` | 스택에 append |
| `@pushif($cond, 'name')` ... `@endpushif` | 조건부 push |
| `@pushonce('name')` ... `@endpushonce` | 중복 제거 push |
| `@prepend('name')` ... `@endprepend` | 스택 앞에 |
| `@prependif`, `@prependonce` | 위와 동일 (앞) |
| `@isset($v)` ... `@endisset` | `isset` 가드 |
| `@unset($v)` ... `@endunset` | `!isset` 가드 |
| `@empty($v)` ... `@endempty` | `empty` 가드 |
| `@admin` ... `@endadmin` | `$this->user->isAdmin()`이 참인 최고 관리자만 |
| `@auth('type')` ... `@endauth` | `member`/`manager`/`admin` |
| `@guest` ... `@endguest` | 비로그인만 |
| `@can('cap')` / `@cannot` / `@canany(['a','b'])` ... `@end*` | `Rhymix\Modules\Module\Models\Permission`의 `can()` 호출 |
| `@desktop` / `@mobile` ... `@end*` | `UA::isMobile()` 직접 호출 + 태블릿은 `config('mobile.tablets')` 기준. **`Mobile::isFromMobilePhone()`을 거치지 않으므로** 사용자의 `m=0/1` 파라미터/`FullBrowse` 쿠키/`config('mobile.enabled')` 토글이 반영되지 않는다 (`Template::_v2_isMobile` `:957-960`). 사용자 토글까지 따라야 하면 `@if(\Mobile::isFromMobilePhone())` 사용 |
| `@env('APP_ENV')` ... `@endenv` | `!empty($_ENV[$key])`. 값이 `''` 또는 `'0'`이면 거짓 |
| `@error('validator_id')` ... `@enderror` | 인자를 `XE_VALIDATOR_ID`와 비교. 필드별 error bag이 아님 |

#### 단일 디렉티브

`@else`, `@elseif`, `@case`, `@default`, `@continue`, `@break`.

Rhymix v2의 `@break`와 `@continue`는 조건부 인자를 구현하지 않는다. `@break($cond)`처럼 써도 인자를 무시하고 항상 중단하므로 조건이 필요하면 `@if($cond) @break @endif`로 작성한다.

`@unset($v) ... @endunset`도 PHP의 `unset($v)`를 실행하는 문법이 아니다. 이름과 달리 `!isset($v)`인 동안 본문을 보여 주는 조건 블록이다.

#### 종료 디렉티브의 자동 매칭

`@end`만 써도 가장 안쪽 스택의 디렉티브를 종료한다 (`:651-655`). v1과의 호환을 위함. 단 균형이 맞지 않으면 컴파일된 PHP에서 "unexpected end of file" 발생.

권장 — `@endif`/`@endforeach`처럼 명시적 종료. `@end`는 v1에서 옮긴 템플릿에만.

#### 대소문자 변형

`_convertLoopDirectives` (`:625-637`)이 디렉티브 정규식을 빌드할 때 단어 끝 `if`/`once`에 한해 대소문자 양쪽을 허용한다.

- **시작 디렉티브 `@if` / `@once`** — 단어 시작 위치이므로 `(?<=\w)` lookbehind에 걸리지 않아 **소문자만** 인식. `@If`/`@Once`는 매칭되지 않는다.
- **시작 디렉티브 `@pushif` / `@pushonce` / `@pushIf` / `@pushOnce`** — `if`/`once` 직전에 단어 문자가 있으므로 양쪽 인식.
- **종료 디렉티브 `@end<name>`** — 종료 디렉티브 빌드 코드가 첫 글자를 `[xX]` 형식으로 만든다. 따라서 `@endif`/`@endIf`, `@endonce`/`@endOnce`, `@endpush`/`@endPush` 등이 모두 매칭된다.

추천 — 항상 소문자로 통일.

대부분의 v2 디렉티브는 이름과 `(` 사이에 공백을 **0개 또는 1개**만 허용한다. 탭, 여러 칸, 줄바꿈을 Laravel Blade처럼 관대하게 받아준다고 가정하지 말고 `@if($cond)`, `@include('view')`처럼 붙여 쓴다. 또한 종료 이름과 시작 이름의 종류를 엄격히 검증하지 않으므로 `@if ... @endforeach` 같은 불일치는 컴파일된 PHP를 깨뜨린다.

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

v2 파서에서는 `|if=""`, `|when=""`, `|cond=""`가 같고 `|unless=""`는 역조건이다. 이 호환 표기는 큰따옴표 속성에서만 사용한다. **v1 파서가 지원하는 단일 속성 조건은 `|cond=""`뿐**이므로 두 엔진에 공통인 문법으로 착각하지 않는다.

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
| `@include('view', $vars)` | 진입 템플릿에서는 자식에 `$vars`만 노출. 명시 vars가 있는 부모에서는 병합 |
| `@includeIf('view')` | 파일 없으면 무시 |
| `@includeWhen($cond, 'view', $vars?)` | 조건 만족 시만 |
| `@includeUnless($cond, 'view', $vars?)` | 역 |
| `@each('view', $items, 'item', 'empty_view')` | 각 항목마다 include + 비었을 때 |
| `<include src="view" vars="$vars" />` | v2의 XE-style 정적 include. 조건 속성은 아래 주의사항 참고 |

#### 경로와 확장자 규칙

| 부모 및 표기 | 확장자 생략 시 선택 |
|---|---|
| `.blade.php` 부모의 `@include('view')` | `view.blade.php`를 강제 |
| v2로 옵트인한 `.html` 부모의 `@include('view')` | `.html` 우선, 없으면 `.blade.php` |
| v2 XE-style `<include src="view" />` | 부모 파일의 확장자를 그대로 사용 |
| 확장자를 명시한 `@include('view.html')` | 명시한 파일 |

경로는 같은 디렉토리가 기준이며 `'partials/box'`는 서브디렉토리, `'^/common/tpl/header'`는 Rhymix 설치 루트 기준이다. Laravel의 dot notation(`partials.box`)은 지원하지 않으므로 `/`를 사용한다. `.blade.php` 부모에서 레거시 부분 템플릿을 포함하려면 `@include('child.html')`처럼 확장자를 명시해야 한다.

`{{ }}`는 출력 문법이지 디렉티브 인자 안에서 문자열을 보간하는 문법이 아니다.

```blade
{{-- 잘못된 사용: 변환 과정에서 생성된 PHP 안에 echo PHP가 삽입될 수 있다 --}}
@include('partials/{{ $view }}')
@load('css/{{ $theme }}.css')

{{-- 올바른 PHP 표현식 --}}
@include('partials/' . $view)
@load('css/' . $theme . '.css')
@include($view)
```

동적 include 경로에 요청값이나 사용자 입력을 직접 넘기지 않는다. `normalizePath()`와 파일명 문자 정리는 접근 경계가 아니며 선행 `../`를 완전히 차단하지 않는다. 서버에서 정한 allowlist의 키를 실제 파일명으로 매핑한다.

v2의 XE-style `<include src="..." if="$cond">`는 현재 조건의 `$cond`를 `$__Context->cond`로 변환하지 않는 구현상 제약이 있다. 일반 템플릿 변수 조건은 `@includeWhen($cond, 'view')` 또는 `@includeUnless($cond, 'view')`를 사용한다.

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

이는 Laravel Blade와 다르다 — Blade의 `@include('view', $vars)`는 부모 컨텍스트에 추가만 한다. Rhymix는 부모에 명시 vars가 없는 진입 템플릿에서 vars 인자를 주면 자식 `execute()`가 `Context::getAll()` 폴백 대신 명시 vars만 사용한다.

일반 진입 템플릿의 `@each()`는 각 자식에게 항목 변수만 담은 배열을 명시적으로 넘기므로 글로벌 Context 폴백도 차단한다. 부모 Template에 이미 명시 vars가 설정돼 있다면 그 vars와 항목 변수가 병합된다. 자식이 `$lang`, `$module_info` 등 다른 값을 필요로 한다면 `@foreach` + `@include`로 필요한 변수를 함께 전달하거나 자식의 Context 의존성을 없앤다.

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
| `/lang` 또는 `/lang.xml`로 끝나는 경로 | `Context::loadLang(...)` |
| `.js` | JS |
| `.css`, `.scss`, `.less` | CSS (SCSS/LESS는 자동 컴파일) |
| `/css?...` | CSS |
| 두 번째 인자의 `css:<media>` / `js:<position>` | type 강제 (`@load($path, 'css:screen')` 등) |
| 기타 | 경고 + 무시 |

XE-style 속성은 **`target`/`src`/`type`/`media`/`index`/`vars` 6개만** 인식된다 (`_convertResource:558`의 정규식). 도크블록 주석에 보이는 `<load lang="...">`는 실제 정규식 대상에 포함되지 않으므로 동작하지 않는다 — 대신 `<load src="./lang" />`처럼 경로 자동 추론(`/lang` 또는 `/lang.xml`로 끝나는 경로)을 사용한다.

```html
<load src="script.js" type="body" index="10" />
<load src="^/common/js/plugins/ckeditor" />
<load src="./lang" />                <!-- 경로에 /lang 포함 → lang 디렉토리 로드 -->
```

상대 경로 `script.js`는 현재 템플릿 디렉토리 기준. `^/...`는 `RX_BASEURL` 기준.

XE-style `<load src="...">`의 경로 속성은 정적 문자열이며 `{{ }}`나 `$변수`를 평가하지 않는다. 동적 경로는 `@load($asset)`을 사용하되 반드시 allowlist로 제한한다. 외부 URL도 로드할 수 있으므로 요청값을 그대로 넘기면 원격 스크립트 삽입으로 이어질 수 있다. 조건부 로드는 `<load cond="...">`에 의존하지 말고 `@if ... @load(...) @endif`로 감싼다. `@unload()`은 로컬 경로 해제 용도로 사용하며 외부 URL을 올바르게 정규화한다고 가정하지 않는다.

### 상대 경로 자동 변환 (Blade에 없음)

`_convertRelativePaths` (`TemplateParser_v2.php:274-313`)가 다음을 자동으로 절대 경로로 변환.

| 위치 | 변환되는 속성 |
|---|---|
| `<img>`/`<audio>`/`<video>`/`<script>`/`<input>`/`<source>`/`<link>` 태그 | **`src`/`srcset`/`poster` 만** (`<link href="...">`의 `href`는 정규식 대상에서 빠져 있어 변환되지 않음) |
| 모든 태그 인라인 | `style="..."` 내 `url(...)` |
| `<style>` 블록 | 내부 `url(...)` |

변환 제외 — `Template::isRelativePath` (`Template.php:529-532`)가 false인 경로: **첫 토큰이 `http(s)://`/`file:`/`data:`** 이거나, **첫 글자가 `/`(절대 경로)/`{`/`\`/`<`/`$`/`#`/`@`** 이거나, escape sentinel(`&#x1B;`)로 시작.

`^/path`는 isRelativePath() 검사에서 `^`로 시작해 위 제외 목록에 들지 않아 **상대 경로로 분류**된 뒤, `Template::convertPath`가 `^/`를 `RX_BASEURL` prefix로 치환한다.

이 자동 변환 정규식은 **소문자 태그·소문자 속성명·큰따옴표·`src="..."`처럼 공백 없는 등호**를 전제로 한다. `SRC='logo.png'`, `src = "logo.png"` 같은 변형은 보정되지 않을 수 있으므로 템플릿 자원 속성은 정규화된 소문자와 큰따옴표로 작성한다.

```blade
<img src="logo.png" />
{{-- → <img src="/modules/myboard/skins/default/logo.png" /> --}}

<img src="^/files/attach/logo.png" />
{{-- → <img src="/files/attach/logo.png" /> --}}

<img src="/files/attach/logo.png" />
{{-- 첫 글자 / → isRelativePath = false → 그대로 (이미 절대 경로) --}}

<img src="https://example.com/logo.png" />
{{-- 그대로 --}}

<img src="images/{{ $filename }}" />
{{-- 정적 images/가 먼저 템플릿 경로로 변환되고 filename이 런타임 출력됨 --}}

<img src="{{ $image_url }}" />
{{-- 첫 글자가 {이므로 자동 prefix 없음. image_url이 완성 URL이어야 함 --}}

<link rel="stylesheet" href="style.css" />
{{-- href는 변환 대상이 아님. ^/... 명시 또는 @load 사용 권장 --}}
```

즉 `{{ }}`를 HTML 경로 속성에 전혀 쓸 수 없는 것은 아니지만, 값 전체를 표현식으로 만들면 템플릿 디렉토리 기준 자동 보정이 우회된다. 동적 파일명에는 `/`, `..`, URL scheme 등이 들어오지 않도록 allowlist를 적용한다. `srcset`은 쉼표로 단순 분리하므로 쉼표를 포함하는 data URL은 후보 경계로 오인될 수 있다.

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

치환 범위가 PHP 토큰으로 제한되지 않고 남은 템플릿 전체에 적용되므로, 짧고 일반적인 별칭은 HTML 텍스트나 문자열까지 바꿀 수 있다. `MyBoardPostModel`처럼 충돌 가능성이 낮은 고유 별칭을 사용한다.

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

스택 저장소는 Template 인스턴스별이 아니라 정적 속성으로 같은 요청 안에서 공유된다. 다른 모듈·레이아웃과 우연히 합쳐지지 않도록 `myboard.scripts`처럼 패키지 접두사가 있는 이름을 사용한다.

### 기타 디렉티브

| 디렉티브 | 결과 |
|---|---|
| `@csrf` | `<input type="hidden" name="_rx_csrf_token" value="...">` |
| `@json($v)` | 컨텍스트 인식 JSON 출력. JS 컨텍스트면 raw, 그 외에는 HTML escape |
| `@lang('key')` | 다국어. `'this.key'`의 `this`는 템플릿 경로에서 감지한 최상위 패키지 이름으로 치환 (예: `modules/board/...` → `board.key`) |
| `@dump($v, ...)` | `var_dump` 결과 출력 |
| `@dd($v, ...)` | `var_dump` 후 `exit()` |
| `@stack('name')` | `@push` 누적 출력 |
| `@url('', 'mid', $m, 'act', $a)` / `@url(['mid' => $m])` | 인자를 그대로 `getUrl(...)`에 전달. 레거시 key/value 나열과 단일 연관 배열을 모두 지원. HTML 밖에서는 `getNotEncodedUrl()` 후 컨텍스트 escape |
| `@widget('login_info', $args)` | `WidgetController::execute($widget, $args, ...)`에 인자를 그대로 위임. 위젯 이름이 첫 번째 필수 인자 |
| `@php ... @endphp` | PHP 블록 (변수 스코프 자동 변환 적용) |
| `{@ ... }` | 같은 PHP 블록의 단축 형태 |
| `<?php ... ?>` / `<? ... ?>` / `<?= ... ?>` | 동상 |
| `@verbatim ... @endverbatim` | 템플릿 토큰을 문자 그대로 출력. 선행 주석 제거·후행 상대 경로 변환까지 막지는 않음 |
| `@@directive`, `@{{ ... }}` | 이스케이프된 디렉티브 (출력 시 `@` 1개 제거) |

### Laravel Blade와의 차이 (요약)

비교 기준은 [Laravel 13.x 공식 Blade 문서](https://laravel.com/docs/13.x/blade)다. Rhymix가 "Blade 호환"이라고 부르는 범위만 비교하며 Laravel의 전체 기능을 재현한다는 뜻은 아니다.

| 항목 | Laravel Blade | Rhymix v2 |
|---|---|---|
| 변수 스코프 | `$var` 그대로 | **자동으로 `$__Context->var`** (PHP 블록 포함) |
| escaped echo `{{ }}` | `htmlspecialchars` 기반 HTML escape | **컨텍스트 인식**. JS는 `escape_js`, CSS는 HTML escape뿐 |
| 상대 경로 | 없음 | `<img src="x.png">` **자동 절대화** |
| 자원 로드 | 없음 (`<link>` 직접) | `@load` 통합 (CSS/JS/SCSS/플러그인/lang) |
| `@include('view', $vars)` 변수 | 부모 + 추가 | 진입 템플릿에서 명시 vars를 주면 글로벌 Context 폴백 대신 그 vars만 사용 |
| `@extends`/`@yield`/`@section` | 지원 | **미지원** — `@include`/`@fragment`/`@stack` 조합 사용 |
| Blade components·`<x-slot>`·`@props`·`@inject` | 지원 | 대응 기능 **미지원** |
| `@error` | session error bag 사용 | Validator (`XE_VALIDATOR_ID`) 사용 |
| `@can` | Policy/Gate | `Rhymix\Modules\Module\Models\Permission::can()` |
| `@end` 자동 매칭 | 안 됨 | **됨** (v1 호환) |
| XE-style `<!--@if-->` | 안 됨 | **인식** (v1 호환) |
| 단일 `{$var}` | 안 됨 | **HTML 컨텍스트에서만 됨** (v1 호환) |
| 필터 체인 `{$v\|filter}` | 안 됨 | **됨** (여러 내장 필터와 별칭 지원) |

### v1 ↔ v2 매핑

| v1 | v2 |
|---|---|
| `{$x}` | `{{ $x }}` (또는 `{$x}` 그대로 — HTML 컨텍스트만) |
| `{$x\|noescape}` | `{!! $x !!}` (또는 `{$x\|noescape}` 그대로) |
| `<!--@if(...)-->` | `@if(...)` (또는 `<!--@if(...)-->` 그대로) |
| `<!--@foreach(...)-->` | `@foreach(...)` |
| `<include target="..." />` | `@include('...')` (또는 그대로) |
| `cond="..."` 속성 | `\|if="..."` (인라인) 또는 `@if` 블록 |
| `loop="$arr=>$k,$v"` | `@foreach($arr as $k => $v)` |
| `{getUrl(...)}` | `{{ getUrl(...) }}` |
| `<!--%import-->`, `<!--%load_js_plugin-->`, `<block>` | v2에서 **미지원** → `@load`/`@include` 사용 (사용 시 경고) |

### 유의점

1. **PHP 블록 안의 변수도 변환된다.** `@php $count = 0; @endphp`는 `$__Context->count = 0`이 된다. 진짜 로컬은 `\$count`처럼 달러 기호를 escape한다.
2. **`{$var}`는 CSS/JS 컨텍스트에서 동작하지 않는다.** 사용 시 `E_USER_WARNING`이 발생한다. HTML은 `{{ }}`, JS 값은 `@json()`을 우선 사용한다.
3. **출력 표현식은 여러 줄을 지원하지만 v2 서버측 주석은 지원하지 않는다.** `{{ $cond ?\n$a :\n$b }}`는 가능해도 `{{--\n...\n--}}`는 불가능하다.
4. **`@end`와 잘못 짝지은 명시적 종료는 모두 위험하다.** 가능하면 `@endif`/`@endforeach`처럼 시작 구문과 정확히 맞춘다.
5. **`@include`의 vars 인자는 글로벌 Context 폴백을 바꾼다.** 진입 템플릿에서 두 번째 인자를 주면 자식은 그 vars만 받는다. 이미 명시 vars가 있는 부모에서는 부모 vars에 새 값이 병합된다.
6. **`@verbatim`은 템플릿 토큰 충돌 회피용이다.** 서버측 주석이나 완전한 원문 보존, 중첩 블록으로 사용하지 않는다.
7. **`^/...`는 자동 변환 차단 표기가 아니다.** Rhymix 설치 루트 URL로 변환하는 특수 상대 경로다. `/...`·완성 URL·값 전체가 표현식인 경로는 자동 prefix가 붙지 않는다.
8. **v1과 v2 파일은 같은 디렉토리에 둘 수 있지만 선택 규칙을 고려해야 한다.** 같은 basename이면 `.html`이 우선하고, `.blade.php` 부모의 확장자 없는 include는 `.blade.php`를 강제한다. 엔진을 넘나들 때는 확장자를 명시한다.
9. **실제 파일은 파싱 전에 `trim($content) . PHP_EOL`로 읽힌다.** 부분 템플릿의 맨 앞·뒤 공백에 출력 의미를 의존하지 않는다.
10. **동적 URL·include·load 경로는 escape만으로 안전해지지 않는다.** 서버측 allowlist로 선택지를 제한하고 외부 입력을 직접 경로로 사용하지 않는다.

## 템플릿에서 사용 가능한 기본 변수

일반 모듈 View 템플릿은 별도의 `setVars()`가 없을 때 `Context::getAll()`을 사용하므로 다음 값을 흔히 사용할 수 있다. 모든 액션에서 모든 변수가 존재하는 것은 아니므로 선택적 값은 `isset()`/`??`로 방어한다.

| 변수 | 의미 |
|---|---|
| `$lang` | 다국어 객체 (`$lang->key`로 접근) |
| `$logged_info` | 로그인 회원 정보 또는 false |
| `$is_logged` | 로그인 여부 |
| `$module_info` | 현재 모듈 인스턴스 정보 |
| `$grant` | 권한 객체 (모듈 액션 내) |
| `$this->user` | 현재 사용자 (`SessionHelper`) — 그냥 `$user`가 아니라 `$this->user`로 접근 |
| `$this->request` | 현재 요청 객체 |
| `$mid` | 현재 mid |
| `$site_module_info` | 현재 도메인 루트 모듈 |
| `$layout_info` | 현재 레이아웃 (레이아웃 내부) |
| `$content` | 본문 HTML (레이아웃 내부). v2 레이아웃에서 프레임워크가 만든 본문을 넣을 때만 `{!! $content !!}` 사용 |

`Template::setVars()`를 한 번 호출하면 전달 객체가 글로벌 Context와 자동 병합되는 것이 아니라 **그 객체가 전체 `$__Context`가 된다**. 직접 Template 인스턴스를 사용하는 코드에서는 `$lang`, `$logged_info`, `$mid` 등이 필요하면 함께 넘기거나 `setVars()`를 생략한다.

## 스킨 디렉토리 구조

### 모듈 스킨

```
modules/<module>/
├── skins/<skin>/              # PC 스킨
│   ├── skin.xml               # 권장: 메타 + extra_vars + colorset
│   ├── list.html              # v1 진입 템플릿 예시
│   ├── list.blade.php         # v2 대안 (같은 basename의 .html과 둘 중 하나)
│   ├── _header.html 또는 _header.blade.php
│   └── images/, css/, js/
└── m.skins/<mskin>/           # 모바일 스킨
    └── (동일 구조)
```

스킨 정보 파싱: `common/framework/parsers/SkinInfoParser.php`, 호출부: `ModuleModel::loadSkinInfo()`.

`skin.xml`이 없어도 스킨 디렉토리 자체는 폴더명 기준으로 발견되고 실행될 수 있다. 그러나 제목·설명·extra_vars·colorset 등 메타데이터와 관리자 설정 UI를 사용할 수 없으므로 배포 스킨에는 작성하는 것을 권장한다. `ModuleModel::loadSkinInfo()`는 현재 XML을 즉시 파싱하며 이 메서드 자체가 결과 캐시를 저장한다는 전제는 두지 않는다.

`skin.xml` 작성법: [27-extension-points/module-skin.md](27-extension-points/module-skin.md).

### 레이아웃

```
layouts/<name>/                # PC 레이아웃
├── conf/info.xml              # 권장: 메타 + extra_vars + menus
├── layout.html                # v1 진입점 ┐ 둘 중 하나
├── layout.blade.php           # v2 진입점 ┘
├── <name>.layout.css          # 자동 로드되지 않음
├── <name>.layout.js           # 자동 로드되지 않음
└── thumbnail.png

m.layouts/<name>/              # 모바일 레이아웃 (동일 구조)
```

레이아웃 정보 파싱: `common/framework/parsers/LayoutInfoParser.php`.

레이아웃은 읽을 수 있는 `layout.html` 또는 `layout.blade.php`가 있으면 발견되며, `conf/info.xml`이 없으면 최소 기본 정보 객체로 fallback한다. 다만 설정 변수와 메뉴 선언을 제공하려면 `info.xml`이 필요하다. CSS/JS는 관례적인 파일명을 사용해도 자동 로드되지 않으므로 템플릿에서 `<load>`/`@load`로 명시한다. 두 진입 파일을 함께 두면 확장자 생략 탐색에서 `layout.html`이 먼저 선택된다.

레이아웃의 `$content`는 이미 렌더링된 모듈 본문 HTML이다. 프레임워크가 설정한 이 값에 한해서 v1은 `{$content|noescape}`, v2는 `{!! $content !!}`로 출력한다. `{{ $content }}`는 본문 태그를 문자로 escape하며, 임의 사용자 HTML에 raw 출력 구문을 재사용해서는 안 된다.

상세: [27-extension-points/layout.md](27-extension-points/layout.md).

## 스킨 설정값 (`$module_info`)

`skin.xml`의 `<extra_vars>`로 정의하고 관리자가 저장한 값은 일반 프런트 템플릿에서 `$module_info->{var_id}`로 접근한다. `$skin_vars`는 주로 관리자 스킨 설정 화면의 DB 레코드 배열이며 프런트 렌더링에 자동 제공되는 표준 객체가 아니다.

```xml
<extra_vars>
    <var name="show_thumbnail" type="select" default="Y">
        <title xml:lang="ko">썸네일 표시</title>
        <options value="Y"><title xml:lang="ko">사용</title></options>
        <options value="N"><title xml:lang="ko">사용 안 함</title></options>
    </var>
</extra_vars>
```

```html
<!--@if($module_info->show_thumbnail == 'Y')-->
  <img src="..." />
<!--@end-->
```

SkinInfoParser v0.2의 select 옵션은 위처럼 반복되는 `<options value="...">` 형식이다. `<options><option value="..." /></options>`는 현재 스킨 파서 문법이 아니다. 저장값은 기존 `$module_info` 속성을 덮어쓰지 않는 범위에서 병합된다.

`default="Y"`는 파서 메타데이터와 설정 UI 초기값이지, 저장 전의 모든 런타임 요청에 자동 주입된다는 보장이 없다. 필수 동작은 `$module_info->show_thumbnail ?? 'Y'`처럼 템플릿이나 모듈 코드에도 fallback을 둔다.

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

관리자가 저장한 값은 일반 모듈 스킨에서 `$module_info->colorset`으로 접근한다. 독립 `$colorset` 변수는 editor 등 일부 모듈이 별도로 `Context::set()`한 경우에만 존재하므로 일반 스킨에서 기대하지 않는다.

현재 표준 모듈 스킨 설정 화면은 `extra_vars`가 하나 이상 있을 때 그 내부에서 colorset UI도 렌더링한다. colorset만 선언하고 실제 extra_var가 하나도 없으면 파서는 읽어도 관리자가 선택할 UI가 나타나지 않을 수 있다. 자세한 XML·UI 제약은 [27-extension-points/module-skin.md](27-extension-points/module-skin.md)를 따른다.

## 모듈 스킨 경로 선택

`ModuleObject::setLayoutAndTemplatePaths()` 중 스킨 경로를 선택하는 부분 (`ModuleObject.class.php:751-795`):

```
if PC:
    skin = config.skin or 'default'
    if skin == '/USE_DEFAULT/': use ModuleModel::getModuleDefaultSkin(module, 'P')
    template_path = "<module_path>/skins/<skin>/"
    if not exists: template_path = "<module_path>/skins/default/"

elif Mobile:
    mskin = config.mskin or 'default'
    if mskin == '/USE_DEFAULT/': use getModuleDefaultSkin(module, 'M')
    if mskin == '/USE_RESPONSIVE/':
        choose PC skin path (including its default fallback)
    else:
        template_path = "<module_path>/m.skins/<mskin>/"
        if not exists: template_path = "<module_path>/m.skins/default/"
```

## 컴파일 캐시

- 위치: `files/cache/template/<상대경로>.compiled.php` (`../`는 `__parentdir/`로 치환, 해시가 아닌 상대 경로 그대로). (`Template.php:211-212`)
- 무효화 기준: 소스 파일 mtime과 `Template.php` mtime 중 최신값 > 캐시 파일 mtime (`Template.php:355-366`). 소스 변경 시 자동 무효화.
- 인스턴스별 `$template->disableCache()`는 매번 다시 컴파일하게 할 뿐, 캐시 파일 쓰기와 include는 계속 사용한다. `cache.no_template_cache` 같은 전역 설정은 존재하지 않는다.

`Rhymix\Framework\Template::$_delay_compile` (`config('view.delay_compile')`, 초)은 최근 변경된 소스 파일의 재컴파일을 일정 시간 지연시켜 (소스 mtime을 무시하고 `Template.php` mtime만 비교) 캐시 회전을 줄이는 용도다 (`Template.php:96-99, 356-363`). 동시성 잠금과는 무관하다.

신선도 비교가 `cache mtime < latest mtime`이므로 소스와 캐시가 같은 초의 mtime을 갖거나 배포 도구가 과거 mtime을 보존하면 변경이 바로 보이지 않을 수 있다. 이런 경우 `view.delay_compile`을 확인한 뒤 해당 템플릿 캐시를 삭제하거나 소스 mtime을 갱신한다.

## Template 인스턴스 직접 사용

```php
$tpl = new Rhymix\Framework\Template('./modules/foo/tpl', 'index');
$tpl->setVars([
    'title' => '제목',
    'list' => $list,
    'lang' => Context::get('lang'), // 필요한 글로벌 Context 값도 명시적으로 전달
]);
$html = $tpl->compile();
echo $html;
```

`setVars()`는 배열을 내부 객체로 변환하지만 `Context::getAll()`과 자동 병합하지 않는다. 레거시 `TemplateHandler`는 `Rhymix\Framework\Template`을 그대로 상속하는 빈 호환 subclass이므로 `TemplateHandler::getInstance()->compile($path, $file)`도 같은 구현을 사용한다.

## 부분 페이지 렌더링 (Partial Page Rendering)

비관리자 화면에서 레이아웃을 버리고 본문만 렌더링하려면 먼저 `Context::get('isLayoutDrop')`이 참이어야 하며, 동시에 `HTMLDisplayHandler::isPartialPageRendering()`의 정책 검사도 통과해야 한다 (`ModuleHandler.class.php:1185-1197`). 두 조건은 OR가 아니다. 관리자 액션의 layout drop은 `popup_layout`을 선택한다.

`isPartialPageRendering()`은 `config('view.partial_page_rendering')`의 `disabled`/`ajax_only`/`internal_only`/`except_robots` 정책을 검사한다. 기본 `internal_only`에서는 내부 Referer 여부가 기준이며 XHR 자체가 필수는 아니다. 반대로 `ajax_only`일 때만 `X-Requested-With`가 필요하다. 정책 함수가 참인 것만으로 레이아웃이 바뀌지는 않는다.

조건을 모두 만족하면 비관리자 레이아웃을 `common/tpl/default_layout.html`로 바꾸며, 이 템플릿은 v2로 컴파일되어 `{!! $content !!}`만 출력한다.

## 다음 문서

- 새 모듈 스킨 만들기: [27-extension-points/module-skin.md](27-extension-points/module-skin.md)
- 새 레이아웃 만들기: [27-extension-points/layout.md](27-extension-points/layout.md)
- Template 클래스 상세: [10-framework.md](10-framework.md)
