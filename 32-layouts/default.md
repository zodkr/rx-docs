# default (PC 레이아웃)

## 개요

- **위치**: `layouts/default/`
- **목적**: Rhymix 기본 레이아웃. GNB + 비주얼 이미지 + 콘텐츠 영역.

## info.xml 핵심

```xml
<layout version="0.2">
    <title xml:lang="ko">기본 레이아웃</title>
    <menus>
        <menu name="GNB" maxdepth="2" default="true">
            <title xml:lang="ko">전역 네비게이션 바</title>
        </menu>
    </menus>
    <extra_vars>
        <var name="LOGO_IMG" type="image">...</var>
        <var name="LOGO_TEXT" type="text">...</var>
        <var name="WEB_FONT" type="select">...</var>
        <var name="LAYOUT_TYPE" type="select">
            <!-- MAIN_PAGE / SUB_PAGE -->
        </var>
        <var name="VISUAL_USE" type="select">...</var>
        <var name="VISUAL_IMAGE_1..3" type="image">...</var>
        <var name="VISUAL_TEXT_1..3" type="text">...</var>
        <var name="VISUAL_LINK_1..3" type="text">...</var>
        <var name="FOOTER" type="textarea">...</var>
    </extra_vars>
</layout>
```

## 구조

- 헤더: 로고 + GNB.
- 비주얼 영역 (`VISUAL_USE=YES`일 때): 3개 비주얼 이미지/텍스트/링크.
- 콘텐츠: 1단(MAIN_PAGE) 또는 2단(SUB_PAGE) 레이아웃.
- 푸터: `FOOTER` 변수 출력. 비어 있으면 "Powered by Rhymix" 문구가 출력됨.

## 자원

- `default.layout.css`, `default.layout.js`.
- `default.layout.webfont.css` (WEB_FONT=='YES'일 때 조건부 로드).
- 이미지 자원: 레이아웃 루트에 직접 위치 (`visual.main.1~3.jpg`, `visual.sub.jpg`, `siteTitle.png`, `slideNav.png` 등).

## 관련

- 레이아웃 작성: [../27-extension-points/layout.md](../27-extension-points/layout.md)
- menu 모듈: [../28-modules/menu.md](../28-modules/menu.md)
