# image_gallery (에디터 컴포넌트)

## 개요

- **위치**: `modules/editor/components/image_gallery/`
- **목적**: 본문에 이미지 갤러리(슬라이드 또는 리스트) 삽입.
- **클래스명**: 소문자 `image_gallery` (`image_gallery.class.php:8` `class image_gallery extends EditorHandler`).

## 동작

1. 도구바 → 팝업 (`getPopupContent`, `:26-36` — `tpl/popup.html` 컴파일).
2. 팝업에서 이미지 업로드/선택, 갤러리 스타일/색상/정렬 설정.
3. 본문에 마커 삽입:
   ```html
   <img editor_component="image_gallery"
        images_list="img1.jpg img2.png img3.gif"
        gallery_style="slide"
        gallery_align="center"
        border_thickness="0"
        border_color="cccccc"
        bg_color="ffffff"
        style="width:400" />
   ```
4. 출력 시 `transHTML($xml_obj)` (`:44-91`)가 갤러리 HTML을 생성.

## transHTML 동작

읽는 속성:

| 속성 | 처리 |
|---|---|
| `border_thickness` | `(int)` 강제 |
| `gallery_style` | `list`이면 `list_gallery.html`, 그 외엔 `slide_gallery.html` |
| `border_color` | 16진 RGB 6자리 추출 후 `#`prepend |
| `bg_color` | 동상 |
| `gallery_align` | `left`/`center`/`right` 중 하나만 허용, 그 외엔 `center`로 강제 |
| `images_list` | 공백 구분 파일명들. `(gif\|jpe?g\|png)` 확장자만 허용 |
| `style` | `width([^digit]+)([0-9]+)` regex로 width 추출, 없으면 400 |

각 갤러리 인스턴스에 고유 `srl`(`rand(111111, 999999)`)을 부여.

### XMLRPC 응답 분기

`Context::getResponseMethod() == 'XMLRPC'`이면 슬라이드 템플릿 대신 `<img src=... />` 태그를 `<br />`로 연결한 단순 HTML 반환.

## 데이터 저장

별도 테이블 없음 — `images_list` 속성에 파일 URL들이 공백 구분 문자열로 직렬화되어 보관된다.

## 관련

- file 모듈: [../28-modules/file.md](../28-modules/file.md)
- 에디터 컴포넌트 작성: [../27-extension-points/editor-component.md](../27-extension-points/editor-component.md)
