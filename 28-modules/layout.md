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

## 시각 편집기

`modules/layout/tpl/` 하위에 드래그앤드롭 편집 UI. 편집 결과는 `files/cache/layout/edited_<layout_srl>.html`에 저장되어 `ModuleObject::edited_layout_file`로 사용.

## 모델 메서드

```php
LayoutModel::getLayout($layout_srl);             // 단일 레이아웃 정보
LayoutModel::getLayoutList($site_srl, $type);
LayoutAdminModel::getSiteDefaultLayout($type, $site_srl);  // -1 매핑
```

## 관련

- 새 레이아웃 만들기: [../27-extension-points/layout.md](../27-extension-points/layout.md)
- menu: [menu.md](menu.md)
- 코어 레이아웃: [../32-layouts/](../32-layouts/)
