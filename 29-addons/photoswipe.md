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

- `target_selector` — 어느 영역의 이미지만 대상 (예: `.xe_content`).
- `min_width` / `min_height` — 최소 크기 (작은 이미지는 제외).
- `show_caption` — 캡션 표시 여부.
- `pinch_to_close` — 모바일 제스처.

## 외부 라이브러리

[PhotoSwipe](https://photoswipe.com/) — MIT 라이선스. `addons/photoswipe/` 디렉토리에 동봉.

## 관련

- file 모듈: [../28-modules/file.md](../28-modules/file.md)
