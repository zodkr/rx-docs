# layout (레이아웃)

## 개요

- **카테고리**: construction
- **역할**: 레이아웃 등록/관리/사용자 편집.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Layout` | `layout.class.php` |
| `LayoutModel` | `layout.model.php` |
| `LayoutView` | `layout.view.php` |
| `LayoutAdminController` | `layout.admin.controller.php` |
| `LayoutAdminModel` | `layout.admin.model.php` |
| `LayoutAdminView` | `layout.admin.view.php` |

(`layout.controller.php`는 없다 — 사용자 처리 액션이 없고 관리자 액션만 사용.)

## 주요 액션 (25개)

| 액션 | 비고 |
|---|---|
| `dispLayoutPreviewWithModule` | 모듈 적용 미리보기 (root) |
| `getLayoutInstanceListForJSONP` | 인스턴스 목록 JSONP (root) |
| `dispLayoutAdminInstalledList` | 설치된 레이아웃 목록 (admin_index, menu_name=installedLayout) |
| `dispLayoutAdminAllInstanceList` / `dispLayoutAdminInstanceList` | 인스턴스 목록 |
| `dispLayoutAdminInsert` / `dispLayoutAdminModify` / `dispLayoutAdminEdit` | 생성/수정/시각 편집 폼 |
| `dispLayoutAdminCopyLayout` / `dispLayoutAdminLayoutModify` | 복사/수정 |
| `getLayoutAdminSetInfoView` / `getLayoutAdminSiteDefaultLayout` | 모델 조회 |
| `procLayoutAdminInsert` / `procLayoutAdminUpdate` / `procLayoutAdminDelete` | 인스턴스 CRUD (ruleset=insertLayout/updateLayout/deleteLayout) |
| `procLayoutAdminCopyLayout` | 복사 |
| `procLayoutAdminCodeUpdate` / `procLayoutAdminCodeReset` | 사용자 정의 코드 (ruleset=codeUpdate) |
| `procLayoutAdminUserImageUpload` / `procLayoutAdminUserImageDelete` | 사용자 이미지 (ruleset=imageUpload) |
| `procLayoutAdminConfigImageUpload` / `procLayoutAdminConfigImageDelete` | 설정 이미지 |
| `procLayoutAdminUserLayoutImport` / `procLayoutAdminUserLayoutExport` | user_layout 가져오기/내보내기 (ruleset=userLayoutImport) |
| `procLayoutAdminUserValueInsert` | 사용자 값 저장 |

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `layouts` | `schemas/layouts.xml` — 레이아웃 인스턴스 + extra_vars |

(`layout_extra_vars`, `layout_menus`라는 별도 테이블은 없다 — extra_vars는 직렬화하여 `layouts` 테이블에 함께 저장.)

## 레거시 FaceOff 시각 편집기

`modules/layout/tpl/` 하위의 드래그앤드롭 편집 UI는 `type="faceoff"`인 과거 인스턴스를 위한 레거시 기능이다. 현재 `procLayoutAdminInsert()`는 새 FaceOff 레이아웃 생성을 거부한다 (`modules/layout/layout.admin.controller.php:24-27`).

기존 인스턴스의 편집 결과는 `files/faceOff/<getNumberingPath(layout_srl)>layout.html`(`getNumberingPath()`는 뒤에 `/`를 포함, 예: `layout_srl=1`이면 `files/faceOff/001/layout.html`)에 저장되며, `LayoutModel::getUserLayoutHtml()`이 반환한 경로를 `ModuleHandler`가 `ModuleObject::setEditedLayoutFile()`로 설정해 `edited_layout_file`로 사용한다 (`classes/module/ModuleHandler.class.php:1178-1181`). `files/cache/layout/`에는 컴파일된 `*.cache.php` 외에도 미리보기 중 고정 임시 파일 `tmp.tpl`을 만들었다가 삭제한다 (`modules/layout/layout.admin.view.php:327-341`).

## 모델 메서드

```php
LayoutModel::getLayout($layout_srl);             // 단일 레이아웃 정보
LayoutModel::getLayoutList($site_srl, $type);    // 현재 $site_srl은 호환용이며 조회에서 사용하지 않음
getAdminModel('layout')->getSiteDefaultLayout($type); // 사이트 기본 레이아웃 srl 반환(없으면 0); -1 치환은 LayoutModel::getLayoutList()에서
```

현재 레이아웃 목록 쿼리는 `$type`만 사용하고, 기본 디자인도 `files/site_design/design_0.php`에서 읽으므로 이 API를 site별 목록 분리로 해석하면 안 된다 (`layout.model.php:26-60`, `layout.admin.model.php:107-126`).

## 관련

- 새 레이아웃 만들기: [../27-extension-points/layout.md](../27-extension-points/layout.md)
- menu: [menu.md](menu.md)
- 코어 레이아웃: [../32-layouts/](../32-layouts/)
