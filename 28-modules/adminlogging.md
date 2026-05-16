# adminlogging (관리자 로깅)

## 개요

- **카테고리**: system
- **역할**: 슈퍼관리자가 admin 액션을 호출할 때마다 한 행을 `admin_log` 테이블에 기록. 모듈 자체는 자체 화면이 없고, 동명 애드온이 기록 전부를 담당한다.

## 주요 클래스

| 클래스 | 파일 | 내용 |
|---|---|---|
| `adminlogging extends ModuleObject` | `adminlogging.class.php` | 설치/업데이트 hook 4개 (`moduleInstall`/`checkUpdate`/`moduleUpdate`/`recompileCache`). `moduleUpdate`는 `admin_log` 테이블에 `member_srl` 컬럼, `idx_member_srl` 인덱스, `request_vars` 컬럼의 `bigtext` 타입을 추가/변경. |
| `adminloggingController extends adminlogging` | `adminlogging.controller.php` | 인스턴스 메서드 `insertLog($module, $act)` 하나만 정의. |
| `adminloggingModel extends adminlogging` | `adminlogging.model.php` | **빈 클래스** — 메서드를 정의하지 않는다. 호환성을 위해 존재만 함. |

(`adminlogging.view.php`, `adminlogging.admin.controller.php`/`model.php`/`view.php`, `adminlogging.mobile.php`, `adminlogging.api.php`는 모두 없다.)

## 주요 액션 (0개)

`modules/adminlogging/conf/module.xml`의 `<actions>` 절은 비어 있다. 사용자/관리자 진입 액션을 두지 않고, 동명 애드온이 로깅을 수행한다.

## DB 스키마 — `schemas/admin_log.xml`

| 컬럼 | 타입 | 비고 |
|---|---|---|
| `id` | number, PK, auto_increment | |
| `site_srl` | number, default 0 | |
| `member_srl` | number, default 0 | `idx_member_srl` |
| `module` | varchar(100) | 기록 시점의 모듈명 |
| `act` | varchar(100) | 기록 시점의 액션명 |
| `request_vars` | bigtext | `Context::getRequestVars()`를 `json_encode`로 직렬화한 사용자 요청 전체 |
| `regdate` | date | `idx_admin_date`, `YmdHis` |
| `ipaddress` | varchar(60), notnull | `idx_admin_ip`, `RX_CLIENT_IP` |

쿼리: `queries/insertLog.xml` (호출 ID `adminlogging.insertLog`).

## 동작

`addons/adminlogging/adminlogging.addon.php`의 실제 가드 조건 (`logged_info`가 false여도 별도 검사 없이 속성을 직접 평가하므로, 비로그인 요청에서는 PHP가 `false->is_admin`을 평가하면서 `null === 'Y'` → false가 되어 자연히 분기가 통과되지 않을 뿐, **명시적인 logged_info 존재 검사는 없다**):

```php
$logged_info = Context::get('logged_info');
if ($called_position === 'before_module_proc'
    && $logged_info->is_admin === 'Y'
    && stripos(Context::get('act') ?? '', 'admin') !== false)
{ ... }
```

즉 실제 가드 조건은 세 개:

- `$called_position === 'before_module_proc'` — 4개 hook 위치 중 이 위치일 때만. 다른 hook(`before_module_init`/`after_module_proc`/`before_display_content`)에서는 같은 컴파일 캐시가 include되지만 조건이 false라 분기 안 됨.
- `$logged_info->is_admin === 'Y'` (로그인되지 않았으면 PHP 8 기준 `Attempt to read property "is_admin" on false` 경고가 발생할 수 있음)
- `stripos(Context::get('act') ?? '', 'admin') !== false` — 액션명에 `'admin'`이 포함

이때 애드온이 `$this`(현재 ModuleObject) 스코프에서 다음을 호출:

```php
$oAdminloggingController = adminloggingController::getInstance();
$oAdminloggingController->insertLog($this->module, $this->act);
```

`insertLog($module, $act)` 내부 (`adminlogging.controller.php:18-33`):

```php
if (!$module || !$act) { return; }   // 둘 중 하나라도 비면 무시
$args = (object)[
    'member_srl'   => $this->user->member_srl,
    'module'       => $module,
    'act'          => $act,
    'request_vars' => json_encode(Context::getRequestVars(),
        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT),
    'regdate'      => date('YmdHis'),
    'ipaddress'    => \RX_CLIENT_IP,
];
executeQuery('adminlogging.insertLog', $args);
```

조회 메서드(모델)나 관리자 UI는 없어 로그는 직접 DB나 외부 도구로 조회한다. 비밀번호 같은 민감한 필드가 `request_vars` JSON에 그대로 들어가므로 운영 환경에서는 접근 제어에 주의.

## 관련

- 동명 애드온: [../29-addons/adminlogging.md](../29-addons/adminlogging.md)
- admin 모듈: [admin.md](admin.md)
