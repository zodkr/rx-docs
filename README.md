# rx-docs tools

[zodkr/rx-docs](https://github.com/zodkr/rx-docs)의 `36-deprecated/` 표를 생성·검사하는 도구. `main`은 문서(Markdown·텍스트)만 담고, 스크립트와 설정 맵은 이 orphan 브랜치에만 둔다. `main`에 병합하지 않는다.

```
deprecated/generate.py     # 생성기 + 검사기 (Python 3 표준 라이브러리만)
deprecated/overrides.json  # 수기 대체 API 맵, 삭제 목록 포함/제외 규칙
```

## 가져오기

```bash
# 문서 체크아웃 옆에 worktree로 (권장)
git -C docs worktree add ../rx-docs-tools tools

# 또는 별도 clone
git clone --branch tools --single-branch https://github.com/zodkr/rx-docs.git rx-docs-tools
```

## 사용

문서 저장소 루트에서 실행한다. `--docs` 기본값은 현재 디렉토리, `--rhymix` 기본값은 그 부모(docs가 본체 안에 있을 때)다.

```bash
# 1. Rhymix 체크아웃에 스냅숏 태그를 받는다 (depth 1이면 충분)
git -C /path/to/rhymix fetch --depth=1 origin \
  refs/tags/1.8.0:refs/tags/1.8.0 refs/tags/1.9.0:refs/tags/1.9.0 refs/tags/1.9.13:refs/tags/1.9.13 \
  refs/tags/2.0.0:refs/tags/2.0.0 refs/tags/2.0.24:refs/tags/2.0.24 refs/tags/2.1.0:refs/tags/2.1.0

# 2. 생성
python3 ../rx-docs-tools/deprecated/generate.py generate --rhymix /path/to/rhymix

# 3. 검사
python3 ../rx-docs-tools/deprecated/generate.py check --links --rhymix /path/to/rhymix

# 맵 정리
python3 ../rx-docs-tools/deprecated/generate.py stale --rhymix /path/to/rhymix
```

- `generate`: 릴리스 태그 스냅숏을 날짜순으로 대조해 `36-deprecated/*.md`를 다시 쓴다. `--dry-run`은 수치만 출력한다.
- `check`: 본문 문서의 deprecated 심볼 표시 누락, 전역 래퍼 단축 표기, 문서 트리에 허용되지 않는 파일(`.md`·`.txt`·`.gitignore`·`LICENSE` 외)과 실행 비트, `36-deprecated/README.md`와 `llms.txt`의 규칙 문장 일치, 상대 링크(`--links`), 생성 파일 최신 여부(`--rhymix` 지정 시)를 검사한다. 실패가 있으면 exit 1.
- `stale`: `overrides.json`에서 더 이상 존재하지 않는 심볼을 가리키는 키를 보고한다.
- 대체 API는 `deprecated/overrides.json`에서 고친다. 키는 표의 심볼 표기와 같다(대소문자 무시, 괄호 생략 가능).

판정 방법과 한계는 문서 저장소의 `36-deprecated/README.md`에 있다.
