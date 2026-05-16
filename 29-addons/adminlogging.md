# adminlogging (애드온)

## 개요

- **목적**: 관리자 페이지 액션을 자동 로깅. 누가 언제 어떤 설정을 변경했는지 추적.

## hook 위치

`before_module_proc` — 로그인 사용자가 admin 관련 액션(`act`에 'admin' 포함)을 호출하고 `is_admin === 'Y'`일 때 1회 기록.

## 동작

`addons/adminlogging/adminlogging.addon.php` (실제 코드):

```php
$logged_info = Context::get('logged_info');
if ($called_position === 'before_module_proc'
    && $logged_info->is_admin === 'Y'
    && stripos(Context::get('act') ?? '', 'admin') !== false)
{
    $oAdminloggingController = adminloggingController::getInstance();
    $oAdminloggingController->insertLog($this->module, $this->act);
}
```

`adminloggingController::insertLog($module, $act)`는 `adminlogging` 모듈의 로그 테이블에 모듈/액션/요청 정보를 기록한다.

## 관련

- 동명 모듈: [../28-modules/adminlogging.md](../28-modules/adminlogging.md)
