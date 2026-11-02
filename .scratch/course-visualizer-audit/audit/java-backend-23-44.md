# java-backend 수업 23–44 감사 (읽기 전용 검토)

Goal (restated): the owner wants every lesson re-reviewed for leveling quality, and wants 코드 흐름 보기 used in narrations only where it shows something the printed output cannot. This file covers java-backend manifest order 23–44 (22 lessons, 225 steps).

## 방법과 근거의 깊이

- **Java lessons 27–30** (java-regex, java-rq, java-calculator, java-crud; 43 steps). A Python harness (`%TEMP%/jb-audit/harness.py`, outside the repo) compiled the code with the local JDK 25. For every step it ran the starter and the solution against `tests[]`, ran the checker `QuestContract` on the solution, and replayed the narration (`patch_code`, `set_code`, `set_input`, `run`). The input defaults to `tests[0].input`, the same rule as `examples/replay_lesson_outputs.rs:36`. Every narration run output matched `tests/lesson-cases/<key>.json` `expected_outputs`. Every starter fails at least one test. Every solution passes all tests. Every `reject` case is refused. The narration's final code equals the solution, except a blank line in java-crud 2.1.5. I read the goal, the starter and every narration line of all 43 steps.
- **DB lessons 34–41** (6 SQL lessons, h2-memory-file, java-jdbc). I did not run them (MySQL, PostgreSQL and H2 are not available here). I paired each narration `run` with the recorded `expected_outputs` and with the `say` line that follows it, for all 46 steps, and checked that the claims match the recorded output.
- **Git/Docker/CI lessons 23–26, 31–33, 42**. A script compared the backticked commands in each 「할 일」 with the narration's `git_command`/`bash_command` sequence for all 83 steps, and I read every mismatch. Read in full: git-branch 1.1.1, git-branch-advanced 1.2.1, github-pr 1.2.2, docker-image-container 1.1.2/1.1.5/2.1.1, gitlab-ci 1.1.2/1.1.3. Everything else in these lessons got only the automated checks.
- **Frontend lessons 43–44** (java-tailwind, java-react; 46 steps). Automated lint on all steps. Read in full: java-tailwind 1.2.2, java-react 1.1.1, 3.1.3, 3.1.4 (part).
- Automated lint, run on all 225 steps: a 「할 일」 is present and its last item is 제출; an item that only restates the title; starter equals solution; caution count; narration sentences repeated in 3+ steps; narration that reads the goal text verbatim; unused and redundant Java imports (Java lessons and h2/jdbc).
- Every step has lesson and step objectives (inventory check).

Visualizer facts used: `Task::code_flow_availability` (src/repository_course.rs:169-182). Java is Ready on Windows, macOS and Linux. git-terminal steps (all Git/Docker-terminal lessons) are Hidden. Docker-language SQL steps show "SQL/터미널… 아직 지원하지 않아요". java_libraries (h2, jdbc) and web (tailwind, react) show an unsupported reason. In this range only the 43 Java steps are Ready, and they are Ready on all three OS. The Java tracer draws `java.util` Maps and Collections element by element and arrays as objects (assets/java-trace/jmv/Tracer.java:398-455). Lambdas and other JDK types are `OPAQUE`.

---

## 23. git-branch

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.1.14, 1.2.1 (15 steps) | 저장소 바깥의 안내 파일을 가져오세요 … 두 기능을 브랜치로 차례로 개발하세요 | ok (automated; 1.1.1 read) | IMPOSSIBLE (git terminal, Hidden) |

- The 「할 일」 commands match the narration commands in 1.1.1–1.1.13. 1.1.14 and the challenge 1.2.1 describe goals in words; the narration commands fit those goals.
- 1.1.12 and 1.1.13 have no 「조심하세요」. That is allowed.
- No defects found. Coverage is shallow, see the method section.

## 24. git-remote

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.1.9, 2.1.1–2.1.13, 2.2.1 (23 steps) | 팀의 공유 저장소를 직접 연결하세요 … 동료의 변경과 합쳐 내 운영 시간 커밋을 공유하세요 | ok (automated) | IMPOSSIBLE (git terminal) |

- The commands match. Steps 1.1.5, 1.1.8, 2.1.8 and 2.1.13 list commands in words (no backticks); their narration commands are `git remote -v`/`git branch`, `git show origin/main:guide.txt`/`git show HEAD:guide.txt`, and so on. These are consistent with the text.
- No defects found (automated only).

## 25. git-branch-advanced

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1, 1.1.2, 1.2.1, 1.2.2, 1.2.3, 1.3.1 | 두 브랜치의 변경을 main에 합치세요 … 두 의도를 살려 갈라진 안내를 병합하세요 | minor (1.2.1 read) | IMPOSSIBLE (git terminal) |

- minor: in 1.1.2, 1.2.1 and 1.3.1, the 「할 일」 commands are not in backticks ("1. git status로 충돌 파일을 확인하세요."). The other Git lessons use backticks. voice.md also shows commands as code.

## 26. github-pr (내용은 GitLab MR, revision `gitlab-mr-1`)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.1.5, 1.2.1–1.2.4 (9 steps) | GitLab에 비공개 프로젝트를 만드세요 … 새 프로젝트에서 변경 제안부터 병합까지 마치세요 | minor | IMPOSSIBLE (git terminal) |

- minor (systemic): all 9 steps read a goal sentence verbatim as a `say`. For example, 1.2.2 says "합치기 전에 무엇이 빠지고 들어가는지 읽으세요. 한 실습 계정으로 …" on `text:` with the same sentence. This breaks content-rules 「해설은 문제를 설명한다」 ("문제 전체를 소리 내어 다시 읽거나").
- info: the lesson key `github-pr` does not match its GitLab content. It is internal only, not shown to students.

## 27. java-regex

| 위치 | 제목 | 정합성 | 비주얼라이저 (Win/Mac/Linux Ready) |
|---|---|---|---|
| 1.1.1 | &로 이어진 조건을 나누어 개수를 돌려주세요 | minor (할 일) | NOT-APPLY (output 1→2 already shows the count) |
| 1.1.2 | 물음표 앞의 작업 이름을 돌려주세요 | minor (할 일) | NOT-APPLY |
| 1.1.3 | 값 안의 등호를 보존하도록 split의 두 번째 인수를 고치세요. | minor (title period, starter comment) | **APPLY** (medium) |
| 1.1.4 | 등호 뒤의 빈 값도 보존하고 길이를 돌려주세요 | minor (할 일) | **APPLY** (high) |
| 1.2.1 | 문자열 전체가 한 자리 이상 숫자인지 검사하세요 | minor (할 일) | NOT-APPLY |
| 1.2.2 | 전체 일치와 숫자 부분 검색을 각각 구현하세요 | minor (할 일) | NOT-APPLY (two printed booleans are the point) |
| 1.2.3 | 점을 문자 그대로 나누도록 Pattern.quote를 적용하세요. | minor (title period, starter comment) | NOT-APPLY (`[]` output already shows an empty array) |
| 1.2.4 | 숫자를 찾는 것과 식 전체의 유효성을 나누어 검사하세요 | minor (할 일, verbatim read) | NOT-APPLY (the `while (matcher.find())` loop result is printed) |

APPLY detail:
- 1.1.3, starter: line `System.out.println(pair[1]);`, event `step_line`, target `flow_memory`. The viewer shows `pair` = ["text", "a", "b"]: the third cell "b" that the output never prints, which proves the narration's claim "b가 다음 조각으로 떨어졌어요". After the patch, the same line shows ["text", "a=b"].
- 1.1.4, starter: line `return Integer.toString(pair[1].length());`, event `exception`. The viewer shows `pair` = ["text"] with one cell: the trailing empty piece was dropped. After the patch, `step_line` on the same line shows ["text", ""], an empty-string cell. The printed output is only "0", so it cannot show that the empty value is kept.

Defects:
- minor (systemic, see the summary): item 2 of the 「할 일」 is the title without a period ("2. &로 이어진 조건을 나누어 개수를 돌려주세요"). Item 3 is generic ("3. 서로 다른 입력으로 다시 실행하세요.") and names no input.
- minor: the titles of 1.1.3 and 1.2.3 end with "." and the other six do not. The same pattern appears in java-rq and java-calculator; all are the "…고치세요." steps.
- minor: starter comments state the target behavior while the code does the opposite. 1.1.3: "// 처음 만난 등호에서만 나눠 값 안의 등호를 보존해요." above `part.split("=")`. 1.2.3: "// 점 자체를 구분자로 써요." above `text.split(".")`. Read literally, the comment says the code is already right.
- minor: 1.2.4 reads the goal verbatim ("숫자를 찾았어도 계산식 전체가 올바르진 않아요.").

Leveling:
- The objective ("문자열 분리와 정규식의 전체 검사·일부 검색을 구분해요.") matches the steps. The order is split → regex escape → limit → trailing empty → whole match → find → quote → combine. One concept per step, and each edit is one line. ok.
- Prerequisites: java-collections and java-roles (manifest 15–16) come before. ok.

## 28. java-rq

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1 | Rq가 보관한 작업 이름을 돌려주세요 | minor (할 일) | **APPLY** (medium) |
| 1.1.2 | 조건이 붙은 요청에서도 작업 이름만 분리하세요 | minor | NOT-APPLY |
| 1.1.3 | 조건의 이름을 키로 삼아 값을 저장하세요 | minor (redundant imports) | **APPLY** (high) |
| 1.1.4 | 조건이 적힌 순서 대신 이름으로 값을 조회하세요 | minor (redundant imports) | NOT-APPLY (output "hello" vs "2" is enough) |
| 1.1.5 | Rq가 text=a=b의 값을 보존하도록 split을 고치세요. | minor (title period; repeats java-regex 1.1.3) | NOT-APPLY (already shown in java-regex 1.1.3) |
| 1.1.6 | 빈 문자열 값과 없는 조건을 구별하세요 | minor (redundant imports) | NOT-APPLY (the `[ ]` brackets are designed for this) |
| 1.2.1 | 문자열 id를 정수로 바꾼 뒤 1을 더하세요 | minor | NOT-APPLY |
| 1.2.2 | 없는 id만 기본값으로 처리하고 잘못된 숫자는 거절하세요 | minor | NOT-APPLY |
| 1.2.3 | 스트림의 각 조건을 키와 값 배열로 바꾸세요 | minor | NOT-APPLY (`deepToString` prints the arrays) |
| 1.2.4 | 나눈 배열의 이름과 값을 Map으로 모으세요 | minor | NOT-APPLY (same idea as 1.1.3 with a stream; the lambda is OPAQUE) |
| 1.2.5 | 같은 조건 이름이 두 번 오면 명시적으로 거절하세요 | minor | **APPLY** (medium) |
| 1.2.6 | getIntParam이 문자열 값을 정수로 바꾸도록 고치세요. | minor (title period) | NOT-APPLY |
| 1.3.1 | 빈 Rq를 완성해 목록 요청을 해석하세요 | ok | NOT-APPLY (combination challenge; the output shows each rule) |

APPLY detail:
- 1.1.1, starter: line `String getActionName() { return ""; }`, event `call`, target `flow_objects`. The `rq` object already holds `actionName = "list"`; the getter just doesn't return it. The output is an empty line and cannot show that the value is stored.
- 1.1.3, starter: line `String getParam(String name, String fallback) { return params.getOrDefault(name, fallback); }`, event `call`, target `flow_objects`. The HashMap `params` is {"2"="id", "hello"="text"}, so keys and values are swapped. The output only says "none".
- 1.2.5, starter: line `return newValue;`, event `call`, target `flow_stack`. The `duplicate(oldValue="1", newValue="2")` frame shows `toMap` handing over both values and the code silently dropping "1". The JDK frames between `Rq.<init>` and `duplicate` are not recorded; the user frames are enough.

Defects:
- minor: redundant explicit imports next to `import java.util.*;` in 1.1.3, 1.1.4, 1.1.6, 1.2.1, 1.2.2, 1.2.4 and 1.2.5. Example (1.1.3 starter and solution): `import java.util.*;\nimport java.util.HashMap;\nimport java.util.Map;`. The classes are used, so this is not rule §4, but it is noise.
- minor (systemic): 할 일 item 2 is the title, and item 3 "3. 값이나 순서를 바꾼 요청도 실행하세요." is generic in 1.1.1–1.2.6.

Leveling:
- ok overall. 1.1.5 re-teaches java-regex 1.1.3 almost word for word (text=a=b, split limit 2). It works as a recap inside Rq; the narration says so ("작업 이름에서 물음표를 나눌 때 쓴 2와 같은 방식이에요."). See PLAN.
- Streams (1.2.3–1.2.5) rely on java-streams (manifest 19). ok.

## 29. java-calculator

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1 | 이어진 숫자를 하나의 토큰으로 묶으세요 | minor (할 일) | NOT-APPLY |
| 1.1.2 | 두 숫자 토큰을 정수로 바꾸어 더하세요 | minor | NOT-APPLY |
| 1.1.3 | 곱셈을 먼저 계산한 결과에 첫 숫자를 더하세요 | minor | NOT-APPLY |
| 1.1.4 | 덧셈 단계가 완성된 곱셈 항을 받게 하세요 | minor (starter comment) | NOT-APPLY (optional: the stack shows expression→factor with no term frame; 1.2.1 shows the same idea better) |
| 1.2.1 | 괄호 안을 덧셈 단계부터 다시 계산하세요 | minor (starter comment) | **APPLY** (high) |
| 1.2.2 | 괄호 안에서 계산한 값을 호출한 쪽에 돌려주세요 | minor | **APPLY** (high) |
| 1.2.3 | 연 괄호를 닫지 않은 식을 거절하세요 | minor | NOT-APPLY |
| 1.2.4 | 읽은 위치로 입력을 끝까지 처리했는지 확인하세요 | minor | NOT-APPLY (`finished` prints the position fact) |
| 1.2.5 | term이 곱셈 기호 뒤의 값을 곱하도록 고치세요. | minor (title period) | NOT-APPLY |
| 1.2.6 | evaluate가 남은 입력을 확인하도록 검사 한 줄을 넣으세요. | minor (title period) | NOT-APPLY |
| 1.3.1 | 뺄셈을 덧셈과 같은 단계에서 왼쪽부터 계산하세요 | ok | **APPLY** (medium) |

APPLY detail. This is the strongest visualizer lesson in this range: mutual recursion and a `position` field that changes.
- 1.2.1, starter, input `(2+3)*4`: line `accept(')');` inside `factor`, event `step_line`, nth 1, target `flow_stack`. The stack is main → evaluate → expression → term → factor. The `factor` frame holds `value = 2`, and the Calculator's `position` sits on '+', not ')'. The inner `term()` stopped before the '+', which is what the narration says in words ("term이 덧셈 앞에서 멈췄어요"). After the patch, the same line shows `value = 5` with `position` on ')'.
- 1.2.2, starter, input `2*(3+4)`: line `return 0;`, event `step_line`, target `flow_stack`. The `factor` frame holds `value = 7`, and that value is about to be discarded. The outer `term` frame waits with `value = 2`. The output "0" cannot show that 7 was computed.
- 1.3.1, after the narration's deliberate wrong patch (`else if (accept('-')) value -= expression();`), input `10-2-3`: line `else return value;`, event `return`, nth 2, target `flow_stack`. The inner expression returns -1 (= 2-3) while the outer expression frame still holds 10, so 10-(-1) = 11. This makes the right-associativity visible. Verify the nth against the real trace with the validator: the first return is the innermost "3".

Defects:
- minor: the 1.1.4 starter comment "// 덧셈 단계예요. 무엇을 더하는지는 term 호출을 보세요." sits above an `expression()` that has no `term` call (`value += factor();`). The 1.2.1 starter comment "// 여는 괄호를 만나면 괄호 안을 덧셈 단계부터 다시 계산해요." sits above `int value = term();`. Same pattern as java-regex.
- minor (systemic): 할 일 item 2 is the title, and item 3 "3. 숫자나 괄호 위치를 바꾼 입력으로 다시 실행하세요." is generic in 1.1.1–1.2.6.

Leveling / prerequisites:
- **Prerequisite gap**: recursion is first used in 1.2.1 (`factor` calls `expression`) and first named in the 1.2.2 goal ("재귀 호출의 결과도 반환값으로 전달돼요."). No earlier lesson in manifest 1–28 teaches recursion: "재귀" appears only in java-calculator and java-parser. The listed prerequisites are java-regex and java-methods. This is the main reason the 1.2.1/1.2.2 code-flow moments matter. See PLAN.

## 30. java-crud

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1 | 글을 추가할 때마다 새 번호를 배정하세요 | minor (unused import) | NOT-APPLY (`1 1 {1=다음}` already shows the overwrite) |
| 1.1.2 | 요청한 글 번호로 내용을 조회하세요 | minor (unused import) | NOT-APPLY |
| 1.1.3 | 존재하는 글만 수정하고 없는 번호는 거절하세요 | minor (unused import) | NOT-APPLY |
| 1.1.4 | 지정한 글을 삭제하고 나머지 번호를 유지하세요 | minor (unused import) | NOT-APPLY |
| 1.1.5 | 공백 입력을 먼저 거절하고 원래 글을 보존하세요 | minor (unused import) | NOT-APPLY (the map print shows the half-applied change) |
| 2.1.1 | 반환한 목록을 비워도 원본 글이 남도록 사본을 만드세요 | minor (할 일 item 3 has no input to vary; unused import) | NOT-APPLY: the tracer draws `records.values()` as a separate `COLLECTION "LinkedValues"` box with no link to the map (Tracer.java:444-453). It would show two independent-looking lists, the opposite of the lesson. |
| 2.1.2 | 파일에서 글 번호와 내용 전체를 복원하세요 | **defect** (code flow vs task files) | IMPOSSIBLE as shipped: the trace has no quotes.txt (see defect) |
| 2.1.3 | 서비스가 전달받은 저장소를 사용하게 하세요 | **defect** (code flow vs task files); minor (할 일 item 3) | **APPLY** on the starter only (high), blocked on the after-fix trace |
| 2.1.4 | 삭제 뒤에도 발급한 적 없는 새 번호로 글을 추가하세요 | minor (unused import) | NOT-APPLY |
| 2.1.5 | targetId에 해당하는 기존 글만 수정하세요 | minor (unused import) | NOT-APPLY |
| 2.2.1 | 네 동작의 규칙을 지키는 글 서비스를 완성하세요 | ok | NOT-APPLY |

APPLY detail:
- 2.1.3, starter: line `public String load() { return "메모리 메모"; }` (MemoryStore), event `call`, nth 2, target `flow_objects`. The second `QuoteService`'s `store` field points to a `FileStore` object, yet the running frame is `MemoryStore.load`, because the service built a new MemoryStore. The output only repeats "메모리 메모". This moment works on the starter, because `FileStore.load` is never called. After the fix, a learner's own 코드 흐름 보기 hits the file defect below.

Defects:
- **defect**: in 2.1.2 and 2.1.3, code flow is Ready, but the Java trace runs without the task's `files`. `src/player_ui.rs:1236` calls `java_trace::trace(&source,&input)`, while the Python trace receives `&files`. `src/java_trace.rs:110-111` writes only `Main.java` and `stdin.txt`. So after the fix, `Files.readAllLines(path)` (2.1.2, input `quotes.txt`) and `FileStore.load()` → `Files.readString(Path.of("quotes.txt"))` (2.1.3) would throw NoSuchFileException in the viewer, while the graded run prints `{1=시작, 2=다음:메모}` / `파일 메모`. I derived this from the source and did not run the tracer here. Fix it in one of two ways: pass `task.files` to the Java trace, or set `code_flow: false` on these two steps until the tracer takes files. Root should check other courses' Java steps that have `files`.
- minor (content-rules §4, unused import): `import java.nio.file.*;` sits in the starter and solution of 1.1.1–1.1.5, 2.1.1, 2.1.4 and 2.1.5, and none of them uses Files, Path or Paths. The build's `drop_unused_imports` apparently does not catch wildcard imports.
- minor: 2.1.1 and 2.1.3 「할 일」 item 3 "3. 다른 입력으로도 실행해 글의 번호와 내용을 확인하세요." Both programs read no input (`tests` input `''`), and 2.1.3 has no 글 번호.
- info: in 2.1.5 the narration's final code differs from the solution only by one blank line after the imports.

Leveling: CRUD rules come one per step (id issue, lookup, update-only-existing, remove, validate-before-mutate), then copy, file restore, injection, id after delete, and a combination step. ok. 2.1.3 uses an interface, which java-roles (15) teaches.

## 31. docker-image-container

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.1.8, 2.1.1, 3.1.1, 3.2.1, 4.1.1, 5.1.1 (13 steps) | 실행하기 전에 이미지를 내려받으세요 … 앱을 고쳐 다시 빌드해도 메모가 남게 하세요 | minor (1.1.2 read; others automated) | IMPOSSIBLE (git terminal) |

- The command mismatches are all intended try/fail demonstrations: 1.1.2 runs `docker run` twice (Conflict), 1.1.5 runs `ls /memo.txt` on the host, and 1.1.8 runs `docker rm` before `docker stop`. ok.
- minor: the 1.1.2 goal explains BOX twice: '"$BOX"는 터미널에 미리 들어 있는 이번 수업의 이름이에요.' and later 'BOX에는 이번 수업만의 고유한 컨테이너 이름이 들어 있어요.'
- Leveling: 1.1.2 brings in `-d`, `--name` and `-p 127.0.0.1::80` at once, and 2.1.1 brings in a Compose file together with the PID 1 lifetime. See PLAN.

## 32. gitlab-ci

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1 | 먼저 내 터미널에서 검사 파일을 실행하세요 | minor (verbatim read) | IMPOSSIBLE (git terminal) |
| 1.1.2–1.3.3 (9 steps) | 검사 명령을 CI 작업에서 실행하세요 … 실패한 검사를 고치고 결과 파일까지 남기세요 | **defect** | IMPOSSIBLE |

Defects:
- **defect** (1.1.2–1.3.3): 「할 일」 item 5 is "`glab ci status --wait`로 이 커밋의 파이프라인이 끝날 때까지 기다려 결과를 확인하세요." and item 6 is "원하는 작업 상태와 산출물을 확인하고 제출하세요.". The narration runs only `git add .`, `git commit -m "CI 설정 변경"` and `git push`, then asserts results it never shows. In 1.1.3: "Runner도 이 틀린 값으로 검사하므로 실패해야 해요." / "종료 코드가 실패이면 화면의 파이프라인도 failed가 돼요." This breaks content-rules 「결과를 읽을 때 관찰한 값」 and voice.md 「해설도 할 일의 순서와 대응시킨다」.
- minor: in 1.1.2 and 1.1.3, item 6 mentions 산출물, but artifacts first appear in 1.2.2.
- minor (systemic): all 10 steps read the goal verbatim. Example (1.1.2): "직접 실행하던 sh check.sh를 GitLab Runner가 실행하게 하세요."
- info: the lint flag "starter==solution" on 1.1.3 and 1.1.4 is not a defect. The edited file there is `check.sh`, and the starter shown is `.gitlab-ci.yml`.

## 33. docker-network-ports

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1, 1.1.2, 1.2.1, 1.2.2 | 클라이언트가 web 서비스에 연결하게 하세요 … PC에서도 빈 포트로 서버에 연결하게 하세요 | ok (automated) | IMPOSSIBLE (git terminal) |

## 34. sql-first (MySQL 8.4)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–5.1.1 (18 steps) | 상품 한 행의 네 열을 조회하세요 … milk 재고만 한 개 차감하세요 | ok (all 36 run/say pairs match the recorded output) | IMPOSSIBLE (SQL unsupported) |

- Leveling: 2.2.3 (COUNT(*)→SUM(qty)) and 2.2.4 (COUNT(*)→COALESCE(SUM(qty),0)) are nearly the same step. The 2.2.4 narration only hints at the all-NULL case ("변형 검사에서는 … 모두 미정일 때도 확인해요") and never shows it. See PLAN.

## 35. sql-tables-constraints (MySQL 8.4)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.3.1 (6 steps) | 이름이 없는 회원을 DB에서 거절하세요 … 다른 클라이언트가 와도 예약 규칙을 지키세요 | ok | IMPOSSIBLE |

## 36. sql-join-group (PostgreSQL 18)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.3.2 (6 steps) | 주문을 실제 회원과만 연결하세요 … 모든 회원의 유료 주문 수와 합계를 구현하세요 | ok | IMPOSSIBLE |

- Note: the engine switches from MySQL (34–35) to PostgreSQL here (`||` concatenation, `::text`). The goal does mention PostgreSQL. In MySQL `||` means OR, so state the switch where it first matters. See PLAN.

## 37. sql-transactions (PostgreSQL)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.2.2 (4 steps) | 시험 변경을 저장하지 않고 되돌리세요 … 선택 작업의 실패만 취소하세요 | ok | IMPOSSIBLE |
| 1.3.1 | 정상 이체는 확정하고 실패한 이체는 전부 취소하세요 | minor | IMPOSSIBLE |

- minor (1.3.1): both narration runs print `1:70 / 2:130`, so the learner sees no difference before and after the change. The narration admits it ("30인 이번 입력은 우연히 두 문장 모두 성공해요"). content-rules asks to change one condition and observe the difference. A `set_input` to a failing amount for the second pair of runs would show the rollback.

## 38. h2-memory-file (java_libraries)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.1.5 | 두 연결에서 같은 메모를 읽게 하세요 … 여러 번 재시작해도 두 메모를 보관하세요 | minor (1.1.3–1.1.5 unused import) | IMPOSSIBLE (java_libraries unsupported; Connection and ResultSet would be OPAQUE anyway) |

- minor (content-rules §4): `import java.sql.*;` in Main of 1.1.3–1.1.5 is unused. Only the provided `Child.java` uses JDBC.

## 39. java-jdbc (java_libraries)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1, 1.1.2, 1.2.1, 1.2.2 | 조회한 모든 행을 순회해 개수를 세세요 … JDBC 이체가 중간에 실패하면 전체를 취소하세요 | minor (할 일 item 2 = title) | IMPOSSIBLE (java_libraries) |

## 40. sql-index-plan (PostgreSQL)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.2.2 (4 steps) | 송장 코드 조회용 인덱스를 만드세요 … 지역·상태·대소문자 조건을 함께 지원하세요 | ok | IMPOSSIBLE |

## 41. sql-isolation-locks (java_libraries over PostgreSQL)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1, 1.2.1, 1.2.2, 1.3.1 | 한 트랜잭션에서 같은 잔액을 다시 읽게 하세요 … 마지막 재고 하나가 두 번 팔리지 않게 하세요 | minor (할 일 item 2 = title) | IMPOSSIBLE |

- Reader load: the 1.3.1 provided code uses `CyclicBarrier` and `ExecutorService`. No earlier lesson teaches them. The student edits only SQL, so this is not a blocker. See PLAN.

## 42. docker-compose-db

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1, 1.2.1, 1.3.1 | app이 db 서비스의 데이터베이스에 접속하게 하세요 … 기존 메모를 보존하며 새 열을 추가하세요 | ok (automated) | IMPOSSIBLE (git terminal) |

## 43. java-tailwind (web)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–5.3.2 (24 steps) | 같은 클래스를 가진 두 카드에만 규칙을 적용하세요 … 화면 조건과 상태를 함께 만족하는 카드 규칙을 완성하세요 | minor | IMPOSSIBLE (web; CSS has no execution trace, so it stays NOT-APPLY even once JS tracing lands) |

- minor (systemic): 18 of 24 steps read the goal verbatim (1–11, 17–19, 21–24 by order).
- minor: the 1.2.2 title "뒤에 쓴 규칙이 이기지 않는 이유를 고치세요" asks to fix a reason. The step fixes the cause: delete the id color declaration.

## 44. java-react (web)

| 위치 | 제목 | 정합성 | 비주얼라이저 |
|---|---|---|---|
| 1.1.1–1.1.3, 2.1.1–2.1.3 | DOM 갱신, JSX, props | minor | NOT-APPLY (the DOM is the observation) |
| 3.1.1–3.1.3 | 새 상태 / 버튼과 설명 / 갱신 함수 | minor | NOT-APPLY (React's update queue is library internals; a JS trace of user frames would not show the snapshot) |
| 3.1.4 | 원본 배열을 바꾸지 말고 새 배열로 알리세요 | minor | **HOLD** (JS): a heap view would show `items.push` mutating the same array that `setItems(items)` passes back |
| 3.1.5 | 객체의 다른 필드는 보존하고 새 객체로 갱신하세요 | minor | **HOLD** (JS): old and new object identity |
| 4.1.1–7.1.2 (11 steps) | 상태 위치, key, 이벤트, 구독 정리, 파생 값 | minor | NOT-APPLY |

Defects:
- minor (systemic): 22/22 steps read the goal verbatim, often two or three sentences per step. Example (1.1.1): "좋아요 버튼은 count를 올려요. 화면 숫자까지 두 번 연속 바뀌게 고치세요." is read word for word.
- minor (systemic): the 「할 일」 is the same template in all 22 steps: "1. 코드를 실행하고 준비된 버튼·입력을 조작해 현재 동작을 확인하세요." / "2. <title>" / "3. 다시 실행하고 같은 조작을 반복해 전후 차이를 확인하세요." / "4. 값을 한 번 더 바꾸어 같은 원리가 적용되는지 확인한 뒤 코드를 제출하세요.". It names no button and no value, which breaks the voice.md 할 일 rules ("대상과 행동을 함께 쓴다", "추측하게 하는 지시는 쓰지 않는다").
- minor: the 1.1.1 goal asks "화면 숫자까지 두 번 연속 바뀌게", but after the fix the narration clicks `#like` once and reads "1".
- **Prerequisite gap**: the lesson uses JavaScript (`let`, arrow functions, `import`, `document.querySelector`, JSX) that no lesson in manifest 1–43 teaches. The prerequisites are only java-tailwind, and java-tailwind has none. See PLAN.

---

## PLAN items (structure, not fixes)

1. **java-calculator recursion intro.** Before 1.2.1, add a step (or reshape 1.2.1) that introduces "a method calls the parse chain again" with a 코드 흐름 보기 moment on the nested `factor → expression` stack. The 1.2.1/1.2.2 APPLY moments are a minimal version that needs no new step.
2. **Dedupe split-limit teaching.** java-regex 1.1.3 (값 안의 등호) and 1.1.4 (빈 값) and java-rq 1.1.5 all teach `split(…, 2)`. Keep java-regex 1.1.4 as the concept step. Turn java-regex 1.1.3 into a prediction or recap question, or drop it, and keep java-rq 1.1.5 as the in-context recap it already claims to be.
3. **sql-first 2.2.3/2.2.4.** Merge them, or make 2.2.4 visibly about the all-NULL input (`set_input`/data where every qty is NULL, so SUM gives NULL and COALESCE gives 0).
4. **SQL engine switch.** Add one sentence at the first PostgreSQL step of sql-join-group, and in the sql-index-plan intro, stating that these lessons run PostgreSQL and that `||` there concatenates text.
5. **docker-image-container leveling.** Split 1.1.2: run `-d --name` first, and move `-p` to the port step or the network lesson. Split 2.1.1: Compose file as a run recipe first, then PID 1 lifetime.
6. **java-react prerequisites.** Add or point to a minimal JavaScript lesson (variables, arrow functions, modules, DOM query) before java-react, or list a JS lesson as a prerequisite.
7. **sql-isolation-locks 1.3.1.** Move the concurrency scaffolding (`CyclicBarrier`, `ExecutorService`) out of sight into a provided helper, or label it explicitly as "읽지 않아도 되는 준비 코드".
8. **gitlab-ci narration.** Add a narration action that runs `glab ci status --wait` (or reads the pipeline) after each push, so the narration observes the result the 할 일 requires. It needs a real GitLab Runner in the demo, so this is a production change, not a text edit.
9. **Java trace coverage.** `src/java_trace.rs:177-181` replays only tasks with `"code_flow": true` from four engineer lessons, with input `""`. When APPLY moments are added here, set `code_flow: true` on those tasks and extend that test (or the narration validator) to java-backend lessons with `tests[0].input`. Otherwise the narration's `line`/`nth` is never checked against a real trace.
10. **Systemic 할 일 template** (java-regex, java-rq, java-calculator, java-crud, java-jdbc, sql-isolation-locks, java-react: 69 steps). Replace "2. <title>" with the concrete one-line edit, and replace the generic "다른 입력으로 다시 실행" with one concrete input per step. Where the program reads no input, drop the item.
11. **Systemic verbatim goal reading** (java-react 22, java-tailwind 18, gitlab-ci 10, github-pr 9, java-regex 1). Rewrite each into "why this sentence matters", per content-rules. This touches 60 steps, so batch it per lesson, and re-run `tools/narration_review.py` on each batch.

## 요약: APPLY 후보 (9)

All are Java, Ready on Windows, macOS and Linux. "starter" means the moment is opened before the narration's patch.

| # | 수업 위치 | 줄 (코드) | event | target | 보여 주는 것 |
|---|---|---|---|---|---|
| 1 | java-regex 1.1.3 | `System.out.println(pair[1]);` | step_line | flow_memory | `pair` = [text, a, b]; after the patch [text, a=b] |
| 2 | java-regex 1.1.4 | `return Integer.toString(pair[1].length());` | exception (starter) / step_line (after) | flow_memory | [text] with one cell, then [text, ""] |
| 3 | java-rq 1.1.1 | `String getActionName() { return ""; }` | call | flow_objects | the Rq already holds actionName = "list" |
| 4 | java-rq 1.1.3 | `String getParam(String name, String fallback) { return params.getOrDefault(name, fallback); }` | call | flow_objects | params = {2=id, hello=text}, keys and values swapped |
| 5 | java-rq 1.2.5 | `return newValue;` | call | flow_stack | duplicate(oldValue=1, newValue=2): "1" is dropped |
| 6 | java-calculator 1.2.1 | `accept(')');` | step_line nth 1 | flow_stack | nested main→…→factor; value=2, position on '+'; after the patch value=5 |
| 7 | java-calculator 1.2.2 | `return 0;` | step_line | flow_stack | factor holds value=7 but returns 0; outer term waits with 2 |
| 8 | java-calculator 1.3.1 (wrong try) | `else return value;` | return nth 2 (verify) | flow_stack | inner expression returns -1 while outer holds 10, so the result is 11 |
| 9 | java-crud 2.1.3 (starter only) | `public String load() { return "메모리 메모"; }` | call nth 2 | flow_objects | service.store → FileStore, yet MemoryStore.load runs |

HOLD (2): java-react 3.1.4 and 3.1.5 (JS heap identity), pending JS tracing.

## 요약: 결함

Defects (3 groups):
1. java-crud 2.1.2 and 2.1.3: Java code flow runs without the task files (`src/player_ui.rs:1236`, `src/java_trace.rs:110-111`), so the after-fix trace would throw NoSuchFileException while the graded run succeeds. Derived from source, not run.
2. gitlab-ci 1.1.2–1.3.3 (9 steps): the 「할 일」 requires `glab ci status --wait` and checking the job state, but the narration never runs it and asserts results it never shows ("실패해야 해요", "failed가 돼요").
3. (counted with 1) The trace test does not cover java-backend lessons at all (`src/java_trace.rs:179-181`), so nothing would catch #1 or a wrong `line`/`nth` in new narration.

Minor (13 groups):
1. 할 일 item 2 equals the title without a period, and item 3 is generic: java-regex 1–8, java-rq 1–12, java-calculator 1–10, java-crud 1–9, java-jdbc 1–4, sql-isolation-locks 1–4, java-react 1–22 (69 steps).
2. java-crud 2.1.1 and 2.1.3 item 3 asks for "다른 입력", but neither program reads input.
3. Verbatim goal reading: java-react 22, java-tailwind 18, gitlab-ci 10, github-pr 9, java-regex 1.2.4.
4. Unused `import java.nio.file.*;` in java-crud 1.1.1–1.1.5, 2.1.1, 2.1.4 and 2.1.5. Unused `import java.sql.*;` in h2-memory-file 1.1.3–1.1.5.
5. Redundant explicit `java.util` imports next to `java.util.*` in java-rq 1.1.3, 1.1.4, 1.1.6, 1.2.1, 1.2.2, 1.2.4, 1.2.5.
6. Starter comments that state target behavior the code does not do: java-regex 1.1.3 and 1.2.3, java-calculator 1.1.4 and 1.2.1.
7. Titles ending in "." only on the "…고치세요." steps: java-regex 1.1.3/1.2.3, java-rq 1.1.5/1.2.6, java-calculator 1.2.5/1.2.6.
8. sql-transactions 1.3.1 shows no observable before/after difference.
9. java-react 1.1.1: the goal asks for two consecutive changes, but the narration clicks once.
10. docker-image-container 1.1.2 explains BOX twice.
11. java-tailwind 1.2.2 title "…이유를 고치세요".
12. gitlab-ci 1.1.2/1.1.3 item 6 mentions 산출물 before artifacts are introduced.
13. git-branch-advanced 1.1.2, 1.2.1 and 1.3.1: commands not in backticks.

## 검토 범위의 한계 (빠짐 없이 밝힘)

- **All 22 lessons have a section, but not at the same depth.** Full read plus execution: lessons 27–30 (43 steps). Run-versus-narration pairing on recorded outputs: lessons 34–41 (46 steps), not executed here. Automated command and lint checks plus sampled reads: lessons 23–26, 31–33 and 42 (83 steps; read in full: git-branch 1.1.1, git-branch-advanced 1.2.1, github-pr 1.2.2, docker-image-container 1.1.2/1.1.5/2.1.1, gitlab-ci 1.1.2/1.1.3), and lessons 43–44 (46 steps; read: java-tailwind 1.2.2, java-react 1.1.1/3.1.3/3.1.4). Steps not read in full may hold semantic narration defects (for example a wrong 「-아도」 contrast) that these checks cannot find.
- I did not run the Java tracer. The APPLY lines and events come from reading the code and tracer semantics; `nth` values, especially java-calculator 1.3.1, need the validator replay.
- I did not run the SQL, H2, Docker or GitLab steps. Their outputs come from `tests/lesson-cases/*.json`.
