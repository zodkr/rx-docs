# poll_maker (에디터 컴포넌트)

## 개요

- **위치**: `modules/editor/components/poll_maker/`
- **목적**: 본문에 인라인 투표(설문) 삽입.
- **클래스명**: 소문자 `poll_maker` (`poll_maker.class.php:8` `class poll_maker extends EditorHandler`).

## 동작

1. 도구바 → 팝업 (`getPopupContent`, `:26-38`):
   - `ModuleModel::getSkins(RX_BASEDIR . 'widgets/pollWidget/')`로 **pollWidget의 스킨 목록**을 가져와 팝업에 노출. (poll 모듈이 아니라 pollWidget의 스킨을 재사용한다는 점이 중요.)
   - `tpl/popup.html` 컴파일 후 반환.
2. 팝업에서 질문/항목/스킨 등 입력 → `poll` 모듈에 데이터 저장 → `poll_srl` 발급.
3. 본문에 마커 삽입:
   ```html
   <img editor_component="poll_maker" poll_srl="42" skin="default" style="width:400" />
   ```
4. 출력 시 `transHTML($xml_obj)` (`:46-76`)가 pollWidget 스킨을 컴파일해 투표 폼/결과 HTML 반환.

## transHTML이 읽는 속성

| 속성 | 처리 |
|---|---|
| `poll_srl` | `intval()`로 강제 |
| `skin` | 빈 값이면 `'default'`로 fallback. `widgets/pollWidget/skins/<skin>/` 경로로 사용 |
| `style` | `width([^digit]+)([0-9]+)` regex로 width 추출. 없으면 400 → `style="width:<n>px"` 형식으로 컨텍스트에 주입 |

## 컨텍스트로 전달되는 변수

| 키 | 값 |
|---|---|
| `poll_data` | `PollModel::_getPollinfo($args->poll_srl)` (`modules/poll/poll.model.php:20`) |
| `colorset` | `$args->colorset ?? null` (마커에 colorset 속성이 있으면 사용) |
| `poll_srl` | 정수 변환된 srl |
| `style` | `width:<n>px` 문자열 |

스킨 진입 템플릿: **`widgets/pollWidget/skins/<skin>/pollview.html`** — 즉 `pollWidget` 위젯과 동일한 진입 템플릿을 공유한다. 컴포넌트 자체의 `tpl/`은 팝업(`popup.html`)에만 사용.

## 관련

- poll 모듈: [../28-modules/poll.md](../28-modules/poll.md)
- pollWidget (스킨/진입 템플릿 공유): [../30-widgets/pollWidget.md](../30-widgets/pollWidget.md)
- 에디터 컴포넌트 작성: [../27-extension-points/editor-component.md](../27-extension-points/editor-component.md)
