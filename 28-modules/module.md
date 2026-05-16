# module (모듈 관리)

## 개요

- **카테고리**: system
- **역할**: 모듈 자체의 메타 관리 — 등록/설치/업데이트/삭제, 트리거 등록, 모듈 인스턴스 생성/복사.

다른 모듈을 다루는 **메타 모듈**.

## 주요 클래스

| 클래스 | 파일 | 역할 |
|---|---|---|
| `Module` | `module.class.php` | ModuleObject. |
| `ModuleController` | `module.controller.php` | `insertModule`/`updateModule`/`deleteModule` 등 모듈 인스턴스 CRUD. `insertEventHandler`(트리거 DB 등록). |
| `ModuleModel` | `module.model.php` | 모듈 정보 조회. `getModuleInfoByMid`, `getModuleConfig`, `getTriggers`, `getModuleActionXml`. |
| `ModuleView` | `module.view.php` | (거의 비어 있음) |
| `ModuleMobile` | `module.mobile.php` | 모바일 분기. |
| `ModuleAdminController` | `module.admin.controller.php` | 관리자 처리. |
| `ModuleAdminModel` | `module.admin.model.php` | 관리자 조회. |
| `ModuleAdminView` | `module.admin.view.php` | 관리자 UI. |

(`module.api.php`는 없다.)

## 주요 액션 (44개)

`modules/module/conf/module.xml` 전수.

### 사용자/공용

| 액션 | 비고 |
|---|---|
| `dispModuleSelectList` / `dispModuleSkinInfo` | 모듈 선택/스킨 정보 (all-managers) |
| `dispModuleFileBox` / `dispModuleFileBoxAdd` | 파일박스 (root) |
| `dispModuleChangeLang` | 언어 전환 |
| `getModuleSkinInfoList` / `getFileBoxListHtml` / `getModuleInfoByMenuItemSrl` | 모델 (root) |
| `getLangListByLangcodeForAutoComplete` / `getLangByLangcode` | 다국어 자동완성 |
| `procModuleFileBoxAdd` / `procModuleFileBoxDelete` | 파일박스 CRUD (root) |
| `procModuleClearCache` | 캐시 비우기 (CSRF 면제) |

### 관리자

| 액션 | 비고 |
|---|---|
| `dispModuleAdminContent` | 모듈 관리 진입 (admin_index, menu_name=installedModule) |
| `dispModuleAdminCategory` / `dispModuleAdminInfo` / `dispModuleAdminModuleSetup` / `dispModuleAdminModuleAdditionSetup` / `dispModuleAdminModuleGrantSetup` / `dispModuleAdminCopyModule` | 모듈 설정 화면 |
| `dispModuleAdminFileBox` / `dispModuleAdminLangcode` | 파일박스/다국어 관리 |
| `getModuleAdminModuleList` / `getModuleAdminModuleInfo` / `getModuleAdminGrant` 외 6개 | 관리자 모델 조회 |
| `procModuleAdminInsertCategory` / `UpdateCategory` / `DeleteCategory` | 카테고리 CRUD (ruleset 동명) |
| `procModuleAdminModuleSetup` / `procModuleAdminModuleGrantSetup` / `procModuleAdminCopyModule` | 모듈 설정/권한/복사 (ruleset=insertModuleSetup/insertModulesGrant/copyModule) |
| `procModuleAdminInsertGrant` / `procModuleAdminUpdateSkinInfo` | 권한/스킨 (manager) |
| `procModuleAdminInsertLang` / `procModuleAdminDeleteLang` | 다국어 코드 CRUD (manager) |
| `procModuleAdminGetList` / `procModuleAdminSetDesignInfo` / `procModuleAdminUpdateUseMobile` | 목록/디자인/모바일 토글 |

> **모듈 인스턴스 자체의 생성/수정/삭제(`insertModule`/`updateModule`/`deleteModule`)는 module.xml 액션이 아니다** — `ModuleController`의 인스턴스 메서드로만 제공되어, autoinstall/page/menu 등 다른 모듈에서 직접 호출한다. **모듈 자체 설치/제거(`procModuleAdminInstall`/`Uninstall`/`Update`)는 `autoinstall` 모듈에 있다**.

## DB 스키마

`modules/module/schemas/`의 20개 테이블:

| 테이블 | 용도 |
|---|---|
| `modules` | 모듈 인스턴스 (도메인별 mid) |
| `module_admins` | 모듈 관리자 매핑 |
| `module_categories` | 모듈 카테고리 |
| `module_config` | 모듈 전역 설정 (직렬화) |
| `module_part_config` | 부분 설정 |
| `module_extra_vars` | 모듈 사용자 정의 변수 |
| `module_extend` | 모듈 확장 정보 |
| `module_skins` | PC 스킨 설정 |
| `module_mobile_skins` | 모바일 스킨 설정 |
| `module_grants` | 모듈별 권한 |
| `module_trigger` | 등록된 트리거 핸들러 (단수) |
| `module_locks` | 모듈 잠금 |
| `module_filebox` | 파일박스 |
| `module_update` | 모듈 업데이트 상태 |
| `action_forward` | 외부 모듈이 추가한 액션 forward |
| `domains` | 도메인 등록 |
| `sites` | 사이트 (deprecated, 호환만) |
| `lang` | 다국어 사용자 정의 |
| `task_queue` | 큐 작업 |
| `task_schedule` | 큐 스케줄 |

(`triggers`/`extension_actions` 같은 옛 이름은 잘못 — 정확한 이름은 `module_trigger`, `action_forward`.)

## 핵심 메서드

### `ModuleModel::getModuleInfoByMid($mid, $domain_srl)`

mid로 모듈 인스턴스 정보 조회. 캐싱.

### `ModuleModel::getModuleActionXml($module)`

모듈의 `conf/module.xml` 파싱 결과 반환. 캐싱.

### `ModuleModel::getTriggers($name, $position)`

특정 트리거 이름의 등록 핸들러 목록 반환. `ModuleHandler::triggerCall`이 사용.

### `ModuleController::registerEventHandlers(string $module_name)` (`module.controller.php:1467`)

`ModuleModel::getModuleActionXml($module_name)->event_handlers`를 순회해서 신규 항목은 `insertTrigger(...)`(`:75`)로 `module_trigger` 테이블에 등록하고, 더 이상 정의되지 않은 항목은 `deleteTrigger(...)`(`:100`)로 제거. 캐시 키는 `'triggers'`. `insertEventHandler` 같은 메서드는 없다.

### `ModuleController::insertTrigger($name, $module, $type, $method, $position)`

코드 단에서 트리거 등록.

## 이 모듈이 정의하는 트리거

| 이름 | 시점 |
|---|---|
| `module.dispAdditionSetup` | before/after — 모듈 추가 설정 UI (board.admin.view.php / module.admin.view.php / module.admin.model.php에서 발사) |
| `module.getModuleAdminScopes` | 관리자 권한 scope 등록 |
| `module.deleteModule` | before/after — 모듈 인스턴스 삭제 |
| `module.procModuleAdminCopyModule` | before/after — 모듈 복사 |

(`module.dispAdditionSetupGeneral`/`module.dispAdditionSetupSecurity` 같은 분기는 코드에 없다.)

## CLI 스크립트

| 스크립트 | 호출 |
|---|---|
| `cleanMiscLogs.php` | `php index.php module.cleanMiscLogs` |
| `updateAllModules.php` | `php index.php module.updateAllModules` |

## 관련 모듈

- `admin` — 관리 UI.
- `autoinstall` — 외부 모듈 자동 설치.
- 모든 다른 모듈 (메타 관리 대상).

## 다음 문서

- 새 모듈 만들기: [../27-extension-points/module.md](../27-extension-points/module.md)
- 트리거 시스템: [../13-event-and-trigger-system.md](../13-event-and-trigger-system.md)
- 자동 설치: [autoinstall.md](autoinstall.md)
