# language_select (위젯)

## 개요

- **목적**: 사이트 다국어 선택 폼.

## proc() 인자 (`$args`)

`widgets/language_select/conf/info.xml`에 **사용자 정의 extra_vars가 없다**. 기본 스킨/컬러셋 외에 별도 인자가 노출되지 않는다.

| 인자 | 의미 |
|---|---|
| `$args->skin` | 스킨 |
| `$args->colorset` | 컬러셋 |

표시 형태(드롭다운/플래그/링크 등)는 모두 **스킨이 결정**한다.

## proc() 동작

`language_select.class.php`의 `proc()`은 `Context::set('colorset', ...)`만 호출하고 스킨 템플릿(`language_select.html`)을 컴파일해 반환한다. 사용 가능한 언어 목록 자체는 `Context::getLangType()` / `$lang_supported` 등 사이트 코어 변수를 스킨이 직접 조회한다.

## 동작

언어 선택 시 코어가 `lang_type` 쿠키를 갱신한다. URL prefix 옵션(`config('url.lang_in_url')`) 활성 시 prefix 변경.

## 스킨

`widgets/language_select/skins/default/language_select.html`.

## 관련

- 다국어: [../16-i18n-and-lang.md](../16-i18n-and-lang.md)
