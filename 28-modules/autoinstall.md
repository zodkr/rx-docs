# autoinstall (쉬운 설치)

## 개요

- **카테고리**: system
- **역할**: 관리자 모드에서 클릭으로 모듈/스킨/레이아웃/위젯/위젯스타일 등을 자동 설치.

원격 저장소에서 패키지를 다운받아 압축 해제 + 설치.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Autoinstall` | `autoinstall.class.php` |
| `AutoinstallModel` | `autoinstall.model.php` |
| `AutoinstallAdminController` | `autoinstall.admin.controller.php` |
| `AutoinstallAdminModel` | `autoinstall.admin.model.php` |
| `AutoinstallAdminView` | `autoinstall.admin.view.php` |
| (라이브러리) | `autoinstall.lib.php` — 원격 카탈로그/패키지 유틸 |

(`autoinstall.controller.php`, `autoinstall.view.php`, `autoinstall.mobile.php`, `autoinstall.api.php`는 없다 — autoinstall은 관리자 전용 모듈.)

## 주요 액션 (15개)

| 액션 | 비고 |
|---|---|
| `dispAutoinstallAdminIndex` | 설치 가능 패키지 목록 (admin_index, menu_name=easyInstall) |
| `dispAutoinstallAdminInstall` / `dispAutoinstallAdminUninstall` | 설치/제거 화면 |
| `dispAutoinstallAdminInstalledPackages` | 설치된 패키지 목록 |
| `dispAutoinstallAdminConfig` | 설정 |
| `getAutoinstallAdminMenuPackageList` / `getAutoinstallAdminLayoutPackageList` / `getAutoinstallAdminSkinPackageList` | 카테고리별 패키지 모델 |
| `getAutoinstallAdminIsAuthed` | 인증 상태 |
| `getAutoInstallAdminInstallInfo` / `getAutoInstallAdminModuleConfig` | 설치 정보/설정 |
| `procAutoinstallAdminUpdateinfo` | 카탈로그 업데이트 |
| `procAutoinstallAdminPackageinstall` / `procAutoinstallAdminUninstallPackage` | 설치/제거 (ruleset=ftp) |
| `procAutoinstallAdminInsertConfig` | 설정 저장 |

## 저장소

원격 카탈로그 API로부터 패키지 목록을 가져온다. 기본 저장소는 Rhymix 공식 + xpressengine.org legacy.

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `autoinstall_packages` | `schemas/autoinstall_packages.xml` |
| `ai_installed_packages` | `schemas/ai_installed_packages.xml` — 설치된 패키지 |
| `ai_remote_categories` | `schemas/ai_remote_categories.xml` — 원격 카탈로그 |

## 관련

- module 모듈: [module.md](module.md)
- 코어 정리 스크립트: [../21-cli-and-scripts.md](../21-cli-and-scripts.md)
