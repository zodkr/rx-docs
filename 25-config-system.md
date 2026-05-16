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
        'type' => ['file'],
        'ttl' => 86400,
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

`config('a.b.c')` 형태로 어디서든 접근 가능. 기본값은 `getDefaults()`(`common/defaults/config.php`)에서 가져와 비교용으로 사용한다.

## 계층 구조 (`common/defaults/config.php`)

주요 카테고리:

| 키 | 의미 |
|---|---|
| `db.*` | DB 연결 정보 |
| `cache.*` | 캐시 드라이버 |
| `ftp.*` | FTP 폴백 |
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
| `queue.*` | 큐 |
| `sms.*` | SMS |
| `push.*` | 푸시 |

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

`files/config/config.php`에 직렬화 저장. 안전성을 위해:

1. 임시 파일에 먼저 쓰기.
2. 기존 파일을 `.bak`로 백업.
3. 임시 → 실제로 rename.
4. 새 파일이 PHP로 정상 로드되는지 검증.
5. 성공 시 백업 삭제, 실패 시 백업 복구.

## dot-notation

```php
config('db.master.host');           // 'localhost'
config('cache');                    // ['type'=>['file'], 'ttl'=>86400, ...]
```

## `config.user.inc.php` (코드 override)

`config/config.user.inc.php`가 존재하면 `autoload.php:141`에서 require됨. PHP 파일로 작성 — 버전 관리 친화적.

```php
<?php
// config/config.user.inc.php
config('debug.enabled', true);
config('debug.display_to', 'admin');
config('cache.type', ['file']);

// 환경 변수 활용
if (getenv('APP_ENV') === 'production') {
    config('debug.enabled', false);
    config('cache.type', ['redis', 'file']);
    config('cache.servers', [getenv('REDIS_HOST') . ':6379']);
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
config('url.lang_in_url');                      // true/false
config('url.ssl');                              // 'always'/'optional'/'none'
```

### 캐시

```php
config('cache.type');                           // ['redis', 'file']
config('cache.ttl');                            // 86400
config('cache.servers');                        // ['127.0.0.1:6379']
```

### 보안

`common/defaults/config.php`의 `security` 절은 5개 키만 가진다.

```php
config('security.x_frame_options');             // 'SAMEORIGIN'
config('security.x_content_type_options');      // 'nosniff'
config('security.robot_user_agents');           // []
config('security.nofollow');                    // false
config('security.check_csrf_token');            // false (false면 폼 토큰 검사 생략)
```

(`security.password_hashing_cost`/`security.password_hashing_algorithm`은 코어 키가 아니다 — 비밀번호 알고리즘/work factor는 `MemberModel::getMemberConfig()->password_hashing_algorithm`/`password_hashing_work_factor`에서 읽는다. [19-security.md](19-security.md) 참고.)

### 모바일

```php
config('mobile.enabled');                       // true
config('mobile.tablets');                       // false
config('mobile.viewport');                      // true
```

### 디버그

```php
config('debug.enabled');                        // false (프로덕션)
config('debug.display_to');                     // 'admin'
config('debug.allow');                          // IP 화이트리스트
config('debug.display_type');                   // ['comment', 'panel']
config('debug.log_slow_queries');               // 0.25
```

### 큐

```php
config('queue.driver');                         // 'db'/'redis'
config('queue.key');                            // HTTP 워커 인증 키
```

### 회원

```php
config('member.signup_check_email');            // true
config('member.password_strength');             // 'normal'
config('member.identifier');                    // 'user_id'/'email_address'/'both'
```

## ConfigHelper

특정 설정 그룹을 객체로:

```php
$cfg = new Rhymix\Framework\Helpers\ConfigHelper('debug');
$enabled = $cfg->enabled;
$cfg->set('enabled', true);
```

## 캐시

`Config::get`은 in-memory 캐싱되므로 반복 호출 비용이 거의 없다.

## 새 설정 키 추가

1. `common/defaults/config.php`에 기본값 추가 (코어 영역만).
2. 플러그인이라면 `config.user.inc.php`나 자체 설정 모듈로 관리 — 글로벌 키네임스페이스 충돌 주의 (`<plugin>.*` prefix 권장).

## 다음 문서

- 설치 모듈: [28-modules/install.md](28-modules/install.md)
- admin 모듈: [28-modules/admin.md](28-modules/admin.md)
