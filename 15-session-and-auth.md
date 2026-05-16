# 15. 세션과 인증

PHP 표준 세션과 `Rhymix\Framework\Session`(`common/framework/Session.php`, 1139줄)이 결합되어 동작한다.

## 기본 모델

- PHP `$_SESSION`을 활용한다 — 세션 저장소(file/redis/db/...)는 PHP ini 또는 `config('session.use_db')`로 결정.
- Rhymix가 자체 토큰/refresh/SSL 분리 쿠키 정책을 덧붙인다.
- 로그인 정보는 `$_SESSION['RHYMIX']['login']` 등에 보관된다.

## Session 정적 API

시그니처 (`common/framework/Session.php`):

| 메서드 | 시그니처 | 의미 |
|---|---|---|
| `start` | `start(bool $force = false): bool` | 세션 시작 (이미 시작되어도 안전) |
| `close` | `close(): void` | 세션 저장 후 종료 |
| `destroy` | `destroy(): void` | 세션 파기 |
| `isStarted` | `isStarted(): bool` | — |
| `create` | `create(): bool` | 빈 세션 생성/초기화 |
| `login` | `login(int $member_srl, bool $refresh = true): bool` | **member_srl(int)을 받음** |
| `logout` | `logout(): void` | — |
| `refresh` | `refresh(bool $refresh_cookie = false): bool` | 세션 ID 회전 |
| `isMember` / `isAdmin` / `isTrusted` | `(): bool` | 로그인/관리자/비밀번호 재확인 통과 여부 |
| `isValid` | `isValid(int $member_srl = 0): bool` | 토큰/멤버 검증 |
| `getMemberSrl` | `getMemberSrl(): int` | — |

사용:

```php
// 사용 예
if (!Rhymix\Framework\Session::isMember()) {
    Rhymix\Framework\Session::login($member_srl);
}
```

> `Session::login()`은 **member_srl(int)을 받는다**. 회원 정보 객체에서 로그인하려면 `member.controller.php`의 `MemberController::doLogin($user_id, $password, $keep_signed)`(`:2548`) 같은 상위 API를 사용한다.

## 현재 회원 정보 — `SessionHelper`

```php
$member = Rhymix\Framework\Session::getMemberInfo();
// 또는 컨텍스트에서:
$member = Context::get('logged_info');
```

반환 타입: `Rhymix\Framework\Helpers\SessionHelper` 또는 `false` (비로그인).

### 자주 쓰는 속성/메서드

| 속성/메서드 | 의미 |
|---|---|
| `$member->member_srl` | 회원 srl |
| `$member->user_id` | 로그인 ID |
| `$member->nick_name` | 닉네임 |
| `$member->email_address` | 이메일 |
| `$member->is_admin` (`'Y'`/`'N'`) | 슈퍼관리자 여부 |
| `$member->isMember()` | 로그인 여부 |
| `$member->isAdmin()` | 관리자 여부 |
| `$member->isTrusted()` | 신뢰 세션 여부 |
| `$member->can($scope)` | 특정 권한 보유 여부 |

`$member`가 `false`면 비로그인 — 항상 truthy 체크부터.

## 토큰 / CSRF

### 일반 토큰

`Context::init` 시점에 세션별 토큰이 자동 생성·검증된다.

```php
$token = Rhymix\Framework\Session::getGenericToken();
$ok = Rhymix\Framework\Session::verifyToken($token);
```

POST 등 비-안전 메서드는 `_rx_csrf_token` 파라미터/헤더 또는 referer/origin 검증을 자동 수행한다. 검증 실패 시 모듈 처리가 거부된다.

### 액션별 토큰

시그니처:

- `Session::createToken(string $key = ''): string`
- `Session::verifyToken(string $token, string $key = '', bool $strict = true): bool`
- `Session::invalidateToken(string $token): bool`

사용:

```php
$token = Rhymix\Framework\Session::createToken('mymodule.action');
// 폼/링크에 $token 포함
$ok = Rhymix\Framework\Session::verifyToken($token, 'mymodule.action');
Rhymix\Framework\Session::invalidateToken($token);
```

`$key`는 액션 식별 문자열 — 같은 키로 생성·검증해야 일치. `$strict=false`면 invalidate 이후에도 짧은 grace 시간 동안 통과시킨다.

### `module.xml` CSRF 비활성

```xml
<action name="procExternalCallback" type="controller" check-csrf="false" />
```

기본은 GET/HEAD/OPTIONS만 면제 (`ModuleHandler::$_nocsrf_methods`).

## 신뢰 세션 (Trusted Session)

민감 작업(회원 정보 변경 등) 직전 비밀번호 재확인을 거치면 일정 시간 신뢰 상태로 전환.

```php
if (!Rhymix\Framework\Session::isTrusted()) {
    // 재확인 폼으로 리다이렉트
}
// ...
Rhymix\Framework\Session::setTrusted(1800);    // 30분 신뢰 유지
```

## 자동 로그인 (Autologin)

`config('session.autologin_lifetime')`(초)가 0이 아니면 활성화. 자체 토큰을 쿠키에 저장하고 만료 임박 시 자동 갱신.

`Session::login()` 자체는 autologin 인자가 없다 — `MemberController::doLogin($user_id, $password, $keep_signed)`의 `$keep_signed=true`로 트리거된다.

내부 동작:

1. 로그인 시 쿠키 토큰 생성 + DB(`autologin` 테이블)에 매핑 저장.
2. 다음 요청 시 토큰 검증 → 세션 자동 복원.
3. `autologin_refresh` 임계 초과 시 토큰 회전.

## SSL 분리 쿠키

HTTPS와 HTTP 사이트에서 별도 세션 키를 사용하는 정책 (`config('use_ssl_cookies')`).

- HTTPS 전용 영역은 `Secure` 쿠키로 별도 부세션을 관리.
- HTTP로 다운그레이드되면 부세션이 노출되지 않음 (관리자 작업 보호).

## 세션 도메인

`config('session.domain')`. 서브도메인 공유:

```php
'session' => [
    'domain' => '.example.com',
]
```

다중 사이트(domain_srl 분리) 환경에서 SSO를 원하면 공유 도메인 설정.

## 로그인 상태 쿠키

`Session::checkLoginStatusCookie()`가 다른 사이트와의 SSO 처리에 활용된다. 공통 도메인에 익명 토큰을 두고 다른 사이트가 그것으로 자동 로그인.

## DB 세션 저장소

`config('session.use_db') = true` 시 PHP 세션 저장소를 자체 DB(`session` 테이블)로 교체.

장점:
- 멀티 서버 환경에서 세션 공유.
- TTL/정리 자동.

단점:
- DB 부하 증가 — Redis 백엔드 권장.

## member 모듈과의 연동

`MemberController` (`modules/member/member.controller.php`)의 주요 액션:

- `procMemberLogin` — 로그인 폼 처리 → `Session::login()`.
- `procMemberLogout` — `Session::logout()`.
- `procMemberInsert` — 가입.
- `procMemberModifyInfo` — 정보 수정 (신뢰 세션 요구).
- `doLogin($user_id, $password)` — 프로그래매틱 로그인.

## 흔한 패턴

### 로그인 강제

```php
public function dispBoardWrite()
{
    if (!$this->user->isMember()) {
        throw new Rhymix\Framework\Exceptions\MustLogin;
    }
}
```

### 관리자 강제

```php
public function dispBoardAdminContent()
{
    if (!$this->user->isAdmin()) {
        throw new Rhymix\Framework\Exceptions\NotPermitted;
    }
}
```

### 토큰이 필요한 POST 액션

```php
public function procMemberDelete()
{
    if (!Rhymix\Framework\Session::isTrusted()) {
        $url = getUrl('', 'act', 'dispMemberCheckPassword', 'ru_act', 'procMemberDelete');
        $this->setRedirectUrl($url);
        return;
    }
    // ... 실제 삭제 ...
}
```

## 다음 문서

- 보안: [19-security.md](19-security.md)
- 다중 사이트: [22-multi-site-and-domain.md](22-multi-site-and-domain.md)
- 회원 모듈: [28-modules/member.md](28-modules/member.md)
