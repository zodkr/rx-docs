# 01. Rhymix 개요

## Rhymix란

Rhymix는 **PHP로 작성된 콘텐츠 관리 시스템(CMS)**이며, **XpressEngine(XE) 1.8을 fork**해 발전시킨 한국 커뮤니티 친화 CMS다. 게시판, 회원, 페이지, 다중 사이트, 모바일 자동 분기, 모듈/애드온/위젯/스킨 등 풍부한 확장 메커니즘을 가진다.

- 최초 fork 시점부터 약 10여 년간 독자 개발이 진행되어 왔다.
- XpressEngine 호환성을 의도적으로 유지하므로 옛 XE 모듈/위젯/애드온/스킨 다수가 큰 수정 없이 동작한다.

## XpressEngine과의 관계

- XE는 LGPL v2.1로 배포되었다.
- Rhymix는 **LGPL §3에 따라 GPL v2+로 라이선스 전환**했으며, 이는 비가역이다 (`index.php:29-34`).
- `__XE__`, `__ZBXE__`, `__XE_VERSION__` 등 XE 호환 상수를 그대로 유지한다 (`common/constants.php:133-151`).
- `classes/` 하위의 전역 클래스 구조는 XE 시절 구조를 보존한다.
- 신규 코드는 `Rhymix\Framework` 네임스페이스에 작성한다.

## 핵심 디자인 원칙

### 1. 컨벤션 기반 라우팅

액션 메서드는 접두사로 의미를 갖는다.

| 접두사 | 의미 |
|---|---|
| `disp*` | HTML 페이지 표시 (View 계열) |
| `proc*` | 처리/변경 액션 (Controller 계열) |
| `get*` | 데이터 조회 (Model/API 계열) |

`ModuleActionParser`가 이를 활용해 `module.xml`의 type 속성을 자동 결정한다 (`common/framework/parsers/ModuleActionParser.php`).

### 2. XML 기반 메타데이터

대부분의 메타정보는 XML 파일로 선언적으로 기술된다.

| 파일 | 용도 |
|---|---|
| `conf/info.xml` | 플러그인 메타(title, description, version, author, extra_vars) |
| `conf/module.xml` | 모듈 액션, 권한, 메뉴, 라우트, 트리거 핸들러 |
| `queries/*.xml` | 선언적 DB 쿼리 |
| `schemas/*.xml` | DB 테이블 정의 |
| `ruleset/*.xml` | 입력 검증 규칙 |
| `skin.xml` | 스킨/레이아웃/위젯스타일 메타와 사용자 변수 |

파서는 `common/framework/parsers/`에 모여 있다.

### 3. 두 클래스 계층의 공존

- **레거시**: `classes/` 하위, namespace 없음. 모든 모듈은 `ModuleObject`를 상속.
- **신형**: `common/framework/`, `Rhymix\Framework\*`. PSR-4 스타일.

대부분의 레거시 클래스는 신형의 wrapper다. 예시:

```php
// classes/db/DB.class.php
class DB extends Rhymix\Framework\DB {}
```

### 4. 동적 모듈 인스턴스 캐싱

`ModuleObject::getInstance()`가 `$GLOBALS['_module_instances_']`에 인스턴스를 캐싱한다 (`classes/module/ModuleObject.class.php`). `getController('member')`, `getModel('document')` 같은 헬퍼 함수는 모두 이 캐시를 거친다 (`common/legacy.php`).

### 5. 통일된 응답 모델

모든 모듈/위젯의 조상인 `BaseObject`(`classes/object/Object.class.php`)는 `error`/`message`/`variables` 상태와 `setError`/`get`/`add`/`toBool` API를 제공한다. 에러 상태는 `toBool()`로 평가되어 트리거/액션 중단을 결정한다.

## 라이선스

- **GPL v2 또는 그 이후 버전** (GPL-2.0-or-later).
- XE의 LGPL과 호환되지만 한 번 GPL로 전환된 부분은 되돌릴 수 없다.
- 보안 보고는 GitHub 이슈가 아닌 `devops@rhymix.org`로 (`SECURITY.md`).

## 버전과 호환성

- 현재 버전: **2.1.33** (`common/constants.php:6`).
- 최소 PHP: **7.4** (`common/autoload.php:14-19`, `composer.json`의 `require.php`).
- 권장 PHP: **8.1+**.
- CI 매트릭스: PHP **7.4 ~ 8.5** (`.github/workflows/ci.yml`).
- DB: MySQL 5.5+ / MariaDB 10+.

## 가장 자주 보게 될 디렉토리 5종

| 디렉토리 | 무엇이 있나 |
|---|---|
| `modules/` | 코어 32개 모듈. 게시판/회원/페이지 등 도메인 단위. |
| `common/framework/` | 신형 `Rhymix\Framework\*` 클래스. 캐시/DB/세션/메일 등. |
| `classes/` | XE 레거시 전역 클래스. `Context`, `ModuleHandler`가 여기. |
| `addons/` | 코어 동봉 애드온 6개. 요청 라이프사이클 hook. |
| `widgets/` | 코어 동봉 위젯 6개. 레이아웃에 끼워 넣는 동적 컴포넌트. |

각 디렉토리의 역할은 [03-directory-structure.md](03-directory-structure.md)에서 표로 정리한다.

## 다음 문서

- 환경/요구사항: [02-infrastructure.md](02-infrastructure.md)
- 디렉토리 트리: [03-directory-structure.md](03-directory-structure.md)
- 요청 라이프사이클: [04-bootstrap-and-request-lifecycle.md](04-bootstrap-and-request-lifecycle.md)
