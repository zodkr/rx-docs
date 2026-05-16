# 24. 디버그와 로깅

`Rhymix\Framework\Debug` (`common/framework/Debug.php`, 996줄)이 모든 디버그/로깅을 담당한다.

## 활성화

`config('debug.enabled')` + IP 화이트리스트(`config('debug.allow')`) 또는 `display_to=admin`.

```php
'debug' => [
    'enabled' => true,
    'display_to' => 'admin',        // 'admin' / 'everyone'
    'allow' => ['127.0.0.1', '192.168.0.0/16'],
    'display_type' => ['comment', 'panel'],
    'display_content' => ['errors', 'queries', 'slow_queries', 'slow_triggers', 'entries', 'request_info'],
    'log_slow_queries' => 0.25,
    'log_slow_triggers' => 0.25,
    'log_slow_widgets' => 0.25,
    'log_slow_remote_requests' => 1.25,
    'write_error_log' => 'fatal',   // 'none'/'fatal'/'all'
    'log_filename' => null,         // null = files/cache/debug.log
    'query_comment' => false,
    'query_full_stack' => false,
]
```

## 표시 위치 (`display_type`)

- `comment` — HTML 끝에 `<!-- ... -->` 주석으로 삽입.
- `panel` — 우하단 고정 디버그 패널 (`common/js/debug.js` + CSS).
- `file` — `log_filename`에 기록 (응답에 표시 안 함).

복수 지정 가능 (`['comment', 'panel']`).

## 표시 내용 (`display_content`)

| 항목 | 의미 |
|---|---|
| `request_info` | URL, 메서드, 파라미터, 헤더 |
| `entries` | `Debug::addEntry`로 추가된 메시지 |
| `errors` | PHP 에러/예외 |
| `queries` | 모든 SQL 쿼리 + 실행 시간 |
| `slow_queries` | 임계 초과 쿼리만 |
| `slow_triggers` | 임계 초과 트리거 |
| `slow_widgets` | 임계 초과 위젯 |
| `slow_remote_requests` | 임계 초과 외부 HTTP |

## 에러 처리

`Debug::registerErrorHandlers($level)` (`common/autoload.php:149`)가:

- `set_error_handler` — Warning/Notice를 캡처.
- `set_exception_handler` — uncaught 예외 처리.
- `register_shutdown_function` — fatal error 캡처.

캡처된 에러는:
- 디버그 활성 사용자에게 화면 표시 (또는 주석).
- `write_error_log` 옵션에 따라 PHP error_log 또는 파일로 기록.

## PHP error_log 동작

`config('debug.write_error_log')`:

| 값 | 동작 |
|---|---|
| `'none'` | error_log 미사용 |
| `'fatal'` (기본) | E_ERROR/E_PARSE/E_CORE_ERROR/E_COMPILE_ERROR만 |
| `'all'` | 모든 에러 |

기록 위치: PHP ini의 `error_log` 또는 `log_filename`.

## 쿼리 로깅

### 모든 쿼리 + 실행 시간

`display_content`에 `queries` 포함 시. 각 쿼리는:

```
SELECT ... [3.45ms]
  caller: BoardModel::getDocumentList (modules/board/board.model.php:152)
```

### 슬로우 쿼리만

`display_content`에 `slow_queries`. 임계 `log_slow_queries` (초).

### SQL 주석

`config('debug.query_comment')` = true:

```sql
SELECT * FROM rx_documents WHERE document_srl = 123
/* PHP File: modules/board/board.controller.php; Caller: BoardController->procBoardInsertDocument */
```

### 전체 스택

`config('debug.query_full_stack')` = true: 호출 스택 전체를 주석에.

### 쿼리 로그 조회

```php
$queries = Rhymix\Framework\Debug::getQueries();  // 누적된 쿼리 배열
$errors  = Rhymix\Framework\Debug::getErrors();
$entries = Rhymix\Framework\Debug::getEntries();
$triggers = Rhymix\Framework\Debug::getTriggers();
```

## 트리거 로깅

```php
Rhymix\Framework\Debug::addTrigger(array $trigger): void;
// $trigger = ['name' => 'document.insertDocument.after', 'target' => ..., 'target_plugin' => ..., 'elapsed_time' => 0.012]
```

`display_content`에 `slow_triggers` 포함 시 임계 초과만 표시. `ModuleHandler::triggerCall`이 자동 호출한다.

## 위젯 로깅

```php
Rhymix\Framework\Debug::addWidget(array $widget): void;
```

## 시간 측정 / 사용자 정의 entry

```php
Rhymix\Framework\Debug::addTime(string $type, float $time): void;  // type='template'/'db'/...
Rhymix\Framework\Debug::addEntry($message): void;                  // entries 누적
Rhymix\Framework\Debug::addQuery(array $query): void;
```

`entries` 표시 시 출력.

## 디버그 모드 확인

```php
if (Rhymix\Framework\Debug::isEnabledForCurrentUser()) {
    // 디버그 출력
}
```

내부에서 IP/관리자 검증을 수행.

## 디버그 자체 비활성

CLI 모드는 `index.php:65`에서 `Debug::disable()`이 호출되어 핸들러가 minimal 모드.

```php
Rhymix\Framework\Debug::disable();
```

## 로그 파일 위치

`config('debug.log_filename')`:

- `null` → `files/cache/debug.log`.
- 사용자 정의 가능.

회전: 외부 logrotate 권장. `common/scripts/clean_old_logs.php`로 mtime 기반 정리 가능.

## 외부 시스템 연동

별도의 `common.flushDebugInfo`/`common.writeSlowlog` 트리거는 존재하지 않는다 — Debug는 자체 정적 배열(`$_triggers`/`$_slow_triggers`/`$_queries` 등)에 누적 후 `DisplayHandler::getDebugInfo()`가 직접 출력/로그 파일에 기록한다.

외부 시스템(Sentry/Datadog 등)으로 보내려면 `Debug::registerErrorHandlers`가 등록하는 PHP shutdown 핸들러나 `display.after`/`moduleHandler.proc.after` 같은 라이프사이클 트리거에서 직접 송신한다.

## 디버그 비활성 시 동작

- 에러 핸들러는 등록되지만 사용자에게 노출되지 않음.
- 응답에 디버그 정보 누설 안 함.
- 슬로우 쿼리/트리거는 `log_filename`이 설정되어 있으면 기록됨.

## 슬로우 로그 분석

`log_slow_*` 옵션을 활성화한 채 운영하면 `files/cache/debug.log`에 슬로우 항목이 누적된다. 정기적으로 살펴 병목을 찾는 패턴 유용.

## 디버그 패널 (panel)

`common/js/debug.js` + `common/css/debug.css`가 우하단 토글 패널을 그린다. 관리자 화면에서 매우 유용 — 쿼리/트리거/메모리 사용량 한눈에 파악.

## 환경별 권장

| 환경 | 권장 설정 |
|---|---|
| 로컬 개발 | `enabled=true`, `display_type=panel`, `display_content` 전체 |
| 스테이징 | `enabled=true`, `display_to=admin`, IP 화이트리스트 |
| 프로덕션 | `enabled=false`, `log_slow_*` 활성, `write_error_log=fatal` |

## 다음 문서

- 설정: [25-config-system.md](25-config-system.md)
- 트리거: [13-event-and-trigger-system.md](13-event-and-trigger-system.md)
- 쿼리: [14-database-and-queries.md](14-database-and-queries.md)
