# mcontent (위젯)

## 개요

- **목적**: 모바일 응답에 최적화된 콘텐츠 위젯. `content`와 유사하나 모바일 친화 옵션만 노출하고 RSS 외 동작은 거의 동일.
- 클래스명은 소문자 `mcontent` (`widgets/mcontent/mcontent.class.php`).

## proc() 인자 (`$args`)

`widgets/mcontent/conf/info.xml` + `mcontent.class.php::proc()` 기준.

| 인자 | 타입 | 유효값 / 기본 | 비고 |
|---|---|---|---|
| `content_type` | select | `document` / `comment` / `image` / `rss` | — |
| `list_type` | select | `normal` / `image_title` / `image_title_content` | content와 달리 `gallery` 옵션은 없다. |
| `option_view` | select-multi-order | `title` / `thumbnail` / `regdate` / `nickname` / `content` 다중 선택 + 순서 | — |
| `show_browser_title` | select | `Y` / `N` | 게시판 이름. |
| `show_comment_count` | select | `Y` / `N` | 댓글 수. |
| `show_category` | select | `Y` / `N` | 카테고리. |
| `order_target` | select | `list_order` / `update_order` | (content와 달리 `regdate` 옵션이 select에 없다.) |
| `order_type` | select | `desc` / `asc` | — |
| `list_count` | text | (proc에서 빈 값/0이면 기본 적용) | 표시 개수. |
| `subject_cut_size` | text | — | 제목 자르기. |
| `content_cut_size` | text | — | 본문 요약 자르기. |
| `module_srls` | module_srl_list | — | 대상 모듈 srl 콤마 구분. 비우면 사이트 전체. |
| `rss_url0`~`rss_url4` | text | — | `content_type=rss`일 때 외부 RSS URL 5개. |
| `markup_type` | (info.xml에 없음) | 기본 `list` (proc()에서 강제) | content는 기본 `table`이지만 mcontent는 기본 `list`. |
| `tab_type` | (info.xml에 없음) | 코드 분기는 `none`/빈 값 vs 그 외로 처리 | UI에서는 노출되지 않으나 `_compile`이 값을 전달. |
| `$args->skin` | (자동) | — | 스킨. |
| `$args->colorset` | (자동) | — | 컬러셋. |

(content 위젯에 있는 `cols_list_count`/`page_count`/`thumbnail_type`/`thumbnail_width`/`thumbnail_height`/`new_window`/`nickname_cut_size`/`show_icon`/`show_secret`/`duration_new`는 mcontent에는 정의되어 있지 않다. `mobile_layout` 같은 인자도 없다.)

> `widgets/mcontent/conf/info.xml`에는 `content_type=trackback` 옵션과 `show_trackback_count` 항목이 아직 정의되어 있지만, 트랙백은 deprecated되어 본 문서에서는 다루지 않는다(사용 금지).

## 동작 분기

`mcontent.class.php::proc()`은 `content_type`에 따라 다음 헬퍼로 분기한다:

| `content_type` | 사용 메서드 | 소스 |
|---|---|---|
| `comment` | `_getCommentItems` | `CommentModel::getNewestCommentList` |
| `image` | `_getImageItems` | `file.getOneFileInDocument` + `DocumentModel::getDocuments` |
| `rss` | `getRssItems` → `_getRssItems` | `FileHandler::getRemoteResource` + `XeXmlParser` (RSS 2.0 / RSS 1.0 / Atom 1.0) |
| 그 외 (`document` 포함) | `_getDocumentItems` | `widgets.content.getNewestDocuments` + `DocumentModel::setToAllDocumentExtraVars` |

(쿼리는 mcontent 자체에 `queries/` 디렉토리가 없어 `widgets.content.*`를 그대로 재사용한다.)

결과는 `widget_info`로 컨텍스트에 주입되어 스킨 템플릿이 렌더링한다.

## 스킨

`widgets/mcontent/skins/` 하위.

## 관련

- content (PC 대응): [content.md](content.md)
- 모바일: [../23-mobile-detection.md](../23-mobile-detection.md)
