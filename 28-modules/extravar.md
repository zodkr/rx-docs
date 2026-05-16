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

- 타입: `text`/`select`/`radio`/`checkbox`/`textarea`/`tel`/`date`/`address`/`country`/`email_address`/`homepage`/`kr_zip`/`color`/`url`/`image`/`file`.
- 필수/선택.
- 기본값/허용값.

### 저장

`DocumentItem::getExtraValue` / `getExtraVars`로 접근.

```php
$value = $oDoc->getExtraValue('my_custom_field');
$all = $oDoc->getExtraVars();
foreach ($all->getAll() as $value_obj) {
    echo $value_obj->name . ': ' . $value_obj->value;
}
```

회원도 동일:

```php
$member = MemberModel::getMemberInfo($member_srl);
$value = $member->extra_vars->my_field;
```

## DB 스키마 사용

| 테이블 | 용도 |
|---|---|
| `document_extra_keys` | 게시판별 확장 변수 정의 |
| `document_extra_vars` | 게시판 확장 변수 값 |
| `member_extra_info` | 회원 확장 정보 |

## 관련

- document: [document.md](document.md)
- member: [member.md](member.md)
- namespace 모듈 패턴: [../26-namespaces-and-autoload.md](../26-namespaces-and-autoload.md)
