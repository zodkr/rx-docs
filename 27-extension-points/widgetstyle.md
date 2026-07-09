# 27.6 위젯스타일 (Widget Style)

위젯스타일은 **위젯 출력 결과를 감싸는 데코레이터**. 박스/제목/더보기 링크/패딩을 통일된 스타일로 입힌다.

## 디렉토리 구조

```
widgetstyles/<name>/
├── widgetstyle.html           # [필수] 진입 템플릿
├── skin.xml                   # [필수] 메타 + extra_vars
├── style.css                  # [권장] 자체 CSS
├── preview.jpg                # [권장] 미리보기 (기본 파일명). skin.xml의 <preview>로 변경 가능
└── images/                    # [선택]
```

`skin.xml`에 `<preview>preview_alt.png</preview>`로 다른 파일명을 지정할 수도 있다 (`WidgetStyleInfoParser.php:45`).

## skin.xml

`common/framework/parsers/WidgetStyleInfoParser.php`가 파싱. **루트는 `<widgetstyle>`이며 version 속성은 없다** (코어 `widgetstyles/simple/skin.xml`도 `<widgetstyle>` 단일 태그). 파서는 `<version>` 자식 노드 값을 따로 읽는다 — XML 형식 자체의 버전은 표기하지 않는다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgetstyle>
    <title xml:lang="ko">단순 박스</title>
    <description xml:lang="ko">제목과 본문이 있는 단순한 박스</description>
    <version>1.0</version>
    <date>2026-05-16</date>
    <preview>preview.gif</preview>
    <author email_address="me@example.com">
        <name xml:lang="ko">Me</name>
    </author>

    <extra_vars>
        <var name="border_color" type="color" default="#cccccc">
            <title xml:lang="ko">테두리 색</title>
        </var>
        <var name="background_color" type="color" default="#ffffff">
            <title xml:lang="ko">배경 색</title>
        </var>
    </extra_vars>
</widgetstyle>
```

`<var>`의 식별자는 `id="..."` 속성이 우선이지만, **없으면 `name="..."` 속성을 식별자로 사용한다** (`BaseParser.php:138-150`). 즉 `<var name="ws_title" type="text">` 형식도 유효(`id`가 자동으로 `name` 값이 됨). 코어 `widgetstyles/simple/skin.xml`이 이 패턴.

## widgetstyle.html

진입 템플릿. 위젯 출력은 `{$widget_content}` 변수 자리에 삽입된다 (v2에서는 `{!! $widget_content !!}`). `compileWidgetStyle()`이 `Context::set('widget_content', ...)`로 주입하며 (`widget.controller.php:822,826`), `<!--#WidgetContents-->` 같은 매크로/치환자는 존재하지 않는다.

### v1 예시

```html
<!--%import("style.css")-->
<div class="widget-box" style="border: 1px solid {$widgetstyle_extra_var->border_color}; background: {$widgetstyle_extra_var->background_color};">
    <!--@if($widgetstyle_extra_var->ws_title)-->
        <h3 class="widget-title">
            {$widgetstyle_extra_var->ws_title}
            <!--@if($widgetstyle_extra_var->ws_more_url)-->
                <a href="{$widgetstyle_extra_var->ws_more_url}" class="more">{$widgetstyle_extra_var->ws_more_text ?: '더보기'}</a>
            <!--@end-->
        </h3>
    <!--@end-->

    <div class="widget-content">
        {$widget_content}
    </div>
</div>
```

### v2 예시

```blade
@load('style.css')
<div class="widget-box" style="border:1px solid {{ $widgetstyle_extra_var->border_color }};">
    @if($widgetstyle_extra_var->ws_title)
        <h3>{{ $widgetstyle_extra_var->ws_title }}</h3>
    @endif
    <div class="widget-content">
        {!! $widget_content !!}
    </div>
</div>
```

## 관습 변수 (위젯스타일에서 사용)

| 변수 | 의미 | 출처 |
|---|---|---|
| `$widget_content` | 위젯 출력 | 자동 주입 (`widget.controller.php:822,826`) |
| `$widgetstyle_extra_var` | extra_vars 값을 담은 객체 | 자동 주입 (`widget.controller.php:816`) |
| `$widgetstyle_extra_var->ws_title` | 위젯 제목 | extra_vars |
| `$widgetstyle_extra_var->ws_colorset` | 컬러셋 | extra_vars |
| `$widgetstyle_extra_var->ws_more_url` | "더보기" 링크 URL | extra_vars |
| `$widgetstyle_extra_var->ws_more_text` | "더보기" 링크 텍스트 | extra_vars |
| `$widgetstyle_extra_var-><id>` | 임의 extra_vars 정의값 | skin.xml |

개별 `extra_vars` 값은 `$ws_title`처럼 최상위 변수로 노출되지 않는다. `extra_vars`로 정의한 각 var는 skin.xml의 `id`(없으면 `name` 속성)를 키로 `$widgetstyle_extra_var` 객체의 프로퍼티로 노출된다 (`widget.controller.php:807-816`, `BaseParser.php:273-280`). 자동으로 붙는 `ws_` prefix는 없으며, 위 표의 `ws_title`·`ws_colorset` 등은 단지 코어 `simple` 스타일이 var name을 `ws_`로 시작하도록 지었기 때문이다 (`widgetstyles/simple/skin.xml:32,68,84,100`).

패딩은 위젯스타일 템플릿으로 전달되지 않는다. 위젯 편집기의 여백 설정(`widget_padding_top`/`_right`/`_bottom`/`_left`)은 위젯 래퍼를 만드는 `execute()`가 `padding:%dpx %dpx %dpx %dpx !important`로 직접 적용하며 (`widget.controller.php:541-545`), 위젯스타일 자체의 여백은 `style.css`로 처리한다.

## 위젯스타일과 위젯의 관계

```
사용자가 페이지/레이아웃에 위젯 추가
  ↓
위젯 호출 → HTML 반환
  ↓
위젯스타일 호출 → 위 HTML을 감쌈
  ↓
최종 HTML 출력
```

위젯 자체는 콘텐츠만, 위젯스타일이 박스/장식을 담당.

## 위젯 호출에서 위젯스타일 지정

페이지 콘텐츠 마크업:

```html
<img class="zbxe_widget_output" widget="content"
     widgetstyle="simple"
     ws_title="최근 글" ws_more_url="/free" ws_more_text="더보기"
     skin="default" />
```

위젯스타일 `extra_vars`의 var id와 이름이 같은 속성만 `$widgetstyle_extra_var`로 전달된다 (`widget.controller.php:811-814`). 코어 `simple` 스타일은 var를 `ws_`로 시작하도록 지었기 때문에 속성명도 `ws_title`·`ws_more_url` 형태가 된다. 위젯 여백은 위젯스타일이 아니라 위젯 래퍼의 `widget_padding_*` 속성으로 지정한다.

## 최소 예제

### `widgetstyles/myboxstyle/skin.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgetstyle>
    <title xml:lang="ko">My Box</title>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
</widgetstyle>
```

### `widgetstyles/myboxstyle/widgetstyle.html`

```html
<!--%import("style.css")-->
<div class="my-box">
    <div class="content">{$widget_content}</div>
</div>
```

### `widgetstyles/myboxstyle/style.css`

```css
.my-box { border: 1px solid #ccc; padding: 10px; border-radius: 4px; }
.my-box h3 { margin: 0 0 10px; }
```

설치:
1. 파일 작성.
2. 관리자 → 위젯스타일 → 새 위젯스타일 인식.
3. 페이지 위젯 편집기에서 위젯스타일로 선택.

## 미리보기 이미지

기본 파일명은 `preview.jpg`. 다른 이름을 쓰려면 `skin.xml`에 `<preview>my_thumb.png</preview>`. 권장 크기 400x300.

## 다음 문서

- 위젯: [widget.md](widget.md)
- 코어 위젯스타일: [../31-widgetstyles/simple.md](../31-widgetstyles/simple.md)
