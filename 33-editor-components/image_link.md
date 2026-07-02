# image_link (에디터 컴포넌트)

## 개요

- **위치**: `modules/editor/components/image_link/`
- **목적**: 이미지 + 링크를 한 번에 삽입. 본문에 클릭 시 URL로 이동하는 이미지를 표시.
- **클래스명**: 소문자 `image_link` (`image_link.class.php:8` `class image_link extends EditorHandler`).

## 동작

1. 도구바 → 팝업 (`getPopupContent`, `:26-36` — `tpl/popup.html` 컴파일).
2. 팝업에서 이미지 업로드/주소 + 링크 URL/제목/크기/여백 등 입력.
3. 본문에 마커 삽입 (예):
   ```html
   <img editor_component="image_link"
        src="/files/.../1.jpg"
        link_url="https://example.com"
        open_window="Y"
        alt="설명" title="툴팁"
        width="320" height="240"
        align="center" border="1" margin="8"
        style="margin:8px; border:1px solid #000;" />
   ```
4. 출력 시 `transHTML($xml_obj)` (`:44-108`)가 `<a><img/></a>` 또는 단독 `<img/>`로 변환.

## transHTML이 읽는 속성 (`:44-108`)

| 속성 | 처리 |
|---|---|
| `src` | URL. `&` → `&amp;`, `"` → `&qout;`(원본 그대로 — 오타). `./`로 시작하면 `RX_BASEURL` prepend. `/`나 `http:`/`https:`(정규식 `^https?:` — 슬래시 `//`는 검사하지 않음)로 시작하지 않으면 `RX_BASEURL` prepend |
| `alt` | 항상 출력 (escape 없음) |
| `title` | 있을 때만 출력 (escape 없음) |
| `width` / `height` | 있을 때만 속성 출력 |
| `align` | 있을 때만 |
| `border` | `(int)`. 값이 0이 아니면(음수 포함) 기존 `style`의 `border-*` 속성을 제거하고 `border-style: solid; border-width:<n>px;` 추가 |
| `margin` | `(int)`. 값이 0이 아니면(음수 포함) 기존 `margin*` 속성을 제거하고 `margin:<n>px;` 추가 |
| `style` | 그대로 사용 + 위 border/margin 가공 |
| `link_url` | 있으면 `<a href="..." [target=_blank rel=noopener]><img/></a>`로 감쌈 |
| `open_window` | `'Y'`이면 `target="_blank" rel="noopener"` 추가 |

(주의: `src`/`alt`/`title`이 별도 escape 없이 속성 값으로 들어가므로, 외부 입력은 컴포넌트 팝업/서버 측에서 사전 정화되어야 한다 — `transHTML`은 이미 저장된 마커를 재구성만 한다.)

## 관련

- 에디터 컴포넌트 작성: [../27-extension-points/editor-component.md](../27-extension-points/editor-component.md)
- file 모듈 (업로드 측): [../28-modules/file.md](../28-modules/file.md)
