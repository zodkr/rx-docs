# member_extra_info (애드온)

## 개요

- **목적**: 본문 내 `member_<srl>` 클래스(`<div>`/`<span>`/`<a>`)를 찾아 회원의 이미지 이름/이미지 마크로 자동 치환.

## hook 위치

`before_display_content` — HTML 본문 문자열을 정규식으로 직접 가공. admin 페이지 / 비-HTML 응답 / 크롤러는 제외.

## 동작

`addons/member_extra_info/member_extra_info.addon.php` (실제 코드):

```php
if($called_position != "before_display_content"
    || Context::get('act') == 'dispPageAdminContentModify'
    || Context::getResponseMethod() != 'HTML'
    || isCrawler())
{
    return;
}
require_once __DIR__ . '/member_extra_info.lib.php';

$temp_output = preg_replace_callback(
    '!<(div|span|a)([^\>]*)member_([0-9]+)([^\>]*)>(.*?)\<\/(div|span|a)\>!is',
    'memberTransImageName',
    $output
);
if ($temp_output) {
    $output = $temp_output;
}
```

`member_extra_info.lib.php`의 `memberTransImageName()` 콜백이 `MemberController::transImageName()`을 호출해 이미지 이름/마크가 설정된 회원이면 해당 부분을 이미지로 교체한다.

## 관련

- member: [../28-modules/member.md](../28-modules/member.md)
- communication: [../28-modules/communication.md](../28-modules/communication.md)
