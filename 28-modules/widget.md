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
| `dispWidgetAdminDownloadedList` | 설치된 위젯 목록/카탈로그 (관리자 index) |
| `dispWidgetInfo` | 위젯 상세 팝업 |
| `dispWidgetAdminGenerateCode` | 위젯 코드 생성기 |
| `procWidgetGenerateCode` | 코드 생성 |
| `dispWidgetAdminAddContent` | 콘텐츠 위젯 추가 |

## DB 스키마

`modules/widget/schemas/` 디렉토리는 **존재하지 않는다** (스키마/쿼리 정의 없음) — 위젯 자체는 별도 DB 테이블을 사용하지 않는다. skin·widgetstyle·colorset과 스타일 extra vars를 포함한 설정은 각 위젯 인스턴스의 본문 마크업 속성으로 직렬화되며, 페이지/모듈은 이 마커를 담는 컨테이너다 (`widget.controller.php:840-910`).

## 위젯 실행

```php
$oWidgetController = getController('widget');
// function execute($widget, $args, $javascript_mode = false, $escaped = true)
$html = $oWidgetController->execute($widget_name, $args);
```

응답 HTML 생성 직전 `display`(before) 트리거로 호출되는 `triggerWidgetCompile`(`widget.controller.php:271`)이 본문의 `<img class="zbxe_widget_output" widget="...">` 마커를 정규식으로 찾아 `transWidgetCode`(`:280`)→`transWidget`(`:303`)를 거쳐 이 `execute()`(`:491`)를 호출해 HTML로 치환한다. (`Context::transContent()`는 현재 `@deprecated` no-op이다.)

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `display` (before) | `triggerWidgetCompile` (controller) | 응답 HTML 직전, 본문의 위젯 마커를 실제 HTML로 치환 |

## 관련

- 새 위젯 만들기: [../27-extension-points/widget.md](../27-extension-points/widget.md)
- 위젯스타일: [../27-extension-points/widgetstyle.md](../27-extension-points/widgetstyle.md)
- 페이지: [page.md](page.md)
- 코어 위젯: [../30-widgets/](../30-widgets/)
