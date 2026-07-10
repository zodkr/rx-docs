# language_select (위젯)

## 개요

- **목적**: 사이트 다국어 선택 폼.

## proc() 인자 (`$args`)

`widgets/language_select/conf/info.xml`에 **사용자 정의 extra_vars가 없다**. 기본 스킨/컬러셋 외에 별도 인자가 노출되지 않는다.

| 인자 | 의미 |
|---|---|
| `$args->skin` | 호출자가 선택하는 스킨. `proc()`에는 fallback이 없음 |
| `$args->colorset` | 컬러셋. 누락 시 공통 실행기가 빈 문자열로 초기화 |

표시 형태(드롭다운/플래그/링크 등)는 모두 **스킨이 결정**한다.

## proc() 동작

`language_select.class.php`의 `proc()`은 `Context::set('colorset', ...)`만 호출하고 스킨 템플릿(`language_select.html`)을 컴파일해 반환한다. 사용 가능한 언어 목록 자체는 `Context::getLangType()` / `$lang_supported` 등 사이트 코어 변수를 스킨이 직접 조회한다.

## 동작

언어 선택 시 스킨의 `doChangeLangType()`(`common/js/common.js:1668-1686`, `@deprecated`)이 코어의 `setLangType()`을 호출해 `lang_type` 쿠키를 갱신한 뒤(`common/js/common.js:108-114`) URL의 `?l=` 파라미터를 제거하거나 페이지를 새로 고친다. 서버 측에서는 `l` 쿼리 파라미터(`?l=en` 등)로도 언어를 지정할 수 있으며, 이 경우 코어가 `lang_type` 쿠키를 함께 갱신한다(`classes/context/Context.class.php:269`, `295-298`). Rhymix에는 언어를 URL 경로 prefix로 표현하는 기능이 없으며, `config('url.lang_in_url')` 같은 설정 키도 존재하지 않는다.

## 스킨

`widgets/language_select/skins/default/language_select.html`.

## 관련

- 다국어: [../16-i18n-and-lang.md](../16-i18n-and-lang.md)
