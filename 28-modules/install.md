# install (설치)

## 개요

- **카테고리**: system
- **역할**: Rhymix 초기 설치. `Context::isInstalled()`가 false일 때 진입하는 모듈.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Install` | `install.class.php` |
| `InstallController` | `install.controller.php` |
| `InstallModel` | `install.model.php` |
| `InstallView` | `install.view.php` |
| `InstallAdminController` | `install.admin.controller.php` |

(`install.admin.model.php`/`view.php`/`mobile.php`/`api.php`는 없다.)

## 주요 액션 (10개)

| 액션 | 비고 |
|---|---|
| `dispInstallIndex` | 라이센스 동의(index) |
| `dispInstallCheckEnv` | 환경 검사 |
| `dispInstallDBConfig` | DB 정보 입력 |
| `dispInstallOtherConfig` | 사이트/관리자 정보 입력 |
| `getInstallFTPList` | (root) FTP 모드 목록 |
| `procInstallLicenseAgreement` | 라이센스 동의 처리 |
| `procDBConfig` | DB 연결 테스트/저장 |
| `procInstall` | 설치 실행 (ruleset=install) |
| `procInstallAdminInstall` | 관리자 모드 모듈 설치 |
| `procInstallAdminUpdate` | 관리자 모드 모듈 업데이트 |

## 동작

`Context::isInstalled()`이 false면 `ModuleHandler.class.php:61-66`이 `$this->module = 'install'`로 강제 설정. 사용자가 어떤 URL을 호출해도 install로 라우팅.

## 설치 단계

1. **환경 검사** — PHP 버전, 확장, 권한 등.
2. **DB 설정** — 호스트/포트/사용자/DB명 입력.
3. **DB 테스트** — 연결 가능 확인.
4. **관리자 계정** — root 회원 생성.
5. **사이트 정보** — 사이트 제목/관리자 이메일.
6. **테이블 생성** — 모든 코어 모듈의 `schemas/*.xml` 일괄 실행.
7. **`files/config/config.php`** — 자동 생성.
8. **완료** → 관리자 페이지로 이동.

## 코어 모듈 일괄 설치

설치 마지막 단계에서 `modules/` 하위의 모든 모듈을 순회하며 `moduleInstall()` 호출 + `schemas/*.xml` 실행.

## 보안

설치 후 `install` 모듈 자체는 자동으로 차단된다 (`Context::isInstalled()` true 시 진입 불가).

## 관련

- module: [module.md](module.md)
- 설정: [../25-config-system.md](../25-config-system.md)
- DB: [../14-database-and-queries.md](../14-database-and-queries.md)
