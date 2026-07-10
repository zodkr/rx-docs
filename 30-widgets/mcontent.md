# mcontent (위젯)

## 개요

- **목적**: 모바일용으로 남아 있는 레거시 콘텐츠 위젯. `content` 위젯의 쿼리와 피드 파서 구조를 공유하지만, 옵션과 보안 필터·썸네일 처리·페이징 동작은 더 제한적이다.
- 클래스명은 소문자 `mcontent` (`widgets/mcontent/mcontent.class.php`).

## proc() 인자 (`$args`)

`widgets/mcontent/conf/info.xml` + `mcontent.class.php::proc()` 기준.

| 인자 | 타입 | 유효값 / 기본 | 비고 |
|---|---|---|---|
| `content_type` | select | `document` / `comment` / `image` / `trackback` / `rss` | `trackback`은 XML과 코드에 잔재만 남아 있으며 현재는 사용할 수 없음(아래 주의 참고). |
| `list_type` | select | `normal` / `image_title` / `image_title_content` | content와 달리 `gallery` 옵션은 없다. |
| `option_view` | select-multi-order | `title` / `thumbnail` / `regdate` / `nickname` / `content` 다중 선택 + 순서 | — |
| `show_browser_title` | select | `Y` / `N` | 게시판 이름. |
| `show_comment_count` | select | `Y` / `N` | 댓글 수. |
| `show_category` | select | `Y` / `N` | 카테고리. |
| `order_target` | select | `list_order` / `update_order`, 그 외 값은 `list_order` | (content와 달리 `regdate` 옵션이 select에 없다.) |
| `order_type` | select | `desc` / `asc`, 그 외 값은 `asc` | document 분기는 `list_order`/`update_order`의 역순 저장 관례 때문에 SQL 방향을 반전한다. RSS는 병합 결과를 `asc`/`desc`로 정렬하며 comment·image 분기는 이 값을 사용하지 않는다. |
| `list_count` | text | 기본 5 | 빈 값/0이면 `proc()`이 5로 강제. |
| `subject_cut_size` | text | 기본 0 | 제목 자르기. |
| `content_cut_size` | text | 기본 100 | 본문 요약 자르기. |
| `module_srls` | module_srl_list | — | 대상 모듈 srl 콤마 구분. 비우면 사이트 전체. |
| `rss_url0`~`rss_url4` | text | — | `content_type=rss`일 때 외부 RSS URL 5개. |
| `markup_type` | (info.xml에 없음) | 기본 `list` (proc()에서 강제) | content는 기본 `table`이지만 mcontent는 기본 `list`. |
| `tab_type` | (info.xml에 없음) | 코드 분기는 `none`/빈 값 vs 그 외로 처리 | UI에서는 노출되지 않으나 `_compile`이 값을 전달. |
| `$args->skin` | 공통 실행 인자 | 호출자가 선택 | 스킨. `proc()` 자체에는 fallback이 없다. |
| `$args->colorset` | 공통 실행 인자 | 기본 `''` | 공통 실행기가 누락값을 빈 문자열로 초기화. |

(content 위젯에 있는 `cols_list_count`/`page_count`/`thumbnail_type`/`thumbnail_width`/`thumbnail_height`/`new_window`/`nickname_cut_size`/`show_icon`/`show_secret`/`duration_new`는 mcontent에는 정의되어 있지 않다. `mobile_layout` 같은 인자도 없다.)

> `widgets/mcontent/conf/info.xml`에는 `content_type=trackback` 옵션과 `show_trackback_count` 항목이 아직 정의되어 있고 `_getTrackbackItems()` 분기도 남아 있다. 그러나 현재 코어에는 `modules/trackback/`이 없으므로 이 분기는 `getModel('trackback')` 뒤의 메서드 호출을 완료할 수 없다 (`mcontent.class.php:580-620`). 호환 잔재일 뿐이며 선택하면 안 된다.

## 동작 분기

`mcontent.class.php::proc()`은 `content_type`에 따라 다음 헬퍼로 분기한다:

| `content_type` | 사용 메서드 | 소스 |
|---|---|---|
| `comment` | `_getCommentItems` | `CommentModel::getNewestCommentList` |
| `image` | `_getImageItems` | `file.getOneFileInDocument` + `DocumentModel::getDocuments` |
| `rss` | `getRssItems` → `_getRssItems` | `FileHandler::getRemoteResource` + `XeXmlParser` (RSS 2.0 / RSS 1.0 / Atom 1.0) |
| `trackback` | `_getTrackbackItems` | 현재 `trackback` 모듈이 없어 실행 불가 |
| 그 외 (`document` 포함) | `_getDocumentItems` | `widgets.content.getNewestDocuments` + `DocumentModel::setToAllDocumentExtraVars` |

(쿼리는 mcontent 자체에 `queries/` 디렉토리가 없어 `widgets.content.*`를 그대로 재사용한다.)

결과는 `widget_info`로 컨텍스트에 주입되어 스킨 템플릿이 렌더링한다.

## 스킨

`widgets/mcontent/skins/` 하위.

## 관련

- content (PC 대응): [content.md](content.md)
- 모바일: [../23-mobile-detection.md](../23-mobile-detection.md)
