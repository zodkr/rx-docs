# point_level_icon (애드온)

## 개요

- **목적**: 회원 닉네임 옆에 포인트 레벨에 따른 아이콘 자동 표시.

## hook 위치

`before_display_content` — HTML 본문 문자열을 정규식으로 가공. admin 페이지 / 비-HTML 응답 / 크롤러는 제외.

## 동작

본문/댓글의 `member_<srl>` 클래스(`<div>`/`<span>`/`<a>`)를 찾아 회원 포인트로 산출한 레벨 아이콘을 삽입.

`addons/point_level_icon/point_level_icon.addon.php` (실제 코드):

```php
if($called_position != "before_display_content"
    || Context::get('act') == 'dispPageAdminContentModify'
    || Context::getResponseMethod() != 'HTML'
    || isCrawler())
{
    return;
}
require_once __DIR__ . '/point_level_icon.lib.php';

$temp_output = preg_replace_callback(
    '!<(div|span|a)([^\>]*)member_([0-9\-]+)([^\>]*)>(.*?)\<\/(div|span|a)\>!is',
    function($matches) use($addon_info) {
        return pointLevelIconTrans($matches, $addon_info);
    },
    $output
);
if ($temp_output) {
    $output = $temp_output;
}
```

`point_level_icon.lib.php`의 `pointLevelIconTrans()`가 `PointModel::getPoint()`로 포인트를 읽어 레벨 아이콘을 prepend.

## extra_vars

- `icon_position` — 닉네임 앞/뒤.
- `icon_size` — 아이콘 크기.
- `level_icon_<N>` — 레벨별 아이콘 이미지 경로.

## 관련

- point: [../28-modules/point.md](../28-modules/point.md)
