# 27.7 에디터 컴포넌트 (Editor Component)

에디터 본문의 전용 마커를 최종 HTML로 변환하는 확장 컴포넌트. 기본 CKEditor 스킨에서는 **버튼 → 팝업 → 본문 삽입** 흐름까지 제공한다. 예: 이모티콘, 이미지 갤러리, 투표. 다른 에디터 스킨은 같은 도구바 통합을 제공하지 않을 수 있다.

## 디렉토리 구조

```
modules/editor/components/<name>/
├── <name>.class.php           # [필수] EditorHandler 상속
├── info.xml                   # [필수]
├── component_icon.gif         # [권장] 도구바 아이콘, 코어 관례 32x32 GIF
├── icon.gif                   # [선택] 본문 내 placeholder 아이콘
├── tpl/
│   ├── popup.html             # 팝업 UI
│   └── index.html             # 추가 템플릿 (옵션)
├── lang/<langtype>.php        # [권장]
├── css/, js/, images/         # [선택]
```

에디터 컴포넌트는 `modules/editor/components/<name>/`에만 배치할 수 있다. 목록 생성 `makeCache()`가 `RX_BASEDIR . 'modules/editor/components'`만 readDir 하고(`modules/editor/editor.controller.php:425`), 객체 생성 `getComponentObject()`가 경로를 `./modules/editor/components/%s/`로 하드코딩하기 때문(`modules/editor/editor.model.php:587`). `plugins/` 하위에 두어도 인식되지 않는다.

`getComponentObject()`는 폴더명과 같은 문자열을 그대로 `new $component(...)`의 클래스명으로 사용한다. 요청 검증 정규식은 하이픈도 허용하지만 PHP 클래스명에는 사용할 수 없으므로, 실제 컴포넌트 이름은 영문자 또는 `_`로 시작하고 영문자·숫자·`_`만 쓰며 폴더·파일 basename·클래스명을 모두 맞춘다(예: `image_gallery`).

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
            <options value="basic"><title xml:lang="ko">기본</title></options>
        </var>
    </extra_vars>
</component>
```

`select` 타입의 선택지는 각각을 별도의 `<options>` 요소로 표기한다. 값은 `value` 속성(또는 `<value>` 자식), 라벨은 `<title>` 자식으로 넣으며, 선택지가 여러 개면 `<options>` 요소를 그만큼 반복한다. `<options>`로 `<option>` 자식들을 감싸면 파서가 인식하지 못해 빈 옵션만 만들어진다.

현재 컴포넌트 설정 UI가 입력 폼으로 렌더링하는 extra_vars type은 `text`/`textarea`/`select` 3종이다. 또한 `default`는 파서 메타에는 저장되지만 컴포넌트 설정 UI와 `EditorHandler::setInfo()` 경로가 이를 런타임 `value`로 자동 대입하지 않는다. 컴포넌트 코드는 설정값이 없을 때의 fallback을 직접 두고, 활성화 전에 관리자 설정을 한 번 저장하는 흐름을 전제로 하는 것이 안전하다.

## EditorHandler API

`classes/editor/EditorHandler.class.php`. 모든 컴포넌트의 부모. **`BaseObject` 상속** — `error`/`message`/`get`/`add` 등 BaseObject API도 사용 가능.

```php
class EditorHandler extends BaseObject
{
    // 자식 컴포넌트는 반드시 생성자를 정의해야 한다.
    // EditorModel::getComponentObject가 `new $component($editor_sequence, $component_path)`로
    // 객체를 만들기 때문(editor.model.php:593). 생성자를 아예 정의하지 않으면
    // 상속된 BaseObject::__construct($error, $message)가 대신 호출되어 error=$editor_sequence로
    // 세팅되고, 0이 아닌 팝업용 editor_sequence에서는 dispEditorPopup의 $oComponent->toBool()
    // 검사(editor.view.php:77)에서 실패해 component_not_founded 템플릿이 출력된다. 반면 생성자를
    // 정의하되 두 인자를 $this에 저장하지 않으면 부모 생성자는 자동 호출되지 않고 error는 0으로
    // 남아 toBool()은 통과한다. 이 경우 실패는 toBool이 아니라 이후 getPopupContent에서 발생하며,
    // $this->component_path 등이 채워지지 않은 채(대개 빈 문자열 기본값) 잘못된 경로/URL로 동작이 깨진다.
    // $editor_sequence  : 동일 페이지의 에디터 인스턴스 식별자
    // $component_path   : 컴포넌트 디렉토리 경로 (`./modules/editor/components/<name>/`)

    // 정의된 메서드 — setInfo만 부모 클래스에 있다.
    // extra_vars의 각 var 값을 $this->{key}로 펼치고, 메타 전체는 Context 변수 `component_info`로 노출.
    public function setInfo($info);       // Context::set('component_info', $info) + 값 펼침

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
    // 필수: getComponentObject가 `new $component($editor_sequence, $component_path)`로 생성.
    public function __construct($editor_sequence, $component_path)
    {
        $this->editor_sequence = $editor_sequence;
        $this->component_path = $component_path;
    }

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
$xml_obj->attrs = (object)[
    'editor_component' => 'emoticon',
    'emoticon_code' => 'smile',
    // ...컴포넌트 마크업의 다른 속성
];
$xml_obj->body = null;   // div형 컴포넌트의 내부 HTML. <img> 형태면 null
```

`transEditorComponent`(`modules/editor/editor.controller.php:268-275`)가 마커의 속성들을 `$xml_obj->attrs`(stdClass)에, `<div ...>...</div>` 형태 컴포넌트의 내부 HTML을 `$xml_obj->body`에 담아 넘긴다. `->name` 속성은 설정되지 않는다.

## CKEditor 통합

`common/js/plugins/ckeditor/ckeditor/plugins/xe_component/plugin.js`가 핵심.

### 작동 원리

1. CKEditor 초기화 시 `config.xe_component_arrays`에 컴포넌트 목록을 주입.
2. `xe_component` 플러그인이 각 컴포넌트마다 도구바 버튼 생성.
3. 버튼 클릭 → `window.openComponent(component_name, editor_sequence)` 호출.
4. `modules/editor/tpl/js/editor_common.js`의 `openComponent`(`:205`)가 `?module=editor&act=dispEditorPopup&editor_sequence=...&component=...` URL을 팝업 창(PC는 `popopen()`)이나 모달 iframe(모바일은 `openModalIframe()`)으로 연다 — ajax 호출이 아니다.
5. `dispEditorPopup` 액션(`modules/editor/editor.view.php:54`)이 컴포넌트의 `getPopupContent()`를 실행 → 팝업 HTML을 렌더.
6. 사용자가 팝업에서 옵션 선택 → 컴포넌트 마크업을 에디터에 삽입.

### 본문에 삽입되는 마크업

```html
<img editor_component="emoticon" emoticon_code="smile" />
<img editor_component="image_gallery" gallery_id="42" thumbnail="thumb1" />
```

- `editor_component=` 속성으로 컴포넌트 식별.
- 나머지 속성은 컴포넌트 데이터.

## transHTML 호출 시점

변환은 두 층에서 일어난다. `DocumentItem::getTransContent()`(`modules/document/document.item.php:796`)와 `widgetContent` 처리(`modules/widget/widget.controller.php:576`)가 본문 조각을 먼저 변환하고, 에디터 모듈의 `display.before` 이벤트 핸들러 `triggerEditorComponentCompile()`이 최종 HTML 문자열에도 `transComponent()`를 적용한다. `transComponent()`가 `<div|img ... editor_component="...">`를 발견하면 콜백 `transEditorComponent`가 해당 컴포넌트의 `transHTML`을 호출한다(`modules/editor/editor.controller.php:290`). 이미 변환된 마커는 다음 단계에서 다시 매칭되지 않는다. 구 API인 `Context::transContent()`는 `@deprecated` no-op이라 `$content`를 그대로 반환한다.

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
    // 필수: getComponentObject가 `new $component($editor_sequence, $component_path)`로 생성.
    public function __construct($editor_sequence, $component_path)
    {
        $this->editor_sequence = $editor_sequence;
        $this->component_path = $component_path;
    }

    public function getPopupContent()
    {
        return '<form id="myhello_form">
            <input type="text" name="name" placeholder="이름" />
            <button type="button" onclick="myhelloInsert()">삽입</button>
        </form>
        <script>
            // PC 팝업에서는 실제 opener, 모바일 modal iframe에서는 popup_layout이
            // opener를 window.parent로 연결하므로 두 경우 모두 opener를 사용한다.
            function myhelloInsert() {
                var n = document.querySelector("[name=name]").value;
                var marker = document.createElement("img");
                marker.setAttribute("src", "./common/img/blank.gif");
                marker.setAttribute("editor_component", "myhello");
                marker.setAttribute("name_encoded", encodeURIComponent(n));
                var html = marker.outerHTML;
                opener.editorFocus(opener.editorPrevSrl);
                var iframe = opener.editorGetIFrame(opener.editorPrevSrl);
                opener.editorReplaceHTML(iframe, html);
                window.close();
            }
        </script>';
    }

    public function transHTML($xml_obj)
    {
        $name = rawurldecode($xml_obj->attrs->name_encoded ?? 'world');
        return '<strong>Hello, ' . escape($name) . '!</strong>';
    }
}
```

### `modules/editor/components/myhello/component_icon.gif`

코어 컴포넌트와 같은 32x32 GIF 아이콘. 런타임은 파일 존재 여부만 검사하고 실제 크기는 검증하지 않는다. 파일이 없어도 컴포넌트 인식과 CKEditor 버튼 생성 자체는 계속되지만, CKEditor 플러그인은 이 고정 경로를 아이콘 URL로 사용하므로 도구바에 깨진 아이콘이 표시된다. `component_icon` 메타 플래그도 파일이 있을 때만 설정된다.

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

## 컴포넌트의 AJAX 메서드

팝업에서 서버 작업이 필요하면 `module=editor&act=procEditorCall&component=<name>&method=<method>` POST 요청으로 컴포넌트 메서드를 호출할 수 있다. 현재 `procEditorCall()`은 `method_exists()`로 요청된 이름의 존재만 확인할 뿐 별도 allowlist나 visibility 검사를 하지 않은 채 `$oComponent->{$method}()`를 실행한다. 따라서 실제로 호출 가능한 public 메서드는 외부 요청 가능한 엔드포인트로 간주하고, 입력값·로그인·그룹/모듈 권한을 메서드 안에서 다시 검증해야 한다. protected/private 메서드 이름도 존재 검사는 통과하지만 실제 호출 시 `Error`가 발생할 수 있다. 액션은 controller 타입이므로 기본 POST 전용이며 일반 CSRF 검사가 적용된다.

## 권한

- 컴포넌트 사용 권한은 에디터 모듈 단에서 관리.
- 게시판/모듈별 에디터 설정에서는 그룹 단위로 기본/확장 컴포넌트 사용 권한(`enable_default_component_grant`/`enable_component_grant`)만 부여한다(컴포넌트별 토글은 없음).
- 개별 컴포넌트의 활성화 및 노출 범위(사용 그룹 `target_group`, 노출 모듈 `mid_list`)는 컴포넌트 관리 화면에서 전역으로 설정하며, `mid_list`로 특정 게시판에만 노출되도록 제한할 수 있다. `editor_components_site` 테이블과 사이트별 관리자 저장 쿼리는 남아 있지만, 현재 `EditorModel::getComponentList()`와 `getComponent()`는 `site_srl`을 실제 조회에 반영하지 않으므로 사이트별 설정이 런타임에 적용된다고 가정하면 안 된다.

## 코어 컴포넌트 (4종)

- `emoticon` — 이모티콘.
- `image_gallery` — 이미지 갤러리.
- `image_link` — 이미지 + 링크.
- `poll_maker` — 투표 생성.

상세: [33-editor-components/](../33-editor-components/).

## 다음 문서

- editor 모듈: [../28-modules/editor.md](../28-modules/editor.md)
- 외부 라이브러리(CKEditor + xe_component): [../34-external-libraries.md](../34-external-libraries.md)
