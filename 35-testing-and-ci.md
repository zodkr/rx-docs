# 35. 테스팅과 CI

## Codeception

Rhymix는 **Codeception 5.x** 기반 테스트를 사용한다. composer dev 의존성이 아니라 **`.phar` 파일을 다운로드**해 실행한다.

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

설치 시나리오 + autoinstall 등 통합 테스트.

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
# Codeception phar 다운로드 (PHP 버전 맞춤)
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

## 코딩 표준

`.editorconfig`:

- **PHP**: tabs, BSD-style braces, `<?php` only (short tag 금지).
- **JSON/YAML/Markdown**: 2-space indent.
- **JS framework files**: 2-space indent.
- UTF-8, LF, trim trailing whitespace, final newline.

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
