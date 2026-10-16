"""Format the course's Python the same way everywhere: spaces around operators and after
commas, as PEP 8 writes them (`sum(prices) / len(prices)`, `x = 1`, `a >= 3`).

    python tools/format-kpc-code.py            # rewrite tools/kpc_course/*.py in place
    python tools/format-kpc-code.py --check    # report what would change, write nothing

What it touches, inside the authoring modules (dsl.py, d*_p*.py, challenges.py, decks*.py):
- `starter=`, `solution=` and `check=` strings of coding problems, and the module-level
  UPPERCASE code constants they are built from (TI, SPLIT, PREP, ...): formatted as whole
  programs with ruff (line length 400, quotes preserved).
- ```python fences inside prose (concept bodies, goals, hints, slides): formatted the same way.
- Inline `code` spans in prose: formatted only when the result differs from the original by
  whitespace alone, so prose never changes meaning.

A literal is rewritten only when its text changes, and the new literal is checked to parse
back to exactly the new value. Solutions that change make their narration stale; run
`python tools/narrate.py` afterwards, then the build.
"""
import ast
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULES = [ROOT / "tools" / "kpc_course" / "dsl.py", ROOT / "tools" / "kpc_course" / "challenges.py"]
MODULES += sorted((ROOT / "tools" / "kpc_course").glob("d*_p*.py"))
MODULES += sorted((ROOT / "tools" / "kpc_course").glob("decks*.py"))
MODULES = list(dict.fromkeys(MODULES))
CODE_KEYWORDS = {"starter", "solution", "check"}
FENCE = re.compile(r"(```python\n)(.*?)(\n[ \t]*```)", re.S)
SPAN = re.compile(r"`([^`\n]+)`")
_cache = {}


def ruff(code):
    """ruff-formatted code, or None when ruff refuses it (a fragment, a template)."""
    if code in _cache:
        return _cache[code]
    out = None
    for launcher in (["ruff"], ["uvx", "ruff"]):
        try:
            result = subprocess.run(
                [*launcher, "format", "--line-length", "400", "--config", "format.quote-style='preserve'",
                 "--stdin-filename", "snippet.py", "-"],
                input=code, capture_output=True, text=True, encoding="utf-8", timeout=120,
            )
        except OSError:
            continue
        if result.returncode == 0:
            out = result.stdout
        break
    _cache[code] = out
    return out


def format_program(code):
    """Whole lines of code: keep leading/trailing newline layout, format the rest."""
    if not code.strip():
        return code
    body = code.rstrip("\n")
    out = ruff(body + "\n")
    if out is None:
        return code
    out = out.rstrip("\n")
    return out + ("\n" if code.endswith("\n") else "")


def format_span(code):
    """An inline span: only a call, an index or a literal (it has brackets) that also carries an
    operator or a comma, and only when the formatted form differs by whitespace alone. Names
    like `scikit-learn`, paths like `data/credit.csv`, selectors like `#prices li` and keyword
    arguments like `index=False` stay exactly as written."""
    if not re.search(r"[(\[{]", code) or not re.search(r"[=<>+*/%,]", code):
        return code
    if code.lstrip().startswith("#"):
        return code
    out = ruff(code + "\n")
    if out is None:
        return code
    out = out.rstrip("\n")
    if "\n" in out:
        return code
    if re.sub(r"\s+", "", out) != re.sub(r"\s+", "", code):
        return code
    return out


def format_prose(text):
    def fence(match):
        block = match.group(2)
        indent = min((len(l) - len(l.lstrip()) for l in block.splitlines() if l.strip()), default=0)
        formatted = format_program(textwrap.dedent(block) + "\n").rstrip("\n")
        return match.group(1) + textwrap.indent(formatted, " " * indent) + match.group(3)

    text = FENCE.sub(fence, text)
    # Inline spans outside fences.
    parts = re.split(r"(```.*?```)", text, flags=re.S)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            parts[i] = SPAN.sub(lambda m: "`" + format_span(m.group(1)) + "`", part)
    return "".join(parts)


def encode_like(segment, value):
    """A Python literal for `value` in the same style as `segment` (the original literal)."""
    prefix = re.match(r"^[rRbBuUfF]*", segment).group(0)
    rest = segment[len(prefix):]
    raw = "r" in prefix.lower()
    for quotes in ('"""', "'''", '"', "'"):
        if rest.startswith(quotes):
            break
    else:
        return None
    if raw:
        if "\\" in value and value != segment[len(prefix) + len(quotes):-len(quotes)]:
            pass
        body = value
        if quotes in body or body.endswith(quotes[0]):
            return None
        literal = prefix + quotes + body + quotes
    elif len(quotes) == 3:
        body = value.replace("\\", "\\\\").replace(quotes, "\\" + quotes)
        if body.endswith(quotes[0]):
            body = body[:-1] + "\\" + quotes[0]
        literal = prefix + quotes + body + quotes
    else:
        body = value.replace("\\", "\\\\").replace(quotes, "\\" + quotes).replace("\n", "\\n").replace("\t", "\\t")
        literal = prefix + quotes + body + quotes
    try:
        if ast.literal_eval(literal) != value:
            return None
    except Exception:  # noqa: BLE001
        return None
    return literal


def code_nodes(tree):
    """Constant string nodes that are code: coding() keyword values and UPPERCASE constants."""
    code = set()

    def strings_in(expr):
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            yield expr
        elif isinstance(expr, ast.BinOp):
            yield from strings_in(expr.left)
            yield from strings_in(expr.right)
        elif isinstance(expr, (ast.Tuple, ast.List)):
            for e in expr.elts:
                yield from strings_in(e)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg in CODE_KEYWORDS:
                    code.update(id(n) for n in strings_in(kw.value))
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name.isupper() and name not in ("MARP_FRONT", "FRONT", "PROMPTS", "ASKS", "CHALLENGES", "DECK_PLACEMENTS", "PLACEMENTS", "SOLUTIONS", "CODE_TOKEN"):
                code.update(id(n) for n in strings_in(node.value))
    return code


def rewrite(path, check_only):
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    code = code_nodes(tree)
    edits = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        value = node.value
        new = format_program(value) if id(node) in code else format_prose(value)
        if new == value:
            continue
        segment = ast.get_source_segment(src, node)
        if segment is None:
            continue
        literal = encode_like(segment, new)
        if literal is None:
            print(f"  ? {path.name}:{node.lineno}: 다시 쓸 수 없는 리터럴 (건너뜀)")
            continue
        edits.append((node.lineno, node.col_offset, node.end_lineno, node.end_col_offset, literal, value, new))
    if not edits:
        return 0
    lines = src.split("\n")
    # Line/column → absolute offsets, applied from the end so earlier offsets stay valid.
    starts = []
    pos = 0
    for line in lines:
        starts.append(pos)
        pos += len(line) + 1
    out = src
    for lineno, col, end_lineno, end_col, literal, value, new in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        a = starts[lineno - 1] + len(lines[lineno - 1][:col].encode("utf-8").decode("utf-8", "ignore"))
        # ast columns are UTF-8 byte offsets: convert.
        a = starts[lineno - 1] + len(lines[lineno - 1].encode("utf-8")[:col].decode("utf-8"))
        b = starts[end_lineno - 1] + len(lines[end_lineno - 1].encode("utf-8")[:end_col].decode("utf-8"))
        out = out[:a] + literal + out[b:]
    ast.parse(out)  # the rewritten module must still parse
    if check_only:
        for lineno, *_rest, value, new in sorted(edits, key=lambda e: e[0])[:6]:
            before = next((l for l in value.splitlines() if l.strip()), "")[:80]
            after = next((l for l in new.splitlines() if l.strip()), "")[:80]
            if before != after:
                print(f"    {path.name}:{lineno}: {before!r} → {after!r}")
    else:
        path.write_text(out, encoding="utf-8")
    return len(edits)


def main():
    check_only = "--check" in sys.argv
    total = 0
    for path in MODULES:
        n = rewrite(path, check_only)
        if n:
            print(f"{'would change' if check_only else 'changed'} {n:3} literal(s) in {path.name}")
            total += n
    print(f"{total} literal(s) {'to change' if check_only else 'changed'}")


if __name__ == "__main__":
    main()
