# file (파일)

## 개요

- **카테고리**: content
- **역할**: 첨부 파일 업로드/다운로드/관리. 모든 콘텐츠 모듈의 첨부를 통합.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `File` | `file.class.php` |
| `FileController` | `file.controller.php` |
| `FileModel` | `file.model.php` |
| `FileView` | `file.view.php` |
| `FileAdminController` | `file.admin.controller.php` |
| `FileAdminModel` | `file.admin.model.php` |
| `FileAdminView` | `file.admin.view.php` |

(`file.mobile.php`, `file.api.php`는 없다.)

## 주요 액션 (22개)

| 액션 | 비고 |
|---|---|
| `getFileList` | 파일 목록 모델 |
| `procFileUpload` | 파일 업로드 (CSRF 면제) |
| `procFileIframeUpload` | iframe 업로드 |
| `procFileImageResize` | 이미지 리사이즈 |
| `procFileDelete` | 파일 삭제 |
| `procFileSetCoverImage` | 커버 이미지 지정 |
| `procFileDownload` | 다운로드 (GET/POST) |
| `procFileOutput` | 출력 (file_key 기반) |
| `procFileGetList` | 관리자 ajax 목록 (root) |
| `dispFileAdminList` / `dispFileAdminEdit` | 파일 관리 화면 (admin_index) |
| `dispFileAdminUploadConfig` / `dispFileAdminDownloadConfig` / `dispFileAdminOtherConfig` | 설정 화면 |
| `procFileAdminInsertUploadConfig` / `procFileAdminInsertDownloadConfig` / `procFileAdminInsertOtherConfig` | 설정 저장 |
| `procFileAdminInsertModuleConfig` | 모듈별 파일 설정 (manager:config:*) |
| `procFileAdminAddCart` / `procFileAdminDeleteChecked` / `procFileAdminEditFileName` / `procFileAdminEditImage` | 일괄/단건 처리 |

## 다운로드 라우트

`Router::$_global_routes`에 정의:

```
files/download/link/$file_srl/$sid/$filename       → procFileDownload
files/download/$file_srl/$file_key/$filename       → procFileOutput
```

- `procFileDownload` — 접근권한/외부링크/다운로드가능 여부를 검사하고 `download_count`를 올린 뒤, `file_key`를 붙여 `procFileOutput`으로 302 리다이렉트 (5분 유효·클라이언트 IP·uploaded_filename에 바인딩된 서명 링크 발급).
- `procFileOutput` — `file_key`로 권한 검증.

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `files` | `schemas/files.xml` — 첨부 파일 메타. `file_srl`, `upload_target_srl`(문서 등 srl), `module_srl`, `source_filename`, `uploaded_filename`, `file_size`, `mime_type`, `direct_download`, `cover_image`, `regdate`. |
| `files_changelog` | `schemas/files_changelog.xml` — 파일 변경 로그 |

(`file_categories` 같은 테이블은 없다.)

## 파일 저장 경로

저장 경로는 `FileController::getStoragePath()`(`file.controller.php:2011`)가 `file.folder_structure` 설정에 따라 두 구조로 분기한다. `file_type`은 `images`(직접 다운로드 가능한 멀티미디어)/`binaries`(그 외) 문자열이 그대로 쓰인다.

```
# folder_structure=2 (신규 설치 기본): regdate 기준 년/월/일 분산
files/attach/binaries/<YYYY>/<MM>/<DD>/<32자리 무작위 hex>
files/attach/images/<YYYY>/<MM>/<DD>/<32자리 무작위 hex>

# folder_structure=1/0 (기존 설치): module_srl + upload_target_srl 3자리 분산
files/attach/binaries/<module_srl>/<upload_target_srl 3자리씩 끊은 경로>/<32자리 무작위 hex>
files/attach/images/<module_srl>/<upload_target_srl 3자리씩 끊은 경로>/<32자리 무작위 hex>
```

- 실제 파일명은 `<srl>`이 아니라 `Security::getRandom(32, 'hex')`로 만든 32자리 무작위 hex 문자열(`file.controller.php:1083`)이며, 직접 다운로드 파일에는 확장자가 붙는다.
- 분산 디렉토리 패턴으로 inode 폭발 방지.
- `.htaccess`/nginx 차단으로 직접 접근 불가 → 모듈 거쳐서 다운로드.

## 파일 키 (file_key)

`file_key`는 `procFileDownload`이 발급하는 서명 토큰으로 총 48자다. 앞 8자리는 발급 시각의 hex 타임스탬프(`dechex(RX_TIME)`), 뒤 40자는 HMAC-SHA256 기반 서명(`Security::createSignature` — salt 8자 + base64url 해시 32자, `Security.php:106-112`)이다. 발급 후 300초(5분) 동안만 유효하고 클라이언트 IP·`uploaded_filename`에 바인딩된다(`file.controller.php:416-419`, 검증은 `:456-469`). 별도의 소비/무효화 저장소가 없어 5분 이내에는 재사용 가능하다.

다운로드 링크 자체는 `FileModel`의 정적 메서드가 생성한다 (`File` 클래스에는 `getDownloadUrl`이 없다). 이 URL에는 `file_key`가 아니라 파일의 `sid`가 들어간다.

```php
$url = FileModel::getDownloadUrl($file_srl, $sid, 0, $source_filename);
// files/download/link/123/<sid>/filename.pdf  (rewrite + download_short_url=Y)
// 그 외: index.php?module=file&act=procFileDownload&file_srl=123&sid=<sid>
```

`file_key`가 포함된 `files/download/123/<file_key>/filename.pdf` 형식은 `procFileDownload`이 `procFileOutput`으로 리다이렉트할 때 생성한다(`file.controller.php:416-424`).

## 이 모듈이 정의하는 트리거

| 이름 | 시점 | 호출 위치 |
|---|---|---|
| `file.insertFile` | before/after | `FileController::insertFile` (`file.controller.php:941, 1153`) |
| `file.deleteFile` | before/after | `FileController::deleteFile` (`file.controller.php:1716, 1746`) |
| `file.downloadFile` | before/after | `FileController::procFileDownload` (`file.controller.php:394, 413`) |

(`file.updateFile`/`file.uploadFile` 같은 트리거는 코드에 없다.)

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `document.deleteDocument` (after) | `triggerDeleteAttached` (controller) | 문서 삭제 시 첨부 파일 정리 |
| `comment.deleteComment` (after) | `triggerCommentDeleteAttached` (controller) | 댓글 삭제 시 첨부 파일 정리 |
| `editor.deleteSavedDoc` (after) | `triggerDeleteAttached` (controller) | 에디터 임시저장 삭제 시 첨부 정리 |
| `module.deleteModule` (after) | `triggerDeleteModuleFiles` (controller) | 모듈 삭제 시 모든 첨부/설정 삭제 |
| `module.procModuleAdminCopyModule` (after) | `triggerCopyModule` (controller) | 모듈 복사 시 파일 설정 복사 |
| `document.moveDocumentModule` (after) | `triggerMoveDocument` (controller) | 문서 이동 시 첨부의 module_srl 변경 |
| `document.copyDocumentModule.each` (before) | `triggerAddCopyDocument` (controller) | 문서 복사 시 첨부 복제 |
| `comment.copyCommentByDocument.each` (before) | `triggerAddCopyCommentByDocument` (controller) | 댓글 복사 시 첨부 복제 |
| `module.dispAdditionSetup` (before) | `triggerDispFileAdditionSetup` (view) | 관리자 모듈 설정 UI에 파일 옵션 추가 |

## 업로드 보안

`FilenameFilter` + `FileContentFilter` 적용:

- 파일명의 위험 문자를 치환하고 오해를 부르는 이중 확장자를 정리하며, 최종 `.php`는 `.phps`로 바꾼다. 비관리자는 세션 또는 모듈의 허용 확장자 목록에 없는 파일을 거부한다.
- 지정된 이미지·오디오·동영상 확장자는 `fileinfo`가 판별한 MIME 대분류와 비교.
- HTML/XML처럼 보이는 콘텐츠에서는 PHP 태그와 위험한 스크립트·외부 entity 패턴 검사.
- 비관리자의 SVG 업로드는 `Security::sanitize(..., 'svg')`로 한 번 더 정화.

상세: [../19-security.md](../19-security.md).

## 이미지 처리

- 파일 모듈 설정의 `image_autorotate`가 켜진 JPEG는 EXIF 방향을 읽어 회전 보정 (`file.controller.php:1247-1259`).
- 업로드 시 이미지 리사이즈/재인코딩과 동영상 포스터 썸네일 생성은 `FileHandler::createImageFile`로 처리 (`file.controller.php:1401`은 이미지 변환, `:1368`은 mp4 썸네일)되며, 생성된 썸네일은 `files/attach/`의 storage_path(`thumbnail_filename` 컬럼, `file.controller.php:1103-1110`)에 저장된다.
- 목록/조회용 썸네일은 file 모듈이 아니라 document/comment 아이템 클래스의 `getThumbnail($w, $h, $type)`이 생성해 `files/thumbnails/<번호경로>/`에 캐싱한다 (`document.item.php:1100`(경로 `:1134`), `comment.item.php:776`(경로 `:810`)).
- 리사이즈·재인코딩·형식 변환이 필요 없으면 원본 파일을 그대로 통과시키므로 애니메이션도 유지된다. 변환이 필요한 경우에는 보존을 보장하지 않는다. GD 경로의 `createImageFile()`은 animated WebP를 거부하고, animated GIF는 단일 프레임으로 처리한다. WebP는 ImageMagick 설정이 있으면 실패 후 폴백할 수 있다 (`file.controller.php:1398-1422`, `FileHandler.class.php:608-633`).

## JS 위젯

업로드 UI는 `common/js/plugins/jquery.fileupload/` (blueimp + Rhymix `main.js`). 상세: [../34-external-libraries.md](../34-external-libraries.md).

## 정리 스크립트

| 스크립트 | 용도 |
|---|---|
| `common/scripts/clean_empty_dirs.php` | 빈 `files/attach/` 디렉토리 |
| `common/scripts/clean_garbage_files.php` | 고아 파일 (참조 없는) |
| `common/scripts/clean_message_files.php` | 메시지 첨부 |
| `common/scripts/clean_old_thumbnails.php` | 썸네일 캐시 |

## 관련 모듈

- `document` / `comment` — 첨부 대상.
- `editor` — 파일 업로드 UI.

## 다음 문서

- 스토리지: [../20-storage-and-files.md](../20-storage-and-files.md)
- 보안 (업로드): [../19-security.md](../19-security.md)
- 라우터: [../07-router.md](../07-router.md)
