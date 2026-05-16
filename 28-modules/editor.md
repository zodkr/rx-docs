# editor (에디터)

## 개요

- **카테고리**: utility
- **역할**: WYSIWYG 에디터 출력 + 에디터 컴포넌트(이모티콘 등) 관리.

CKEditor 4 기반.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Editor` | `editor.class.php` |
| `EditorController` | `editor.controller.php` |
| `EditorModel` | `editor.model.php` |
| `EditorView` | `editor.view.php` |
| `EditorApi` | `editor.api.php` |
| `EditorAdminController` | `editor.admin.controller.php` |
| `EditorAdminView` | `editor.admin.view.php` |

(`editor.mobile.php`, `editor.admin.model.php`는 없다 — 모바일/관리자 모델 책임은 기본 클래스에 통합.)

## 주요 액션 (15개)

| 액션 | 비고 |
|---|---|
| `dispEditorComponentInfo` | 컴포넌트 정보 화면 |
| `dispEditorFrame` | 에디터 iframe |
| `dispEditorPopup` | 컴포넌트 팝업 |
| `dispEditorSkinColorset` | 스킨 컬러셋 조회 (all-managers) |
| `dispEditorConfigPreview` | 설정 미리보기 (root) |
| `procEditorCall` | 에디터 ajax 진입점 |
| `procEditorSaveDoc` / `procEditorRemoveSavedDoc` / `procEditorLoadSavedDocument` | 자동 저장 CRUD |
| `procEditorInsertModuleConfig` | 모듈별 에디터 설정 (manager:config:*) |
| `dispEditorAdminIndex` | 관리자 에디터 화면 (admin_index, menu=editor) |
| `dispEditorAdminSetupComponent` | 컴포넌트 설정 |
| `procEditorAdminGeneralConfig` | 일반 설정 저장 (ruleset=generalConfig) |
| `procEditorAdminCheckUseListOrder` | 컴포넌트 순서/사용 저장 (ruleset=componentOrderAndUse) |
| `procEditorAdminSetupComponent` | 컴포넌트 설정 저장 (ruleset=setupComponent) |

## 에디터 출력 헬퍼

```php
$oEditor = getModel('editor');
$option = new stdClass;
$option->editor_skin = 'ckeditor';
$option->primary_key_name = 'document_srl';
$option->content_key_name = 'content';
$option->allow_html = true;
$option->enable_default_component = true;
$option->enable_component = true;
$option->enable_autosave = true;
$option->resizable = true;
$option->disable_html_filter = false;
$option->editor_height = 400;

$html = $oEditor->getEditor($document_srl, $option);
echo $html;
```

`getEditor()`는 에디터 HTML + 필요한 JS/CSS 로드를 일괄 처리한다.

## 컴포넌트 디렉토리

```
modules/editor/components/
├── emoticon/
├── image_gallery/
├── image_link/
├── poll_maker/
```

각 컴포넌트는 `EditorHandler`를 상속. 자세한 작성법: [../27-extension-points/editor-component.md](../27-extension-points/editor-component.md).

## CKEditor 통합

`common/js/plugins/ckeditor/ckeditor/`에 CKEditor 4 풀세트. Rhymix 커스텀 플러그인 2종:

- `plugins/xe_component/plugin.js` — Rhymix 컴포넌트 시스템 통합. 도구바 버튼/팝업 호출.
- `plugins/rx_paste/plugin.js` — 붙여넣기 정화.

상세: [../34-external-libraries.md](../34-external-libraries.md#ckeditor).

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `editor_autosave` | 자동 저장 본문 (회원/문서 키) — `schemas/editor_autosave.xml` |
| `editor_components` | 컴포넌트 전역 설정 |
| `editor_components_site` | 사이트별 컴포넌트 설정 |

## 이 모듈이 정의하는 트리거

| 이름 | 시점 |
|---|---|
| `editor.deleteSavedDoc` | before/after — 자동 저장본 삭제 |

(그 외 `act:editor.<액션>.before/after`는 코어가 모든 액션에서 자동 발사하는 표준 act 트리거.)

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `document.insertDocument` (after) | `triggerDeleteSavedDoc` (controller) | 문서 저장 완료 시 임시저장본 삭제 |
| `document.updateDocument` (after) | `triggerDeleteSavedDoc` (controller) | 문서 수정 완료 시 임시저장본 삭제 |
| `module.procModuleAdminCopyModule` (after) | `triggerCopyModule` (controller) | 모듈 복사 시 에디터 설정 복사 |
| `module.dispAdditionSetup` (before) | `triggerDispEditorAdditionSetup` (view) | 관리자 모듈 설정 UI에 에디터 옵션 추가 |
| `display` (before) | `triggerEditorComponentCompile` (controller) | 응답 HTML 직전, 본문의 에디터 컴포넌트 마커를 실제 HTML로 치환 |

## 컴포넌트 호출 흐름

```
사용자가 도구바 컴포넌트 버튼 클릭
  ↓
xe_component 플러그인이 window.openComponent(name, sequence) 호출
  ↓
editor_common.js가 ajax 호출:
  GET /?module=editor&act=dispEditorPopup&...
  ↓
EditorView가 컴포넌트의 getPopupContent() 호출
  ↓
HTML 반환 → 팝업 표시
  ↓
사용자 선택 → 본문에 마커 삽입:
  <img editor_component="name" attr1="..." />
  ↓
저장은 마커 그대로
  ↓
출력 시 transHTML(...)이 마커 → 실제 HTML 변환
```

## 자동저장

`editor_autosaved` 테이블이 회원 + 문서 키 단위로 작성 중 본문 보관. 글쓰기 폼 진입 시 자동 복원 prompt.

## 이모티콘 팩

`modules/editor/`의 이모티콘 관리자 UI로 이미지 묶음을 등록. 사용자는 이모티콘 컴포넌트로 본문에 삽입.

## 관련 모듈

- `document`/`comment` — 본문 저장.
- `file` — 에디터 파일 업로드.

## 다음 문서

- 새 컴포넌트 만들기: [../27-extension-points/editor-component.md](../27-extension-points/editor-component.md)
- CKEditor 통합: [../34-external-libraries.md](../34-external-libraries.md)
- 코어 컴포넌트: [../33-editor-components/](../33-editor-components/)
