# 06. ModuleHandler / ModuleObject 라이프사이클

`classes/module/ModuleHandler.class.php`와 `classes/module/ModuleObject.class.php`는 Rhymix의 핵심 디스패처다.

- `ModuleHandler` — 요청을 받아 모듈 인스턴스를 생성하고 액션을 실행한 뒤 결과를 출력한다.
- `ModuleObject` — 모든 모듈 클래스의 부모. 액션 메서드 호출, 권한 검사, 스킨/레이아웃 적용을 담당한다.

## ModuleHandler 핵심 속성

`ModuleHandler.class.php:10-22`.

| 속성 | 의미 |
|---|---|
| `method` | HTTP 메서드 (GET/POST/...) |
| `module_info` | 현재 처리할 모듈 정보 (DB에서 로드) |
| `module_srl` | 모듈 인스턴스 srl |
| `module` | 모듈 이름 (예: `board`) |
| `act` | 액션 이름 (예: `dispBoardContent`) |
| `mid` | 모듈 인스턴스 mid |
| `document_srl` | 문서 srl |
| `entry` | 문서 alias |
| `route` | `Rhymix\Framework\Request` 인스턴스 |
| `is_mobile` | 모바일 여부 |
| `httpStatusCode` | 현재 HTTP 상태 (기본 200) |
| `error` / `error_detail` | 에러 코드/세부 |

## 타입/카인드 매트릭스

`ModuleHandler.class.php:27-39`:

```php
protected static $_types = [
    'model'      => 'Model',
    'view'       => 'View',
    'controller' => 'Controller',
    'mobile'     => 'Mobile',
    'api'        => 'Api',
    'wap'        => 'Wap',
    'class'      => '',
];
protected static $_kinds = [
    'admin' => 'Admin',
    'svc'   => '',
];
```

→ 클래스명 합성 규칙: `<module><Kind><Type>`. 예: `module='board'`, `type='controller'`, `kind='admin'` → `BoardAdminController`.

`getModuleInstance($module, $type, $kind)` (`:1265`)가 이를 사용한다.

## CSRF 면제 메서드

`ModuleHandler.class.php:44-46`:

```php
protected static $_nocsrf_methods = ['GET', 'HEAD', 'OPTIONS'];
```

이 메서드는 CSRF 토큰 검증을 건너뛴다. POST 등은 토큰을 요구한다(`module.xml`의 `check-csrf="false"`로 액션별 해제 가능).

## 생성자 (`:58`)

`new ModuleHandler($module, $act, $mid, $document_srl, $module_srl)` 형태. 모든 인자는 옵셔널 — 빈 인자는 Context에서 추출.

순서:

1. 미설치 시 `$this->module = 'install'`로 고정 후 즉시 return.
2. `Context::security_check` 검사 — 보안 위반 발견 시 `msg_security_violation` 에러.
3. 요청 변수 추출 — `Context::get`으로 module/act/mid/document_srl/module_srl/route 채움.
4. `Mobile::isFromMobilePhone()` 결과 캐싱.
5. `entry` alias 사니타이즈.
6. `mid='admin'`이면 module을 'admin'으로 변환.
7. **트리거** — `moduleHandler.init.before`.
8. **애드온 hook** — `before_module_init` 위치의 컴파일된 PHP 파일을 include.

## init() (`:122`)

반환값:
- `true` — 정상 진행 (`procModule` + `displayContent` 호출).
- `false` — 리다이렉트 등으로 진행 중단.

처리 단계 (요약, 상세는 [04-bootstrap-and-request-lifecycle.md](04-bootstrap-and-request-lifecycle.md)):

1. 미등록 도메인 액션 — `redirect_301`/`redirect_302`/`block`/`display`.
2. 라우터 에러 → 404.
3. entry → document_srl 변환.
4. document_srl → module_info 역추적.
5. mid → module_info 매핑.
6. 도메인 일치 검사.
7. 기본 모듈/인덱스 문서 적용.
8. PC/Mobile 레이아웃 srl 결정 (`-1`: 사이트 기본, `-2`: PC와 공유).
9. `module_info->site_srl` 오버라이드(레거시).
10. **트리거** — `moduleHandler.init.after`.

> `success_return_url`/`error_return_url` 내부 URL 검증은 더 이상 init()에 없다. 요청 변수 사니타이즈 단계(`Context.class.php:1533-1541`)로 옮겨져 **비(非)GET 요청에 한해** `URL::isInternalURL()` 실패 시 `security_check = 'DENY ALL'`로 처리된다. GET 요청은 앞선 분기(`Context.class.php:1525`)에서 escape만 되고 이 검증을 거치지 않는다 (`19-security.md` Open Redirect 참고).

## procModule() (`:320`)

1. 모바일 재감지 (`:323`).
2. 에러 있으면 message 모듈로 변환해 반환 (`:326-329`).
3. `ModuleModel::getModuleActionXml($this->module)` — module.xml 캐시된 결과 (`:332`).
4. install 모듈일 때 `default_index_act` 폴백 (`:335-341`).
5. act가 비어 있으면 `default_index_act` 폴백, 여전히 없으면 404 (`:344-353`).
6. type/class_name/ruleset/meta_noindex 결정 — admin이 포함된 액션은 `kind='admin'` (`:356-370`).
7. **HTTP 메서드 검사** — 허용 method에 없으면 405 (`:372-380`).
8. **CSRF 검사** — 비-GET/HEAD/OPTIONS + `check_csrf !== 'false'` + 설치됨이면 `Security::checkCSRF()`. 실패 시 403 (`:382-389`).
9. **standalone 검사** — `standalone='auto'`인데 module/mid 둘 다 비었거나, `standalone='false'`인데 mid 없으면 403 (`:391-402`).
10. `use_mobile='N'`이면 `Mobile::setMobile(false)` (`:404-412`).
11. 로그인 회원 메뉴 lang 재할당 (`:414-419`).
12. **모듈 인스턴스 생성** (`:421-463`):
    - `class_name` 있으면 `<namespaces>` 첫 항목 또는 표준 `Rhymix\Modules\<Module>` prefix로 풀네임 만들어 `class_exists` 후 `getInstance()` (v2).
    - 그 외엔 `getModuleInstance($module, $type, $kind)` (v1). 못 찾으면 `ModuleModel::getModuleDefaultClass()` fallback.
13. 액션 메서드 미존재 시 forward 탐색 — 액션명에서 모듈명 역추론, 그 다음 `getActionForward($act)`로 DB 등록 forward 확인. 매칭되면 그 모듈의 인스턴스로 다시 생성 (`:471-617`).
14. **ruleset 검증** — `ruleset=` 있으면 `Validator` 실행. v2(namespaced) 모듈에서는 `E_USER_WARNING`(`Ruleset is deprecated`) (`:619-665`).
15. `setAct($act)` + `setModuleInfo($module_info, $xml_info)` — 후자가 권한 검사/admin 레이아웃/init() 호출 (`:667-670`).
16. view/mobile + 비-admin이면 도메인 헤더/푸터/타이틀 주입, admin이면 `robots=noindex` 메타 추가 (`:672-695`).
17. **`$oModule->proc()` 실행** (`:700`).
18. HTML(비-XMLRPC/JSON/JS_CALLBACK) 응답이면 error/message/redirect를 세션 INPUT_ERROR로 저장 (`:702-740`).
19. JSON/XMLRPC 응답일 때 같은 모듈의 API 인스턴스 추가 실행 + 결과 병합은 `ModuleObject::proc()` 내부에서 처리(아래 §ModuleObject `proc()`).

## displayContent() (`:993`)

상세는 [04-bootstrap-and-request-lifecycle.md](04-bootstrap-and-request-lifecycle.md). 요약:

1. **트리거** — `moduleHandler.proc.after`.
2. 리다이렉트 처리(`getRedirectUrl`)와 새 세션 케이스의 HTML refresh 응답.
3. 에러 → MessageObject로 변환 후 템플릿/HTTP 상태 적용.
4. 레이아웃 srl 확정, layout_info / extra_vars / menus 컨텍스트 주입.
5. HTTP 상태 코드/메시지 설정.
6. `new DisplayHandler() -> printContent($oModule)`.

## getModuleInstance() (`:1265`)

```php
$class_name = $module . self::$_kinds[$kind] . self::$_types[$type];
if (class_exists($class_name) && is_subclass_of($class_name, 'ModuleObject')) {
    return $class_name::getInstance($module);
}
```

- autoloader가 클래스 파일을 찾는다.
- `getInstance()`가 `$GLOBALS['_module_instances_']`에 캐시된 인스턴스를 반환.

## triggerCall() (`:1293`)

```php
ModuleHandler::triggerCall($trigger_name, $called_position, $obj_or_data);
```

처리 단계:

1. 미설치 시 빈 BaseObject 반환.
2. `ModuleModel::getTriggers($trigger_name, $called_position)`로 DB 등록 트리거 조회.
3. 각 트리거에 대해:
   - `type`이 `controller|model|view|mobile|api|wap|class` 중 하나면 `getModule($module, $type)`으로 인스턴스화.
   - 그 외(PSR-4 클래스명) 경우 `Rhymix\Modules\<Module>\<Type>` 또는 절대 namespace로 인스턴스화.
   - 블랙리스트 검사.
   - `try-catch`로 메서드 호출.
4. 호출 결과가 false면 즉시 종료 → 호출자에게 BaseObject 반환.
5. 추가로 `ModuleModel::getTriggerFunctions(...)`로 코드 단 등록 콜백 실행.
6. Debug가 현재 사용자에게 활성화되어 있으면 각 트리거의 소요 시간을 `Debug::addTrigger()`로 무조건 기록. `config('debug.log_slow_triggers')`(기본 0.25초)를 초과하는 트리거는 `Debug::addTrigger()` 내부에서 슬로우 트리거 목록에 별도 표시된다.

상세: [13-event-and-trigger-system.md](13-event-and-trigger-system.md).

## ModuleObject

### 핵심 속성

`ModuleObject.class.php:11-39`:

| 속성 | 의미 |
|---|---|
| `module` | 모듈 이름 |
| `module_info` | 모듈 인스턴스 정보 |
| `origin_module_info` | setModuleInfo 호출 시점의 원본 (덮어쓰기 전) |
| `module_config` | 모듈 전역 설정 |
| `module_path` | `modules/<name>/` 경로 |
| `xml_info` | module.xml 파싱 결과 |
| `module_srl` / `mid` / `act` | 현재 액션 컨텍스트 |
| `template_path` / `template_file` | 스킨 템플릿 |
| `layout_path` / `layout_file` / `edited_layout_file` | 레이아웃 |
| `stop_proc` | true면 proc() 건너뜀 |
| `user` | 현재 사용자 (`SessionHelper`) |
| `request` | 현재 요청 객체 |
| `ajaxRequestMethod` | `['XMLRPC', 'JSON']` 호환용 — proc()는 `Context::getResponseMethod()` 직접 검사 |
| `gzhandler_enable` | gzip 활성화 (BaseObject 계열 호환용) |

> `grant` 속성은 클래스에 선언되지 않고 `setPrivileges()` 마지막에 `$this->grant = $grant`로 동적 할당된다 (`:339`). 모듈 코드에서 `$this->grant->access` 같은 식으로 안전하게 참조 가능.

### `getInstance()` 싱글톤 (`:59`)

- `$GLOBALS['_module_instances_'][$class_name]`에 캐시.
- 인스턴스 생성 시 `module_path`/`module` 자동 추출(파일 경로의 `/modules/<name>/` 추출).
- `Context::get('logged_info')` 또는 `Session::getMemberInfo()`로 `$user` 채움.
- `Context::getCurrentRequest()`로 `$request` 채움.

### `setModuleInfo($module_info, $xml_info)` (`:195`)

1. `mid`/`module_srl`/`module_info`/`origin_module_info`/`xml_info`/`skin_vars` 저장.
2. `module_config` 로드(`ModuleModel::getModuleConfig`).
3. `setPrivileges()` 호출 — 현재 사용자 권한 매트릭스 `$this->grant` 채움 + 실패 시 `stop('msg_not_permitted')`.
4. 액션명이 `disp(Admin[A-Z]|[A-Z][a-z0-9_]+Admin)` 패턴이면 (`:214`):
   - `config('view.manager_layout') === 'admin'`이면 `modules/admin/tpl/layout.html` 강제, 아니면 `_admin_common.html` 컴파일.
   - 일정 간격으로 세션 갱신.
5. 클래스에 `init()` 메서드가 있으면 호출 (`Rhymix\Framework\Exception`은 `stop()`으로 전환).

> 스킨/레이아웃 경로 설정(`setLayoutAndTemplatePaths`)은 `setModuleInfo`가 아니라 `proc()`에서 호출한다 (`:846-855`).

### `setLayoutAndTemplatePaths($type, $config)` (`:697`)

- `$type === 'P'` (PC):
  - `layout_srl === -1` → 사이트 기본 PC 레이아웃.
  - 그 외 → 지정 레이아웃.
- `$type === 'M'` (Mobile):
  - `mlayout_srl === -2` → PC 레이아웃과 공유.
  - `mlayout_srl === -1` → 사이트 기본 모바일 레이아웃.
  - 그 외 → 지정.
- 스킨 결정:
  - PC: `module_path/skins/<skin>/`. `skin === '/USE_DEFAULT/'`면 모듈 기본 스킨.
  - Mobile: `module_path/m.skins/<mskin>/`. `mskin === '/USE_RESPONSIVE/'`면 PC 스킨 사용.
- 디렉토리 없으면 `default`로 폴백.

### `proc()` (`:802`)

1. `stop_proc` 체크 — true면 FALSE 즉시 반환 (`:805-808`).
2. `is_mobile` 캐싱 (`:811`).
3. **트리거** — `moduleObject.proc.before` (`:814`). 실패 시 종료.
4. **애드온** — `before_module_proc` (`:828-830`).
5. `is_mobile` 재캐싱 (`:833`).
6. `xml_info->action->{$act}`이 등록되어 있고 `method_exists($this, $act)`인 경우에 한해 (`:836`):
   - **권한 검사** — `module_srl && !grant->access`면 `stop("msg_not_permitted_act")` 후 FALSE (`:839-843`).
   - **스킨 동기화** — `is_skin_fix === 'N'`이면 `setLayoutAndTemplatePaths(viewType, module_info)`, `ModuleModel::syncSkinInfoToModuleInfo` (`:846-855`).
   - **트리거** — `act:<module>.<act>.before` (`:859`).
   - **액션 실행** — `$this->{$act}()` (`:874`). `Rhymix\Framework\Exception`은 BaseObject(-2)로 변환.
   - **트리거** — `act:<module>.<act>.after` (`:883`).
7. 반환값이 `BaseObject`면 에러/메시지 복사 + `original_output` 보관 (`:891-904`).
8. **트리거** — `moduleObject.proc.after` (`:907`).
9. **애드온** — `after_module_proc` (`:921-923`).
10. `original_output` 또는 `output`의 에러를 다시 평가, 실패 시 FALSE.
11. `module_info->module_type`이 `view`/`mobile`이고, HTTP 상태가 400 미만이며 `Context::getResponseMethod()`가 JSON/XMLRPC면 같은 모듈의 `getAPI($module)` 인스턴스에 같은 액션이 있을 때 호출 (`:941-951`).

### 권한 체계 (`grant`)

`module.xml`의 `<permissions>`/액션의 `permission` 속성으로 정의된다.

| 값 | 의미 |
|---|---|
| `guest` | 누구나 |
| `member` | 로그인한 회원 |
| `not_member` | 비로그인만 |
| `manager` | 모듈 매니저 |
| `root` | 슈퍼 관리자 |
| `manager:scope` | 특정 scope의 매니저 |
| `*-managers` | 전체/같은 모듈 매니저 |
| custom grant name | `<grants>`에 정의된 grant ID |

`checkPermission()`이 현재 사용자와 grant를 평가해 boolean을 반환한다.

`grant` 객체는 다음 boolean 속성을 가질 수 있다.

- `access` — 모듈 접근.
- `manager` — 매니저 권한.
- `list` / `view` / `write_document` / `write_comment` / `delete_document` ... (게시판 등).
- module.xml의 grant ID 별 동명 속성.

### `stop($msg_code, $error_code = -1)` (`:531`)

- `stop_proc = true` 설정 후 다시 호출되어도 무시.
- `setError($error_code ?: -1)` + `setMessage($msg_code)`.
- `MessageView::getInstance()`로 메시지 모듈 만들어 `dispMessage('', $location)` (호출지 file:line 자동 기록).
- 그 MessageView의 template_path/template_file/http_status_code를 자신에 복사.

### `copyResponseFrom($oModule)`

- 다른 ModuleObject의 응답(error/message/template_*/redirect_url/variables)을 자신에 복사.
- 위임 패턴에 사용 (예: trash 모듈이 document 모듈 응답을 받음).

## 자주 보게 될 패턴

### 1. View 액션

```php
public function dispBoardContent()
{
    $document_srl = Context::get('document_srl');
    $oDocument = DocumentModel::getDocument($document_srl);
    if (!$oDocument->isExists()) {
        throw new Rhymix\Framework\Exceptions\TargetNotFound;
    }
    Context::set('document', $oDocument);
    $this->setTemplateFile('content');
}
```

### 2. POST 처리 + redirect

```php
public function procBoardInsertDocument()
{
    if (!$this->user->isMember()) {
        throw new Rhymix\Framework\Exceptions\MustLogin;
    }
    // 처리 ...
    $url = getUrl('', 'mid', $this->module_info->mid, 'document_srl', $document_srl);
    $this->setRedirectUrl($url);
}
```

### 3. JSON 응답

```php
public function procBoardGetList()
{
    Context::setResponseMethod('JSON');
    // ...
    $this->add('documents', $list);
    $this->add('total_count', $count);
}
```

### 4. CLI에서 직접 호출

```php
// common/scripts/myscript.php
$oController = getController('board');
$output = $oController->procBoardInsertDocument();
if (!$output->toBool()) {
    echo $output->getMessage();
}
```

## 다음 문서

- 라우팅: [07-router.md](07-router.md)
- 응답 출력: [08-display-and-response.md](08-display-and-response.md)
- 트리거: [13-event-and-trigger-system.md](13-event-and-trigger-system.md)
- 새 모듈 만들기: [27-extension-points/module.md](27-extension-points/module.md)
