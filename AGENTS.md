## Agent skills

### Issue tracker

Before creating or reading issues and specs, read `docs/agents/issue-tracker.md`. Work is tracked in local Markdown files under `.scratch/`.

### Triage labels

Before triaging an issue, read `docs/agents/triage-labels.md` for the default role labels.

### Domain docs

Before exploring the codebase, read `docs/agents/domain.md` for the single-context layout and domain documentation rules.

### 콘텐츠 룰

수업 내용(해설, 정답 코드, 주석)을 만들거나 고치기 전에 `docs/content-rules.md`를 읽는다. 코딩 해설은 살짝 코딩→실행을 반복하고 「조심하세요」 순간이 있어야 하며, 정답 코드에는 주석이 풍부해야 한다. 빌드가 강제한다.

### 목소리

학생에게 가는 글이나 LLM 프롬프트를 쓰기 전에 `docs/voice.md`를 읽는다. 말투·용어 규칙은 그 파일에만 있고, `tools/narrate.py`와 `src/assistant.rs`가 그 파일을 통째로 프롬프트에 넣는다. 새 LLM 호출을 만들면 같은 파일을 넣는다.

### 해설 모드 스크립트

개념 본문, 코딩 문제의 정답, 퀴즈 해설, 덱의 강사 스크립트를 바꾸기 전에 `docs/agents/narration.md`를 읽는다. 내용을 바꾸면 같은 커밋에서 `python tools/narrate.py`로 그 미션의 해설을 다시 만들고(바뀐 미션만 다시 쓴다) `python tools/build-kpc-course.py`로 확인한다.
