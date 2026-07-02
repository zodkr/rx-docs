# point_level_icon (애드온)

## 개요

- **목적**: 회원 닉네임 옆에 포인트 레벨에 따른 아이콘 자동 표시.

## hook 위치

`before_display_content` — HTML 본문 문자열을 정규식으로 가공. 페이지 콘텐츠 수정 화면(`act=dispPageAdminContentModify`) / 비-HTML 응답 / 크롤러는 제외.

## 동작

본문/댓글의 `member_<srl>` 클래스(`<div>`/`<span>`/`<a>`)를 찾아 회원 포인트로 산출한 레벨 아이콘을 삽입. 단, `icon_duplication` 설정이 '사용함'(기본)이면 해당 회원에게 그룹 아이콘(`MemberModel::getGroupImageMark`)이 있을 경우 레벨 아이콘을 삽입하지 않으며, 포인트 정보가 없는 회원(`getPoint`의 `$exists`가 false)도 제외한다.

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

- `icon_duplication` — 아이콘 중복 방지 (`conf/info.xml`의 유일한 extra_var). 값 `''`(사용함, 기본)이면 회원에게 그룹 아이콘이 있을 때 레벨 아이콘을 달지 않고, 값 `'N'`(사용하지 않음)이면 그룹 아이콘 유무와 무관하게 레벨 아이콘을 표시한다.

레벨 아이콘 이미지(`level_icon`)와 확장자(`level_icon_type`)는 이 애드온이 아니라 point 모듈 설정값이며(`point_level_icon.lib.php:57-58`), `modules/point/icons/<level_icon>/<level>.<type>` 경로로 참조된다.

## 관련

- point: [../28-modules/point.md](../28-modules/point.md)
