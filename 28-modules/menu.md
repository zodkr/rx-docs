# menu (메뉴)

## 개요

- **카테고리**: construction
- **역할**: 레이아웃과 페이지를 연결하는 메뉴 트리 관리. 사이트맵.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Menu` | `menu.class.php` |
| `MenuMobile` | `menu.mobile.php` |
| `MenuAdminController` | `menu.admin.controller.php` |
| `MenuAdminModel` | `menu.admin.model.php` |
| `MenuAdminView` | `menu.admin.view.php` |

(menu는 일반 controller/model/view를 두지 않는다 — 사용자 메뉴 UI는 모바일 클래스 + 관리자 클래스만 사용.)

## 주요 액션 (23개)

| 액션 | 비고 |
|---|---|
| `dispMenuMenu` | (mobile) 모바일 메뉴 |
| `dispMenuAdminSiteMap` | 사이트맵 (admin_index, menu_name=siteMap) |
| `dispMenuAdminSiteDesign` | 사이트 디자인 (menu_name=siteDesign) |
| `getMenuAdminSiteMap` / `getMenuAdminItemInfo` / `getMenuAdminTplInfo` / `getMenuAdminInstalledMenuType` / `getMenuAdminDetailSetup` | 모델 조회 (ajax) |
| `procMenuAdminInsert` | 메뉴 생성 (ruleset=insertMenu) |
| `procMenuAdminUpdate` | 메뉴 제목 수정 (ruleset=updateMenuTitle) |
| `procMenuAdminUpdateDesign` | 디자인 수정 (ruleset=updateMenuDesign) |
| `procMenuAdminDelete` | 메뉴 삭제 |
| `procMenuAdminInsertItem` / `procMenuAdminUpdateItem` / `procMenuAdminDeleteItem` / `procMenuAdminMoveItem` / `procMenuAdminCopyItem` / `procMenuAdminArrangeItem` | 메뉴 항목 CRUD/이동 |
| `procMenuAdminUpdateAuth` | 항목 권한 갱신 |
| `procMenuAdminButtonUpload` | 메뉴 버튼 이미지 업로드 |
| `procMenuAdminInsertItemForAdminMenu` | 관리자 메뉴용 항목 추가 |
| `procMenuAdminMakeXmlFile` | 메뉴 XML 캐시 갱신 |
| `procMenuAdminAllActList` | 모든 액션 목록 |

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `menu` | `schemas/menu.xml` — 메뉴 정의 (단수) |
| `menu_item` | `schemas/menu_item.xml` — 메뉴 항목 (트리) |
| `menu_layout` | `schemas/menu_layout.xml` — 메뉴 ↔ 레이아웃 매핑 |

(`menus`/`menu_items` 복수형은 잘못된 명칭 — 단수형이 정확.)

## 메뉴 캐시

`MenuAdminController::makeXmlFile()`가 메뉴 트리를 캐싱한다. 이때 `<menu_srl>.xml.php`(XML 데이터)와 `<menu_srl>.php`(실행형 PHP 캐시) 두 파일을 함께 갱신한다 (`menu.admin.controller.php:1778-1779`).

`ModuleHandler::displayContent`이 레이아웃 처리 시 이 중 `<menu_srl>.php`(`$menu->php_file`)를 include해서 `$GNB`/`$LNB` 등 메뉴 객체를 컨텍스트에 주입 (`ModuleHandler.class.php:1163`).

## 홈 메뉴

`menu_srl == -1`은 도메인의 홈 메뉴를 가리킨다. `MenuAdminController::getHomeMenuCacheFile()`로 홈 메뉴 캐시 파일(`files/cache/menu/homeSitemap.php`, 사이트 전역 단일 파일) 경로 획득.

## 이 모듈이 정의하는 트리거

| 이름 | 시점 | 호출 위치 |
|---|---|---|
| `menu.getModuleListInSitemap` | **after만** | `MenuAdminModel::getModuleListInSitemap` (`menu.admin.model.php:423`) |

이 트리거는 `MenuAdminModel`이 사이트맵 데이터를 만들 때 한 번 발사된다 (before는 없다). board 등 콘텐츠 모듈이 hook해서 자체 게시판/페이지 목록을 사이트맵에 추가한다.

## 관련

- layout: [layout.md](layout.md)
- page: [page.md](page.md)
- 레이아웃 작성: [../27-extension-points/layout.md](../27-extension-points/layout.md)
