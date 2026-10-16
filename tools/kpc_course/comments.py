"""Rich `#` comments on every reference solution (a content rule: docs/content-rules.md).

The unit files keep the bare solution (the code the checks and the narration are written
against). The commented version is derived text, cached per problem in
tools/kpc_course/solution_comments/<problem id>.json with the hash of the bare code it was
written for (tools/annotate.py writes it with the Claude CLI). The build and tools/narrate.py
use the commented solution everywhere a student sees code: 정답 보기, the typed 해설 chunks,
courses/kpc-solutions.json. When the bare code changes, the cache is stale and the build refuses
until `python tools/annotate.py` rewrites the comments.

Comments never change what the code does: stripping them gives the bare solution back, line
for line (`strip_comments`), and the starter's own lines stay untouched (the app keeps them).
"""
import hashlib
import io
import json
import os
import pathlib
import tokenize

CACHE_DIR = pathlib.Path(__file__).parent / "solution_comments"


def strip_comments(code):
    """The code without `#` comments and without comment-only or blank lines: what must stay
    identical between the bare and the commented solution."""
    out = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, SyntaxError):
        return None
    drop = {(t.start[0], t.start[1]) for t in tokens if t.type == tokenize.COMMENT}
    for number, line in enumerate(code.split("\n"), start=1):
        cut = len(line)
        for row, col in drop:
            if row == number:
                cut = min(cut, col)
        kept = line[:cut].rstrip()
        if kept.strip():
            out.append(kept)
    return "\n".join(out) + "\n"


def code_hash(code):
    return hashlib.sha256(strip_comments(code).encode("utf-8")).hexdigest()[:16]


def cache_path(problem_id):
    return CACHE_DIR / f"{problem_id}.json"


def read(problem_id):
    path = cache_path(problem_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write(problem_id, bare, commented, by):
    CACHE_DIR.mkdir(exist_ok=True)
    data = {"hash": code_hash(bare), "by": by, "code": commented}
    cache_path(problem_id).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def check(bare, commented, starter_prefix=""):
    """Why a commented solution is not acceptable, or None."""
    if strip_comments(commented) is None:
        return "주석을 단 코드가 파이썬으로 읽히지 않습니다"
    if strip_comments(commented) != strip_comments(bare):
        return "주석을 빼면 원래 코드와 같아야 하는데 코드가 달라졌습니다"
    if starter_prefix and not commented.startswith(starter_prefix):
        return "준비 코드 부분은 글자 그대로 두어야 합니다 (그 아래부터 주석을 답니다)"
    comment_lines = sum(1 for line in commented.split("\n") if "#" in line)
    code_lines = sum(1 for line in strip_comments(bare).split("\n") if line.strip())
    if comment_lines < max(1, min(3, code_lines // 2)):
        return f"주석이 너무 적습니다 ({comment_lines}줄; 코드 {code_lines}줄)"
    try:
        compile(commented, "<solution>", "exec")
    except SyntaxError as error:
        return f"주석을 단 코드에 문법 오류: {error}"
    return None


def status(problem_id, bare):
    """fresh / stale / none for a problem's cached comments."""
    cached = read(problem_id)
    if cached is None:
        return "none"
    return "fresh" if cached["hash"] == code_hash(bare) else "stale"


def apply(solutions):
    """{problem id: commented solution} for every problem whose cache is fresh. Any missing or
    stale cache stops the build (KPC_LENIENT=1: that problem keeps its bare code)."""
    out = {}
    missing = []
    for problem_id, bare in solutions.items():
        state = status(problem_id, bare)
        if state == "fresh":
            out[problem_id] = read(problem_id)["code"]
        else:
            missing.append(f"{problem_id} ({state})")
            out[problem_id] = bare
    if missing and not os.environ.get("KPC_LENIENT"):
        raise SystemExit("정답 주석이 없거나 낡았습니다: " + ", ".join(missing) + "\npython tools/annotate.py 를 실행하세요 (바뀐 문제만 다시 답니다).")
    return out
