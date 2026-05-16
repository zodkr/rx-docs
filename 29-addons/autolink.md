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
- 괄호/대괄호/`<>`/한글 1-3자 접미사 자동 분리 처리.

## 장점

- 서버 비용 0.
- 본문 원본 보존 (DB는 평문 그대로).

## 단점

- JS 비활성 사용자에게는 효과 없음.
- 검색엔진은 평문으로 인식.

## 관련

- 외부 라이브러리 위치: `addons/autolink/autolink.js`
