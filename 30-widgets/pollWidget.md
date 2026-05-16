# pollWidget (위젯)

## 개요

- **목적**: 사이트에 설문(poll) 표시. 투표/결과 그래프.
- 클래스명은 **카멜케이스 `pollWidget`** (다른 위젯이 소문자인 것과 다름) — `widgets/pollWidget/pollWidget.class.php:9` `class pollWidget extends WidgetHandler`.
- 스킨 진입 템플릿 파일명은 위젯명이 아니라 **`pollview`** (`pollview.html`).

## proc() 인자 (`$args`)

`widgets/pollWidget/conf/info.xml`의 extra_vars는 **`poll_srl` 1개뿐**이지만, `proc()`은 `$args->style`도 컨텍스트에 그대로 set한다 (info.xml에 없어 관리자 UI로 입력은 안 되고, 외부에서 직접 전달할 때만 의미).

| 인자 | 타입 | 의미 |
|---|---|---|
| `poll_srl` | text | 표시할 설문의 `poll_srl`. `proc()`이 `intval()`로 강제 변환 |
| `$args->style` | (info.xml에 없음) | `Context::set('style', $args->style)`로 그대로 노출. 스킨이 활용 가능 |
| `$args->skin` | (자동) | 스킨 |
| `$args->colorset` | (자동) | 컬러셋 |

(`display_type`/`show_total_count`/`bar_color` 같은 인자는 코어 info.xml에 정의되어 있지 않다.)

## 컨텍스트로 전달되는 변수 (`proc()` 본문)

| 키 | 값 |
|---|---|
| `poll_data` | `PollModel::_getPollinfo((int)$args->poll_srl)` 반환값 (`modules/poll/poll.model.php:20`). 메서드명이 `_` prefix지만 PHP가 가시성을 강제하지 않아 외부 호출됨 |
| `colorset` | `$args->colorset` |
| `poll_srl` | `intval($args->poll_srl)` |
| `style` | `$args->style` (위 참조) |

스킨 진입은 `TemplateHandler::getInstance()->compile($tpl_path, 'pollview')` — `<skin_dir>/pollview.html`을 컴파일한다.

## 동작

- 비투표자: 투표 폼.
- 투표 완료자: 결과 그래프.
- 동작 분기는 스킨의 `pollview.html`(+ `_header.html` 부분 템플릿)이 `poll_data` 값으로 결정.

## 스킨

`widgets/pollWidget/skins/`:

| 스킨 | 파일 |
|---|---|
| `default` | `skin.xml`, `pollview.html`, `_header.html`, `css/`, `js/` |
| `simple` | (동일 구조) |

## 관련

- poll 모듈: [../28-modules/poll.md](../28-modules/poll.md)
- 에디터 컴포넌트 (본문 내 투표): [../33-editor-components/poll_maker.md](../33-editor-components/poll_maker.md)
