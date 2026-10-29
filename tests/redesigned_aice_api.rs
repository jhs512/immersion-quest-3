// 2026-10-29: this lesson's answer-picking steps became coding steps (tools/coding_conversions/aice_python_api.py).
// The earlier per-step table pinned the reading steps' outputs; the converted steps are pinned and
// checked against wrong and other correct answers in tests/lesson-cases/aice-python-api.json, replayed here.
#[path="support/lesson_cases.rs"] mod lesson_cases;

#[tokio::test]
async fn aice_python_api_steps_match_their_validated_cases_and_grade_real_code() { lesson_cases::replay("aice-python-api").await }
