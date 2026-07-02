# krzip (한국 우편번호)

## 개요

- **카테고리**: (info.xml에 미지정 — 기본 `service`)
- **역할**: 공개 API를 이용한 한국 우편번호 검색.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Krzip` | `krzip.class.php` |
| `KrzipController` | `krzip.controller.php` |
| `KrzipModel` | `krzip.model.php` |
| `KrzipView` | `krzip.view.php` |
| `KrzipAdminController` | `krzip.admin.controller.php` |
| `KrzipAdminView` | `krzip.admin.view.php` |

(`krzip.mobile.php`, `krzip.admin.model.php`, `krzip.api.php`는 없다.)

## 주요 액션 (4개)

| 액션 | 비고 |
|---|---|
| `dispKrzipSearchForm` | 우편번호 검색 폼 |
| `getKrzipCodeList` | 우편번호 검색 모델 호출 |
| `dispKrzipAdminConfig` | 관리자 설정 (admin_index) |
| `procKrzipAdminInsertConfig` | 설정 저장 (ruleset=krzipConfig) |

## JS 위젯

`kr_zip` extravar 타입 필드는 `KrzipModel::getKrzipCodeSearchHtml()`(`krzip.model.php:238`)이 렌더링한다 (호출부: `modules/extravar/skins/default/form_types/kr_zip.blade.php:5`). 설정된 API(`daumapi`/`epostapi`/`postcodify`)에 맞는 `tpl/template.{api}.html`을 컴파일하고, 해당 템플릿이 `modules/krzip/tpl/js/{api}.js`의 `$.fn.Krzip` jQuery 플러그인을 로드한다.

`common/js/plugins/ui.krzip/krzip_search.js`는 순수 jQuery(jQuery UI 아님)로 작성됐으나 현재 어디서도 로드되지 않는 레거시(고아) 코드다.

## API

외부 우편번호 API 3종만 활용 (`krzip.class.php:23` `$api_list = array('daumapi', 'epostapi', 'postcodify')`) — 다음/카카오(`daumapi`), 우체국(`epostapi`), Postcodify(`postcodify`). 자체 DB는 없다 (`schemas/`·`queries/` 디렉터리 부재). 우체국 API는 도로명주소 검색(`target=postRoad`, `krzip.model.php:153`)을 사용한다.

## 관련

- extravar: [extravar.md](extravar.md)
- 외부 라이브러리: [../34-external-libraries.md](../34-external-libraries.md)
