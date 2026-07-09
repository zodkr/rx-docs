# 17. 캐시와 큐

## 캐시 — `Rhymix\Framework\Cache`

`common/framework/Cache.php` (434줄). 정적 인터페이스.

### 드라이버

`common/framework/drivers/cache/` 하위 6종. 환경에 따라 자동 폴백.

| 드라이버 | 필요 환경 | 특징 |
|---|---|---|
| `apc` | ext-apcu | 단일 서버, 매우 빠름 |
| `dummy` | — | 항상 miss (디버깅) |
| `file` | — | `files/cache/store/` 디렉토리 |
| `memcached` | ext-memcached | 분산 |
| `redis` | ext-redis | 분산 + persistence |
| `sqlite` | ext-sqlite3 | 단일 파일 DB |

선택은 `config('cache.type')` (단일 드라이버 문자열). 선택한 드라이버를 사용할 수 없으면 `dummy` 드라이버로 폴백 (`redis 실패 시 file로` 같은 체인 폴백 없음).

```php
'cache' => [
    'type' => 'redis',
    'ttl' => 86400,
    'servers' => ['127.0.0.1:6379'],
    'truncate_method' => 'delete',       // 'delete' 또는 'empty'
]
```

### 정적 API

```php
Cache::init(Config::get('cache'));                              // 부트스트랩 시 자동
Cache::set(string $key, $value, int $ttl = 0, bool $force = false): bool;
$value = Cache::get(string $key);
Cache::delete(string $key): bool;
$bool = Cache::exists(string $key): bool;

// 그룹 단위 (그룹 키는 사용자가 "{group}:{key}" 형태로 직접 합성)
Cache::set("{$group}:{$key}", $value);    // 키 prefix 형식
Cache::get("{$group}:{$key}");
Cache::clearGroup(string $group_name): bool;     // 그룹 전체 무효화 (group_version 증가)
Cache::getGroupVersion(string $group_name): int; // 현재 버전 카운터

Cache::clearAll(): bool;                          // 전체 비우기

Cache::getPrefix(): string;                       // 현재 전역 prefix
Cache::getDriverName(): ?string;                  // 실제 사용 중인 드라이버 이름
```

### 그룹 무효화 메커니즘

- 각 그룹마다 `group_version` 카운터 보관.
- `clearGroup`은 키를 직접 삭제하지 않고 버전을 증가.
- 키 조회 시 `{prefix}{group}#{version}:{key}` 형식 (그룹 버전은 `{prefix}{group}#version` 키에 저장) — 옛 버전 키는 자연 만료.
- 대량 키 일괄 무효화에 효율적.

### prefix

prefix는 설정 항목이 아니라 자동 생성된다 (`cache.prefix` 같은 설정 키는 없음). 드라이버의 `$prefix` 플래그가 `true`인 분산 드라이버(`redis`/`memcached`)는 `substr(sha1(RX_BASEDIR), 0, 10) . ':' . RX_VERSION . ':'`, `file`/`dummy`는 `RX_VERSION . ':'`를 쓴다. 도메인/사이트 정보가 아니라 설치 경로(`RX_BASEDIR`) 해시 기반으로 멀티 인스턴스 키 충돌을 방지한다.

### TTL

- 기본 `config('cache.ttl')` (보통 86400 = 1일).
- `Cache::set($key, $value, 0)` — ttl에 0을 주면 기본 TTL(`config('cache.ttl')`, 보통 86400)이 적용된다 (무만료 아님).

### PSR-6 어댑터

```php
$pool = new Rhymix\Framework\Helpers\CacheItemPoolHelper();
$item = $pool->getItem('mykey');
if (!$item->isHit()) {
    $item->set($expensive_data);
    $item->expiresAfter(3600);
    $pool->save($item);
}
$data = $item->get();
```

PSR-6 호환 라이브러리(예: Symfony Cache 사용자)와 연동 시 유용.

### 캐시 truncate 방식

`config('cache.truncate_method')` — `files/cache` 폴더 정리 방식만 결정한다 (개별 키 삭제나 DB cache와 무관).

- `'delete'` (기본) — `files/cache` 폴더 전체를 `files/cache_<timestamp>`로 옮긴 뒤 재생성 (폴더 자체 삭제).
- `'empty'` — 폴더는 유지하고 내부 내용만 삭제 (마운트포인트 등 폴더 자체를 지울 수 없을 때).

## 큐 — `Rhymix\Framework\Queue`

`common/framework/Queue.php` (535줄). 비동기 작업 큐.

### 드라이버

| 드라이버 | 비고 |
|---|---|
| `db` | RDBMS (`task_queue` 테이블, 예약 작업은 `task_schedule`). 기본 |
| `redis` | Redis List(lPush/rPush·lpop/blpop) 기반 FIFO. PRIORITY_HIGH만 앞쪽 삽입 |
| `dummy` | 즉시 무시 |

예약 작업(`addTaskAt`/`addTaskAtInterval`)은 드라이버 설정과 무관하게 항상 DB 드라이버(`task_schedule` 테이블)를 사용한다.

설정 (`files/config/config.php`):

```php
'queue' => [
    'driver' => 'db',
    'key' => '...',           // HTTP 워커 인증 키 (수동 생성 권장)
],
```

### 작업 추가

`$args` / `$options`는 **단일 객체(`stdClass`)**여야 한다. 배열이 아님에 주의.

```php
use Rhymix\Framework\Queue;

// 즉시 큐 (백그라운드에서 가능한 빨리)
$task_srl = Queue::addTask(
    'My\\Class::staticMethod',         // 핸들러 (string, 필수)
    (object)['user_srl' => 42],        // ?object $args
    null,                              // ?object $options
    Queue::PRIORITY_NORMAL             // ?string $priority
);

// 특정 시각 예약 (unix timestamp)
Queue::addTaskAt(
    $unix_timestamp,
    'My\\Class::staticMethod',
    (object)['srl' => 42]
);

// 주기 반복 — crontab 구문 사용 (초 단위 아님)
Queue::addTaskAtInterval(
    '*/5 * * * *',                     // 5분마다
    'My\\Class::staticMethod',
    (object)['scope' => 'all']
);

// 0시/12시 일 2회
Queue::addTaskAtInterval('0 0,12 * * *', 'My\\Class::dailyReport');
```

### 핸들러 형식

`Queue.php:112-115`의 docblock에 정의된 4개 형식만 지원된다.

| 형식 | 예 |
|---|---|
| 글로벌 함수 | `'doSomething'` |
| 정적 메서드 | `'My\\Class::staticMethodName'` |
| 싱글톤 메서드 | `'My\\Class::getInstance()->methodName'` |
| 새 인스턴스 메서드 | `'new My\\Class()->methodName'` |

핸들러는 호출 시 `$args`와 `$options`를 그대로 받는다. 반환값은 무시되며 예외는 로깅된다.

### 우선순위 상수

```php
Queue::PRIORITY_HIGH    // 'high'
Queue::PRIORITY_NORMAL  // 'normal'
Queue::PRIORITY_LOW     // 'low'
```

### 예약 작업 관리

```php
$info = Queue::getScheduledTask($task_srl);       // ?object
$ok = Queue::cancelScheduledTask($task_srl);      // bool
```

### 워커 — `common/scripts/cron.php`

큐 워커는 cron으로 주기 실행한다.

```bash
# /etc/crontab 또는 crontab -e
* * * * * /usr/bin/php /var/www/rhymix/index.php common.cron
```

워커는 내부적으로 `Queue::process($index, $count, $timeout)`을 호출해 timeout(초)까지 큐를 비운다. `RXQUEUE_CRON` 상수가 정의된 상태로 실행된다.

또는 HTTP로 `cron.php`를 **직접** 호출 가능 (별도 모듈 액션 없음 — 스크립트 자체가 진입점):

```
GET https://example.com/common/scripts/cron.php?key=<config('queue.key')>
```

CLI가 아닐 때 cron.php는 자체적으로 `autoload.php`를 require하고 `Context::init()`을 호출한 뒤 `Context::get('key')`로 읽은 키를 `Queue::checkKey()`로 검증한다. 키 불일치 시 403 응답.

관리자 → 시스템 → 큐 설정 화면에 위 URL이 자동 생성된다 (`modules/admin/tpl/config_queue.html:130`).

### 시그널 처리

CLI 모드에서 SIGTERM/SIGINT 수신 시 현재 작업 완료 후 안전 종료. `pcntl_*` 함수 필요.

### 키 인증

`cron.php`를 HTTP로 호출할 때 `key` 파라미터를 `config('queue.key')`와 비교. 미일치 시 403.

```php
$ok = Rhymix\Framework\Queue::checkKey((string)Context::get('key'));
```

키는 16자 이상, 영숫자만 가능. 관리자 화면에서 자동 발급/회전.

### cron 설치 예시

#### Linux (cron)

```bash
* * * * * php /var/www/rhymix/index.php common.cron > /dev/null 2>&1
```

#### Plesk Scheduled Tasks

- 실행 명령: `php /var/www/vhosts/.../httpdocs/index.php common.cron`
- 주기: 매분.

#### cPanel Cron Jobs

- `* * * * * cd /home/user/public_html && /usr/local/bin/php index.php common.cron`

#### HTTP (cron 없을 때)

외부 서비스(uptimerobot 등)에서 매분 다음 URL 호출 — `cron.php`를 **직접** 호출:

```
https://yoursite.com/common/scripts/cron.php?key=YOURKEY
```

`config('queue.key')`는 관리자 → 시스템 → 큐 설정에서 발급(16자 이상 영숫자).

### 큐 작업 상태

- 활성 작업: `task_queue` 테이블의 행 (예약 작업은 `task_schedule` 테이블).
- 작업은 dequeue(`getNextTask`) 시점에 fetch와 동시에 즉시 삭제된다 — 실행 전 삭제이며 재시도/dead letter 기능은 없다 (`task_queue`에 `attempts` 컬럼 없음: id/handler/args/options/regdate만 존재).
- 실행 중 예외는 `error_log`에 기록만 되고 작업은 그대로 폐기된다.

## 캐시 vs 큐 선택 기준

| 상황 | 권장 |
|---|---|
| 자주 조회되는 데이터 | 캐시 |
| 무거운 계산 결과 | 캐시 |
| 이메일/푸시 발송 | 큐 |
| 외부 API 호출 (즉시 응답 불필요) | 큐 |
| 통계 집계 | 큐 (주기 실행 — `addTaskAtInterval`) |
| 검색 인덱스 갱신 | 큐 |

## 캐시 무효화 패턴

```php
// 모듈에서
function getBoardInfo($module_srl) {
    $key = "board:info:{$module_srl}";
    if ($info = Cache::get($key)) {
        return $info;
    }
    $info = executeQuery('board.getBoard', (object)['module_srl' => $module_srl])->data;
    Cache::set($key, $info, 3600);
    return $info;
}

function updateBoardInfo($module_srl, $args) {
    executeQuery('board.updateBoard', $args);
    Cache::delete("board:info:{$module_srl}");      // 또는 Cache::clearGroup("board:{$module_srl}")
}
```

## 다음 문서

- 메일/SMS/푸시 (큐와 자주 결합): [18-mail-sms-push.md](18-mail-sms-push.md)
- CLI 스크립트: [21-cli-and-scripts.md](21-cli-and-scripts.md)
- 설정 시스템: [25-config-system.md](25-config-system.md)
