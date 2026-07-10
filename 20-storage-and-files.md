# 20. 파일 스토리지

`Rhymix\Framework\Storage` (`common/framework/Storage.php`, 1058줄)는 파일/디렉토리 조작의 통합 진입점이다. `classes/file/FileHandler.class.php`(legacy)는 대부분 이쪽으로 위임한다.

## 핵심 디자인

- **조건부 atomic write**: `safe_overwrite`가 켜져 있고 append 모드가 아니며 대상 디렉토리에 쓸 수 있을 때 임시 파일 → `rename()` 패턴을 사용한다. 그 외에는 대상 파일에 직접 잠금 쓰기.
- **권한 캐시**: `config('file.umask')` 값을 처음 필요할 때 읽어 정적 프로퍼티에 캐싱.
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
| `Storage::readPHPData($path)` | 값을 `return`하는 PHP 데이터 파일을 `include`하여 결과 반환 |

### 쓰기

| 메서드 | 비고 |
|---|---|
| `Storage::write($path, $content, $mode='w', ?int $perms=null)` | 조건이 맞으면 temp+rename atomic, 아니면 직접 잠금 쓰기 |
| `Storage::writePHPData($path, $data, ?string $comment=null, bool $serialize=true)` | PHP 데이터 직렬화 파일 |

`writePHPData`는 기본적으로 `serialize()` 결과를 `return unserialize(...)` 형태의 PHP 파일로 저장하고, `$serialize=false`면 `var_export`한 값을 직접 `return`하도록 쓴다. `readPHPData()`는 이를 일반 `unserialize()`로 읽는 것이 아니라 PHP 파일로 include한다 (`common/framework/Storage.php:240-250`).

### 복사/이동/삭제

| 메서드 | 비고 |
|---|---|
| `Storage::copy($source, $destination, ?int $destination_perms=null)` | |
| `Storage::move($source, $destination)` | rename만 수행하며, 실패하면 false 반환 (copy+delete 폴백 없음) |
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
- Apache에서 `.htaccess`가 허용된 경우 외부 직접 접근 차단.

`protectDirectory()`는 best-effort 보조 수단이며 웹서버 설정에 의존한다. nginx 등 `.htaccess`를 해석하지 않는 서버에서는 별도 location 규칙으로 차단해야 한다 (`Storage.php:876-913`).

### 메타데이터

| 메서드 | 비고 |
|---|---|
| `Storage::getSize($filename)` | bytes |
| `Storage::getServerUID()` | 현재 PHP 프로세스의 effective UID (umask 계산용) |

> `Storage`는 mtime / mime-type / touch wrapper를 제공하지 않는다. 그 용도는 PHP 표준 함수(`filemtime`, `touch`, `mime_content_type` 등) 또는 `Rhymix\Framework\MIME`을 직접 사용한다.

## 쓰기 실패 처리

`Storage::write()`는 권한 부족 등으로 쓰기에 실패하면 `trigger_error`(`E_USER_WARNING`) 후 `false`를 반환할 뿐, FTP 등 다른 경로로 폴백하지 않는다 (`Storage.php:312-316`). XE 시절의 레거시 FTP 클래스 `common/libraries/ftp.php`는 `tar.php`와 함께 제거되어 현재 존재하지 않는다. `common/defaults/config.php`에는 호환을 위한 `ftp.*` 기본값이 남아 있지만 현재 코어가 파일 쓰기나 관리자 FTP 설정에 사용하지 않는다.

## 잠금 (lock)

```php
if (Rhymix\Framework\Storage::getLock(string $name): bool) {
    try {
        // 배타적 잠금(exclusive lock) 획득됨 — 작업 진행
        // (LOCK_NB 논블로킹이라 이미 다른 프로세스가 잠금 중이면 getLock()은 즉시 false 반환)
    } finally {
        // 요청 종료 시 자동 해제. 즉시 모두 해제하려면:
        Rhymix\Framework\Storage::clearLocks();
    }
}
```

`flock` 기반의 명명된 잠금. 큐 워커 1개 보장 등 동시성 제어용. 잠금 파일은 `files/locks/`에 생성된다.

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

이미지 리사이즈 (GD 함수 직접 사용). animated WebP는 처리하지 않고 `false`를 반환하며, animated GIF도 애니메이션을 보존하지 않는다. EXIF 방향은 자동 적용되지 않으므로 필요하면 `FileHandler::checkImageRotation($source_file)` 결과를 `$rotate` 인자로 전달한다 (`FileHandler.class.php:504-534,627-646`).

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
$ok = FileHandler::getRemoteFile(
    $url,
    $target_path,
    null,   // body
    3,      // timeout
    'GET',  // method
    null,   // content_type
    [],     // headers
    [],     // cookies
    [],     // post_data
    []      // request_config
);
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
// ['width' => ..., 'height' => ..., 'type' => 'jpg', 'bits' => ..., 'channels' => ...]
// type은 gif/jpg/jp2/png/webp/bmp/psd/ico 중 하나의 축약 문자열 (MIME 타입 아님).
// 'animated' 키는 반환하지 않음 — 애니메이션 여부는 아래 메서드로 확인.

$is_animated = Rhymix\Framework\Image::isAnimatedGIF($path);
$is_animated = Rhymix\Framework\Image::isAnimatedWebP($path);
```

리사이즈는 `FileHandler::createImageFile`를 사용. 라이브러리: GD.

## 첨부 파일 모듈 연계

`modules/file/` (코어 모듈)이 업로드/다운로드를 관리. 저장 경로는 `getStoragePath()`(`file.controller.php:2011-2036`)가 `config('file.folder_structure')` 값에 따라 두 가지 구조로 결정한다. `<type>`은 `images` 또는 `binaries`.

- 신규 설치 기본값 (`folder_structure=2`) — 날짜 기반:

  ```
  files/attach/<type>/YYYY/MM/DD/
  ```

- 기존 사용자 (`folder_structure=1` 또는 `0`) — module_srl + 업로드 대상 번호 기반:

  ```
  files/attach/<type>/<module_srl>/<upload_target_srl 3자리 분할 경로>/
  ```

  3자리 분할은 `getNumberingPath()`(`common/legacy.php:876-886`)가 하위 자리부터 재귀적으로 끊는다 (예: `12345` → `345/012/`). 경로 끝에 별도의 `/<srl>` 디렉토리는 붙지 않는다.

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
