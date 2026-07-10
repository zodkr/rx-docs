# 27.3 레이아웃 (Layout)

레이아웃은 사이트 전체의 뼈대 HTML. 모듈 본문이 `{$content}` 자리에 삽입된다.

## 디렉토리 구조

```
layouts/<name>/                # PC
├── conf/info.xml              # [필수]
├── layout.html                # [선택지 A] v1 진입 템플릿
├── layout.blade.php           # [선택지 B] v2 진입 템플릿 (둘 중 하나는 필수)
├── <name>.layout.css          # [선택]
├── <name>.layout.js           # [선택]
├── thumbnail.png              # [권장] 미리보기 (180x135 권장)
└── images/, css/, js/         # [선택] 자원

m.layouts/<name>/              # 모바일 (동일 구조)
```

## info.xml

`common/framework/parsers/LayoutInfoParser.php`가 파싱.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layout version="0.2">
    <title xml:lang="ko">내 레이아웃</title>
    <title xml:lang="en">My Layout</title>
    <description xml:lang="ko">설명…</description>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author email_address="me@example.com">
        <name xml:lang="ko">홍길동</name>
    </author>

    <menus>
        <menu name="GNB" maxdepth="2">
            <title xml:lang="ko">전역 네비게이션 바</title>
        </menu>
        <menu name="LNB" maxdepth="3">
            <title xml:lang="ko">로컬 네비게이션 바</title>
        </menu>
    </menus>

    <extra_vars>
        <var name="LOGO_IMG" type="image">
            <title xml:lang="ko">사이트 로고 이미지</title>
        </var>
        <var name="LOGO_TEXT" type="text">
            <title xml:lang="ko">사이트 로고 문자</title>
        </var>
        <var name="WEB_FONT" type="select">
            <title xml:lang="ko">웹 폰트</title>
            <options value="NO"><title xml:lang="ko">사용 안 함</title></options>
            <options value="YES"><title xml:lang="ko">'나눔고딕' 사용</title></options>
        </var>
    </extra_vars>
</layout>
```

### `<menus>`

관리자가 레이아웃에 메뉴 트리를 할당. 템플릿에서 `$<menu_name>->list`로 접근 (예: `$GNB->list`).

| 속성 | 의미 |
|---|---|
| `name` | 메뉴 ID (템플릿 변수명) |
| `maxdepth` | 레이아웃이 기대하는 최대 depth 메타데이터. 파서는 정수로 저장하지만 현재 레이아웃/메뉴 실행 경로가 트리를 잘라내거나 관리자 입력을 강제하지는 않음 |

(parser는 `name`/`maxdepth`/`title`만 읽는다 — `default` 같은 추가 속성은 무시됨.)

### `<extra_vars>`

| 속성 | 의미 |
|---|---|
| `name` | 변수 ID. 템플릿에서 `$layout_info->{name}` |
| `type` | `image`/`text`/`textarea`/`select`/`checkbox`/`radio`/`colorpicker` |

레이아웃 옵션값은 반복되는 `<options value="...">`의 `value` **속성**으로 선언한다. `LayoutInfoParser`는 위젯처럼 `<value>` 자식을 읽지 않는다. 또한 `<var default="...">`는 파서 결과의 `default` 필드에 보존되지만 현재 레이아웃 설정 UI와 `LayoutModel::getLayoutInfo()`는 이를 `value`에 자동 대입하지 않는다. 따라서 최초 저장 전에도 필요한 값은 템플릿에서 fallback을 두고, 선택형 변수는 원하는 기본 항목을 첫 번째에 배치하는 것이 안전하다.

### 색상 테마 (컬러셋)

레이아웃에는 최상위 `<colorset>` 요소가 없다 (`LayoutInfoParser`는 파싱하지 않음 — 최상위 `<colorset>`은 스킨 전용 기능이다). 색상 테마는 `type="select"`인 `<extra_vars>`로 구현하며, 관례상 `name="colorset"`을 쓴다 (`m.layouts/colorCode/conf/info.xml`). 템플릿에서는 `$layout_info->colorset`으로 접근한다.

## layout.html / layout.blade.php

레이아웃 진입 템플릿. 본문 자리에 `{$content}`를 둔다.

### v1 예시

```html
<!doctype html>
<html lang="{$lang_type}">
<head>
    <title>{Context::getSiteTitle()}</title>
    <load target="default.layout.css" />
</head>
<body>
    <header>
        <a href="{getUrl()}">
            <!--@if($layout_info->LOGO_IMG)-->
                <img src="{$layout_info->LOGO_IMG}" alt="{$layout_info->LOGO_TEXT}" />
            <!--@else-->
                <span>{$layout_info->LOGO_TEXT}</span>
            <!--@end-->
        </a>
        <nav>
            <ul>
                <!--@foreach($GNB->list as $key => $item)-->
                <li><a href="{$item['href']}">{$item['link']}</a></li>
                <!--@end-->
            </ul>
        </nav>
    </header>

    <main>
        {$content}
    </main>

    <footer>
        &copy; 2026 My Site
    </footer>
    <load target="default.layout.js" />
</body>
</html>
```

### v2 (`layout.blade.php`) 예시

```blade
<!doctype html>
<html lang="{{ $lang_type }}">
<head>
    <title>{{ Context::getSiteTitle() }}</title>
    @load('default.layout.css')
</head>
<body>
    <header>
        <a href="{{ getUrl() }}">
            @if($layout_info->LOGO_IMG)
                <img src="{{ $layout_info->LOGO_IMG }}" alt="{{ $layout_info->LOGO_TEXT }}">
            @else
                <span>{{ $layout_info->LOGO_TEXT }}</span>
            @endif
        </a>
        <nav>
            <ul>
                @foreach($GNB->list as $key => $item)
                <li><a href="{{ $item['href'] }}">{{ $item['link'] }}</a></li>
                @endforeach
            </ul>
        </nav>
    </header>
    <main>{!! $content !!}</main>
    <footer>&copy; 2026 My Site</footer>
    @load('default.layout.js')
</body>
</html>
```

## 사용 가능한 템플릿 변수

| 변수 | 의미 |
|---|---|
| `$layout_info` | extra_vars 포함, 모든 사용자 입력값 |
| `$content` | 본문 HTML (모듈 출력) |
| `$lang` | 다국어 객체 |
| `$lang_type` | 'ko'/'en'/... |
| `$logged_info` | 로그인 정보 또는 false |
| `$is_logged` | 로그인 여부 |
| `$module_info` | 현재 모듈 정보 |
| `$site_module_info` | 현재 도메인 루트 모듈 |
| `$layout_info->colorset` | 선택된 컬러셋 (extra_var로 정의한 경우) |
| `$mid` | 현재 mid |
| `Context::getSiteTitle()` | 사이트 제목 (독립 변수 `$site_title`은 없음) |
| `$module_info->browser_title` | 현재 페이지 타이틀 |
| `$<menu_name>` | `<menus>`에 정의된 메뉴 (예: `$GNB`, `$LNB`) |

### 메뉴 객체 구조

```php
$GNB->list = [
    1 => [                         // 실제 키는 menu_item_srl 정수
        'node_srl' => 1,
        'link' => '메뉴1',
        'href' => '/free',          // getSiteUrl로 생성된 완성 링크 (rewrite 설정에 따라 값이 달라짐)
        'url' => 'free',            // 관리자 입력 원본값: 내부 메뉴는 슬래시 없는 mid 문자열. 링크에는 href를 사용.
        'text' => '메뉴1',
        'open_window' => 'N',
        'list' => [ /* 하위 메뉴 */ ],
        'selected' => 1,            // 1/0, 현재 페이지가 이 메뉴인가
        'expand' => 'Y',            // 'Y'/'N'
    ],
    ...
];
```

## `<load>` 자원 로드

```html
<load target="default.layout.css" media="screen" />
<load target="default.layout.js" type="body" />
<load target="./css/extra.css" />        <!-- 레이아웃 디렉토리 기준 -->
<load target="^/common/js/common.js" />  <!-- 사이트 루트(RX_BASEDIR) 기준 -->
```

`./` 또는 접두사 없는 경로는 모두 레이아웃 디렉토리 기준이다 (`./css/extra.css` → `layouts/<name>/css/extra.css`). 사이트 루트(`RX_BASEDIR`) 자원은 `^/`(예: `^/common/js/foo.js`) 접두사나 `../../`(예: `../../common/css/xeicon/xeicon.min.css`)로 접근한다.

자동으로 mtime 쿼리스트링(`?t=12345`) 부여 → 캐시 무효화.

## 모바일 레이아웃

`m.layouts/<name>/`. PC 레이아웃과 별도. 같은 디렉토리 구조.

```php
$module_info->layout_srl       // PC 레이아웃 srl
$module_info->mlayout_srl      // 모바일 레이아웃 srl
```

`mlayout_srl == -2`이면 PC 레이아웃을 그대로 사용 (반응형).

## 사용자 편집 레이아웃

드래그앤드롭 편집은 모든 레이아웃의 공통 기능이 아니라 `type="faceoff"`인 레거시 FaceOff 레이아웃 전용이다. 현재 `procLayoutAdminInsert()`는 새 `faceoff` 인스턴스 생성을 `not supported`로 거부하고 관련 API도 deprecated 상태다. 일반 레이아웃은 관리자 설정 화면에서 `extra_vars`·메뉴·헤더 스크립트를 편집하며, 템플릿 자체를 시각적으로 재구성하지 않는다.

기존 FaceOff 인스턴스의 편집 결과는 `files/faceOff/<numbering>/layout.html`에 저장되며(예: `layout_srl=5` → `files/faceOff/005/layout.html`; `getNumberingPath`는 3자리 0채움, 1000 이상부터 디렉토리를 중첩) `ModuleObject::edited_layout_file`로 적용된다. `files/cache/layout/`에는 info.xml 파싱 결과(레이아웃 정보 객체) 캐시인 `*.cache.php`와 관리자 미리보기용 `tmp.tpl`이 저장된다. 레이아웃 템플릿 자체의 컴파일 캐시는 `files/cache/template/*.compiled.php`에 별도로 저장된다.

## 최소 예제

### `layouts/mylayout/conf/info.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layout version="0.2">
    <title xml:lang="ko">My Layout</title>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
    <menus>
        <menu name="GNB" maxdepth="2">
            <title xml:lang="ko">메뉴</title>
        </menu>
    </menus>
    <extra_vars>
        <var name="SITE_TITLE" type="text">
            <title xml:lang="ko">사이트 제목</title>
        </var>
    </extra_vars>
</layout>
```

### `layouts/mylayout/layout.html`

```html
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>{$layout_info->SITE_TITLE ?: Context::getSiteTitle()}</title>
</head>
<body>
    <header>
        <h1>{$layout_info->SITE_TITLE}</h1>
        <nav>
            <!--@foreach($GNB->list as $item)-->
            <a href="{$item['href']}">{$item['link']}</a>
            <!--@end-->
        </nav>
    </header>
    <main>{$content}</main>
</body>
</html>
```

설치:
1. 위 두 파일 작성.
2. 관리자 → 레이아웃 → 설치된 레이아웃 목록에서 자동 인식되는지 확인.
3. 해당 레이아웃을 선택해 실제 설정값을 담을 레이아웃 인스턴스를 생성.
4. 관리자 기본 디자인에서 사이트 기본 레이아웃으로 지정하거나, 각 모듈/페이지의 디자인 설정에서 적용.

## 다음 문서

- 모듈 스킨 (본문측): [module-skin.md](module-skin.md)
- 위젯 (레이아웃 내 동적): [widget.md](widget.md)
- 모바일: [../23-mobile-detection.md](../23-mobile-detection.md)
- 메뉴 모듈: [../28-modules/menu.md](../28-modules/menu.md)
