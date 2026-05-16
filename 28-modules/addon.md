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
| `addons` | `schemas/addons.xml` | 사이트 기본 애드온 설정 (`addon`, `is_used`, `is_used_m`, `is_fixed`, `extra_vars`) |
| `addons_site` | `schemas/addons_site.xml` | 다중 사이트의 site_srl별 override (`site_srl`, `addon`, `is_used`, `is_used_m`, `extra_vars`) |

(`addons_module` 같은 테이블은 없다 — 애드온 활성화는 사이트 단위, 모듈별 override는 모듈 설정 화면의 별도 컬럼으로 관리.)

## 활성화 단위

- 사이트 기본 (`addons`).
- 다중 사이트의 사이트별 override (`addons_site`).
- 각 활성화는 PC(`is_used`)와 모바일(`is_used_m`)을 별도로 토글.

## 다음 문서

- 새 애드온 만들기: [../27-extension-points/addon.md](../27-extension-points/addon.md)
- 코어 애드온: [../29-addons/](../29-addons/)
- 이벤트 시스템: [../13-event-and-trigger-system.md](../13-event-and-trigger-system.md)
