# 27.6 위젯스타일 (Widget Style)

위젯스타일은 **위젯 출력 결과를 감싸는 데코레이터**. 박스·제목·더보기 링크 등 공통 장식을 입힌다. 페이지 편집기의 패딩은 위젯스타일이 아니라 별도 위젯 래퍼가 처리한다.

## 디렉토리 구조

```
widgetstyles/<name>/
├── widgetstyle.html           # [선택지 A] v1 진입 템플릿
├── widgetstyle.blade.php      # [선택지 B] v2 진입 템플릿 (둘 중 하나는 필수)
├── skin.xml                   # [필수] 메타 + extra_vars
├── style.css                  # [권장] 자체 CSS
├── preview.jpg                # [권장] 미리보기 (기본 파일명). skin.xml의 <preview>로 변경 가능
└── images/                    # [선택]
```

`skin.xml`에 `<preview>preview_alt.png</preview>`로 다른 파일명을 지정할 수도 있다 (`WidgetStyleInfoParser.php:45`).

## skin.xml

`common/framework/parsers/WidgetStyleInfoParser.php`가 파싱. 루트는 `<widgetstyle>`이며 코어 형식은 version 속성을 사용하지 않는다. 파서는 루트의 version 속성을 참조하지 않고 `<version>` 자식 노드만 읽으므로, 메타 버전은 반드시 자식으로 표기한다.

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

`select` 등의 선택지는 위젯과 같은 문법을 사용한다. 각 `<options>` 안에 값은 `<value>`, 표시명은 `<name xml:lang="...">` 자식으로 선언한다. `WidgetStyleInfoParser`가 내부적으로 widget 방식의 extra_vars 파서를 호출하므로 `<options value="...">` 속성은 선택값으로 읽히지 않는다.

위젯스타일 코드 생성 경로가 실제 마크업 속성으로 복사하는 type은 `color`/`text`/`select`/`filebox`/`textarea` 5종이다 (`WidgetController::arrangeWidgetVars()`). 현재 설정 템플릿에는 `radio`/`checkbox` 렌더링 분기도 남아 있지만 컨트롤러의 복사 allowlist에 없어 결과 마크업으로 전달되지 않으므로 사용하지 않는다.

## widgetstyle.html / widgetstyle.blade.php

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

### v2 (`widgetstyle.blade.php`) 예시

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

`compileWidgetStyle()`은 전달된 위젯 인자에 같은 키가 없으면 해당 프로퍼티를 `null`로 만든다. `skin.xml`의 `default`를 이 단계에서 자동 대입하지는 않는다. 표준 위젯 코드 생성 UI는 일반적으로 기본값이 채워진 입력을 마크업 속성으로 저장하지만, 마크업을 직접 작성하거나 PHP에서 호출한다면 필요한 기본값을 명시해야 한다.

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

기본 파일명은 `preview.jpg`. 다른 이름을 쓰려면 `skin.xml`에 `<preview>my_thumb.png</preview>`. 파서는 파일 존재 여부만 확인하고 크기를 제한하지 않는다(코어 `simple`의 `preview.gif`는 96x96).

## 다음 문서

- 위젯: [widget.md](widget.md)
- 코어 위젯스타일: [../31-widgetstyles/simple.md](../31-widgetstyles/simple.md)
