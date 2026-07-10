# 25. 설정 시스템

`Rhymix\Framework\Config` (`common/framework/Config.php`, 209줄)가 모든 시스템 설정을 관리한다.

## 저장 형식

`files/config/config.php` — PHP array 직렬화. 예:

```php
<?php
return [
    'db' => [
        'master' => [
            'type' => 'mysql',
            'host' => 'localhost',
            'port' => 3306,
            'user' => 'rhymix',
            'pass' => '...',
            'database' => 'rhymix',
            'prefix' => 'rx_',
            'charset' => 'utf8mb4',
            'engine' => 'innodb',
        ],
    ],
    'cache' => [
        'type' => 'redis',
        'ttl' => 86400,
        'servers' => ['redis://127.0.0.1:6379#0'],
    ],
    // ...
];
```

`Config::serialize()`(`common/framework/Config.php:186`)가 `var_export` 결과를 정리해 저장한다.

## 진입점

1. **`config/config.inc.php`** — autoloader 진입. 거의 비어있음 (bridge).
2. **`files/config/config.php`** — 런타임 설정. gitignore.
3. **`config/config.user.inc.php`** — 코드 기반 override. gitignore. 옵션.

## 부트스트랩

`Config::init()` (`common/framework/Config.php:29`, `common/autoload.php:136`에서 호출):

1. `files/config/config.php`가 있으면 그대로 로드 (사용자 설정이 우선).
2. 없으면 `Parsers\ConfigParser::convert()`로 옛 XE 형식을 변환 후 `save()`로 신규 형식 저장.
3. 결과에 `namespaces` 키가 있으면 `$GLOBALS['RX_NAMESPACES']`에 매핑.

`config('a.b.c')` 형태로 어디서든 접근 가능. `getDefaults()`(`common/defaults/config.php`)가 반환하는 기본값은 설치 시 초기 설정 시드로만 사용된다 (`modules/install/install.controller.php:112`). `Config::get`은 기본값으로 폴백하지 않으며, 미설정 키는 `null`을 반환한다.

## 계층 구조 (`common/defaults/config.php`)

주요 카테고리:

| 키 | 의미 |
|---|---|
| `config_version` | 설정 파일 스키마 버전 (`'2.0'`) |
| `db.*` | DB 연결 정보 |
| `cache.*` | 캐시 드라이버 |
| `ftp.*` | XE 호환용 legacy 기본값 (현재 코어와 Storage 쓰기 폴백에서 사용하지 않음) |
| `crypto.*` | 암호화 키 |
| `locale.*` | 시간대, 언어 |
| `url.*` | 라우팅, 도메인 |
| `session.*` | 세션 |
| `cookie.*` | 쿠키 정책 |
| `file.*` | 파일 업로드 |
| `mail.*` | 메일 |
| `view.*` | 출력 / minify |
| `admin.*` | 관리자 보호 |
| `lock.*` | 사이트 잠금 |
| `debug.*` | 디버그 |
| `seo.*` | SEO 헤더 |
| `mediafilter.*` | 임베드 필터 |
| `security.*` | 보안 헤더 |
| `mobile.*` | 모바일 감지 |
| `namespaces.*` | 외부 plugin namespace 매핑 |
| `use_rewrite` | rewrite 사용 여부 |
| `other.*` | 기타 (`proxy` 등) |

`queue.*`/`sms.*`/`push.*`는 defaults 파일에 정의되어 있지 않고, 런타임에 admin/모듈이 설정하는 그룹이다.

## API

### get

```php
$value = Rhymix\Framework\Config::get('db.master.host');
$value = config('cache.ttl');                              // 헬퍼
$all = Rhymix\Framework\Config::getAll();
$defaults = Rhymix\Framework\Config::getDefaults();
```

### set

```php
Rhymix\Framework\Config::set('cache.ttl', 3600);
config('cache.ttl', 3600);                                 // 헬퍼

// 메모리에만 반영됨 → 영구화하려면 save() 호출
Rhymix\Framework\Config::save();
```

### save

`files/config/config.php`에 직렬화 저장 (`common/framework/Config.php:137`):

1. 기존 `config.php`가 있으면 `config.php.backup.<시각>.php`로 복사 백업하고 원본과 크기가 일치하는지 확인 (불일치 시 `false` 반환·중단).
2. 직렬화한 설정을 `Storage::write()`로 기록하고, 기록된 크기가 예상과 일치하는지 확인 (불일치·실패 시 `false` 반환). `Storage::write()`는 일반적인 조건에서 임시 파일+rename을 사용한다.
3. 성공 시 백업 파일 삭제.
4. XE 호환 더미 파일 `files/config/db.config.php`·`files/config/ftp.config.php`를 경고 주석과 함께 갱신.

(PHP 로드 검증과 실패 시 백업 자동 복구는 하지 않는다. 쓰기 실패 시 남은 backup 파일은 수동 복구에 활용할 수 있다.)

## dot-notation

```php
config('db.master.host');           // 'localhost'
config('cache');                    // ['type'=>'redis', 'ttl'=>86400, ...]
```

## `config.user.inc.php` (코드 override)

`config/config.user.inc.php`가 존재하면 `autoload.php:141-143`에서 require됨. PHP 파일로 작성 — 버전 관리 친화적.

```php
<?php
// config/config.user.inc.php
config('debug.enabled', true);
config('debug.display_to', 'admin');
config('cache.type', 'redis');

// 환경 변수 활용
if (getenv('APP_ENV') === 'production') {
    config('debug.enabled', false);
    config('cache.type', 'redis');
    config('cache.servers', ['redis://' . getenv('REDIS_HOST') . ':6379#0']);
}
```

장점:
- 비밀번호/키를 코드에서 분리해 ENV로.
- 환경별 설정 분기.
- Git에 안 들어감 (gitignore).

단점:
- 관리자 UI에서 변경한 값이 무시될 수 있음 (overwritten).

## XE 호환 더미 파일

다음 두 파일은 비어있는 더미로 유지된다 (XE 시절 코드 호환).

- `files/config/db.config.php`
- `files/config/ftp.config.php`

실제 설정은 `config.php`에 통합되어 있다.

## 자주 보는 설정 항목

### DB

```php
config('db.master.type');         // 'mysql'
config('db.master.prefix');       // 'rx_'
config('db.master.charset');      // 'utf8mb4'
```

### URL

```php
config('url.rewrite');                          // 0/1/2
config('url.unregistered_domain_action');       // 'redirect_301'/...
config('url.ssl');                              // 'always'/'optional'/'none'
```

### 캐시

```php
config('cache.type');                           // 'apc'/'dummy'/'memcached'/'redis'/'sqlite' 중 하나
config('cache.ttl');                            // 86400
config('cache.servers');                        // ['redis://127.0.0.1:6379#0']
```

### 보안

`common/defaults/config.php`의 `security` 절은 5개 키만 가진다.

```php
config('security.x_frame_options');             // 'SAMEORIGIN'
config('security.x_content_type_options');      // 'nosniff'
config('security.robot_user_agents');           // []
config('security.nofollow');                    // false
config('security.check_csrf_token');            // false (토큰 검사만 생략, same-origin 검사는 계속)
```

(`security.password_hashing_cost`/`security.password_hashing_algorithm`은 코어 키가 아니다 — 비밀번호 알고리즘/work factor는 `MemberModel::getMemberConfig()->password_hashing_algorithm`/`password_hashing_work_factor`에서 읽는다. [19-security.md](19-security.md) 참고.)

### 모바일

```php
config('mobile.enabled');                       // true
config('mobile.tablets');                       // false
config('mobile.viewport');                      // 'width=device-width, initial-scale=1.0, user-scalable=yes'
```

### 디버그

```php
config('debug.enabled');                        // true (common/defaults의 초기 기본값, 운영에서는 false 권장)
config('debug.display_to');                     // 'admin'
config('debug.allow');                          // IP 화이트리스트
config('debug.display_type');                   // ['comment'] (초기 기본값, 복수 지정 가능)
config('debug.log_slow_queries');               // 0.25
```

### 큐

```php
config('queue.enabled');                        // 비동기 알림/예약 작업 활성 여부
config('queue.driver');                         // 'db'/'redis'/'dummy'
config('queue.key');                            // HTTP 워커 인증 키
config('queue.interval');                       // 워커 실행 간격(분)
config('queue.process_count');                  // CLI 워커 프로세스 수
config('queue.display_errors');                 // HTTP 워커 오류 표시 여부
config('queue.redis');                          // Redis 선택 시 host/port/dbnum 등
```

### 회원

회원 설정은 시스템 config가 아니라 모듈 설정이므로 `config('member.*')`가 아니라 `MemberModel::getMemberConfig()`(내부적으로 `ModuleModel::getModuleConfig('member')`)로 접근한다 (`modules/member/member.model.php:29`).

```php
$mconf = MemberModel::getMemberConfig();
$mconf->password_strength;   // 'normal'
$mconf->identifiers;         // 로그인 식별자 배열. 기본 ['user_id', 'email_address'], phone_number도 가능
$mconf->identifier;          // 하위 호환용 대표 식별자(user_id/email_address)로 계산된 값
$mconf->enable_confirm;      // 'Y'/'N' (이메일 인증 — signup_check_email 키는 없음)
```

## ConfigHelper

`ConfigHelper::consolidate($format)` (`common/framework/helpers/ConfigHelper.php:24`) — module.xml 등의 설정 포맷 배열을 받아 `common:키`(시스템 config)/`<module>:키`(`getModuleConfig`) 참조와 필터 함수(`strtolower` 등 함수명)를 적용해 여러 소스에서 값을 취합하는 정적 메서드다. 생성자·인스턴스 프로퍼티·`set()`은 없다.

```php
$values = Rhymix\Framework\Helpers\ConfigHelper::consolidate([
    'foo' => ['common:debug.enabled'],   // 시스템 config에서 취합
    'bar' => ['member:enable_join'],     // member 모듈 설정에서 취합
]);
```

## 캐시

`Config::get`은 in-memory 캐싱되므로 반복 호출 비용이 거의 없다.

## 새 설정 키 추가

1. `common/defaults/config.php`에 기본값 추가 (코어 영역만).
2. 플러그인이라면 `config.user.inc.php`나 자체 설정 모듈로 관리 — 글로벌 키네임스페이스 충돌 주의 (`<plugin>.*` prefix 권장).

## 다음 문서

- 설치 모듈: [28-modules/install.md](28-modules/install.md)
- admin 모듈: [28-modules/admin.md](28-modules/admin.md)
