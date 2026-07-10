# user_layout (PC 레이아웃)

## 개요

- **위치**: `layouts/user_layout/`
- **목적**: 디자인이 거의 없는 테스트/기반 레이아웃. 새 스킨(레이아웃)을 만들 때 이 사본을 복사해 사용하도록 권장됨(`layouts/user_layout/conf/info.xml`).

## 특징

- info.xml에 `global_menu`(maxdepth=3) 메뉴 슬롯 1개가 정의되어 있으며, `layout.html`에서 GNB/LNB로 렌더링된다(`layouts/user_layout/conf/info.xml:16-22`, `layouts/user_layout/layout.html:13-40`).
- `layout.html`에는 `login_info` 위젯이 `skin="xe_official"`로 하드코딩되어 있다 (`layouts/user_layout/layout.html:28`). 그러나 현재 코어에 동봉된 `login_info` 스킨은 `default`와 `ncenter_login`뿐이므로, 이 레이아웃을 복사해 사용할 때는 실제로 존재하는 스킨이나 함께 배포할 사용자 스킨으로 반드시 바꿔야 한다.
- 관리자 웹 코드 편집기(`dispLayoutAdminEdit`)는 신규·미편집 레이아웃에는 더 이상 열리지 않는다. `files/faceOff/<getNumberingPath(layout_srl)>/layout.html` 또는 `layout.css`가 이미 있는 과거 인스턴스에만 한시적으로 편집 링크가 노출되고, 저장 결과도 그 경로에 기록된다 (`modules/layout/layout.model.php:283-291,601-604,662-664`, `modules/layout/layout.admin.view.php:221-250`). 신규 커스터마이징은 `layouts/user_layout/` 디렉토리를 복사한 뒤 원본 파일을 코드 편집기로 수정한다.
- 드래그앤드롭 시각 편집기는 별도의 레거시 XE FaceOff 레이아웃(`modules/layout/faceoff/`, `type="faceoff"`) 기능이며, 일반 `user_layout`의 기능이 아니다.

## 관련

- layout 모듈: [../28-modules/layout.md](../28-modules/layout.md)
- 시각 편집기는 `modules/layout/`의 관리자 UI 참고.
