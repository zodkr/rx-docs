# 02. 인프라스트럭처 요구사항

Rhymix를 실행/배포할 때 필요한 PHP 환경, DB, 드라이버, 웹서버 설정을 정리한다.

## PHP

- 최소: **7.4** (`common/autoload.php:14-19`에서 강제 체크).
- CI 매트릭스: **7.4 ~ 8.5** (`.github/workflows/ci.yml`).
- composer 명목상 `>=7.2.5`로 적혀 있으나 (`common/composer.json:17`) 런타임 체크가 우선한다.

### 필수 PHP 확장 (`common/composer.json:18-25`)

| 확장 | 용도 |
|---|---|
| `ext-curl` | HTTP/푸시/외부 API |
| `ext-gd` | 이미지 리사이즈/썸네일 |
| `ext-iconv` | 인코딩 변환 |
| `ext-json` | JSON 응답/큐 페이로드 |
| `ext-mbstring` | 멀티바이트 문자열 |
| `ext-openssl` | TLS, 암호화 |
| `ext-pcre` | 정규식 |
| `ext-xml` | XML 메타/쿼리 파싱 |

권장 추가 확장: `ext-mysqli` 또는 `ext-pdo_mysql` (DB 접속), `ext-mbstring`, `ext-zip`(설치/업데이트), `ext-fileinfo`(파일 타입 검출), `ext-bcmath`, `ext-intl`.

### PHP ini 권장값

| 항목 | 권장값 | 참고 |
|---|---|---|
| `memory_limit` | 128M ~ 256M | 큰 파일/일괄 작업 시 |
| `post_max_size` | 32M ~ | 첨부 업로드 한도 |
| `upload_max_filesize` | 32M ~ | 위와 일치 |
| `max_execution_time` | 60 ~ 300 | 큐/일괄 처리 |
| `default_charset` | `UTF-8` | autoload에서 강제 (`common/autoload.php:34`) |

## 데이터베이스

- **공식 지원**: MySQL 5.5+ / MariaDB 10.0+.
- 드라이버: `common/framework/DB.php` — PDO MySQL 기반, prefix 자동 적용, prepared statement.
- 설치 모듈(`modules/install/`)이 초기 스키마를 생성한다.

테이블 prefix는 `db.master.prefix` 설정(기본 `rx_`). 멀티 마스터/슬레이브 분리는 `DB::getInstance($type)` 인자로 지원하지만 기본 단일 마스터로 동작한다.

## 드라이버 (자동 폴백)

런타임에 환경에 맞게 선택되며, 가용성 검사 후 자동 폴백된다.

### 캐시 (`common/framework/drivers/cache/`)

| 드라이버 | 비고 |
|---|---|
| `apc` | APCu 기반, 단일 서버 |
| `dummy` | 항상 cache miss (디버깅/비활성화) |
| `file` | `files/cache/store/` 디렉토리 사용 |
| `memcached` | `ext-memcached` 필요 |
| `redis` | `ext-redis` 필요 |
| `sqlite` | `ext-sqlite3` 필요 |

### 메일 (`common/framework/drivers/mail/`)

| 드라이버 | 비고 |
|---|---|
| `mailfunction` | PHP `mail()` 사용 |
| `smtp` | SwiftMailer SMTP |
| `sendgrid`, `mailgun`, `mandrill`, `postmark`, `ses`, `sparkpost`, `brevo` | 외부 SaaS API |
| `ncloud_mailer`, `woorimail` | 국내 SaaS |
| `dummy` | 송신 안 함 (개발용) |

### SMS (`common/framework/drivers/sms/`)

| 드라이버 | 비고 |
|---|---|
| `coolsms`, `twilio`, `solapi`, `iwinv`, `ncloud_sens`, `ppurio` | 외부 SaaS |
| `dummy` | 송신 안 함 |

### 푸시 (`common/framework/drivers/push/`)

| 드라이버 | 비고 |
|---|---|
| `apns` | Apple Push Notification Service |
| `fcm` | Firebase Cloud Messaging (legacy) |
| `fcmv1` | FCM HTTP v1 API |

### 큐 (`common/framework/drivers/queue/`)

| 드라이버 | 비고 |
|---|---|
| `db` | RDBMS 백엔드 (기본) |
| `redis` | Redis List 기반 (lPush/rPush, lpop/blpop) |
| `dummy` | 즉시 무시 |

## 웹서버

### Apache

루트의 `.htaccess`가 다음을 처리한다 (요지).

- `index.php`로 모든 요청 라우팅.
- `.git`, `.ht*`, `composer.*` 차단.
- `files/`(attach·config·cache 내 실행형 확장자), 보호 디렉토리(addons·modules·themes·widgets 등)의 `.html`/`.xml`/`.blade.php` 차단.

### nginx

샘플 설정 2종:

- `common/manual/server_config/rhymix-nginx.conf` — 단독 도메인.
- `common/manual/server_config/rhymix-nginx-subdir.conf` — 서브 디렉토리 설치.

각 파일에 보호 패턴(`location ~ ^/(\.git|\.ht|\.travis|codeception\.|composer\.|...)`로 dotfile/설정파일 차단, `location ~ ^/files/(attach|config|cache)/.+\.(ph(p|t|ar)?[0-9]?|p?html?|cgi|pl|exe|[aj]spx?|inc|bak)$`로 업로드 디렉토리 내 실행형 파일 차단, `location ~ ^/(addons|common/tpl|modules|themes|widgets|...)/.+\.(html|xml|blade\.php)$` 등)이 포함된다.

## 설정 파일

| 파일 | 역할 | 커밋 여부 |
|---|---|---|
| `config/config.inc.php` | autoload 진입점 (얇은 brigde) | 커밋됨 |
| `files/config/config.php` | 런타임 설정 — DB/캐시/메일/보안 등 | gitignore |
| `config/config.user.inc.php` | 코드 기반 설정 override | gitignore |
| `files/config/db.config.php` | XE 호환용 더미 | gitignore |
| `files/config/ftp.config.php` | XE 호환용 더미 | gitignore |

설정 시스템 상세는 [25-config-system.md](25-config-system.md) 참고.

## 권장 디렉토리 권한

- `files/`: 웹서버 사용자가 쓰기 가능 (보통 0755 디렉토리 + 0644 파일).
- umask: `config('file.umask')` 값을 8진수로 해석해 사용한다 (`common/framework/Storage.php:920-927`). 미설정 시 `0`(umask 적용 안 함). 설치 환경에 적절한 값은 `Storage::recommendUmask()`(`:940-`)가 제안한다 — Windows면 `0000`, 그 외엔 파일 소유자 UID(`fileowner(__FILE__)`)와 PHP 프로세스 UID(`getServerUID()`)가 같으면 `0022`, 다르면 `0000`.

런타임 생성 디렉토리는 [03-directory-structure.md](03-directory-structure.md)의 `files/` 절 참고.

## CLI 모드

`index.php:57-67`에서 `PHP_SAPI === 'cli'` 분기:

```bash
php index.php <plugin>.<script>
```

예시:

```bash
php index.php common.cron                       # 큐 워커
php index.php common.clean_old_logs             # 오래된 로그 정리
php index.php module.updateAllModules           # 모든 모듈 업데이트
```

상세: [21-cli-and-scripts.md](21-cli-and-scripts.md).

## OS 호환성

- **권장**: 리눅스. macOS도 개발용으로 OK.
- 윈도우 분기: `common/constants.php:128`의 `RX_WINDOWS` 상수가 `PHP_OS_FAMILY === 'Windows'` 기준으로 정의되며, 경로 정규화 등에서 참조된다.

## CloudFlare/리버스 프록시

- 클라이언트 IP: `HTTP_CF_CONNECTING_IP`가 있으면 `IpFilter::getCloudFlareRealIP()`로 `REMOTE_ADDR`을 실제 IP로 덮어쓴 뒤 정규 분기 진행 (`common/constants.php:59-83`).
- HTTPS: `$_SERVER['HTTPS']`(`off`가 아님), `HTTP_X_FORWARDED_PROTO=https`, `HTTP_X_FORWARDED_SSL=on`, `HTTP_CF_VISITOR`에 `https`, 또는 `SERVER_PORT=443` 중 하나로 `RX_SSL` 자동 감지 (`common/constants.php:88-111`).

## 다음 문서

- 디렉토리 트리: [03-directory-structure.md](03-directory-structure.md)
- 설치 모듈: [28-modules/install.md](28-modules/install.md)
