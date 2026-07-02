# user_layout (PC 레이아웃)

## 개요

- **위치**: `layouts/user_layout/`
- **목적**: 디자인이 거의 없는 테스트/기반 레이아웃. 새 스킨(레이아웃)을 만들 때 이 사본을 복사해 사용하도록 권장됨(`layouts/user_layout/conf/info.xml`).

## 특징

- info.xml에 `global_menu`(maxdepth=3) 메뉴 슬롯 1개가 정의되어 있으며, `layout.html`에서 GNB/LNB로 렌더링된다(`layouts/user_layout/conf/info.xml:16-22`, `layouts/user_layout/layout.html:13-40`).
- 위젯(`login_info`)이 `layout.html`에 하드코딩되어 있고(`layouts/user_layout/layout.html:28`), 편집은 코드 편집기(`dispLayoutAdminEdit`)로만 이루어진다. 드래그앤드롭 시각 편집기는 별도의 XE FaceOff 레이아웃(`modules/layout/faceoff/`, `type="faceoff"`) 기능이다.
- 편집 결과는 `files/faceOff/<getNumberingPath(layout_srl)>/layout.html`에 저장된다(`modules/layout/layout.model.php:601-604,662-664`).

## 관련

- layout 모듈: [../28-modules/layout.md](../28-modules/layout.md)
- 시각 편집기는 `modules/layout/`의 관리자 UI 참고.
