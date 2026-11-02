# engineer-practical 수업 감사 (30 수업, 365 스텝)

Reviewer: read-only delegate, 2026-11-02. Scope is inventory.json `courses[1]` plus a liveness check of the 9 lessons in no course.

## How this was checked

- Every lesson was rendered from `courses/redesigned/<key>.json` (goal, starter, solution diff, tests, narration). Every coding step was read in full. For quiz lessons (18 to 29) I read the goal, options, answer, fields and the non-title narration lines.
- Scripts checked these for all 365 steps. Each narration `run` was compared with `tests/lesson-cases/<key>.json` `expected_outputs`, and the next `say[output]` was checked for the real value. Starter == solution: none. Unused Python imports: none. Repeated narration sentences in 3 or more steps: none. Coding steps whose narration never patches the code: 4 (D8). Glued-spacing typos were found with a regex (D9).
- I worked out C starter outputs by hand from the code. This checkout has no gcc, and the root's baseline validator run is green. I did not run any Java or Python myself.
- Visualizer facts used: `Task::code_flow_availability` (Java/Python Ready on all OS, C Ready on Windows and macOS, macOS still under verification, Linux unsupported). The C tracer shows stack, globals/static locals, arrays cell by cell (`ARRAY`), pointers by target name (`C_PTR "stock"`), heap blocks, and freed memory (`C_NOTE … 해제된 동적 메모리`) (assets/c-trace/c_instrument.py:357-380). Python lists, dicts and instances are shown element by element. The Java viewer shows stack, objects and statics.

### Cross-cutting gates for every C/Python APPLY below

1. **Builder gate.** `tools/build-redesigned-git.py:112` rejects any narration `code_flow` whose task language is not `java`. The same gate is at `examples/validate_redesigned_lesson.rs:156` (decisions.tsv row 3). C and Python APPLY items cannot be authored until this is lifted.
2. **Linux C.** `assets/layout/agent.js:1019-1020` throws `이 미션에는 코드 흐름 보기가 없습니다` when the `.code-flow-open` button is absent. On Linux every C step lacks it, so a C narration with `code_flow` would fail mid-narration. Either agent.js has to skip `code_flow` actions when availability is not ready, or the C APPLY items stay HOLD for Linux.
3. **macOS C** is still under the 79-step verification run. Treat C APPLY as Windows-first until that passes.

Verdict legend: APPLY / NOT-APPLY / IMPOSSIBLE / HOLD, as defined in the brief. "W/M/L" is Windows/macOS/Linux availability.

---

## 1. engineer-c-start

Goal: 변수 이름·저장값·출력, 대입 시점. 7 steps, C, W/M ready, L unsupported. Progression: print a variable → assign → copy → copy+compute → order → final. It is clean and has one concept per step.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 printf count | %d placeholder | ok (unit premise names stock, the step uses count; cosmetic) | NOT-APPLY |
| 1.1.2 printf stock | same concept again (practice) | ok | NOT-APPLY |
| 1.1.3 stock = counted | assignment | ok | NOT-APPLY |
| 2.1.1 int shown = stock | copy at that moment | ok | NOT-APPLY (output `5 2` already shows it) |
| 2.1.2 shown = stock + 1 | value, not formula | ok | NOT-APPLY |
| 2.1.3 swap two lines | execution order | ok | NOT-APPLY |
| 2.2.1 final | same swap as 2.1.3 | defect D3, minor D12, D20 | NOT-APPLY |

Defects:
- D3: U2.2 premise says 「지금 출력은 8 5 5여야 해요」. The starter prints `8 8 5`.
- minor D12: the 2.2.1 caution 「stock이 바뀌어도 이미 복사한 before 값은 함께 바뀌지 않아요」 warns about `before`. The mistake in this step is copying `after` too early.
- minor: the 2.2.1 solution has no explanatory comment. Every earlier solution has one, and content-rules asks for rich comments.
- D4: objective 3 「주어진 짧은 코드의 순서에 따라 결과를 답해요」 promises an answer step that does not exist.

Plan: P2. The final challenge repeats the 2.1.3 line swap instead of combining copy and order.

## 2. engineer-c-conditions

Goal: 몫·나머지, 비교, if/else, 0·비영. 9 steps. The progression is good.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 stock / group | integer division | ok | NOT-APPLY |
| 1.1.2 % | remainder | ok | NOT-APPLY |
| 1.1.3 >= gives 1/0 | comparison value | ok | NOT-APPLY |
| 1.1.4 if | branch | ok | NOT-APPLY |
| 2.1.1 else | else path | ok | **APPLY** |
| 2.1.2 딱 세 개도 포장해요 | boundary > vs >= (debug) | minor D17 「포장 수가 영으로 나와요」 (write 0); minor D19 (the last outputs do not state values); 할 일 「문제가 말한 한 곳을 고치세요」 is vague (D16) | NOT-APPLY |
| 2.1.3 if (stock) | truthiness | ok | NOT-APPLY |
| 2.1.4 group - left | == vs = | ok | NOT-APPLY |
| 2.2.1 final | div + mod + boundary | D3, D6 (ternary), D20 | NOT-APPLY |

APPLY 2.1.1: after the patch, `code_flow` on line `packs = 0;`, event `step_line`, nth 1, target `flow_line`. The viewer shows execution jumping from `if (stock >= group) {` straight into else without ever visiting `packs = stock / group;`. The narration currently only infers 「if 안을 건너뛰었고」 from the output.

Defects:
- D3: U2.2 premise 「지금 답은 2 1이에요」. The starter prints `3 1`.
- D6: the 2.2.1 solution uses `stock % size == 0 ? 0 : …`, but `?:` is never taught here (it is first explained in engineer-mixed 1.1.2). Output tests accept if/else, so this is minor.
- D20: two patches before one run.
- D4: objective 3 「짧은 코드의 경계 결과를 읽고 답해요」 has no answer step.

## 3. engineer-c-arrays

Goal: 위치·원소·개수, 반복, 문자 배열. 11 steps.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 bins[0] | index from 0 | ok | NOT-APPLY |
| 1.1.2 sizeof | element count | ok | NOT-APPLY |
| 1.1.3 index + 1 | variable index | ok | NOT-APPLY |
| 1.1.4 for total += | accumulate | ok | NOT-APPLY (1.1.6 shows loop state better) |
| 1.1.5 while | while form | ok | NOT-APPLY |
| 1.1.6 remove total = 0 | accumulator reset bug | ok | **APPLY** |
| 1.1.7 count > 0 guard | divide by zero | ok | NOT-APPLY |
| 2.1.1 strlen vs sizeof | NUL terminator | ok | **APPLY** |
| 2.1.2 label[0] = 'F' | char element | **defect D1**; minor D19 | NOT-APPLY |
| 2.1.3 count - 1 bound | off-by-one (debug) | minor: the caution 「반복은 개수보다 작은 위치까지만 읽어요」 states a fact, not a mistake; D19 | NOT-APPLY |
| 2.2.1 final | sum + first max | D3, D6, D20 | NOT-APPLY |

APPLY 1.1.6: on the starter, before the patch, `code_flow` on line `total = 0;`, event `step_line`, nth 2, target `flow_stack`. It shows total=2 carried into the second iteration and then wiped to 0. The output `6` only lets the student infer this.

APPLY 2.1.1: after the patch, `code_flow` on line `printf("%d\n%d", cells, letters);`, `step_line`, target `flow_memory`. `label` is drawn as `char[8]` with cells B, O, X, the NUL, and four empty cells. The student sees why sizeof gives 8 and strlen gives 3.

Defects:
- **D1 (defect)**: in 2.1.2 the narration patches `"BOX"` to `"BAG"` and says 「이번에도 첫 글자만 바뀌어 FAG가 나왔어요」. A grader variation also expects `FAG`. "FAG" is an English slur, and it appears on screen and in TTS. Sources: `tools/redesigned_lessons/engineer_c_arrays/content.json:631-714`, `tests/lesson-cases/engineer-c-arrays.json:41`. Use another word, such as `"BIN"` → `FIN`.
- D3: U2.2 premise 「지금 답은 24 1이에요」. The starter prints `9 2`.
- D6: the 2.2.1 solution introduces `i++`, `+=`, a braceless `if`, `int total = 0, best = 0;`, and max-index tracking. None of these were taught in this lesson.
- D20: three patches before one run.
- minor: U1.1 and U2.1 share the same premise text word for word.

## 4. engineer-c-functions

Goal: 인수 복사·반환·이름 범위, static, 재귀. 11 steps. Six tasks are already `code_flow: true`.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 return value + 1 | return | ok | NOT-APPLY |
| 1.1.2 copy value | pass by value | ok | NOT-APPLY (1.1.4 covers it more strongly) |
| 1.1.3 store return | assign return | ok | NOT-APPLY |
| 1.1.4 local stock = 10 | same name, different frame | minor: the starter uses `scanf("%d", &stock)` before `&` is taught (lesson 5) | **APPLY** |
| 1.1.5 static calls | static local | `i++` first appears here in the starter | **APPLY** |
| 1.1.6 global stock | global | ok | NOT-APPLY |
| 2.1.1 base case | recursion end | minor D13: this starter already contains `return n + sum_to(n - 1);`, which is 2.1.2's answer | NOT-APPLY (the starter overflows the stack) |
| 2.1.2 n + sum_to(n - 1) | recursive return | ok | **APPLY** |
| 2.1.3 print after call | unwind order | ok | **APPLY** |
| 2.1.4 빈 합은 무엇일까요 | base value (debug) | typo D9 「0이상5이하의」 in the starter comment; D16; D19 | NOT-APPLY |
| 2.2.1 final | recursion + static | D3, D6, minor D14 | NOT-APPLY |

APPLY 1.1.4: on the solution, `code_flow` on line `return stock + value;`, `step_line`, target `flow_stack`. The `adjusted` frame (stock=10, value=2) sits above the `main` frame (stock=2). Two cells share one name, which the output cannot show.

APPLY 1.1.5: on the solution, `code_flow` on line `calls = calls + 1;`, `step_line`, nth 2, target `flow_memory` (the static local is registered as static). On the second call, calls is already 1 on entry. The starter shows 0 at the same nth.

APPLY 2.1.2: on the solution, `code_flow` on line `return 0;`, event `return`, target `flow_stack`. At the deepest point, sum_to(3), sum_to(2), sum_to(1) and sum_to(0) are all live frames. Then the narration can say each return adds n on the way back.

APPLY 2.1.3: on the solution, `code_flow` on the second `printf("%d", n);` (line 10, after the recursive call), `step_line`, nth 1, target `flow_stack`. visit(0) is on top of visit(1) and visit(2), so the output starts 0 1 2 on the way back.

Defects:
- D3: U2.2 premise 「지금 출력은 10 3이에요」. The starter prints `0 0`.
- D9: U1.1 premise 「같은 재고2개를」. U2.1 premise 「입력은0이상5이하로」.
- D6: the final uses `calls++` and a braceless `if`.
- D14: `static int calls` in the final is dead code. It is incremented and never printed, so it distracts from the recursion task.
- D4: objective 3 「…짧은 결과로 답해요」 has no answer step.

## 5. engineer-c-pointers

Goal: 포인터 값 vs 대상 값, 재대입·간접 대입·배열 이동, 함수 전달. 11 steps. Several tasks are `code_flow: true`. Progression: read *p → write *p → copy pointer → retarget → arithmetic → ++ → function → NULL → debug → swap. It is good.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 *p read | dereference | ok | NOT-APPLY |
| 1.1.2 *p = fresh | write through | ok | NOT-APPLY |
| 1.1.3 int *q = p | alias | ok | **APPLY** |
| 1.1.4 p = &other | retarget vs write | ok | **APPLY** |
| 1.1.5 *(p + 1) | pointer arithmetic | ok | NOT-APPLY |
| 1.1.6 p++ vs (*p)++ | move vs value | ok | NOT-APPLY (the output `5 2` already shows it) |
| 2.1.1 p = redirect(...) | pointer copied into callee | ok | **APPLY** |
| 2.1.2 *p = *p + 1 in add | write through param | ok | NOT-APPLY (2.1.1 carries the frame view) |
| 2.1.3 NULL check | NULL | ok | NOT-APPLY |
| 2.1.4 복사 대신 원래 재고 | debug | D16, D19 | NOT-APPLY |
| 2.2.1 swap | final | D3 | NOT-APPLY |

APPLY 1.1.3: on the solution, `code_flow` on line `*q = 7;`, `step_line`, target `flow_stack`. Both p and q show `→ stock`. The output `7 7 9` shows the effect, not the shared target.

APPLY 1.1.4: run it on the starter and on the solution, on line `printf("%d\n%d", *p, stock);`, `step_line`, target `flow_stack`. The starter shows p → stock with stock=7. The solution shows p → other with stock=2.

APPLY 2.1.1: on the starter, `code_flow` on line `return p;`, `step_line`, target `flow_stack`. The redirect frame's p → other, while main's p → stock. Two pointer copies with different targets are only visible here.

Defects:
- D3: U2.2 premise 「지금 결과는 8 3이에요」. The starter prints `3 3`.

## 6. engineer-c-double-pointers

Goal: pp·*pp·**pp 층. 9 steps. One layer per step, which is good.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 **pp read | two hops | ok | NOT-APPLY |
| 1.1.2 **pp = fresh | write final | ok | NOT-APPLY |
| 1.1.3 *pp = &other | change p via pp | ok | **APPLY** |
| 1.1.4 pp = &q | change pp only | ok | **APPLY** |
| 2.1.1 *target = other | caller's pointer | ok | **APPLY** |
| 2.1.2 **(pp + 1) | pointer array | ok | NOT-APPLY |
| 2.1.3 *(*pp + 1) | array via pp | ok | NOT-APPLY |
| 2.1.4 원래 재고에 두 번 따라가 써요 | debug | minor D21: the patch `stock = 5;` → `stock = 2;` has an empty `say`; D16, D19 | NOT-APPLY |
| 2.2.1 final select_min | layer choice | D3, D6 | NOT-APPLY |

APPLY 1.1.3 and 1.1.4, as a pair. Both solutions print exactly `9` and `2`, yet they change different layers. That is the textbook case where the viewer beats the output. Use `code_flow` on the printf line, `step_line`, target `flow_stack`. In 1.1.3 it shows pp → p → other. In 1.1.4 it shows pp → q → other while p → stock.

APPLY 2.1.1: on the solution, `code_flow` on line `*target = other;`, `step_line`, target `flow_stack`. The redirect frame's target points at main's cell `p`. A second `code_flow` on main's printf shows p → other.

Defects:
- D3: U2.2 premise 「…지금 1 2 8이에요」. The starter prints `0 2 2`.
- D6: `(int)(chosen - bins)` (pointer subtraction with a cast) and `&bins[i]` are new in the final.

## 7. engineer-c-structures

Goal: 구조체 복사/포인터, 함수 포인터, 비트 연산, 동적 메모리 수명. 19 steps across 4 chapters and 5 objectives. This is the most overloaded lesson in the course (P1).

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 item.code | field | ok | NOT-APPLY |
| 1.1.2 Stock b = a | struct copy | ok | NOT-APPLY |
| 1.1.3 p->count | pointer to struct | ok | **APPLY** |
| 1.1.4 items[1].count | array of struct | ok | NOT-APPLY |
| 1.1.5 Label copy | array inside struct copied | ok | NOT-APPLY |
| 2.1.1 rule = add_one | function pointer | two edits in one step, but ordered in 할 일 | NOT-APPLY |
| 2.1.2 apply(rule) | fn pointer argument | ok | **APPLY** |
| 2.1.3 요구한 계산 규칙을 골라요 | debug | D16, D19 「선택한 함수와 실제 결과를 확인했어요」 | NOT-APPLY |
| 3.1.1–3.1.6 & && \| ^ << ~ | bit ops | ok; 할 일 「결과가 바뀌었는지 확인하세요」 gives no expected value (D16) | NOT-APPLY (the viewer shows decimal ints, no bits) |
| 4.1.1 malloc + *p = stock | allocation | ok | NOT-APPLY |
| 4.1.2 calloc | zeroed | ok | NOT-APPLY (optional: heap block [0,4,0]) |
| 4.1.3 int *q = p (heap) | alias of allocation | ok | **APPLY** |
| 4.1.4 NULL all aliases | dangling after free | ok | **APPLY** |
| 4.2.1 final price rules | struct + fn ptr | D3, D6 (ternary), D20 | NOT-APPLY |

APPLY 1.1.3: on the solution, `code_flow` on the printf line, `step_line`, target `flow_stack`. p → item, item.count=5, other.count=4.

APPLY 2.1.2: on the solution, `code_flow` on line `return value + 1;` (inside add_one), event `call`, nth 1, target `flow_stack`. The stack is main → apply(value=2, rule → 함수 add_one) → add_one(value=2). The student sees the parameter holding a function.

APPLY 4.1.3: on the solution, `code_flow` on line `printf("%d\n", *p);`, `step_line`, target `flow_memory`. p and q both point to one heap block, and `other` is untouched.

APPLY 4.1.4: on the starter, `code_flow` on line `int cleared = 0;`, `step_line`, target `flow_stack`. p is NULL and alias[0] is NULL, while alias[1] and alias[2] are drawn as `해제된 동적 메모리 (따라가지 않음)`. Dangling pointers are invisible in the output `1 1`.

Defects:
- D3: U4.2 premise 「지금 출력은 220이에요」. The starter prints `240`.
- D6: `sale ? half : normal` (ternary not taught). D20: two patches before one run.

Plan: P1. Split this lesson, for example structs plus fn pointers, then bit ops, then the heap lifecycle. The U4.2 final sits in the memory chapter but uses no malloc at all.

## 8. engineer-java-flow

Goal: 형·연산·조건·반복 순서, 기본형 전달. 9 steps. Java, ready on W/M/L.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 (double) cast | int division | ok | NOT-APPLY |
| 1.1.2 "sum=" + (a+b) | string concat | ok | NOT-APPLY |
| 1.1.3 ++stock | pre vs post | ok | NOT-APPLY |
| 1.1.4 && order | short circuit | ok | NOT-APPLY (the tracer is line-level and cannot show sub-expression skipping) |
| 2.1.1 switch break | fallthrough | ok | NOT-APPLY (`BC` shows it) |
| 2.1.2 continue | continue | ok | NOT-APPLY |
| 2.1.3 stock = add(stock) | primitive copy | minor D7: 할 일 4 「코드 흐름 보기를 눌러…」 but the narration has no code_flow | **APPLY** |
| 2.1.4 for-each + twice | combine | ok | NOT-APPLY |
| 2.2.1 final | break/continue | D3, D19, D20 | NOT-APPLY |

APPLY 2.1.3: on the starter, `code_flow` on line `static int add(int value) { return value + 1; }`, event `call`, target `flow_stack`. The add frame (value=3) sits above main (stock=3). Then `step_line` on `System.out.println(stock);` shows stock still 3 after the 4 was discarded. This also closes the 할 일/narration gap.

Defects:
- D3: U2.2 premise 「지금 답은 6이에요」. The starter prints `0`.
- D4: objective 3 「짧은 코드의 출력값을 직접 답안으로 적어요」 and U2.1 premise 「마지막에는 출력 숫자를 직접 적어요」 name a step that does not exist.

## 9. engineer-java-references

Goal: 참조 복사 vs 대상 복사, 필드 수정 vs 재대입, String/==/null. 9 steps. 1.1.1 and 1.1.3 already have code_flow (5 actions). Their lines and events are plausible and the validator replays them.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 a.clone() | array reference | ok | existing APPLY, keep |
| 1.1.2 b[0] = a[0].clone() | shallow outer copy | D7: 할 일 2 asks for code flow, the narration does not show it | **APPLY** |
| 1.1.3 value.count = next | param field write | ok | existing APPLY, keep |
| 1.1.4 a = replace(...) | param reassignment | D7 (할 일 2) | **APPLY** |
| 2.1.1 a = a + "!" | immutable String | ok | NOT-APPLY |
| 2.1.2 equals | == vs equals | ok | NOT-APPLY (output; String identity rendering is unverified) |
| 2.1.3 && null | short circuit | ok | NOT-APPLY |
| 2.1.4 reorder b moves | alias then rebind | ok | **APPLY** |
| 2.2.1 final source.clone() | array shared by objects | D3, D6 (`static class`) | NOT-APPLY (optional: three refs to one array) |

APPLY 1.1.2: on the starter, `code_flow` on line `b[0][0] = 7;`, `step_line`, target `flow_memory`. Two outer arrays both have their [0] cell pointing at the same inner {2, 4}. After the patch, b[0] points at a new inner array.

APPLY 1.1.4: on the starter, `code_flow` on line `return value;` in replace, event `return`, target `flow_memory`. replace's value → Stock(9) while main's a → Stock(2).

APPLY 2.1.4: run it on the starter and on the solution, on the println line, `step_line`, target `flow_memory`. In the starter, the added 3 lands in the new object (12) and a's object stays 2. In the solution, the shared object becomes 5 before b moves.

Defects:
- D3: U2.2 premise 「지금 출력은 2 5 2예요」. The starter prints `5 5 5`.
- D4: U2.1 title 「내용 비교와 참조 비교 뒤 결과를 답해요」 has no answer step.

## 10. engineer-java-static

Goal: static vs instance, 초기화 순서. 9 steps. Only 1.1.3 has code_flow, but seven steps' 할 일 tell the student to press 코드 흐름 보기.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 Ticket.total | class variable | D7 (할 일 3) | NOT-APPLY (output shows no `new ticket`); resolve D7 |
| 1.1.2 b.local++ / total++ | instance vs static | D7 (할 일 5) | **APPLY** |
| 1.1.3 new Ticket() | constructor count | ok | existing APPLY, keep |
| 1.1.4 static order | default 0 before init | D7 (할 일 2) | **APPLY** |
| 2.1.1 static block once | class init | D7 (할 일 4) | NOT-APPLY (`SICIC`); resolve D7 |
| 2.1.2 extends Parent | init order | D7 (할 일 4) | NOT-APPLY (`PCp1c2`); resolve D7 |
| 2.1.3 static int total | field moves to class | D7 (할 일 4) | **APPLY** |
| 2.1.4 id = next++ order | shared counter | ok | NOT-APPLY |
| 2.2.1 final | counter + alias | D3, D6 (`static class`), D19 | NOT-APPLY |

APPLY 1.1.2: on the solution, `code_flow` on the println line, `step_line`, target `flow_statics`. Ticket.total=2 lives in statics, while objects a and b each hold local=1.

APPLY 1.1.4: on the starter, `code_flow` on line `static int read() { return b; }`, event `call`, nth 1, target `flow_statics`. Both a and b are still 0 when read() runs. This is the "default value first" fact the output `0:7` can only imply.

APPLY 2.1.3: run it on the starter and on the solution, on the println line, `step_line`. The starter shows a total field inside each object (a=2, b=0). The solution shows total in statics, with objects holding only `local`.

Defects:
- D3: U2.2 premise 「지금 출력은 1 1 2 2예요」. The starter prints `0 0 0 0`.
- D7: four steps (1.1.1, 2.1.1, 2.1.2, plus the three APPLY steps until they are authored) tell the student to press 코드 흐름 보기 with no matching narration. voice.md:62 says 「해설도 할 일의 순서와 대응시킨다」. For the NOT-APPLY ones, either drop that 할 일 line or add a one-sentence code_flow.

## 11. engineer-java-polymorphism

Goal: 필드/static/오버로드/오버라이딩 선택, 생성 중 호출, 예외·finally. 9 steps. 2.1.1 already has 3 code_flow actions, and they are good.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 override value() | dynamic dispatch | D7 (할 일 4) | NOT-APPLY (`7`); resolve D7 |
| 1.1.2 ((Bonus) rule).count | field hiding | D7 (할 일 4) | **HOLD**: need to verify that the Java viewer draws both `count` fields of one Bonus object distinguishably |
| 1.1.3 Bonus.name() | static hiding | D7 (할 일 4) | NOT-APPLY (`P`/`C` already names the class); resolve D7 |
| 1.1.4 overload by declared type | overload | ok | NOT-APPLY |
| 2.1.1 show() during ctor | init order | ok | existing APPLY, keep |
| 2.1.2 catch | exception path | ok | NOT-APPLY |
| 2.1.3 return after finally | return value fixed before finally | the `System.out.print("")` placeholder in try is awkward (minor) | **APPLY** |
| 2.1.4 super.value() | super call | ok | NOT-APPLY |
| 2.2.1 final | field + override + finally | D4 premise, D20; edits exceed 3 lines (5-line try/finally) | NOT-APPLY |

APPLY 2.1.3: on the starter, `code_flow` on line `System.out.print("F");` inside finally, `step_line`, target `flow_stack`. choose's value is already 9. Then an event `return` code_flow on choose shows the return value is still 2. The validator must confirm which line the JVM attributes the return to. The hidden "return value captured before finally" state is exactly what the output `F2` cannot explain.

Defects:
- D4: U2.2 premise 「각 답안에는 해당 출력만 적으세요」 and U2.1 premise 「합계를 직접 답해요」 refer to answer fields that do not exist. Objective 3 「…출력 결과를 직접 답해요」 has the same problem.

## 12. engineer-python-values

Goal: 슬라이스, 공유/복사, 집합·사전. 9 steps. Python, ready everywhere.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 [start:end] | slice end exclusive | ok | NOT-APPLY |
| 1.1.2 [::step] | step | ok | NOT-APPLY |
| 1.1.3 [::-1] | reverse | ok | NOT-APPLY |
| 1.1.4 stocks.copy() | alias vs copy | ok | **APPLY** |
| 2.1.1 copy.deepcopy | shared inner list | ok | **APPLY** |
| 2.1.2 & and \| | sets | minor: two new operators in one step | NOT-APPLY |
| 2.1.3 get(item, 0) | dict default | ok | NOT-APPLY |
| 2.1.4 split/join | strings | ok | NOT-APPLY |
| 2.2.1 final | nested copy + get | D3, D6 (list comprehension), D19 | NOT-APPLY |

APPLY 1.1.4: on the starter, `code_flow` on the line `print(stocks)`, `step_line`, target `flow_memory`. stocks and backup both point at one list [2, 4, 6].

APPLY 2.1.1: on the starter, `code_flow` on the line `print(rows)`, `step_line`, target `flow_memory`. rows and backup are two outer lists whose first slot points at the same [2, 6]. After the patch, the inner lists are distinct.

Defects:
- D3: U2.2 premise 「지금 출력은 1 9와 0 False예요」. The starter prints `9 9` / `1 False`.
- D6: the 2.2.1 solution `[row[:] for row in rows]` relies on a list comprehension that was never taught (the lesson taught `copy.deepcopy`). Its 할 일 does not give the syntax.
- D4: objective 3 and U2.1 「…결과를 직접 답해요」.

## 13. engineer-python-calls

Goal: 인수·이름 범위·공유 상태, 클래스, 예외, 재귀, 가변 인수. 11 steps.

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1 size=2 | default arg | ok | NOT-APPLY |
| 1.1.2 items=[] shared | mutable default | ok | **APPLY** |
| 1.1.3 append vs rebinding | mutation vs rebind | ok | **APPLY** |
| 1.1.4 Counter.total | class vs instance attr | ok | **HOLD**: verify the tracer draws class attributes. The instance's own `total` would show, but the class value may not |
| 1.1.5 super().value() | super | ok | NOT-APPLY |
| 2.1.1 global | scope | ok | NOT-APPLY |
| 2.1.2 finally | finally | ok | NOT-APPLY |
| 2.1.3 n * multiply(n-1) | recursion | ok | **APPLY** |
| 2.1.4 keyword args | kwargs | ok | NOT-APPLY |
| 2.1.5 *stocks | varargs | the caution 「…목록 하나를 넘기는 호출과 섞으면 받는 방식이 달라져요」 is vague (minor) | NOT-APPLY |
| 2.2.1 final | default None | D6 (`*,` keyword-only, `is None`), D19, D20 | NOT-APPLY |

APPLY 1.1.2: on the solution, `code_flow` on line `print(first is second)`, `step_line`, target `flow_memory`. first and second point at the single list [2, 4], which is the function's default object.

APPLY 1.1.3: on the starter, `code_flow` on line `items = items + [value]`, event `return` (add returning), target `flow_memory`. add's items points at a new [2, 4] while the module's stocks still points at [2].

APPLY 2.1.3: on the solution, `code_flow` on line `return 1`, event `return`, target `flow_stack`. multiply(4), (3), (2) and (1) are all stacked at the base case.

Defects:
- D4: objective 3 「필답형에 필요한 짧은 결과를 직접 답해요」 and the CH2/U2.1 objectives 「…결과를 직접 답해요」.

## 14. engineer-db-model

9 steps. 1.1.1–1.1.4 are SQL (IMPOSSIBLE). 2.1.1–2.2.1 are Python wrapping sqlite3 (Ready).

| Step | Concept | Correctness | Visualizer |
|---|---|---|---|
| 1.1.1–1.1.4 | columns, COUNT DISTINCT, NULL, JOIN | 1.1.4 first output does not state rows (D19) | IMPOSSIBLE (SQL) |
| 2.1.1 PRIMARY KEY | PK | ok | NOT-APPLY (the effect lives in the DB; the sqlite3 Connection is opaque) |
| 2.1.2 NOT NULL | | ok | NOT-APPLY |
| 2.1.3 REFERENCES | FK | ok | NOT-APPLY |
| 2.1.4 composite PK | | ok | NOT-APPLY |
| 2.2.1 final | all three | D20 (two patches, one run) | NOT-APPLY |

Minor:
- The U1.1 premise 「ID1/2의 pen과 ID3의 book」 has glued spacing, and U1.1 and U2.1 share it word for word.
- Objective 3 「기본 DDL이 보장하는 것과 업무 규칙을 나눠요」 has no step that shows a rule DDL cannot express. Only the 2.1.2 caution about `''` touches it.

Plan P9: in 2.1.x a roughly 30-line Python harness wraps a one-keyword SQL edit. Consider collapsing or labelling the harness.

## 15. engineer-sql-select

11 steps, all SQL, IMPOSSIBLE. Correctness: the outputs match lesson-cases. Progression: WHERE → IS NULL → precedence → LIKE → BETWEEN → DISTINCT → LEFT JOIN → EXISTS → NOT EXISTS → debug → final. This is good.

Defects and minor:
- D8: the 2.1.5 「재주문할 물건을 빠짐없이 찾아요」 narration diagnoses `stock = NULL`, runs, and stops. It never patches `IS NULL` or shows the fixed result.
- D9: U1.1/U2.1 premise 「ID1 pen/재고2/A/공급처10 … 공급처30에는」 is glued, dense, and duplicated.
- D20: 2.2.1 applies two patches before one run.
- D19: the 2.1.2 and 2.2.1 output lines do not state the rows.

## 16. engineer-sql-group

11 steps, SQL, IMPOSSIBLE. COUNT/SUM/AVG/NULL, GROUP BY, HAVING, WHERE vs HAVING, DISTINCT in COUNT, RANK, PARTITION, running window, debug, final. The outputs are consistent.

- D8: the 2.1.5 「묶은 뒤의 합계로 골라요」 narration stops before the fix.
- D20/D19: 2.2.1 patches several lines and the final output line does not list rows (「양수만 집계해 C와 A를 남기고…」).

## 17. engineer-sql-change

11 steps: 9 SQL (IMPOSSIBLE) and 2 SQL choice (hidden). INSERT/UPDATE/DELETE WHERE, transactions, savepoints, INSERT…SELECT, NULL debug, GRANT/REVOKE choice, final.

- D8: 2.1.3 「모르는 재고만 0으로 정해요」 and 2.1.4 「모르는 재고는 남기고 지워요」 both stop after diagnosis.
- D9: U3.1 premise 「PostgreSQL18 명령 자료」.
- The 3.2.1 final is fine. Its 할 일 「다시 실행해 결과를 확인하고 작성한 코드를 제출하세요」 bundles two actions (voice.md: one action per item). This bundling is systematic in all finals.

## 18. engineer-db-storage

19 steps: 16 choice, 2 fill, 1 fill_fields, all hidden, IMPOSSIBLE. 1NF→5NF, physical design, index, plan, denormalization, view/function/procedure/trigger. The answers are correct. I checked BCNF 2.1.2: PR→M and M→R with keys PR and PM give 3NF, not BCNF, so "third" is right.

- D9: options 「아니요.모든 합법 자료에」, 「아니요.후보키는」, 「아니요.비자명 다치 종속이4NF」, 「네.원래 행을」, 「아니요.갑·남과을·북이라는」 (also missing the space in 「남과 을」), 「직접CALL해야만」, 「같은SQL의」, and the 5.1.2 goal 「PostgreSQL18」.
- D10: 5.1.3 option 「학생이 매번 트리거 이름을 직접CALL해야만 해요」. The actor is not a student.
- Minor: 2.1.2 question 「BCNF까지 중 최고 정규형은」 is awkward; 「BCNF까지 중에서」 reads better.
- P5: several 「조심하세요」 lines are policy statements (「…단정하지 않아요」).

## 19. engineer-requirements

9 steps: 8 choice and 1 fill_fields, hidden, IMPOSSIBLE.

- D9: 「같은10개 동시 요청에서 응답1초 이내」, 「「수량 정정」과「동시 요청에서1초 이내」」, 「전자는 기능,후자는」, 「기간이7일에서30일로」.
- P5 strawmen: 1.1.4 「구현 코드가 있으니 요구도 검증된 거예요」 and 2.1.3 「테스트가 모두 통과했으니 요구도 맞아요」.
- The answers are correct.

## 20. engineer-design

28 steps: 25 choice, 2 fill, 1 fill_fields, IMPOSSIBLE. UML views plus 23 GoF patterns. The answers are correct. Cross-references such as 「6번의 추상 팩터리」, 「12번의 컴포지트」, 「17번」 and 「18번」 match global step order.

- D15: the 4.1.8 fill expects 「상태」 and 4.1.9 expects 「전략」. Neither pattern was introduced in an earlier step (Strategy first appears as a distractor in 4.1.10, after these). Recall of untaught names is a prerequisite gap.
- D18 (maintainer-only): option ids do not match their text in 2.1.1 `abstract`, 2.1.4 `prototype`→추상 팩터리, 3.1.1 `facade`, 3.1.4 `proxy`→컴포지트, 4.1.1 `observer`→데코레이터, 4.1.2 `memento`→책임 연쇄, 4.1.3 `iterator`→커맨드, and 4.1.4 `visitor`→컴포지트. This is not learner-visible.
- D9: objective 2 「생성5·구조7·행위11」.
- P4: 28 recognition-only steps make one lesson.

## 21. engineer-server

23 steps: 9 choice, 13 fill, 1 fill_fields, IMPOSSIBLE. The cohesion/coupling, environment, baseline and batch content is correct. The coupling and cohesion orders are given in the 3.1.1 and 3.1.6 goals before recall, which is good.

- P5: many 「조심하세요」 lines are policy statements (「…가정하지 않아요」, 「…모든 분리가 개선은 아니에요」).

## 22. engineer-interfaces

11 steps, IMPOSSIBLE. Units, types, accepted vs done, required fields, compatibility, timeout, idempotency, dedupe, correlation, contract tests, final.

- D9: 「한쪽 수량3은」, 「"3"과3을」, 「재고를7로 맞춤」, 「같은7이에요」, 「아니요.접수와 완료」, 「아니요.처리됐지만」, 「재고를1 증가」.
- P4: 2.1.2/2.1.3 (set vs increment idempotency) would make a strong small Python run step.

## 23. engineer-ui

9 steps, IMPOSSIBLE.

- D10: the 2.1.2 goal 「검토 화면으로 이동했는데 학생이 저장 완료라고 생각해요」. The persona is 점원.
- D9: 「수량10을」, 「수량은1~9개라고」, U1.1 premise 「허용 범위는1~9예요」, 「점원이1~9개」.

## 24. engineer-test-cases

9 steps, IMPOSSIBLE.

- D9: the U1.1 premise 「수량은 정수1~9만 허용해요.0 이하와10 이상은」 and the 1.1.1 goal 「입력10을」.
- P4: boundary values (1.1.3/1.1.4, 2.2.1) suit a Python step that runs the real `accept()` against boundary inputs.

## 25. engineer-test-integration

11 steps, IMPOSSIBLE. Stub/driver, coverage, cyclomatic complexity, performance comparison. Answers checked: 2.1.4 V = 6 − 5 + 2 = 3.

- D9: 2.1.1 「A·B만 지나고C는」.
- D11: the U3.2 premise ends 「…셉니다」 (합니다체; voice.md:12 forbids it).
- **P4, strongest conversion candidate**: CH2 asks for statement and branch coverage on an imaginary program. A Python step with a 5-line `if` plus code_flow (Python Ready) would let the student see which lines and branch outcomes ran. That beats counting from prose.

## 26. engineer-security

15 steps, IMPOSSIBLE. The authn/authz, SQLi, XSS, hashing and signature answers are correct.

- D10: the 2.1.4 question 「학생 화면에 보여 줄 내용은」. The persona is the end user.

## 27. engineer-os

15 steps: 14 quiz steps (IMPOSSIBLE) and 1 Python final (3.2.1, Ready). FCFS/SJF/RR, paging, FIFO/LRU, deadlock. The quiz answers are correct.

| Step | Correctness | Visualizer |
|---|---|---|
| 1.1.1–3.1.4 quiz | ok | IMPOSSIBLE (hidden) |
| 3.2.1 SJF + FIFO code | **defect D2** | **APPLY** |

**D2 (defect)**: the U3.2 premise says 「빈 프레임 3개에서 참조열 1,2,3,1,4,2를 FIFO로 처리해요」. The code and tests use `refs = [1, 2, 3, 4, 1, 2]`. With the premise's sequence, FIFO gives 4 faults. The graded answer and the narration (「페이지 부재는 6이에요」) use the code's sequence. Source: `tools/redesigned_lessons/engineer_os/content.json:769`.

APPLY 3.2.1: run it on the starter and on the solution, `code_flow` on line `memory.append(page)`, `step_line`, nth 4 (the first eviction), target `flow_memory`. After `pop()`, memory is [1, 2] because 3 was removed. After `pop(0)`, memory is [2, 3]. The output only shows a fault count, while the viewer shows which page left.

## 28. engineer-network

15 steps: 14 quiz steps (IMPOSSIBLE) and 1 Python final (2.2.1). The subnet math and layer answers are correct, and the final's narration outputs (`0.0.0.0, 0.0.0.0, -1`, then `.64 .95 30`) match.

- 2.2.1: NOT-APPLY. The viewer shows ints in decimal, so the bit operations stay invisible.
- D9: 1.1.8 「RFC3021」.

## 29. engineer-build

11 steps, IMPOSSIBLE. The SemVer answers are correct (1.10.0 > 1.9.9 handled).

- D9: U2.1 premise 「SemVer2.0.0」.
- D11: the U2.2 premise and 2.2.1 goal use 「SemVer를 따릅니다」 (합니다체).

## 30. engineer-mixed

15 steps: C 2, Java 2, Python 3 Ready, SQL 3 IMPOSSIBLE, 5 quiz hidden. It is a review lesson.

| Step | Correctness | Visualizer |
|---|---|---|
| 1.1.1 p++ | ok | NOT-APPLY (already covered in lesson 5) |
| 1.1.2 ternary recursion | ok; this is the first place `?:` is explained | NOT-APPLY |
| 1.1.3 static count | ok | NOT-APPLY |
| 1.1.4 override read() | ok | NOT-APPLY |
| 1.1.5 nested copy | list comprehension given in 할 일 | NOT-APPLY (lesson 12 carries it) |
| 1.1.6 // and % | ok | NOT-APPLY |
| 2.1.1–2.1.3 SQL | 할 일 「결과가 바뀌었는지 확인하세요」 has no expected value (D16) | IMPOSSIBLE |
| 3.1.1–3.1.5 quiz | ok | IMPOSSIBLE |
| 3.2.1 final | D5, D6, D19 | NOT-APPLY |

Defects:
- **D5**: the U3.2 objective 「참조 공유와 NULL 집계, 수정 후 영향 검사를 서로 다른 근거로 판단해요」 and its premise 「공통 함수 수정 후 기존 주문·취소·환불 기능이 깨지지 않았는지 다시 시험해야 해요」 promise a regression-test judgement. The step only edits the copy and the None count.
- D4: objective 1 「짧은 코드와 SQL의 실제 결과를 답안으로 적어요」, U1.1 「결과 숫자나 출력 한 줄을 적으세요」 and U2.1 「조회 결과 숫자를 적으세요」 describe answer steps. The steps are code edits.
- D6: 3.2.1 `sum(1 for value in qty if value is not None)` is a generator expression that was never taught.
- D19: the second run's line 「2 5예요.」 omits the `3` count line.

---

## Lessons in no course (9)

| Key | Live? | Evidence |
|---|---|---|
| sys-page-table, sys-sliding-window, sys-buffer-pool, sys-cache-locality, sys-interpreter-env, sys-interleavings, socket-partial-frames, node-cpu-offload | No | Listed under `catalog.json` `courses[0:java].withdrawn_lessons` (`required: false`). `build.rs:50-51` compiles only `course["lessons"]` into the lesson registry, so these are not registered or bundled. `src/` has no reference. |
| java-parser | No | Not in catalog.json at all. It is referenced only as `source_lesson` in `tools/redesigned_courses/java/backend-extension-plan.json:882` and by the authoring flag in `tools/narrate.py:478`. |

---

## Defect catalogue

Severity "defect" means wrong, visible, or contradicting content. "Minor" means a rule or style violation.

| ID | Sev | What | Where |
|---|---|---|---|
| D1 | defect | Narration and a grader variation produce the word "FAG" (`"BAG"` with the first letter set to F) | c-arrays 2.1.2; content.json:631-714; lesson-cases:41 |
| D2 | defect | The premise reference string `1,2,3,1,4,2` contradicts the code's `[1, 2, 3, 4, 1, 2]`, and the answers differ (4 vs 6 faults) | engineer-os U3.2; content.json:769 |
| D3 | defect, systematic | A final-challenge premise or goal states the *target* output as 「지금 출력은/지금 답은 X」 while the starter prints something else. Instances and real starter output: c-start `8 8 5`, c-conditions `3 1`, c-arrays `9 2`, c-functions `0 0`, c-pointers `3 3`, c-double-pointers `0 2 2`, c-structures `240`, java-flow `0`, java-references `5 5 5`, java-static `0 0 0 0`, python-values `9 9/1 False` | each lesson's U*.2 premise and final goal in tools/redesigned_lessons/<x>/content.json |
| D4 | defect, systematic | Objectives or premises promise 「직접 답해요/적으세요/각 답안에는」 answer steps that no longer exist | c-start obj3, c-conditions obj3, c-functions obj3, java-flow obj3 and U2.1, java-references U2.1, java-polymorphism obj3, U2.1 and U2.2, python-values obj3 and U2.1, python-calls obj3 and CH2, engineer-mixed obj1, U1.1 and U2.1 |
| D5 | defect | The final's goal and premise promise a regression-test judgement that the step does not test | engineer-mixed U3.2 / 3.2.1 |
| D6 | minor | Finals use syntax never taught: ternary (c-conditions, c-structures), `i++`/`+=`/braceless if (c-arrays, c-functions), pointer subtraction (c-double-pointers), `static class` (java-references, java-static), list comprehension (python-values), `*,` keyword-only (python-calls), generator expression (mixed) | finals |
| D7 | minor | 할 일 tells the student to press 코드 흐름 보기 but the narration never shows it (voice.md:62) | java-flow 2.1.3; java-references 1.1.2, 1.1.4; java-static 1.1.1, 1.1.2, 1.1.4, 2.1.1, 2.1.2, 2.1.3; java-polymorphism 1.1.1, 1.1.2, 1.1.3 (12 steps) |
| D8 | minor | Debug-step narration stops after diagnosis with no fix and no fixed run, unlike every other coding step | sql-select 2.1.5; sql-group 2.1.5; sql-change 2.1.3, 2.1.4 |
| D9 | minor | Glued spacing typos: 「재고2개」 「입력은0이상5이하」 「공급처30」 「아니요.…」(×7) 「같은10개」 「응답1초」 「기간이7일에서30일로」 「기능,후자는」 「수량3은」 「"3"과3」 「재고를7로」 「같은7」 「수량10」 「1~9」(×3) 「정수1~9만 허용해요.0 이하와10」 「C는」 「PostgreSQL18」(×2) 「RFC3021」 「SemVer2.0.0」 「직접CALL」 「같은SQL」 「남과을」 | listed per lesson above |
| D10 | minor | 「학생」 used for the in-story user | db-storage 5.1.3 option, ui 2.1.2 goal, security 2.1.4 |
| D11 | minor | 합니다체 (「셉니다」, 「따릅니다」) against voice.md:12 | test-integration U3.2, build U2.2 and 2.2.1 |
| D12 | minor | The caution warns about the wrong variable | c-start 2.2.1 |
| D13 | minor | A step's starter contains the next step's answer (practice before introduce) | c-functions 2.1.1 → 2.1.2 |
| D14 | minor | Dead `static int calls` in the final | c-functions 2.2.1 |
| D15 | minor | Fill steps recall pattern names never introduced | design 4.1.8 (State), 4.1.9 (Strategy) |
| D16 | minor | Vague 할 일 with no expected value: 「결과가 바뀌었는지 확인하세요」 and 「문제가 말한 한 곳을 고치세요」 | c-structures 3.1.x, mixed 2.1.x, debug steps in lessons 2–7 |
| D17 | minor | 「포장 수가 영으로」 should be 0 | c-conditions 2.1.2 |
| D18 | minor (maintainer) | Option ids do not match their option text | design (8 options) |
| D19 | minor | A `say[output]` does not state the observed value (narration.md: 「output은 실제로 나올 값을 말한다」) | c-conditions 2.1.2, c-arrays 2.1.2/2.1.3, c-functions 2.1.4, c-pointers 2.1.4, c-double-pointers 2.1.4, c-structures 2.1.3, java-flow 2.2.1, java-static 2.2.1, python-values 2.2.1, python-calls 2.2.1, db-model 1.1.4, sql lessons, mixed 3.2.1 |
| D20 | minor | Several patches before one run (one action → one result) | finals of c-start, c-conditions, c-arrays, c-structures, java-flow, java-polymorphism, db-model, sql-select, sql-group, python-calls |
| D21 | minor | A patch with an empty `say` | c-double-pointers 2.1.4 |

Counts: 5 defect items (D1, D2, D5 single; D3 with 11 instances; D4 across 10 lessons), and 16 minor items.

## Plan items (structural, not fixes)

- **P1**: split engineer-c-structures (19 steps, 5 objectives). Move its final into the chapter whose concepts it combines.
- **P2**: several finals repeat the previous single edit instead of combining: c-start (line swap again), c-functions (same `n + sum(...)` edit), c-pointers. Redesign them as true combination steps.
- **P3 (lever)**: fix D3 at the source with the template 「고친 뒤 출력은 X여야 해요」. Add a build check in `tools/build-redesigned-git.py` that runs the starter and rejects any 「지금 출력/답/결과」 sentence that does not match. Add a second check that a 「코드 흐름 보기」 item in 할 일 implies at least one narration `code_flow` (D7).
- **P4**: recall-only lessons 18–29 (about 180 choice/fill steps) rarely run anything, even though content-rules says 「정상 상태를 실행하고 조건 하나를 바꾼 뒤 실제 결과를 비교」. Candidates for small Python run steps where the Python visualizer is Ready and useful:
  - test-integration CH2 coverage, the strongest. code_flow shows which lines and branch outcomes ran.
  - os scheduling and page replacement, as a queue/frames list per step.
  - interfaces idempotency (set vs increment with a request-id dict).
  - test-cases boundary checks.
  - design's 28 GoF recognition steps could be split or given code.
- **P5**: run `tools/narration_review.py packet` on lessons 18–29. Many 「조심하세요」 lines are factual or policy statements (「…단정하지 않아요」), which narration.md says not to mark as cautions. Several distractors are strawmen (「구현 코드가 있으니 요구도 검증된 거예요」, 「테스트가 모두 통과했으니 요구도 맞아요」, 「학생이 매번 … 직접CALL해야만 해요」, 「정처기 실기에서도 같은 점수…」).
- **P6**: rewrite the stale objectives and premises from D4 in one pass. They read like the earlier answer-writing version of these lessons.
- **P7**: decide the policy for D8. Either the SQL debug narrations show the fix like every other debug step, or the "diagnose only" style becomes a documented pattern.
- **P8**: the course's first visualizer moment would now be C (c-conditions 2.1.1). Give that first code_flow one sentence on how to read the panel.
- **P9**: db-model 2.1.x. The roughly 30-line sqlite3 harness dominates a one-keyword edit, so consider collapsing it or marking the line to read.

## Summary of visualizer verdicts

APPLY (31 new; plus 5 existing Java steps to keep: java-references 1.1.1 and 1.1.3, java-static 1.1.3, java-polymorphism 2.1.1):

| # | Lesson step | Lang | Line / event / target | What the viewer shows that the output cannot |
|---|---|---|---|---|
| 1 | c-conditions 2.1.1 | C | `packs = 0;` step_line flow_line (solution) | execution goes from the if straight to else |
| 2 | c-arrays 1.1.6 | C | `total = 0;` step_line nth2 flow_stack (starter) | total reset to 0 every iteration |
| 3 | c-arrays 2.1.1 | C | the printf line, step_line flow_memory (solution) | char[8] cells B O X, NUL, then empty cells |
| 4 | c-functions 1.1.4 | C | `return stock + value;` step_line flow_stack | two frames, each with its own `stock` |
| 5 | c-functions 1.1.5 | C | `calls = calls + 1;` step_line nth2 | static calls survives between calls |
| 6 | c-functions 2.1.2 | C | `return 0;` return flow_stack | four live sum_to frames at the base case |
| 7 | c-functions 2.1.3 | C | second `printf("%d", n);` (line 10) step_line nth1 flow_stack | unwinding starts at visit(0) |
| 8 | c-pointers 1.1.3 | C | `*q = 7;` step_line flow_stack | p and q both point at stock |
| 9 | c-pointers 1.1.4 | C | printf line step_line, starter vs solution | p retargeted vs stock overwritten |
| 10 | c-pointers 2.1.1 | C | `return p;` step_line flow_stack (starter) | the callee's pointer copy points elsewhere |
| 11 | c-double-pointers 1.1.3 | C | printf line step_line flow_stack | pp → p → other (same output as #12) |
| 12 | c-double-pointers 1.1.4 | C | printf line step_line flow_stack | pp → q → other, p → stock |
| 13 | c-double-pointers 2.1.1 | C | `*target = other;` step_line, then main printf | target points at main's p cell |
| 14 | c-structures 1.1.3 | C | printf line step_line | p points at item, not other |
| 15 | c-structures 2.1.2 | C | `return value + 1;` call nth1 flow_stack | apply's rule = 함수 add_one, nested frame |
| 16 | c-structures 4.1.3 | C | `printf("%d\n", *p);` step_line flow_memory | two pointers, one heap block |
| 17 | c-structures 4.1.4 | C | `int cleared = 0;` step_line flow_stack (starter) | aliases marked as freed memory |
| 18 | java-flow 2.1.3 | Java | `static int add(…)` call, then println step_line | add.value vs main.stock; return discarded |
| 19 | java-references 1.1.2 | Java | `b[0][0] = 7;` step_line flow_memory | two outer arrays share an inner array |
| 20 | java-references 1.1.4 | Java | `return value;` return flow_memory | replace's value → new Stock, a → old |
| 21 | java-references 2.1.4 | Java | println step_line, starter vs solution | which object received += added |
| 22 | java-static 1.1.2 | Java | println step_line flow_statics | total in statics, local per object |
| 23 | java-static 1.1.4 | Java | `static int read()` call nth1 flow_statics | a and b both still 0 during static init |
| 24 | java-static 2.1.3 | Java | println step_line, starter vs solution | the field moves from objects into statics |
| 25 | java-polymorphism 2.1.3 | Java | `System.out.print("F");` step_line, then return | value=9 but return value 2 |
| 26 | python-values 1.1.4 | Py | `print(stocks)` step_line flow_memory | two names, one list |
| 27 | python-values 2.1.1 | Py | `print(rows)` step_line flow_memory | the inner list is shared after .copy() |
| 28 | python-calls 1.1.2 | Py | `print(first is second)` step_line | one default list reused |
| 29 | python-calls 1.1.3 | Py | add return flow_memory | the param is rebound to a new list, stocks untouched |
| 30 | python-calls 2.1.3 | Py | `return 1` return flow_stack | four multiply frames |
| 31 | engineer-os 3.2.1 | Py | `memory.append(page)` step_line nth4, starter vs solution | which page pop() vs pop(0) evicted |

Total: 31 APPLY steps (17 C, 8 Java, 6 Python). Lessons 14–30 have no other APPLY.

HOLD (2): java-polymorphism 1.1.2 needs a check that the Java viewer distinguishes the hidden field. python-calls 1.1.4 needs a check that the Python tracer draws class attributes. In addition, all 17 C APPLY items are HOLD on Linux and until the builder gate is lifted (see the cross-cutting gates). The 6 Python items need only the builder gate lifted.

IMPOSSIBLE: all SQL steps (lessons 14–17 and mixed 2.1.x, 38 steps) and all choice/fill steps without code (lessons 17–30, 180 steps).

NOT-APPLY: the other 109 of the 147 Ready steps (147 = 31 new APPLY + 5 existing + 2 HOLD + 109 NOT-APPLY). The output already shows the effect, or the trace adds nothing over it (bit ops in decimal, opaque sqlite3).

## Coverage gaps

- All 30 lessons were reviewed, and none were skipped.
- For quiz lessons 18–29 I read goals, options, answers and fields in full, but read narration only for non-title `say` lines. Title-introduction lines were not semantically reviewed.
- I did not compile or run C, Java or Python. C starter outputs in D3 were derived by hand from the code. The validity of APPLY lines and events (for example the JVM's attribution of the return line in java-polymorphism 2.1.3) must be confirmed by the validator once the code_flow actions are authored.
- I did not listen to any audio.
