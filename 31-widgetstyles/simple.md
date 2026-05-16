# simple (위젯스타일)

## 개요

- **목적**: 가장 단순한 박스 데코레이터. 콘텐츠 영역에 컬러셋 클래스, 위젯 제목, "더보기" 링크를 두른다.

## 디렉토리

```
widgetstyles/simple/
├── widgetstyle.html
├── skin.xml
├── style.css
└── preview.gif
```

## 사용 변수 (`widgetstyle.html`)

| 변수 | 의미 |
|---|---|
| `$widgetstyle_extra_var->ws_colorset` | 사용자 선택 컬러셋 (`black`/`white`/그 외) |
| `$widgetstyle_extra_var->ws_title` | 위젯 제목 |
| `$widgetstyle_extra_var->ws_more_url` | 더보기 URL (앞뒤 공백 trim 후 사용) |
| `$widgetstyle_extra_var->ws_more_text` | 더보기 텍스트 |
| `$widget_content` | **위젯 본문 자리** (코어가 실제 위젯 출력 HTML로 치환) |
| `$layout_info->colorset` | 컬러셋 자동 fallback |

## 동작

`widgetstyle.html`(실제 코드):

1. `ws_colorset`이 `black`/`white`이면 동명 CSS 클래스, 아니면 `$layout_info->colorset`을 fallback.
2. `style.css` import.
3. `<h2>{ws_title}</h2>`.
4. `ws_more_url`이 있으면 (http로 시작하지 않으면 `http://` prepend) `widgetMoreLink` 앵커 추가.
5. `{$widget_content}` 출력.

`<!--#WidgetContents-->` 같은 매크로가 아니라 단순 변수 `{$widget_content}`를 사용한다 — 위젯스타일은 일반 템플릿 파일이므로 모든 변수 접근은 `$var`/`$obj->prop` 문법.

## 관련

- 위젯스타일 작성: [../27-extension-points/widgetstyle.md](../27-extension-points/widgetstyle.md)
