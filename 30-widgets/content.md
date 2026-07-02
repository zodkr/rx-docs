# content (위젯)

## 개요

- **목적**: 게시판 문서/댓글/첨부 이미지/외부 RSS 피드를 다양한 형태(리스트/탭/갤러리)로 출력.
- 가장 많이 쓰이는 위젯. 사이트 메인 페이지의 핵심.
- 클래스명은 소문자 `content` (`widgets/content/content.class.php:9` `class content extends WidgetHandler`).

## proc() 인자 (`$args`)

`widgets/content/conf/info.xml` 정의 + `content.class.php::proc()`의 런타임 기본값을 합친 실제 동작.

| 인자 | 타입 | 유효값 / 기본 | 의미 |
|---|---|---|---|
| `content_type` | select | `document`(기본 — switch의 default) / `comment` / `image` / `rss` | 추출 대상. |
| `module_srls` | module_srl_list | 콤마 구분 | 대상 모듈 srl. 비우면 전체 사이트에서 추출. |
| `list_type` | select | `normal` / `image_title` / `image_title_content` / `gallery` | 출력 형식 (스킨이 해석). |
| `tab_type` | select | `none` (기본) / `tab_top` / `tab_left` | 탭 모드. `none`/빈 값이면 모듈별 분리하지 않고 단일 리스트. |
| `markup_type` | select | `table` (기본, `proc()`의 fallback) / `list` | 출력 마크업. (`html`/`text` 같은 값은 없다.) |
| `list_count` | text | 기본 5 (`proc()`이 0/빈 값을 5로 강제) | 표시 개수. |
| `cols_list_count` | text | 기본 5 (동일) | 갤러리/이미지의 가로 컬럼 수. |
| `page_count` | select | `1` / `2` / `3` (기본 1) | 페이지 수. 2 이상이면 이전/다음 버튼 노출. 실제 한 페이지의 fetch count는 `list_count * page_count`. |
| `subject_cut_size` | text | 기본 0 (자르지 않음) | 제목 자르기. |
| `content_cut_size` | text | 기본 100 (`proc()` fallback) | 본문 요약 자르기. |
| `nickname_cut_size` | text | 기본 0 | 닉네임 자르기. |
| `new_window` | select | `''`(현재 창) / `Y`(새 창) | 링크 target. |
| `option_view` | select-multi-order | `title` / `thumbnail` / `regdate` / `nickname` / `content` 중 다중 선택 + 순서 (init 기본: `title,regdate,nickname`) | 표시 항목 / 순서. `proc()`이 콤마 split해 `option_view_arr`로 변환. |
| `show_browser_title` | select | `Y` / `N` | 게시판 이름 표시. |
| `show_comment_count` | select | `Y` / `N` | 댓글 수 표시. |
| `show_category` | select | `Y` / `N` | 카테고리 표시. |
| `show_icon` | select | `Y` / `N` | 아이콘 표시. |
| `show_secret` | select | `N` (기본) / `Y` | 비밀글 포함 여부. (`Y`일 때만 status에 `SECRET` 추가, 댓글은 `is_secret='N'` 필터 해제.) |
| `duration_new` | text | 기본 12 (시간 단위) | NEW 표시 유지 시간. |
| `order_target` | select | `regdate` / `list_order` / `update_order` (그 외 값은 `regdate`로 강제) | 정렬 기준. |
| `order_type` | select | `asc` / `desc` (그 외 값은 `asc`로 강제) | 정렬 방향. **단** `order_target`이 `list_order`/`update_order`이고 content_type이 document(기본)인 경우 `_getDocumentItems`(`content.class.php:250-253`)가 의미를 반전한다 (`desc`로 지정하면 SQL은 `asc`). 이 반전은 문서 추출에만 적용되며 comment(`_getCommentItems`는 `sort_index`만 전달)·image·rss(`getRssItems`는 `order_type=='asc'` 여부로 ksort/krsort) 분기에는 없다. |
| `thumbnail_type` | select | `fill` (기본) / `crop` / `ratio` | 썸네일 생성 방식. |
| `thumbnail_width` | text | 기본 100 (`proc()` fallback) | 썸네일 너비. |
| `thumbnail_height` | text | 기본 75 (`proc()` fallback) | 썸네일 높이. |
| `rss_url0`~`rss_url4` | text | — | 외부 RSS URL 5개 (`content_type=rss`일 때만 사용). |
| `$args->skin` | (자동) | — | 스킨. |
| `$args->colorset` | (자동) | — | 컬러셋. |

(`cut_title_length`/`cut_content_length`/`module_srl`(단수)/`category_srl`/`cache` 같은 인자는 코어 info.xml에 없다 — 실제 이름은 `subject_cut_size`/`content_cut_size`/`module_srls`다. `tab_top`/`tab_left`도 `tab_top_*` 같은 변형이 아닌 정확히 이 값들이다.)

## 동작 분기

`proc()`은 `content_type`에 따라 다음 헬퍼로 분기한다:

| `content_type` | 사용 메서드 | 소스 |
|---|---|---|
| `comment` | `_getCommentItems` | `CommentModel::getNewestCommentList` |
| `image` | `_getImageItems` | `file.getOneFileInDocument` + `DocumentModel::getDocuments` |
| `rss` | `getRssItems` → `_getRssItems` | `FileHandler::getRemoteResource` + `XeXmlParser` (RSS 2.0 / RSS 1.0 / Atom 1.0) |
| 그 외 (`document` 포함) | `_getDocumentItems` | `widgets.content.getNewestDocuments` + `DocumentModel::setToAllDocumentExtraVars` |

각 헬퍼는 `contentItem` 인스턴스(파일 하단 동명 클래스 정의)를 만들어 배열로 반환하고, `_compile($args, $content_items)`이 컨텍스트(`widget_info`/`colorset`)에 주입한 뒤 스킨의 `content.html`을 컴파일한다.

## 스킨

`widgets/content/skins/`:

- `default` — 표준 리스트/그리드.
- `simple_rectangle` — 단순 사각형 리스트.

추가 스킨은 서드파티/사용자 영역에서 별도 패키지로 배포된다.

## DB 쿼리

위젯 자체 쿼리 3종 (`widgets/content/queries/`):

- `widgets.content.getNewestDocuments` — 문서 목록.
- `widgets.content.getCategories` — 카테고리 목록.
- `widgets.content.getMids` — module_srls → mid/도메인 매핑.

추가로 file 모듈의 `file.getOneFileInDocument` 쿼리도 `image` 분기에서 사용한다.

## 캐시

위젯 차원의 인자 기반 캐시(`cache=...`)는 코어 info.xml에 없다 — 캐싱이 필요하면 위젯스타일/외부 캐싱 레이어 또는 큐를 활용한다.

## 관련

- 위젯 작성: [../27-extension-points/widget.md](../27-extension-points/widget.md)
- document: [../28-modules/document.md](../28-modules/document.md)
- file: [../28-modules/file.md](../28-modules/file.md)
- 모바일 대응: [mcontent.md](mcontent.md)
