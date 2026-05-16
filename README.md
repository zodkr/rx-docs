# Rhymix 코드베이스 문서

이 디렉토리는 **Rhymix CMS** (PHP 기반 콘텐츠 관리 시스템)의 구조와 확장 메커니즘을 한국어로 정리한 문서 모음이다. LLM 어시스턴트와 신규 개발자가 저장소를 빠르게 파악하도록 작성했다.

## Rhymix가 무엇인가

XpressEngine(XE) 1.8을 fork해 발전시킨 한국 커뮤니티 CMS다. 라이선스는 GPL v2+이며 PHP 7.4 이상에서 동작한다. 현재 버전은 `common/constants.php:6`의 `RX_VERSION` 상수로 확인할 수 있다(2.1.33).

가장 큰 구조적 특징은 **두 개의 클래스 계층이 공존**한다는 점이다.

- **레거시 XE 시스템** — `classes/` 하위의 namespace 없는 전역 클래스 (`Context`, `ModuleHandler`, `ModuleObject`, `FileHandler` 등).
- **신형 Rhymix 프레임워크** — `common/framework/` 하위 `Rhymix\Framework\*` namespace (`Cache`, `DB`, `Storage`, `Template`, `Session` 등).

두 시스템은 `common/autoload.php`의 커스텀 autoloader로 통합되며, 대부분의 레거시 클래스는 신형 framework 클래스의 얇은 wrapper다.

## 문서 목차

### 기초

| 문서 | 내용 |
|---|---|
| [01-overview.md](01-overview.md) | Rhymix 개요, XE 관계, 핵심 디자인 원칙 |
| [02-infrastructure.md](02-infrastructure.md) | PHP 요구사항, 드라이버, 웹서버 설정 |
| [03-directory-structure.md](03-directory-structure.md) | 저장소 트리, 디렉토리 역할 |

### 요청 라이프사이클

| 문서 | 내용 |
|---|---|
| [04-bootstrap-and-request-lifecycle.md](04-bootstrap-and-request-lifecycle.md) | `index.php` ~ `Context::close()` 흐름 |
| [05-context.md](05-context.md) | `Context` 클래스 API 일람 |
| [06-module-handler-lifecycle.md](06-module-handler-lifecycle.md) | `ModuleHandler`/`ModuleObject` 라이프사이클 |
| [07-router.md](07-router.md) | `Rhymix\Framework\Router` 라우팅 엔진 |
| [08-display-and-response.md](08-display-and-response.md) | DisplayHandler와 응답 포맷 |
| [09-templates-and-skins.md](09-templates-and-skins.md) | 템플릿 v1/v2 엔진과 스킨 |

### 프레임워크 코어

| 문서 | 내용 |
|---|---|
| [10-framework.md](10-framework.md) | `Rhymix\Framework\*` 클래스 인덱스 |
| [11-legacy-classes.md](11-legacy-classes.md) | `classes/*` 레거시 클래스 인덱스 |
| [12-helpers-and-globals.md](12-helpers-and-globals.md) | 전역 함수, 상수, `$GLOBALS` |

### 서브시스템

| 문서 | 내용 |
|---|---|
| [13-event-and-trigger-system.md](13-event-and-trigger-system.md) | 트리거/애드온/eventHandler |
| [14-database-and-queries.md](14-database-and-queries.md) | DB 추상화, XML 쿼리 |
| [15-session-and-auth.md](15-session-and-auth.md) | Session, 로그인, CSRF |
| [16-i18n-and-lang.md](16-i18n-and-lang.md) | 다국어 시스템 |
| [17-cache-and-queue.md](17-cache-and-queue.md) | 캐시와 큐 |
| [18-mail-sms-push.md](18-mail-sms-push.md) | 메일/SMS/푸시 추상화 |
| [19-security.md](19-security.md) | CSRF/XSS/파일 업로드/IP 차단 |
| [20-storage-and-files.md](20-storage-and-files.md) | 파일 스토리지 |
| [21-cli-and-scripts.md](21-cli-and-scripts.md) | CLI 모드, cron, 정리 스크립트 |
| [22-multi-site-and-domain.md](22-multi-site-and-domain.md) | 다중 사이트 지원 |
| [23-mobile-detection.md](23-mobile-detection.md) | 모바일 감지 |
| [24-debug-and-logging.md](24-debug-and-logging.md) | 디버그/로깅 |
| [25-config-system.md](25-config-system.md) | 설정 시스템 |
| [26-namespaces-and-autoload.md](26-namespaces-and-autoload.md) | autoloader 4단계 분기 |

### 확장 포인트

| 문서 | 내용 |
|---|---|
| [27-extension-points/module.md](27-extension-points/module.md) | 모듈 작성법 |
| [27-extension-points/addon.md](27-extension-points/addon.md) | 애드온 작성법 |
| [27-extension-points/layout.md](27-extension-points/layout.md) | 레이아웃 작성법 |
| [27-extension-points/module-skin.md](27-extension-points/module-skin.md) | 모듈 스킨 작성법 |
| [27-extension-points/widget.md](27-extension-points/widget.md) | 위젯 작성법 |
| [27-extension-points/widgetstyle.md](27-extension-points/widgetstyle.md) | 위젯스타일 작성법 |
| [27-extension-points/editor-component.md](27-extension-points/editor-component.md) | 에디터 컴포넌트 작성법 |

### 코어 자원 카탈로그

- [28-modules/](28-modules/) — 코어 32개 모듈
- [29-addons/](29-addons/) — 코어 6개 애드온
- [30-widgets/](30-widgets/) — 코어 6개 위젯
- [31-widgetstyles/](31-widgetstyles/) — 코어 위젯스타일
- [32-layouts/](32-layouts/) — 코어 레이아웃 (PC + 모바일)
- [33-editor-components/](33-editor-components/) — 코어 에디터 컴포넌트
- [34-external-libraries.md](34-external-libraries.md) — Composer 패키지와 JS 라이브러리

### 개발/배포

| 문서 | 내용 |
|---|---|
| [35-testing-and-ci.md](35-testing-and-ci.md) | Codeception, GitHub Actions |

## "내가 X를 만들고 싶다" 빠른 참조

| 만들고 싶은 것 | 가야 할 문서 |
|---|---|
| 새 모듈 | [27-extension-points/module.md](27-extension-points/module.md) |
| 새 애드온 (요청 hook) | [27-extension-points/addon.md](27-extension-points/addon.md) |
| 새 위젯 | [27-extension-points/widget.md](27-extension-points/widget.md) |
| 새 레이아웃 (테마) | [27-extension-points/layout.md](27-extension-points/layout.md) |
| 모듈에 새 스킨 | [27-extension-points/module-skin.md](27-extension-points/module-skin.md) |
| 위젯 데코레이터 | [27-extension-points/widgetstyle.md](27-extension-points/widgetstyle.md) |
| 에디터에 새 컴포넌트 | [27-extension-points/editor-component.md](27-extension-points/editor-component.md) |
| 새 메일/SMS/푸시 드라이버 | [18-mail-sms-push.md](18-mail-sms-push.md) |
| 새 캐시/큐 드라이버 | [17-cache-and-queue.md](17-cache-and-queue.md) |
| 새 CLI 스크립트 | [21-cli-and-scripts.md](21-cli-and-scripts.md) |
| 기존 액션을 hook | [13-event-and-trigger-system.md](13-event-and-trigger-system.md) |

## LLM 권장 진입 순서

처음 코드베이스에 진입하는 LLM은 다음 순서로 읽으면 빠르게 적응할 수 있다.

1. [01-overview.md](01-overview.md) — Rhymix가 무엇인지.
2. [04-bootstrap-and-request-lifecycle.md](04-bootstrap-and-request-lifecycle.md) — 요청이 어떻게 흐르는지.
3. [06-module-handler-lifecycle.md](06-module-handler-lifecycle.md) — 모듈이 어떻게 실행되는지.
4. [27-extension-points/](27-extension-points/) — 확장 메커니즘 7종.
5. 작업할 모듈을 [28-modules/](28-modules/)에서 찾아 읽기.
6. 필요한 framework 클래스를 [10-framework.md](10-framework.md)에서 인덱스로 찾기.

## 코드 식별자 명명 규칙

레거시 모듈 클래스는 파일명과 1:1로 대응한다. autoloader가 다음 규칙으로 자동 매핑한다 (`common/autoload.php:75-86`).

| 클래스명 | 파일 |
|---|---|
| `Board` | `modules/board/board.class.php` |
| `BoardController` | `modules/board/board.controller.php` |
| `BoardModel` | `modules/board/board.model.php` |
| `BoardView` | `modules/board/board.view.php` |
| `BoardAdminController` | `modules/board/board.admin.controller.php` |
| `BoardAdminModel` | `modules/board/board.admin.model.php` |
| `BoardAdminView` | `modules/board/board.admin.view.php` |
| `BoardMobile` | `modules/board/board.mobile.php` |
| `BoardApi` | `modules/board/board.api.php` |
| `BoardWap` | `modules/board/board.wap.php` |

신형 namespace 모듈은 `Rhymix\Modules\Board\Controllers\Foo` 형식을 사용하며 `module.xml`의 `<action class="Controllers\Foo" />`로 등록한다.

## 작성 원칙

- 모든 코드 참조는 `file_path:line_number` 형식.
- `@deprecated` 표시 메서드/클래스는 설명하지 않음.
- PHP 8.4 기준 문법으로 예제 작성.
- 추측 금지 — 모든 내용은 실제 코드 또는 `info.xml`에서 확인.
