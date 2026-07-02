# 23. 모바일 감지

`classes/mobile/Mobile.class.php`. 진입점은 정적 메서드 `Mobile::isFromMobilePhone()`.

## 우선순위 (`Mobile::isFromMobilePhone`)

```
1. config('mobile.enabled') == false
   → 항상 PC

2. Context::get('full_browse') == true 또는 'FullBrowse' 쿠키
   → PC 강제 (사용자가 "PC 버전 보기" 선택)

3. URL 파라미터 m=0/1
   → 명시 지정

4. rx_uatype 쿠키 (이전 판단 결과 캐시)
   → 캐시된 결과 사용 (UA 해시 일치 시)

5. Rhymix\Framework\UA::isMobile() / isTablet()
   → User-Agent 기반 자동 감지

6. 결과를 rx_uatype 쿠키에 저장 (다음 요청 캐싱)
```

## 태블릿 분기

`config('mobile.tablets')` :

- `true` — 태블릿도 모바일로 처리.
- `false` (기본) — 태블릿은 PC로 처리.

## User-Agent 파싱

`Rhymix\Framework\UA` (480줄). 정규식 기반 분류.

```php
Rhymix\Framework\UA::isMobile(?string $ua = null): bool;     // 휴대전화
Rhymix\Framework\UA::isTablet(?string $ua = null): bool;     // 태블릿
Rhymix\Framework\UA::isRobot(?string $ua = null): bool;      // 봇/크롤러
Rhymix\Framework\UA::getLocale(?string $header = null): string;  // 브라우저 우선 locale
Rhymix\Framework\UA::getColorScheme(): string;               // 'light' / 'dark' / 'auto'

// OS/브라우저/디바이스/버전을 한 번에
$info = Rhymix\Framework\UA::getBrowserInfo(?string $ua = null): UA;
// $info->os, $info->os_version, $info->device, $info->browser, $info->version
```

User-Agent가 비어 있으면 `$_SERVER['HTTP_USER_AGENT']` 사용.

## 쿠키 캐싱

`rx_uatype` 쿠키 값 형식: `<ua_hash>:<result>`

- `<ua_hash>` — UA 문자열의 짧은 해시.
- `<result>` — `0` (PC) 또는 `1` (Mobile).

다음 요청 시 UA 해시가 일치하면 캐시된 결과 즉시 사용 → UA 정규식 매칭 회피.

## 모듈 동작 차이

### 스킨 디렉토리

- PC: `modules/<m>/skins/<skin>/`.
- 모바일: `modules/<m>/m.skins/<mskin>/`.

`ModuleObject::setLayoutAndTemplatePaths()`가 디바이스에 맞는 디렉토리를 선택.

### 레이아웃 srl

- `module_info->layout_srl` — PC 레이아웃.
- `module_info->mlayout_srl` — 모바일 레이아웃.

특수값:

| 값 | 의미 |
|---|---|
| `0` 또는 양수 | 지정 레이아웃 |
| `-1` | 사이트 기본 |
| `-2` (mlayout_srl만) | PC 레이아웃 공유 |

### 응답형 마커 (`/USE_RESPONSIVE/`)

`mskin === '/USE_RESPONSIVE/'`로 설정하면 모바일에서도 PC 스킨을 사용한다. 단일 스킨으로 반응형 디자인을 구현할 때.

### 기본 마커 (`/USE_DEFAULT/`)

`skin === '/USE_DEFAULT/'`이면 모듈의 기본 스킨을 사용 (사이트 전역 설정).

### 모바일 컨트롤러

`modules/<m>/<m>.mobile.php`에 `<Module>Mobile` 클래스가 있으면 모바일 요청 시 우선 인스턴스화된다. 모바일 전용 액션을 작성하기 위함.

```php
class FooMobile extends FooView
{
    public function dispFooIndex()
    {
        // 모바일 전용 처리
        $this->setTemplateFile('index_mobile');
    }
}
```

대부분의 모듈은 PC/모바일 동일 로직을 쓰고 스킨만 분리해서 모바일 컨트롤러가 없음.

## 모바일 강제 토글

### URL 파라미터

```
https://example.com/?m=1     ← 모바일 강제
https://example.com/?m=0     ← PC 강제
```

쿠키에도 저장되어 다음 요청부터 유지.

### 사용자 토글 UI

레이아웃에서:

```html
<a href="{getUrl('m', '0')}">PC 버전 보기</a>
<a href="{getUrl('m', '1')}">모바일 버전 보기</a>
```

## viewport 메타 태그

`config('mobile.viewport')`는 **viewport content 문자열** 자체다. 이 값은 모든 HTML 응답의 공통 레이아웃(`common/tpl/common_layout.html:9`)에 PC/모바일 구분 없이 항상 다음 형식으로 삽입된다. 값이 지정되지 않으면(null) `HTMLDisplayHandler::DEFAULT_VIEWPORT` 상수로 폴백한다 (빈 문자열이면 `content=""`로 출력).

```html
<meta name="viewport" content="{{ config('mobile.viewport') ?? HTMLDisplayHandler::DEFAULT_VIEWPORT }}" />
```

`common/defaults/config.php`의 기본값:

```
width=device-width, initial-scale=1.0, user-scalable=yes
```

별도의 `mobile.viewport_content` 키는 없다 — viewport 활성/비활성과 내용을 한 키로 관리한다.

## Mobile 클래스의 deprecated 메서드

`@deprecated`로 표시된 메서드는 사용하지 않음 (예: 일부 옛 헬퍼). 신형 코드는 `Mobile::isFromMobilePhone()`만 사용.

## 봇 분기

`Rhymix\Framework\UA::isRobot()`로 봇 감지. 봇은 PC로 처리된다. `seo` 설정에는 robots/canonical 관련 키가 없다 — robots `noindex` 메타 태그는 액션의 `meta-noindex` 속성(`module.xml`)에 따라 `Context::addMetaTag('robots', 'noindex')`로 출력되고(`classes/module/ModuleHandler.class.php:364`; admin 액션도 동일), 모듈의 `robots_tag === 'noindex'` 설정은 이와 별도로 `X-Robots-Tag: noindex` HTTP 헤더를 출력하며(`classes/display/DisplayHandler.class.php:128`), canonical URL은 `HTMLDisplayHandler`에서 `Context::setCanonicalURL()`로 seo 설정과 무관하게 설정된다(`classes/display/HTMLDisplayHandler.php:565`). `config('security.nofollow')`는 이와 별개로 본문 콘텐츠 내 링크에 `rel="nofollow"`를 붙이는 옵션이다(`common/framework/filters/HTMLFilter.php:230`).

## 다음 문서

- 라이프사이클: [04-bootstrap-and-request-lifecycle.md](04-bootstrap-and-request-lifecycle.md)
- 모듈 스킨: [27-extension-points/module-skin.md](27-extension-points/module-skin.md)
- 레이아웃: [27-extension-points/layout.md](27-extension-points/layout.md)
