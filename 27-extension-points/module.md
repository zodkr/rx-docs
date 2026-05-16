# 27.1 모듈 (Module)

모듈은 Rhymix의 가장 큰 확장 단위. 게시판/회원/페이지 같은 도메인 단위 미니 앱.

Rhymix는 두 가지 모듈 작성 스타일을 지원한다.

| 스타일 | 위치 | 권장 대상 |
|---|---|---|
| **v2 — Rhymix 전용 (PSR-4 namespace)** | `controllers/`, `models/`, `views/` 하위 namespace 클래스 | **신규 서드파티 모듈은 반드시 v2로 작성한다.** |
| **v1 — XE 호환 (단일 파일)** | `<name>.controller.php` / `.model.php` / `.view.php` 등 | XE/옛 Rhymix 모듈 유지보수, 코어 모듈의 기존 코드. 신규 작성 비권장 |

같은 모듈 안에 두 스타일을 혼용해도 동작하지만(코어 `admin`/`board`가 그렇게 한다), **새로 작성하는 모듈은 v2 단일 스타일로 통일**한다.

문서는 v2 PSR-4 패턴을 중심으로 설명하고, v1 호환 정보는 별도 섹션(§10)에 모았다.

## 1. 디렉토리 구조 (v2 권장)

```
modules/<name>/                          # 또는 plugins/<name>/
│
│  ───── [필수] ─────
├── conf/
│   ├── info.xml                         # 메타 (제목/저자/버전/...)
│   └── module.xml                       # 액션/권한/메뉴/트리거/네임스페이스
│
│  ───── [v2 진입/설치] ─────  ★ <name>.class.php는 v2에서 선택적
├── <name>.class.php                     # (선택) 모듈 진입 클래스 (ModuleObject 상속)
│                                          v2에서는 controllers/Base.php +
│                                          controllers/Install.php로 대체 가능.
│
│  ───── [v2 코드 위치] ─────
├── controllers/                         # Rhymix\Modules\<Name>\Controllers\*
│   ├── Base.php                         # (선택) 공용 init/베이스 클래스
│   ├── Install.php                      # (선택) 설치/업데이트 hook 자동 탐색
│   └── *.php
├── models/                              # Rhymix\Modules\<Name>\Models\*
│   └── *.php
├── views/                               # Rhymix\Modules\<Name>\Views\* (옵션)
│   └── *.php
│
│  ───── [부가 자원] ─────
├── lang/<langtype>.php                  # 다국어 (autoloader가 자동 로드)
├── queries/*.xml                        # 선언적 DB 쿼리
├── schemas/*.xml                        # 테이블 정의 (설치 시 자동 생성)
├── ruleset/*.xml                        # v1 입력 검증 규칙 (v2 모듈에서는 사용 금지)
├── skins/<skin>/                        # PC 스킨 (.blade.php 권장)
├── m.skins/<mskin>/                     # 모바일 스킨 (모바일 페이지가 있을 때만)
├── tpl/                                 # 모듈 자체 템플릿 (관리자 화면 등)
├── scripts/                             # CLI 스크립트 (php index.php <module>.<script>)
```

### v2에서 `<name>.class.php`가 선택적인 이유

기존 XE/v1 관습에서는 `<name>.class.php`에 `ModuleObject` 상속 + 설치 hook(`moduleInstall`/`moduleUpdate` 등)을 모두 두었다. v2에서는 이 두 책임이 분리되어 있다.

- **진입/공용 베이스** → `controllers/Base.php` (또는 `Base.php`)
- **설치/업데이트 hook** → `controllers/Install.php` (또는 `Install.php`)

`ModuleModel::getModuleInstallClass()`(`modules/module/module.model.php:1364-1402`)와 `getModuleDefaultClass()`(`:1316-1354`)가 다음 순서로 자동 탐색한다.

```
Install hook:
1) module.xml <classes><class type="install" name="..." /></classes>로 명시된 클래스
2) Rhymix\Modules\<Module>\Install
3) Rhymix\Modules\<Module>\Controllers\Install
4) v1 fallback: <Module> 클래스 (getModule($name, 'class'))

기본 진입 클래스(액션 디스패치가 명시 클래스를 못 찾았을 때):
1) module.xml <classes><class type="default" name="..." /></classes>
2) Rhymix\Modules\<Module>\Base
3) Rhymix\Modules\<Module>\Controllers\Base
4) v1 fallback: <Module> 클래스
```

코어 `admin` 모듈이 이 패턴 — `admin.class.php`는 `class_alias`만 있고, 실제 설치/업데이트 hook은 `modules/admin/controllers/Install.php`에 있다.

### 사용하지 않는 패턴 (새 모듈에 만들지 말 것)

| 항목 | 코어 사용 | 이유 |
|---|---|---|
| `<name>.wap.php` / `<Module>Wap` | **0개** | XE 시절 WAP 페이지 잔재. 현대 모바일은 `m.skins/`로 충분 |
| `<Module>Item` (`.item.php`) | 코어 도메인 객체(`DocumentItem` 등) | v2에서는 `Models\<Entity>` namespace 클래스로 대체 |
| `script/` (단수형) | install 1개 | install 모듈 전용 — 설치 화면 lang 파일과 정적 컨텐츠 보관. 일반 CLI 스크립트는 `scripts/`(복수) |

## 2. info.xml

`common/framework/parsers/ModuleInfoParser.php`가 파싱한다. **v0.2 권장** (v0.1은 XE 1.x 호환용으로만 유지).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<module version="0.2">
    <title xml:lang="ko">내 모듈</title>
    <title xml:lang="en">My Module</title>
    <description xml:lang="ko">설명…</description>
    <version>1.0.0</version>
    <date>2026-05-16</date>
    <category>service</category>
    <homepage>https://example.com</homepage>
    <license link="https://opensource.org/licenses/GPL-2.0">GPL-2.0</license>
    <author email_address="me@example.com" link="https://example.com">
        <name xml:lang="ko">홍길동</name>
        <name xml:lang="en">John Doe</name>
    </author>
</module>
```

| 필드 | 비고 |
|---|---|
| `version="0.2"` | 스키마 버전. **0.2 권장** |
| `<title xml:lang="..">` | 다국어 제목 (여러 lang 반복 가능; 매칭 없으면 첫 항목) |
| `<description xml:lang="..">` | 다국어 설명 |
| `<version>` | 모듈 자체 버전. 코어 동봉 모듈은 리터럴 `RX_VERSION` |
| `<date>` | 빌드 날짜 (`YYYY-MM-DD`). 코어 동봉 모듈은 리터럴 `RX_CORE`. 이 경우 `info->date = ''`로 파싱됨 |
| `<category>` | `service` / `system` / `extension` (기본 `service`) |
| `<homepage>`, `<license>`, `<author>` | 메타 |
| `<author email_address link>` | 속성으로 이메일/링크. 자식 `<name xml:lang>` |

> **v0.1 (구 XE 형식) 참고만**: `<author date="..." description="..." link="...">` 처럼 author 안에 description/date를 두는 구조. 새 모듈에 쓰지 말 것.

## 3. module.xml

`common/framework/parsers/ModuleActionParser.php`가 파싱한다. 최상위 요소들:

| 요소 | 역할 |
|---|---|
| `<grants>` | 모듈 권한 ID 정의 |
| `<menus>` | 관리자/모듈 메뉴 그룹 |
| `<actions>` | 액션(URL → 처리) 등록 — **핵심** |
| `<permissions>` | 액션별 권한을 액션 정의 밖에서 일괄 지정 |
| `<errorHandlers>` | HTTP 상태 코드별 핸들러 |
| `<eventHandlers>` | 트리거(이벤트) 후킹 |
| `<classes>` | 기본/설치 클래스 명시적 지정 |
| `<namespaces>` | 액션/이벤트 클래스에 적용할 PSR-4 root namespace |
| `<prefixes>` | URL prefix (mid 없이 도달하는 추가 경로) |

```xml
<?xml version="1.0" encoding="utf-8"?>
<module>
    <grants>
        <grant name="access" default="guest">
            <title xml:lang="ko">접근</title>
        </grant>
        <grant name="write" default="member">
            <title xml:lang="ko">쓰기</title>
        </grant>
    </grants>

    <menus>
        <menu name="setup" type="all">
            <title xml:lang="ko">기본 설정</title>
        </menu>
    </menus>

    <actions>
        <action name="dispMyModuleIndex"
                class="Controllers\Index"
                permission="access" index="true" />

        <action name="dispMyModuleWrite"
                class="Controllers\Write"
                permission="write" meta-noindex="true" method="GET,POST" />

        <action name="procMyModuleInsert"
                class="Controllers\Write"
                permission="write" />

        <action name="getMyModuleList"
                class="Controllers\Api\Posts"
                permission="guest" />

        <action name="dispMyModuleAdminSetup"
                class="Controllers\Admin\Setup"
                permission="manager" admin_index="true"
                menu_name="setup" menu_index="true" />
    </actions>

    <eventHandlers>
        <eventHandler after="document.insertDocument"
                      class="Controllers\Hooks"
                      method="onAfterInsertDocument" />
    </eventHandlers>
</module>
```

### 3.1 `<namespaces>` 선언은 보통 필요 없다

코어 `admin`/`board`/`module` 등 v2 모듈도 `<namespaces>` 블록을 **선언하지 않는다**. `class="Controllers\Foo"`만 적으면 ModuleHandler가 자동으로 `Rhymix\Modules\<현재 모듈 이름>\` 접두사를 붙여 풀 클래스명을 만든다 (`ModuleHandler.class.php:435-442`).

```php
// ModuleHandler 내부 동작
if (isset($xml_info->namespaces) && count($xml_info->namespaces)) {
    $class_fullname = array_first($xml_info->namespaces) . '\\' . $class_name;
} else {
    $class_fullname = sprintf('Rhymix\\Modules\\%s\\%s', $this->module, $class_name);
}
```

→ `class="Controllers\Index"`가 있는 `mymodule` 모듈에서는 자동으로 `Rhymix\Modules\Mymodule\Controllers\Index`로 해석된다.

`<namespaces>`는 **외부 vendor namespace로 클래스를 두고 싶을 때만** 선언한다. 파서는 `name` 속성을 읽는다(`ModuleActionParser.php:269-272`):

```xml
<!-- 표준 경로(Rhymix\Modules\…)로 충분하면 이 블록 자체를 생략 -->

<!-- 다른 루트 네임스페이스를 쓰고 싶을 때만 -->
<namespaces>
    <namespace name="Vendor\Acme\MyModule" />
</namespaces>
```

> **잘못된 형식** — 파서가 `name` 속성을 읽으므로 텍스트 컨텐츠는 무시되어 클래스 해석이 깨진다.
>
> ```xml
> <namespace>Rhymix\Modules\MyModule</namespace>   <!-- 동작 안 함 -->
> ```

`<namespaces>`를 선언하면 `<eventHandlers>`의 `class`에도 동일 prefix가 적용된다 — 단, `class`가 v1 호환 분류명(`controller`/`model`/`view`/`mobile`/`api`/`wap`/`class`)이면 prefix가 붙지 않고 v1 fallback으로 해석된다(`ModuleActionParser.php:295-302`).

### 3.2 액션 디스패치 — 매우 중요

ModuleHandler 디스패치 흐름 (`ModuleHandler.class.php:433-453`, `ModuleObject.class.php:874`):

1. `class="Controllers\Index"`가 있으면 위 규칙으로 **`Rhymix\Modules\<Module>\Controllers\Index`** 풀 클래스명 생성.
2. `class_exists($fullname)` 검사 후 `$fullname::getInstance()` 인스턴스 생성.
3. **그 인스턴스의 메서드 중 액션 이름과 동일한 이름의 메서드를 호출**한다 — `$this->{$this->act}()` (`ModuleObject.class.php:874`).

따라서 컨트롤러 클래스의 **메서드명은 액션의 전체 이름과 일치**해야 한다.

```php
class Index extends \ModuleObject
{
    // 이 메서드명이 곧 액션 이름 dispMyModuleIndex와 같아야 한다
    public function dispMyModuleIndex() { ... }
}
```

XML의 `method=` 속성은 **PHP 메서드명이 아니라 허용 HTTP 메서드**(`GET,POST`)다. 잘못 쓰면 405 응답이 난다.

### 3.3 action 속성 일람

| 속성 | 의미 |
|---|---|
| `name` | 액션 이름. **컨트롤러의 메서드명과 동일하게.** `disp*`/`proc*`/`get*` 접두사 컨벤션 |
| `type` | `view`/`controller`/`model`/`mobile`/`api`/`wap`/`class`/`auto`. 미지정 + `class=` 있으면 접두사로 자동(`disp*`→`view`, `proc*`→`controller`, 그 외→`auto`) |
| `class` | PSR-4 클래스 경로. `<namespaces>` 첫 항목 또는 표준 `Rhymix\Modules\<Module>` 기준 상대. 예: `Controllers\Index` |
| `permission` | `guest`/`member`/`not_member`/`manager`/`root`/`manager:scope`/`*-managers` 또는 `<grants>` ID. 콤마로 다중 grant(모두 통과해야 허용) |
| `check_var`(=`check-var`) | permission이 grant ID일 때 권한 확인 대상 module_srl을 읽어올 Context 변수명 |
| `check_type`(=`check-type`) | 권한 확인 대상 모듈 타입(스코프) |
| `grant` | 액션의 grant 이름 (기본 `guest`) — `<grants>`에 정의되지 않은 임의 값 가능 |
| `method` | 허용 HTTP 메서드. `\|` 또는 `,`로 다중 (`GET,POST`/`GET\|POST\|PUT`). **미지정 시 자동 결정** — 아래 표 |
| `ruleset` | `ruleset/*.xml` 파일명(확장자 제외). **v2 모듈에서는 deprecated** — `E_USER_WARNING` 발생 |
| `check-csrf` | `false`면 비-GET 요청에서도 CSRF 검증 면제 (기본 검증함) |
| `meta-noindex` | `true`면 `<meta robots="noindex">` 자동 삽입 |
| `session` | `false`면 세션 비활성. 기본 활성 |
| `cache-control` | `false`/`off`면 Cache-Control 헤더 미적용. 기본 적용 |
| `index="true"` | 모듈의 mid 기본 액션 (`default_index_act`) |
| `admin_index="true"` | 관리자 진입 액션 |
| `setup_index="true"` | 모듈 설정 진입 액션 |
| `simple_setup_index="true"` | 간이 설정 진입 (모달 등) |
| `menu_name`(=`menu-name`) | `<menus>`의 menu name과 연결 |
| `menu_index="true"` | 해당 메뉴의 기본 진입 액션 |
| `route` | 단일 라우트(간단). `\|`로 다중 가능. 복수면 자식 `<route>` 권장 |
| `standalone` | `true`/`false`/`auto`. mid 없이 직접 호출 가능 여부. v2(`class=` 있음) 기본 `auto`, v1 기본 `true` |
| `global_route`(=`global-route`) | `true`면 도메인 전역에서 인식. standalone도 자동으로 `true` |
| `error-handlers` | 이 액션을 핸들러로 등록할 HTTP 상태 코드. 콤마로 다중 (`404,500`). 200 초과만 유효 |

> **속성 이름 정규화**: 파서가 attribute 키에서 영문자만 남기고 소문자화한다 (`BaseParser.php:38-50`). 즉 `menu_name` ↔ `menu-name`, `check_var` ↔ `check-var`처럼 하이픈/언더스코어 표기가 호환된다.

### 3.4 HTTP 메서드 기본값 (`method=` 미지정 시)

ModuleActionParser (`:99-115`)가 다음 우선순위로 결정한다. **`disp*` 액션에 `class=`가 붙으면 기본이 `GET only`** 이므로 그 액션에 POST 폼을 제출하면 405 응답이 난다. POST가 필요하면 `method="GET,POST"`를 명시한다.

| 우선순위 | 조건 | 기본 method |
|---|---|---|
| 1 | `method=` 명시됨 | 명시된 값 (대문자로 정규화, `\|`/`,` 구분) |
| 2 | `type="controller"` 또는 액션명이 `proc*`로 시작 | **POST only** |
| 3 | `class=`가 있고 액션명이 `disp*`로 시작 (v2 패턴) | **GET only** |
| 4 | 그 외 (v1 `disp*`, get*, type=model/api/mobile 등) | `GET, POST` |

v2 컨트롤러에서 자주 발생하는 경우:

```xml
<!-- v2: disp + class → 기본 GET만. POST 폼이 있으면 명시 -->
<action name="dispHelloEdit" class="Controllers\Edit" permission="write" />

<!-- POST 제출도 받는 disp -->
<action name="dispHelloEdit" class="Controllers\Edit" permission="write" method="GET,POST" />

<!-- proc → 기본 POST만. 명시 불필요 -->
<action name="procHelloInsert" class="Controllers\Edit" permission="write" />

<!-- proc인데 GET으로도 호출 가능하게 하려면 -->
<action name="procHelloPing" class="Controllers\Ping" method="GET,POST" />
```

### 3.5 라우팅 (`<route>`)

```xml
<!-- 단일 라우트 -->
<action name="dispMyModulePost" class="Controllers\Post" route="post/$post_srl:int" />

<!-- 다중 라우트 (속성에서 |로) -->
<action name="dispMyModulePost" class="Controllers\Post" route="post/$post_srl:int|p/$post_srl:int" />

<!-- 다중 라우트 (자식 태그 — priority 지정 가능) -->
<action name="dispMyModulePost" class="Controllers\Post">
    <route route="post/$post_srl:int" priority="100" />
    <route route="category/$category:int" priority="40" />
    <route route="page/$page:int" priority="10" />
</action>
```

priority 큰 순서로 매칭. 미지정 시 `0`.

변수 타입(`ModuleActionParser.php:13-22`):

| 타입 | 정규식 |
|---|---|
| `int` | `[0-9]+` |
| `float` | `[0-9]+(?:\.[0-9]+)?` |
| `alpha` | `[a-zA-Z]+` |
| `alnum` | `[a-zA-Z0-9]+` |
| `hex` | `[0-9a-f]+` |
| `word` | `[a-zA-Z0-9_]+` |
| `any` | `[^/]+` |
| `delete` | `[^/]+` (URL 역생성 시 변수 제거 표시) |

타입 생략 시: 이름이 `*_srl`로 끝나면 `int`, 그 외 `any`.

### 3.6 `<grants>`

모듈 권한 ID 정의. `permission="<grant_name>"`에서 참조.

```xml
<grants>
    <grant name="list" default="guest">
        <title xml:lang="ko">목록</title>
    </grant>
    <grant name="write_document" default="member">
        <title xml:lang="ko">글 작성</title>
    </grant>
</grants>
```

`default` 값: `guest`/`member`/`manager`/`root` 또는 그룹 SRL 목록. 모듈 설치 시 초기값.

### 3.7 `<menus>`

관리자 사이드바/그룹 메뉴.

```xml
<menus>
    <menu name="board" type="all">
        <title xml:lang="ko">게시판</title>
        <title xml:lang="en">Board</title>
    </menu>
</menus>
```

`type` 속성은 메뉴 분류(예: `all`, `admin`) — 관리자 화면에서 메뉴 표시 그룹 결정. action에서 `menu_name="board"`로 연결, `menu_index="true"`인 액션이 그 메뉴의 기본 진입.

### 3.8 `<permissions>` (액션 외부 일괄 정의)

action 정의에 `permission=`을 안 쓰고 별도 절로 모을 때.

```xml
<permissions>
    <permission action="procMyModuleAdminUpdate"
                target="manager:config:*"
                check-var="module_srl"
                check-type="board" />
</permissions>
```

- `action`: 대상 액션 이름
- `target`: permission 값 (`permission` 속성과 동일)
- `check-var` / `check-type`: 위 action 속성과 동일 의미

action 정의의 `permission=`보다 **나중에 적용되므로 우선**한다(`ModuleActionParser.php:251-260`).

### 3.9 `<errorHandlers>` & action의 `error-handlers`

HTTP 상태 코드별 에러 처리 액션. **두 가지 방식**이 있고 결과가 다르다.

**방식 A — action 자체를 핸들러로 등록** (`error-handlers="404"` 속성):

```xml
<action name="dispBoardNotFound" type="view" standalone="false" error-handlers="404" />
```

→ `info->error_handlers[404] = 'dispBoardNotFound'` (문자열 = 액션 이름)

라우터가 매칭 실패 시 이 액션으로 폴백한다.

**방식 B — 별도 클래스/메서드를 핸들러로 등록** (`<errorHandlers>` 절):

```xml
<errorHandlers>
    <errorHandler code="405" class="Controllers\Errors" method="dispErrorMethod" />
</errorHandlers>
```

→ `info->error_handlers[405] = ['Controllers\Errors', 'dispErrorMethod']` (배열 = 클래스+메서드)

action의 `error-handlers="404,500"`처럼 콤마로 다중 코드 지정 가능. **200 이하 코드는 무시**된다(`ModuleActionParser.php:243`).

### 3.10 `<eventHandlers>` (트리거 후킹)

| 속성 | 의미 |
|---|---|
| `before="<name>"` / `after="<name>"` | 트리거 이름 (예: `document.insertDocument`) |
| `beforeAction="<act>"` / `afterAction="<act>"` | `act:<module>.<act>` 단축 (대소문자는 정규화로 호환) |
| `class` | PSR-4 클래스(`Controllers\Hooks`) 권장. v1 호환을 위해 분류명(`controller`/`model`/`view`/`mobile`/`api`/`wap`/`class`)도 인식 |
| `method` | 호출할 메서드명 (액션과 달리 자유롭게 지정) |

```xml
<eventHandlers>
    <!-- v2: PSR-4 클래스 -->
    <eventHandler after="document.insertDocument"
                  class="Controllers\Hooks"
                  method="onAfterInsertDocument" />

    <!-- 특정 액션의 전/후 -->
    <eventHandler beforeAction="document.procDocumentVoteUp"
                  class="Controllers\Hooks"
                  method="beforeVoteUp" />

    <!-- v1 분류명 — board.controller.php의 triggerXxx 메서드 -->
    <eventHandler after="member.getMemberMenu"
                  class="controller"
                  method="triggerMemberMenu" />
</eventHandlers>
```

namespace prefix 규칙(`ModuleActionParser.php:295-302`):
- `class`가 분류명(`controller`/`model`/…)이면 v1 fallback (`getModule($module, $type)`로 인스턴스화)
- 그 외에는 `<namespaces>` 첫 항목이 있으면 그 prefix가, 없으면 ModuleHandler가 dispatch 시점에 `Rhymix\Modules\<현재 모듈>\` prefix를 붙임

상세: [13-event-and-trigger-system.md](../13-event-and-trigger-system.md).

### 3.11 `<classes>` (기본/설치 클래스 명시)

자동 탐색을 우회하고 클래스를 명시할 때만 사용.

```xml
<classes>
    <class type="default" name="Custom\DefaultClass" />
    <class type="install" name="Custom\InstallClass" />
</classes>
```

- `type="default"`: 액션 dispatch가 `class=` 없는 액션을 처리할 때 사용할 기본 베이스 클래스. 미지정 시 `Rhymix\Modules\<Module>\Base` → `Rhymix\Modules\<Module>\Controllers\Base` → v1 fallback 순으로 자동 탐색.
- `type="install"`: 모듈 설치/업데이트 hook (`moduleInstall`/`checkUpdate`/`moduleUpdate`/`moduleUninstall`) 위치. 미지정 시 `Rhymix\Modules\<Module>\Install` → `Rhymix\Modules\<Module>\Controllers\Install` → v1 fallback 순.

name은 `<namespaces>` 첫 항목(있으면) 또는 `Rhymix\Modules\<ucfirst(Module)>` 기준 상대.

### 3.12 `<prefixes>` (URL prefix)

mid 없이 도메인 루트에서 직접 도달할 추가 URL prefix.

```xml
<prefixes>
    <prefix name="foobar" />
</prefixes>
```

→ `https://example.com/foobar/...`로 들어오는 요청을 mid 매칭과 동등하게 이 모듈로 라우팅. (Router는 일단 mid를 우선 시도하므로 충돌 시 mid가 이긴다.)

## 4. 권한 체계

`ModuleObject::setPrivileges()` / `checkPermission()`이 처리한다.

| permission 값 | 의미 |
|---|---|
| `guest` (또는 `everyone`) | 누구나 |
| `member` | 로그인 |
| `not_member` (또는 `not-member`) | 비로그인만 (manager는 예외 통과) |
| `manager` | 모듈 매니저 |
| `manager:scope` | scope 매니저 (다중 스코프 모듈) |
| `root` | 슈퍼관리자만 |
| `all-managers` / `same-managers` / `<module>-managers` | 모듈 매니저 일반/같은 모듈/특정 모듈 |
| custom (콤마 다중) | `<grants>`에 정의된 ID. 콤마로 여러 grant 모두 통과해야 함 |

`check_var`/`check_type`이 지정되면 Context에서 모듈 SRL을 읽어 해당 모듈의 권한으로 검사한다(예: 다른 게시판의 관리자 권한 확인). 권한 실패 시 `stop("msg_not_permitted_act")`.

`disp*Admin*` / `proc*Admin*` 등 `Admin`이 포함된 액션은 기본 permission이 `root`로 자동 설정된다.

## 5. 설치/업데이트 hook

v2 권장 — `controllers/Install.php`에 두기 (admin 모듈 패턴):

```php
<?php
namespace Rhymix\Modules\MyModule\Controllers;

class Install extends Base
{
    public function moduleInstall()
    {
        // 설치 시 1회. 테이블은 schemas/*.xml로 자동 생성됨.
        return new \BaseObject;
    }

    public function checkUpdate(): bool
    {
        // 업데이트 필요 여부 판단
        $oDB = \Rhymix\Framework\DB::getInstance();
        return !$oDB->isColumnExists('mymodule_post', 'extra_col');
    }

    public function moduleUpdate()
    {
        // checkUpdate가 true일 때 실행
        return new \BaseObject(0, 'success_updated');
    }

    public function moduleUninstall()
    {
        // 삭제 직전 hook (테이블 자동 drop)
        return new \BaseObject;
    }
}
```

v1 스타일 — `<name>.class.php`에 두기:

```php
<?php
class MyModule extends ModuleObject
{
    public function moduleInstall()  { return new BaseObject; }
    public function checkUpdate()    { return false; }
    public function moduleUpdate()   { return new BaseObject; }
    public function moduleUninstall(){ return new BaseObject; }
}
```

`install` 모듈이 `ModuleModel::getModuleInstallClass()`로 찾아 호출한다(`install.controller.php:582-585`, `install.admin.controller.php:47-50`).

## 6. autoloader 매핑 (v2)

`common/autoload.php:60-70`의 분기 1. **디렉토리/파일명은 소문자화**된다(`strtolower($matches[2])`).

| 클래스명 | 파일 경로 |
|---|---|
| `Rhymix\Modules\MyModule\Controllers\Index` | `modules/mymodule/controllers/Index.php` (없으면 `index.php`) |
| `Rhymix\Modules\MyModule\Controllers\Admin\Setup` | `modules/mymodule/controllers/admin/Setup.php` |
| `Rhymix\Modules\MyModule\Models\Post` | `modules/mymodule/models/Post.php` |
| `Rhymix\Modules\MyModule\Views\Layout` | `modules/mymodule/views/Layout.php` |
| `Rhymix\Modules\MyModule\Install` | `modules/mymodule/Install.php` |

- 모듈 이름은 항상 디렉토리에서 **소문자**(`modules/mymodule/`). 클래스 namespace 마디는 PascalCase가 관용이지만 PHP namespace 자체는 case-insensitive라 `Rhymix\Modules\Mymodule\…` / `Rhymix\Modules\mymodule\…` 모두 동작.
- 클래스 마지막 마디는 그대로(`Index.php`) → 없으면 소문자(`index.php`)로 다시 시도.
- 매칭 시 `modules/<name>/lang/`이 `Context::loadLang()`로 자동 로드.

상세 분기 흐름: [26-namespaces-and-autoload.md](../26-namespaces-and-autoload.md).

## 6.5. namespace 컨트롤러에서 클래스 import 관용 (v2)

`Rhymix\Modules\<Name>\Controllers\…`에 소속된 클래스에서 **다른 namespace의 클래스를 그냥 `Context` / `DocumentModel` / `Cache`로 쓰면 PHP는 현재 namespace 안에서 찾는다** — 즉 `Rhymix\Modules\Admin\Controllers\Context` 같은 존재하지 않는 클래스를 찾다가 fatal. 그래서 v2 컨트롤러는 파일 상단의 `use` 선언으로 가져오는 게 표준 관용이다.

대안은 매번 root namespace 접두 `\Context::get(...)`, `\Rhymix\Framework\Cache::get(...)`를 쓰는 것이지만, 코어 모듈은 `use` 쪽을 일관되게 채택한다(`v1` 단축어를 그대로 쓰면 가독성·grep 친화성도 좋다).

### 6.5.1 v1 글로벌 클래스 (no leading `\`)

`Context`, `ModuleModel`, `DocumentModel`, `FileHandler` 등 **namespace 없이 정의된 레거시 XE 클래스**도 `use ClassName;`으로 가져올 수 있다 (PHP namespace 도입과 함께 지원되어 5.3+에서 동작). `use` 뒤 이름은 항상 절대 경로로 해석되므로 leading `\`를 붙이지 않는다.

`modules/admin/controllers/Dashboard.php:1-13`:

```php
<?php

namespace Rhymix\Modules\Admin\Controllers;

use Context;
use FileHandler;
use AddonAdminModel;
use DocumentAdminModel;
use DocumentModel;
use CommentModel;
use MemberAdminModel;
use MemberController;
use ModuleModel;

class Dashboard extends Base
{
    public function dispAdminIndex()
    {
        $oDocumentModel = getModel('document');
        Context::set('total_document_count', $oDocumentModel->getDocumentCount());
        // …
    }
}
```

→ `use DocumentModel;` 한 줄로 본문에서 `\DocumentModel` 대신 `DocumentModel`만 써도 된다. `getModel('document')`는 `DocumentModel` 인스턴스를 그대로 반환한다 (`DocumentModel`과 `DocumentController`는 모두 같은 `Document` 베이스를 상속하는 형제 클래스이며, 둘 사이의 alias 같은 건 없다).

### 6.5.2 Framework namespace 클래스

`Rhymix\Framework\*`도 동일 패턴.

```php
use Rhymix\Framework\Cache;
use Rhymix\Framework\Config;
use Rhymix\Framework\DB;
use Rhymix\Framework\Lang;
use Rhymix\Framework\Storage;
use Rhymix\Framework\URL;
```

이렇게 import하면 본문에서 `Cache::get(...)`, `Config::set(...)`, `DB::getInstance()`, `Lang::get(...)` 등 짧게 사용 가능.

### 6.5.3 같은 v2 모듈 내부 클래스 + `as` alias

같은 모듈 안의 다른 namespace 클래스는 full namespace로 import. **v1 시대의 `IconModel`/`UtilityModel`처럼 "마지막 segment + `Model`" 형식의 호출 코드와 시각적 일관성을 맞추기 위해** `as`로 alias하는 게 코어 admin 모듈의 관용이다(`Models\Icon` → `IconModel`로 묶어 `IconModel::method()`로 호출).

`modules/admin/controllers/SystemConfig/Domains.php:1-17`:

```php
<?php

namespace Rhymix\Modules\Admin\Controllers\SystemConfig;

use Context;
use ModuleModel;
use Rhymix\Framework\Cache;
use Rhymix\Framework\Config;
use Rhymix\Framework\DateTime;
use Rhymix\Framework\DB;
use Rhymix\Framework\Exception;
use Rhymix\Framework\Lang;
use Rhymix\Framework\Storage;
use Rhymix\Framework\URL;
use Rhymix\Modules\Admin\Controllers\Base;
use Rhymix\Modules\Admin\Models\Icon as IconModel;
use Rhymix\Modules\Admin\Models\Utility as UtilityModel;

class Domains extends Base
{
    // …
}
```

→ `Models\Icon`을 `IconModel`이라는 v1 스타일 이름으로 alias해서 본문에서 `IconModel::method(...)`로 호출. v1 글로벌 클래스(`Context`, `ModuleModel`)와 framework 클래스(`Cache`, `DB`)와 자기 모듈의 namespace 클래스를 한 블록에 섞어 import하는 것이 표준 스타일.

### 6.5.4 예외 클래스

`Rhymix\Framework\Exceptions\*`도 같은 식으로 import해서 `throw new InvalidRequest();` 형태로 짧게 던진다.

`modules/admin/controllers/maintenance/Cleanup.php:1-12`:

```php
<?php

namespace Rhymix\Modules\Admin\Controllers\Maintenance;

use Context;
use ModuleController;
use ModuleModel;
use Rhymix\Framework\Exceptions\InvalidRequest;
use Rhymix\Framework\Exceptions\TargetNotFound;
use Rhymix\Framework\Security;
use Rhymix\Framework\Storage;
use Rhymix\Modules\Admin\Controllers\Base;
```

본문 어디서나 `throw new InvalidRequest();` / `throw new TargetNotFound();`로 사용. (`Rhymix\Framework\Exception` 자체도 다른 곳에서 같은 방식으로 import.)

### 6.5.5 정리

| 대상 | 권장 import | 본문 사용 |
|---|---|---|
| v1 글로벌 클래스 (`Context`, `*Model`, `*Controller`, `FileHandler`, …) | `use ClassName;` (leading `\` 없이) | `Context::get(...)` |
| Framework 클래스 | `use Rhymix\Framework\Cache;` | `Cache::get(...)` |
| Framework 예외 | `use Rhymix\Framework\Exceptions\InvalidRequest;` | `throw new InvalidRequest();` |
| 같은 모듈의 다른 namespace 클래스 | `use Rhymix\Modules\<Name>\Controllers\Base;` | `extends Base` |
| 같은 모듈의 Models — v1 `*Model` 관용에 맞추기 | `use Rhymix\Modules\<Name>\Models\Icon as IconModel;` | `IconModel::method(...)` |

> v1 hook 메서드(`triggerXxx`, `procXxxYyy` 등) 시그니처에서 타입힌트로 글로벌 클래스를 받을 때도 마찬가지. `function foo(Context $c)`가 의도라면 미리 `use Context;` 해두지 않으면 PHP가 `Rhymix\Modules\<Name>\Controllers\Context`를 찾는다.

## 7. 최소 동작 예제 (v2)

가장 작은 hello world. **4개 파일** (`hello.class.php` 없이도 가능).

### `modules/hello/controllers/Install.php`

```php
<?php
namespace Rhymix\Modules\Hello\Controllers;

class Install extends \ModuleObject
{
    public function moduleInstall()  { return new \BaseObject; }
    public function checkUpdate()    { return false; }
    public function moduleUpdate()   { return new \BaseObject; }
    public function moduleUninstall(){ return new \BaseObject; }
}
```

### `modules/hello/controllers/Index.php`

```php
<?php
namespace Rhymix\Modules\Hello\Controllers;

class Index extends \ModuleObject
{
    /**
     * 메서드명 = 액션 이름 (dispHelloIndex)
     */
    public function dispHelloIndex()
    {
        \Context::set(
            'greeting',
            'Hello, ' . ($this->user->isMember() ? $this->user->nick_name : 'guest')
        );
        $this->setTemplateFile('index');
    }
}
```

### `modules/hello/skins/default/index.blade.php`

```blade
<h1>{{ $greeting }}</h1>
```

신규 스킨은 v2 템플릿(`.blade.php`)으로 — [09-templates-and-skins.md](../09-templates-and-skins.md).

### `modules/hello/conf/info.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<module version="0.2">
    <title xml:lang="ko">Hello</title>
    <description xml:lang="ko">최소 예제</description>
    <version>1.0.0</version>
    <date>2026-05-16</date>
    <category>service</category>
    <author email_address="me@example.com">
        <name xml:lang="ko">Me</name>
    </author>
</module>
```

### `modules/hello/conf/module.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<module>
    <grants>
        <grant name="access" default="guest">
            <title xml:lang="ko">접근</title>
        </grant>
    </grants>
    <actions>
        <!-- class="Controllers\Index" → Rhymix\Modules\Hello\Controllers\Index 자동 해석 -->
        <action name="dispHelloIndex"
                class="Controllers\Index"
                permission="access" index="true" />
    </actions>
</module>
```

`<namespaces>` 블록은 표준 경로를 쓸 때 필요 없다.

설치:

1. 위 4개 파일 작성.
2. 관리자 → 모듈 → 새 모듈 자동 인식 → 설치.
3. 페이지(`/admin/menu`)에 mid `hello`로 추가.
4. `/hello`로 접속 → "Hello, ..." 출력.

### 액션이 여러 개일 때

같은 컨트롤러에 메서드를 추가하면 된다 — 액션 이름과 메서드명만 일치하면 자동 라우팅된다.

```xml
<action name="dispHelloIndex"   class="Controllers\Index" permission="access" index="true" />
<action name="dispHelloAbout"   class="Controllers\Index" permission="access" route="about" />
<action name="procHelloContact" class="Controllers\Index" permission="member" />
```

```php
class Index extends \ModuleObject
{
    public function dispHelloIndex() { ... }
    public function dispHelloAbout() { ... }
    public function procHelloContact() { ... }
}
```

### 공용 init이 필요할 때 — Base 클래스 패턴

`modules/admin/controllers/Base.php`처럼 모듈 내부에 Base 클래스를 두고 모든 컨트롤러가 상속한다.

```php
// modules/hello/controllers/Base.php
<?php
namespace Rhymix\Modules\Hello\Controllers;

class Base extends \ModuleObject
{
    public function init()
    {
        // 모든 액션 직전에 setModuleInfo()에서 호출됨 (ModuleObject.class.php:240-251)
        $this->setTemplatePath($this->module_path . 'tpl');
    }
}
```

```php
// modules/hello/controllers/Index.php
<?php
namespace Rhymix\Modules\Hello\Controllers;

class Index extends Base
{
    public function dispHelloIndex() { ... }
}
```

`init`은 `setModuleInfo()` 시점에 자동 실행되며, `Rhymix\Framework\Exception`을 던지면 그 메시지로 `stop()` 처리된다.

## 8. 모듈 인터페이스 사용 (다른 모듈 호출)

### v2 모듈에서 namespace 클래스 직접 사용 (권장)

```php
$post = \Rhymix\Modules\MyModule\Models\Post::getById($srl);
```

### XE 호환 헬퍼 (v1/v2 모두 동작 — `common/legacy.php:66-170`)

| 함수 | 호출 |
|---|---|
| `getModule($name, $type, $kind)` | 임의 타입/kind |
| `getController($name)` | `<Name>Controller` |
| `getAdminController($name)` | `<Name>AdminController` |
| `getView($name)` | `<Name>View` |
| `getAdminView($name)` | `<Name>AdminView` |
| `getModel($name)` | `<Name>Model` |
| `getAdminModel($name)` | `<Name>AdminModel` |
| `getAPI($name)` | `<Name>Api` |
| `getMobile($name)` | `<Name>Mobile` |

모두 `ModuleHandler::getModuleInstance()` 단축 — v1 클래스 규약대로 `<Name><Kind><Type>` 형태로 인스턴스화한다. v2 모듈이라도 v1 분류 클래스를 만들었으면 동일하게 동작.

## 9. 입력 검증

### v2 — 컨트롤러에서 직접 검증

v2(namespace) 모듈에서 `ruleset=` 속성을 쓰면 ModuleHandler가 `trigger_error('Ruleset is deprecated in namespaced modules', E_USER_WARNING)`를 발생시킨다 (`ModuleHandler.class.php:633-637`). v2 컨트롤러는 메서드 안에서 직접 검증한다.

```php
namespace Rhymix\Modules\Hello\Controllers;

use Rhymix\Framework\Exceptions\InvalidRequest;

class Index extends \ModuleObject
{
    public function procHelloInsert()
    {
        $title = trim((string)\Context::get('title'));
        $email = trim((string)\Context::get('email'));

        if (mb_strlen($title) < 2 || mb_strlen($title) > 100) {
            throw new InvalidRequest('msg_invalid_title');
        }
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidRequest('msg_invalid_email');
        }

        // 처리 …
    }
}
```

복잡한 폼은 클라이언트에서 HTML5 validation / 자체 JS로 처리하고 서버에서 위처럼 한 번 더 검증한다.

### v1 — ruleset/*.xml 사용 (레거시)

기존 v1 모듈에서는 ruleset XML로 서버+JS 검증을 자동화한다.

```xml
<!-- modules/hello/ruleset/insert.xml -->
<ruleset version="1.5.0">
    <fields>
        <field name="title" required="true">
            <rule rule="minlength" arg="2" />
            <rule rule="maxlength" arg="100" />
        </field>
        <field name="email" required="true">
            <rule rule="email" />
        </field>
    </fields>
</ruleset>
```

```xml
<!-- module.xml — v1 액션(class= 없음)에서만 사용 -->
<action name="procHelloInsert" type="controller" permission="access" ruleset="insert" />
```

v2 모듈에서는 사용 금지(deprecation warning).

## 10. v1 (XE 호환) 패턴 참고

기존 v1 모듈을 유지보수하거나 옛 XE 모듈을 이해할 때만 참고. **새 모듈에 사용 금지.**

### 디렉토리 구조 (v1)

```
modules/<name>/
├── <name>.class.php                     # ModuleObject 상속 + 설치 hook
├── <name>.controller.php                # procXxx 액션
├── <name>.model.php                     # getXxx 조회
├── <name>.view.php                      # dispXxx 렌더
├── <name>.api.php                       # JSON/XMLRPC API
├── <name>.mobile.php                    # 모바일 전용 분기
├── <name>.admin.controller.php          # 관리자 액션
├── <name>.admin.model.php
├── <name>.admin.view.php
├── conf/{info.xml,module.xml}
├── lang/, queries/, schemas/, ruleset/, skins/, m.skins/, tpl/
```

### autoloader 매핑 (v1 — `common/autoload.php:75-86`)

| 클래스명 | 파일 |
|---|---|
| `MyModule` | `modules/mymodule/mymodule.class.php` |
| `MyModuleController` | `modules/mymodule/mymodule.controller.php` |
| `MyModuleModel` | `modules/mymodule/mymodule.model.php` |
| `MyModuleView` | `modules/mymodule/mymodule.view.php` |
| `MyModuleAdminController` | `modules/mymodule/mymodule.admin.controller.php` |
| `MyModuleMobile` | `modules/mymodule/mymodule.mobile.php` |
| `MyModuleApi` | `modules/mymodule/mymodule.api.php` |

(정규식상 `<Module>Wap`/`<Module>Item`도 인식되지만 실사용 없음 — 새 모듈에 만들지 말 것.)

### module.xml (v1)

```xml
<module>
    <actions>
        <action name="dispMyModuleIndex" type="view"       permission="access" index="true" />
        <action name="procMyModuleInsert" type="controller" permission="write" />
        <action name="getMyModuleList"   type="api"        permission="guest" />
    </actions>
</module>
```

`class=` 속성 없이 액션 이름 + `type`만 지정. ModuleHandler가 `getModuleInstance($module, $type)`으로 `<Module><Type>` 클래스를 찾고 그 인스턴스의 `$this->{$act}()` 메서드를 호출한다.

```php
class MyModuleView extends MyModule
{
    public function dispMyModuleIndex() { ... }
}
```

### eventHandlers (v1)

```xml
<eventHandler after="document.insertDocument" class="controller" method="onAfterInsertDocument" />
```

`class="controller"`처럼 분류명만 적으면 ModuleHandler가 `getModule('mymodule', 'controller')`로 해석한다.

### v1 → v2 마이그레이션 가이드 (선택)

- 새 액션은 namespace 컨트롤러에 작성하고 `module.xml`에 `class="Controllers\…"`로 등록.
- 설치 hook은 점차 `controllers/Install.php`로 이동.
- 기존 v1 액션은 즉시 변환 금지 — 회귀 위험. 사용자/관리자가 변경을 요청할 때만 PR 단위로 마이그레이션.
- 같은 모듈 안에 v1/v2가 공존해도 동작하지만, 시간이 지나면서 v2 쪽으로 옮겨 가는 점진적 접근.

## 다음 문서

- 라우팅: [../07-router.md](../07-router.md)
- 트리거 / eventHandlers: [../13-event-and-trigger-system.md](../13-event-and-trigger-system.md)
- ModuleObject / 권한: [../06-module-handler-lifecycle.md](../06-module-handler-lifecycle.md)
- autoloader 분기: [../26-namespaces-and-autoload.md](../26-namespaces-and-autoload.md)
- DB 쿼리: [../14-database-and-queries.md](../14-database-and-queries.md)
- 템플릿 (스킨은 .blade.php): [../09-templates-and-skins.md](../09-templates-and-skins.md)
- 스킨: [module-skin.md](module-skin.md)
