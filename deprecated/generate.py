#!/usr/bin/env python3
"""
rx-docs: Rhymix deprecated / removed API index generator and checker.

Reads tagged snapshots of a Rhymix checkout (without touching the working
tree) and writes the tables under 36-deprecated/.  Also checks the body docs
for unmarked references to deprecated symbols.

Python 3 standard library only.

This file lives on the `tools` branch of zodkr/rx-docs, which is never merged
into `main`: `main` holds only the documentation (Markdown and text), and
`check` enforces that.

Usage (run from the docs checkout, with the tools branch in a sibling worktree):
  git worktree add ../rx-docs-tools tools
  python3 ../rx-docs-tools/deprecated/generate.py generate --rhymix /path/to/rhymix [--dry-run]
  python3 ../rx-docs-tools/deprecated/generate.py check [--rhymix /path/to/rhymix] [--links]
  python3 ../rx-docs-tools/deprecated/generate.py stale --rhymix /path/to/rhymix
--docs defaults to the current directory; --rhymix defaults to its parent.
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = "36-deprecated"
OVERRIDES = os.path.join(HERE, "overrides.json")
# The docs branch may contain nothing but these.
DOCS_ALLOWED_EXT = (".md", ".txt")
DOCS_ALLOWED_NAMES = (".gitignore", "LICENSE")

DEFAULT_TAGS = ["1.8.0", "1.9.0", "1.9.13", "2.0.0", "2.0.24", "2.1.0"]
REMOVED_BASELINES = ["1.8.0", "2.0.24"]

# Paths never scanned (third-party code, runtime data, tests, bundled editors).
EXCLUDE_PREFIXES = (
    "common/vendor/", "vendor/", "libs/", "common/libraries/", "tests/",
    "tools/", "files/", "node_modules/", "common/js/plugins/", "common/tpl/",
    "modules/editor/components/", "modules/editor/skins/",
)
JS_PATH_RE = re.compile(r"^common/js/[^/]+\.js$")

ERA_ORDER = ["XE", "1.x", "2.0", "2.1"]
ERA_FILE = {
    "XE": "xe.md",
    "1.x": "rhymix-1.x.md",
    "2.0": "rhymix-2.0.md",
    "2.1": "rhymix-2.1.md",
}
ERA_TITLE = {
    "XE": "XE 1.8.0에서 이미 deprecated 처리된 API",
    "1.x": "Rhymix 1.x(1.9.x)에서 deprecated 처리된 API",
    "2.0": "Rhymix 2.0.x에서 deprecated 처리된 API",
    "2.1": "Rhymix 2.1.x에서 deprecated 처리된 API",
}
GENERATED_HEADER = (
    "<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. "
    "대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->"
)

# Names whose bare (global) form is a deprecated wrapper of a framework class.
COLLIDING_CLASSES = ["Security", "Password", "IpFilter", "Purifier", "EmbedFilter"]

MAGIC = {"__construct", "__destruct", "__get", "__set", "__call", "__callstatic",
         "__isset", "__unset", "__tostring", "__invoke", "__clone", "__wakeup",
         "__sleep", "__set_state", "__debuginfo", "__serialize", "__unserialize"}

# PHP builtins / keywords that are never a "replacement".
NOISE_CALLS = set("""
if foreach for while switch return array isset empty list function count unset
echo print exit die catch elseif new sprintf implode explode is_array is_object
in_array trim strlen substr str_replace preg_match preg_replace intval strval
is_string defined define include require require_once include_once compact
extract array_merge array_keys array_shift func_get_args func_num_args
call_user_func call_user_func_array strpos strtolower strtoupper is_null
is_bool is_int is_numeric json_encode json_decode htmlspecialchars ltrim rtrim
file_exists is_dir is_file basename dirname microtime time date max min abs
round floor ceil md5 sha1 base64_encode base64_decode urlencode urldecode
rawurlencode iconv mb_strlen mb_substr preg_split array_map array_filter
array_values array_unique array_key_exists ini_get ini_set function_exists
class_exists method_exists property_exists get_class gettype settype
var_export serialize unserialize filter_var parse_url http_build_query header
headers_sent ob_start ob_get_clean error_log trigger_error is_readable
opcache_invalidate ksort get_object_vars extension_loaded
preg_replace_callback html_entity_decode str_starts_with str_contains
array_pop end reset current key next is_callable escape strtr join array_walk
utf8_check executeQuery executeQueryArray getController getModel getAdminModel
getAdminController getView jQuery
""".split())


# ---------------------------------------------------------------------------
# git helpers
# ---------------------------------------------------------------------------

def git(repo, *args, text=True):
    res = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if res.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {res.stderr.decode(errors='ignore').strip()}")
    return res.stdout.decode("utf-8", "ignore") if text else res.stdout


def commit_date(repo, ref):
    return int(git(repo, "log", "-1", "--format=%ct", ref).strip())


def load_snapshot(repo, ref):
    """Return {path: text} for every scanned .php/.js file at ref (in memory)."""
    paths = []
    for p in git(repo, "ls-tree", "-r", "--name-only", ref).split("\n"):
        if not p or p.startswith(EXCLUDE_PREFIXES):
            continue
        if p.endswith(".php") or (JS_PATH_RE.match(p) and not p.endswith(".min.js")):
            paths.append(p)
    batch = subprocess.run(
        ["git", "-C", repo, "cat-file", "--batch"],
        input=b"\n".join(f"{ref}:{p}".encode() for p in paths) + b"\n",
        capture_output=True,
    ).stdout
    files = {}
    i = 0
    for p in paths:
        j = batch.index(b"\n", i)
        hdr = batch[i:j].split()
        if len(hdr) < 3 or hdr[1] != b"blob":
            i = j + 1
            continue
        size = int(hdr[2])
        files[p] = batch[j + 1:j + 1 + size].decode("utf-8", "ignore")
        i = j + 1 + size + 1
    return files


# ---------------------------------------------------------------------------
# PHP / JS parsing
# ---------------------------------------------------------------------------

NS_RE = re.compile(r"^\s*namespace\s+([\w\\]+)\s*;")
USE_RE = re.compile(r"^\s*use\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;")
CLASS_RE = re.compile(
    r"^\s*(?:(?:abstract|final|readonly)\s+)*(class|interface|trait)\s+(\w+)"
    r"(?:\s+extends\s+([\w\\]+))?")
FUNC_RE = re.compile(
    r"^\s*((?:(?:abstract|final|public|protected|private|static)\s+)*)function\s+&?(\w+)\s*\(")
ALIAS_RE = re.compile(r"class_alias\(\s*(?:'([\w\\]+)'|\"([\w\\]+)\"|([\w\\]+)::class)\s*,\s*['\"]([\w\\]+)['\"]")
JSDEF_RE = re.compile(r"(?:^|\s)function\s+(\w+)\s*\(|^\s*(?:var\s+|window\.)?([\w$]+)\s*=\s*function|^\s*([\w$]+)\s*:\s*function")
CALL_RE = re.compile(r"((?:\\?[A-Za-z_][\w\\]*::)?(?:\$\w+->|self::\$\w+->|parent::)?[A-Za-z_]\w*)\s*\(")
DOC_USE_RE = re.compile(r"\buse\s+([\w\\$>:()\-]+)\s+instead", re.I)
DOC_SEE_RE = re.compile(r"@see\s+([\w\\$>:()\-]+)")


class Snapshot:
    def __init__(self, ref, files):
        self.ref = ref
        self.paths = set(files)
        self.classes = {}    # fqcn_lower -> dict(display, file, line, parent(raw), ns, uses)
        self.methods = {}    # (fqcn_lower, name_lower) -> dict(display, file, line, vis)
        self.funcs = {}      # name_lower -> dict(display, file, line)
        self.aliases = {}    # alias_lower -> target_lower (fqcn)
        self.deprecated = {} # key -> dict(file, line, note, hint, doc_replace, display, kind)
        self.js_funcs = {}   # name -> (file, line)
        self.php_text = []
        for path, text in files.items():
            if path.endswith(".js"):
                self._parse_js(path, text)
            else:
                self._parse_php(path, text)
                self.php_text.append(text)

    # -- PHP -------------------------------------------------------------
    def _parse_php(self, path, text):
        lines = text.split("\n")
        ns = ""
        uses = {}
        cur = None          # fqcn_lower of the class being parsed
        cur_display = None
        for i, line in enumerate(lines):
            m = NS_RE.match(line)
            if m:
                ns = m.group(1).strip("\\")
                continue
            m = USE_RE.match(line)
            if m and cur is None:
                full = m.group(1).strip("\\")
                alias = (m.group(2) or full.split("\\")[-1]).lower()
                uses[alias] = full.lower()
                continue
            for m in ALIAS_RE.finditer(line):
                target = (m.group(1) or m.group(2) or m.group(3)).strip("\\").lower()
                alias = m.group(4).strip("\\").lower()
                self.aliases[alias] = target
            m = CLASS_RE.match(line)
            if m:
                name = m.group(2)
                fqcn = (ns + "\\" + name if ns else name)
                cur = fqcn.lower()
                cur_display = fqcn
                self.classes[cur] = {"display": fqcn, "file": path, "line": i + 1,
                                     "parent": m.group(3), "ns": ns.lower(), "uses": uses}
                continue
            m = FUNC_RE.match(line)
            if m:
                vis = "private" if "private" in m.group(1) else ("protected" if "protected" in m.group(1) else "public")
                name = m.group(2)
                if cur:
                    self.methods[(cur, name.lower())] = {"display": f"{cur_display}::{name}()", "file": path, "line": i + 1, "vis": vis}
                else:
                    self.funcs[name.lower()] = {"display": f"{name}()", "file": path, "line": i + 1}
        # deprecated docblocks
        cls_stack = []
        for i, line in enumerate(lines):
            m = CLASS_RE.match(line)
            if m:
                fq = (ns + "\\" + m.group(2) if ns else m.group(2))
                cls_stack = [(fq.lower(), fq)]
            if "@deprecated" not in line:
                continue
            note = line.split("@deprecated", 1)[1].strip(" */\t")
            doc = self._docblock_around(lines, i)
            doc_replace = None
            mm = DOC_USE_RE.search(doc)   # "@see" is a cross reference, not a replacement
            if mm:
                doc_replace = mm.group(1).rstrip(".")
            key = None
            display = None
            kind = None
            sig = None
            for j in range(i + 1, min(i + 16, len(lines))):
                mc = CLASS_RE.match(lines[j])
                mf = FUNC_RE.match(lines[j])
                if mc:
                    fq = (ns + "\\" + mc.group(2) if ns else mc.group(2))
                    key, display, kind = "class:" + fq.lower(), "class " + fq, "class"
                    break
                if mf:
                    owner = cls_stack[0] if cls_stack else None
                    if owner:
                        key = f"method:{owner[0]}::{mf.group(2).lower()}"
                        display = f"{owner[1]}::{mf.group(2)}()"
                        kind = "method"
                    else:
                        key = "func:" + mf.group(2).lower()
                        display = mf.group(2) + "()"
                        kind = "func"
                    sig = j
                    break
            if key is None:
                if i < 15:
                    key, display, kind = "file:" + path, "file " + path, "file"
                else:
                    continue  # stray inline comment; not a declaration
            hint = self._delegation_hint(lines, sig) if sig is not None else None
            self.deprecated[key] = {"file": path, "line": i + 1, "note": note, "hint": hint,
                                    "doc_replace": doc_replace, "display": display, "kind": kind}

    @staticmethod
    def _docblock_around(lines, i):
        start = i
        while start > 0 and "/**" not in lines[start] and i - start < 30:
            start -= 1
        end = i
        while end < len(lines) - 1 and "*/" not in lines[end] and end - i < 30:
            end += 1
        return " ".join(lines[start:end + 1])

    @staticmethod
    def _delegation_hint(lines, sig):
        """First non-trivial call in the body.  Returns (name, is_thin_wrapper)."""
        depth = 0
        started = False
        body = []
        first = None
        for j in range(sig, min(sig + 40, len(lines))):
            s = lines[j]
            if j > sig:
                stripped = s.strip()
                if stripped and stripped not in ("{", "}"):
                    body.append(stripped)
                if first is None:
                    for m in CALL_RE.finditer(s):
                        name = m.group(1)
                        base = name.split("::")[-1].split("->")[-1]
                        if base in NOISE_CALLS:
                            continue
                        first = (name, stripped.startswith("return"))
                        break
            depth += s.count("{") - s.count("}")
            if "{" in s:
                started = True
            if started and depth <= 0:
                break
        if first is None:
            return None
        return (first[0], first[1] and len(body) <= 2)

    # -- JS --------------------------------------------------------------
    def _parse_js(self, path, text):
        lines = text.split("\n")
        for i, line in enumerate(lines):
            m = JSDEF_RE.search(line)
            if m:
                name = m.group(1) or m.group(2) or m.group(3)
                self.js_funcs.setdefault(name, (path, i + 1))
            if "@deprecated" in line:
                note = line.split("@deprecated", 1)[1].strip(" */\t")
                for j in range(i + 1, min(i + 8, len(lines))):
                    m2 = JSDEF_RE.search(lines[j])
                    if m2:
                        name = m2.group(1) or m2.group(2) or m2.group(3)
                        self.deprecated["js:" + name] = {"file": path, "line": i + 1, "note": note, "hint": None,
                                                         "doc_replace": None, "display": name + "()", "kind": "js"}
                        break

    # -- resolution ------------------------------------------------------
    def resolve_class(self, name_lower, depth=0):
        """Return the fqcn_lower this name resolves to at this snapshot, or None."""
        if depth > 5:
            return None
        if name_lower in self.classes:
            return name_lower
        if name_lower in self.aliases:
            return self.resolve_class(self.aliases[name_lower], depth + 1)
        return None

    def resolve_parent(self, fqcn_lower):
        info = self.classes.get(fqcn_lower)
        if not info or not info["parent"]:
            return None
        raw = info["parent"]
        if raw.startswith("\\"):
            cand = [raw.strip("\\").lower()]
        else:
            low = raw.lower()
            first = low.split("\\")[0]
            cand = []
            if first in info["uses"]:
                cand.append(info["uses"][first] + low[len(first):])
            if info["ns"]:
                cand.append(info["ns"] + "\\" + low)
            cand.append(low)
        for c in cand:
            r = self.resolve_class(c)
            if r:
                return r
        return None

    def has_method(self, fqcn_lower, name_lower):
        seen = set()
        cur = self.resolve_class(fqcn_lower)
        while cur and cur not in seen:
            seen.add(cur)
            if (cur, name_lower) in self.methods:
                return True
            cur = self.resolve_parent(cur)
        return False

    def exists(self, key):
        kind, _, rest = key.partition(":")
        if kind == "class":
            return self.resolve_class(rest) is not None
        if kind == "method":
            cls, _, name = rest.rpartition("::")
            return self.has_method(cls, name)
        if kind == "func":
            return rest in self.funcs
        if kind == "file":
            return rest in self.paths
        if kind == "js":
            return rest in self.js_funcs
        return False


# ---------------------------------------------------------------------------
# overrides
# ---------------------------------------------------------------------------

def norm_key(display):
    s = display.strip().replace("()", "")
    s = re.sub(r"\s+", " ", s).strip().lstrip("\\")
    return s.lower()


def load_overrides():
    if not os.path.exists(OVERRIDES):
        return {"replacements": {}, "removed": {}}
    with open(OVERRIDES, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("replacements", {})
    data.setdefault("removed", {})
    data["_norm"] = {norm_key(k): v for k, v in data["replacements"].items()}
    return data


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------

def era_of(ref):
    if ref == "1.8.0":
        return "XE"
    if ref.startswith("1."):
        return "1.x"
    if ref.startswith("2.0"):
        return "2.0"
    return "2.1"


def md_cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def code(s):
    return f"`{s}`" if s else ""


def section_of(path):
    parts = path.split("/")
    if parts[0] in ("modules", "addons", "widgets", "widgetstyles", "layouts") and len(parts) > 2:
        return f"{parts[0]}/{parts[1]}/"
    if parts[0] == "common" and len(parts) > 2:
        return f"common/{parts[1]}/"
    if parts[0] == "common":
        return path
    return parts[0] + "/"


def replacement_for(key, dep, overrides):
    """Return (replacement_text, note_from_override)."""
    ov = overrides["_norm"].get(norm_key(dep["display"]))
    if ov:
        if isinstance(ov, str):
            return ov, ""
        return ov.get("replace", "확인 필요"), ov.get("note", "")
    if dep.get("doc_replace"):
        return dep["doc_replace"], ""
    hint = dep.get("hint")
    if hint:
        name, thin = hint
        low = name.lower()
        # Only a thin wrapper (single return statement) is evidence of a replacement.
        if thin and low.startswith(("rhymix\\", "\\rhymix\\")):
            return f"추정: {name.lstrip(chr(92))}()", ""
        if thin and low.startswith(("self::", "static::", "$this->", "parent::")):
            return f"추정: {name}()", ""
    return "확인 필요", ""


def core_call_count(head, key, dep):
    kind = dep["kind"]
    if kind == "method":
        name = key.rpartition("::")[2]
        pat = re.compile(r"(?:->|::)\s*" + re.escape(name) + r"\s*\(", re.I)
    elif kind == "func":
        name = key.partition(":")[2]
        pat = re.compile(r"(?<![\w>:$\\])" + re.escape(name) + r"\s*\(", re.I)
    else:
        return None
    n = 0
    for text in head.php_text:
        n += len(pat.findall(text))
    if kind == "func":
        n = max(0, n - 1)
    return n


def build(repo, tags):
    refs = list(tags) + ["HEAD"]
    dated = sorted(refs, key=lambda r: (commit_date(repo, r), r != "HEAD"))
    snaps = {}
    for r in dated:
        snaps[r] = Snapshot(r, load_snapshot(repo, r))
    head = snaps["HEAD"]
    return dated, snaps, head


def classify(dated, snaps, head, overrides):
    rows = []
    for key, dep in head.deprecated.items():
        when_ref = next(r for r in dated if key in snaps[r].deprecated)
        origin_ref = next((r for r in dated if snaps[r].exists(key)), "HEAD")
        when = era_of(when_ref)
        origin = era_of(origin_ref)
        repl, ov_note = replacement_for(key, dep, overrides)
        notes = []
        if dep["note"]:
            notes.append(dep["note"])
        if ov_note:
            notes.append(ov_note)
        if when_ref == "1.9.13" and key not in snaps.get("2.0.0", head).deprecated:
            notes.append("1.9.13에서 표시(2.0.x 백포트 가능)")
        elif when_ref not in ("HEAD", "1.8.0"):
            notes.append(f"{when_ref}에서 표시")
        calls = core_call_count(head, key, dep)
        if calls:
            notes.append("코어 호출 있음")
        if dep["kind"] == "class" and dep["display"].split(" ", 1)[1] in COLLIDING_CLASSES:
            notes.append("동명 `Rhymix\\Framework` 클래스와 이름 충돌")
        rows.append({"key": key, "display": dep["display"], "kind": dep["kind"], "file": dep["file"],
                     "line": dep["line"], "when": when, "origin": origin, "replace": repl,
                     "note": "; ".join(notes)})
    return rows


def removed_candidates(dated, snaps, head, overrides):
    conf = overrides.get("removed", {})
    excl_paths = tuple(conf.get("exclude_paths", []))
    excl_re = re.compile(conf.get("exclude_names_regex", "$^"), re.I)
    include = {norm_key(k) for k in conf.get("include", [])}
    exclude = {norm_key(k) for k in conf.get("exclude", [])}
    method_classes = {c.lower() for c in conf.get("method_classes", [])}
    exclude_methods = {m.lower() for m in conf.get("exclude_methods", [])}
    order = {r: i for i, r in enumerate(dated)}
    out = {}
    for base in REMOVED_BASELINES:
        if base not in snaps:
            continue
        s = snaps[base]
        cands = []
        for fq, info in s.classes.items():
            name = fq.split("\\")[-1]
            if info["file"].startswith(excl_paths) or excl_re.match(name):
                continue
            cands.append(("class:" + fq, "class " + info["display"], info))
        for name, info in s.funcs.items():
            if info["file"].startswith(excl_paths) or excl_re.match(name) or name.startswith("_"):
                continue
            cands.append(("func:" + name, info["display"], info))
        for (fq, name), info in s.methods.items():
            if info["vis"] == "private" or name.startswith("_") or name in MAGIC or name in exclude_methods:
                continue
            if info["file"].startswith(excl_paths):
                continue
            short = fq.split("\\")[-1]
            if name == short.lower():
                continue  # PHP4-style constructor
            in_framework = info["file"].startswith("common/framework/")
            if method_classes and not in_framework and short not in method_classes and fq not in method_classes:
                continue
            if head.resolve_class(fq) is None:
                continue  # whole class gone: listed as a class, not per method
            cands.append((f"method:{fq}::{name}", info["display"], info))
        for key, display, info in cands:
            nk = norm_key(display)
            if nk in exclude:
                continue
            if head.exists(key) and nk not in include:
                continue
            # last snapshot (date order) where it exists
            last = None
            for r in dated:
                if r == "HEAD":
                    continue
                if snaps[r].exists(key):
                    last = r
            if last is None:
                continue
            after = dated[order[last] + 1] if order[last] + 1 < len(dated) else "HEAD"
            removed_in = era_of(after)
            if key in out and order[out[key]["last_ref"]] >= order[last]:
                continue
            # Report the symbol as it was at the last snapshot where it existed
            # (baseline line numbers are stale by then), and apply the path
            # exclusions to that location as well.
            ls = snaps[last]
            kind, _, rest = key.partition(":")
            linfo = None
            if kind == "class":
                # Keep the removed name itself (it may have been a class_alias
                # of a class that still exists, e.g. Object -> BaseObject).
                r = ls.resolve_class(rest)
                linfo = ls.classes.get(r) if r else None
            elif kind == "func":
                linfo = ls.funcs.get(rest)
            else:
                cls, _, mname = rest.rpartition("::")
                r = ls.resolve_class(cls)
                linfo = ls.methods.get((r, mname)) if r else None
            if linfo:
                if kind != "class":
                    display = linfo["display"]
                if linfo["file"].startswith(excl_paths):
                    continue
            else:
                linfo = info
            loc = linfo["file"] + ":" + str(linfo["line"])
            ov = overrides["_norm"].get(nk)
            repl = (ov.get("replace") if isinstance(ov, dict) else ov) if ov else "확인 필요"
            note = (ov.get("note", "") if isinstance(ov, dict) else "")
            out[key] = {"display": display, "last_ref": last, "last_loc": loc, "removed_in": removed_in,
                        "replace": repl, "note": note, "kind": key.partition(":")[0]}
    return out


def header_lines(title, head_info, count):
    return [
        GENERATED_HEADER,
        f"# {title}",
        "",
        f"검증 기준: Rhymix {head_info['version']}, 커밋 `{head_info['sha']}`, {head_info['date']}. "
        "규칙과 열 설명은 [README.md](README.md). 항목 수: " + str(count) + ".",
        "",
    ]


def render_era_file(era, rows, head_info):
    rows = sorted(rows, key=lambda r: (r["file"], r["line"]))
    lines = header_lines(ERA_TITLE[era], head_info, len(rows))
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault(section_of(r["file"]), []).append(r)
    for sec, items in groups.items():
        lines.append(f"## {sec}")
        lines.append("")
        lines.append("| 심볼 | 위치 | 유래 | 대체 API | 비고 |")
        lines.append("|---|---|---|---|---|")
        for r in items:
            repl = r["replace"]
            repl_cell = code(repl) if repl not in ("확인 필요", "없음") and not repl.startswith("추정: ") else repl
            if repl.startswith("추정: "):
                repl_cell = "추정: " + code(repl[4:])
            lines.append("| {} | {} | {} | {} | {} |".format(
                code(md_cell(r["display"])), code(f"{r['file']}:{r['line']}"), r["origin"],
                md_cell(repl_cell), md_cell(r["note"])))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def render_js_file(rows, head_info):
    rows = sorted(rows, key=lambda r: (r["file"], r["line"]))
    lines = header_lines("JavaScript(common/js)에서 deprecated 처리된 함수", head_info, len(rows))
    lines.append("| 심볼 | 위치 | 시점 | 유래 | 대체 API | 비고 |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        repl = r["replace"]
        repl_cell = code(repl) if repl not in ("확인 필요", "없음") else repl
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            code(md_cell(r["display"])), code(f"{r['file']}:{r['line']}"), r["when"], r["origin"],
            md_cell(repl_cell), md_cell(r["note"])))
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def render_removed_file(removed, head_info):
    lines = header_lines("`@deprecated` 표시 없이 삭제된 공개 API", head_info, len(removed))
    lines.append("삭제된 API는 호출 즉시 fatal error가 난다. 발견 즉시 대체 API로 바꾼다. "
                 "마지막 존재 열은 `태그 경로:줄`이며, 제거 시점은 그 다음 릴리스 태그 기준이다.")
    lines.append("")
    by_era = collections.OrderedDict()
    for key, r in sorted(removed.items(), key=lambda kv: (ERA_ORDER.index(kv[1]["removed_in"]), kv[1]["kind"] != "class", kv[1]["last_loc"])):
        by_era.setdefault(r["removed_in"], []).append(r)
    for era, items in by_era.items():
        lines.append(f"## Rhymix {era}에서 삭제됨" if era != "XE" else "## XE 시절에 삭제됨")
        lines.append("")
        lines.append("| 심볼 | 마지막 존재 | 대체 API | 비고 |")
        lines.append("|---|---|---|---|")
        for r in items:
            repl = r["replace"]
            repl_cell = code(repl) if repl not in ("확인 필요", "없음") else repl
            lines.append("| {} | {} | {} | {} |".format(
                code(md_cell(r["display"])), code(f"{r['last_ref']} {r['last_loc']}"),
                md_cell(repl_cell), md_cell(r["note"])))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def head_info_of(repo, head):
    ver = "?"
    text = git(repo, "show", "HEAD:common/constants.php")
    m = re.search(r"define\('RX_VERSION',\s*'([^']+)'\)", text)
    if m:
        ver = m.group(1)
    sha = git(repo, "rev-parse", "--short=9", "HEAD").strip()
    date = git(repo, "log", "-1", "--format=%cs", "HEAD").strip()
    return {"version": ver, "sha": sha, "date": date}


def generate_outputs(repo, tags, overrides):
    dated, snaps, head = build(repo, tags)
    rows = classify(dated, snaps, head, overrides)
    removed = removed_candidates(dated, snaps, head, overrides)
    hi = head_info_of(repo, head)
    outputs = {}
    php_rows = [r for r in rows if r["kind"] != "js"]
    for era in ERA_ORDER:
        outputs[ERA_FILE[era]] = render_era_file(era, [r for r in php_rows if r["when"] == era], hi)
    outputs["javascript.md"] = render_js_file([r for r in rows if r["kind"] == "js"], hi)
    outputs["removed.md"] = render_removed_file(removed, hi)
    return outputs, rows, removed, snaps, dated


def cmd_generate(args):
    overrides = load_overrides()
    outputs, rows, removed, snaps, dated = generate_outputs(args.rhymix, args.tags, overrides)
    php = [r for r in rows if r["kind"] != "js"]
    print("snapshots (date order):", " -> ".join(dated))
    for era in ERA_ORDER:
        print(f"  {era:<4} PHP={sum(1 for r in php if r['when'] == era):3d}  JS={sum(1 for r in rows if r['kind'] == 'js' and r['when'] == era):3d}")
    print(f"  removed candidates: {len(removed)}")
    unknown = sorted(r["display"] for r in rows if r["replace"] == "확인 필요")
    print(f"  '확인 필요' entries: {len(unknown)}")
    if args.dry_run:
        for name, text in outputs.items():
            print(f"  would write {OUT_DIR}/{name} ({text.count(chr(10))} lines)")
        return 0
    os.makedirs(os.path.join(args.docs, OUT_DIR), exist_ok=True)
    for name, text in outputs.items():
        path = os.path.join(args.docs, OUT_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"  wrote {OUT_DIR}/{name} ({text.count(chr(10))} lines)")
    stale = stale_keys(overrides, rows, removed)
    if stale:
        print("  stale override keys:", ", ".join(stale))
    return 0


def stale_keys(overrides, rows, removed):
    known = {norm_key(r["display"]) for r in rows} | {norm_key(r["display"]) for r in removed.values()}
    return sorted(k for k in overrides["replacements"] if norm_key(k) not in known)


def cmd_stale(args):
    overrides = load_overrides()
    outputs, rows, removed, snaps, dated = generate_outputs(args.rhymix, args.tags, overrides)
    stale = stale_keys(overrides, rows, removed)
    print("\n".join(stale) if stale else "(no stale keys)")
    return 0


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

SYMBOL_CELL_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|")
ABOLISHED = ["대체:", "더 이상 사용하지 않음", "폐기", "권장하지 않음", "호환만", "사용 권장"]


def load_symbols_from_docs(docs):
    """Parse the generated tables and return (php_patterns, js_names)."""
    pats = []   # (label, compiled regex, kind)
    js = []
    folder = os.path.join(docs, OUT_DIR)
    if not os.path.isdir(folder):
        raise SystemExit(f"{OUT_DIR}/ not found; run generate first")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name == "README.md":
            continue
        is_js = name == "javascript.md"
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            for line in f:
                m = SYMBOL_CELL_RE.match(line)
                if not m:
                    continue
                sym = m.group(1).strip()
                if is_js:
                    js.append(sym.replace("()", ""))
                    continue
                if sym.startswith("class "):
                    cname = sym[6:].split("\\")[-1]
                    if cname in COLLIDING_CLASSES:
                        # The bare word is ambiguous with the framework class; `Name::` is
                        # caught by the FQCN rule, so only flag instantiation here.
                        pats.append((sym, re.compile(r"\bnew\s+" + re.escape(cname) + r"\s*\("), "class"))
                    else:
                        pats.append((sym, re.compile(r"(?<![\w\\\-/.])" + re.escape(cname) + r"(?![\w\-/.])"), "class"))
                elif sym.startswith("file "):
                    pats.append((sym, re.compile(re.escape(os.path.basename(sym[5:]))), "file"))
                elif "::" in sym:
                    cls, _, meth = sym.replace("()", "").rpartition("::")
                    cls_short = cls.split("\\")[-1]
                    pats.append((sym, re.compile(r"(?<![\w\\])" + re.escape(cls_short) + r"::" + re.escape(meth) + r"\b"), "method"))
                else:
                    fn = sym.replace("()", "")
                    pats.append((sym, re.compile(r"(?<![\w>:$\\.])" + re.escape(fn) + r"\s*\("), "func"))
    return pats, js


def iter_doc_files(docs):
    for root, dirs, files in os.walk(docs):
        rel_root = os.path.relpath(root, docs)
        if rel_root.startswith((".git", OUT_DIR)):
            continue
        for fn in sorted(files):
            if fn.endswith(".md") or fn == "llms.txt":
                rel = os.path.normpath(os.path.join(rel_root, fn))
                if rel == "PROMPT.md":
                    continue
                yield rel, os.path.join(root, fn)


def code_contexts(line, in_fence):
    """Return list of (text, is_code) segments to inspect."""
    if in_fence or line.lstrip().startswith("|"):
        return [(line, True)]
    segs = []
    for m in re.finditer(r"`([^`]+)`", line):
        segs.append((m.group(1), True))
    return segs


def cmd_check(args):
    docs = args.docs
    failures = []
    warnings = []
    pats, js_names = load_symbols_from_docs(docs)
    fqcn_re = re.compile(r"(?<![\w\\])(" + "|".join(COLLIDING_CLASSES) + r")::")
    js_res = [(n, re.compile(r"(?<![\w.$])" + re.escape(n) + r"\s*\(")) for n in js_names]
    for rel, path in iter_doc_files(docs):
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        in_fence = False
        fence_lang = ""
        for no, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                fence_lang = stripped[3:].strip().lower() if in_fence else ""
                continue
            exempt = ("@deprecated" in line) or ("removed" in line) or (OUT_DIR + "/" in line)
            if fqcn_re.search(line):
                failures.append(f"{rel}:{no}: 전역 래퍼 단축 표기 (FQCN 필요): {stripped[:100]}")
            if exempt:
                for phrase in ABOLISHED:
                    if phrase in line:
                        warnings.append(f"{rel}:{no}: 마커 줄에 폐지 표현 '{phrase}'")
                continue
            for text, _ in code_contexts(line, in_fence):
                for label, rx, kind in pats:
                    if rx.search(text):
                        failures.append(f"{rel}:{no}: deprecated 심볼 표시 없음: {label}")
                        break
                if in_fence and fence_lang in ("js", "javascript", "html"):
                    for name, rx in js_res:
                        if rx.search(text):
                            failures.append(f"{rel}:{no}: deprecated JS 함수 표시 없음: {name}()")
                            break
            if args.links:
                for m in re.finditer(r"\]\(([^)\s]+)\)", line):
                    target = m.group(1)
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    target = target.split("#", 1)[0]
                    if not target:
                        continue
                    dest = os.path.normpath(os.path.join(os.path.dirname(path), target))
                    if not os.path.exists(dest):
                        failures.append(f"{rel}:{no}: 깨진 링크 {m.group(1)}")
    # The docs tree may contain nothing but Markdown/text.
    for root, dirs, files in os.walk(docs):
        dirs[:] = [d for d in dirs if d != ".git"]
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, docs)
            if not (fn.endswith(DOCS_ALLOWED_EXT) or fn in DOCS_ALLOWED_NAMES):
                failures.append(f"{rel}: 문서 트리에 허용되지 않는 파일 (Markdown·텍스트만 허용)")
            elif os.stat(p).st_mode & 0o111:
                failures.append(f"{rel}: 실행 비트가 설정된 파일")
    # README rules must match llms.txt
    readme = os.path.join(docs, OUT_DIR, "README.md")
    llms = os.path.join(docs, "llms.txt")
    if os.path.exists(readme) and os.path.exists(llms):
        with open(readme, encoding="utf-8") as f:
            rtext = f.read()
        with open(llms, encoding="utf-8") as f:
            ltext = f.read()
        m = re.search(r"^## 규칙\n(.*?)(?=^## )", rtext, re.S | re.M)
        if m:
            for bullet in [b for b in m.group(1).split("\n") if b.startswith("- ")]:
                if bullet not in ltext:
                    failures.append(f"{OUT_DIR}/README.md 규칙 불릿이 llms.txt와 다름: {bullet[:80]}")
    # freshness against the Rhymix checkout
    if args.rhymix:
        overrides = load_overrides()
        outputs, _, _, _, _ = generate_outputs(args.rhymix, args.tags, overrides)
        for name, text in outputs.items():
            p = os.path.join(docs, OUT_DIR, name)
            cur = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
            if cur != text:
                failures.append(f"{OUT_DIR}/{name}: 재생성 필요 (생성 결과와 다름)")
    for w in warnings:
        print("WARN", w)
    for f in failures:
        print("FAIL", f)
    print(f"check: {len(failures)} failure(s), {len(warnings)} warning(s)")
    return 1 if failures else 0


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("generate", "check", "stale"):
        p = sub.add_parser(name)
        p.add_argument("--rhymix", default=None,
                       help="Rhymix checkout (default: parent of --docs; check skips the freshness test when omitted)")
        p.add_argument("--docs", default=os.getcwd(), help="docs checkout (default: current directory)")
        p.add_argument("--tags", default=",".join(DEFAULT_TAGS))
        if name == "generate":
            p.add_argument("--dry-run", action="store_true")
        if name == "check":
            p.add_argument("--links", action="store_true")
    args = ap.parse_args(argv)
    args.tags = [t for t in args.tags.split(",") if t]
    args.docs = os.path.abspath(args.docs)
    if args.rhymix is None and args.cmd != "check":
        args.rhymix = os.path.dirname(args.docs)
    if args.rhymix is not None:
        args.rhymix = os.path.abspath(args.rhymix)
    if args.cmd == "generate":
        return cmd_generate(args)
    if args.cmd == "check":
        return cmd_check(args)
    return cmd_stale(args)


if __name__ == "__main__":
    sys.exit(main())
