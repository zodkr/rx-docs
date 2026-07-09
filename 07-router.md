# 07. Router

`common/framework/Router.php` (645줄). `Rhymix\Framework\Router` 클래스는 URL을 `module/mid/act/document_srl/...` 변수로 분해(`parseURL`)하거나, 역으로 변수에서 URL을 합성(`getURL`)한다.

## rewrite_level

`config('url.rewrite')` 값으로 결정 (`Router.php:102-110`).

| 값 | 의미 |
|---|---|
| `0` | 리라이트 없음. `?mid=xxx&act=yyy` 형식만 |
| `1` | XE 호환 라우트만 (예: `/board/123`) |
| `2` | 전체 리라이트 (모듈별 라우트 포함) |

기본은 `Config::get('use_rewrite')`가 truthy면 1, 아니면 0.

## 글로벌 라우트

`$_global_routes` (`Router.php:13-67`)는 모듈과 무관하게 항상 매칭 시도되는 패턴들이다.

| 라우트 패턴 | regexp | extra_vars | priority |
|---|---|---|---|
| `$document_srl` | `^(?<document_srl>[0-9]+)$` | — | 0 |
| `$act` | `^(?<act>rss\|atom)$` | — | 0 |
| `$mid` | `^(?<mid>[a-zA-Z0-9_-]+)/?$` | — | 0 |
| `$mid/$document_srl` | `^(?<mid>...)/(?<document_srl>[0-9]+)$` | — | 30 |
| `$mid/category/$category` | `^(?<mid>...)/category/(?<category>[0-9]+)$` | — | 10 |
| `$mid/entry/$entry` | `^(?<mid>...)/entry/(?<entry>[^/]+)$` | — | 0 |
| `$mid/$act` | `^(?<mid>...)/(?<act>rss\|atom\|api)$` | — | 20 |
| `files/download/link/$file_srl/$sid/$filename` | … | `act=procFileDownload` | 0 |
| `files/download/$file_srl/$file_key/$filename` | … | `act=procFileOutput` | 0 |
| `common/rewrite/test/$test` | … | `act=dispAdminRewriteTest` | 0 |

이 라우트들은 정의된 순서대로 매칭을 시도하며, priority는 매칭 순서가 아니라 URL 생성 시(`getURL`, `_getBestMatchingRoute`) 가장 잘 맞는 라우트를 고르는 데 쓰인다 (아래 '모듈별 라우트' 참고).

## 변수 타입

라우트 변수에 지정 가능한 타입 (`vars` 배열):

| 타입 | 매칭 |
|---|---|
| `int` | 정수만 |
| `float` | 실수 |
| `alpha` | 알파벳 |
| `alnum` | 알파벳/숫자 |
| `hex` | 16진수 |
| `word` | `\w+` |
| `any` | 슬래시 없는 임의 문자열 |
| `delete` | 매칭 후 URL 생성 시 제거 (검색용 임시 변수) |

## prefix 우회

```php
protected static $_except_prefixes = ['rss' => true, 'atom' => true];
protected static $_except_modules = ['socialxe' => true];
```

`/rss`, `/atom`은 mid가 아니라 액션으로 해석된다. `socialxe` 모듈은 prefix 단축을 적용하지 않는다.

## 모듈별 라우트

`conf/module.xml`에서 액션마다 라우트를 정의할 수 있다.

```xml
<action name="dispBoardContent" type="view" index="true">
    <route route="$document_srl:int" priority="100" />
    <route route="category/$category:int" priority="40" />
    <route route="page/$page:int" priority="10" />
</action>
```

라우트는 mid(prefix) 다음의 내부 URL에 대해 상대적으로 매칭되므로 route 정의에 `$mid`를 쓰지 않는다 (`Router.php:183-196`).

route 값의 `$변수명:타입`에서 `:타입`은 해당 세그먼트에 대한 정규식 제약이며, `ModuleActionParser::analyzeRoute()`가 명명 캡처그룹으로 컴파일한다 (`$page:int` → `(?P<page>[0-9]+)`). 지원 타입은 `int`(`[0-9]+`), `float`(`[0-9]+(?:\.[0-9]+)?`), `alpha`(`[a-zA-Z]+`), `alnum`(`[a-zA-Z0-9]+`), `hex`(`[0-9a-f]+`), `word`(`[a-zA-Z0-9_]+`), `any`(`[^/]+`)이다 (`common/framework/parsers/ModuleActionParser.php:13-22`). 타입을 생략하면 변수명이 `_srl`로 끝날 때 `int`, 그 외에는 `any`로 처리된다 (`:339`). 특수 타입 `:delete`는 매칭 시 `[^/]+`이지만 URL 생성(`getURL`) 시에는 변수를 소비만 하고 URL에 출력하지 않는다 (`Router.php:631`).

파싱은 `common/framework/parsers/ModuleActionParser.php`가 담당한다. `priority`는 URL 매칭 순서가 아니라 URL 생성 시(`getURL`, `_getBestMatchingRoute`)에 가장 잘 맞는 라우트를 고르는 데 사용된다 (`Router.php:603`). `parseURL`은 라우트를 XML 정의 순서대로 매칭한다 (`Router.php:183`).

## parseURL() 흐름 (`:120`)

1. URL에서 `?` 이후를 파싱해 `$_GET` 변수로 분리.
2. URL을 urldecode + UTF-8 검증.
3. **rewrite_level ≥ 2일 때**: 첫 segment를 prefix로 보고:
   - `_getActionInfoByPrefix($prefix)` — 등록된 prefix.
   - `_getActionInfoByModule($prefix)` — 모듈 이름 자체.
   - 매칭되면 해당 모듈의 라우트 순회 → 매칭되는 액션 실행.
   - 매칭 안 되면 인덱스 액션(`default_index_act`)으로.
4. **그렇지 않으면**: forwarded 라우트와 글로벌 라우트 매칭 시도.
5. 최종 결과는 `Rhymix\Framework\Request` 객체에 채워져 반환.

`Request` 객체는 `module`, `mid`, `act`, 그 외 임의 변수, `getRouteStatus()`(200/404 등), `args` 배열을 제공한다.

## getURL() 흐름

`Router::getURL(array $args, int $rewrite_level): string` (`:308`).

1. `rewrite_level == 0`이면 즉시 `index.php?...` 쿼리스트링 반환.
2. 모듈/mid가 분명하면 해당 모듈 라우트(우선순위 순)에서 변수 매칭.
3. 안 맞으면 글로벌 라우트 시도.
4. 안 맞으면 query string으로 폴백 (`index.php?mid=...&act=...`).

호출자: `Context::getUrl()`, `getUrl()`, `getNotEncodedUrl()` 등 (`common/legacy.php`, `classes/context/Context.class.php`). 실제로 `Router::getURL`을 호출하는 것은 `Context::getUrl()` (`classes/context/Context.class.php:1726`, 호출 지점 `:1862`)이며, `getUrl()`/`getNotEncodedUrl()`은 `common/legacy.php:279,302`에서 이를 감싼다.

## forwarded 라우트

`ModuleModel::getActionForward()`로 등록된 액션은 다른 모듈로 위임(action-forward)될 수 있다. 이 라우트들은 `_internal_forwarded_cache`(모듈 내부)/`_global_forwarded_cache`(글로벌)에 모듈 정보와 함께 매핑되어 `parseURL`에서 매칭 시 `is_forwarded=true`로 설정된다 (`Router.php:543`).

주의: 정적 `$_global_routes`에 정의된 `files/download/...`(→ file 모듈 `procFileOutput`/`procFileDownload`), `common/rewrite/test/...`(→ admin 모듈 `dispAdminRewriteTest`) 등은 forwarded 라우트가 **아니다**. 이들은 `extra_vars`의 `act`만 채우는 'XE 호환 글로벌 라우트' 루프에서 매칭되며 `is_forwarded=false`이고, `$result->module`은 빈 문자열로 남는다 (`Router.php:49-66,268-282`).

## 캐싱

다음 5종 캐시가 Router 동작을 빠르게 한다.

- `_action_cache_prefix[$prefix]` — prefix → 모듈 이름 (문자열 또는 `false`). action_info는 이 모듈 이름으로 `_getActionInfoByModule()`을 다시 호출해 얻는다 (`Router.php:451-468`).
- `_action_cache_module[$module]` — module name → action_info.
- `_global_forwarded_cache` — 글로벌 forwarded 라우트.
- `_internal_forwarded_cache` — 모듈별 forwarded.
- `_route_cache` — 라우트 컴파일 결과.

모듈 설치/업데이트 시 캐시가 무효화된다 (`ModuleModel::getModuleActionXml`가 캐시 키 관리).

## 사용 예

### URL 분해

```php
$result = Router::parseURL('GET', 'board/123?page=2', 2);
// $result->module = 'board'
// $result->mid    = 'board'
// $result->act    = 'dispBoardContent'
// $result->args['document_srl'] = 123  (또는 $result->get('document_srl') == 123)
// $result->args   = ['page' => 2, 'document_srl' => 123, 'mid' => 'board', 'act' => 'dispBoardContent']
```

### URL 생성

```php
$url = getUrl('', 'mid', 'free', 'document_srl', 42);
// '/free/42' (rewrite_level=2)
// 또는 '/?mid=free&document_srl=42' (rewrite_level=0)
```

## 다음 문서

- 응답 출력: [08-display-and-response.md](08-display-and-response.md)
- 다중 사이트: [22-multi-site-and-domain.md](22-multi-site-and-domain.md)
- 모듈 라우트 등록: [27-extension-points/module.md](27-extension-points/module.md)
