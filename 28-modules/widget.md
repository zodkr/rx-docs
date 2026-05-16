# widget (위젯 관리)

## 개요

- **카테고리**: construction
- **역할**: 위젯 등록/설정/실행. 위젯 코드 생성기 제공.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Widget` | `widget.class.php` |
| `WidgetController` | `widget.controller.php` |
| `WidgetModel` | `widget.model.php` |
| `WidgetView` | `widget.view.php` |
| `WidgetAdminView` | `widget.admin.view.php` |

(`widget.admin.controller.php`, `widget.admin.model.php`는 없다 — 관리자 처리는 `WidgetController`/`WidgetModel`이 겸한다.)

## 주요 액션 (14개)

| 액션 | 비고 |
|---|---|
| `dispWidgetAdminWidgetList` | 위젯 카탈로그 |
| `dispWidgetAdminInfo` | 위젯 상세 |
| `dispWidgetAdminGenerateCode` | 위젯 코드 생성기 |
| `procWidgetGenerateCode` | 코드 생성 |
| `procWidgetSaveExtraVarConfig` | 위젯 변수 설정 |

## DB 스키마

`modules/widget/schemas/` 디렉토리는 **비어 있다** — 위젯 자체는 별도 DB 테이블을 사용하지 않는다. 위젯 인스턴스 설정은 본문 마크업 안의 속성으로 직렬화되고, 위젯스타일/스킨 설정은 모듈/페이지 단위로 관리된다.

## 위젯 실행

```php
$oWidgetController = getController('widget');
$html = $oWidgetController->execute($widget_marker_args);
```

`Context::transContent()`가 본문의 `<img class="zbxe_widget_output" widget="...">` 마커를 발견하면 이 메서드를 호출해 HTML로 치환.

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `display` (before) | `triggerWidgetCompile` (controller) | 응답 HTML 직전, 본문의 위젯 마커를 실제 HTML로 치환 |

## 관련

- 새 위젯 만들기: [../27-extension-points/widget.md](../27-extension-points/widget.md)
- 위젯스타일: [../27-extension-points/widgetstyle.md](../27-extension-points/widgetstyle.md)
- 페이지: [page.md](page.md)
- 코어 위젯: [../30-widgets/](../30-widgets/)
