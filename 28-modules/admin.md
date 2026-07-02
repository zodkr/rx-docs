# admin (관리자)

## 개요

- **카테고리**: system
- **역할**: 관리자 페이지 전체 — 대시보드/시스템 설정/통계/사이트맵/메뉴.

`modules/admin/`은 **namespace 패턴을 광범위하게 사용**하는 모듈로 좋은 참조 예시.

## 주요 클래스

### 레거시 (관리자 전용 파일만 존재)

| 클래스 | 파일 |
|---|---|
| `Admin` | `admin.class.php` — `class_alias('Rhymix\Modules\Admin\Controllers\Base', 'Admin')`만 정의 |
| `AdminAdminController` | `admin.admin.controller.php` |
| `AdminAdminModel` | `admin.admin.model.php` |
| `AdminAdminView` | `admin.admin.view.php` |

> 일반 사용자용 `admin.controller.php`/`admin.model.php`/`admin.view.php`는 없다 — admin 모듈은 관리자 전용이므로 admin 클래스만 존재.

### namespace (controllers/, models/)

`modules/admin/controllers/`, `modules/admin/models/` 하위 (views 디렉토리는 admin에 없음). `Rhymix\Modules\Admin\Controllers\*` 형식.

실제 파일 (`controllers/`):

- `Base.php` — 공용 init/관리자 권한 체크/admin 메뉴 로드.
- `Dashboard.php` — 대시보드.
- `Install.php` — 모듈 설치 hook (`moduleInstall`/`moduleUpdate`).
- `AdminMenu.php`, `Design.php`, `ServerEnv.php` — 각 화면.
- `maintenance/CacheReset.php`, `maintenance/Cleanup.php` — 유지보수.
- `systemconfig/Advanced.php`, `systemconfig/Debug.php`, `systemconfig/Domains.php`, `systemconfig/Notification.php`, `systemconfig/Queue.php`, `systemconfig/SEO.php`, `systemconfig/Security.php`, `systemconfig/SiteLock.php` — 시스템 설정.

> 디스크상 디렉토리명은 **소문자** `maintenance/`/`systemconfig/`다(파일 시스템 그대로). autoloader가 `Rhymix\Modules\Admin\Controllers\<Sub>\…`의 중간 segment를 `strtolower`로 매핑하므로(`common/autoload.php:62`) `Controllers\SystemConfig\Domains`(코어 `module.xml`의 표기)와 `Controllers\systemconfig\Domains` 모두 동일 파일을 가리킨다.

`module.xml`에서 `<action ... class="Controllers\Dashboard" />` 형식으로 등록 (메서드명 = 액션 이름).

## 주요 액션 (`modules/admin/conf/module.xml`)

| 액션 | 비고 |
|---|---|
| `dispAdminIndex` | 대시보드 (index) |
| `procAdminLogout` | 로그아웃 |
| `dispAdminConfigGeneral` | 도메인 관리(시스템 설정 진입, menu_index) |
| `dispAdminInsertDomain` / `dispAdminCopyDomain` | 도메인 추가/복사 |
| `procAdminInsertDomain` / `procAdminUpdateDomainConfig` / `procAdminDeleteDomain` | 도메인 CRUD |
| `dispAdminConfigNotification` / `procAdminUpdateNotification` | 알림 설정 |
| `dispAdminConfigSecurity` / `procAdminUpdateSecurity` | 보안 설정 |
| `dispAdminConfigAdvanced` / `procAdminUpdateAdvanced` | 고급 설정 |
| `dispAdminConfigDebug` / `procAdminUpdateDebug` | 디버그 |
| `dispAdminConfigSEO` / `procAdminUpdateSEO` | SEO |
| `dispAdminConfigQueue` / `procAdminUpdateQueue` | 큐 |
| `dispAdminConfigSitelock` / `procAdminUpdateSitelock` | 사이트 잠금 |
| `dispAdminSetup` | 관리자 화면 설정 |
| `procAdminMenuReset` / `procAdminToggleFavorite` | 관리자 메뉴 조작 |
| `dispAdminViewServerEnv` / `dispAdminRewriteTest` | 서버 환경/리라이트 테스트 |
| `procAdminClearApcu` / `procAdminClearOpcache` / `procAdminRecompileCacheFile` | 캐시 비우기 |
| `dispAdminCleanupList` / `procAdminCleanupFiles` / `procAdminAddCleanupException` / `procAdminResetCleanupException` | 정리 |
| `dispAdminConfigFtp` / `procAdminUpdateFTPInfo` / `procAdminRemoveFTPInfo` | FTP (레거시) |
| `procAdminUpdateConfig` / `procAdminDeleteLogo` | 일반 config 저장/로고 삭제 |
| `procAdminInsertDefaultDesignInfo` | 기본 디자인 정보 저장 |
| `getSiteAllList` | 사이트 전체 목록 (root 권한) |

## 권한

`is_admin === 'Y'` 회원(관리자)만 접근 가능. 모든 admin 컨트롤러는 `init()`에서 `isAdmin()`을 검사해 관리자가 아니면 `NotPermitted` 예외를 던진다 — namespace 컨트롤러 및 `AdminAdminView`는 `Base::init()`(`controllers/Base.php:23-25`), 레거시 `AdminAdminController`는 자체 init override에서 동일 체크(`admin.admin.controller.php:13-19`). `module.xml`의 `<grants />`는 비어 있고(`conf/module.xml:3`), `getSiteAllList`만 추가로 root 권한을 요구한다(`conf/module.xml:53`). 모듈 매니저(`*-managers`)에게 부분 허용하는 액션은 없다.

## DB 스키마

자체 테이블 1개. 다른 모듈의 데이터를 종합 표시.

| 테이블 | 정의 파일 | 용도 |
|---|---|---|
| `admin_favorite` | `schemas/admin_favorite.xml` | 관리자 즐겨찾기 메뉴 (`admin_favorite_srl`, `site_srl`, `module`, `type`) |

(관리자 액션 로그는 별개의 `adminlogging` 모듈에서 `admin_log` 테이블로 관리. [adminlogging.md](adminlogging.md) 참고.)

## URL 패턴

`mid='admin'` 또는 admin 액션이면 자동으로 admin 모듈 라우팅. `ModuleHandler.class.php:102-106`:

```php
if (!$this->module && $this->mid === 'admin') {
    Context::set('module', $this->module = 'admin');
    Context::set('mid', $this->mid = null);
}
```

## namespace 사용 예 (`module.xml` 발췌)

```xml
<action name="dispAdminConfigGeneral"
        class="Controllers\SystemConfig\Domains"
        menu_name="adminConfigurationGeneral" menu_index="true" />

<action name="procAdminInsertDomain"
        class="Controllers\SystemConfig\Domains" />
```

→ `Rhymix\Modules\Admin\Controllers\SystemConfig\Domains` 클래스의 `dispAdminConfigGeneral()` / `procAdminInsertDomain()` 메서드 호출 (메서드명 = 액션 이름). `method=` 속성은 PHP 메서드명이 아니라 허용 HTTP 메서드.

## 이 모듈이 정의하는 트리거

| 이름 | 시점 |
|---|---|
| `admin.dashboard` | before — `modules/admin/tpl/index.html`에서 대시보드 빌드 직전 발사. 외부 모듈이 hook해 대시보드 위젯/위 표시 추가 가능 |

## 관련 모듈

- 모든 다른 모듈 (관리 UI 진입점).
- `module` — 모듈 관리.
- `layout` — 레이아웃 관리.
- `menu` — 메뉴 관리.
- `adminlogging` — 관리자 액션 로그.

## 다음 문서

- 다중 사이트: [../22-multi-site-and-domain.md](../22-multi-site-and-domain.md)
- 설정: [../25-config-system.md](../25-config-system.md)
- namespace autoload: [../26-namespaces-and-autoload.md](../26-namespaces-and-autoload.md)
