# xedition (PC 레이아웃)

## 개요

- **위치**: `layouts/xedition/`
- **목적**: XE 시절부터 이어진 클래식 레이아웃. 회사/단체 사이트에 적합한 정돈된 디자인.

## info.xml 특징

- 다수의 extra_vars (레이아웃 타입/메뉴 타입, 로고 이미지·문자, 푸터 정보, 로그인 위젯, 슬라이드 이미지 등).
- `<menus>`는 GNB(메인 메뉴), UNB(매거진형 추가 메뉴), FNB(푸터 메뉴) 세 개를 정의한다. LNB는 서브형 레이아웃에서 선택된 GNB 하위 메뉴로 `layout.html`이 자동 렌더링한다.

## 자원

- `css/layout.css` (그 외 `idangerous.swiper.css`, `welcome.css`, `webfont.css`, `xeicon.css`, `widget.login.css`).
- 이미지 자원 풍부.

## 관련

- 레이아웃 작성: [../27-extension-points/layout.md](../27-extension-points/layout.md)
