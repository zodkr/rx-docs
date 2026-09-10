# 36. deprecated / 삭제된 API

## 존재 의의

이 폴더는 **기존 서드파티(모듈·애드온·스킨·레이아웃·위젯) 혹은 코드의 deprecated된 부분들에 대해 명확한 가이드를 제공하기 위해** 있다. 어떤 API가 deprecated 또는 삭제되었는지, 어느 버전부터인지, 무엇으로 바꿔야 하는지를 한 곳에서 답한다. 옛 XE·Rhymix 2.0 시절 코드를 유지보수하거나 현재 버전으로 이전할 때 추측 대신 이 표를 근거로 판단한다.

본문 문서(01~35)는 현행 API만 예시로 쓴다. 이 폴더는 옛 코드에서 만난 심볼의 대체 API를 찾는 **조회용** 문서다. 진입 순서에 넣지 않으며, 필요할 때 심볼명으로 grep해서 쓴다.

```bash
grep -rn "addJsFile" docs/36-deprecated/
```

## 규칙

- **`@deprecated`·삭제된 API는 신규 코드와 이번 작업에서 수정하는 줄에 쓰지 않는다.** 본문 문서는 현행 API만 예시로 쓰며, deprecated 심볼을 언급할 때는 `` `X` (`@deprecated` → `대체`) `` 형식으로만 표시한다. 목록·대체 API·시점 구분은 [36-deprecated/](36-deprecated/)에서 심볼명으로 grep한다.
- **기존 코드의 deprecated 사용:** 손대지 않는 줄은 바꾸지 않되 최종 보고에 `파일:줄 → 대체 API` 목록으로 보고한다. 파일 단위 일괄 전환은 사용자가 명시적으로 요청할 때만 한다. 삭제된 API([36-deprecated/removed.md](36-deprecated/removed.md), 예: `Object` → `BaseObject`)는 호출 즉시 fatal error이므로 발견 즉시 고친다.
- **전역 `Security`·`Password`·`IpFilter`·`Purifier`·`EmbedFilter`는 `@deprecated` 래퍼다.** 코드와 문서에서 항상 `Rhymix\Framework\Security`, `Rhymix\Framework\Password`, `Rhymix\Framework\Filters\IpFilter`, `Rhymix\Framework\Filters\HTMLFilter`, `Rhymix\Framework\Filters\MediaFilter`처럼 전체 이름 또는 `use` 문을 쓴다.

위 세 항목은 [../llms.txt](../llms.txt)의 "작업 전 필수 규약"과 같은 문장이다. 한쪽을 고치면 다른 쪽도 고친다(`check` 모드가 대조한다).

## deprecated와 삭제의 차이

| 구분 | 상태 | 신호 | 처리 |
|---|---|---|---|
| `@deprecated` | 현재 커밋에서 **여전히 동작**한다. 본체도 아직 여러 곳에서 호출한다(표의 `코어 호출 있음`). | Rhymix는 `E_USER_DEPRECATED`를 발생시키지 않는다. 런타임으로는 알 수 없고 docblock과 이 폴더가 유일한 신호다. | 신규 코드·수정 줄에서 대체 API를 쓴다. 손대지 않는 줄은 보고만 한다. |
| 삭제됨 | 호출 즉시 fatal error(`Class not found`, `Call to undefined method`). | Rhymix는 `@deprecated` 예고 없이 삭제하는 경우가 있다. 2.0.24에서 deprecated였던 항목은 하나도 삭제되지 않은 반면, `XmlGenerater`·`ModuleInstaller`·`boardWAP` 등은 예고 없이 사라졌다. | 발견 즉시 대체한다. 대표 예: `Object` (removed 2.1 → `BaseObject`). |

그래서 [removed.md](removed.md)는 `@deprecated` 스캔이 아니라 릴리스 스냅숏 diff로 만든다.

## 파일 구성

| 파일 | 내용 | 판정 기준 |
|---|---|---|
| [xe.md](xe.md) | XE 1.8.0(fork 기준선)에 이미 `@deprecated`였던 PHP API | 태그 `1.8.0`에서 표시 |
| [rhymix-1.x.md](rhymix-1.x.md) | Rhymix 1.9.x에서 deprecated 처리된 PHP API | 태그 `1.9.0`·`1.9.13`에서 처음 표시 |
| [rhymix-2.0.md](rhymix-2.0.md) | Rhymix 2.0.0~2.0.24에서 deprecated 처리된 PHP API | 태그 `2.0.0`·`2.0.24`에서 처음 표시 |
| [rhymix-2.1.md](rhymix-2.1.md) | Rhymix 2.1.0~현재에서 deprecated 처리된 PHP API | 태그 `2.1.0` 또는 HEAD에서 처음 표시 |
| [javascript.md](javascript.md) | `common/js/*.js`의 `@deprecated` 함수. 시점 열 포함 | 동일 |
| [removed.md](removed.md) | `@deprecated` 없이 삭제된 공개 API | 스냅숏에 있었고 HEAD에서 해석 불가 |

항목 수는 각 파일 머리의 "항목 수"에 있다. README를 제외한 파일은 모두 생성 파일이므로 직접 고치지 않는다.

## 표 읽는 법

| 열 | 내용 |
|---|---|
| 심볼 | `Context::addJsFile()`, `checkCSRF()`, `class Security`, `file common/scripts/clean_old_logs.php`. 메서드는 정적·인스턴스 구분 없이 `Class::method()`. 대소문자는 HEAD 선언 기준 |
| 위치 | HEAD의 선언 줄. 본체 루트 기준 `file:line` |
| 유래 | 심볼이 처음 존재한 스냅숏. `XE` / `1.x` / `2.0` / `2.1`. 학습 데이터 시대를 짐작하는 데 쓴다 |
| 대체 API | `tools` 브랜치 `deprecated/overrides.json`의 값이 최우선. 없으면 docblock의 `Use X instead`. 그것도 없으면 deprecated 본문이 한 줄 위임일 때만 `추정: X`. 나머지는 `확인 필요`(소스를 직접 읽는다) 또는 `없음`(대체 없이 제거된 기능) |
| 비고 | docblock 메모, 표시된 태그, `코어 호출 있음`, 이름 충돌 경고, 수기 메모 |

`removed.md`의 "마지막 존재"는 `태그 경로:줄`이고, 절 제목의 제거 시점은 그 다음 릴리스 태그 기준이다.

## 이름 충돌 경고

전역 클래스 `Security`·`Password`·`IpFilter`·`Purifier`·`EmbedFilter`(`classes/security/`)는 모두 `@deprecated` 래퍼다. `use` 문 없는 레거시 모듈에서 `Security::getRandom()`처럼 쓰면 래퍼로 간다. 현행 클래스는 다음과 같다.

| 전역(deprecated) | 현행 |
|---|---|
| `Security` | `Rhymix\Framework\Security` |
| `Password` | `Rhymix\Framework\Password` |
| `IpFilter` | `Rhymix\Framework\Filters\IpFilter` |
| `Purifier` | `Rhymix\Framework\Filters\HTMLFilter` |
| `EmbedFilter` | `Rhymix\Framework\Filters\MediaFilter` |
| `XmlParser` / `XeXmlParser` | `Rhymix\Framework\Parsers\XEXMLParser` (`XmlParser`는 `XeXmlParser`의 `class_alias`, 둘 다 deprecated) |
| `XEHttpRequest` | `Rhymix\Framework\HTTP` |

## 시점 판정 방법

Rhymix 저장소의 릴리스 태그 스냅숏을 **릴리스 날짜순**으로 대조한다. `git blame`이 필요 없으므로 depth 1 체크아웃으로 충분하다.

| 태그 | 날짜 | 시점 | 비고 |
|---|---|---|---|
| `1.8.0` | 2015-04-08 | XE | XE 1.8.0 그 자체(README 첫 줄이 XpressEngine). fork 기준선 |
| `1.9.0` | 2017-12-01 | 1.x | 첫 Rhymix 릴리스(`common/framework/` 등장) |
| `2.0.0` | 2020-12-18 | 2.0 | |
| `1.9.13` | 2021-10-08 | 1.x | 2.0.0 **이후**에 나온 1.9 유지보수 릴리스 |
| `2.0.24` | 2022-12-21 | 2.0 | 2.0 마지막 |
| `2.1.0` | 2023-06-21 | 2.1 | |
| HEAD | 문서 검증 커밋 | 2.1 | [../README.md](../README.md#검증-기준) |

- **처리 시점** = 날짜순으로 처음 `@deprecated`가 붙은 태그. 2.0.0에서 표시되고 1.9.13에도 있으면 2.0이다(백포트). 1.9.13에만 있으면 1.x로 두고 비고에 적는다.
- **유래** = 날짜순으로 심볼이 처음 존재한 태그.
- **삭제** = 기준선(`1.8.0`, `2.0.24`)에 있던 public/protected 심볼이 HEAD에서 해석되지 않을 때. 해석은 `class_alias`, `extends` 체인(부모에 있으면 존재), 대소문자 무시를 모두 거친다. `TemplateHandler::compile()`은 자체 정의가 사라졌지만 `Rhymix\Framework\Template`에서 상속되므로 삭제가 아니다.
- 심볼 키는 소문자다. 2.0의 `boardView`와 현재의 `BoardView`는 같은 심볼이다.

## 재생성 절차

스크립트와 대체 API 맵은 orphan 브랜치 `tools`에 있다. `main`에는 문서(Markdown·텍스트)만 두며 `check`가 그 밖의 파일을 실패로 처리한다. `tools`는 `main`에 병합하지 않는다.

```bash
# 0. tools 브랜치를 옆 디렉토리에 worktree로 꺼낸다 (한 번만)
git worktree add ../rx-docs-tools tools

# 1. Rhymix 체크아웃에 스냅숏 태그를 받는다 (depth 1이면 충분)
git -C /path/to/rhymix fetch --depth=1 origin \
  refs/tags/1.8.0:refs/tags/1.8.0 refs/tags/1.9.0:refs/tags/1.9.0 refs/tags/1.9.13:refs/tags/1.9.13 \
  refs/tags/2.0.0:refs/tags/2.0.0 refs/tags/2.0.24:refs/tags/2.0.24 refs/tags/2.1.0:refs/tags/2.1.0

# 2. 생성 (문서 저장소 루트에서. --docs 기본값은 현재 디렉토리, --rhymix 기본값은 그 부모)
python3 ../rx-docs-tools/deprecated/generate.py generate --rhymix /path/to/rhymix

# 3. 검사: 본문 표시 누락, FQCN, 허용되지 않는 파일, 규칙 문장 일치, 링크, 생성 파일 최신 여부
python3 ../rx-docs-tools/deprecated/generate.py check --links --rhymix /path/to/rhymix
```

- 대체 API를 채우거나 고칠 때는 `tools` 브랜치의 `deprecated/overrides.json`을 편집하고 다시 생성한다. 키는 표의 심볼 표기와 같다.
- `python3 ../rx-docs-tools/deprecated/generate.py stale --rhymix ...`는 더 이상 존재하지 않는 심볼을 가리키는 맵 키를 보고한다.
- `check`는 `--rhymix` 없이도 동작한다(생성 파일 최신 여부만 건너뛴다). 본문 문서를 편집한 뒤 커밋 전에 한 번 돌린다.

## 한계

- 시점 판정은 태그 스냅숏 diff다. 태그 사이의 커밋은 보지 않으므로 릴리스 단위 정밀도다.
- 대소문자 무시로 매칭한다. 파일 이동이나 클래스 개명은 새 심볼로 보인다. `XmlParser` → `XeXmlParser`처럼 alias가 있으면 잡지만, alias 없는 개명은 유래가 늦게 나온다.
- `1.9.13`이 `2.0.0`보다 뒤라 날짜순으로 판정한다. 1.9.13에서만 표시된 항목은 백포트일 수 있어 비고에 남긴다.
- `추정:`은 deprecated 본문이 한 줄 위임일 때의 첫 호출이며 항상 옳지는 않다. `overrides.json`이 우선하고, `확인 필요`는 소스를 직접 읽어야 한다.
- 삭제 목록은 상속·alias를 해석하지만 `__call`/`__callStatic` 같은 동적 디스패치와 PHP 버전 가드 안의 조건부 `class_alias`는 잡지 못한다. 모듈 메서드는 `overrides.json`의 `removed.method_classes`에 적힌 클래스만 본다.
- 런타임 `E_USER_DEPRECATED`가 없으므로 이 문서와 docblock 외에 deprecated를 알 방법이 없다. 본체 갱신 시 반드시 재생성한다.
- `common/libraries/`·`common/vendor/`·`tests/`·`tools/`·`modules/editor/components/`는 스캔하지 않는다.
