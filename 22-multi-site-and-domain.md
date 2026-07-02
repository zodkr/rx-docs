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
  settings           (JSON — 도메인별 언어/타임존/제목/색상 등)
  ...
```

`domains`에는 `default_language` 컬럼이 없다. 도메인별 언어는 `settings` 텍스트(JSON)의 `language` 키에 저장되며, `$domain_info->default_language`는 모델이 `settings->language`(없으면 `config('locale.default_lang')`)로 계산해 채우는 런타임 파생 프로퍼티다 (`modules/module/module.model.php:88`).

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

관리자 UI: `modules/admin/controllers/systemconfig/Domains.php` (`procAdminInsertDomain`), 화면은 `modules/admin/tpl/config_domains_edit.html`. 등록 항목:

- 도메인명 (예: `another.example.com`), 기본 도메인 지정 여부 (`is_default_domain`).
- 사이트 제목/부제목 (`title`/`subtitle`).
- 인덱스 모듈 (`index_module_srl`), 인덱스 문서 (`index_document_srl`).
- 기본 언어 (`default_lang`), 언어 강제 여부 (`force_lang`).
- 기본 타임존 (`default_timezone`).
- SSL 정책 (`domain_security` — `none`/`optional`/`always`), HTTP/HTTPS 포트 (`http_port`/`https_port`).
- 파비콘/다크 파비콘/모바일 아이콘/기본 이미지 (`favicon`/`dark_favicon`/`mobicon`/`default_image`), 색상 스킴 (`color_scheme`).
- 메타 키워드/설명 (`meta_keywords`/`meta_description`), 헤더/푸터 스크립트 (`html_header`/`html_footer`).

`title`/`subtitle`·언어·타임존·색상·메타·헤더/푸터 등 대부분의 값은 `domains.settings` (JSON) 로 직렬화되어 저장된다 (`procAdminInsertDomain`의 `$settings` 배열 — `modules/admin/controllers/systemconfig/Domains.php:363-374`). 도메인·기본 도메인 여부·인덱스 모듈/문서·포트·SSL 정책은 `domains`의 개별 컬럼이다. 파비콘/다크 파비콘/모바일 아이콘/기본 이미지는 settings JSON이 아니라 `files/attach/xeicon/`에 파일로 저장된다 (`IconModel::saveIcon`). 레이아웃(`default_layout_srl`/`default_mlayout_srl`)은 이 UI에서 설정하지 않는다. DB의 `domains`에 추가되며 즉시 적용된다.

## 미등록 도메인 처리

`config('url.unregistered_domain_action')` 값으로 분기 (`ModuleHandler::init`:131-165):

| 값 | 동작 |
|---|---|
| `redirect_301` (기본) | 기본 도메인으로 301 |
| `redirect_302` | 기본 도메인으로 302 |
| `block` | 404 응답 |
| `display` | 임시 사이트로 처리 계속 (위험 — XSS 노출 가능) |

## mid는 전역 유일

`mid`는 `modules` 테이블 전체에서 **전역적으로 유일**하다 — 스키마상 단일 컬럼 unique 인덱스 `unique_mid` (`modules/module/schemas/modules.xml:8`). 따라서 같은 mid를 여러 도메인에서 재사용할 수 없으며, 각 mid는 정확히 하나의 도메인(`domain_srl`)에 속한다.

- 모듈은 `domain_srl` 없이 **mid만으로** 조회된다 (`ModuleModel::getModuleInfoByMid`, `ModuleModel::isIDExists`) — `modules/module/module.model.php:230`, `:27`.
- 조회는 쿼리 단계에서 도메인으로 필터링하지 않는다. 대신 `ModuleHandler::init`이 조회된 모듈의 `domain_srl`이 현재 도메인과 다르면 **사후 검증**으로 404를 반환한다 (`classes/module/ModuleHandler.class.php:207-215`).

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
$url = getFullSiteUrl($other_site_info->domain, '', 'mid', 'free');
```

`getFullSiteUrl()`의 첫 인자는 **도메인 문자열**이다 — 내부에서 `array_shift` 후 `Context::getUrl(..., $domain)`로 넘겨지고, `getUrl`은 이 값에 `strpos` 등 문자열 연산을 수행한다 (`common/legacy.php:444`, `classes/context/Context.class.php:1748`). 사이트 정보 객체를 그대로 넘기면 PHP 8에서 TypeError가 난다. 사이트 정보는 `ModuleModel::getSiteInfoByDomain($domain)` 또는 `ModuleModel::getDefaultDomainInfo()` 등으로 획득하며 (`modules/module/module.model.php:75`, `:132`), 그 객체의 `->domain` 프로퍼티를 넘겨야 한다.

## domain_srl > -1 검증

모듈이 다른 도메인 소속이면 404 (`ModuleHandler::init`:207-215 — 외곽 가드 `$module_info->domain_srl > -1`이 207행, 내부 불일치 검사가 209-214행):

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

옛 XE는 `sites` 테이블과 `site_srl`을 사용했다. Rhymix는 deprecated 처리하고 항상 0을 채워 호환을 유지한다 (`modules` 스키마 `default=0`, `getDefaultDomainInfo`/`getSiteInfo`/`getSiteInfoByDomain` 모두 `site_srl = 0`을 세팅 — `modules/module/schemas/modules.xml:6`, `modules/module/module.model.php:86`). 신규 코드는 `domain_srl`을 사용.

## 다음 문서

- 라우터: [07-router.md](07-router.md)
- module 모듈: [28-modules/module.md](28-modules/module.md)
- admin 모듈: [28-modules/admin.md](28-modules/admin.md)
