# java-backend 1-22 audit: leveling, correctness, code-flow use

Goal. The owner wants every lesson re-reviewed for leveling quality. They also want 코드 흐름 보기 used in narrations only where a trace shows something the printed output cannot, and never where the trace is hidden or adds nothing. This file is read-only review output. No repo file was changed.

## How this was reviewed

- Scope is course `java-backend`, manifest lessons 1 to 22 (inventory.json `courses[0].lessons[0..21]`). That is 214 steps.
- The review was split three ways. Lessons 2, 5, 6, 7, 13, 14 and 15 were reviewed in this thread. A delegate reviewed the eight terminal lessons (1, 3, 4, 8, 9, 10, 11, 12). A second delegate reviewed lessons 16 to 22. I spot-checked the delegates' sharpest claims against the dumps. The typo "늘 계획이 없으면" is confirmed. So are `switch` (0 hits in lessons 2 to 17) and `@Override` (2 hits in java-class-objects, 0 earlier). I did not re-review their remaining verdicts.
- Measured. Every Java task's starter and solution was run with `java Main.java` (JDK 25.0.3) against its `tests`. All 129 solutions pass. Every starter fails, except java-arrays #3 (see that lesson). The runner script is `C:\Users\jangk\AppData\Local\Temp\jb\run.py`, with its output in `run.out`.
- Measured. All 60 bash/java shell steps were replayed by the terminal delegate in Git Bash, from each step's demo state. Each final state matches `shell.goal`, and the narration's terminal-output claims match the real outputs (except the minor points listed). git-first was replayed with real git. Vim was checked only by reading.
- Visualizer availability comes from `Task::code_flow_availability` (src/repository_course.rs:169-180) and inventory.json. Every git_terminal step is Hidden on all OS, and that includes java-launch and java-arguments. Every other Java step is Ready on win, mac and linux. java-testing #7 to #9 are junit, which is Unsupported. No step in 1-22 has a `code_flow` narration action today.
- APPLY line numbers count lines in the starter or solution named. `step_line` means the line about to run. Every APPLY should be opened once in the app before its `say` is written. Two of them depend on tracer behavior I could only infer (marked "verify").

## Cross-lesson finding: generic template steps

Each of the following steps uses the same generic 할 일, "1. 코드 실행 버튼을 눌러 수정 전 결과를 확인하세요 … 4. 요구한 동작과 실행 결과를 비교한 뒤 코드를 제출하세요." None of them names an expected output. Most also open with the stock line "이 스텝은 제공된 코드에서 시작해요." and their 조심하세요 is often an anti-hardcoding line, not the step's real mistake. Measured by a scan of every goal:

| lesson | generic 할 일 | stock opener "이 스텝은 제공된…" |
|---|---|---|
| java-values | #2 af7ffe, #9 5002ef | |
| java-conditions | #8 a408a4 | #8 |
| java-arrays | #8 23d98f | #8 |
| java-methods | #8 0364a9 | |
| java-references | #10 8015f8 | |
| java-static | #7 f1733b, #8 a78b82 | #7, #8 |
| java-roles | #8 ff0ce5 | |
| java-collections | #10 6a6c4c | |
| java-class-objects | | #1 #2 #3 #5 #6 #7 #8 #9 |
| java-inheritance-composition | | #1 to #7 |
| java-streams | #10 0f6824 | |
| java-files | #10 7d0950 | |
| java-testing | #7 d6c54c, #8 84165e | |
| java-oop-patterns | | #1 #3 #5 #7 |

This conflicts with docs/voice.md (할 일 작성 규칙) and with content-rules 「해설은 문제를 설명한다」 ("모든 스텝에 같은 첫 문장 … 붙이지 않는다"). It is one minor defect family. The fix for each step is to name the concrete edit and the expected output, the way the neighboring steps already do, for example "3. 코드 실행을 눌러 6000이 나오는지 확인하세요." I list it once here and do not repeat it under each lesson.

---

## 1. bash-basics

Leveling is strong (terminal delegate). Each of the 24 steps adds one command or idea, in this order: pwd, ls, echo, `>`, cat, `>>`, mkdir, cd, `cd ..`, paths, hidden files, cp, overwrite, `cp -R`, mv, rm, rmdir, then `rm -r`. The 조심하세요 moments sit where real mistakes happen: #4 and #14 (`>` overwrites), #15 (cp overwrites silently) and #21 (rm cannot be undone). #24 is a real combine step whose check is a final state. #23 has the learner run the failing `rmdir` first. That command is correctly left out of `commands`, and the narration "Directory not empty" matches the real output.

| # | title | lang/flow (win,mac,linux) | verdict | note |
|---|---|---|---|---|
| 1-24 | all | git / hidden,hidden,hidden | IMPOSSIBLE | terminal step |

Defects:
- minor, #12 4ec454. "`.practice가 보여요. 점으로 시작하는 이름은 -a를 붙여야 목록에 나와요.`" does not mention the `.` and `..` entries the learner sees first in the real `ls -a` output. Fix: add "`.`은 지금 폴더, `..`은 10번에서 쓴 상위 폴더예요."

Plan:
- Optionally merge #1 and #2 (each a single command) to shorten a 24-step lesson.

## 2. java-values

Leveling is strong. The goal (값·식·출력, 변수의 현재 값, 덧셈 vs 연결) matches the 10 steps one to one. The steps run: print (#1), change the value (#2), quotes vs expression (#3), a variable name vs the string "quantity" (#4), assignment order (#5), `quantity = quantity + 1` (#6), string concatenation (#7), left-to-right `+` (#8), parentheses (#9), then a combine step (#10). Each step edits one line, except #10, which writes three. Every step has a variation run that catches hardcoding. The narration follows the edit, run, read loop. Every output claim matches the code; I recomputed `2개1`, `수량: 71` and `합계: 23개`.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 9d8f72 | 수량 2 출력 | java R,R,R | NOT-APPLY | one println |
| 2 af7ffe | 3으로 바꾸기 | java R,R,R | NOT-APPLY | |
| 3 98f40b | 식 계산 | java R,R,R | NOT-APPLY | |
| 4 9c81ab | 저장한 수량 | java R,R,R | NOT-APPLY | |
| 5 48e65c | 출력 전에 대입 | java R,R,R | APPLY | late assignment is invisible in the output |
| 6 837626 | 1 늘려 저장 | java R,R,R | NOT-APPLY | both values are already printed |
| 7 4b76b6 | 글자 뒤 수량 | java R,R,R | NOT-APPLY | |
| 8 293635 | 식의 순서 | java R,R,R | NOT-APPLY | a trace cannot show left-to-right `+` inside one expression |
| 9 5002ef | 괄호 | java R,R,R | NOT-APPLY | |
| 10 34c57b | 마지막 도전 | java R,R,R | NOT-APPLY | |

APPLY #5. The narration's middle demo puts `quantity = chosen;` after the println, so in that patched code it is line 8. Open the `return` event of main (line 9 `}`). The viewer shows `quantity = 3` while the output already printed 2. It makes the narration's sentence "그 뒤에 바뀐 값은 이미 찍힌 2를 고치지 못해요" visible: the value did change, just too late. This is the lesson's only variable-state moment, and it supports the chapter objective "지역 변수 값을 읽고 바꾸는 순서".

Defects:
- minor, #2 and #9. These are generic template steps (see the cross-lesson table). #9 never names the expected `수량: 8` in its 할 일.

Plan: none.

## 3. vim-basics

The terminal delegate found the progression works: i, Esc, :w, o, gg/j, I, x/u, dd, yy/p, search/n, Ctrl+R, :q! and :wq, then a combine step. Each check list matches its 할 일 order. #10's search columns are right under the character-column rule (assets/vim/practice.vim:28). Two steps carry more than one new idea: #7 (0, x and u) and #11 (G, A and Ctrl+R).

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-15 | all | git / hidden,hidden,hidden | IMPOSSIBLE | Vim state steps |

Defects:
- minor, lesson-wide. Key names in 할 일 are plain text (for example #5 "1. gg로 첫째 줄로 이동하세요"). docs/voice.md shows keys as inline code. Fix: wrap them in backticks.

Plan:
- Split #11 into G and A, then u and Ctrl+R.
- Optionally move `0` from #7 into #6.

## 4. java-launch

Clean, per the terminal delegate. The steps run: cat, then `java Main.java` (no class file), edit and rerun, javac (Main.class appears), `java Main`, then an edit without recompiling. That step returns a stale result and is enforced by `class_relation: same`. Then come recompile, run, and a combine step that shows the missing-class error. #9's narration matches the real JDK message.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-9 | all | git / hidden,hidden,hidden | IMPOSSIBLE | Java runs in the terminal |

Defects: none found.

Plan: none. A trace cannot show source vs class files on disk.

## 5. java-conditions

Leveling is good. The steps run: `>=` prints a boolean (#1), `>` vs `>=` (#2), `=` vs `==` (#3), a stale stored boolean (#4), if (#5), else with definite assignment (#6), separate ifs overwriting vs else if (#7), an AI boundary bug (#8), then a combine step (#9). Every step edits one or two lines. #4 is a good, uncommon concept: `free` holds a computed value, not the expression. Output claims match the code, including the narration's `20000` for `println(amount = paid)`.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 8465c9 | 기준 이상 출력 | java R,R,R | NOT-APPLY | |
| 2 deedd1 | `>` | java R,R,R | NOT-APPLY | |
| 3 f522a8 | `==` | java R,R,R | NOT-APPLY | |
| 4 85eb75 | 할인 후 다시 판단 | java R,R,R | APPLY (secondary) | stale boolean next to the changed amount |
| 5 b42d86 | if | java R,R,R | NOT-APPLY | |
| 6 a8445b | else | java R,R,R | NOT-APPLY | the starter does not compile |
| 7 fb259a | else if | java R,R,R | APPLY | the overwritten intermediate 0 |
| 8 a408a4 | 경계 | java R,R,R | NOT-APPLY | |
| 9 17f3b8 | 마지막 도전 | java R,R,R | NOT-APPLY | |

APPLY #7. On the starter, open `step_line` at line 9 `if (amount >= 10000) {`, nth 1. The viewer shows `fee = 0`, so the first if really ran. Then at line 12 `System.out.println(fee);` it shows 1000. The output prints only 1000, and the narration's claim "첫 if가 fee를 0으로 만든 뒤 두 번째 if도 참이라 1000으로 덮었어요" is otherwise taken on trust.

APPLY #4 (secondary, use it only if the lesson can afford two moments). On the starter, open `step_line` at line 10 `System.out.println(free);`. The locals show `amount = 19000` next to `free = true`. Printing shows only `true`.

Defects:
- minor, #8 a408a4. This is a generic template step, and its goal never states the rule (기준 금액 이상 무료). Only the title implies it.

Plan: none.

## 6. java-arrays

Leveling is good. The steps run: index 0 (#1), out of bounds (#2), `length - 1` (#3), moving an index (#4), while accumulation (#5), the same loop as a for header (#6), for-each plus a condition (#7), a boundary bug (#8), then combine (#9). Output claims match the code (`1001`, `3000`, `7500` and `4001` were rechecked).

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 36178e | 첫 가격 | java R,R,R | NOT-APPLY | |
| 2 0d5827 | 마지막 가격 | java R,R,R | NOT-APPLY | the exception message already gives index 3 and length 3 |
| 3 f71b68 | length - 1 | java R,R,R | NOT-APPLY | |
| 4 35f4e2 | index++ | java R,R,R | NOT-APPLY | optional: the `prices[index]++` demo would show the array cell changing to 1001, but the narration already explains it |
| 5 6bc52d | while 누적 | java R,R,R | APPLY | loop state per iteration |
| 6 a6d6ae | for 머리 | java R,R,R | NOT-APPLY | |
| 7 e3a05b | for-each 조건 | java R,R,R | NOT-APPLY | |
| 8 23d98f | 마지막 빠짐 | java R,R,R | NOT-APPLY | |
| 9 27f94a | 마지막 도전 | java R,R,R | NOT-APPLY | |

APPLY #5. The lesson objective is "조건·위치 갱신·누적을 연결". On the narration's wrong patch (`total = prices[index];`), open `step_line` at `index++;` (line 11 in the patched code), nth 2. It shows `index = 1, total = 2000`: the earlier 1000 was replaced. On the fixed code, the same `step_line`, nth 2, shows `total = 3000`. The output only shows the final 3000 or 6000.

Defects:
- minor, #3 f71b68. The starter passes the primary test (`prices[2]` prints 3000, measured). Only the variations `{4, 2, 1, 9}` and `{700}` catch it. That is fine for grading. But 할 일 1 "코드 실행을 눌러 지금 결과를 확인하세요" shows a correct-looking 3000, and the narration skips that run: it first grows the array to four elements, which is 할 일 3. Fix: reorder 할 일 to match the narration ("1. 가격을 네 개로 늘려 실행하세요 …"), or make the narration run the starter first and say "3000은 맞아 보여요".
- minor, #8 23d98f. Generic template step.

Plan: none.

## 7. java-methods

Leveling is good. The steps run: return (#1), a parameter is a copy and its change is lost (#2), capturing the return value (#3), argument order (#4), early return (#5), overload (#6), return inside a loop (#7), a boundary bug (#8), then combine (#9). The checker calls each method directly, which stops hardcoding. Output claims match the code; I recomputed `-299998` for `discounted(2, 3000)`.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 f9fa9b | return +1000 | java R,R,R | NOT-APPLY | |
| 2 32fa87 | 반환값 출력 | java R,R,R | APPLY | two frames, two `amount`s |
| 3 504bd0 | 반환값 저장 | java R,R,R | NOT-APPLY | |
| 4 bf1c2a | 인수 순서 | java R,R,R | APPLY | swapped parameters visible at the call |
| 5 99a802 | 이른 return | java R,R,R | NOT-APPLY | |
| 6 abf85a | 오버로드 | java R,R,R | NOT-APPLY | the starter does not compile, and the output shows 2 and 2.5 |
| 7 671575 | 반복 안 return | java R,R,R | NOT-APPLY | the output 2000 plus the narration suffice |
| 8 0364a9 | 경계 | java R,R,R | NOT-APPLY | |
| 9 13a5c9 | 마지막 도전 | java R,R,R | NOT-APPLY | |

APPLY #2. This is the clearest call-stack moment in lessons 2 to 15. On the starter, open `step_line` at line 5 `}` of add_fee (or the `return` event of add_fee). The add_fee frame holds `amount = 3000`, and main's frame below it still holds `amount = 2000`. That is exactly the narration's sentence "메서드의 amount는 넘겨받은 값을 복사한 다른 변수라서". The output only shows 2000.

APPLY #4. On the starter, open the `call` event of discounted (line 4 `return price - quantity * 100;`). The new frame shows `price = 2` and `quantity = 3000`. The output `-299998` is a puzzle; the frame is the answer.

Defects:
- minor, #1 to #3. The method names `next_fee` and `add_fee` are snake_case, while the same lesson's #8 uses `freeFrom` and every later lesson uses camelCase. That teaches a non-Java convention and is inconsistent within the lesson. The checkers call `Main.next_fee` and `Main.add_fee`, so a rename is a content change (see Plan).
- minor, #8 0364a9. Generic template step.

Plan:
- Rename `next_fee` and `add_fee` to `nextFee` and `addFee` in the starter, solution, checker, goal and narration, and regenerate the narration for #1 to #3.

## 8. java-arguments

Good one-variable-at-a-time leveling (terminal delegate). The steps run: no arguments, then one, two, `args[0]`, reordered arguments, `args[1]`, a quoted single argument, `007` staying a String, then a combine step. Every java_build stdout matches a real run. Bash quoting appears before lesson 9 teaches it, but #7's goal explains it inline.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-9 | all | git / hidden,hidden,hidden | IMPOSSIBLE | Java runs in the terminal |

Defects:
- minor, #3 a4bf12. The aside "글자 수 10과는 상관없어요." refers to nothing on screen. Fix: delete it.

Plan:
- HOLD, low value. An `args` array trace would need program-argument support in the tracer and a non-terminal step, and `args.length` already prints the same fact. Not recommended.

## 9. bash-variables

Well leveled (terminal delegate). The steps run: assign and read, spaces around `=`, spaces in a value, quoting on read, unset and empty values, a variable as a file name, then a combine step. Every error claim matches real Git Bash output.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-7 | all | git / hidden,hidden,hidden | IMPOSSIBLE | |

Defects:
- minor, #3 d0179d. "memo=우유가 사기 명령에만 붙은 이유는 명령 앞 할당을 배우는 수업에서 다시 봐요." This promises a callback that bash-command-env-args never makes (0 mentions of 우유). Fix: add the tie-back in lesson 11 #1, or drop the promise.
- minor, #5 725a81. "조심하세요. $aa처럼 이름을 잘못 써도 오류가 나지 않아요." contradicts #6, where the typo `"$fiel"` produces `No such file or directory`. Fix: "이름을 잘못 써도 Bash는 알려 주지 않고 빈 값으로 바꿔요."

Plan: none.

## 10. bash-environment

Clean (terminal delegate). The steps run: a plain variable is not inherited, export (with printenv as proof), the child copies the value at start, a child change does not reach the parent, a new shell and unset, then a combine step. All outputs match the narration.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-6 | all | git / hidden,hidden,hidden | IMPOSSIBLE | |

Defects: none found. Plan: none.

## 11. bash-command-env-args

Good (terminal delegate). The steps run: a prefix assignment for one command, a prefix overriding an exported value, environment vs `$1`, the same split read from Java (`System.getenv` vs `args`), then a combine step. The real outputs match, including `APP_MODE=[null]`.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-5 | all | git / hidden,hidden,hidden | IMPOSSIBLE | #4 runs Java in the terminal |

Defects: none, apart from the missing callback reported under lesson 9 #3.

Plan: none. The printed `null` already makes the point.

## 12. git-first

A solid three-places model (terminal delegate). The steps run: init and an untracked file, add, commit, the file differing from the commit, the staging snapshot (all three places differ), re-add with commit and `HEAD^`, then a combine step from an empty folder. Replayed with real git, the narration matches.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-7 | all | git / hidden,hidden,hidden | IMPOSSIBLE | |

Defects:
- minor, #4 36f36d and #5 1e7509. Commands in 할 일 are plain text, for example "1. echo "둘째 메모" > memo.txt를 실행하세요." and "5. git diff --cached로 …". Fix: use inline code, as the other steps do.
- minor, lesson objective. "git init으로 저장소를 만들고 echo로 메모 파일을 작성해요." presents echo as new, but lesson 1 taught it.

Plan: none.

## 13. java-references

This is the course's core aliasing lesson, and it is well built. The steps run: new and a field (#1), two objects (#2), `b = a` (#3), reassigning b vs mutating (#4), a parameter receiving a reference and mutating through it (#5), reassigning a parameter (#6), default equals vs a content method (#7), String `==` vs equals (#8), a final reference (#9), `this.count` (#10), then alias plus copy (#11). Every step edits one or two lines. Output claims match the code.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 945d1f | new Box | java R,R,R | NOT-APPLY | |
| 2 d2d44b | 두 상자 | java R,R,R | NOT-APPLY | #3 covers the picture |
| 3 ba4cd0 | b = a | java R,R,R | APPLY | two arrows, one box |
| 4 5f7f2b | b만 새 상자 | java R,R,R | NOT-APPLY | `a == b` already prints, and #3 has the picture |
| 5 d7d38c | 메서드가 받은 상자 | java R,R,R | APPLY | item and a share one Box |
| 6 2ca989 | 새 상자 돌려받기 | java R,R,R | APPLY | reassigned parameter vs unchanged caller |
| 7 dd589b | sameCount | java R,R,R | NOT-APPLY | |
| 8 4dfcc1 | String equals | java R,R,R | NOT-APPLY | the tracer draws String inline, so identity cannot be shown |
| 9 b654b9 | final 참조 | java R,R,R | NOT-APPLY | the starter does not compile |
| 10 8015f8 | this.count | java R,R,R | APPLY (verify) | two `count`s |
| 11 04d38f | 마지막 도전 | java R,R,R | NOT-APPLY | optional; repeats #3 |

APPLY moments:
- #3. On the starter, open `step_line` at line 17 `System.out.println(a.count);`, nth 1. Two Box objects appear (2 and 7). After the patch, the same step shows one Box with count 7 and both `a` and `b` arrows on it. Model the `say` on the existing engineer-java-references moment.
- #5. On the solution, open the `call` event of add (line 13 `item.count = item.count + 1;`). add's `item` arrow and main's `a` arrow land on the same Box, count 2.
- #6. On the starter, open the `return` event of replace (line 13 `}`). replace's `item` points to a new Box(99), while main's `a` still points to Box(2). This is the moment the output cannot show at all: the 99 box exists, but nobody in main can see it. Pair it with #5 for the contrast the narration already draws.
- #10 (verify). On the starter, open the `return` event of the Box constructor (line 7 `}`). The constructor frame's local `count = 2` sits next to `this`, a Box whose field `count` is 0. Check in the app that the constructor frame shows both the parameter and `this` before writing the say.

Defects:
- minor, #10 8015f8. Generic template step.

Plan:
- java-class-objects #1, #2, #4 and #7 re-teach this lesson's #3 to #6 and java-roles #1 and #6 as if new (lessons 16-22 delegate). Rescope them as recall plus combine.

## 14. java-static

Leveling is good. The steps run: per-object fields (#1), a static counter (#2), a static method and why it cannot read `amount` (#3), statics resetting per run (#4), static vs instance init blocks (#5), static final shared with per-object amounts (#6), a wrongly static `amount` (#7), `created = 1` vs `++` (#8), then combine (#9). Output claims match the code; with `static int amount`, #9's narration "두 주문이 모두 1000" is right.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 090b0a | 객체별 금액 | java R,R,R | NOT-APPLY | #7 shows the contrast better |
| 2 fad962 | Ticket.created | java R,R,R | NOT-APPLY | the count is printed |
| 3 230549 | countCreated | java R,R,R | NOT-APPLY | compile-error demo |
| 4 838e63 | 실행마다 0 | java R,R,R | NOT-APPLY | crosses runs; one trace cannot show it |
| 5 47d12a | static 블록 | java R,R,R | NOT-APPLY | the print order is the evidence |
| 6 8095c2 | isFree | java R,R,R | NOT-APPLY | |
| 7 f1733b | static 지우기 | java R,R,R | APPLY (verify) | static vs instance storage |
| 8 a78b82 | created++ | java R,R,R | NOT-APPLY | |
| 9 72c94e | 마지막 도전 | java R,R,R | NOT-APPLY | |

APPLY #7 (verify). On the starter, open `step_line` at line 17 `System.out.println(a.amount);`. The two Ticket objects have no `amount` field, and the statics area shows one `Ticket.amount = 2000`. After the patch, the same step shows each Ticket holding its own amount (1000 and 2000) and nothing in statics. This is the lesson's first objective, "객체별 상태와 클래스 공유 상태를 구별", as a picture. Verify in the app that user-class statics appear in the statics area and are not listed inside each object.

Defects:
- minor, #7 f1733b and #8 a78b82. Generic template steps with the stock opener.

Plan: none.

## 15. java-roles

Leveling is mostly good. The steps run: private plus a getter (#1), a guard clause (#2), interface and implements (#3), public on the implementation (#4), composition (#5), throw in a constructor (#6), finally (#7), a two-condition guard (#8), then combine (#9). The output claims match the code (`true, -50, true, -90`, `true 101` and `9000 true 11000` recomputed). The leveling gap is `||`: #8 needs it, and nothing before teaches it.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 c46220 | private | java R,R,R | NOT-APPLY | the starter does not compile |
| 2 7d1ddc | 출금 거절 | java R,R,R | NOT-APPLY | |
| 3 fdc3bf | implements | java R,R,R | NOT-APPLY | the starter does not compile; #5 has the dispatch picture |
| 4 aeb880 | public 구현 | java R,R,R | NOT-APPLY | compile error |
| 5 74ccb7 | 정책 꽂기 | java R,R,R | APPLY | composition and dispatch |
| 6 b74f06 | 생성자 예외 | java R,R,R | NOT-APPLY | |
| 7 e67181 | finally | java R,R,R | NOT-APPLY | the print order is the evidence |
| 8 ff0ce5 | 양수·잔액 이하 | java R,R,R | NOT-APPLY | |
| 9 a8f7c2 | 마지막 도전 | java R,R,R | NOT-APPLY | |

APPLY #5. On the solution, open the `call` event of FreeFee.fee (line 7 `public int fee() { return 0; }`). The stack reads main, then Checkout.total, then FreeFee.fee, and the Checkout object's private `policy` field points to a FreeFee object. On the starter, the same moment lands in StandardFee.fee (line 4). This shows "Checkout 코드는 한 줄도 바꾸지 않았는데" as structure: same Checkout, different object plugged in.

Defects:
- defect, #8 ff0ce5. The goal says "2번에서 본 ||를 쓰면 두 조건을 한 줄에 쓸 수 있어요." Step #2's code is `if (amount > balance) return false;`, which has no `||`. A grep of lessons 2, 5, 6, 7, 13, 14 and 15 finds no `||` before this step. The step therefore cites a lesson moment that does not exist and uses an operator never taught. Fix: replace the sentence with an 알아두세요 line such as "`a || b`는 둘 중 하나라도 참이면 참이에요." Or introduce `||` in a short step after #2.
- minor, #8 ff0ce5. Generic template step.
- minor, #9 a8f7c2. The reference solution uses the untaught ternary `return amount >= 10000 ? 0 : 1500;`. The narration also fixes things in the order MemberFee, pay, constructor, while the 할 일 order is MemberFee, constructor, pay. Fix: use an if and return in the solution and the narration, and swap 할 일 2 and 3 to match the narration.

Plan:
- Teach `||` (and `&&`) in java-conditions, where comparison operators live. java-conditions has no compound condition today.

## 16. java-collections

Lessons 16-22 delegate. The order is sound: add, get, element type, remove(index) vs remove(value), immutable List.of, Set, Map overwrite, getOrDefault, shallow copy, accumulate, then combine. The weak spot is #10. Its answer line `counts.put(item, counts.getOrDefault(item, 0) + 1);` is already in #8's starter, so #10 practises nothing new.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-8 | (list, set, map basics) | java R,R,R | NOT-APPLY | the printed collections suffice |
| 9 b3692a | 스냅샷 원소 객체 | java R,R,R | APPLY | shallow copy shares the Box |
| 10 6a6c4c | 개수 누적 | java R,R,R | NOT-APPLY | |
| 11 b21f74 | 종류 수와 개수 | java R,R,R | NOT-APPLY | |

APPLY #9. On the starter, open `step_line` at line 14 `System.out.println(snapshot.get(0).quantity);`. `original` and `snapshot` are different lists, yet both first elements and `item` point to one Box. After the patch, the same println (line 16) shows a separate Box.

Defects:
- minor, #1 fee1ae. "배열 start의 원소로 원소를 더하고 뺄 수 있는 목록을 만들어요" repeats 원소. Fix: "배열 start의 원소로 시작하고, 원소를 더하고 뺄 수 있는 목록을 만들어요".
- minor, #10 6a6c4c. A generic template step. Its 조심하세요 is anti-hardcoding, while the real mistake is `put(item, 1)`. The solution diff adds a stray blank line.
- minor, #11 b21f74. A `say` targeted at "같은 상품이 여러 번 나올 수 있어요." actually says "마지막 도전이에요…". The target and the content do not match.

Plan:
- Stop #8's starter from revealing #10's answer, or drop #10 and give #11 a scaffold.

## 17. java-class-objects

Lessons 16-22 delegate. On its own, the lesson builds well: alias, parameter reassignment, a null field, a constructor rule, shallow copy, equals and hashCode, private, defensive copy, then an atomic move. Against the manifest, #1, #2, #4 and #7 repeat java-references #3 to #6 and java-roles #1 and #6, yet are framed as new. #6 uses `@Override`, `super.hashCode()` and `instanceof Coupon c`, none of which lessons 2 to 16 teach; `@Override` is introduced in lesson 18.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 712955 | 새 객체로 | java R,R,R | APPLY | alias arrows (repeats lesson 13 #3; keep only one) |
| 2 53fe3d | 취소하면 비게 | java R,R,R | APPLY | call frame vs caller |
| 3 ef1561 | 생성자에서 목록 | java R,R,R | NOT-APPLY | the NPE message names `this.items` (measured) |
| 4 294027 | 한도 1 미만 | java R,R,R | NOT-APPLY | |
| 5 70c3de | 복사본 | java R,R,R | APPLY | two Carts share one list |
| 6 397878 | hashCode | java R,R,R | NOT-APPLY | HashMap internals are noise |
| 7 318399 | private | java R,R,R | NOT-APPLY | compile error |
| 8 350529 | 보여 준 목록 | java R,R,R | APPLY | leaked internal reference |
| 9 81fb54 | 옮기다 실패 | java R,R,R | NOT-APPLY | |

APPLY moments:
- #1. `step_line` at line 18 `mine.add(mineAdds);`. One Cart with two arrows; after the patch, two Carts.
- #2. The `call` event at line 14 `cart = new Cart();`, then `step_line` at line 15 `}`. The cancel frame's `cart` points to a new empty Cart, while main's `mine` keeps the count-3 Cart.
- #5. `step_line` at line 30 `copy.addAll(...)`. Two Cart objects whose `items` arrows meet at one ArrayList.
- #8. `step_line` at line 39 `shown.add("(추천 상품)");`. main's `shown` and the Cart's private `items` are one ArrayList.

Defects:
- defect, #6 397878. `@Override`, `super.hashCode()` and pattern-matching `instanceof` are used before they are taught. Fix: add an 알아두세요 (equals and hashCode come from Object, and @Override marks a redefinition), or move this step after lesson 18.
- minor, #8 350529. The 조심하세요 is about `subList`, which the course never teaches.
- minor. Stock opener on 8 of 9 steps (see the cross-lesson table).

Plan:
- Rescope #1, #2, #4 and #7 as recall plus combine, or spend those steps on Coupon object identity (`==` vs equals on user objects, which the tracer can show).

## 18. java-inheritance-composition

Lessons 16-22 delegate. Strong and focused. The steps run: override, the overload trap, field hiding, an overridable call in a constructor, the fragile base class, composition, template method, then combine. The prepared code in #1 to #3 uses a `switch` expression and `getClass().getSimpleName()`. My grep confirms `switch` has 0 hits in lessons 2 to 17.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 382677 | 픽업 0원 재정의 | java R,R,R | APPLY | which override ran |
| 2 a8ecd7 | @Override 오버로드 | java R,R,R | NOT-APPLY | the compiler message is the lesson |
| 3 3ae2cf | 필드 가림 | java R,R,R | APPLY | two `name` fields on one object |
| 4 30840c | 생성 중 호출 | java R,R,R | APPLY (verify) | null region during the super constructor |
| 5 db1d69 | addAll 두 번 셈 | java R,R,R | APPLY | self-call through super |
| 6 46bd23 | 컴포지션 | java R,R,R | NOT-APPLY | the point is a call that does not happen |
| 7 3e0568 | 추상 본문 | java R,R,R | NOT-APPLY | the starter does not compile |
| 8 94f825 | 마지막 도전 | java R,R,R | NOT-APPLY | |

APPLY moments:
- #1. On the starter, the `call` event at line 7 `return 3000;`, nth 2. The frame is Shipping.fee, but `this` is a Pickup. After the patch, the `call` at line 23 (Pickup.fee).
- #3. `step_line` at line 51 `System.out.println(s.name + ...)`. The Express object shows both `name: "일반"` and `Express.name: "특급"`.
- #4 (verify). The `call` event at line 23 `return "특급(" + region + ")";`. The stack is main, then the Shipping constructor, then Express.describe, with `region` null. Per Instrumenter, the Express `<init>` frame is not on the stack yet, so the say should read "Shipping 생성자가 아직 실행 중", not "Express 생성자 안".
- #5. `step_line` at line 11 `addCount++;`, nth 3. The stack is main, then CountingSet.addAll, then CountingSet.add, with `addCount` already 5.

Defects:
- defect, #1, #2 and #3. The prepared code relies on an untaught switch expression and `getClass().getSimpleName()`. Fix: use the if/else form already used in #4, or add an 알아두세요.
- minor, #8 94f825. `Standard.name()` lacks `@Override` while its siblings have it.
- minor. Stock opener on #1 to #7.

Plan:
- Simplify #6's starter. Show the inherited TreeSet counter's wrong count in its own step first.

## 19. java-streams

Lessons 16-22 delegate. The order is clear: lambda, filter vs removeIf, map, laziness, a consumed stream, an empty sum, Optional, distinct and sorted, toMap merge, a boundary, then combine. Stream objects and lambdas trace as OPAQUE plus `lambda$main$N` frames, so pipeline traces are noise for a beginner.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 3eeaa0 | 람다 기준 | java R,R,R | NOT-APPLY | |
| 2 b1f076 | filter 새 목록 | java R,R,R | APPLY | aliasing, not the pipeline |
| 3, 4, 6-11 | | java R,R,R | NOT-APPLY | pipeline traces are noise; #4's prints already show the laziness |
| 5 051ae7 | 소비된 스트림 | java R,R,R | HOLD | the stream is OPAQUE, so its consumed state is invisible |

APPLY #2. On the starter, `step_line` at line 13 `System.out.println(selected);`. `selected` and `prices` are one ArrayList. After the patch (line 12), `selected` is a separate list.

Defects:
- defect, #11 6b5c47. The solution needs `max`, `Optional.map`, `Integer::compare` and `String::valueOf`, none of them taught. Fix: add a `max` step, or accept an isPresent-style solution.
- minor, #1 to #10. Unused wildcard imports.
- minor, #10 0f6824. Generic template step with a stray blank line.

Plan:
- Insert a `max` and Optional step before #11.

## 20. java-files

Lessons 16-22 delegate. Good small steps, with the trap-then-fix pattern used well. No trace adds anything: file state is outside the tracer, and the print order already shows the try and finally behavior.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-11 | all | java R,R,R | NOT-APPLY | file contents are not in the trace |

Defects:
- minor, #1 to #10. Unused imports (`java.io.*` everywhere except #4, and `StandardCharsets` in #3 to #9).
- minor, #8 543dcd. The goal never states the fixture's content; only the narration reveals "oops".
- minor, #10 7d0950. Generic template step.
- minor, #11 96f43d. An interim narration comment says "APPEND는 기존 내용 뒤에 이어 써요" above a write that has no APPEND.

Plan: none.

## 21. java-testing

Lessons 16-22 delegate. The idea sequence is good. The 할 일 text in #1 to #6 is weak: item 2 copies the title with no final period, and item 3 is the vague "검사가 요구를 확인하는지 살펴보세요".

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1-4, 6 | | java R,R,R | NOT-APPLY | |
| 5 e64ab0 | 독립 카운터 | java R,R,R | APPLY | static shared Counter |
| 7-9 | JUnit, AssertJ | junit unsupported | IMPOSSIBLE | |

APPLY #5. On the starter, `step_line` at line 12 `return counter.next();`, nth 2. The local `counter` arrow points to the same Counter held by the static `Main.shared`, whose count is already 1. After the patch, a fresh Counter.

Defects:
- minor, #1 to #6. Item 2 is the title without a period, and item 3 is vague.
- minor, #7 and #8. They write "알아두세요:" inline instead of the **알아두세요** heading.
- minor, lesson objective. "잘못된 AI 변경을 잡는" is never framed in any step.

Plan: none.

## 22. java-oop-patterns

Lessons 16-22 delegate. The order works: Strategy (a class, then a lambda), Factory, then Observer (notify, unsubscribe during iteration, failure isolation). #4 makes the student write a `switch` arrow case, which was never taught. The objective "패턴이 필요 없는 경우도 판단해요" has no step behind it.

| # | title | lang/flow | verdict | note |
|---|---|---|---|---|
| 1 c3020e | vip 정책 | java R,R,R | APPLY | composition plus dispatch |
| 2 e714e4 | coupon 람다 | java R,R,R | NOT-APPLY | an OPAQUE lambda confuses more than it helps |
| 3-5, 7 | | java R,R,R | NOT-APPLY | |
| 6 25460a | 구독 해제 중 반복 | java R,R,R | APPLY | starter only |

APPLY moments:
- #1. On the patched code, the `call` event at line 18 (Vip.apply). The stack is main, then Checkout.total, then Vip.apply, with `Checkout.policy` pointing to a Vip. This overlaps java-roles #5; if both stay, give #1's say the new point (the class choice moved out of Checkout).
- #6. On the starter, `step_line` at line 50 `order.unsubscribe(this);`. The stack is main, then Order.complete mid-loop, then FirstOrderCoupon.onCompleted. The coupon's `order` field points back to the Order whose `listeners` list is being iterated.

Defects:
- defect, #4 7e8608. The student writes an untaught `case "push" -> ...` line. Fix: an 알아두세요 on the switch arrow form, or an if-chain.
- defect, #5 dc43e6. Typo "구독자가 하나뿐이고 늘 계획이 없으면" should be "늘릴 계획이 없으면" (confirmed by grep).
- minor, objective. "패턴이 필요 없는 경우도 판단" has no step behind it.
- minor. Stock opener on #1, #3, #5 and #7.

Plan:
- Add one judgment step, or remove the claim from the objectives.

---

## Summary

### All APPLY candidates (25)

Lessons 2-15 (reviewed in this thread):
1. java-values #5 48e65c. `return` of main after the late `quantity = chosen;`. `quantity = 3` while 2 was already printed.
2. java-conditions #7 fb259a. `step_line` at line 9 `if (amount >= 10000) {`. `fee = 0` before the overwrite.
3. java-conditions #4 85eb75 (secondary). `step_line` at line 10 `System.out.println(free);`. `amount = 19000` next to `free = true`.
4. java-arrays #5 6bc52d. `step_line` at `index++;`, nth 2, on the wrong patch and then on the fix. `total` 2000 (replaced) vs 3000 (accumulated).
5. java-methods #2 32fa87. `return` of add_fee (line 5). add_fee `amount = 3000` above main `amount = 2000`.
6. java-methods #4 bf1c2a. `call` of discounted. `price = 2, quantity = 3000`.
7. java-references #3 ba4cd0. `step_line` at line 17, before and after. Two Boxes, then one Box with two arrows.
8. java-references #5 d7d38c. `call` of add (line 13). `item` and `a` share one Box.
9. java-references #6 2ca989. `return` of replace (line 13). `item` points to Box(99) while `a` keeps Box(2).
10. java-references #10 8015f8 (verify). `return` of the Box constructor (line 7). Local `count = 2` vs `this.count = 0`.
11. java-static #7 f1733b (verify). `step_line` at line 17, before and after. One static `Ticket.amount` vs a field per object.
12. java-roles #5 74ccb7. `call` of FreeFee.fee (line 7). The stack main, Checkout.total, FreeFee.fee, and `policy` pointing to FreeFee.

Lessons 16-22 (delegate, not re-verified by me):
13. java-collections #9 b3692a. Line 14 println: the shallow copy shares the Box.
14. java-class-objects #1 712955. Line 18: one Cart, two arrows.
15. java-class-objects #2 53fe3d. `call` at line 14, then line 15: the cancel frame's new Cart vs main's.
16. java-class-objects #5 70c3de. Line 30: two Carts, one items list.
17. java-class-objects #8 350529. Line 39: `shown` is the private list.
18. java-inheritance-composition #1 382677. `call` at line 7, nth 2: Shipping.fee with `this` a Pickup.
19. java-inheritance-composition #3 3ae2cf. Line 51: `name` and `Express.name`.
20. java-inheritance-composition #4 30840c (verify). `call` at line 23: null region during the super constructor.
21. java-inheritance-composition #5 db1d69. Line 11, nth 3: add re-entered under addAll.
22. java-streams #2 b1f076. Line 13: `selected` and `prices` are one list.
23. java-testing #5 e64ab0. Line 12, nth 2: `counter` is the static shared Counter.
24. java-oop-patterns #1 c3020e. `call` of Vip.apply at line 18.
25. java-oop-patterns #6 25460a. Line 50: unsubscribe during iteration.

HOLD: java-streams #5 (a consumed stream is OPAQUE), and java-arguments (an `args` trace needs program arguments plus a non-terminal step; not recommended).

IMPOSSIBLE: all 82 steps of lessons 1, 3, 4, 8, 9, 10, 11 and 12 (git_terminal, so Hidden), plus java-testing #7 to #9 (junit, Unsupported).

### All defects

Severity "defect" (6):
1. java-roles #8 ff0ce5. "2번에서 본 ||" does not exist, and `||` is never taught before this step.
2. java-class-objects #6 397878. `@Override`, `super.hashCode()` and pattern instanceof come before lesson 18.
3. java-inheritance-composition #1, #2 and #3. Prepared code uses an untaught switch expression and `getClass().getSimpleName()`.
4. java-streams #11 6b5c47. The solution needs untaught `max`, `Optional.map` and method references.
5. java-oop-patterns #4 7e8608. The student writes an untaught switch `case ->`.
6. java-oop-patterns #5 dc43e6. Typo "늘 계획이 없으면" for "늘릴 계획이 없으면".

Severity "minor" (29 entries):
1. Generic template steps across 11 lessons (one family; see the cross-lesson table for the 15 steps and the stock-opener steps).
2. bash-basics #12 4ec454. The `ls -a` narration skips `.` and `..`.
3. vim-basics, lesson-wide. Keys in 할 일 are not inline code.
4. java-arguments #3 a4bf12. The stray aside "글자 수 10과는 상관없어요."
5. bash-variables #3 d0179d. The callback to lesson 11 is never kept.
6. bash-variables #5 725a81. "오류가 나지 않아요" conflicts with #6's real error.
7. git-first #4 36f36d and #5 1e7509. Commands in 할 일 are not inline code.
8. git-first objective. It lists echo as new.
9. java-arrays #3 f71b68. 할 일 1 shows a correct-looking starter result, the narration order differs from 할 일, and the primary test passes on the starter (only the variations catch it).
10. java-methods #1 to #3. snake_case `next_fee` and `add_fee`, against camelCase elsewhere.
11. java-roles #9 a8f7c2. Untaught ternary in the solution, and the narration order differs from 할 일.
12. java-collections #1 fee1ae. "원소로 원소를".
13. java-collections #10 6a6c4c. The answer is already in #8's starter, plus a stray blank line.
14. java-collections #11 b21f74. A `say` target does not match its content.
15. java-class-objects #8 350529. 조심하세요 about the untaught subList.
16. java-inheritance-composition #8 94f825. A missing `@Override`.
17. java-streams #1 to #10. Unused imports.
18. java-streams #10 0f6824. A stray blank line in the solution diff.
19. java-files #1 to #10. Unused imports.
20. java-files #8 543dcd. The fixture content is not stated.
21. java-files #11 96f43d. An interim comment says APPEND without APPEND.
22. java-testing #1 to #6. 할 일 item 2 copies the title, and item 3 is vague.
23. java-testing #7 and #8. Inline "알아두세요:".
24. java-testing objective. "AI 변경" is never framed.
25. java-oop-patterns objective. "패턴이 필요 없는 경우" has no step.
26. java-values #9 5002ef. 할 일 does not name `수량: 8` (also listed under the template family).
27. java-conditions #8 a408a4. The rule is not stated in the goal.
28. java-class-objects #1, #2, #4 and #7. Re-teach earlier lessons as new (leveling).
29. java-oop-patterns, java-class-objects and java-inheritance-composition. Stock openers (template family).

### Plan items (structural, not fixes)

- java-conditions. Add a compound-condition step (`&&` and `||`) so java-roles #8 has a prerequisite.
- java-methods. Rename `next_fee` and `add_fee` to camelCase in the starter, solution, checker, goal and narration. This regenerates the narration for #1 to #3.
- java-class-objects. Rescope #1, #2, #4 and #7 as recall plus combine, or replace them with user-object identity steps.
- java-collections. Stop #8 from revealing #10's answer.
- java-streams. Add a `max` and Optional step before #11.
- java-inheritance-composition. Split #6 so that the inherited counter's wrong count is its own step.
- java-oop-patterns. Add a "no pattern needed" judgment step, or drop the claim.
- vim-basics. Split #11, and optionally move `0` from #7 into #6.
- Course-wide. Rewrite the 15 generic-template steps in their lessons' own 할 일 style.

### Coverage and gaps

- Every step of all 22 lessons (214 steps) got a verdict and a correctness read. Lessons 2, 5, 6, 7, 13, 14 and 15 were read in full in this thread. The other 15 lessons were read in full by two delegates. I spot-checked three of their claims and did not re-read the rest.
- Not done: no APPLY moment was opened in the running app. The line numbers come from the starter and solution text. java-references #10, java-static #7 and java-inheritance-composition #4 depend on tracer behavior (constructor frames, user-class statics) that was inferred and not observed.
- Not done: vim-basics was never run in a real Vim. Checkers were read only as far as the dump's 600-character truncation. approved-prd.json files were not opened for lessons 2-15. tools/build-kpc-course.py was not run.
- Narration output claims in lessons 2-15 were checked by reading the code and recomputing values, not by running each narration patch. Every solution and starter was run against `tests`.
