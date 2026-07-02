# 21. CLI 모드와 스크립트

`index.php`는 `PHP_SAPI === 'cli'`일 때 `ModuleHandler::procCommandLineArguments($argv)`로 분기한다 (`index.php:57-67`).

## CLI 호출 형식

```bash
php index.php <plugin>.<script>
```

`<plugin>` = `common` 또는 모듈명. `<script>` = 디렉토리 내 스크립트 파일명(확장자 제외).

경로 규칙 (`ModuleHandler.class.php:1236`):

```
common.<name>    → common/scripts/<name>.php
<module>.<name>  → modules/<module>/scripts/<name>.php
```

자동으로 `common/scripts/common.php`가 먼저 require되어 부트스트랩이 완성된다 (`:1243`).

## 동봉 스크립트

### common/scripts/

| 스크립트 | 호출 | 용도 |
|---|---|---|
| `cron.php` | `php index.php common.cron` | 큐 워커 (예약 작업 실행) |
| `clean_empty_dirs.php` | `php index.php common.clean_empty_dirs` | **@deprecated** — `file.cleanEmptyDirs` wrapper (빈 첨부 디렉토리 정리) |
| `clean_garbage_files.php` | `php index.php common.clean_garbage_files` | **@deprecated** — `file.cleanGarbageFiles` wrapper (고아 첨부 파일 정리) |
| `clean_message_files.php` | `php index.php common.clean_message_files` | **@deprecated** — `communication.cleanMessageFiles` wrapper (메시지 첨부 정리) |
| `clean_old_logs.php` | `php index.php common.clean_old_logs` | **@deprecated** — `module.cleanMiscLogs` wrapper (오래된 로그 정리) |
| `clean_old_notifications.php` | `php index.php common.clean_old_notifications` | **@deprecated** — `ncenterlite.cleanNotifications` wrapper (알림 정리) |
| `clean_old_thumbnails.php` | `php index.php common.clean_old_thumbnails` | **@deprecated** — `file.cleanThumbnails` wrapper (썸네일 캐시 정리) |
| `update_all_modules.php` | `php index.php common.update_all_modules` | **@deprecated** — `module.updateAllModules` wrapper (모든 모듈 일괄 업데이트) |

### 모듈 스크립트

| 스크립트 | 호출 |
|---|---|
| `modules/module/scripts/cleanMiscLogs.php` | `php index.php module.cleanMiscLogs` |
| `modules/module/scripts/updateAllModules.php` | `php index.php module.updateAllModules` |
| `modules/file/scripts/cleanEmptyDirs.php` | `php index.php file.cleanEmptyDirs` |
| `modules/file/scripts/cleanGarbageFiles.php` | `php index.php file.cleanGarbageFiles` |
| `modules/file/scripts/cleanThumbnails.php` | `php index.php file.cleanThumbnails` |
| `modules/communication/scripts/cleanMessageFiles.php` | `php index.php communication.cleanMessageFiles` |

(`cron.php`를 제외한 `common/scripts` 스크립트는 모두 `@deprecated`된 wrapper이며, 대응 모듈 스크립트를 직접 부르는 것과 동등하다. 각 파일 docblock이 권장 호출을 지시한다. 신규 cron 등록에는 위 모듈 스크립트를 직접 사용한다.)

## cron 등록

### 매분 큐 워커

```cron
* * * * * /usr/bin/php /var/www/rhymix/index.php common.cron > /dev/null 2>&1
```

### 매일 새벽 정리

```cron
0 4 * * * /usr/bin/php /var/www/rhymix/index.php module.cleanMiscLogs > /dev/null 2>&1
30 4 * * * /usr/bin/php /var/www/rhymix/index.php file.cleanGarbageFiles > /dev/null 2>&1
0 5 * * * /usr/bin/php /var/www/rhymix/index.php file.cleanThumbnails > /dev/null 2>&1
```

### 매주

```cron
0 6 * * 0 /usr/bin/php /var/www/rhymix/index.php file.cleanEmptyDirs
```

### HTTP 폴백 (cron 없을 때)

외부 모니터링 서비스에서 매분 호출 — `cron.php`를 **직접** 호출 (별도 모듈 액션 없음):

```
https://example.com/common/scripts/cron.php?key=<config('queue.key')>
```

`config('queue.key')`는 관리자 → 시스템 → 큐 설정에서 발급(16자 이상 영숫자). cron.php가 CLI가 아닐 때 자체적으로 `autoload.php`/`Context::init()`을 부르고 `Queue::checkKey()`로 키를 검증한다 (`common/scripts/cron.php`).

## cron.php 동작

`common/scripts/cron.php`는 다음 작업을 수행한다:

1. `RXQUEUE_CRON` 상수 정의 (큐 워커 모드 마커).
2. 시그널 핸들러 등록 (SIGINT/SIGHUP/SIGTERM/SIGQUIT/SIGUSR1/SIGUSR2 → 안전 종료) — CLI 전용 (`cron.php:60`).
3. `Rhymix\Framework\Queue::process($index, $count, $timeout)` 호출 — timeout(초)까지 큐 처리.

핵심 큐 처리(`Queue::process`)는 CLI/HTTP 동일하다. 다만 시그널 핸들러 등록(`cron.php:60`)과 멀티프로세스 fork(`cron.php:73`, `process_count > 1`일 때)는 CLI 전용이며, HTTP 호출 시에는 이 둘을 건너뛰고 단일 프로세스 `Queue::process(0, 1, $timeout)`(`cron.php:116`)만 실행한다. HTTP의 경우 `key` 인증 필수. 정상 처리 결과를 stderr로 로깅하는 단계는 없고, fork 실패(`RxQueue: could not fork!`)나 태스크 핸들러 오류만 `error_log`에 남는다.

## 새 스크립트 작성

### 위치

- 코어 영역: `common/scripts/` (보통 코어 PR로만).
- 모듈 영역: `modules/<module>/scripts/`.
- 플러그인 영역: 자체 `<plugin>/scripts/`.

### 템플릿

```php
<?php
// common/scripts/my_script.php

// RX_VERSION은 부트스트랩이 끝난 상태에서만 정의됨.
if (!defined('RX_VERSION')) {
    exit;
}

// 작업 수행
$db = Rhymix\Framework\DB::getInstance();
$result = $db->query("SELECT COUNT(*) FROM `documents`")->fetch(PDO::FETCH_COLUMN);
echo "총 문서 수: {$result}\n";

// 모듈 인스턴스 사용 가능
$oDocumentModel = getModel('document');
$list = $oDocumentModel->getDocumentList((object)['module_srl' => 1]);
```

### 인자 받기

`procCommandLineArguments`가 첫 2개 토큰만 명령으로 쓰고, 나머지는 `$args`로 전달하지만 스크립트 내부에서 명시적으로 접근하지 않으면 사용되지 않는다.

전역 `$argv` 사용:

```php
<?php
// modules/foo/scripts/run.php

global $argv;
$user_srl = isset($argv[2]) ? (int)$argv[2] : 0;
// php index.php foo.run 123
```

### 환경

CLI 모드에서는 `index.php:65`에서 `Rhymix\Framework\Debug::disable()`이 호출되어 인메모리 디버그 로그 수집이 꺼진다(CLI에는 디버그 툴바가 없어 불필요). 이때 일반 경고/에러는 `addError()`가 조기 return하여 기록되지 않으며(`Debug.php:349-353`), 미처리 예외와 치명적 오류만 `config('debug.write_error_log') !== 'none'`일 때 `error_log`로 남는다(`Debug.php:672-704`).

### 출력

`echo` / `print` / `fwrite(STDOUT, ...)` 사용. HTML 응답이 아니므로 디스플레이 핸들러는 작동하지 않는다.

## 신중하게: 워커 vs 일회성 작업

- **워커**: `cron.php`처럼 큐를 비울 때까지 도는 형태. 시그널 핸들러 필수.
- **일회성**: 한 번 실행 후 종료. 별 처리 불필요.

큐 시스템이 있으므로 무거운 작업은 큐에 넣고 워커가 처리하게 분리하는 편이 안전.

## 관리자 UI에서 cron 도움

`modules/admin/`의 시스템 설정에 cron 가이드와 `queue.key` 발급 UI가 있다.

## 다음 문서

- 큐: [17-cache-and-queue.md](17-cache-and-queue.md)
- 디버그: [24-debug-and-logging.md](24-debug-and-logging.md)
- admin 모듈: [28-modules/admin.md](28-modules/admin.md)
