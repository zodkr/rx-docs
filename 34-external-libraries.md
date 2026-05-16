# 34. 외부 라이브러리

Rhymix가 사용하는 외부 PHP/JS/CSS 라이브러리. 3개 범주로 분류한다.

## 1. Composer 패키지 (변경 없이 사용)

`common/composer.json`이 정의. `common/vendor/`에 설치되어 커밋된다.

| 패키지 | 버전 | 용도 |
|---|---|---|
| `bordoni/phpass` | `0.3.6` | phpass 비밀번호 해싱 (옛 XE 호환). |
| `composer/ca-bundle` | `*` | CA 인증서 번들 (curl/openssl용). |
| `coolsms/php-sdk` | `2.*` | CoolSMS SDK. |
| `doctrine/lexer` | `1.*` | 이메일 검증 의존성. |
| `egulias/email-validator` | `3.2.*` | 이메일 형식 검증. |
| `enshrined/svg-sanitize` | `0.*` | SVG XSS 정화. |
| `ezyang/htmlpurifier` | `4.18.*` | HTML 정화 (HTMLFilter 백엔드). |
| `firebase/php-jwt` | `6.4.0` | JWT 토큰. |
| `google/auth` | `1.26.*` | Google OAuth (FCM v1). |
| `guzzlehttp/guzzle` | `7.9.*` | HTTP 클라이언트 (`Rhymix\Framework\HTTP` 백엔드). |
| `guzzlehttp/psr7` | `2.7.*` | PSR-7 메시지. |
| `jbbcode/jbbcode` | `1.4.*` | BBCode 파서. |
| `leafo/lessphp` | `dev-master` | LESS → CSS 컴파일. |
| `league/html-to-markdown` | `5.1.*` | HTML → Markdown. |
| `matthiasmullie/minify` | `1.3.*` | JS/CSS 압축. |
| `matthiasmullie/path-converter` | `1.1.*` | 압축 시 경로 변환. |
| `michelf/php-markdown` | `1.9.*` | Markdown → HTML. |
| `michelf/php-smartypants` | `1.8.*` | 스마트 따옴표. |
| `psr/cache` | `1.0.1` | PSR-6 캐시 인터페이스. |
| `rmccue/requests` | `1.8.*` | HTTP 폴백. |
| `scssphp/scssphp` | `1.13.*` | SCSS → CSS 컴파일. |
| `swiftmailer/swiftmailer` | `6.3.0` | 메일 발송 (`Rhymix\Framework\Mail` 백엔드). |
| `symfony/deprecation-contracts` | `2.5.*` | 호환성. |
| `true/punycode` | `2.*` | IDN ↔ punycode. |

## 2. Bundled PHP libraries (수정 또는 비-composer)

`common/libraries/`. composer로 관리하지 않는 PHP 파일.

| 파일 | 용도 |
|---|---|
| `cryptocompat.php` | `hash_equals` 폴리필 (PHP 5.6 미만 호환, 현재는 무력화). |
| `ftp.php` | XE 시절의 PHP FTP 클래스. Rhymix용 일부 수정. `Storage::FTP` 폴백에서 사용. |
| `swift_mail.php` | Swift 호환 헬퍼. |
| `tar.php` | 순수 PHP tar 압축/해제 (모듈 설치/백업용). |
| `vendorpass.php` | 패스워드 호환성 wrapper. |

## 3. JavaScript 라이브러리

`common/js/plugins/` 하위. **jQuery 자체는 본 문서 대상 외**(요청 사항).

### 각 플러그인 형식

```
common/js/plugins/<name>/
├── plugin.load      # 로드할 파일 목록 매니페스트
├── *.js, *.css      # 실제 자원
└── (선택 자원)
```

`Context::loadJavascriptPlugin('<name>')` 호출 시 `plugin.load`를 읽어 모든 자원 자동 로드.

### 카탈로그

#### ckeditor (CKEditor 4)

**위치**: `common/js/plugins/ckeditor/ckeditor/`.

**Rhymix 커스텀 플러그인 2종**:

- **`plugins/xe_component/plugin.js`** — Rhymix 에디터 컴포넌트 시스템 통합.
  - CKEditor 도구바에 컴포넌트 버튼 동적 생성 (config `xe_component_arrays` 기반).
  - 더블클릭 시 컴포넌트 편집 팝업 호출 (`window.openComponent`).
  - 본문 내 컴포넌트 마커 시각화.

- **`plugins/rx_paste/plugin.js`** — Rhymix 전용 붙여넣기 정화.
  - 외부 에디터(Word/Google Docs)에서 붙여넣기 시 불필요한 스타일 제거.
  - 첨부 이미지 자동 업로드.

**기본 CKEditor 플러그인 (40개+)**:

`a11yhelp`, `about`, `clipboard`, `colordialog`, `copyformatting`, `dialog`, `div`, `divarea`, `exportpdf`, `find`, `flash`, `forms`, `iframe`, `image`, `imageresize`, `ios_enterkey`, `link`, `liststyle`, `magicline`, `onchange`, `pagebreak`, `pastefromgdocs`, `pastefromlibreoffice`, `pastefromword`, `pastetools`, `preview`, `scayt`, `tableresize`, `tabletools`, `wsc`, `xml`, ...

**로딩**:

```
plugin.load
└── ckeditor/ckeditor.js
```

#### jquery.fileupload (blueimp + Rhymix 래퍼)

**위치**: `common/js/plugins/jquery.fileupload/`.

**원본**: [blueimp/jQuery-File-Upload](https://github.com/blueimp/jQuery-File-Upload). MIT.

**Rhymix 추가물**:

- `js/main.js` — Rhymix 전용 래퍼.
  - Handlebars 템플릿 사용.
  - `xefu-*` 셀렉터로 마커 검출.
  - 이미지/비디오/일반 파일 별 리스트 분리.
  - 커버 이미지 지정 UI.
  - 자동 업로드 모드.

**plugin.load**:

```
css/jquery.fileupload.css
css/style.css
js/vendor/jquery.ui.widget.js
js/jquery.iframe-transport.js
js/jquery.fileupload.js
js/main.js
```

에디터/회원 프로필/첨부 UI에서 광범위하게 사용.

#### blankshield

`window.opener` 누수 방지. `target="_blank"`로 열 때 보안.

#### cookie

`js-cookie` (v2.x). 쿠키 read/write 간편 API.

#### filebox

Rhymix 자체 제작. 파일 선택 UI 위젯.

#### foggyLayer

Rhymix 자체 제작. 모달 오버레이.

#### handlebars / handlebars.runtime

Handlebars.js 템플릿 엔진. 컴파일/런타임 분리.

#### hotkeys

jQuery 핫키 (`jquery.hotkeys-packed.js`).

#### jquery.finderSelect

파인더 스타일 선택 UI (다중 선택, shift+click 범위).

#### jquery.migrate

jQuery 1.x → 3.x 마이그레이션 헬퍼. **1.4.1과 3.6.0 두 버전 동봉**.

`config('view.jquery_version')` 값에 따라 선택.

#### qtip

qTip2 툴팁.

#### spectrum

컬러 피커.

#### ui (jQuery UI)

전체 jQuery UI. 다이얼로그/탭/슬라이더/datepicker 등.

#### ui.calendar, ui.colorpicker, ui.krzip, ui.tree

XE 시절의 jQuery UI 기반 위젯들.

- **ui.krzip** — 한국 우편번호 검색 위젯. `krzip` 모듈과 연동.
- **ui.tree** — 트리 위젯 (메뉴 편집 등).
- **ui.calendar** — 캘린더.
- **ui.colorpicker** — 컬러 피커 (구버전).

#### uri

URI.js — URL 파싱/조작.

#### watchinput

입력 변화 감지 (debounced input events).

## 4. 폰트/CSS

`common/css/`:

- **Bootstrap 2.x** (`bootstrap.css`, `bootstrap-responsive.css`) — XE 호환용 옛 버전.
- **`rhymix.scss`** — Rhymix 공통 SCSS.
- **`xeicon/`** — XEIcon v1.0.4 (SIL OFL 1.1, MIT 라이선스). 약 680개 아이콘 폰트.

## 5. JS 진입 파일

`common/js/`:

- `common.js` — 공통 함수 (`XE.checkboxToggleAll` 등).
- `x.js` — XE 호환 글로벌 함수.
- `js_app.js` — 통합 app 진입.
- `debug.js` — 디버그 패널.
- `modernizr.js` — 기능 감지.
- `xml2json.js`, `xml_handler.js`, `xml_js_filter.js` — XML-RPC 통신.
- `jquery-2.2.4.js`, `jquery-3.7.1.js` — 두 버전 jQuery (jQuery 자체는 본 문서 범위 외이나 위치 표기).
- `polyfills/formdata.min.js`, `polyfills/promise.min.js` — 구브라우저 폴리필.

## 라이선스

각 라이브러리는 자체 라이선스를 따른다. 주요 라이선스:

- MIT — jQuery, Bootstrap, blueimp/jQuery-File-Upload, qTip2, Handlebars, Spectrum, js-cookie 등.
- GPL/MIT (dual) — CKEditor 4 (LGPL/GPL/MPL).
- BSD — phpass, Markdown 등.
- SIL OFL 1.1 — XEIcon.
- Apache 2.0 — Google Auth.

번들 시 `LICENSE.txt`를 함께 동봉.

## 업데이트

Composer 의존성 업데이트는 `common/`에서 수행 (project root 아님):

```bash
cd common && composer update <package>
```

업데이트 후 변경 사항을 `common/vendor/`에 커밋.

## 다음 문서

- 메일/SMS/푸시 (Composer 패키지 활용): [18-mail-sms-push.md](18-mail-sms-push.md)
- 에디터 모듈 (CKEditor 활용): [28-modules/editor.md](28-modules/editor.md)
- 파일 (jquery.fileupload 활용): [28-modules/file.md](28-modules/file.md)
- 한국 우편번호 (ui.krzip 활용): [28-modules/krzip.md](28-modules/krzip.md)
