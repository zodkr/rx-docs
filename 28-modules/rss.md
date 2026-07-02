# rss (RSS)

## 개요

- **카테고리**: utility
- **역할**: 게시판/사이트의 RSS/Atom 피드 출력.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Rss` | `rss.class.php` |
| `RssController` | `rss.controller.php` |
| `RssModel` | `rss.model.php` |
| `RssView` | `rss.view.php` |
| `RssAdminController` | `rss.admin.controller.php` |
| `RssAdminView` | `rss.admin.view.php` |

(`rss.mobile.php`, `rss.admin.model.php`, `rss.api.php`는 없다.)

## 주요 액션 (6개)

| 액션 | 비고 |
|---|---|
| `rss` | 사이트/모듈 RSS 출력 |
| `atom` | Atom 출력 |
| `dispRssAdminIndex` | RSS 관리자 화면 (admin_index) |
| `procRssAdminInsertConfig` | 사이트 RSS 설정 저장 (ruleset=insertRssConfig) |
| `procRssAdminInsertModuleConfig` | 모듈별 RSS 설정 저장 (manager:config:*) |
| `procRssAdminDeleteFeedImage` | RSS 피드 이미지 삭제 |

## 라우트

`Router::$_global_routes`의 `$act` (`rss\|atom`)와 `$mid/$act`(`rss\|atom\|api`) — `/rss`, `/atom`, `/free/rss`, `/free/atom` 모두 매칭. 이 모듈의 `rss`/`atom` 액션으로 forward된다.

## 출력 포맷

`RssView::output()`의 `switch`가 네 가지 포맷을 처리한다 (`rss.view.php:60-78`). 각 포맷은 `tpl/format/`의 템플릿으로 렌더된다.

- RSS 2.0 (기본, `rss20.html`).
- Atom 1.0 (`format=atom`, `atom10.html`).
- RSS 1.0 (`format=rss1.0`, `rss10.html`).
- XE 호환 포맷 (`format=xe`, `xe.html`).

`rss` 액션은 `Context::get('format')` 값으로 `output()`을 호출하므로 `?format=rss1.0`·`?format=xe` 등으로 포맷을 선택하며, 지정하지 않으면 RSS 2.0을 출력한다. `atom` 액션은 항상 `output('atom')`을 호출해 Atom 1.0을 출력한다.

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `moduleHandler.proc` (after) | `triggerRssUrlInsert` (controller) | RSS/Atom 자동 발견 링크를 HTML head에 삽입 |
| `module.procModuleAdminCopyModule` (after) | `triggerCopyModule` (controller) | 모듈 복사 시 RSS 설정 복사 |
| `module.dispAdditionSetup` (before) | `triggerDispRssAdditionSetup` (view) | 관리자 모듈 설정 UI에 RSS 옵션 추가 |

## 관련

- board: [board.md](board.md)
- 라우터: [../07-router.md](../07-router.md)
