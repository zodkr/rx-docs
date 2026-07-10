# addon (애드온 관리)

## 개요

- **카테고리**: utility
- **역할**: 애드온 등록/활성화/비활성화/설정. 활성 애드온을 PHP 파일로 컴파일.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Addon` | `addon.class.php` |
| `AddonController` | `addon.controller.php` |
| `AddonModel` | `addon.model.php` |
| `AddonAdminController/Model/View` | `addon.admin.*.php` |

## 주요 액션 (6개)

| 액션 | 비고 |
|---|---|
| `dispAddonAdminIndex` | 애드온 목록(installedAddon 메뉴 진입) |
| `dispAddonAdminInfo` | 개별 애드온 정보 |
| `dispAddonAdminSetup` | 애드온 설정 화면 |
| `procAddonAdminSetupAddon` | 설정 저장 (ruleset=updateAddonSetup) + 컴파일 |
| `procAddonAdminToggleActivate` | 활성/비활성 토글 |
| `procAddonAdminSaveActivate` | 활성 상태 일괄 저장 |

## 컴파일 캐시

- 위치: `files/cache/addons/pc.php`, `files/cache/addons/mobile.php`.
- 생성자: `AddonController::makeCacheFile($site_srl, $type, $gtype)` (`modules/addon/addon.controller.php:72`).
- 활성 애드온 전체를 하나의 PHP 파일로 결합.

`AddonController::getCacheFilePath('pc'|'mobile')` 메서드로 캐시 파일 경로 획득.

## DB 스키마

| 테이블 | 정의 파일 | 용도 |
|---|---|---|
| `addons` | `schemas/addons.xml` | global/fixed 레거시 설정 (`is_fixed` 포함) |
| `addons_site` | `schemas/addons_site.xml` | `site_srl`별 일반 애드온 설정(기본 사이트 `0` 포함) |

(`addons_module` 같은 테이블은 없다 — 애드온 활성화는 사이트 단위이며, 모듈별 실행 제어는 애드온 설정 화면(`dispAddonAdminSetup`)에서 선택한 `mid_list`(`extra_vars`에 직렬화 저장)로 관리한다. `makeCacheFile`이 이 값을 이용해 현재 `mid`에 따라 실행 여부를 결정한다 — `modules/addon/addon.controller.php:95-128`.)

## 활성화 단위

- 일반 site 설정 (`gtype='site'`)은 `addons_site`에 저장하며 기본 사이트도 `site_srl=0` 레코드를 사용한다.
- global/fixed 설정 (`gtype='global'`)은 `addons`에 저장한다. `makeCacheFile(..., gtype='global')`을 명시 호출할 때만 `is_fixed='Y'` 항목을 포함하며, 현재 표준 관리자·자동 재생성 호출은 모두 site 설정을 생성한다.
- 각 활성화는 PC(`is_used`)와 모바일(`is_used_m`)을 별도로 토글.

현재 런타임 캐시 경로는 site별이 아니라 PC/모바일 각각 `pc.php`·`mobile.php` 하나뿐이다. `makeCacheFile($site_srl, ...)`는 어느 site를 받더라도 같은 파일을 덮어쓰고, cache miss 자동 재생성은 `site_srl=0`을 사용한다 (`addon.controller.php:27-45,72-86,147-148`). 따라서 DB에 site별 행을 저장할 수 있다는 사실을 동시 다중 사이트별 런타임 캐시 격리 보장으로 해석하면 안 된다.

## 다음 문서

- 새 애드온 만들기: [../27-extension-points/addon.md](../27-extension-points/addon.md)
- 코어 애드온: [../29-addons/](../29-addons/)
- 이벤트 시스템: [../13-event-and-trigger-system.md](../13-event-and-trigger-system.md)
