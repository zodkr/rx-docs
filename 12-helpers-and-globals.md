# 12. 전역 함수, 상수, `$GLOBALS`

`common/functions.php`, `common/legacy.php`, `common/constants.php`가 정의하는 전역 심볼 모음.

## RX_* 상수

`common/constants.php`. 부트스트랩 시 정의된다.

| 상수 | 의미 | 정의 위치 |
|---|---|---|
| `RX_VERSION` | 현재 Rhymix 버전 (예: `'2.1.35'`) | `:6` |
| `RX_MICROTIME` | 스크립트 시작 microtime (float) | `:11` |
| `RX_TIME` | 시작 unix time (int) | `:16` |
| `RX_BASEDIR` | 서버측 절대 경로 (trailing `/`) | `:21` |
| `RX_BASEURL` | 클라이언트측 경로 (도메인 미포함, trailing `/`) | `:26-42` |
| `RX_REQUEST_URL` | `RX_BASEURL` 이후 URL 부분 | `:47-54` |
| `RX_CLIENT_IP_VERSION` | 4 또는 6 | `:59-83` |
| `RX_CLIENT_IP` | 방문자 IP (CloudFlare 실제 IP 추출 후) | 동상 |
| `RX_SSL` | 현재 요청 HTTPS 여부 | `:88-111` |
| `RX_POST` | 현재 요청이 POST인가 | `:116-123` |
| `RX_WINDOWS` | OS가 Windows인가 | `:128` |

### XE 호환 상수

| 상수 | 값 |
|---|---|
| `__XE__` | `true` |
| `__ZBXE__` | `true` |
| `__XE_VERSION__` | `RX_VERSION` |
| `__XE_VERSION_ALPHA__` | `false` |
| `__XE_VERSION_BETA__` | `false` |
| `__XE_VERSION_RC__` | `false` |
| `__XE_VERSION_STABLE__` | `true` |
| `__XE_MIN_PHP_VERSION__` | `'7.4.0'` |
| `__XE_RECOMMEND_PHP_VERSION__` | `'7.4.0'` |
| `__ZBXE_VERSION__` | `RX_VERSION` |
| `_XE_LOCATION_` | `'ko'` |
| `_XE_PACKAGE_` | `'XE'` |
| `_XE_PATH_` | `RX_BASEDIR` |

### 콘텐츠 상태 `RX_STATUS_*`

문서/댓글/파일의 라이프사이클 상태.

| 상수 | 값 | 의미 |
|---|---|---|
| `RX_STATUS_TEMP` | 0 | 임시 저장 |
| `RX_STATUS_PUBLIC` | 1 | 공개 |
| `RX_STATUS_SECRET` | 2 | 비밀글 |
| `RX_STATUS_EMBARGO` | 3 | 예약 발행 |
| `RX_STATUS_TRASH` | 4 | 휴지통 |
| `RX_STATUS_CENSORED` | 5 | 신고 처리 |
| `RX_STATUS_CENSORED_BY_ADMIN` | 6 | 관리자 검열 |
| `RX_STATUS_DELETED` | 7 | 삭제 (사용자) |
| `RX_STATUS_DELETED_BY_ADMIN` | 8 | 삭제 (관리자) |
| `RX_STATUS_OTHER` | 9 | 기타 |
| `RX_STATUS_PRIVATE` | 10 | 비공개 |

### 문자열 상수

| 상수 | 값 |
|---|---|
| `DIGITS` | `'0123456789'` |
| `XDIGITS` | `'0123456789abcdef'` |
| `ALPHABETS` | `'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'` |
| `UPPER` | `'A...Z'` |
| `LOWER` | `'a...z'` |
| `CR` | `"\r"` |
| `CRLF` | `"\r\n"` |
| `LF` | `"\n"` |
| `Y` | `'Y'` |
| `N` | `'N'` |

### SSL 강제 옵션

| 상수 | 값 | 의미 |
|---|---|---|
| `FOLLOW_REQUEST_SSL` | 0 | 요청 그대로 |
| `ENFORCE_SSL` | 1 | 항상 HTTPS |
| `RELEASE_SSL` | 2 | 항상 HTTP |

## `common/functions.php`

### 설정/언어

| 함수 | 시그니처 | 비고 |
|---|---|---|
| `config(string $key, $value = null)` | `$value` null이면 get, 아니면 set | `Rhymix\Framework\Config` |
| `lang(?string $code, $value = null)` | 다국어 get/set | `Rhymix\Framework\Lang` |

### 배열

| 함수 | 비고 |
|---|---|
| `array_first(array)` | `reset()` wrapper |
| `array_first_key(array)` | `array_key_first()` |
| `array_last(array)` | `end()` wrapper |
| `array_last_key(array)` | `array_key_last()` |
| `array_escape(array, $double_escape=true)` | 재귀 htmlspecialchars |
| `array_flatten(array)` | 다차원 → 평면 |
| `class_basename($class)` | 마지막 namespace segment |

### 경로/URL

| 함수 | 비고 |
|---|---|
| `clean_path($path)` | `..` 정규화 |
| `path2url($path)` | `RX_BASEDIR` 기준 → URL |
| `url2path($url)` | URL → `RX_BASEDIR` 기준 |

### 이스케이프/문자열

| 함수 | 비고 |
|---|---|
| `escape($str, $double_escape=true)` | htmlspecialchars |
| `escape_css($str)` | CSS 컨텍스트 |
| `escape_js($str)` | JS 컨텍스트 |
| `escape_sqstr($str)` | `'작은따옴표'` PHP 문자열 리터럴 |
| `escape_dqstr($str)` | `"큰따옴표"` PHP 문자열 리터럴 |
| `explode_with_escape($delim, $str, $limit=0, $escape_char='\\')` | 이스케이프 인식 split |
| `starts_with($needle, $haystack)` | bool |
| `ends_with($needle, $haystack)` | bool |
| `contains($needle, $haystack, $case_sensitive=true)` | bool |
| `is_between($value, $min, $max)` | bool |
| `force_range($value, $min, $max)` | 범위 강제 |

### 인코딩

| 함수 | 비고 |
|---|---|
| `base64_encode_urlsafe($data)` | URL-safe base64 |
| `base64_decode_urlsafe($data)` | 역변환 |
| `hex2rgb($hex)` | `[r, g, b]` |
| `rgb2hex(array $rgb, $hash_prefix=true)` | `[r, g, b]` 배열 → `'#rrggbb'` |
| `number_shorten($n)` | `1234` → `'1.2K'` |

### 타입 변환

| 함수 | 비고 |
|---|---|
| `tobool($val)` | `'Y'`/`'N'`/`'true'`/`'false'`/`1`/`0` → bool |
| `countobj($var)` | array/Countable이면 count, 객체이면 프로퍼티 개수, 그 외 truthy면 1·falsy면 0 (`@deprecated`) |

### UTF-8

| 함수 | 비고 |
|---|---|
| `utf8_check($str)` | bool |
| `utf8_clean($str)` | 잘못된 바이트 제거 |
| `utf8_mbencode($str)` | mb safe |
| `utf8_normalize_spaces($str)` | NBSP 등 정규화 |
| `utf8_trim($str)` | UTF-8 인식 trim |

### HTML 콘텐츠

| 함수 | 비고 |
|---|---|
| `is_html_content($str)` | `<태그>` 포함 여부 |
| `is_empty_html_content($str)` | 시각적으로 비었는지 |

### include 헬퍼

| 함수 | 비고 |
|---|---|
| `include_in_clean_scope($file)` | 격리된 스코프로 include |
| `include_and_ignore_errors($file)` | 에러 무시 include |
| `include_and_ignore_output($file)` | 출력 ob로 흡수 |

## `common/legacy.php`

### `RX_AUTOLOAD_FILE_MAP`

autoloader 분기 2가 사용하는 정적 매핑 (lc 클래스명 → 파일 경로). 43개 항목.

### 모듈 인스턴스 헬퍼

| 함수 | 등가 |
|---|---|
| `getModule($name, $type='view', $kind='')` | `ModuleHandler::getModuleInstance(...)` |
| `getController($name)` | `getModuleInstance($name, 'controller')` |
| `getAdminController($name)` | `getModuleInstance($name, 'controller', 'admin')` |
| `getView($name)` | `getModuleInstance($name, 'view')` |
| `getAdminView($name)` | `getModuleInstance($name, 'view', 'admin')` |
| `getModel($name)` | `getModuleInstance($name, 'model')` |
| `getAdminModel($name)` | `getModuleInstance($name, 'model', 'admin')` |
| `getAPI($name)` | `getModuleInstance($name, 'api')` |
| `getMobile($name)` | `getModuleInstance($name, 'mobile')` |
| `getWAP($name)` | `getModuleInstance($name, 'wap')` (deprecated) |
| `getClass($name)` | `getModuleInstance($name, 'class')` |

모두 `$GLOBALS['_module_instances_']` 캐시를 사용한다.

### DB 헬퍼

| 함수 | 비고 |
|---|---|
| `executeQuery($query_id, $args=null, $columnList=null)` | `module.queryName` 형식 |
| `executeQueryArray($query_id, $args=null, $columnList=null)` | 결과를 array로 |
| `getNextSequence()` | 다음 시퀀스 |
| `setUserSequence($seq)` | 세션(`$_SESSION['seq']`)에 시퀀스 저장 |
| `checkUserSequence($seq)` | 시퀀스 소유자 검증 |

### URL 헬퍼

| 함수 | 비고 |
|---|---|
| `getUrl(...)` | `Context::getUrl` |
| `getNotEncodedUrl(...)` | URL 인코딩 안 함 |
| `getAutoEncodedUrl(...)` | 인코딩 자동 |
| `getFullUrl(...)` | 도메인 포함 |
| `getNotEncodedFullUrl(...)` | 두 옵션 결합 |
| `getSiteUrl($site_info, ...)` | 특정 사이트 |
| `getNotEncodedSiteUrl($site_info, ...)` | 동상 |
| `getFullSiteUrl($site_info, ...)` | 도메인 포함 |
| `getCurrentPageUrl()` | 현재 페이지 URL |
| `isSiteID($id)` | 사이트 ID 형식 검증 |

### 문자열/시간

| 함수 | 비고 |
|---|---|
| `cut_str($str, $cut_size=0, $tail='...')` | 멀티바이트 안전 자르기 |
| `get_time_zone_offset($timezone)` | 초 단위 오프셋 |
| `zgap($timestamp=null)` | 사용자 ↔ 내부 timezone 오프셋 (초) |
| `ztime($str)` | YYYYMMDDHHMMSS → unix time (내부 timezone 가정) |
| `zdate($str, $format='Y-m-d H:i:s', $conversion=false)` | YYYYMMDDHHMMSS → 사용자 timezone 포맷팅 |
| `getInternalDateTime($timestamp=null, $format='YmdHis')` | 내부 timezone 포맷팅 |
| `getDisplayDateTime($timestamp=null, $format='YmdHis')` | 사용자 timezone 포맷팅 |
| `getTimeGap($date, $format='Y.m.d')` | "방금"/"3분 전"/포맷 |
| `getMonthName($month, $short=true)` | `'Jan'` 또는 `'January'` |

### 기타 legacy 헬퍼

| 함수 | 비고 |
|---|---|
| `getEncodeEmailAddress($email)` | `&#NN;` 엔티티 인코딩 |
| `debugPrint(...)` | Debug에 추가 (개발용) |
| `delObjectVars($target, $del)` | object에서 다른 object의 키 제거 |
| `getDestroyXeVars($vars)` | XE 시스템 변수 제거 (error_return_url, success_return_url, ruleset, xe_validator_id, _rx_csrf_token 등) |
| `getNumberingPath($no, $size=3)` | `12345` → `'345/012/'` (해시 디렉토리) |
| `removeHackTag($content)` | XE 호환 XSS 정화 (`Filters\HTMLFilter` 위임) |
| `detectUTF8($str, $return_convert=false, $urldecode=true)` | UTF-8 감지/변환 |
| `isCrawler($ua=null)` | 봇 UA 패턴 매칭 |
| `stripEmbedTagForAdmin(&$content, $writer_member_srl)` | 비관리자 작성 embed 차단 |
| `checkCSRF()` | `Security::checkCSRF()` wrapper |

## `$GLOBALS` 사용 패턴

| 키 | 용도 |
|---|---|
| `$GLOBALS['lang']` | `lang()` 헬퍼의 캐시된 `Rhymix\Framework\Lang` 인스턴스 |
| `$GLOBALS['RX_AUTOLOAD_FILE_MAP']` | autoloader 분기 2의 매핑 테이블 |
| `$GLOBALS['RX_NAMESPACES']` | autoloader 분기 4의 외부 namespace 매핑 |
| `$GLOBALS['_module_instances_']` | `getController` 등 모듈 인스턴스 캐시 |

`Rhymix\Framework` 도입 후로도 일부 wrapper가 이들 글로벌을 활용한다.

## 템플릿 / PHP에서 헬퍼 사용

### 템플릿 v1

```html
<a href="{getUrl('', 'mid', 'free')}">자유게시판</a>
<p>{$lang->cmd_login}</p>
<p>{lang('member.cmd_login')}</p>
<p>{config('site.title')}</p>
```

### 템플릿 v2

```blade
<a href="{{ getUrl('', 'mid', 'free') }}">자유게시판</a>
<p>{{ $lang->cmd_login }}</p>
<p>{{ lang('member.cmd_login') }}</p>
```

### PHP

```php
$theme = config('view.theme');
$prompt = lang('member.cmd_login');
$url = getUrl('', 'mid', 'free', 'document_srl', $srl);
```

## 다음 문서

- autoloader 분기: [26-namespaces-and-autoload.md](26-namespaces-and-autoload.md)
- 설정 시스템: [25-config-system.md](25-config-system.md)
- 다국어: [16-i18n-and-lang.md](16-i18n-and-lang.md)
