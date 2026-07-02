# 27.4 모듈 스킨 (Module Skin)

모듈의 본문 영역 HTML 템플릿 묶음. PC는 `skins/`, 모바일은 `m.skins/`에 위치.

## 디렉토리 구조

```
modules/<module>/
├── skins/<skin>/              # PC
│   ├── skin.xml               # [필수] 메타 + extra_vars + colorset
│   ├── list.html              # 모듈마다 다른 진입 템플릿
│   ├── view.html
│   ├── _header.html           # 부분 템플릿 (선택)
│   ├── _footer.html
│   └── css/, js/, images/
└── m.skins/<mskin>/           # 모바일 (동일 구조)
```

## skin.xml

`common/framework/parsers/SkinInfoParser.php`가 파싱.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<skin version="0.2">
    <title xml:lang="ko">내 스킨</title>
    <title xml:lang="en">My Skin</title>
    <description xml:lang="ko">설명…</description>
    <version>1.0.0</version>
    <date>2026-05-16</date>
    <author email_address="me@example.com">
        <name xml:lang="ko">홍길동</name>
    </author>

    <extra_vars>
        <var name="show_thumbnail" type="select" default="Y">
            <title xml:lang="ko">썸네일 표시</title>
            <options value="Y"><title xml:lang="ko">사용</title></options>
            <options value="N"><title xml:lang="ko">사용 안 함</title></options>
        </var>
        <var name="thumbnail_width" type="text" default="200">
            <title xml:lang="ko">썸네일 너비</title>
        </var>
    </extra_vars>

    <colorset>
        <color name="white"><title xml:lang="ko">화이트</title></color>
        <color name="dark"><title xml:lang="ko">다크</title></color>
    </colorset>
</skin>
```

extra_vars/colorset 구조는 레이아웃과 동일. 자세히는 [layout.md](layout.md).

## 모듈별 진입 템플릿명

각 모듈은 자체 템플릿명 규약을 가진다.

### board (게시판)

| 템플릿 | 용도 |
|---|---|
| `list.html` | 글 목록 (글 상세는 별도 템플릿 없이 `_read.html`을 include) |
| `_read.html` | 글 상세 본문 (`list.html`이 `$oDocument->isExists()`일 때 include) |
| `write_form.html` | 글쓰기 폼 |
| `comment.html` | 댓글 목록 |
| `comment_form.html` | 댓글 폼 |
| `input_password_form.html` | 비밀글 비밀번호 입력 |
| `delete_form.html` | 글 삭제 확인 |
| `delete_comment_form.html` | 댓글 삭제 |
| `delete_trackback_form.html` | 트랙백 삭제 |
| `tag_list.html` | 태그 목록 |
| `_header.html`, `_footer.html`, `_comment.html` | 부분 템플릿 |

글 상세는 `view.html` 같은 별도 진입 템플릿이 없다. `list.html`이 문서가 존재하면 `_read.html`을 include해 목록과 같은 진입점에서 상세를 렌더한다 (`board.view.php:224` → `list.html:2`). 댓글 목록 템플릿명은 `comment.html`이며 `board.view.php:844`에서 지정된다. RSS/Atom은 board 스킨이 아니라 별도 `rss` 모듈이 처리한다.

### member (회원)

| 템플릿 | 용도 |
|---|---|
| `login_form.html` | 로그인 |
| `signup_form.html` | 가입 |
| `member_info.html` | 회원 정보 |
| `modify_info.html` | 정보 수정 |
| `find_member_account.html` | 계정 찾기 |

### page (페이지)

| 템플릿 | 용도 |
|---|---|
| `content.html` | 페이지 본문 (옵션 — 페이지 콘텐츠는 보통 위젯 페이지로 직접 작성) |

### document / file / comment

이들은 보통 board 등의 보조로 동작하므로 자체 스킨이 거의 없다.

자세한 진입 템플릿 목록은 각 모듈 문서 ([28-modules/](../28-modules/)) 참고.

## 스킨 적용 알고리즘

`ModuleObject::setLayoutAndTemplatePaths()` (`ModuleObject.class.php:697`):

```
PC:
    skin = config.skin or 'default'
    if skin == '/USE_DEFAULT/': skin = ModuleModel::getModuleDefaultSkin(module, 'P')
    template_path = "<module_path>/skins/<skin>/"
    if not exists: template_path = "<module_path>/skins/default/"

Mobile:
    mskin = config.mskin or 'default'
    if mskin == '/USE_DEFAULT/': mskin = ModuleModel::getModuleDefaultSkin(module, 'M')
    if mskin == '/USE_RESPONSIVE/': use PC skin
    else: template_path = "<module_path>/m.skins/<mskin>/"
    if not exists: fallback to default
```

### 특수 마커

| 값 | 의미 |
|---|---|
| `'default'` | `default/` 디렉토리 |
| `'/USE_DEFAULT/'` | 모듈의 사이트 기본 스킨 |
| `'/USE_RESPONSIVE/'` | (mskin만) PC 스킨 사용 |

## 부분 템플릿 인클루드

```html
<!-- v1 -->
<include target="_header.html" />
<include target="_footer.html" />

<!-- v2 -->
@include('_header')
@include('_footer')
```

같은 스킨 디렉토리 내 검색. `_` prefix는 관습 (직접 진입 안 함).

## 사용 가능한 변수

| 변수 | 의미 |
|---|---|
| `$module_info` | 모듈 인스턴스 정보 (extra_vars 포함, skin_vars 동기화됨) |
| `$skin_vars` | extra_vars로 정의된 값 (= `$module_info`의 부분집합) |
| `$colorset` | 선택된 컬러셋 |
| `$lang` | 다국어 객체 |
| `$logged_info`, `$is_logged`, `$user` | 사용자 정보 |
| `$grant` | 현재 사용자 권한 |
| `$mid` | 현재 mid |
| 모듈 액션이 `Context::set`한 변수들 | 예: `$documents`, `$page_navigation`, `$document`, ... |

## 게시판 스킨 표준 변수 (예시)

`modules/board/skins/default/list.html`에서 사용:

| 변수 | 의미 |
|---|---|
| `$document_list` | 글 목록 (DocumentItem array) |
| `$category_list` | 카테고리 |
| `$page_navigation` | 페이지네이션 객체 |
| `$total_count` / `$total_page` / `$page` | 페이지 정보 |
| `$module_info->use_category` | 카테고리 사용 여부 |
| `$grant->write_document` | 쓰기 권한 |

`$document`(상세 화면) 예:

```html
<h1>{$document->getTitle()}</h1>
<div class="content">{$document->getContent()|noescape}</div>
<div class="author">{$document->getNickName()}</div>
```

## 자원 로드

```html
<load target="css/style.css" />
<load target="js/skin.js" type="body" />
```

스킨 디렉토리 내 경로. `Context::loadFile`이 자동 처리.

컬러셋 기반 CSS:

```html
<load target="css/style.{$module_info->colorset}.css" />
```

## 최소 예제

### `modules/myboard/skins/simple/skin.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<skin version="0.2">
    <title xml:lang="ko">단순 스킨</title>
    <version>1.0</version>
    <date>2026-05-16</date>
    <author><name xml:lang="ko">Me</name></author>
</skin>
```

### `modules/myboard/skins/simple/list.html`

```html
<load target="css/style.css" />

<h2>{$module_info->browser_title}</h2>
<ul>
    <!--@foreach($document_list as $doc)-->
    <li>
        <a href="{getUrl('document_srl', $doc->document_srl)}">
            {$doc->getTitle()}
        </a>
    </li>
    <!--@end-->
</ul>

<div class="pagination">
    {@$page_navigation}
</div>
```

## 모바일 스킨

같은 구조를 `m.skins/`에 둔다. extra_vars/colorset도 별도.

```
modules/myboard/m.skins/simple/
├── skin.xml
└── list.html
```

## skin.xml 다국어

XE 호환을 위해 `<title xml:lang="ko">` 다국어를 항상 정의. 미정의 시 기본 lang 폴백.

## 다음 문서

- 레이아웃: [layout.md](layout.md)
- 위젯: [widget.md](widget.md)
- 템플릿 엔진: [../09-templates-and-skins.md](../09-templates-and-skins.md)
- 모바일 감지: [../23-mobile-detection.md](../23-mobile-detection.md)
