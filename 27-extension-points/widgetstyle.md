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

진입 템플릿. 위젯 출력은 `<!--#WidgetContents-->` 또는 `{$widget_content}` 자리에 삽입된다.

### v1 예시

```html
<div class="widget-box" style="border: 1px solid {$ws_border_color}; background: {$ws_background_color};">
    <!--@if($ws_title)-->
        <h3 class="widget-title">
            {$ws_title}
            <!--@if($ws_more_url)-->
                <a href="{$ws_more_url}" class="more">{$ws_more_text ?: '더보기'}</a>
            <!--@end-->
        </h3>
    <!--@end-->

    <div class="widget-content"
         style="padding: {$ws_box_padding_top}px {$ws_box_padding_right}px {$ws_box_padding_bottom}px {$ws_box_padding_left}px;">
        <!--#WidgetContents-->
    </div>
</div>
```

### v2 예시

```blade
<div class="widget-box" style="border:1px solid {{ $ws_border_color }};">
    @if($ws_title)
        <h3>{{ $ws_title }}</h3>
    @endif
    <div class="widget-content">
        {!! $widget_content !!}
    </div>
</div>
```

## 관습 변수 (위젯스타일에서 사용)

| 변수 | 의미 | 출처 |
|---|---|---|
| `$ws_title` | 위젯 제목 | 사용자 입력 |
| `$ws_colorset` | 컬러셋 | 사용자 입력 |
| `$ws_more_url` | "더보기" 링크 URL | 사용자 입력 |
| `$ws_more_text` | "더보기" 링크 텍스트 | 사용자 입력 |
| `$ws_box_padding_top` | 상단 패딩 | 사용자 입력 |
| `$ws_box_padding_right` | 우측 패딩 | 사용자 입력 |
| `$ws_box_padding_bottom` | 하단 패딩 | 사용자 입력 |
| `$ws_box_padding_left` | 좌측 패딩 | 사용자 입력 |
| `$widget_content` 또는 `<!--#WidgetContents-->` | 위젯 출력 | 자동 주입 |
| `$ws_<extra_var_name>` | extra_vars 정의값 | skin.xml |

extra_vars로 정의한 변수는 `$ws_<name>` 형식으로 prefix가 붙는다.

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
     ws_box_padding_top="10" ws_box_padding_right="10"
     ws_box_padding_bottom="10" ws_box_padding_left="10"
     skin="default" />
```

`ws_*` prefix가 위젯스타일로 전달된다.

## 최소 예제

### `widgetstyles/myboxstyle/skin.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgetstyle version="0.2">
    <title xml:lang="ko">My Box</title>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
</widgetstyle>
```

### `widgetstyles/myboxstyle/widgetstyle.html`

```html
<div class="my-box">
    <!--@if($ws_title)--><h3>{$ws_title}</h3><!--@end-->
    <div class="content"><!--#WidgetContents--></div>
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
