"""Source identity and stale detection for derived text, without the AI or the app.

    python -m pytest tools/kpc_course/test_sources.py -q
"""
import copy
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import chapters as outline, comments, dsl, narration, sources  # noqa: E402


def _narrate():
    spec = importlib.util.spec_from_file_location("narrate", ROOT / "tools" / "narrate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# outline.build() is not repeatable (quiz options are shuffled with a seeded generator that
# keeps advancing), so the course is built once and shared, as the real build does.
_CHAPTERS = outline.build()
# The solutions as the build sees them: with their comments.
_SOLUTIONS = comments.apply(dsl.SOLUTIONS)


def _missions():
    return {a["id"]: a for c in _CHAPTERS for u in c["units"] for a in u["activities"]}


def test_body_blocks_are_paragraphs_and_fences_in_order():
    body = "첫 문단이에요.\n둘째 줄.\n\n```python\nprint(1)\n\nprint(2)\n```\n\n마지막 문단."
    assert sources.body_blocks(body) == ["첫 문단이에요.\n둘째 줄.", "```python\nprint(1)\n\nprint(2)\n```", "마지막 문단."]


def test_content_hash_ignores_reflow_but_not_words():
    assert sources.content_hash("가격을  먼저\n계산해요") == sources.content_hash("가격을 먼저 계산해요")
    assert sources.content_hash("가격을 먼저 계산해요") != sources.content_hash("가격을 나중에 계산해요")


def test_every_mission_has_numbered_keys_for_each_kind():
    seen = set()
    for activity in _missions().values():
        number = sources.mission_number(activity)
        assert number.count("-") == 2, number
        assert number not in seen, f"duplicate mission number {number}"
        seen.add(number)
        keys = [key for key, _ in sources.blocks(activity, "x = 1\n" if activity["kind"] == "coding" else None)]
        assert keys[0] == "title"
        if activity["kind"] == "concept":
            assert keys[-1] == "check" and any(k.startswith("p") for k in keys)
        elif activity["kind"] == "coding":
            assert keys[1:] == ["problem", "starter", "example", "solution"]
        elif activity["kind"] == "slides":
            assert keys[1].startswith("s") and len(keys) > 2
        else:
            assert keys[1].startswith("q")


def test_a_changed_paragraph_names_only_the_lines_written_for_it():
    concept = _missions()["numbers-text"]
    cached = narration.read_cache(concept["id"])
    assert narration.entry_for(concept, None)[1] == "fresh"
    changed = copy.deepcopy(concept)
    block = sources.body_blocks(changed["body"])[2]
    changed["body"] = changed["body"].replace(block, block + " 한 문장을 더 붙였어요.", 1)
    assert narration.entry_for(changed, None)[1] == "stale"
    keys, kept, why = narration.stale_report(changed, cached, None)
    assert keys == ["p3"]
    affected = [i for i in range(len(cached["entry"])) if i not in kept]
    assert affected == [i for i, line in enumerate(cached["sources"]) if line["block"] == "p3"]
    assert len(affected) >= 1 and len(kept) == len(cached["entry"]) - len(affected)
    assert "/p3 바뀜" in why and "그대로" in why


def test_a_changed_check_question_names_only_the_check_line():
    concept = _missions()["numbers-text"]
    cached = narration.read_cache(concept["id"])
    changed = copy.deepcopy(concept)
    changed["check"]["explanation"] += " 덧붙임."
    keys, kept, why = narration.stale_report(changed, cached, None)
    assert keys == ["check"]
    assert [cached["sources"][i]["block"] for i in range(len(cached["entry"])) if i not in kept] == ["check"]


def test_a_new_paragraph_keeps_every_existing_line():
    concept = _missions()["numbers-text"]
    cached = narration.read_cache(concept["id"])
    changed = copy.deepcopy(concept)
    changed["body"] += "\n\n새 문단이에요."
    keys, kept, why = narration.stale_report(changed, cached, None)
    assert len(keys) == 1 and keys[0].startswith("p") and "새 블록" in why
    assert kept == list(range(len(cached["entry"])))


def test_a_changed_solution_names_the_code_run_and_output_lines():
    coding = _missions()["variable-print"]
    cached = narration.read_cache(coding["id"])
    solution = _SOLUTIONS[coding["problem"]["id"]]
    keys, kept, why = narration.stale_report(coding, cached, solution + "\nprint(1)\n")
    assert keys == ["solution"]
    affected_steps = {cached["entry"][i][0] for i in range(len(cached["entry"])) if i not in kept}
    assert {"code", "run", "output", "submit"} <= affected_steps <= {"code", "try", "undo", "caution", "run", "output", "submit"}
    kept_steps = {cached["entry"][i][0] for i in kept}
    assert "problem" in kept_steps


def test_line_sources_follow_anchors_and_coding_steps():
    missions = _missions()
    concept = missions["numbers-text"]
    entry = narration.read_cache(concept["id"])["entry"]
    recorded = narration.line_sources(concept, entry, None)
    index = sources.index(concept)
    assert [line["block"] for line in recorded][0] == "title"
    assert [line["block"] for line in recorded][-1] == "check"
    assert all(index[line["block"]] == line["hash"] for line in recorded)
    coding = missions["variable-print"]
    solution = _SOLUTIONS[coding["problem"]["id"]]
    entry = narration.read_cache(coding["id"])["entry"]
    recorded = narration.line_sources(coding, entry, solution)
    assert {line["block"] for line in recorded} <= {"problem", "starter", "example", "solution"}


def test_restore_kept_puts_unchanged_lines_back_verbatim():
    narrate = _narrate()
    previous = [("title", "원래 제목 줄"), ("구절 하나", "원래 설명"), ("check", "원래 확인")]
    answered = [("title", "모델이 바꾼 제목 줄"), ("구절 하나", "모델이 다시 쓴 설명"), ("check", "모델이 바꾼 확인")]
    restored = narrate.restore_kept(answered, previous, kept=[0, 2])
    assert restored == [("title", "원래 제목 줄"), ("구절 하나", "모델이 다시 쓴 설명"), ("check", "원래 확인")]
    previous = [("code", "a = 1\n", "원래"), ("code", "print(a)\n", "원래 둘")]
    answered = [("code", "a = 1\n", "새"), ("code", "print(a)\n", "새 둘")]
    assert narrate.restore_kept(answered, previous, kept=[1]) == [("code", "a = 1\n", "새"), ("code", "print(a)\n", "원래 둘")]


def test_course_index_lists_every_block_with_hash_and_excerpt():
    index = sources.course_index(_CHAPTERS, _SOLUTIONS)
    assert len(index) == len(_missions())
    sample = next(iter(index.values()))
    assert {"key", "hash", "text"} <= set(sample["blocks"][0])
    assert all(len(block["hash"]) == 12 for mission in index.values() for block in mission["blocks"])


def test_narration_prompts_embed_the_shared_voice_guide():
    narrate = _narrate()
    guide = (ROOT / "docs" / "voice.md").read_text(encoding="utf-8")
    concept = _missions()["numbers-text"]
    assert guide in narrate.concept_prompt(concept)
    coding = _missions()["variable-print"]
    solution = _SOLUTIONS[coding["problem"]["id"]]
    assert guide in narrate.coding_prompt(coding, solution, "30000", "")
