# 27.3 레이아웃 (Layout)

레이아웃은 사이트 전체의 뼈대 HTML. 모듈 본문이 `{$content}` 자리에 삽입된다.

## 디렉토리 구조

```
layouts/<name>/                # PC
├── conf/info.xml              # [필수]
├── layout.html                # [필수] 진입 템플릿
├── <name>.layout.css          # [선택]
├── <name>.layout.js           # [선택]
├── thumbnail.png              # [권장] 미리보기 (240x180 권장)
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

    <colorset>
        <color name="white"><title xml:lang="ko">화이트</title></color>
        <color name="dark"><title xml:lang="ko">다크</title></color>
    </colorset>
</layout>
```

### `<menus>`

관리자가 레이아웃에 메뉴 트리를 할당. 템플릿에서 `$<menu_name>->list`로 접근 (예: `$GNB->list`).

| 속성 | 의미 |
|---|---|
| `name` | 메뉴 ID (템플릿 변수명) |
| `maxdepth` | 최대 depth (관리자 UI 제한) |

(parser는 `name`/`maxdepth`/`title`만 읽는다 — `default` 같은 추가 속성은 무시됨.)

### `<extra_vars>`

| 속성 | 의미 |
|---|---|
| `name` | 변수 ID. 템플릿에서 `$layout_info->{name}` |
| `type` | `image`/`text`/`textarea`/`select`/`filebox`/`color`/`date`/`radio`/`checkbox` |

옵션이 있는 type은 `<options>` 또는 `<options value="...">` 자식.

### `<colorset>`

색상 테마. 관리자가 선택. 템플릿에서 `$layout_info->colorset` 또는 `$colorset`.

## layout.html

레이아웃 진입 템플릿. 본문 자리에 `{$content}`를 둔다.

### v1 예시

```html
<!doctype html>
<html lang="{$lang_type}">
<head>
    <title>{$site_title}</title>
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
                <li><a href="{$item['url']}">{$item['link']}</a></li>
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

### v2 (Blade) 예시

```blade
<!doctype html>
<html lang="{{ $lang_type }}">
<head>
    <title>{{ $site_title }}</title>
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
                <li><a href="{{ $item['url'] }}">{{ $item['link'] }}</a></li>
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
| `$user` | 사용자 객체 |
| `$colorset` | 선택된 컬러셋 |
| `$mid` | 현재 mid |
| `$site_title` | 사이트 제목 |
| `$module_info->browser_title` | 현재 페이지 타이틀 |
| `$<menu_name>` | `<menus>`에 정의된 메뉴 (예: `$GNB`, `$LNB`) |

### 메뉴 객체 구조

```php
$GNB->list = [
    'menu_srl_1' => [
        'node_srl' => 1,
        'link' => '메뉴1',
        'url' => '/free',
        'text' => '메뉴1',
        'open_window' => 'N',
        'list' => [ /* 하위 메뉴 */ ],
        'selected' => true,         // 현재 페이지가 이 메뉴인가
        'expand' => true,
    ],
    ...
];
```

## `<load>` 자원 로드

```html
<load target="default.layout.css" media="screen" />
<load target="default.layout.js" type="body" />
<load target="./external.css" />
```

상대 경로면 레이아웃 디렉토리 기준. 절대 경로(`./`로 시작)면 `RX_BASEDIR` 기준.

자동으로 mtime 쿼리스트링(`?v=12345`) 부여 → 캐시 무효화.

## 모바일 레이아웃

`m.layouts/<name>/`. PC 레이아웃과 별도. 같은 디렉토리 구조.

```php
$module_info->layout_srl       // PC 레이아웃 srl
$module_info->mlayout_srl      // 모바일 레이아웃 srl
```

`mlayout_srl == -2`이면 PC 레이아웃을 그대로 사용 (반응형).

## 사용자 편집 레이아웃

레이아웃 자체를 관리자가 드래그앤드롭으로 편집 가능 (`modules/layout/`). 편집 결과는 `files/cache/layout/edited_<srl>.html`에 저장되며 `ModuleObject::edited_layout_file`로 적용.

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
    <title>{$layout_info->SITE_TITLE ?: $site_title}</title>
</head>
<body>
    <header>
        <h1>{$layout_info->SITE_TITLE}</h1>
        <nav>
            <!--@foreach($GNB->list as $item)-->
            <a href="{$item['url']}">{$item['link']}</a>
            <!--@end-->
        </nav>
    </header>
    <main>{$content}</main>
</body>
</html>
```

설치:
1. 위 두 파일 작성.
2. 관리자 → 레이아웃 → 새 레이아웃 자동 인식 → 설치.
3. 도메인 또는 모듈 설정에서 레이아웃 적용.

## 다음 문서

- 모듈 스킨 (본문측): [module-skin.md](module-skin.md)
- 위젯 (레이아웃 내 동적): [widget.md](widget.md)
- 모바일: [../23-mobile-detection.md](../23-mobile-detection.md)
- 메뉴 모듈: [../28-modules/menu.md](../28-modules/menu.md)
