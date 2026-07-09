# extravar (확장 변수)

## 개요

- **카테고리**: service
- **역할**: 회원/문서 등 모듈의 **사용자 정의 입력 항목** 관리. 회원 가입 시 추가 필드, 게시판별 추가 컬럼 등을 동적으로 정의.

## 주요 클래스

extravar는 **완전한 v2 namespace 모듈**이다 (`modules/extravar/`에 `<name>.class.php`/`<name>.controller.php` 등 레거시 파일이 전혀 없다).

| 레거시 alias | 정의 위치 | 신형 namespace |
|---|---|---|
| `ExtraVar` | `classes/extravar/Extravar.class.php`의 `class_alias` | `Rhymix\Modules\Extravar\Models\ValueCollection` |
| `ExtraItem` | (동상) | `Rhymix\Modules\Extravar\Models\Value` |

`modules/extravar/` 트리:

- `controllers/Base.php`, `controllers/Install.php`, `controllers/Config.php`
- `models/ValueCollection.php`, `models/Value.php`
- `views/header.blade.php`, `views/config.blade.php`
- `skins/default/form.blade.php` + `skins/default/form_types/*.blade.php`

## 주요 액션 (2개)

| 액션 | 비고 |
|---|---|
| `dispExtravarAdminConfig` | 확장 변수 관리자 설정 (admin_index, menu=extravar, `class="Controllers\Config"`) |
| `procExtravarAdminInsertConfig` | 설정 저장 (standalone="true", `class="Controllers\Config"`) |

(이 모듈은 namespace 컨트롤러 `Rhymix\Modules\Extravar\Controllers\Config`를 사용한다. 회원/문서의 확장 변수 정의 UI는 각 도메인 모듈에서 직접 처리.)

## 사용 패턴

### 정의

회원 모듈/게시판 관리자 UI에서 확장 필드를 추가:

- 타입 (관리자 선택 목록 `$lang->column_type_list`, `common/lang/ko.php:321`): `text`/`textarea`/`password`/`select`/`radio`/`checkbox`/`tel`/`tel_v2`/`tel_intl`/`tel_intl_v2`/`homepage`(URL)/`email_address`/`kr_zip`(한국 주소·우편번호)/`country`/`language`/`date`/`time`/`timezone`/`number`/`file`.
- 필수/선택.
- 기본값/허용값.

### 저장

`DocumentItem::getExtraEidValue`(필드명=eid) / `getExtraValue`(숫자 var_idx) / `getExtraVars`로 접근.

```php
$value = $oDoc->getExtraEidValue('my_custom_field'); // eid(필드명)로 조회
$value = $oDoc->getExtraValue($idx);                 // 숫자 var_idx로 조회
$all = $oDoc->getExtraVars();                         // var_idx로 키가 매겨진 Value 객체 배열
foreach ($all as $value_obj) {
    echo $value_obj->name . ': ' . $value_obj->value;
}
```

`getExtraValue($idx)`(`modules/document/document.item.php:943`)는 숫자 var_idx로 조회하므로 필드명 문자열을 넘기면 빈 문자열이 반환된다. 필드명(eid)으로 조회하려면 `getExtraEidValue($eid)`(`document.item.php:955`)를 쓴다.

회원은 최상위 프로퍼티로 접근한다. `getMemberInfo()`가 부르는 `arrangeMemberInfo()`(`modules/member/member.model.php:506`)는 `extra_vars`를 unserialize한 뒤 `unset($info->extra_vars)`로 제거하고 각 항목을 `$info->{$key}`로 최상위에 승격한다. 따라서 `$member->extra_vars`는 존재하지 않는다.

```php
$member = MemberModel::getMemberInfo($member_srl);
$value = $member->my_field;
```

## DB 스키마 사용

| 테이블 | 용도 |
|---|---|
| `document_extra_keys` | 게시판별 확장 변수 정의 |
| `document_extra_vars` | 게시판 확장 변수 값 |
| `member_join_form` | 회원 가입 확장 필드(항목) 정의 (`modules/member/schemas/member_join_form.xml`) |
| `member` 테이블의 `extra_vars` 컬럼 | 회원 확장 변수 값 (serialized text, `modules/member/schemas/member.xml:30`) |

> `member_extra_info`는 DB 테이블이 아니라 `files/` 하위 파일 저장 디렉토리(프로필 이미지·서명 등)다.

## 관련

- document: [document.md](document.md)
- member: [member.md](member.md)
- namespace 모듈 패턴: [../26-namespaces-and-autoload.md](../26-namespaces-and-autoload.md)
