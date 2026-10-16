"""The fixed 7-chapter, 20-unit outline. Unit files are named by day and period."""
import importlib

from kpc_course.prompts import PROMPTS
from kpc_course.asks import ASKS
from kpc_course.challenges import CHALLENGES
from kpc_course.decks import DECK_PLACEMENTS
from kpc_course.table_quizzes import PLACEMENTS as TABLE_QUIZ_PLACEMENTS

OUTLINE = [
    ("python", "1. 파이썬 개발 환경과 기본 문법 이해", ["d1_p1_environment", "d1_p2_structures", "d1_p3_control"]),
    ("pandas", "2. 데이터 수집 기초 및 pandas 활용", ["d1_p4_files", "d1_p5_missing", "d1_p6_html"]),
    ("eda", "3. Titanic 데이터 탐색 및 기초 분석", ["d1_p7_titanic_structure", "d1_p8_titanic_groups"]),
    ("visualization", "4. Titanic 데이터 시각화 분석", ["d2_p1_bar_chart", "d2_p2_distribution", "d2_p3_insight"]),
    ("modeling", "5. Titanic 전처리 및 머신러닝 모델링", ["d2_p4_features", "d2_p5_preprocessing", "d2_p6_classifiers"]),
    ("credit", "6. 금융 데이터 분석 및 신용카드 부도 예측", ["d2_p7_credit_target", "d2_p8_credit_metrics"]),
    ("stock", "7. 주가 데이터 기반 회귀 분석 프로젝트", ["d3_p1_stock_data", "d3_p2_stock_features", "d3_p3_stock_split", "d3_p4_regression_project"]),
]


def build():
    chapters = []
    for chapter_id, title, modules in OUTLINE:
        units = [importlib.import_module(f"kpc_course.{name}").UNIT for name in modules]
        # The chapter ends with a ★ 도전 과제 that needs everything the chapter taught.
        units[-1]["activities"].append(CHALLENGES[chapter_id])
        # Instructor decks sit where the instructor presents them. A position counts the unit's
        # own activities (before any deck): the deck goes in front of that activity, so inserting
        # from the back keeps every position valid when a unit gets several decks.
        placements = [p for p in DECK_PLACEMENTS if p[0] == chapter_id]
        by_slot = {}
        for _, unit_index, position, deck in placements:
            by_slot.setdefault((unit_index, position), []).append(deck)
        for (unit_index, position), decks in sorted(by_slot.items(), key=lambda item: (item[0][0], -item[0][1])):
            for offset, deck in enumerate(decks):
                units[unit_index]["activities"].insert(position + offset, deck)
        # 표에서 고르기 quizzes go right after their unit's 단원 점검 (or at the end).
        for _, unit_id, table_quiz, after_id in [p for p in TABLE_QUIZ_PLACEMENTS if p[0] == chapter_id]:
            unit = next(u for u in units if u["id"] == unit_id)
            ids = [a["id"] for a in unit["activities"]]
            if after_id is not None and after_id not in ids:
                raise SystemExit(f"{unit_id}: 표 고르기 퀴즈를 붙일 미션 '{after_id}'이 없습니다.")
            after = ids.index(after_id) if after_id is not None else next((i for i, a in enumerate(unit["activities"]) if a["kind"] == "quiz" and a["title"] == "단원 점검"), len(ids) - 1)
            unit["activities"].insert(after + 1, table_quiz)
        seen = set()
        for _, _, _, deck in placements:
            if deck["id"] in seen:
                raise SystemExit(f"{chapter_id}: 덱 id '{deck['id']}'가 두 번 꽂혀 있습니다.")
            seen.add(deck["id"])
        for unit in units:
            for activity in unit["activities"]:
                # Every mission gets its three hand-written quick questions for the tutor panel:
                # from asks.py, or, for a deck, the ones written next to the deck itself.
                if activity["id"] in ASKS:
                    activity["ask"] = list(ASKS[activity["id"]])
                elif not (activity.get("ask") and activity.get("ask_is_default") is False):
                    raise SystemExit(f"{unit['id']}/{activity['id']}: tools/kpc_course/asks.py에 추천 질문이 없습니다.")
                if activity["kind"] == "coding":
                    problem = activity["problem"]
                    if problem["id"] not in PROMPTS:
                        raise SystemExit(f"{unit['id']}/{problem['id']}: tools/kpc_course/prompts.py에 인간 버전 프롬프트가 없습니다.")
                    problem["prompt"], problem["prompt_why"] = PROMPTS[problem["id"]]
        chapters.append(dict(id=chapter_id, title=title, units=units))
    # Numbering the student sees everywhere: chapter "1.", unit "1-1", mission "1-1-1".
    for c, chapter in enumerate(chapters, start=1):
        for u, unit in enumerate(chapter["units"], start=1):
            unit["title"] = f"{c}-{u} {unit['title']}"
            for a, activity in enumerate(unit["activities"], start=1):
                activity["title"] = f"{c}-{u}-{a} {activity['title']}"
    return chapters
