# Rhymix 코드베이스 문서

작성용 프롬프트는 [PROMPT.md](PROMPT.md)를 참고하시고, 실제 설치 및 AI 적용 방법은 하단의 "AI 어시스턴트 활용 방법"을 참고해주시기 바랍니다.

**Rhymix CMS**(PHP 기반 콘텐츠 관리 시스템)의 구조와 확장 메커니즘을 한국어로 정리한 문서 모음이다. 신규 기여자가 저장소를 빠르게 파악할 수 있도록 작성했다.

> LLM 어시스턴트가 이 저장소에서 작업한다면 [`llms.txt`](llms.txt)부터 읽는다. 그쪽은 진입 순서·명명 규칙·작성 규약을 압축한 LLM 전용 진입 문서다.

## Rhymix가 무엇인가

XpressEngine(XE) 1.8을 fork해 발전시킨 한국 커뮤니티 CMS다. 라이선스는 GPL v2+이며 PHP 7.4 이상에서 동작한다. 현재 버전은 `common/constants.php:6`의 `RX_VERSION` 상수에서 확인할 수 있다.

가장 큰 구조적 특징은 **두 개의 클래스 계층이 공존**한다는 점이다.

- **레거시 XE 시스템** — `classes/` 하위의 namespace 없는 전역 클래스 (`Context`, `ModuleHandler`, `ModuleObject`, `FileHandler` 등).
- **신형 Rhymix 프레임워크** — `common/framework/` 하위 `Rhymix\Framework\*` namespace (`Cache`, `DB`, `Storage`, `Template`, `Session` 등).

두 시스템은 `common/autoload.php`의 커스텀 autoloader로 통합된다. `DB`, `TemplateHandler`, `Mail`처럼 신형 framework 클래스를 직접 상속하는 얇은 호환 wrapper도 있지만, `Context`, `ModuleHandler`, `FileHandler`처럼 자체 구현을 계속 보유한 레거시 클래스도 많다.

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

## AI 어시스턴트 활용 설치방법

이 저장소는 Rhymix 본체의 `docs/` 디렉토리에 놓이도록 설계되어 있다. 본체 루트(보통 `index.php`가 있는 디렉토리) 안에 `docs/`로 배치한 뒤, 사용하는 AI 어시스턴트의 규칙/컨텍스트 파일에서 [`docs/llms.txt`](llms.txt)를 가장 먼저 읽도록 지시하면 된다. `llms.txt`는 도구 중립적인 [llmstxt.org](https://llmstxt.org) 표준을 따르므로 어떤 어시스턴트든 동일하게 활용할 수 있다.

> Rhymix 본체가 아직 없다면 먼저: `git clone https://github.com/rhymix/rhymix.git`

### 방법 1: clone + `.gitignore` (권장)

가장 안전하고 편하다. 본체 저장소 히스토리에는 어떤 변경도 남지 않으므로, 본체에 PR을 보내거나 upstream을 따라가도 충돌이 생기지 않는다.

```bash
# Rhymix 본체 루트에서
git clone https://github.com/zodkr/rx-docs.git docs

# 본체에 docs/가 untracked로 잡히지 않도록 무시 처리 (한 번만)
echo '/docs/' >> .gitignore
```

업데이트:

```bash
cd docs && git pull
```

제거:

```bash
rm -rf docs
```

### 방법 2: git submodule (본체를 fork해 자기 저장소로 관리하는 경우)

본체를 자신의 fork로 관리하고 docs를 특정 커밋에 **고정**해 팀원들과 일관된 버전을 공유하고 싶다면 submodule이 적합하다. 단, `.gitmodules` 파일이 본체 fork에 커밋된다는 점에 유의한다(upstream rhymix/rhymix에 PR을 보낼 때는 이 변경을 포함하지 않아야 한다).

```bash
# 본체 루트에서
git submodule add https://github.com/zodkr/rx-docs.git docs
git commit -m "chore: add docs submodule"
```

이미 submodule이 설정된 저장소를 새로 클론할 때:

```bash
git clone --recurse-submodules <본체 저장소 URL>
# 또는 이미 클론했다면
git submodule update --init --recursive
```

업데이트(최신 커밋으로 이동 후 본체에 커밋):

```bash
git submodule update --remote docs
git add docs && git commit -m "chore: bump docs submodule"
```

### AI 어시스턴트별 컨텍스트 파일

다음은 각 도구에서 흔히 사용하는 저장소 규칙 파일 경로다. 도구와 버전에 따라 자동 로드 여부가 다를 수 있으므로 설정을 확인하고, 해당 파일 안에 **"코드 탐색 전에 `docs/llms.txt`를 먼저 읽어라"**라고 명시한다. 현재 Rhymix 본체 checkout에는 아래 규칙 파일이 기본으로 추적되어 있지 않다.

| 도구 | 본체 루트에 둘 파일 | 비고 |
|---|---|---|
| Claude Code | `CLAUDE.md` | 본체 루트에 별도로 추가 |
| OpenAI Codex / 일반 OSS 에이전트 | `AGENTS.md` | 점차 표준화되는 도구 중립 규약 |
| Cursor | `.cursor/rules/rhymix.mdc` (또는 구형 `.cursorrules`) | rule 파일에 `docs/llms.txt` 우선 참조 명시 |
| Windsurf | `.windsurfrules` | 동일 |
| GitHub Copilot | `.github/copilot-instructions.md` | 저장소 단위 instructions |
| Gemini Code Assist | `GEMINI.md` | 워크스페이스 컨텍스트 |
| Cline / Roo Code | `.clinerules` | 동일 |

위 목록에 없는 도구라도 대부분 "프로젝트 규칙(rules)" 또는 "시스템 프롬프트"를 지정하는 기능이 있으므로, 거기서 `docs/llms.txt`를 가리키면 된다.

## 더 읽을 거리

- 공식 사이트: https://rhymix.org
- 공식 매뉴얼: https://rhymix.org/manual
- 코딩 규칙: https://rhymix.org/manual/contrib/coding-standards
- 이슈/PR: https://github.com/rhymix/rhymix (PR base 브랜치는 `master`)
- 보안 보고: `devops@rhymix.org` (GitHub 이슈가 아님)
