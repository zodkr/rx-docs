# 26. Namespaces와 autoloader

`common/autoload.php`의 4단계 분기를 코드와 함께 해부.

## 등록 코드

```php
spl_autoload_register(function($class_name) {
    $class_name = str_replace('\\', '/', $class_name);

    // 분기 1: Rhymix\(Framework|Addons|Modules|Plugins|Themes|Widgets)\...
    if (preg_match('!^Rhymix/(Framework|Addons|Modules|Plugins|Themes|Widgets)/((\w+)/(?:\w+/)*)?(\w+)$!', $class_name, $matches)) {
        $dir = RX_BASEDIR . ($matches[1] === 'Framework' ? 'common/framework' : strtolower($matches[1])) . '/' . strtolower($matches[2]);
        $filename1 = $dir . $matches[4] . '.php';
        $filename2 = $dir . strtolower($matches[4]) . '.php';
        if ($matches[1] !== 'Framework' && !empty($matches[3])) {
            $lang_plugin = strtolower($matches[3]);
            $lang_path = RX_BASEDIR . strtolower($matches[1]) . '/' . $lang_plugin . '/lang';
        }
    }
    // 분기 2: 명시적 매핑
    elseif (isset($GLOBALS['RX_AUTOLOAD_FILE_MAP'][$lc_class_name = strtolower($class_name)])) {
        $filename1 = RX_BASEDIR . $GLOBALS['RX_AUTOLOAD_FILE_MAP'][$lc_class_name];
    }
    // 분기 3: 레거시 모듈 클래스명 매핑
    elseif (preg_match('/^([a-zA-Z0-9_]+?)(Admin)?(View|Controller|Model|Item|Api|Wap|Mobile)?$/', $class_name, $matches)) {
        $module = strtolower($matches[1]);
        $filename1 = RX_BASEDIR . 'modules/' . $module . '/' . $module .
            (!empty($matches[2]) ? '.admin' : '') .
            (!empty($matches[3]) ? ('.' . strtolower($matches[3])) : '.class') . '.php';
        if ($module !== 'module') {
            $lang_plugin = $module;
            $lang_path = RX_BASEDIR . 'modules/' . $module . '/lang';
        }
    }
    // 분기 4: RX_NAMESPACES로 등록된 외부 plugin namespace
    elseif (isset($GLOBALS['RX_NAMESPACES']) && preg_match($GLOBALS['RX_NAMESPACES']['regexp'], $class_name, $matches)) {
        $plugin_path = $GLOBALS['RX_NAMESPACES']['mapping'][strtr($matches[1], '/', '\\')] ?? '';
        if ($plugin_path) {
            $dir = RX_BASEDIR . $plugin_path . '/' . strtolower($matches[2]);
            $filename1 = $dir . $matches[3] . '.php';
            $filename2 = $dir . strtolower($matches[3]) . '.php';
            $lang_plugin = array_last(explode('/', $plugin_path));
            $lang_path = RX_BASEDIR . $plugin_path . '/lang';
        }
    }

    if ($filename1 && file_exists($filename1)) include $filename1;
    elseif ($filename2 && file_exists($filename2)) include $filename2;

    if ($lang_plugin) Context::loadLang($lang_path, $lang_plugin);
});
```

## 분기 1: Rhymix 네임스페이스

| 1번째 segment | 디렉토리 |
|---|---|
| `Framework` | `common/framework/` |
| `Addons` | `addons/` |
| `Modules` | `modules/` |
| `Plugins` | `plugins/` |
| `Themes` | `themes/` |
| `Widgets` | `widgets/` |

### 매핑 예

| 클래스명 | 시도 경로 |
|---|---|
| `Rhymix\Framework\Cache` | `common/framework/Cache.php` |
| `Rhymix\Framework\Helpers\SessionHelper` | `common/framework/helpers/SessionHelper.php` |
| `Rhymix\Modules\Admin\Controllers\Dashboard` | `modules/admin/controllers/Dashboard.php` |
| `Rhymix\Modules\Board\Models\Document` | `modules/board/models/Document.php` |
| `Rhymix\Plugins\MyPlugin\Foo` | `plugins/myplugin/Foo.php` (또는 `foo.php`) |
| `Rhymix\Widgets\Mywidget\Helper` | `widgets/mywidget/Helper.php` |

### lang 자동 로딩

`Framework`를 제외한 분기 1에서는 3번째 segment(플러그인명)에 해당하는 `lang/` 디렉토리가 자동으로 `Context::loadLang`된다.

예: `Rhymix\Modules\Board\Controllers\Foo` 클래스 사용 시 `modules/board/lang/` 자동 로드.

### 두 가지 파일명 시도

- `filename1` — 클래스명 그대로 (`Cache.php`).
- `filename2` — 소문자 (`cache.php`).

대소문자 구분 파일시스템에서 둘 다 시도하기 위함.

## 분기 2: `RX_AUTOLOAD_FILE_MAP`

`common/legacy.php:12-56`에 정의. 레거시 클래스명 → 경로 직접 매핑.

```php
$GLOBALS['RX_AUTOLOAD_FILE_MAP'] = [
    'context'            => 'classes/context/Context.class.php',
    'modulehandler'      => 'classes/module/ModuleHandler.class.php',
    'moduleobject'       => 'classes/module/ModuleObject.class.php',
    'db'                 => 'classes/db/DB.class.php',
    'displayhandler'     => 'classes/display/DisplayHandler.class.php',
    'htmldisplayhandler' => 'classes/display/HTMLDisplayHandler.php',
    // ...
    'ftp'                => 'common/libraries/ftp.php',
    'tar'                => 'common/libraries/tar.php',
];
```

- 키는 소문자 비교.
- 총 43개 항목. 이 중 `ftp` → `common/libraries/ftp.php`, `tar` → `common/libraries/tar.php`는 해당 파일이 제거되어 현재 존재하지 않는 dangling 항목이다 (`common/legacy.php:52-53`).
- XE 호환을 위해 유지.
- 일부 별칭이 같은 파일을 가리킨다 (예: `xexmlparser` → `classes/xml/XmlParser.class.php` — XmlParser의 별칭).

## 분기 3: 레거시 모듈 클래스명

가장 많이 쓰이는 분기. 정규식:

```
^([a-zA-Z0-9_]+?)(Admin)?(View|Controller|Model|Item|Api|Wap|Mobile)?$
```

| 클래스명 | 파일 경로 |
|---|---|
| `Board` | `modules/board/board.class.php` |
| `BoardController` | `modules/board/board.controller.php` |
| `BoardModel` | `modules/board/board.model.php` |
| `BoardView` | `modules/board/board.view.php` |
| `BoardAdminController` | `modules/board/board.admin.controller.php` |
| `BoardAdminModel` | `modules/board/board.admin.model.php` |
| `BoardAdminView` | `modules/board/board.admin.view.php` |
| `BoardMobile` | `modules/board/board.mobile.php` |
| `BoardApi` | `modules/board/board.api.php` |
| `BoardWap` | `modules/board/board.wap.php` |
| `BoardItem` | `modules/board/board.item.php` |
| `Foo` | `modules/foo/foo.class.php` |

### lang 자동 로드

모듈명이 `module`이 아니면 `modules/<name>/lang/` 자동 로드. (`module` 모듈은 자기 자신을 lang에 의존 — 무한 루프 방지.)

### 주의

이 패턴은 namespace 구분자(`\`)가 없는 영문·숫자·underscore 레거시 클래스명 대부분에 매칭된다. 즉 그 형식의 정의되지 않은 클래스도 결과적으로 경로를 만들어보고 `file_exists` 체크에서 걸러진다.

→ 이 형식의 정의되지 않은 클래스에 `class_exists`를 호출하면 모듈 경로를 한 번 stat한다. 비용은 적지만 인지 필요.

## 분기 4: `RX_NAMESPACES` (사용자 정의 vendor namespace)

`files/config/config.php`의 `namespaces`에는 `mapping`뿐 아니라 이를 바탕으로 미리 생성된 `regexp`도 함께 저장된다. `Config::init()`은 `regexp`가 비어 있지 않을 때만 이 배열을 `$GLOBALS['RX_NAMESPACES']`로 내보낸다 (`common/framework/Config.php:45-48`).

```php
'namespaces' => [
    'mapping' => [
        'Vendor\\MyPlugin' => 'plugins/myplugin',
        'Acme\\Tools'      => 'plugins/acme-tools',
    ],
    'regexp' => '!^(Vendor/MyPlugin|Acme/Tools)/((?:\\w+/)*)(\\w+)$!',
]
```

모듈 등록 시 `ModuleController::registerNamespaces()`가 namespace 이름을 길이 내림차순으로 정렬해 위 정규식을 생성하고 설정에 함께 저장한다 (`modules/module/module.controller.php:1553-1571`). 런타임에는 저장된 값을 그대로 사용한다.

```php
// 구분자는 `!`, 이름은 길이 내림차순 정렬 (modules/module/module.controller.php:1563)
$GLOBALS['RX_NAMESPACES']['regexp'] = '!^(Vendor/MyPlugin|Acme/Tools)/((?:\w+/)*)(\w+)$!';
$GLOBALS['RX_NAMESPACES']['mapping'] = [
    'Vendor\\MyPlugin' => 'plugins/myplugin',
    'Acme\\Tools'      => 'plugins/acme-tools',
];
```

매칭 시:

- `Vendor\MyPlugin\Controllers\Foo` → `plugins/myplugin/controllers/Foo.php`.
- 두 가지 케이스 시도 (`Foo.php` / `foo.php`).
- `plugins/myplugin/lang/` 자동 로드.

### 등록 방법

모듈에서 사용자 정의 vendor namespace를 쓰는 지원 경로는 `modules/<module>/conf/module.xml`에 선언하는 것이다.

```xml
<namespaces>
    <namespace name="Vendor\MyPlugin" />
</namespaces>
```

모듈 설치·업데이트 흐름이 `ModuleController::registerNamespaces($module_name)`를 호출하여 `Vendor\MyPlugin` → `modules/<module>` mapping과 일치하는 regexp를 함께 저장한다 (`modules/install/install.admin.controller.php:58-70`, `modules/module/module.controller.php:1521-1571`). namespace만 따로 입력하는 관리자 UI는 없다.

`config/config.user.inc.php`에서 `namespaces.mapping`만 설정하는 방식은 동작하지 않는다. 이 파일은 `Config::init()`이 `$GLOBALS['RX_NAMESPACES']`를 만든 **뒤에** 로드되고(`common/autoload.php:136-144`), regexp도 생성하지 않기 때문이다. 코어의 모듈 설치·업데이트 등록 절차를 사용하는 것이 안전하다.

모듈 밖의 임의 경로를 vendor namespace에 직접 연결해야 한다면 부트스트랩 전에 읽히는 `files/config/config.php`의 `namespaces`에 **mapping과 일치하는 regexp를 모두** 넣어야 한다. 다만 `Rhymix\Plugins\...`처럼 분기 1이 이미 지원하는 namespace를 쓰는 편이 간단하며 별도 등록도 필요 없다.

## Composer autoloader

`common/vendor/autoload.php`도 spl_autoload_register로 등록된다 (`common/autoload.php:120`). 분기 우선순위:

1. Rhymix 커스텀 autoloader (위 4단계).
2. Composer autoloader.

대부분의 Rhymix 클래스명은 분기 1~3에 의해 처리되므로 Composer까지 거의 가지 않는다. 외부 라이브러리(`GuzzleHttp\Client` 등)는 Composer가 처리.

## 모듈에서 namespace 사용 모범 사례

`modules/admin/`이 좋은 예시.

```
modules/admin/
├── admin.class.php                 ← 기반 클래스 (Admin = Rhymix\Modules\Admin\Controllers\Base 별칭)
├── admin.admin.controller.php      ← 레거시 진입점 (class AdminAdminController, @deprecated 얇은 wrapper)
├── admin.admin.model.php
├── admin.admin.view.php
├── controllers/
│   ├── Dashboard.php               ← Rhymix\Modules\Admin\Controllers\Dashboard
│   └── systemconfig/               ← namespace 세그먼트는 SystemConfig (autoloader가 소문자 매핑)
│       └── Domains.php             ← Rhymix\Modules\Admin\Controllers\SystemConfig\Domains
├── models/
│   └── Favorite.php                ← Rhymix\Modules\Admin\Models\Favorite
└── conf/module.xml
```

`module.xml`에서 namespace 클래스로 액션 등록:

```xml
<action name="dispAdminIndex" class="Controllers\Dashboard" index="true" />
```

→ `ModuleHandler`가 `Rhymix\Modules\Admin\Controllers\Dashboard` 풀 클래스명으로 해석하고 그 인스턴스의 **`dispAdminIndex()` 메서드**(액션 이름과 동일)를 호출한다. XML의 `method=` 속성은 PHP 메서드명이 아니라 허용 HTTP 메서드(`GET`/`POST` 등)다.

## 신구 혼합 패턴

`admin.admin.controller.php`(레거시, `class AdminAdminController`)에 `procAdmin*` wrapper 메서드 그대로 두고, 새 액션은 `controllers/Xyz.php`에 namespace로 작성 — 점진적 전환.

## 안전성

- autoloader는 `file_exists` 체크 후에만 include — 존재하지 않는 클래스 호출은 silent fail.
- 분기 3은 모든 임의 클래스명을 매칭하므로 `class_exists($random)` 호출은 항상 한 번 디스크 stat을 유발.

## 디버깅 팁

autoloader가 어떤 경로를 시도하는지 확인하려면 자체 spl_autoload_register를 일시적으로 추가:

```php
spl_autoload_register(function($cn) {
    error_log("Looking for: {$cn}");
}, true, true);
```

## 다음 문서

- 새 모듈 만들기: [27-extension-points/module.md](27-extension-points/module.md)
- 헬퍼/글로벌: [12-helpers-and-globals.md](12-helpers-and-globals.md)
- 설정 시스템: [25-config-system.md](25-config-system.md)
