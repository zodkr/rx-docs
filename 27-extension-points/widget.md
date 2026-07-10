# 27.5 위젯 (Widget)

위젯은 **레이아웃이나 콘텐츠 안에 끼워 넣을 수 있는 동적 컴포넌트**. 예: 최근 게시물, 로그인 박스, 사이트 카운터.

## 디렉토리 구조

```
widgets/<name>/                # 반드시 최상위 widgets/ 아래에 위치 (경로가 ./widgets/로 하드코딩됨)
├── <name>.class.php           # [필수] WidgetHandler 상속
├── conf/info.xml              # [필수]
├── lang/<langtype>.php        # [권장]
├── queries/*.xml              # [선택]
├── skins/<skin>/              # [표준 관리자 코드 생성 흐름에서는 필수] 최소 1개 스킨
│   ├── skin.xml
│   ├── 1.html 또는 1.blade.php (또는 다른 basename)
│   └── images/, css/, js/
```

관리자 위젯 코드 생성 액션은 `skin`이 없으면 오류를 반환하므로 표준 UI에 노출할 위젯에는 스킨이 필요하다. 다만 런타임의 `getWidgetObject()`는 클래스와 `proc()`만 검사하므로, `proc()`가 HTML을 직접 반환하도록 작성하고 `execute()`를 직접 호출하는 특수한 위젯은 스킨 없이도 실행할 수 있다.

위젯 이름은 폴더명·`<name>.class.php` basename·클래스명이 모두 같다. `getWidgetObject()`가 이름 문자열로 `new $widget()`을 실행하므로 영문자 또는 `_`로 시작하는 유효한 PHP 클래스 식별자를 사용한다.

## info.xml

`common/framework/parsers/WidgetInfoParser.php`가 파싱.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widget version="0.2">
    <title xml:lang="ko">최근 글</title>
    <title xml:lang="en">Recent Posts</title>
    <description xml:lang="ko">최근 게시물 위젯</description>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author email_address="me@example.com">
        <name xml:lang="ko">Me</name>
    </author>

    <extra_vars>
        <group>
            <title xml:lang="ko">추출 대상</title>
            <var id="module_srls" type="text">
                <name xml:lang="ko">모듈 srl 목록</name>
                <description xml:lang="ko">쉼표로 구분</description>
            </var>
            <var id="list_count" type="text" default="5">
                <name xml:lang="ko">출력 개수</name>
            </var>
            <var id="sort_index" type="select" default="list_order">
                <name xml:lang="ko">정렬</name>
                <options>
                    <value>list_order</value>
                    <name xml:lang="ko">기본 정렬</name>
                </options>
                <options>
                    <value>readed_count</value>
                    <name xml:lang="ko">조회수</name>
                </options>
            </var>
        </group>
    </extra_vars>
</widget>
```

### `<extra_vars>` 그룹

위젯은 `<group>` 단위로 변수 묶을 수 있음. 관리자 UI에서 시각적 그루핑.

### `<var id="...">`

위젯의 표준 식별자는 `id=` 속성이다 (위젯 출력 시 `$args->{id}`로 접근). 파서는 하위 호환을 위해 `<id>` 자식, 그다음 `name=` 속성도 fallback으로 읽지만 신규 위젯은 `id=`를 사용한다.

### `<options>`

```xml
<var id="x" type="select">
    <name xml:lang="ko">옵션</name>
    <options>
        <value>a</value>
        <name xml:lang="ko">옵션 A</name>
    </options>
    <options>
        <value>b</value>
        <name xml:lang="ko">옵션 B</name>
    </options>
</var>
```

위젯의 `<options>` 값은 위 예제처럼 `<value>` **자식 요소**에 둔다. `WidgetInfoParser`가 사용하는 widget 분기에서는 `<options value="...">` 속성을 읽지 않는다. 반대로 모듈 스킨·레이아웃 등 다른 확장점의 옵션 문법은 서로 다를 수 있으므로 그대로 복사하지 않는다.

## `<name>.class.php`

```php
<?php
class MyWidget extends WidgetHandler
{
    /**
     * 위젯 실행. HTML 문자열을 return (echo 금지).
     *
     * @param object $args 사용자 입력 (info.xml extra_vars + skin/colorset 포함)
     * @return string
     */
    public function proc($args)
    {
        // 데이터 조회
        $list_count = (int)($args->list_count ?? 5);
        $output = executeQueryArray('widgets.mywidget.getRecentDocuments', $args);
        $documents = $output->data ?? [];

        // 컨텍스트에 넘기기
        Context::set('documents', $documents);
        Context::set('widget_args', $args);

        // 스킨 템플릿 컴파일
        $tpl_path = sprintf('%sskins/%s', $this->widget_path, $args->skin);
        $oTemplate = TemplateHandler::getInstance();
        return $oTemplate->compile($tpl_path, '1');     // 1.html
    }
}
```

### `$args` 속성과 기본값

`WidgetController::execute()`가 `getCache()`를 거쳐 실행할 때, `info.xml`의 extra_vars 중 누락된 값은 각 `default`로 채운다. 반면 아래 공통 속성은 모두가 자동 선택되는 것이 아니라 위젯 코드 생성 UI나 호출자가 전달하는 실행 인자다.

| 속성 | 의미 |
|---|---|
| `$args->skin` | 호출자가 선택해야 하는 스킨. 코드 생성 액션도 값이 없으면 오류를 반환하며 런타임이 임의 스킨을 선택하지 않음 |
| `$args->colorset` | 호출값, 누락 시 `execute()`가 빈 문자열로 초기화 |
| `$args->widget_padding_*` | 호출값. 누락 시 위젯 래퍼 계산에서 0으로 처리 |
| `$args->widget_sequence` / `$args->widget_cache` | 누락 시 0 |
| 사용자 정의 var | `info.xml` extra_vars. 누락 시 `getCache()`가 XML의 `default`를 적용 |

> 위젯 제목/부가정보는 `$args`가 아니라 위젯스타일의 `widgetstyle_extra_var`(예: `ws_title`)로 노출된다.

### `WidgetHandler::$widget_path`

위젯 모듈(`WidgetController::getWidgetObject()`)이 채워주는 위젯 디렉토리 경로(`./widgets/<name>/` 상대경로). 스킨 디렉토리 빌드에 사용.

## 스킨

위젯도 스킨을 갖는다. `widgets/<name>/skins/<skin>/skin.xml` + 진입 템플릿.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<skin version="0.2">
    <title xml:lang="ko">기본 스킨</title>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
    <extra_vars>
        <var name="thumbnail" type="select" default="N">
            <title xml:lang="ko">썸네일</title>
            <options value="Y"><title xml:lang="ko">사용</title></options>
            <options value="N"><title xml:lang="ko">사용 안 함</title></options>
        </var>
    </extra_vars>
</skin>
```

> 위젯 스킨의 `<extra_vars>` 값은 위젯 코드 생성 UI에서 입력받지 못하며 실행 시 $args로 자동 주입되지 않는다(모듈 스킨과 달리 미배선). 템플릿에서 쓰려면 해당 값을 위젯 마크업 속성으로 직접 넣거나 위젯 클래스 proc()에서 스킨 정보를 읽어 Context::set 해야 하고, skin.xml의 default 값도 적용되지 않는다.

진입 템플릿 (예: `1.html`):

```html
<ul class="recent-posts">
    <!--@foreach($documents as $doc)-->
    <li>
        <a href="{getUrl('document_srl', $doc->document_srl)}">
            {cut_str($doc->title, 30)}
        </a>
        <!--@if($widget_args->thumbnail == 'Y')-->
            <img src="{$doc->thumbnail_url}" />
        <!--@end-->
    </li>
    <!--@end-->
</ul>
```

## 위젯 호출

### 본문에서 (위젯 코드)

WYSIWYG 에디터에서 "위젯 추가" UI로 삽입하면 다음 형식의 마크업이 본문에 들어간다:

```html
<img class="zbxe_widget_output" widget="mywidget"
     skin="default" colorset="white" list_count="10" module_srls="3,5" />
```

위젯 모듈이 `conf/module.xml`에 `before display` 트리거로 등록한 `WidgetController::triggerWidgetCompile()` → `transWidgetCode()`가 이를 감지해 위젯을 실행하고 결과 HTML로 치환한다 (`modules/widget/widget.controller.php:271`). (`Context::transContent()`는 현재 인자를 그대로 반환하는 deprecated 스텁이다.)

### PHP에서 수동 호출

직접 `new MyWidget()`를 호출하면 클래스 로드·`widget_path` 설정·XML 기본값·캐시·자원 복원·위젯스타일·래퍼·디버그 측정을 모두 우회한다. 특별한 이유가 없다면 위젯 모듈의 실행 경로를 사용한다.

```php
$args = new stdClass;
$args->skin = 'default';
$args->list_count = 5;
$args->module_srls = '3,5';

$oWidgetController = getController('widget');
$html = $oWidgetController->execute('mywidget', $args);
echo $html;
```

`execute($widget, $args, $javascript_mode = false, $escaped = true)`는 위젯 본문뿐 아니라 패딩 래퍼와 지정된 위젯스타일까지 포함한 최종 HTML을 반환한다. 이미 URL decode가 끝난 프로그램 내부 값이라면 네 번째 인자를 `false`로 전달할 수 있다.

## 위젯 페이지 (페이지 모듈과 결합)

`modules/page/`의 `widget` 타입 페이지는 본문 자체가 위젯 마크업의 모음이다. 페이지 편집기에서 시각적으로 위젯을 배치.

## queries/

위젯도 자체 XML 쿼리를 가질 수 있다.

```
widgets/mywidget/queries/getRecentDocuments.xml
```

호출: `executeQuery('widgets.mywidget.getRecentDocuments', $args)` (위젯 쿼리는 `widgets.<위젯명>.<쿼리명>` 형태의 3단계 ID로 호출해야 `widgets/<위젯명>/queries/` 아래를 찾는다. 2단계 ID는 `modules/` 아래로 해석되어 실패한다).

## 최소 예제

### `widgets/hello/conf/info.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widget version="0.2">
    <title xml:lang="ko">Hello</title>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
    <extra_vars>
        <var id="greeting" type="text" default="Hello">
            <name xml:lang="ko">인사말</name>
        </var>
    </extra_vars>
</widget>
```

### `widgets/hello/hello.class.php`

```php
<?php
class Hello extends WidgetHandler
{
    public function proc($args)
    {
        $greeting = isset($args->greeting) && $args->greeting !== '' ? $args->greeting : 'Hello';
        Context::set('greeting', $greeting);
        $skin = ($args->skin ?? '') ?: 'default';
        $tpl_path = sprintf('%sskins/%s', $this->widget_path, $skin);
        return TemplateHandler::getInstance()->compile($tpl_path, '1');
    }
}
```

### `widgets/hello/skins/default/skin.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<skin version="0.2">
    <title xml:lang="ko">기본</title>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
</skin>
```

### `widgets/hello/skins/default/1.blade.php`

```blade
<div class="hello-widget">{{ $greeting }}!</div>
```

설치:
1. 파일 작성.
2. 관리자 → 위젯 → 새 위젯 인식.
3. 페이지 콘텐츠 또는 본문에 위젯 추가.

## 위젯 캐싱

위젯 마크업의 `widget_cache` 속성(예: `widget_cache="1m"`)을 지정하면 `WidgetController::getCache()`가 위젯별 캐싱을 수행한다. `s`/`m`/`h`/`d` 접미사를 지원하며, 접미사가 없는 숫자는 하위 호환을 위해 **분 단위**로 해석한다. 0은 캐시 비활성이다. 자주 변하지 않는 위젯은 캐싱 권장.

내장 캐시는 HTML뿐 아니라 위젯 실행 중 `Context::loadFile()`로 등록한 자원 목록도 함께 저장했다가 cache hit 시 다시 로드한다. `proc()` 안에서 최종 HTML만 별도 `Cache::set()`하는 방식은 이후 요청에서 CSS/JS 등록이 빠질 수 있으므로, 전체 출력 캐시는 `widget_cache`에 맡기고 필요할 때만 DB 조회 결과 같은 내부 데이터 단위를 별도로 캐시한다.

## 디버깅

- `config('debug.log_slow_widgets')` 임계 초과 시 자동 로깅.
- `Rhymix\Framework\Debug::addWidget(['name' => $name, 'elapsed_time' => $elapsed])`로 수동 기록 가능.

## 다음 문서

- 위젯스타일 (데코레이터): [widgetstyle.md](widgetstyle.md)
- 페이지 모듈 (위젯 페이지): [../28-modules/page.md](../28-modules/page.md)
- 위젯 관리 모듈: [../28-modules/widget.md](../28-modules/widget.md)
- 코어 위젯 카탈로그: [../30-widgets/](../30-widgets/)
