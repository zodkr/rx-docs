# emoticon (에디터 컴포넌트)

## 개요

- **위치**: `modules/editor/components/emoticon/`
- **목적**: 본문에 이모티콘 이미지를 삽입.
- **클래스명**: 소문자 `emoticon` (`emoticon.class.php:8` `class emoticon extends EditorHandler`).

## 동작

1. CKEditor 도구바의 이모티콘 아이콘 클릭 → 팝업 호출.
2. 팝업에서 사용 가능한 이모티콘 그리드를 표시. 팩(디렉토리) 목록은 `getPopupContent()`가 `FileHandler::readDir()`로 읽고(`emoticon.class.php:81`), `getEmoticonList()`는 Context의 `emoticon`(팩 이름)을 검증한 뒤 `getEmoticons($emoticon)`를 호출해 **선택된 단일 팩 디렉토리 안의 이모티콘 이미지 목록**을 `Rhymix\Framework\Storage::readDirectory()`로 읽음(`emoticon.class.php:42-72`).
3. 사용자가 이모티콘 선택 → 본문에 실제 `<img>` 삽입. `insertEmoticon()`(`tpl/popup.js:58`)이 `$('<img>').addClass("emoticon")…`로 **`<img class="emoticon" src="…" alt="…">`** 를 삽입하며, 너비·높이는 jQuery `.width()/.height()`로 인라인 `style`에 들어가고 SVG 팩이면 `srcset` 속성이 추가된다(`tpl/popup.js:60-62`). `editor_component="emoticon"` 속성은 붙지 않는다.
4. 이 컴포넌트가 삽입한 이모티콘에는 `editor_component` 속성이 없으므로 `transComponent()`의 정규식(`editor.controller.php:255`)에 매칭되지 않아 `transHTML()`이 자동 호출되지 않고, 삽입된 실제 `<img>`가 그대로 저장·출력된다. `transHTML($xml_obj)`(`:109-141`)는 `editor_component="emoticon"` 속성이 포함된 (레거시) 콘텐츠에 대해서만 `editor.controller.php:255` 정규식을 통해 호출되어 마커를 실제 `<img>`로 재구성한다.

## transHTML 동작 (`:109-141`)

읽는 속성은 4개만:

| 속성 | 의미 |
|---|---|
| `src` | 이미지 URL (필수) |
| `alt` | 대체 텍스트 (없으면 URL의 마지막 segment, 그것도 없으면 `src` 사용) |
| `width` | 정수, 양수일 때만 출력 |
| `height` | 정수, 양수일 때만 출력 |

- `src`는 `&`를 `&amp;`로, `"`를 `&qout;`(원본 그대로 — 오타 포함)로 치환 (`:122`).
- `alt`만 `htmlspecialchars`로 escape.
- `width`/`height`가 둘 다 있을 때만 속성에 포함.
- 최종 출력: `<img src="…" alt="…" width="…" height="…" style="border:0px" />`.

(`emoticon_code` 같은 속성은 마커에 들어가지 않는다 — docs/외부 자료에서 `emoticon_code="..."` 형식을 본 적이 있다면 잘못된 정보다.)

## 팝업 동작 — `getPopupContent()` (`:78`)

- 컴포넌트의 이모티콘 팩 목록을 컨텍스트에 주입.
- 팝업 템플릿(`tpl/` 또는 컴포넌트 디렉토리)을 컴파일해 HTML 반환.
- 사용자가 그리드에서 이모티콘을 클릭하면 JS(`insertEmoticon()`, `tpl/popup.js:58`)가 `<img class="emoticon" src="…" alt="…">` 형태로 본문에 삽입(너비·높이는 인라인 `style`, SVG 팩이면 `srcset` 추가). 그리드 미리보기 자체는 `<input type="image" class="emoticon">`(`tpl/popup.js:22`)로 렌더링된다.

## 이모티콘 팩 관리

- 이모티콘 팩(이미지 묶음)은 컴포넌트에 동봉된 `modules/editor/components/emoticon/tpl/images/<팩이름>/` 디렉토리로 배포된다(기본 팩 `Twemoji`). 별도의 관리자 UI나 팩 정보 캐시 파일은 없다.
- `getPopupContent()`(`emoticon.class.php:78`)가 `FileHandler::readDir($this->emoticon_path)`로 팩 디렉토리를 매 호출마다 직접 스캔한다(`emoticon.class.php:81`, `emoticon_path`는 `emoticon.class.php:22`의 `'tpl/images'`).
- 각 팩의 제목은 `loadSkinInfo()`(`module.model.php:1078`) → `SkinInfoParser::loadXML()`이 팩의 `skin.xml`을 매번 새로 파싱해 얻는다(캐시 없음 — `SkinInfoParser.php:22`의 `simplexml_load_string`).

## 관련

- 에디터 컴포넌트 작성: [../27-extension-points/editor-component.md](../27-extension-points/editor-component.md)
- editor 모듈: [../28-modules/editor.md](../28-modules/editor.md)
