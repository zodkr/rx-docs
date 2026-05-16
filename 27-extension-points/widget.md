# 27.5 위젯 (Widget)

위젯은 **레이아웃이나 콘텐츠 안에 끼워 넣을 수 있는 동적 컴포넌트**. 예: 최근 게시물, 로그인 박스, 사이트 카운터.

## 디렉토리 구조

```
widgets/<name>/                # 또는 plugins/<name>/widgets/<name>/
├── <name>.class.php           # [필수] WidgetHandler 상속
├── conf/info.xml              # [필수]
├── lang/<langtype>.php        # [권장]
├── queries/*.xml              # [선택]
├── skins/<skin>/              # [필수] 최소 1개 스킨
│   ├── skin.xml
│   ├── 1.html (또는 다른 이름)
│   └── images/, css/, js/
```

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

위젯은 `name=` 대신 `id=` 속성을 쓴다 (위젯 출력 시 `$args->{id}`로 접근).

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
        $output = executeQueryArray('mywidget.getRecentDocuments', $args);
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

### `$args` 기본 속성

`info.xml`의 extra_vars + 다음 자동 주입.

| 속성 | 의미 |
|---|---|
| `$args->skin` | 사용자가 선택한 스킨 |
| `$args->colorset` | 컬러셋 |
| `$args->widget_padding_*` | 위젯 박스 패딩 |
| `$args->widget_title` | 위젯 제목 (위젯스타일이 사용) |
| 사용자 정의 var | extra_vars로 정의된 모든 변수 |

### `WidgetHandler::$widget_path`

부모 클래스가 자동 채워주는 위젯 디렉토리 절대경로. 스킨 디렉토리 빌드에 사용.

## 스킨

위젯도 스킨을 갖는다. `widgets/<n>/skins/<skin>/skin.xml` + 진입 템플릿.

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

`Context::transContent()` (모듈 처리 중)가 이를 감지해 위젯을 실행하고 결과 HTML로 치환한다.

### 레이아웃/페이지에서 (수동 호출)

```php
$args = new stdClass;
$args->skin = 'default';
$args->list_count = 5;
$args->module_srls = '3,5';

$oWidget = new MyWidget();
$oWidget->widget_path = RX_BASEDIR . 'widgets/mywidget/';
$html = $oWidget->proc($args);
echo $html;
```

또는 위젯 모듈의 헬퍼:

```php
$oWidgetController = getController('widget');
$html = $oWidgetController->execute($widget_sequence_args);
```

## 위젯 페이지 (페이지 모듈과 결합)

`modules/page/`의 `widget` 타입 페이지는 본문 자체가 위젯 마크업의 모음이다. 페이지 편집기에서 시각적으로 위젯을 배치.

## queries/

위젯도 자체 XML 쿼리를 가질 수 있다.

```
widgets/mywidget/queries/getRecentDocuments.xml
```

호출: `executeQuery('mywidget.getRecentDocuments', $args)`.

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
        Context::set('greeting', $args->greeting ?: 'Hello');
        $tpl_path = sprintf('%sskins/%s', $this->widget_path, $args->skin ?: 'default');
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

### `widgets/hello/skins/default/1.html`

```html
<div class="hello-widget">{$greeting}!</div>
```

설치:
1. 파일 작성.
2. 관리자 → 위젯 → 새 위젯 인식.
3. 페이지 콘텐츠 또는 본문에 위젯 추가.

## 위젯 캐싱

`getWidgetCache($args, $widget_name)` 등으로 위젯별 캐싱 가능. 자주 변하지 않는 위젯은 캐싱 권장.

```php
public function proc($args)
{
    $cache_key = 'hello:' . md5(serialize($args));
    if ($cached = Cache::get($cache_key)) {
        return $cached;
    }
    // ... 처리 ...
    $html = TemplateHandler::getInstance()->compile($tpl_path, '1');
    Cache::set($cache_key, $html, 600);
    return $html;
}
```

## 디버깅

- `config('debug.log_slow_widgets')` 임계 초과 시 자동 로깅.
- `Debug::addWidget($name, $elapsed)`로 수동 기록 가능.

## 다음 문서

- 위젯스타일 (데코레이터): [widgetstyle.md](widgetstyle.md)
- 페이지 모듈 (위젯 페이지): [../28-modules/page.md](../28-modules/page.md)
- 위젯 관리 모듈: [../28-modules/widget.md](../28-modules/widget.md)
- 코어 위젯 카탈로그: [../30-widgets/](../30-widgets/)
