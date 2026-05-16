# 27.7 에디터 컴포넌트 (Editor Component)

에디터(CKEditor 기반)에 **버튼 → 팝업 → 본문 삽입**의 흐름으로 동작하는 확장 컴포넌트. 예: 이모티콘, 이미지 갤러리, 투표.

## 디렉토리 구조

```
modules/editor/components/<name>/
├── <name>.class.php           # [필수] EditorHandler 상속
├── info.xml                   # [필수]
├── component_icon.gif         # [필수] 에디터 도구바 아이콘 (24x24)
├── icon.gif                   # [선택] 본문 내 placeholder 아이콘
├── tpl/
│   ├── popup.html             # 팝업 UI
│   └── index.html             # 추가 템플릿 (옵션)
├── lang/<langtype>.php        # [권장]
├── css/, js/, images/         # [선택]
```

외부 플러그인은 `plugins/<plugin>/editor/components/<name>/`도 가능.

## info.xml

`common/framework/parsers/EditorComponentParser.php`가 파싱.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component version="0.2">
    <title xml:lang="ko">이모티콘</title>
    <description xml:lang="ko">이모티콘 삽입</description>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author email_address="me@example.com">
        <name xml:lang="ko">Me</name>
    </author>

    <extra_vars>
        <var name="default_skin" type="select" default="basic">
            <title xml:lang="ko">기본 스킨</title>
            <options>
                <option value="basic"><title xml:lang="ko">기본</title></option>
            </options>
        </var>
    </extra_vars>
</component>
```

## EditorHandler API

`classes/editor/EditorHandler.class.php`. 모든 컴포넌트의 부모. **`BaseObject` 상속** — `error`/`message`/`get`/`add` 등 BaseObject API도 사용 가능.

```php
class EditorHandler extends BaseObject
{
    // 부모 BaseObject가 #[AllowDynamicProperties] — 다음 속성은 동적 할당
    // $editor_sequence  : 동일 페이지의 에디터 인스턴스 식별자
    // $component_path   : 컴포넌트 디렉토리 경로
    // $info             : 컴포넌트 메타 (info.xml + 사용자 설정)

    // 정의된 메서드 — setInfo만 부모 클래스에 있다.
    public function setInfo($info);     // info->extra_vars의 var 값들을 $this->{key}로 펼침

    // 자식이 구현 (이 두 메서드는 EditorHandler에 정의 안 됨)
    public function getPopupContent();    // 팝업 HTML 반환
    public function transHTML($xml_obj);  // 저장된 본문의 컴포넌트 마크업 → 최종 HTML
}
```

## `<name>.class.php`

```php
<?php
class Emoticon extends EditorHandler
{
    public function getPopupContent()
    {
        Context::set('emoticon_list', $this->getEmoticonList());
        Context::set('editor_sequence', $this->editor_sequence);
        $tpl_path = sprintf('%stpl/', $this->component_path);
        return TemplateHandler::getInstance()->compile($tpl_path, 'popup');
    }

    public function transHTML($xml_obj)
    {
        $attrs = $xml_obj->attrs;
        $code = $attrs->emoticon_code ?? '';
        $url = $this->getEmoticonUrl($code);
        return '<img src="' . escape($url) . '" alt="' . escape($code) . '" />';
    }

    private function getEmoticonList() { /* ... */ }
    private function getEmoticonUrl($code) { /* ... */ }
}
```

### `getPopupContent()`

- 사용자가 도구바의 컴포넌트 버튼 클릭 → 팝업 호출.
- 컴포넌트의 팝업 HTML을 반환.
- 팝업 내에서 사용자가 옵션 선택 → JS로 본문에 컴포넌트 마크업 삽입.

### `transHTML($xml_obj)`

- 저장된 본문이 클라이언트에 표시될 때 호출.
- 본문 내 `<img editor_component="emoticon" emoticon_code="smile" />` 같은 마커가 `$xml_obj`로 들어옴.
- 실제 HTML(이미지/iframe 등)로 변환해서 return.

`$xml_obj` 구조:

```php
$xml_obj->name = 'img';
$xml_obj->attrs = (object)[
    'editor_component' => 'emoticon',
    'emoticon_code' => 'smile',
    // ...컴포넌트 마크업의 다른 속성
];
```

## CKEditor 통합

`common/js/plugins/ckeditor/ckeditor/plugins/xe_component/plugin.js`가 핵심.

### 작동 원리

1. CKEditor 초기화 시 `config.xe_component_arrays`에 컴포넌트 목록을 주입.
2. `xe_component` 플러그인이 각 컴포넌트마다 도구바 버튼 생성.
3. 버튼 클릭 → `window.openComponent(component_name, editor_sequence)` 호출.
4. `modules/editor/tpl/js/editor_common.js`의 `openComponent`가 PHP의 `procEditorGetComponentPopup`을 ajax 호출.
5. PHP가 컴포넌트의 `getPopupContent()` 실행 → HTML 반환.
6. JS가 팝업 띄움.
7. 사용자가 팝업에서 옵션 선택 → 컴포넌트 마크업을 에디터에 삽입.

### 본문에 삽입되는 마크업

```html
<img editor_component="emoticon" emoticon_code="smile" />
<img editor_component="image_gallery" gallery_id="42" thumbnail="thumb1" />
```

- `editor_component=` 속성으로 컴포넌트 식별.
- 나머지 속성은 컴포넌트 데이터.

## transHTML 호출 시점

문서 출력 시 `Context::transContent()` 또는 `DocumentItem`의 콘텐츠 처리에서 본문을 파싱하면서 `<img editor_component="...">`를 발견하면 해당 컴포넌트의 `transHTML`을 호출한다.

본문 저장 단계에서는 마커가 그대로 DB에 보관됨 — 표시 시점에 transHTML로 변환.

## 최소 예제

### `modules/editor/components/myhello/info.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component version="0.2">
    <title xml:lang="ko">My Hello</title>
    <description xml:lang="ko">최소 컴포넌트</description>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
</component>
```

### `modules/editor/components/myhello/myhello.class.php`

```php
<?php
class MyHello extends EditorHandler
{
    public function getPopupContent()
    {
        return '<form id="myhello_form">
            <input type="text" name="name" placeholder="이름" />
            <button type="button" onclick="myhelloInsert()">삽입</button>
        </form>
        <script>
            function myhelloInsert() {
                var n = document.querySelector("[name=name]").value;
                window.parent.editorReplace("myhello", { name: n });
                window.parent.closePopup();
            }
        </script>';
    }

    public function transHTML($xml_obj)
    {
        $name = $xml_obj->attrs->name ?? 'world';
        return '<strong>Hello, ' . escape($name) . '!</strong>';
    }
}
```

### `modules/editor/components/myhello/component_icon.gif`

24x24 GIF 아이콘.

설치:
1. 파일 작성.
2. 관리자 → 에디터 → 컴포넌트 → 새 컴포넌트 인식.
3. 에디터 도구바에서 활성화.
4. 글쓰기 → 도구바 아이콘 클릭 → 팝업 → "Hello" 컴포넌트 삽입.

## 컴포넌트 데이터 저장 패턴

복잡한 데이터(예: 이미지 갤러리)는 컴포넌트 데이터를 자체 테이블에 저장하고, 본문 마커에는 ID만 두는 게 좋다.

```html
<img editor_component="image_gallery" gallery_id="42" />
```

`transHTML`이 ID로 갤러리 조회 → 실제 HTML 생성.

## 권한

- 컴포넌트 사용 권한은 에디터 모듈 단에서 관리.
- 각 게시판/모듈에서 컴포넌트별 활성화 토글 가능.

## 코어 컴포넌트 (4종)

- `emoticon` — 이모티콘.
- `image_gallery` — 이미지 갤러리.
- `image_link` — 이미지 + 링크.
- `poll_maker` — 투표 생성.

상세: [33-editor-components/](../33-editor-components/).

## 다음 문서

- editor 모듈: [../28-modules/editor.md](../28-modules/editor.md)
- 외부 라이브러리(CKEditor + xe_component): [../34-external-libraries.md](../34-external-libraries.md)
