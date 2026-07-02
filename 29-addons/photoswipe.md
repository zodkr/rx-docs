# photoswipe (애드온)

## 개요

- **목적**: 본문 내 이미지 클릭 시 라이트박스 갤러리 (PhotoSwipe) 표시.

## hook 위치

`after_module_proc` — HTML 응답에 PhotoSwipe JS/CSS 로드.

## 동작

PhotoSwipe 라이브러리(CSS 2개 + JS 3개)를 로드하고, `pswp.html` 풋터 마크업을 `Context::addHtmlFooter()`로 주입한다. admin 모듈/봇은 제외.

`addons/photoswipe/photoswipe.addon.php` 발췌:

```php
if ($called_position == 'after_module_proc' && Context::getResponseMethod() == "HTML"
    && Context::get('module') != 'admin' && !isCrawler())
{
    Context::loadFile(['./addons/photoswipe/PhotoSwipe/photoswipe.css', '', '', null], true);
    Context::loadFile(['./addons/photoswipe/PhotoSwipe/default-skin/default-skin.css', '', '', null], true);
    Context::loadFile(['./addons/photoswipe/PhotoSwipe/photoswipe.js', 'body', '', null], true);
    Context::loadFile(['./addons/photoswipe/PhotoSwipe/photoswipe-ui-default.js', 'body', '', null], true);
    Context::loadFile(['./addons/photoswipe/rx_photoswipe.js', 'body', '', null], true);

    $footer = FileHandler::readFile('./addons/photoswipe/PhotoSwipe/pswp.html');
    Context::addHtmlFooter($style_display . $footer);
}
```

## extra_vars

- `display_name` (select) — 라이트박스 하단 캡션(파일이름) 표시 여부. 옵션: `block`(사용, 기본값) / `none`(사용 안함). 애드온 코드에서 `.pswp__caption__center`의 CSS `display` 값으로 주입된다 (`addons/photoswipe/photoswipe.addon.php:25`).

`conf/info.xml`에 정의된 extra_var는 `display_name` 하나뿐이다 (`addons/photoswipe/conf/info.xml:23-38`). 대상 이미지 셀렉터 `.rhymix_content, .xe_content`는 extra_var가 아니라 `addons/photoswipe/rx_photoswipe.js:267`에 하드코딩되어 있다.

## 외부 라이브러리

[PhotoSwipe](https://photoswipe.com/) — MIT 라이선스. `addons/photoswipe/` 디렉토리에 동봉.

## 관련

- file 모듈: [../28-modules/file.md](../28-modules/file.md)
