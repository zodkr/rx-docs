# krzip (한국 우편번호)

## 개요

- **카테고리**: (info.xml에 미지정 — 기본 `service`)
- **역할**: 공개 API(또는 자체 DB)를 이용한 한국 우편번호 검색.

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

`common/js/plugins/ui.krzip/`이 jQuery UI 기반 우편번호 검색 위젯. extravar의 `kr_zip` 타입 필드에서 자동 사용.

## API

외부 우편번호 API (현재는 도로명주소 검색 API) 또는 자체 데이터 활용.

## 관련

- extravar: [extravar.md](extravar.md)
- 외부 라이브러리: [../34-external-libraries.md](../34-external-libraries.md)
