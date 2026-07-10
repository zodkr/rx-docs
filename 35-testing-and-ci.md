# 35. 테스팅과 CI

## Codeception

Rhymix는 Composer dev 의존성 대신 **Codeception `.phar` 파일을 다운로드**해 테스트한다. 저장소에는 Codeception 버전이나 checksum이 고정되어 있지 않고, CI가 PHP 버전별 `https://res.rhymix.org/ci/php<버전>/codecept.phar`를 받는다 (`.github/workflows/ci.yml:26-27`). 따라서 정확한 Codeception 버전은 저장소만으로 단정할 수 없으며, 받은 파일에서 `php codecept.phar --version`으로 확인해야 한다.

### 설정 — `codeception.dist.yml`

```yaml
actor: Tester
paths:
    tests: tests
    output: tests/_output
    data: tests/_data
    helpers: tests/_support
bootstrap: _bootstrap.php
settings:
    colors: true
    memory_limit: 1024M
    error_level: "E_ALL & ~E_STRICT & ~E_DEPRECATED & ~E_NOTICE"
coverage:
    enabled: true
    whitelist:
        include:
          - common/framework/*
        exclude:
          - common/framework/drivers/*
```

**커버리지 화이트리스트**: `common/framework/*`만 측정, 드라이버 제외 (드라이버는 통합 테스트 영역).

## 테스트 스위트

### unit (`tests/unit/`)

`Rhymix\Framework\*`, `classes/*`, `common/functions.php` 등의 단위 테스트.

대표 파일:

- `tests/unit/framework/RouterTest.php`
- `tests/unit/framework/CacheTest.php`
- `tests/unit/framework/StorageTest.php`
- `tests/unit/framework/SecurityTest.php`
- `tests/unit/framework/UATest.php`

설정: `tests/unit.suite.dist.yml`.

### install (`tests/install/`)

두 가지 설치 시나리오의 통합 테스트.

- `InstallCept.php` — 라이선스 동의부터 환경 확인, DB 설정, 관리자 생성까지 브라우저로 진행하는 대화형 설치.
- `AutoinstallCept.php` — `config/install.config.php`를 미리 작성해 설치 화면 없이 진행하는 자동 설치. 여기서 `Autoinstall`은 `modules/autoinstall` 확장 설치 기능이 아니라 unattended core installation을 뜻한다.

- PHP dev server 필요 (`php -S localhost:8000`).
- MySQL 데이터베이스 `rhymix` (사용자 `rhymix`/비밀번호 `rhymix`) 필요.

설정: `tests/install.suite.dist.yml` (로컬에서 DB 접속정보 등을 바꾸려면 `install.suite.dist.yml`을 `install.suite.yml`로 복사해서 오버라이드; CI는 복사 없이 `.dist.yml`을 그대로 사용).

### `tests/_data/`

테스트용 fixture. 특히 템플릿 엔진 테스트는 `tests/_data/template/`의 `v1*.html`/`v2*.html` 입력 + `*.executed.html` 골든 출력을 비교.

### `tests/_support/`

`UnitTester.php`, `InstallTester.php` 등 Codeception 헬퍼. `codecept build`로 자동 생성.

## 로컬 실행

### 의존성

```bash
# Codeception phar 다운로드 (PHP 8.4용 호스팅 artifact)
wget https://res.rhymix.org/ci/php8.4/codecept.phar
```

### MySQL 준비

```bash
mysql -uroot -e "CREATE DATABASE rhymix; CREATE USER 'rhymix'@'localhost' IDENTIFIED BY 'rhymix'; GRANT ALL ON rhymix.* TO 'rhymix'@'localhost';"
```

### Build

```bash
php codecept.phar build
```

`tests/_support/{Unit,Install}Tester.php`가 자동 생성된다.

### Run

```bash
# 모든 스위트
php codecept.phar run --debug --fail-fast

# unit만
php codecept.phar run unit

# 특정 파일
php codecept.phar run unit framework/RouterTest.php

# 특정 메서드
php codecept.phar run unit framework/RouterTest.php:testParseURL
```

### install 스위트만

```bash
php -S localhost:8000 &
php codecept.phar run install
```

## GitHub Actions

`.github/workflows/ci.yml`:

- **OS**: `ubuntu-24.04`.
- **PHP 매트릭스**: `7.4, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5`.
- **단계**:
  1. PHP 설치 (`setup-php.sh`).
  2. MySQL 준비 (`setup-mysql.sh`).
  3. **PHP Lint** — 모든 `.php`를 `php -l`로 8병렬 검사.
  4. Codeception phar 다운로드.
  5. PHP dev server 백그라운드 실행.
  6. `codecept build && codecept run --debug --fail-fast`.

### PHP Lint 명령

```bash
if find . -name "*.php" ! -path "./common/vendor/*" -print0 | xargs -0 -n 1 -P 8 php -l | grep -v "No syntax errors detected"; then exit 1; fi
```

CI(`.github/workflows/ci.yml:24`)는 위와 같이 파이프라인을 `if ... then exit 1` 래퍼로 감싼다. 안쪽 파이프라인만 떼어 실행하면 `grep -v` 특성상 exit 코드 의미가 역전되므로(에러가 있으면 grep이 출력되어 exit 0, 에러가 없으면 exit 1) 반드시 이 래퍼와 함께 사용한다.

## 저장소 포맷 설정

`.editorconfig`이 직접 강제하는 항목:

- 기본 들여쓰기(따라서 PHP 포함)는 tab.
- Python은 4-space, JSON·`.yml`·Markdown과 JSX/TSX/Svelte/Vue는 2-space. `.yaml` 확장자에는 별도 규칙이 없다.
- UTF-8, LF, final newline, 기본적으로 trailing whitespace 제거. Markdown은 hard line break를 보존하기 위해 trailing whitespace 제거 대상에서 제외.

중괄호 위치나 PHP 태그 사용 규칙은 `.editorconfig` 항목이 아니다. 그 규칙은 `CONTRIBUTING.md`가 연결하는 공식 코딩 규칙을 별도로 따른다.

## PR / 이슈

- `CONTRIBUTING.md`에 기여 가이드.
- 보안 보고: `devops@rhymix.org` (SECURITY.md). GitHub 이슈 금지.
- PR은 master 브랜치 기준.

## 디버깅

테스트 실패 시:

```bash
# 자세한 출력
php codecept.phar run unit --debug

# 단일 테스트 + step 출력
php codecept.phar run unit framework/RouterTest.php:testParseURL --debug

# 커버리지 리포트
php codecept.phar run unit --coverage --coverage-html
# → tests/_output/coverage/index.html
```

## 다음 문서

- 개요: [01-overview.md](01-overview.md)
- 인프라: [02-infrastructure.md](02-infrastructure.md)
- 보안 (보고): [19-security.md](19-security.md)
