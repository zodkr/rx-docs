# 20. 파일 스토리지

`Rhymix\Framework\Storage` (`common/framework/Storage.php`, 1058줄)는 파일/디렉토리 조작의 통합 진입점이다. `classes/file/FileHandler.class.php`(legacy)는 대부분 이쪽으로 위임한다.

## 핵심 디자인

- **Atomic write**: 임시 파일 → `rename()` 패턴으로 부분 쓰기 방지.
- **권한 캐시**: umask를 모듈 초기에 캐싱해 매번 stat 호출 회피.
- **FTP 폴백**: 권한 부족 시 자동으로 FTP 경로로 위임.
- **잠금**: 동시 쓰기 충돌 방지를 위한 파일 잠금 API.

## API

### 권한

| 메서드 | 의미 |
|---|---|
| `Storage::getUmask()` | 현재 umask |
| `Storage::setUmask($mask)` | umask 변경 |
| `Storage::recommendUmask()` | 환경에 맞는 권장 값 계산 |

### 존재/타입 검사

| 메서드 | 의미 |
|---|---|
| `Storage::exists($path)` | bool |
| `Storage::isFile($path)` | bool |
| `Storage::isDirectory($path)` | bool |
| `Storage::isSymlink($path)` | bool |
| `Storage::isValidSymlink($path)` | 유효한 심링크 (대상 존재) |
| `Storage::isEmptyFile($path)` | 빈 파일 |
| `Storage::isEmptyDirectory($path)` | 빈 디렉토리 |
| `Storage::isReadable($path)` | 읽기 가능 |
| `Storage::isWritable($path)` | 쓰기 가능 |
| `Storage::isExecutable($path)` | 실행 가능 |

### 읽기

| 메서드 | 비고 |
|---|---|
| `Storage::read($path, $stream=false)` | 문자열 또는 stream resource 반환 |
| `Storage::readPHPData($path)` | PHP array 직렬화 파일 unserialize |

### 쓰기

| 메서드 | 비고 |
|---|---|
| `Storage::write($path, $content, $mode='w', ?int $perms=null)` | atomic |
| `Storage::writePHPData($path, $data, ?string $comment=null, bool $serialize=true)` | PHP 데이터 직렬화 파일 |

`writePHPData`는 기본적으로 `serialize()` 결과를 PHP guard와 함께 저장한다 (`$serialize=false`면 `var_export` 사용). 설정 파일 작성에 활용.

### 복사/이동/삭제

| 메서드 | 비고 |
|---|---|
| `Storage::copy($source, $destination, ?int $destination_perms=null)` | |
| `Storage::move($source, $destination)` | rename 우선, 안 되면 copy+delete |
| `Storage::moveUploadedFile($source, $destination, $type='')` | **첫 인자는 `$_FILES['x']['tmp_name']`** (임시 경로) |
| `Storage::delete($path)` | |
| `Storage::copyDirectory($source, $destination, $exclude_regexp='')` | 재귀 |
| `Storage::moveDirectory($source, $destination)` | 재귀 |
| `Storage::deleteDirectory($path, bool $delete_self=true)` | 재귀 |
| `Storage::deleteEmptyDirectory($path, bool $delete_empty_parents=false)` | 빈 디렉토리만, 옵션으로 상위 정리 |

### 디렉토리 작업

| 메서드 | 비고 |
|---|---|
| `Storage::createDirectory($dirname, ?int $mode=null)` | mkdir -p |
| `Storage::readDirectory($dirname, bool $full_path=true, bool $skip_dotfiles=true, bool $skip_subdirs=true)` | 디렉토리 내 파일 목록 (단일 깊이) |

### 디렉토리 보호

```php
Rhymix\Framework\Storage::protectDirectory($path);
```

- `.htaccess` (Deny from all) 생성.
- `index.html` (빈 파일) 생성.
- 외부 직접 접근 차단.

### 메타데이터

| 메서드 | 비고 |
|---|---|
| `Storage::getSize($filename)` | bytes |
| `Storage::getServerUID()` | 웹서버 프로세스 UID (umask 계산용) |

> `Storage`는 mtime / mime-type / touch wrapper를 제공하지 않는다. 그 용도는 PHP 표준 함수(`filemtime`, `touch`, `mime_content_type` 등) 또는 `Rhymix\Framework\MIME`을 직접 사용한다.

## FTP 폴백

`config('ftp.*')` 설정 시 활성화. 권한 부족으로 파일 쓰기 실패 시 자동으로 FTP 명령으로 재시도.

```php
'ftp' => [
    'host' => 'localhost',
    'port' => 21,
    'user' => 'ftpuser',
    'pass' => '...',
    'path' => '/public_html/rhymix',
    'sftp' => false,                 // true면 SFTP
]
```

내부 구현: `common/libraries/ftp.php` (XE 시절 PHP-FTP 클래스 수정판).

## 잠금 (lock)

```php
if (Rhymix\Framework\Storage::getLock(string $name): bool) {
    try {
        // 비독점 잠금 획득됨 — 작업 진행
    } finally {
        // 요청 종료 시 자동 해제. 즉시 모두 해제하려면:
        Rhymix\Framework\Storage::clearLocks();
    }
}
```

`flock` 기반의 명명된 잠금. 큐 워커 1개 보장 등 동시성 제어용. 잠금 파일은 `files/cache/locks/`에 생성된다.

## FileHandler (legacy) 메서드 매핑

`classes/file/FileHandler.class.php`의 정적 메서드는 대부분 `Storage`로 위임한다. XE 호환을 위해 유지.

| FileHandler | 대응 Storage |
|---|---|
| `exists` | `exists` |
| `readFile` | `read` |
| `writeFile` | `write` |
| `copyFile` | `copy` |
| `moveFile` | `move` |
| `removeFile` | `delete` |
| `makeDir` | `createDirectory` |
| `removeDir` | `deleteDirectory` |
| `readDir` | `readDirectory` |
| `getRealPath` | `RX_BASEDIR` 기준 절대경로 변환 |

`FileHandler::getRealPath('./files/attach')` → `'/var/www/rhymix/files/attach'`.

### `FileHandler::createImageFile`

이미지 리사이즈 (GD 함수 직접 사용). animated WebP 보존, EXIF 회전 처리.

```php
FileHandler::createImageFile(
    $source_file,
    $target_file,
    $resize_width = 0,
    $resize_height = 0,
    $target_type = '',           // ''/jpg/png/gif/webp/bmp ('' = 원본 형식)
    $thumbnail_type = 'fill',    // fill/ratio/crop
    $quality = 100,
    $rotate = 0
);
```

### `FileHandler::getRemoteFile`

원격 파일 다운로드. `Rhymix\Framework\HTTP` 위에서 동작.

```php
$ok = FileHandler::getRemoteFile($url, $target_path, $body=null, $timeout=5, $method='GET', $content_type='', $headers=[]);
```

### `FileHandler::returnBytes`

```php
FileHandler::returnBytes('2M');     // 2097152
FileHandler::returnBytes('1G');     // 1073741824
```

### `FileHandler::filesize`

```php
FileHandler::filesize(1234567);     // '1.18MB'
```

## 이미지 처리 — `Rhymix\Framework\Image`

`common/framework/Image.php` (101줄).

```php
$info = Rhymix\Framework\Image::getImageInfo($path);
// ['width' => ..., 'height' => ..., 'type' => 'image/jpeg', 'animated' => false]

$is_animated = Rhymix\Framework\Image::isAnimatedGIF($path);
$is_animated = Rhymix\Framework\Image::isAnimatedWebP($path);
```

리사이즈는 `FileHandler::createImageFile`를 사용. 라이브러리: GD.

## 첨부 파일 모듈 연계

`modules/file/` (코어 모듈)이 업로드/다운로드를 관리. 저장 경로 패턴:

```
files/attach/binaries/<srl 끝 3자리>/<srl>
files/attach/images/<srl 끝 3자리>/<srl>
```

분산 디렉토리 패턴으로 단일 디렉토리 inode 폭발 방지.

다운로드 URL:

```
/files/download/<file_srl>/<file_key>/<filename>
```

라우트는 Router의 글로벌 라우트 (`Router.php:55-60`)로 forward되어 `procFileOutput`이 실행됨. 권한 검증/x-sendfile/range 처리 모두 포함.

## 임시 디렉토리

```php
$tmp = sys_get_temp_dir() . '/rhymix_' . uniqid();
mkdir($tmp);
// ... 작업 ...
Storage::deleteDirectory($tmp);
```

또는 `files/tmp/`를 활용.

## 정리 스크립트

| 스크립트 | 대상 |
|---|---|
| `common/scripts/clean_empty_dirs.php` | `files/attach/` 빈 디렉토리 |
| `common/scripts/clean_garbage_files.php` | 모듈에서 참조하지 않는 고아 파일 |
| `common/scripts/clean_message_files.php` | 메시지 첨부 정리 |
| `common/scripts/clean_old_logs.php` | 오래된 로그 |
| `common/scripts/clean_old_notifications.php` | 알림 |
| `common/scripts/clean_old_thumbnails.php` | 썸네일 캐시 |

상세: [21-cli-and-scripts.md](21-cli-and-scripts.md).

## 다음 문서

- CLI/스크립트: [21-cli-and-scripts.md](21-cli-and-scripts.md)
- file 모듈: [28-modules/file.md](28-modules/file.md)
- 보안 (업로드 필터): [19-security.md](19-security.md)
