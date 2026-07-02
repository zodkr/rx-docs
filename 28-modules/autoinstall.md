# autoinstall (쉬운 설치)

## 개요

- **카테고리**: system
- **역할**: 관리자 모드에서 클릭으로 모듈/스킨/레이아웃/위젯/위젯스타일 등을 자동 설치.

원격 저장소에서 패키지를 다운받아 압축 해제 + 설치.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Autoinstall` | `autoinstall.class.php` |
| `AutoinstallAdminController` | `autoinstall.admin.controller.php` |
| `AutoinstallAdminModel` | `autoinstall.admin.model.php` |
| `AutoinstallAdminView` | `autoinstall.admin.view.php` |
| `Rhymix\Modules\Autoinstall\Models\Package` | `models/Package.php` — 패키지 목록/상세 조회·설치 가능 여부 판정 |
| `Rhymix\Modules\Autoinstall\Models\Installer` | `models/Installer.php` — ZIP 다운로드·압축 해제·삭제 |

(`autoinstall.controller.php`, `autoinstall.view.php`, `autoinstall.mobile.php`, `autoinstall.api.php`는 없다 — autoinstall은 관리자 전용 모듈.)

## 주요 액션 (12개)

`conf/module.xml`에 등록된 순서대로:

| 액션 | 비고 |
|---|---|
| `dispAutoinstallAdminIndex` | 추천/카테고리별 패키지 목록·검색 (admin_index, menu_name=easyInstall) |
| `dispAutoinstallAdminPackageDetail` | 패키지 상세 화면 (menu_name=easyInstall) |
| `procAutoinstallAdminDownloadPackage` | 패키지 ZIP 다운로드 |
| `procAutoinstallAdminInstallPackage` | 설치/업데이트 (다운로드된 ZIP 압축 해제) |
| `procAutoinstallAdminPostInstallPackage` | 모듈 설치 후처리 (`procInstallAdminInstall`/`Update` 호출) |
| `procAutoinstallAdminUninstallPackage` | 제거 |
| `getAutoinstallAdminMenuPackageList` / `getAutoinstallAdminLayoutPackageList` / `getAutoinstallAdminSkinPackageList` | 하위호환용 빈 스텁 |
| `getAutoinstallAdminIsAuthed` / `getAutoInstallAdminInstallInfo` / `getAutoInstallAdminModuleConfig` | 하위호환용 액션 (앞 둘은 고정값 스텁, `getAutoInstallAdminModuleConfig`는 실제 모듈 설정 반환 — 뷰 `init()`에서도 사용) |

카탈로그(패키지 목록) 갱신은 별도 액션이 아니라 관리자 뷰 `init()`에서 마지막 갱신 후 4시간(14400초)이 지났을 때 자동 수행된다 (`autoinstall.admin.view.php:16-26`).

## 저장소

Rhymix PDS API(목록 `https://api.rhymix.org/pds/index.json`, 상세 `https://api.rhymix.org/pds/detail/{srl}.json`)에서 패키지 목록을 가져와 로컬 `autoinstall_packages` 테이블에 캐시한다 (`models/Package.php:18-19`). 관리자 뷰 진입 시 마지막 갱신 후 4시간이 지났으면 `Package::updatePackageList()`가 테이블을 비우고(`TRUNCATE`) 최신 목록으로 다시 채운다 (`models/Package.php:434-488`).

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `autoinstall_packages` | `schemas/autoinstall_packages.xml` — 패키지 카탈로그 캐시 |

과거 테이블 `ai_installed_packages`·`ai_remote_categories`(및 `autoinstall_installed_packages`·`autoinstall_remote_categories`)는 재작성 시 deprecated 처리되어, 모듈 업그레이드 시 `Autoinstall::moduleUpdate()`가 `dropTable()`로 삭제한다 (`autoinstall.class.php:13-18`).

## 관련

- module 모듈: [module.md](module.md)
- 코어 정리 스크립트: [../21-cli-and-scripts.md](../21-cli-and-scripts.md)
