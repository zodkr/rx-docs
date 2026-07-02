# integration_search (통합 검색)

## 개요

- **카테고리**: service
- **역할**: 사이트 전체에서 문서/댓글/멀티미디어(이미지)/첨부파일을 통합 검색. 다른 모듈의 검색을 통합. (태그는 문서 검색의 세부 대상 중 하나이며, 회원 검색은 지원하지 않는다.)

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Integration_search` | `integration_search.class.php` |
| `Integration_searchModel` | `integration_search.model.php` |
| `Integration_searchView` | `integration_search.view.php` |
| `Integration_searchMobile` | `integration_search.mobile.php` |
| `Integration_searchAdminController` | `integration_search.admin.controller.php` |
| `Integration_searchAdminView` | `integration_search.admin.view.php` |
| `\Rhymix\Modules\Integration_Search\Models\FileSearchResult` | `models/FileSearchResult.php` |

(`integration_search.controller.php`, `integration_search.admin.model.php`, `integration_search.api.php`는 없다.)

## 주요 액션 (5개)

| 액션 | 비고 |
|---|---|
| `IS` | 검색 결과 페이지 (단순 액션명, CSRF 면제) |
| `dispIntegration_searchAdminContent` | 관리자 — 모듈별 검색 설정 (admin_index) |
| `dispIntegration_searchAdminSkinInfo` | 관리자 — 스킨 설정 |
| `procIntegration_searchAdminInsertConfig` | 검색 설정 저장 (ruleset=insertConfig) |
| `procIntegration_searchAdminInsertSkin` | 스킨 설정 저장 |

## 동작

- 검색어를 받아 document(`DocumentModel`)·comment(`CommentModel`)·file(`FileAdminModel`) 모듈의 model을 호출 → 결과 통합. (멀티미디어·첨부파일 검색도 파일 모델을 사용하며 member 모델은 호출하지 않는다.)
- 게시판별 권한 검증.
- 페이지네이션.

## 검색 대상 확장

이 모듈은 자체 트리거를 정의하지 않는다 (가짜 `integration_search.dispIntegration_searchIndex` 같은 트리거는 코드에 없음). 검색 결과 확장이 필요하면 `act:integration_search.IS.after` 같은 코어 자동 act 트리거에 hook해서 결과를 가공한다.

## 스킨

`modules/integration_search/skins/<skin>/index.html` — 검색 결과 표시.

## 관련

- document/comment/file 모듈.
