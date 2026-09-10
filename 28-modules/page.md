# page (페이지)

## 개요

- **카테고리**: service
- **역할**: 정적/위젯/외부 페이지를 생성. mid를 가진 일반 페이지의 진입 모듈.

## 페이지 유형

| type | 의미 |
|---|---|
| `WIDGET` | 위젯 페이지 — 본문에 위젯 마크업 작성 |
| `ARTICLE` | 일반 문서 |
| `OUTSIDE` | 외부 URL 또는 내부 파일 — 외부 URL은 서버가 원격 페이지를 가져와 삽입, 내부 파일은 옵션에 따라 원문/PHP/템플릿으로 처리 |

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
| `dispPageAdminInfo` | 페이지 설정 진입 (setup_index, `permission="manager:config:*"`, `check_var="module_srl"`) |
| `dispPageAdminPageAdditionSetup` / `dispPageAdminGrantInfo` / `dispPageAdminSkinInfo` / `dispPageAdminMobileSkinInfo` | 부가 설정 화면 (`permission="manager:config:*"`, `check_var="module_srl"`) |
| `dispPageAdminDelete` | 페이지 삭제 폼 |
| `procPageAdminInsert` | 페이지 생성 (ruleset=insertPage) |
| `procPageAdminUpdate` | 페이지 수정 (ruleset=updatePage, `permission="manager:config:*"`, `check_var="module_srl"`) |
| `procPageAdminDelete` | 페이지 삭제 (ruleset=deletePage) |
| `procPageAdminInsertConfig` | 설정 저장 |
| `procPageAdminInsertContent` | 콘텐츠 저장 (permission=modify) |
| `procPageAdminArticleDocumentInsert` | ARTICLE 페이지의 문서 작성 (permission=modify) |
| `procPageAdminRemoveWidgetCache` | 위젯 캐시 비우기 (permission=modify) |

(가짜 액션 `dispPageAdminInsert`는 없다 — 페이지 생성 폼은 `dispPageAdminContent`/`dispPageAdminInfo` 등에서 처리.)

## DB

`modules/page/`에는 `schemas/` 디렉토리 자체가 없어 페이지 전용 테이블이 없다. 본문 등은 `module_extra_vars` 또는 `document`(ARTICLE 페이지의 경우) 테이블에 저장.

## 위젯 페이지

본문의 위젯 마크업은 `page_caching_interval`에 따라 두 경로로 처리된다 (`page.view.php:132-160`).

- interval이 0보다 크고 캐시가 없거나 만료되면 `PageView::_getWidgetContent()`가 `WidgetController::transWidgetCode()`를 직접 호출해 결과 HTML을 `files/cache/page/`에 저장한다. 유효한 캐시는 변환 없이 읽는다.
- interval이 0이면 기존 page cache를 삭제하고 마커가 남은 본문을 반환한다. 이후 최종 출력 직전 `display.before`의 widget trigger가 마커를 실행 결과로 치환한다.

PC·모바일 콘텐츠 편집 화면은 위젯 또는 ARTICLE 편집 준비가 끝난 뒤 자신의 `module_info`를 Context에 다시 설정한다. 준비 과정에서 실행된 위젯 등의 Context 변경이 편집 대상 페이지를 덮어쓰지 않도록 하는 순서다 (`modules/page/page.admin.view.php:192-221`).

## 외부 페이지 설정과 캐시

PC는 `path`, 모바일은 `mpath`가 있으면 그 값을 쓰고 없으면 `path`로 폴백한다. 내부 파일은 `opage_proc_tpl='Y'`이면 템플릿 컴파일, 그렇지 않고 PHP 처리가 활성화되어 있으면 include, 둘 다 아니면 원문을 읽는다 (`modules/page/page.view.php:36-57`, `:281-334`). 설정 저장 시 생략된 PHP·템플릿 옵션은 `N`으로 저장하고, 템플릿을 켜면 PHP도 켠다. 단, 과거 저장 데이터에 PHP 옵션 자체가 없으면 런타임은 PHP 처리를 허용하므로 신규 저장 기본값과 구분한다 (`page.admin.controller.php:42-47`, `page.view.php:47-48`).

`procPageAdminUpdate()`도 내부적으로 `procPageAdminInsert()`를 호출한다. 생성·수정 처리에 성공하고 최종 `page_type`이 `OUTSIDE`이며 `module_srl`이 있으면 `files/cache/opage/<module_srl>.*.php`를 모두 삭제한다 (`modules/page/page.admin.controller.php:112-125`, `:138-141`). 이 패턴에는 출력 캐시와 외부 페이지용 컴파일 캐시가 포함된다. 따라서 경로·처리 옵션을 변경한 뒤 기존 캐시 만료까지 기다리지 않고 새 설정으로 읽는다. 위젯 페이지의 `files/cache/page/`와는 별도다.

## 관련

- widget: [widget.md](widget.md)
- 위젯 작성: [../27-extension-points/widget.md](../27-extension-points/widget.md)
