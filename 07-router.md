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

priority가 높은 라우트가 먼저 매칭된다.

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
<action name="dispBoardContent" type="view">
    <route route="$mid/$category_srl/$document_srl/$page" priority="20" />
    <route route="$mid/$category_srl/$document_srl" priority="20" />
</action>
```

파싱은 `common/framework/parsers/ModuleActionParser.php`가 담당하며, 우선순위 순으로 정렬된다.

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

호출자: `Context::getUrl()`, `getUrl()`, `getNotEncodedUrl()` 등 (`common/legacy.php`, `common/functions.php`).

## forwarded 라우트

글로벌 라우트의 `extra_vars`에 `act`가 지정된 경우, 해당 액션은 모듈의 `<action>` 정의로 다시 위임된다. 예:

- `files/download/...` → file 모듈의 `procFileDownload` 액션.
- `common/rewrite/test/...` → admin 모듈의 `dispAdminRewriteTest`.

내부적으로 `_internal_forwarded_cache`/`_global_forwarded_cache`에 모듈 정보를 매핑해 둔다.

## 캐싱

다음 4종 캐시가 Router 동작을 빠르게 한다.

- `_action_cache_prefix[$prefix]` — prefix → action_info.
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
// $result->document_srl = 123
// $result->args   = ['mid' => 'board', 'document_srl' => 123, 'page' => 2]
```

### URL 생성

```php
$url = getUrl('', 'mid', 'free', 'document_srl', 42);
// '/free/42' (rewrite_level=2)
// 또는 '/?mid=free&document_srl=42' (rewrite_level=0)
```

## 다국어 prefix

`config('url.lang_in_url')` 활성화 시 `/ko/board/123`처럼 언어 코드가 URL prefix로 들어간다. Router가 이를 인식해 `lang_type`을 `ko`로 설정한 뒤 나머지 URL을 다시 파싱한다.

## 다음 문서

- 응답 출력: [08-display-and-response.md](08-display-and-response.md)
- 다중 사이트: [22-multi-site-and-domain.md](22-multi-site-and-domain.md)
- 모듈 라우트 등록: [27-extension-points/module.md](27-extension-points/module.md)
