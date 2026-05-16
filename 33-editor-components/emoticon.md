# emoticon (에디터 컴포넌트)

## 개요

- **위치**: `modules/editor/components/emoticon/`
- **목적**: 본문에 이모티콘 이미지를 삽입.
- **클래스명**: 소문자 `emoticon` (`emoticon.class.php:8` `class emoticon extends EditorHandler`).

## 동작

1. CKEditor 도구바의 이모티콘 아이콘 클릭 → 팝업 호출.
2. 팝업에서 사용 가능한 이모티콘 그리드를 표시. `getEmoticonList()` / `getEmoticons($emoticon)` 헬퍼가 디스크에서 팩 목록을 읽음.
3. 사용자가 이모티콘 선택 → 본문에 마커 삽입. **실제 마커는 `<img editor_component="emoticon" src="…" alt="…" width="…" height="…">`** 형식(`alt`/`width`/`height`는 선택).
4. 출력 시 `transHTML($xml_obj)` (`:109-141`)가 마커를 실제 `<img>` 태그로 재구성.

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
- 사용자가 그리드에서 이모티콘을 클릭하면 JS가 `<img editor_component="emoticon" src="..." />` 형태로 본문에 삽입.

## 이모티콘 팩 관리

- 이모티콘 팩(이미지 묶음)은 `modules/editor/`의 관리자 UI에서 관리.
- 사용 가능한 팩 정보는 캐시 파일에 보관 (재컴파일 시 자동 갱신).

## 관련

- 에디터 컴포넌트 작성: [../27-extension-points/editor-component.md](../27-extension-points/editor-component.md)
- editor 모듈: [../28-modules/editor.md](../28-modules/editor.md)
