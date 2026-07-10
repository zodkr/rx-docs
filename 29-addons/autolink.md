# autolink (애드온)

## 개요

- **목적**: 본문/댓글의 URL 문자열을 자동으로 클릭 가능한 링크로 변환.

## hook 위치

`after_module_proc` — HTML 응답일 때만 JS 로드.

## 코드

`addons/autolink/autolink.addon.php`:

```php
<?php
if (!defined('__XE__')) exit();

if ($called_position == 'after_module_proc' && Context::getResponseMethod() == 'HTML') {
    Context::loadFile(['./addons/autolink/autolink.js', 'body', '', null], true);
}
```

## 동작

서버 측에서 본문을 가공하지 않고, **클라이언트 JS**(`autolink.js`)가 DOM을 순회하며 URL 문자열을 `<a>` 태그로 치환.

- 표적: `.rhymix_content, .xe_content` 셀렉터 (`autolink.js`의 `extractTargets` 인자).
- 대상 URL 프로토콜: `https?`, `ftp`, `news`, `telnet`, `irc`, `mms`. (도메인은 점 포함 패턴 또는 IPv4 또는 `localhost`.)
- 링크가 현재 페이지와 **다른 origin**일 때만 `target="_blank"` 추가. `rel`은 추가되지 않는다.
- 본문 내 **기존 `<a>` 링크**도 클릭 시, `target` 속성이 없고 `isSameOrigin` 판별상 다른 origin이면 `target="_blank"`가 부여된다(단, `javascript:`·`mailto:`로 시작하거나 `#`를 포함하는 링크는 제외) (`addons/autolink/autolink.js:106-115`).
- 괄호/대괄호/`<>`/한글 1-3자 접미사 자동 분리 처리. 또한 매칭된 URL 안에 `&lt;`·`&gt;`·`&quot;` HTML 엔티티가 나타나면 그 지점부터 끝까지를 접미사로 분리한다(escape된 HTML 코드 예시의 과도한 매칭 방지, 커밋 `03d6254f1`). 한글 접미사와 엔티티 접미사 처리는 독립적인 두 개의 `if`로 순차 적용된다 (`addons/autolink/autolink.js:54-61`).

## 장점

- 서버는 본문 HTML을 링크로 변환하지 않고 JS 자원만 등록한다.
- 본문 원본 보존 (DB와 초기 HTML에는 평문 URL이 그대로 남음).

## 단점

- JS 비활성 사용자에게는 효과가 없다.
- 링크는 클라이언트에서 DOM을 가공한 뒤 생기므로, JS를 실행하지 않는 클라이언트가 받는 초기 HTML에는 평문 URL만 있다.

## 관련

- 클라이언트 스크립트 위치: `addons/autolink/autolink.js`
