# page (페이지)

## 개요

- **카테고리**: service
- **역할**: 정적/위젯/외부 페이지를 생성. mid를 가진 일반 페이지의 진입 모듈.

## 페이지 유형

| type | 의미 |
|---|---|
| `WIDGET` | 위젯 페이지 — 본문에 위젯 마크업 작성 |
| `ARTICLE` | 일반 문서 |
| `OUTSIDE` | 외부 URL 또는 내부 파일 — 외부 URL은 서버가 원격 페이지를 가져와 인라인 삽입, 내부 경로는 PHP/템플릿으로 실행해 삽입 |

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Page` | `page.class.php` |
| `PageController` | `page.controller.php` |
| `PageView` | `page.view.php` |
| `PageMobile` | `page.mobile.php` |
| `PageAPI` | `page.api.php` |
| `PageAdminController` | `page.admin.controller.php` |
| `PageAdminView` | `page.admin.view.php` |

(`page.model.php`, `page.admin.model.php`는 없다 — 페이지 자체 데이터가 없어 모델이 필요 없음.)

## 주요 액션 (19개)

| 액션 | 비고 |
|---|---|
| `dispPageIndex` | 페이지 표시 (mid 진입, index="true", standalone="false") |
| `dispPageNotFound` | 404 핸들러 (error-handlers="404") |
| `dispPageAdminContent` | 관리자 콘텐츠 편집 (admin_index, menu=page) |
| `dispPageAdminContentModify` / `dispPageAdminMobileContent` / `dispPageAdminMobileContentModify` | 콘텐츠 편집/모바일 (permission=modify) |
| `dispPageAdminInfo` | 페이지 설정 진입 (setup_index, manager) |
| `dispPageAdminPageAdditionSetup` / `dispPageAdminGrantInfo` / `dispPageAdminSkinInfo` / `dispPageAdminMobileSkinInfo` | 부가 설정 화면 (manager) |
| `dispPageAdminDelete` | 페이지 삭제 폼 |
| `procPageAdminInsert` | 페이지 생성 (ruleset=insertPage) |
| `procPageAdminUpdate` | 페이지 수정 (ruleset=updatePage, manager) |
| `procPageAdminDelete` | 페이지 삭제 (ruleset=deletePage) |
| `procPageAdminInsertConfig` | 설정 저장 |
| `procPageAdminInsertContent` | 콘텐츠 저장 (permission=modify) |
| `procPageAdminArticleDocumentInsert` | ARTICLE 페이지의 문서 작성 (permission=modify) |
| `procPageAdminRemoveWidgetCache` | 위젯 캐시 비우기 (permission=modify) |

(가짜 액션 `dispPageAdminInsert`는 없다 — 페이지 생성 폼은 `dispPageAdminContent`/`dispPageAdminInfo` 등에서 처리.)

## DB

`modules/page/`에는 `schemas/` 디렉토리 자체가 없어 페이지 전용 테이블이 없다. 본문 등은 `module_extra_vars` 또는 `document`(ARTICLE 페이지의 경우) 테이블에 저장.

## 위젯 페이지

본문에 위젯 마크업을 입력하면 `WidgetController::transWidgetCode()`가 위젯을 실행해 결과 HTML로 치환한다 (`page.view.php:150-151`). 결과는 `page_caching_interval`에 따라 `files/cache/page/`에 캐시된다.

## 관련

- widget: [widget.md](widget.md)
- 위젯 작성: [../27-extension-points/widget.md](../27-extension-points/widget.md)
