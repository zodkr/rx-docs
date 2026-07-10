# 08. Display Handler와 응답

`classes/display/`에는 응답 포맷별 핸들러가 있다. `DisplayHandler`가 진입점이고 `*DisplayHandler`가 포맷을 구현한다.

## 응답 메서드 결정

`DisplayHandler::printContent()` (`classes/display/DisplayHandler.class.php:20`)의 분기:

| 조건 | 핸들러 |
|---|---|
| `xeVirtualRequestMethod === 'xml'` | `VirtualXMLDisplayHandler` |
| `responseMethod === 'JSON'` 또는 `$_POST['_rx_ajax_compat']` | `JSONDisplayHandler` |
| `responseMethod === 'JS_CALLBACK'` | `JSCallbackDisplayHandler` |
| `responseMethod === 'XMLRPC'` | `XMLDisplayHandler` |
| `responseMethod === 'RAW'` | `RawDisplayHandler` |
| 그 외 (기본) | `HTMLDisplayHandler` |

`Context::setResponseMethod('JSON')` 등으로 액션에서 지정 가능.

## printContent() 흐름

`DisplayHandler.class.php:20`:

1. 핸들러 인스턴스 결정 (위 표).
2. 디버그 모드 비활성 시 `rx_error_location` 제거(보안). 활성 시 절대경로 → 상대경로.
3. **트리거** — `layout.before`.
4. `$output = $handler->toDoc($oModule)` — 본문 문자열 생성.
5. **트리거** — `display.before`.
6. **애드온** — `before_display_content`.
7. 애드온 결과 처리 (false/null/BaseObject 반환 시 원본 유지).
8. `prepareToPrint($output)` 호출 가능 시 호출.
9. `Context::checkSessionStatus()` — `$_SESSION` 변경 있으면 세션 시작.
10. HTTP 상태/응답 헤더 출력.
11. 보안 헤더(`X-Frame-Options`, `X-Content-Type-Options`) 출력.
12. `robots_tag === 'noindex'`면 `X-Robots-Tag: noindex` 출력.
13. ob 버퍼 비움.
14. **트리거** — `display.after`.
15. 출력 크기 측정(`self::$response_size`).
16. HTML이면 ob 잔여 버퍼 echo.
17. `echo $output` + 디버그 정보 echo.

## 각 핸들러

### HTMLDisplayHandler (`HTMLDisplayHandler.php`)

가장 복잡한 핸들러. 동작:

1. `$oModule->getTemplatePath()` + `getTemplateFile()`로 스킨 템플릿 컴파일 → 본문 HTML.
2. `$oModule->getLayoutPath()` + `getLayoutFile()`로 레이아웃 템플릿 컴파일.
   - 레이아웃 템플릿의 `{!! $content !!}` 자리에 본문 삽입(`Context::set('content', ...)`).
3. `Context::get('html_header')` 등 모든 head/body 자원 합성.
4. 표준 메타 태그 추가 (`<meta charset>`, viewport, canonical, OpenGraph, robots).
5. `Context::getJsFile()`/`getCSSFile()` 결과로 `<link>`/`<script>` 태그 자동 삽입.
6. 디버그 모드면 본문 끝에 주석으로 디버그 정보 추가.
7. Partial Page Rendering 처리 (XHR 요청 시 일부만 응답).

### JSONDisplayHandler (`JSONDisplayHandler.php`)

- `$oModule->getVariables()` 결과를 `json_encode` 한 문자열 반환.
- `error`/`message`/모듈이 `add()`한 변수 모두 포함.
- `Content-Type: application/json; charset=UTF-8`.

### JSCallbackDisplayHandler

- JSONP 응답. `$_GET['xe_js_callback']` 또는 `$_POST['xe_js_callback']`(`Context::getJSCallbackFunc()`)를 callback 함수명으로.
- `<script>//<![CDATA[ func({...json...}); //]]></script>` 형식의 HTML 스크립트 블록으로 감싸 반환(Content-Type은 text/html).

### XMLDisplayHandler

- XML-RPC 응답. XE 호환.
- `<response>` 루트에 `<error>`, `<message>`, 사용자 변수를 XML 노드로 변환.

### VirtualXMLDisplayHandler

- `xeVirtualRequestMethod=xml` — XE 시절 일부 ajax 호환.
- error/message/redirect_url을 바탕으로 alert 및 opener/parent 리다이렉트 스크립트가 담긴 HTML 문서를 생성해 반환 (iframe 폼 전송 호환용).

### RawDisplayHandler

- `Context::get('response_content_type')`로 임의 Content-Type.
- `getTemplatePath()`+`getTemplateFile()`로 스킨 템플릿만 컴파일해 레이아웃 없이 반환(경로/파일 없으면 빈 문자열).
- 파일 다운로드/이미지 출력에 사용.

## 트리거 시퀀스 (응답 단계)

```
moduleHandler.proc.after   → displayContent 진입
layout.before              → 핸들러 선택 후
(toDoc 실행)
display.before             → 본문 생성 후
addon (before_display_content) → 본문 가공 가능
(헤더 출력 / ob 정리)
display.after              → echo 직전
(echo $output + debug)
```

## HTTP 상태 코드

`_setHttpStatusMessage($code)` (`ModuleHandler.class.php`)이 상태 메시지를 매핑한다. 아래는 대표값이며 전체 목록은 `ModuleHandler.class.php:1434-1509`에 있다.

| 코드 | 메시지 |
|---|---|
| 200 | OK |
| 301 | Moved Permanently |
| 302 | Found |
| 304 | Not Modified |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

`ModuleHandler::$error`를 message object로 변환하는 에러 처리 분기에서는 200/403 외의 상태에 `http_status_code` 템플릿을 사용한다 (`ModuleHandler::displayContent` `:1049-1067`). 모듈이 임의의 non-200 상태를 설정한 모든 응답에 이 템플릿이 보편적으로 강제되는 것은 아니다.

## 보안/SEO 헤더

`config('security.x_frame_options')` (기본 `SAMEORIGIN`), `config('security.x_content_type_options')` (기본 `nosniff`)가 자동 출력된다.

## 디버그 정보

`Rhymix\Framework\Debug::isEnabledForCurrentUser()`가 true면 본문 끝에 디버그 정보가 출력된다. 상세는 [24-debug-and-logging.md](24-debug-and-logging.md).

## PageHandler / 페이지네이션

`classes/page/PageHandler.class.php`는 XE 호환 페이지네이션 클래스다. 신형은 `Rhymix\Framework\Pagination`(common/framework/Pagination.php).

사용:

```php
$pageHandler = new PageHandler($total_count, $total_page, $page, $page_count);
Context::set('page_navigation', $pageHandler);
```

템플릿에서:

```html
<block loop="$page_no=$page_navigation->getNextPage()">
  <a href="{getUrl('page',$page_no)}">{$page_no}</a>
</block>
```

`$page_navigation->first_page`는 현재 표시 window의 첫 페이지이고, `$page_navigation->last_page`는 전체 마지막 페이지다. `getNextPage()`는 `first_page`부터 `page_count` 범위 안에서 `last_page`까지 순회한다 (`PageHandler.class.php:56-78`).

## 다음 문서

- 템플릿: [09-templates-and-skins.md](09-templates-and-skins.md)
- 트리거: [13-event-and-trigger-system.md](13-event-and-trigger-system.md)
- 디버그: [24-debug-and-logging.md](24-debug-and-logging.md)
