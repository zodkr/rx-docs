# default (모바일 레이아웃)

## 개요

- **위치**: `m.layouts/default/`
- **목적**: Rhymix 기본 모바일 레이아웃. 상단 헤더(로고 + Menu 링크) + 콘텐츠 1단.

## info.xml 핵심

- `<menus>` 모바일용 GNB.
- `<extra_vars>`: index_title(홈페이지 Title), logo_image(로고 이미지), index_url(로고 클릭 시 이동할 홈 페이지 URL).

## 구조

- 상단 헤더 (로고 + Menu 링크).
- 헤더 우측 `Menu` 텍스트 링크(`class="mu"`) 클릭 시 `dispMenuMenu` 액션의 별도 메뉴 페이지로 이동(해당 화면에 뒤로가기 버튼 제공).
- 콘텐츠 1단.
- 푸터.

## 관련

- PC 레이아웃: [default.md](default.md)
- 모바일 감지: [../23-mobile-detection.md](../23-mobile-detection.md)
