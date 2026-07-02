# 27.2 애드온 (Addon)

애드온은 **요청 라이프사이클의 4개 hook 위치에서 PHP 코드를 실행**하는 확장 메커니즘. 모듈과 달리 액션을 가지지 않고 모든 페이지에 영향을 준다.

## 디렉토리 구조

```
addons/<name>/                # 코어/사용자 영역
├── <name>.addon.php          # [필수] hook PHP 코드
├── conf/
│   └── info.xml              # [필수] 메타 + extra_vars
├── lang/<langtype>.php       # [권장]
├── <name>.js                 # [선택]
├── <name>.css                # [선택]
└── tpl/                      # [선택]
```

애드온은 코어 동봉이든 사용자 추가든 모두 `addons/<name>/` 아래에만 위치한다. (`plugins/`에 둔 애드온은 인식되지 않는다.)

## info.xml

`common/framework/parsers/AddonInfoParser.php`가 파싱.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<addon version="0.2">
    <title xml:lang="ko">내 애드온</title>
    <title xml:lang="en">My Addon</title>
    <description xml:lang="ko">설명…</description>
    <version>1.0.0</version>
    <date>2026-05-16</date>
    <author email_address="me@example.com">
        <name xml:lang="ko">홍길동</name>
    </author>

    <extra_vars>
        <var name="api_key" type="text">
            <title xml:lang="ko">API 키</title>
            <description xml:lang="ko">외부 API용 키</description>
        </var>
        <var name="enable_logging" type="select" default="N">
            <title xml:lang="ko">로깅 사용</title>
            <options>
                <option value="Y"><title xml:lang="ko">사용</title></option>
                <option value="N"><title xml:lang="ko">사용 안 함</title></option>
            </options>
        </var>
    </extra_vars>
</addon>
```

### extra_vars 타입

| type | 입력 UI |
|---|---|
| `text` | 한 줄 텍스트 |
| `textarea` | 여러 줄 텍스트 |
| `select` | 드롭다운 (options 필요) |

애드온 설정 화면(`setup_addon.html`)은 위 3종만 입력 폼으로 렌더링한다 (`modules/addon/tpl/setup_addon.html:70-74`의 `text`/`textarea`/`select` cond 분기). radio/checkbox/image/filebox/color/date 등 다른 타입은 애드온 설정 UI에서 지원되지 않는다.

## hook 위치

| 위치 | 발생 시점 | 발생 코드 |
|---|---|---|
| `before_module_init` | `ModuleHandler` 생성자 끝 | `ModuleHandler.class.php:112-115` |
| `before_module_proc` | `ModuleObject::proc` 시작 | `ModuleObject.class.php:827-830` |
| `after_module_proc` | `ModuleObject::proc` 끝 | (해당 위치) |
| `before_display_content` | `DisplayHandler::printContent` | `DisplayHandler.class.php:73-76` |

## `<name>.addon.php` 작성

애드온 PHP 파일은 위 hook 위치마다 1회씩 include된다. `$called_position` 변수로 분기:

```php
<?php
/* Copyright (C) Me */

if (!defined('__XE__')) {
    exit();
}

if ($called_position == 'before_module_init') {
    // 모든 페이지 진입 시. 보안 검사/IP 차단/리다이렉트.
    if (preg_match('/badbot/i', $_SERVER['HTTP_USER_AGENT'] ?? '')) {
        header('HTTP/1.0 403 Forbidden');
        exit;
    }
}

if ($called_position == 'before_module_proc') {
    // 모듈 액션 실행 직전. 변수 조작 가능.
    Context::set('extra_data', '...');
}

if ($called_position == 'after_module_proc') {
    // 액션 직후. JS/CSS 로드, 컨텍스트 변수 추가.
    if (Context::getResponseMethod() == 'HTML') {
        Context::loadFile(['./addons/myaddon/myaddon.js', 'body', '', null], true);
    }
}

if ($called_position == 'before_display_content') {
    // HTML 출력 직전. $addon_info로 사용자 설정에 접근, $output을 직접 가공.
    $output = preg_replace('/(\bhttps?:\/\/\S+)/i', '<a href="$1">$1</a>', $output);
}
```

### 사용 가능한 변수 (hook 위치별)

addon 코드는 컴파일된 캐시(`files/cache/addons/<type>.php`) 안에서 `include` 되며, 호출자 함수 스코프를 그대로 상속받는다. include 직전·직후로 어떤 변수가 살아 있는지 정확히 알아두는 것이 안전.

**호출자가 컴파일 캐시 include 직전에 정의 (모든 hook 위치 공통)**

각 hook 위치(ModuleHandler/ModuleObject/DisplayHandler)가 컴파일 캐시 파일을 include하기 직전에 다음 3개를 정의한다:

| 변수 | 의미 |
|---|---|
| `$called_position` | 현재 hook 위치 문자열 (`'before_module_init'` 등). 호출자 코드에서 `$called_position = '...'`로 설정됨 |
| `$oAddonController` | `AddonController::getInstance()` |
| `$addon_file` | 캐시 파일 경로 — 단 컴파일 캐시 내부에서 각 addon 처리 시 `RX_BASEDIR . 'addons/<name>/<name>.addon.php'`로 **덮어쓰여진다** |

**컴파일 캐시가 각 addon include 직전에 정의** (`AddonController::makeCacheFile`, `modules/addon/addon.controller.php:100-128`)

| 변수 | 의미 |
|---|---|
| `$addon_info` | 이 애드온의 사용자 설정 (stdClass — `extra_vars` 값을 `var_export`로 직렬화한 값) |
| `$addon_file` | 이 addon의 `<name>.addon.php` 절대 경로 (호출자가 넘긴 캐시 경로를 덮어씀) |
| `$rm` | run method 문자열 (`run_selected`/`no_run_selected`) |
| `$ml` | mid 목록 (`array_fill_keys`로 만든 lookup 배열) |
| `$_m` | 현재 mid (`Context::get('mid')`) |
| `$run` | 이 addon이 현재 요청에서 실행되어야 하는지 — `if($run && file_exists($addon_file)): include $addon_file;` 조건이므로 addon 코드 진입 시 항상 `true` |
| `$before_time` | `microtime(true)` |

> `$after_time`은 include **이후**에 정의되므로 addon 코드 안에서는 사용할 수 없다.

**`before_module_init`** (`ModuleHandler::__construct` 안, `:112-115`)

호출자가 제공하는 변수:

- `$this` — `ModuleHandler` 인스턴스. `$this->module`/`$this->act`/`$this->mid`/`$this->document_srl`/`$this->module_srl`/`$this->method`/`$this->is_mobile`/`$this->route`/`$this->entry`(있을 때) 모두 raw 요청 값 (아직 init/procModule 실행 전).
- 생성자 인자: `$module`, `$act`, `$mid`, `$document_srl`, `$module_srl` (5개, 기본 빈 문자열).
- 그 이전에 정의된 로컬: `$oContext` (`Context::getInstance()`, 설치된 상태에서만).
- `$oAddonController` (`AddonController::getInstance()`).

**`before_module_proc`** (`ModuleObject::proc` 안, `:827-830`)

호출자가 제공하는 변수:

- `$this` — **현재 모듈의 `ModuleObject` 인스턴스 자체** (예: `BoardView`, `Rhymix\Modules\Hello\Controllers\Index`). `$this->module`/`$this->act`/`$this->module_info`/`$this->grant`/`$this->user`/`$this->request`/`$this->xml_info` 등 모두 사용 가능.
- 로컬: `$is_mobile`, `$triggerOutput` (`moduleObject.proc.before` 결과 — 항상 truthy인 BaseObject), `$oAddonController`.

> 이 시점에는 액션이 **아직 실행 전**이므로 `$output`/`$original_output`/`$triggerAct`는 정의되지 않는다.

**`after_module_proc`** (`ModuleObject::proc` 안, `:919-923`)

호출자가 제공하는 변수:

- `$this` — 동일 (모듈 인스턴스).
- 로컬: `$is_mobile`, `$triggerOutput`, `$triggerAct` (예: `'act:board.dispBoardContent'`), `$output` (액션 반환값, `BaseObject` 또는 `null`), `$original_output` (`$output instanceof BaseObject`면 clone, 아니면 `null`), `$oAddonController`.

**`before_display_content`** (`DisplayHandler::printContent` 안, `:73-76`)

호출자가 제공하는 변수:

- `$this` — `DisplayHandler` 인스턴스.
- `$oModule` — **모듈 인스턴스** (함수 인자, `printContent(&$oModule)` 라인 20). 참조 전달이므로 속성 수정 가능.
- `$output` — **본문 HTML 문자열** (직접 가공 가능). 단, include 후 `:77-80`이 `$output`을 `false`/`null`/`BaseObject`로 바꾼 경우엔 `$original_output`으로 되돌린다 — 가공 결과를 보장하려면 문자열만 대입한다.
- `$original_output` — `$output`의 시작 시점 사본.
- `$handler` — 선택된 `*DisplayHandler` 인스턴스 (예: `HTMLDisplayHandler`).
- `$responseMethod` — `Context::getResponseMethod()` 결과.
- `$oAddonController`.

### `$addon_info` 사용

```php
if ($addon_info->enable_logging == 'Y') {
    error_log("MyAddon: {$_SERVER['REQUEST_URI']}");
}
$api_key = $addon_info->api_key;
```

`extra_vars`로 정의된 변수가 자동 주입된다.

## 컴파일 캐시

활성 애드온 전체는 하나의 PHP 파일로 컴파일된다.

- 위치: `files/cache/addons/pc.php`, `files/cache/addons/mobile.php`.
- 생성: `AddonController::makeCacheFile($site_srl, $type, $gtype)` (`modules/addon/addon.controller.php:72`).
- PC/모바일 분리. 다국어는 컴파일 시점이 아니라 런타임에 처리됨.
- 진입은 `AddonController::getCacheFilePath($type)`로 조회.

무효화 조건:

- 애드온 활성/비활성 토글 또는 설정 저장 시 (관리자 컨트롤러가 `makeCacheFile` 호출 — `procAddonAdminToggleActivate`/`procAddonAdminSaveActivate`/`procAddonAdminSetupAddon`).
- 캐시 파일이 없거나 `addon.controller.php`(코어 파일)의 mtime이 캐시보다 새로울 때 (`getCacheFilePath`가 자동 재컴파일 — `modules/addon/addon.controller.php:42`).

> 캐시 파일은 애드온 코드를 인라인하지 않는다. 대신 `$addon_file = RX_BASEDIR . 'addons/<name>/<name>.addon.php';` 경로를 기록한 뒤 실행 시 `include($addon_file)`로 불러온다 (`modules/addon/addon.controller.php:111,132`). 따라서 개별 애드온 파일(`<name>.addon.php`)의 **코드를 수정하면 캐시를 재생성하지 않아도 다음 요청에서 곧바로 반영**된다. 캐시 재생성이 필요한 경우는 활성 애드온 목록·설정(extra_vars)·실행 mid 조건·활성/비활성 상태가 바뀔 때뿐이며, 이때는 위의 무효화 조건(관리자 토글/설정 저장, 또는 `addon.controller.php` mtime 갱신)을 거친다.

## 활성화 단위

### 1) 사이트 전체

`modules/addon/`(addon 관리 모듈)의 관리자 UI에서 활성/비활성.

### 2) 모듈별

각 모듈 설정에서 사이트 기본을 override 가능.

### 3) PC/모바일 별도

같은 애드온을 PC만/모바일만/둘 다 활성화 옵션.

## 실예시 (addons/autolink/)

`addons/autolink/autolink.addon.php`:

```php
<?php
if (!defined('__XE__')) exit();

if ($called_position == 'after_module_proc' && Context::getResponseMethod() == 'HTML') {
    Context::loadFile(['./addons/autolink/autolink.js', 'body', '', null], true);
}
```

→ HTML 응답일 때만 autolink JS를 로드해 클라이언트가 URL 문자열을 자동 링크로 변환.

## 최소 동작 예시

### `addons/myaddon/myaddon.addon.php`

```php
<?php
if (!defined('__XE__')) exit();

if ($called_position == 'before_display_content' && Context::getResponseMethod() == 'HTML') {
    $output = '<!-- MyAddon active -->' . $output;
}
```

### `addons/myaddon/conf/info.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<addon version="0.2">
    <title xml:lang="ko">My Addon</title>
    <description xml:lang="ko">최소 예제</description>
    <version>1.0.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
</addon>
```

설치:
1. 파일 작성.
2. 관리자 → 애드온 → 새 애드온 인식 → 활성화.

## 주의사항

- **모든 요청에서 실행되므로 매우 가볍게 작성**.
- 무거운 작업은 큐로 분리.
- 다른 애드온과의 순서가 중요하면 우선순위 설정.
- `$output`을 직접 가공할 때는 정규식 대신 DOM 파싱 권장 (큰 페이지 오버헤드 주의).
- HTML 응답이 아닌 경우(JSON/RAW 등) `before_display_content`에서 분기 필수.

## 디버깅

`config('debug.enabled')` + `display_content`에 `slow_*` 포함 시 느린 애드온도 캐치 가능.

직접 디버그:

```php
if ($called_position == 'after_module_proc') {
    Rhymix\Framework\Debug::addEntry("MyAddon: " . microtime(true));
}
```

## 다음 문서

- 트리거 시스템 (비교): [../13-event-and-trigger-system.md](../13-event-and-trigger-system.md)
- 코어 애드온 카탈로그: [../29-addons/](../29-addons/)
