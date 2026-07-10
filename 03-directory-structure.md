# 03. 디렉토리 구조

저장소 루트의 2단계 구조와 각 디렉토리 역할을 정리한다.

## 루트 트리 (2단계)

```
rhymix/
├── addons/                       # 코어 동봉 애드온 6개
│   ├── adminlogging/
│   ├── autolink/
│   ├── counter/
│   ├── member_extra_info/
│   ├── photoswipe/
│   └── point_level_icon/
├── classes/                      # XE 레거시 전역 클래스
│   ├── cache/      context/    db/         display/
│   ├── editor/     extravar/   file/       frontendfile/
│   ├── handler/    httprequest/ mail/      mobile/
│   ├── module/     object/     page/       security/
│   ├── template/   validator/  widget/     xml/
├── common/                       # 프레임워크, 헬퍼, 자원
│   ├── framework/                # Rhymix\Framework\*
│   ├── vendor/                   # Composer 패키지 (커밋됨)
│   ├── libraries/                # 번들 PHP 라이브러리
│   ├── js/                       # 공통 JavaScript
│   ├── css/                      # 공통 CSS / XEIcon
│   ├── img/                      # 공통 이미지
│   ├── lang/                     # 코어 다국어
│   ├── tpl/                      # 공통 템플릿
│   ├── defaults/                 # 기본 설정/예약어
│   ├── scripts/                  # CLI 정리 스크립트
│   ├── manual/                   # 매뉴얼, 서버 설정 예시
│   ├── autoload.php              # autoloader + 부트스트랩
│   ├── constants.php             # RX_* 상수
│   ├── functions.php             # 전역 유틸 함수
│   ├── legacy.php                # XE 호환 헬퍼 (getController 등)
│   ├── composer.json             # Composer 매니페스트
│   └── composer.lock             # 잠금 파일
├── config/                       # 설정 진입점 (단일 파일)
│   └── config.inc.php            # autoload bridge
├── layouts/                      # PC 레이아웃 3종
│   ├── default/
│   ├── user_layout/
│   └── xedition/
├── m.layouts/                    # 모바일 레이아웃 3종
│   ├── colorCode/
│   ├── default/
│   └── simpleGray/
├── modules/                      # 코어 모듈 32개
│   ├── addon/      admin/      adminlogging/  advanced_mailer/
│   ├── autoinstall/ board/     comment/       communication/
│   ├── counter/    document/   editor/        extravar/
│   ├── file/       importer/   install/       integration_search/
│   ├── krzip/      layout/     member/        menu/
│   ├── message/    module/     ncenterlite/   page/
│   ├── point/      poll/       rss/           session/
│   ├── spamfilter/ tag/        trash/         widget/
├── tests/                        # Codeception 스위트
│   ├── unit/      install/    _data/   _support/
│   ├── unit.suite.dist.yml
│   └── install.suite.dist.yml
├── widgets/                      # 코어 위젯 6개
├── widgetstyles/                 # 코어 위젯스타일
├── index.php                     # HTTP/CLI 진입점
├── .htaccess                     # Apache 라우팅/차단
├── README.md                     # 설치 사용자용
├── LICENSE                       # GPL v2+
└── SECURITY.md                   # 보안 보고 정책
```

## 최상위 디렉토리 역할표

| 디렉토리 | 역할 | 비고 |
|---|---|---|
| `addons/` | 요청 라이프사이클 hook(애드온) | 6개 |
| `classes/` | XE 시대 전역 클래스 | namespace 없음 |
| `common/` | 프레임워크/헬퍼/벤더/정적자원 | 가장 핵심 |
| `config/` | 설정 진입점 | autoload bridge |
| `layouts/` | PC 레이아웃 | 3종 |
| `m.layouts/` | 모바일 레이아웃 | 3종 |
| `modules/` | 코어 모듈 32개 | 게시판/회원/페이지 등 |
| `tests/` | 자동화 테스트 | Codeception |
| `widgets/` | 코어 위젯 | 6종 |
| `widgetstyles/` | 위젯 데코레이터 | 1종 |

## 외부 플러그인 위치 (선택)

다음 디렉토리는 코어가 자동 인식하지만 기본 생성되지 않는다.

| 디렉토리 | 용도 | autoloader 분기 |
|---|---|---|
| `plugins/` | 통합 플러그인 (자체 namespace) | `Rhymix\Plugins\*` 또는 `RX_NAMESPACES` |
| `themes/` | 테마 패키지 | `Rhymix\Themes\*` |

`.htaccess`와 nginx 샘플 설정에는 이 디렉토리의 보호 규칙이 미리 들어가 있다.

## 런타임 생성 디렉토리 (`files/`)

`files/`는 gitignore로 제외되며 첫 설치 시 자동 생성된다. 모두 웹서버 쓰기 권한이 필요하다.

| 경로 | 용도 | 정리 스크립트 |
|---|---|---|
| `files/attach/binaries/<YYYY>/<MM>/<DD>/` | 업로드 파일 본문 (신규 설치 기본값 `file.folder_structure=2`, 날짜별 경로; 레거시(1/0)는 `.../<module_srl>/<srl 3자리 분할>/`) | `common/scripts/clean_garbage_files.php` |
| `files/attach/images/<YYYY>/<MM>/<DD>/` | 이미지 업로드 + 썸네일 (경로 규칙은 binaries와 동일) | 동일 |
| `files/attach/xeicon/` | 사용자 정의 xeicon | — |
| `files/cache/` | 일반 캐시 | `Cache::clearAll`로 비움 |
| `files/cache/template/` | 컴파일된 템플릿 | 자동 무효화 |
| `files/cache/store/` | Dummy 캐시의 `force=true` 영속 항목 저장소(File 구현은 직접 선택 불가) | 만료 항목은 조회 시 제거 |
| `files/cache/assets/` (하위 `minified/`=minify, `compiled/`=LESS·SCSS 컴파일, `combined/`=concat 결합) | CSS/JS minify·compile·concat 산출물 | 자동 |
| `files/cache/lang/` | 컴파일된 다국어 캐시 | 자동 |
| `files/cache/addons/` | 컴파일된 애드온 (PC/모바일) | 변경 시 자동 |
| `files/locks/` | 파일 기반 락 (`Storage::getLock`) | — |
| `files/config/` | `config.php` 등 런타임 설정 | 수동 |
| `files/env/` | 환경 캐시 (mid info 등) | 자동 |
| `files/member_extra_info/` | 회원 부가 정보 (프로필 이미지/서명) | — |
| `files/faceOff/` | 레이아웃 소스 편집(faceOff)이 레이아웃별 layout.html/layout.css 저장 | — |
| `files/ruleset/` | 생성·커스터마이즈된 ruleset XML (런타임에 PHP가 읽음) | 자동 |
| `files/thumbnails/` | 문서 썸네일 | `common/scripts/clean_old_thumbnails.php` |
| `files/cache/tmp/` | 일시 작업 디렉토리 | — |
| `files/debug/YYYYMMDD.php` | 디버그 로그 (옵션, 경로는 설정 `debug.log_filename`) | 수동/날짜별 파일 로테이션 |

상세 정리 스크립트 매핑: [21-cli-and-scripts.md](21-cli-and-scripts.md).

## modules/<name>/ 표준 구조

모든 모듈이 동일 구조를 가지지는 않지만, 다음 항목들은 관습적이다.

```
modules/<name>/
├── <name>.class.php              # ModuleObject 상속 (v1 필수, v2는 선택)
├── <name>.controller.php         # v1 액션 처리 (procXxx)
├── <name>.model.php              # v1 데이터 조회 (getXxx)
├── <name>.view.php               # v1 HTML 렌더 (dispXxx)
├── <name>.mobile.php             # v1 모바일 분기
├── <name>.api.php                # v1 JSON/XML-RPC API
├── <name>.wap.php                # v1 WAP (희소, 신규 모듈에 만들지 말 것)
├── <name>.admin.controller.php   # v1 관리자 액션
├── <name>.admin.model.php
├── <name>.admin.view.php
├── conf/
│   ├── info.xml                  # 메타
│   └── module.xml                # 액션/권한/메뉴/트리거
├── lang/<lang>.php               # 다국어
├── queries/*.xml                 # 선언적 쿼리
├── schemas/*.xml                 # 테이블 정의
├── ruleset/*.xml                 # v1 입력 검증 (v2 deprecated)
├── tpl/                          # 모듈 내장 템플릿(관리자 화면 등)
├── skins/<skin>/                 # PC 스킨
├── m.skins/<skin>/               # 모바일 스킨
├── controllers/, models/, views/ # v2 namespace 클래스 (PSR-4 권장)
├── scripts/                      # CLI 스크립트 (php index.php <module>.<script>)
└── script/                       # install 모듈 전용 — 설치 화면 lang/정적 컨텐츠
```

자세한 모듈 스펙: [27-extension-points/module.md](27-extension-points/module.md).

## 차단되는 파일/디렉토리 패턴

다음은 외부에서 직접 접근하지 못하도록 `.htaccess`/nginx 설정이 차단한다.

- `.git/`, `.gitignore`, `.gitattributes` (`.git*`), `.travis*`, `codeception.*`, `Gruntfile.js`, `package.json`, `CONTRIBUTING`/`COPYRIGHT`/`LICENSE`/`README`.
- `.ht*` (Apache 설정).
- `composer.json`, `composer.lock` (`composer.*`).
- `files/attach`, `files/config`, `files/cache` 하위의 `*.php`/`*.inc`/`*.bak` 등 스크립트 확장자, `files/faceOff`, `files/ruleset` 하위의 `*.html`/`*.xml`/`*.blade.php` (`*.tpl`는 차단 대상 아님).
- `files/env/` 전체, `files/member_extra_info/new_message_flags/`와 `files/member_extra_info/point/` 전체.
- `common/tpl/` 하위 `*.html`/`*.xml`/`*.blade.php` (`common/vendor/`에 대한 차단 규칙은 없음).
- 모듈 내부의 `queries/*.xml`, `schemas/*.xml`, `ruleset/*.xml` (런타임에 PHP가 읽음).

새 디렉토리 추가 시 같은 차단이 자동 적용되지 않으므로 직접 보호해야 한다 (`Storage::protectDirectory`).

## 다음 문서

- 부트스트랩 흐름: [04-bootstrap-and-request-lifecycle.md](04-bootstrap-and-request-lifecycle.md)
- autoloader 동작: [26-namespaces-and-autoload.md](26-namespaces-and-autoload.md)
