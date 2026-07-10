# adminlogging (애드온)

## 개요

- **목적**: 슈퍼관리자가 `act` 이름에 `admin`이 포함된 액션을 호출하려는 시점에 모듈·액션·요청 정보를 기록. 조회나 실패한 시도도 포함될 수 있어 실제 설정 변경 성공을 보장하는 감사 로그는 아니다.

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
