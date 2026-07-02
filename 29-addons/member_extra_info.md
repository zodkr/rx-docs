# member_extra_info (애드온)

## 개요

- **목적**: 본문 내 `member_<srl>` 클래스(`<div>`/`<span>`/`<a>`)를 찾아 회원의 이미지 이름/이미지 마크 및 소속 그룹의 이미지 마크로 자동 치환.

## hook 위치

`before_display_content` — HTML 본문 문자열을 정규식으로 직접 가공. page 콘텐츠 편집 화면(act가 `dispPageAdminContentModify`) / 비-HTML 응답 / 크롤러는 제외.

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

`member_extra_info.lib.php`의 `memberTransImageName()` 콜백이 회원의 이미지 이름/이미지 마크 및 소속 그룹의 이미지 마크가 설정된 경우 해당 부분을 이미지로 교체한다. 이 콜백은 별도 메서드를 호출하지 않고 함수 내부에서 직접 처리하며, `getModel('member')`로 얻은 MemberModel의 `getMemberConfig()`(image_name/image_mark 설정 확인)·`getGroupImageMark()`와 `files/member_extra_info/image_name/`·`image_mark/` 경로의 gif 파일 존재 여부(`file_exists`)를 근거로 치환한다.

## 관련

- member: [../28-modules/member.md](../28-modules/member.md)
- communication: [../28-modules/communication.md](../28-modules/communication.md)
