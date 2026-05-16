# 22. 다중 사이트와 도메인

하나의 Rhymix 인스턴스로 여러 도메인을 분리 운영할 수 있다.

## 개념

- `modules` 테이블에 도메인별 모듈 인스턴스가 존재.
- `domains` 테이블이 도메인 → `domain_srl` 매핑.
- `site_module_info`는 현재 도메인의 루트 모듈 정보.

## 데이터 모델

```
domains
  domain_srl  PK
  domain      'example.com'
  is_default_domain  'Y'/'N'
  index_module_srl   (이 도메인의 시작 모듈)
  default_language   (도메인별 기본 언어)
  ...
```

```
modules
  module_srl    PK
  domain_srl    FK → domains
  module        'board'
  mid           'free'
  ...
```

## site_module_info

`Context::init()`이 다음 우선순위로 결정:

1. 현재 요청 도메인 (`Rhymix\Framework\URL::getCurrentDomain()`)과 일치하는 `domains` 행.
2. 매칭이 없으면 `is_default_domain = 'Y'` 행.
3. 그것도 없으면 단일 사이트로 처리.

결과는 `Context::set('site_module_info', $info)`로 노출.

```php
$info = Context::get('site_module_info');
// $info->domain_srl
// $info->domain
// $info->mid             ← 도메인 인덱스 모듈의 mid
// $info->module_srl       ← 동상 srl
// $info->layout_srl       ← 도메인 기본 PC 레이아웃
// $info->mlayout_srl      ← 도메인 기본 모바일 레이아웃
// $info->default_language
// $info->index_document_srl
```

## 도메인 등록

관리자 UI: `modules/admin/controllers/SystemConfig/Domains.php`. 등록 항목:

- 도메인명 (예: `another.example.com`).
- 인덱스 모듈 (mid).
- 기본 레이아웃 (PC/모바일).
- 기본 언어.
- HTTPS 강제 여부.

DB의 `domains`에 추가되며 즉시 적용된다.

## 미등록 도메인 처리

`config('url.unregistered_domain_action')` 값으로 분기 (`ModuleHandler::init`:131-165):

| 값 | 동작 |
|---|---|
| `redirect_301` (기본) | 기본 도메인으로 301 |
| `redirect_302` | 기본 도메인으로 302 |
| `block` | 404 응답 |
| `display` | 임시 사이트로 처리 계속 (위험 — XSS 노출 가능) |

## 도메인별 mid 충돌

같은 mid를 여러 도메인에서 사용할 수 있다 (예: 각 도메인에 `free` 게시판).

- DB의 `modules.mid`는 `(domain_srl, mid)` 복합 unique.
- 모듈 매핑 시 항상 현재 `domain_srl`로 필터링.

## 모듈 분리도

| 영역 | 도메인 분리 |
|---|---|
| 모듈 인스턴스 (게시판, 페이지) | **분리** — 각 도메인 자체 인스턴스 |
| 메뉴 | 보통 분리 |
| 회원 | 공유 — 단일 회원 DB |
| 문서/댓글/파일 | 모듈 인스턴스 단위로 분리 (즉 도메인 단위) |
| 권한 그룹 (member_group) | 공유 |
| 설정 (`config`) | 공유 |
| 캐시 prefix | 도메인 자동 부착 가능 |

회원 공유는 **단일 회원 DB** 모델 — 이것이 XE/Rhymix의 표준 다중 사이트 모델. 회원 분리가 필요하면 별도 인스턴스 운영.

## URL 빌드

`getUrl(...)`은 현재 도메인에 대해 URL을 만든다. 다른 도메인 URL은:

```php
$url = getFullSiteUrl($other_site_info, '', 'mid', 'free');
```

`$other_site_info`는 `ModuleModel::getSiteInfoByDomain($domain)` 또는 `ModuleModel::getDefaultDomainInfo()` 등으로 획득한다 (`modules/module/module.model.php:75`, `:132`).

## domain_srl > -1 검증

모듈이 다른 도메인 소속이면 404 (`ModuleHandler::init`:218-226):

```php
if ($module_info->domain_srl != $site_module_info->domain_srl) {
    $this->error = 'msg_module_is_not_exists';
    $this->httpStatusCode = 404;
    return true;
}
```

## 도메인별 설정 오버라이드

도메인별로 다른 SSL 정책/언어/스킨이 필요하면 `domains` 테이블의 컬럼에 저장된다. 모듈/레이아웃 설정은 모듈 인스턴스 단위로 다르다.

## 사이트맵 / 메뉴

각 도메인은 자체 메뉴 트리를 가진다. `menu.getModuleListInSitemap` 트리거가 도메인별 모듈 목록을 반환.

## 다른 도메인으로 강제 리다이렉트

```php
$url = getNotEncodedSiteUrl($site_module_info->domain) . 'mid=foo';
header("Location: {$url}", true, 301);
```

## site_srl (deprecated)

옛 XE는 `sites` 테이블과 `site_srl`을 사용했다. Rhymix는 deprecated 처리하고 항상 1을 채워 호환을 유지한다. 신규 코드는 `domain_srl`을 사용.

## 다음 문서

- 라우터: [07-router.md](07-router.md)
- module 모듈: [28-modules/module.md](28-modules/module.md)
- admin 모듈: [28-modules/admin.md](28-modules/admin.md)
