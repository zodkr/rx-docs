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

- `procFileDownload` — 일회성 보안 링크.
- `procFileOutput` — `file_key`로 권한 검증.

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `files` | `schemas/files.xml` — 첨부 파일 메타. `file_srl`, `upload_target_srl`(문서 등 srl), `module_srl`, `source_filename`, `uploaded_filename`, `file_size`, `mime_type`, `direct_download`, `cover_image`, `regdate`. |
| `files_changelog` | `schemas/files_changelog.xml` — 파일 변경 로그 |

(`file_categories` 같은 테이블은 없다.)

## 파일 저장 경로

```
files/attach/binaries/<srl 끝 3자리>/<srl>      # 일반 파일
files/attach/images/<srl 끝 3자리>/<srl>        # 이미지
```

- 분산 디렉토리 패턴으로 inode 폭발 방지.
- `.htaccess`/nginx 차단으로 직접 접근 불가 → 모듈 거쳐서 다운로드.

## 파일 키 (file_key)

`file_key`는 권한 검증용 토큰. URL에 포함되어 누가 다운로드할 수 있는지 제한.

```php
$url = $oFile->getDownloadUrl();
// /files/download/123/abc123.../filename.pdf
```

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

- 위험 확장자 차단.
- 매직 바이트 검사.
- PHP 코드 검출.
- SVG 정화.

상세: [../19-security.md](../19-security.md).

## 이미지 처리

- 업로드 시 EXIF 회전 보정.
- 썸네일 생성 (`getThumbnail($w, $h, $type)`).
- 자동으로 `files/thumbnails/`에 캐싱.
- animated WebP/GIF 보존.

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
