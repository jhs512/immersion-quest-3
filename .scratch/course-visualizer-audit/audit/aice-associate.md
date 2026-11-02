# AICE Associate course audit (aice-associate, 24 lessons, 228 steps)

The owner wants every lesson in every bundled course re-reviewed for leveling quality. They also want 코드 흐름 보기 used in narrations only where it genuinely helps understanding. This file covers the AICE Associate course (inventory.json courses[2]). It is a read-only review. The root agent applies the edits.

## Coverage and method

- **Coverage.** I reviewed all 24 lessons and all 228 steps (57 + 59 + 56 + 56, matching the inventory). No lesson or step was skipped.
- **Inputs per lesson.**
  - tools/redesigned_lessons/<key>/content.json and approved-prd.json.
  - tests/lesson-cases/<key>.json. Its expected_outputs are the validator's real run outputs. I checked every narration sentence that reads output against them.
  - The step facts in inventory.json.
- **How the review ran.** A script, kept outside the repo, built one digest per lesson. Each digest holds the starter, the solution diff, unused names found by parsing the code, the tests, the real run outputs and the narration. Four parallel reviewers each took six lessons (1-6, 7-12, 13-18, 19-24).
- **What the root reviewer re-checked against the digests.** L6 s10, L10 s11, L20 s9, L22 s2, L22 s5, and the challenge-goal template across lessons 13-23.
- **What was not run on the exam versions.**
  - The exam uses pandas 1.5.3, sklearn 1.3.2, TF 2.13.1 and xgboost 0.90. Local Python has pandas 3.0.5 and sklearn 1.9.0, and TensorFlow is not installed.
  - TF steps (lessons 20-23 and parts of 24) were checked by reading and by hand arithmetic against the validator's recorded outputs.
  - The two xgboost 0.90 defects in lesson 18 are inferred from the 0.90 source. They were not run.
  - The `nth` values in the APPLY suggestions are estimates. Confirm them on a real trace.
- **One precondition holds for every APPLY below.** The builder rejects `code_flow` narration for any step that is not Java (tools/build-redesigned-git.py:112, also examples/validate_redesigned_lesson.rs:156). This is already in decisions.tsv. No APPLY item can ship until that check allows Python.

## Course-level findings

1. **[defect, pattern] Final-challenge goals state the solution's output as the current state.**
   - **Where.** Lessons 13, 14, 15, 16, 17, 18, 20, 21 and 22.
   - **The problem.** The goal gives the target numbers as "지금/현재 결과는 …". 할 일 step 1 says "코드 실행을 눌러 현재 결과를 확인하세요.", but the first real run prints something else. So the text is false, and it also gives away the expected answer.
   - **Examples, each with the real first-run output:**
     - L13 s9 says "지금 자료의 평가 예측은 7분과 9분이고 회귀의 MAE는 0이에요". The run prints '[3.0, 3.0]\n5.0\n5.0'.
     - L14 s9 says "지금 결과는 2.666667, 3.265986, 0.84예요". The run prints '16.0\n290.666667\n-3.36'.
     - L17 s9 says "현재 mean의 MSE는 25, tree는 0이므로". The run prints "{'mean': 25.0, 'tree': 50.0}".
     - L18 s9 says "현재 두 번·0.5 비율이면 예측은 1.625와 6.125예요". The run prints '1\n1.0\n[2.0, 8.0]'.
     - L16 s11 says "현재 결과는 0.666667, 1.0, 0.8이에요".
   - **The fix.** One template change covers all of them: "완성하면 … 이 나와야 해요." L23 s9 already uses the right form ("현재 wait=2이면 … 돌아와야 해요").
   - **Grading.** The 13-18 reviewer graded these minor and the 19-24 reviewer graded them defects. This file counts them as defects because the text contradicts the real run.
2. **[minor, pattern] Inserted practice steps use a vague 할 일 line, "2. 문제가 말한 한 곳을 고치세요."**
   - **Where.** L3 s4/s6/s8, L4 s2, L5 s10, L6 s3/s4/s7, L7 s8, L9 s8, L10 s10, L13-L18 s8 or s10, L19 s8, L20 s8 and L22 s8.
   - **Why it matters.** voice.md forbids instructions that leave the learner guessing what to do. In L6 s10 it is a real defect, because the solution needs two edits.
   - **Narration that stops early.** Several of these steps have empty tests, and their narration stops before the fix: L14 s8, L15 s8, L18 s8, L21 s8, L23 s8 and L24 s10.
3. **[minor, pattern] Unused imports and variables break content-rules section 4 in about 20 steps.**
   - **Imports nothing uses:**
     - seaborn in L8 s3/s4.
     - train_test_split in L10 s1.
     - ShuffleSplit in L11 s6.
     - StandardScaler in L12 s6.
     - numpy in L20 s1/s2.
     - KFold in L19 s2.
   - **Solutions that keep unused imports.** L13 s2, L14 s8, L15 s1/s2/s5, L16 s9 and L17 s3, plus most of L24's shared header.
   - **`y` defined and never used.** L9 s8/s9 and L10 s4.
   - **Cause.** The build's drop_unused_imports apparently does not run on redesigned lessons. A build check would stop this coming back.
4. **[minor, pattern] Student text is missing spaces.**
   - **Examples:**
     - L2 premise "배송 시간은12,30,42분이에요".
     - L10 objective "X와y".
     - L9 s8 "입력X".
     - L12 s9 "다시학습".
     - The options in L17 s7 and L19 s7: "아니요.학습", "네.이 표".
   - **Fix.** A build lint that flags a Hangul letter or period followed directly by a letter would catch them.
5. **[PLAN] Fill in the manifest prerequisites.** All 24 lessons have prerequisites [], although each PRD names earlier lessons. Fill them in from the PRDs.
6. **[PLAN] Refresh the PRDs.** Most PRDs give a stale unit count, because the "마지막 도전" unit was added later.
7. **[PLAN] Pick one policy for representative steps.** In lessons 21, 23 and 24 the narration stops before the fix. In 19, 20 and 22 it demonstrates the fix.
8. **Visualizer, course-wide.**
   - **Why most steps get no APPLY.** The tracer shows a DataFrame, Series, ndarray, estimator or tensor only as its type name. So from lesson 4 on, nearly every step is NOT-APPLY or HOLD-OPAQUE.
   - **Where it helps.** The plain-Python lessons 1-3. Also a few steps in lessons 10, 13, 14, 16, 21 and 23 that build lists, dicts or small functions in main.py.
   - **One viewer feature would serve every HOLD-OPAQUE item: a summary of small objects.**
     - For a DataFrame: shape, columns, dtypes and about 5 head rows.
     - For an ndarray: shape, dtype, and the values when there are 20 or fewer elements.
     - For a fitted estimator: attributes such as mean_.
     - For training: the Keras History.history dict.
   - **A cheaper first step.** A rule to show ndarray values when size is 20 or fewer would on its own turn L8 s4, L11 s6, L12 s9 and L22 s5/s7 into APPLY.

## 1. aice-python-start

**Goal and progression.** Objectives "실행 결과와 코드의 값·이름을 구별해요", "이름의 대입과 리스트 항목 선택을 이해해요" and "자료의 항목과 건수를 구별해" are clear, and every step serves one of them. The order is print, change a value, quote vs name, rebinding, list, index 0, len, then a combined challenge. Each step adds one concept and each edit is one line (the challenge is three). The PRD prerequisites ("파이썬 문법 선행은 없어요") fit a true first lesson. PRD scope says "두 챕터·두 단원·여덟 스텝" but the content has three units, because the "마지막 도전" unit was added later. The same PRD drift appears in lessons 2 to 6. Manifest prerequisites are [], which is correct for a first lesson.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 0853d17f | print(minutes) | code | ok | NOT-APPLY | output shows both lines |
| 2 | 1.1.2 | 6c5324f8 | 숫자 하나를 바꿔요 | code | minor | NOT-APPLY | typo in 할 일 |
| 3 | 1.1.3 | 90c4f6a0 | 따옴표를 지워 | code | ok | NOT-APPLY | output already contrasts "minutes" vs 18 |
| 4 | 1.1.4 | 659c1013 | minutes = corrected | code | ok | APPLY | rebinding is invisible in output |
| 5 | 2.1.1 | 8b071000 | 세 시간을 담은 목록 | code | ok | NOT-APPLY | printed list shows it |
| 6 | 2.1.2 | 04338046 | minutes[0] | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | 18ea3f5c | len(minutes) | code | ok | NOT-APPLY | |
| 8 | 2.2.1 | 5b8e2c47 | 처음과 끝을 읽으세요 | code | ok | APPLY | IndexError try, positions 0-4 |

**Defects.**
- [minor] step 2 (stp_6c5324f8) goal 할 일: "2. print 괄호 안의 숫자를 18을 고치세요." The particle is wrong. Fix to "print 괄호 안의 숫자를 18로 고치세요."
- [minor] step 2 (stp_6c5324f8) narration: "조심하세요. 코드를 고친 뒤 다시 실행해야 새 결과가 나와요." This is a UI fact, not a mistake the step provokes. Keep it as a plain sentence without the 조심하세요 prefix.

**Visualizer details.**
- APPLY step 4. After the teacher patch, `code_flow` at line `minutes = corrected` (event step_line, target flow_memory) shows minutes still 18 and corrected 24. Then `code_flow` at line `print(minutes)` (step_line, flow_memory) shows minutes now 24. The output only shows the final 24, so the viewer is the only place the rebinding is visible. It also turns the caution "print 아래에 쓰면 출력은 18 그대로예요" into something seen.
- APPLY step 8. After the try patch `print(minutes[len(minutes)])`, `code_flow` at that line (event exception, target flow_objects) shows the minutes list with positions 0 to 4 and no position 5. That explains the IndexError better than the message alone.

**PLAN.** none.

## 2. aice-python-conditions

**Goal and progression.** Objectives "숫자 비교의 참과 거짓", "기준과 같은 값이 포함되는지" and "준비된 반복·조건으로 자료를 골라요" match the steps. The progression is good: comparison to bool, > vs >=, change only the limit, if/else, for, condition in a loop, append, change the limit and count, combined challenge. There are two mismatches with the PRD. PRD scope says "완성된 for에 조건과 append를 적용" and the objective says "준비된 반복", but step 5 has the learner write the for loop, and step 9 writes for, if and append from an empty comment. That is four new lines, above the 1-3 line guideline. Steps 2 and 6 repeat the boundary idea, which reads as deliberate practice.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 8b3de82c | late = minutes >= limit | code | ok | NOT-APPLY | |
| 2 | 1.1.2 | 7d273904 | > 를 >= 로 | code | ok | NOT-APPLY | |
| 3 | 1.1.3 | 1328ad1a | 기준값만 바꿔요 | code | minor | NOT-APPLY | stale "고르는 대신" sentence |
| 4 | 1.1.4 | b5f34130 | else | code | ok | NOT-APPLY | output shows the branch |
| 5 | 2.1.1 | 4e5e65a5 | for minute in minutes | code | ok | NOT-APPLY | each item is printed |
| 6 | 2.1.2 | 1b5f4f9a | 기준에 맞는 건만 | code | ok | APPLY | skipped print for 12 and 30 |
| 7 | 2.1.3 | 5f9dd3bf | append로 delayed에 모으기 | code | ok | APPLY | list growth hidden in output |
| 8 | 2.1.4 | b5c56d81 | 조건을 바꾸고 건수 비교 | code | minor | NOT-APPLY | typo in 할 일 |
| 9 | 2.2.1 | 981a0d0f | 모아 건수를 세세요 | code | minor | NOT-APPLY | 4-line edit, narration order |

**Defects.**
- [minor] unit 2 premise: "배송 시간은12,30,42분이에요." Spaces are missing. Fix to "배송 시간은 12, 30, 42분이에요."
- [minor] step 3 (stp_1328ad1a) goal: "출력값을 고르는 대신 코드를 수정하는 문제예요." No step in this lesson asks the learner to choose an output, so the contrast has no referent (a conversion leftover). The narration repeats it ("이번에는 출력값을 고르는 대신"). Drop the sentence from goal and narration.
- [minor] step 8 (stp_b5c56d81) goal 할 일: "2. limit 값 한 곳을 40을 고치세요." Fix to "`limit = 30`을 `limit = 40`으로 고치세요."
- [minor] step 9 (stp_981a0d0f) narration order. The narration patches `print(len(delayed))` before the loop, while 할 일 lists "2. 반복과 조건으로 기준 이상인 배송만 delayed에 모으세요." before "3. 둘째 출력이 모은 건수가 되도록 고치세요." voice.md asks the narration to follow 할 일 order. Swap the first two patches.
- [minor] step 9 (stp_981a0d0f) caution "delayed = []를 반복 안으로 옮기면 매번 비워져서 마지막 한 건만 남아요" is a near copy of step 7's "delayed = []를 반복 안에 두면 매번 비워져 마지막 한 건만 남아요". The builder passes it because the wording differs, but it is the same warning twice. Step 9 could warn about `>` instead, which its own try already shows.

**Visualizer details.**
- APPLY step 7, the strongest in this lesson. After the patch, `code_flow` at line `delayed.append(minute)` (event step_line, nth 2, target flow_memory) shows minute = 42 and delayed already [30]. A last stop at `print(delayed)` shows [30, 42]. The output only prints the final list. The viewer shows it growing one item per pass, and it makes the `delayed = []` reset caution concrete.
- APPLY step 6. On the starter, `code_flow` at line `if minute > 30:` (event step_line, nth 2, target flow_line) shows minute = 30, and the next step returns to `for minute in minutes:` without reaching `print(minute)`. That is what the objective "반복 안의 조건이 각 항목에 따로 적용됨" names, and the output only shows it as a missing line.

**PLAN.**
- Either change the objective and PRD to say the learner writes for, if and append, or give step 9 a prepared loop skeleton so the edit stays within 1-3 lines.

## 3. aice-python-api

**Goal and progression.** Objectives "딕셔너리 키와 목록의 위치를 구별해요", "호출에 자료와 옵션을 전달하는 표기" and "모듈·별칭·기능 호출을 연결해요" match the two chapters. The step order is clean: key, list value under a key, len of dict vs list, wrong key, sorted, the reverse option, module.function, alias, combined challenge. Each edit is one line. Three inserted steps (4, 6, 8) use a generic 할 일 that does not name the edit.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | cfc45a47 | 키 minutes | code | ok | NOT-APPLY | |
| 2 | 1.1.2 | 4c391baa | data["minutes"] 전체 | code | ok | NOT-APPLY | |
| 3 | 1.1.3 | 73257e95 | len(data["minutes"]) | code | minor | APPLY | dict of 2 keys vs list of 3 |
| 4 | 1.1.4 | 45ab05ab | 항목 이름이 틀린 곳 | code | minor | NOT-APPLY | vague 할 일 |
| 5 | 2.1.1 | 464ed6a6 | sorted(minutes) | code | ok | APPLY | aliasing `ordered = minutes` |
| 6 | 2.1.2 | b667b426 | 옵션 이름으로 방향 | code | minor | NOT-APPLY | vague 할 일 |
| 7 | 2.1.3 | f4e5eb8a | statistics.mean | code | ok | NOT-APPLY | |
| 8 | 2.1.4 | 8b12ce97 | 별칭을 바꿔도 | code | minor | NOT-APPLY | vague 할 일, caution misuse |
| 9 | 2.2.1 | 3ec1a5c3 | 건수·평균·정렬 | code | minor | NOT-APPLY | "세 줄" vs four lines |

**Defects.**
- [minor] steps 4, 6, 8 (stp_45ab05ab, stp_b667b426, stp_8b12ce97) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." and "3. 다시 실행해 결과가 요구와 맞는지 비교하세요." voice.md rules out instructions that make the learner guess the action. Name the target, for example "키 `"minute"`에 빠진 글자를 고치세요", "`reverse=False`의 값을 고치세요" and "`statistics.mean`의 모듈 이름을 고치세요".
- [minor] step 3 (stp_73257e95) caution: "조심하세요. 지금처럼 항목 수와 건수가 비슷하면 우연히 맞을 수 있어요." Here the counts are 2 and 3, so they do not match, and "지금처럼" contradicts the run. Rephrase to "키 개수와 건수가 우연히 같은 자료에서는 len(data)도 맞아 보여요."
- [minor] step 8 (stp_8b12ce97) narration: "조심하세요. stats가 정해진 예약 이름은 아니에요." This is a fact, not a mistake, and narration.md allows 조심하세요 only for a real mistake. Also the final RUN is followed by "import는 이름을 연결해요. 라이브러리 설치와는 달라요.", which does not read the output. Drop the prefix and read the 18.
- [minor] step 9 (stp_3ec1a5c3) goal: "세 줄을 차례로 출력해요 ... 마지막 줄은 원래 시간 목록이에요" then lists four values, and 할 일 5 says "네 줄을 확인". Say "네 줄이 나와요. 앞의 세 줄을 고쳐요."

**Visualizer details.**
- APPLY step 5. On the starter, `code_flow` at line `print(ordered)` (event step_line, target flow_objects) shows ordered and minutes pointing to the same list object. After the patch, the same stop shows two separate lists, the new [12, 18, 24] and the original [24, 12, 18]. Printed output cannot show identity, and identity is exactly the "원래 목록은 바꾸지 않아요" claim and the `.sort()` caution.
- APPLY step 3. `code_flow` at line `count = len(data)` (event step_line, target flow_objects) shows the dict with two keys, each pointing to a three-item list. The learner sees "2 vs 3" as structure instead of being told it.

**PLAN.** none.

## 4. aice-table-csv

**Goal and progression.** Objectives "표의 행·열·인덱스 표시", "일부 관찰과 전체 크기를 구별" and "CSV에서 읽은 표의 필요한 열·항목" match. The steps go columns, head, shape, one column, read_csv, iloc, a list of columns, len, combined. There is one concept per step and each edit is one line. Steps 3 and 8 both teach "head does not change df" (with shape, then with len), which is a near repeat. Exam match: only core pandas (DataFrame, head, shape, read_csv, iloc, column lists), all stable in pandas 1.5.3. Step 2 has empty tests and no prepared cases, but it is graded by the built-in `head_three_step` checker in the built lesson, so that is not a gap.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | e79c2e4f | df.columns | code | ok | NOT-APPLY | table printed |
| 2 | 1.1.2 | 315f010b | 앞부분만 살펴봐요 | code | minor | NOT-APPLY | vague 할 일 |
| 3 | 1.1.3 | 25ef3794 | df.shape | code | ok | NOT-APPLY | shape printed |
| 4 | 1.1.4 | d605904e | df["minutes"] | code | minor | NOT-APPLY | off-topic caution |
| 5 | 2.1.1 | 47635cf8 | read_csv 파일 이름 | code | ok | NOT-APPLY | |
| 6 | 2.1.2 | c0f636c6 | iloc[0] | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | 7c333872 | 두 열만 | code | ok | NOT-APPLY | |
| 8 | 2.1.4 | 85396d4d | len(df) | code | ok | NOT-APPLY | repeats step 3 idea |
| 9 | 2.2.1 | 85c153cc | 크기와 두 열 | code | ok | NOT-APPLY | |

**Defects.**
- [minor] step 2 (stp_315f010b) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." Name it, for example "`head(2)`의 숫자를 앞의 세 건이 보이게 고치세요."
- [minor] step 4 (stp_d605904e) caution: "조심하세요. df.head(1)은 첫 행 하나예요. 한 열의 값들을 고르는 것과 달라요." Nothing in the step invites head(1). The real slip here is a misspelled column name (KeyError) or choosing a column by position. Replace it with a column-name caution.

**Visualizer details.** All steps are NOT-APPLY. Every step prints the table, list or shape it is about, and the logic lives inside pandas calls. No HOLD-OPAQUE candidate is worth the cost, because even a DataFrame summary would repeat the printed table.

**PLAN.**
- Merge or differentiate steps 3 and 8, which both teach "head 뒤에도 df는 그대로". Step 8 could instead run `df = df.head(2)` and show that reassignment does shrink df, which step 2 only mentions in its caution.

## 5. aice-selection

**Goal and progression.** Objectives "행·열의 이름과 위치를 구별", "필터·정렬·요약의 대상을 구별" and "평균·중앙값·상관의 의미와 해석 한계" match the three chapters. Inside the lesson the progression is good: column, loc by label, iloc by position, mask with boundary, &, descending sort, median, groupby, corr choice, filter plus sort, combined. Step 1 (`df["minutes"].tolist()`) repeats lesson 4 step 4 almost verbatim. Step 10 repeats step 6's `ascending=False` edit with the filter already prepared, so it adds no new decision. Step 4 introduces the mask idea together with the boundary, but the boundary is known from lesson 2, so that is acceptable.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 77a1d24b | df["minutes"] | code | ok | NOT-APPLY | repeat of lesson 4 step 4 |
| 2 | 1.1.2 | 4d81fbbb | loc[101, "minutes"] | code | ok | HOLD-OPAQUE | table never printed |
| 3 | 1.1.3 | 0038fd19 | iloc[0, 0] | code | ok | HOLD-OPAQUE | table never printed |
| 4 | 2.1.1 | 01126512 | 경계의 배송도 포함 | code | minor | NOT-APPLY | mask printed with tolist |
| 5 | 2.1.2 | 5f29edf5 | & 두 조건 | code | ok | NOT-APPLY | |
| 6 | 2.1.3 | 6f7187a9 | ascending=False | code | ok | NOT-APPLY | both orders printed |
| 7 | 3.1.1 | 2d204e9c | median() | code | ok | NOT-APPLY | |
| 8 | 3.1.2 | f063e605 | groupby 지역별 평균 | code | ok | NOT-APPLY | |
| 9 | 3.1.3 | 9ba83bdc | 함께 커지는 관계 | choice (example_code) | minor | NOT-APPLY | caution states the answer |
| 10 | 3.1.4 | e2d12228 | 조건과 정렬을 연결 | code | minor | NOT-APPLY | vague 할 일, no new decision |
| 11 | 3.2.1 | 5f220155 | 두 조건으로 고르고 요약 | code | ok | HOLD-OPAQUE | selected and ordered never printed |

**Defects.**
- [minor] step 10 (stp_e2d12228) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." Name `ascending=True`. Also the final narration after the last RUN, "행 선택과 정렬 방향을 따로 판단하면 돼요.", does not read the output [42, 30].
- [minor] step 9 (stp_9ba83bdc) narration: "조심하세요. 상관만으로 원인을 증명할 수는 없어요." This is the answer to the question and restates the step objective ("상관계수의 방향과 인과관계의 차이"), and it comes before choose_answer. narration.md forbids a 조심하세요 that restates the objective. Say it as the conclusion. The distractor "거리가 늘어서 시간이 늘어난다는 원인이 밝혀졌어요" is close to a straw man. A more common misreading is the practical causal claim, such as "거리를 줄이면 시간이 줄어든다고 말할 수 있어요".
- [minor] step 4 (stp_01126512) narration: the last RUN (after limit is restored to 30) is followed only by the caution on `mask =`, with no reading of the output.

**Visualizer details.**
- HOLD-OPAQUE steps 2 and 3. The learner never sees the table in these steps, because the first run is a KeyError or an IndexError. A DataFrame summary of `df` showing index labels 101 to 104 next to positions 0 to 3, plus the head rows, would show loc label vs iloc position directly. Needed: index labels, column names, head rows.
- HOLD-OPAQUE step 11. `selected` and `ordered` are DataFrames that are printed only as `ordered.index.tolist()`. A summary with shape and index for each variable at `selected = df.loc[...]` and `ordered = selected.sort_values(...)` would show 6 rows, then 5 after the time-only try, then 4, then the reordered index. Needed: shape, index list.

**PLAN.**
- Replace step 1 with something new, such as a misspelled column name and its KeyError, because lesson 4 step 4 already teaches the same edit.
- Give step 10 a real combined decision, such as a missing filter to add before sorting, or drop it. Step 11 already combines filter and sort.

## 6. aice-quality

**Goal and progression.** Objectives "결측·중복의 검사 대상과 처리 정책", "정상0·미측정·통계적 검토 후보" and "짧은 코드 수정으로 요구한 행과 값을 남겨요" match the chapters. The progression is isna, count vs size, dropna subset, fillna, an all-missing choice, duplicated, keep, the IQR boundary, a real-outlier choice, dropna combined with keep, and the final challenge. The PRD correctly leaves imputer fit/transform to the leakage lesson ("누수 수업에서 다뤄요"). The exam APIs used (isna, count, dropna(subset), fillna, duplicated, drop_duplicates(keep), quantile) are all stable in pandas 1.5.3. The four inserted code steps (3, 4, 7, 10) use the generic 할 일, and on step 10 that is a real defect.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 4d069ee5 | isna() | code | ok | NOT-APPLY | |
| 2 | 1.1.2 | 6e9d9d6b | count() vs size() | code | ok | NOT-APPLY | |
| 3 | 1.1.3 | 94585445 | 시간이 있는 배송만 | code | minor | NOT-APPLY | vague 할 일 |
| 4 | 1.1.4 | 731d6db0 | 빈 시간을 채워요 | code | minor | NOT-APPLY | vague 할 일 |
| 5 | 1.1.5 | af14310d | 모든 시간이 비어 있어요 | choice (example_code) | ok | NOT-APPLY | |
| 6 | 2.1.1 | e64a2273 | duplicated() | code | ok | NOT-APPLY | |
| 7 | 2.1.2 | 29d05539 | 마지막 수정본 | code | minor | NOT-APPLY | stale comment, vague 할 일 |
| 8 | 3.1.1 | ef317a57 | IQR < 와 > | code | ok | NOT-APPLY | |
| 9 | 3.1.2 | 4b962eb4 | 멀리 떨어진 값 | choice (example_code) | minor | NOT-APPLY | caution states the answer |
| 10 | 3.1.3 | 22d818f2 | 처리 순서와 범위 | code | defect | NOT-APPLY | 할 일 says one edit, needs two |
| 11 | 3.2.1 | 57fb87ab | 측정 못한 시간과 옛 수정본 | code | ok | HOLD-OPAQUE | clean reassigned twice |

**Defects.**
- [defect] step 10 (stp_22d818f2) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." The solution changes two things on the line, `dropna()` to `dropna(subset=["minutes"])` and `keep="first"` to `keep="last"`, and the narration patches them separately. The goal text itself says "두 처리 조건을 맞춰 보세요". A learner who follows 할 일 fixes one place and fails. Fix: "2. dropna가 시간 열만 검사하도록 고치세요." and "3. 같은 주문의 마지막 수정본을 남기도록 keep을 고치세요.", then renumber.
- [minor] steps 3, 4, 7 (stp_94585445, stp_731d6db0, stp_29d05539) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." Name the target (`dropna()`, `fillna(0)`, `keep="first"`).
- [minor] step 7 (stp_29d05539) starter comment: "# None은 측정하지 못한 값이에요. 0은 실제 시간이에요." The step's data has no None and no 0 (`'minutes': [12, 18, 30, 42]`). Replace it with the duplicate-order comment that step 6 uses.
- [minor] step 9 (stp_4b962eb4) narration: "조심하세요. 후보 계산만으로 원래 행을 삭제하지 않아요." This is the answer to the choice, said before choose_answer, and it repeats step 8's caution "후보로 표시된 값도 바로 지우지 않아요". State it as the conclusion after reading the output.

**Visualizer details.**
- HOLD-OPAQUE step 11. `clean` is reassigned twice, first `df.dropna(subset=["minutes"])` and then `clean.drop_duplicates(...)`. A DataFrame summary with shape and index at each line would show 6, then 5, then 4 rows and which order_id disappears, while the output shows only the end. Needed: shape and the index or a key column (order_id). Step 10 does the same in one chained expression, so even a summary would show nothing there, because intermediate results are not main.py variables.

**PLAN.**
- Besides fixing the 할 일, split step 10's line into two statements like step 11, so each change gets its own run and observation.


## 7. aice-join

**Goal and progression.** The lesson goal is clear and matches the steps: "JSON과 월별 표를 읽고 행 추가와 키 결합을 구별해요" (steps 1-2), "원본 행 보존·중복 키·자료형·결측 키를 검토해요" (steps 3-7), "새 배송 자료에서도 필요한 결합을 직접 고쳐 확인해요" (steps 8-9). Each step changes one call or one argument (read_csv to read_json, merge to concat, assign to merge, left to inner, len(orders) to len(joined), astype(int), dropna(subset=...)). Step 8 reverses step 4 (inner back to left) on new data as a transfer check, and step 9 combines concat, left merge and fillna. The manifest has prerequisites []. The PRD audience is "표 선택과 자료 품질을 익힌 에이스 학습자", which matches the course order (selection 5, quality 6). The PRD claims pandas 1.5.3 verification; every API used (read_json orient, concat ignore_index, merge validate/sort) exists in 1.5.3.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 04c4cef9 | read_json으로 JSON 회원 파일 | code | ok | NOT-APPLY | printed columns and zones show the result |
| 2 | 1.1.2 | cf3096d8 | concat으로 다음 달 배송 | code | ok | NOT-APPLY | order_id and index lists printed |
| 3 | 1.1.3 | d568adc8 | merge(on="member_id") | code | ok | HOLD-OPAQUE | joined DataFrame rows |
| 4 | 1.1.4 | 6e0f592a | how="inner" | code | ok | NOT-APPLY | printed lists show the dropped 103 |
| 5 | 2.1.1 | 644fdedb | len(joined)로 늘어난 행 | code | ok | HOLD-OPAQUE | joined DataFrame rows |
| 6 | 2.1.2 | 16761765 | astype(int)로 키 자료형 | code | ok | NOT-APPLY | dtype mismatch is the error itself |
| 7 | 2.1.3 | f86bcd8f | dropna로 빈 회원 키 | code | ok | NOT-APPLY | zones printed |
| 8 | 2.1.4 | 19a6791c | 모든 배송을 보존 | code | minor | NOT-APPLY | vague 할 일 |
| 9 | 2.2.1 | b05f4187 | 두 달 배송을 붙이고 지역별로 | code | ok | NOT-APPLY | final challenge, three runs match real outputs |

**Defects.**
- [minor] step 8 (stp_19a6791c) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." docs/voice.md forbids actions the learner has to guess. The goal does say "how 한 곳만 고치세요", so write "2. joined 줄의 `how` 값을 모든 배송이 남는 값으로 고치세요." without giving the answer.
- [minor] PRD drift (not student-facing): approved-prd.json scope says "두 챕터·두 단원·아홉 스텝" while the lesson has three units (the final-challenge unit). The representative says "inner라 조회에 없는 배송103이 사라져요" but step 8 uses orders 201-204. Update the PRD text on the next touch.

**Visualizer details.** Steps 3 and 5 are HOLD-OPAQUE. In step 3 the point is that `orders.assign(zone=regions["zone"])` pairs rows by position. A DataFrame view of `joined` (all rows, columns order_id, member_id, zone) would show member 2 next to north, which the printed zone list only implies. In step 5 a row view of `joined` (4 rows, member 1 twice with north and west) would show the fan-out directly, where the output shows only "3\n4". Both need a small-DataFrame summary of shape, column names and head rows (5 rows is enough). Every other step prints the lists it is about.

**PLAN.** none.

## 8. aice-plots

**Goal and progression.** The objectives "개수·평균·밀도·그룹 비율을 구별해요", "그림 표시와 원자료 처리의 차이를 판단해요", "질문에 맞는 축·통계를 골라 실제 그림으로 검증해요" map to chapter 1 (count, mean, bin edges), chapter 2 (density area, common_norm, overlapping points) and chapter 3 (showfliers, corr heatmap, ylabel, transfer, challenge). Each step changes one call or option, and a printed "확인용 출력" of patch heights turns the picture into numbers, which works well for grading and narration. Steps 1 and 2 are mirror images (barplot to countplot, then back). That is an intended contrast, but it uses two steps for one distinction. The manifest has prerequisites []. The PRD audience "표 선택·요약·결측과 후보 검토를 익힌" matches the order. The seaborn 0.12 `errorbar=None` and matplotlib 3.7 `plt.hist` behavior claimed in the PRD hold for those versions.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 519e5d3e | countplot으로 개수 | code | ok | NOT-APPLY | heights printed |
| 2 | 1.1.2 | cea0f493 | barplot y="minutes" 평균 | code | ok | NOT-APPLY | heights printed |
| 3 | 1.1.3 | 78ff95a5 | pd.cut(right=False) | code | minor | NOT-APPLY | unused seaborn import |
| 4 | 2.1.1 | 66e2dc95 | 밀도 막대의 면적 | code | minor | HOLD-OPAQUE | unused seaborn import; `widths` never shown |
| 5 | 2.1.2 | 9bfd0198 | common_norm=False | code | ok | NOT-APPLY | heights printed |
| 6 | 2.1.3 | 6c6b0104 | len(df)로 겹친 점 | code | ok | NOT-APPLY | counts printed |
| 7 | 3.1.1 | 3a9878d6 | showfliers=False | code | ok | NOT-APPLY | plain list comprehension; len/max printed |
| 8 | 3.1.2 | 81365ec8 | corr()로 heatmap | code | ok | NOT-APPLY | shape and values printed |
| 9 | 3.1.3 | 542ecd75 | set_ylabel | code | ok | NOT-APPLY | label printed |
| 10 | 3.1.4 | b93b2586 | 평균 거리를 그려요 | code | minor | NOT-APPLY | transfer step; caution highlight off |
| 11 | 3.2.1 | 037eb885 | 끝난 배송 평균 시간 막대 | code | ok | NOT-APPLY | three runs match real outputs; 41.67 caution checks out |

**Defects.**
- [minor] step 3 (stp_78ff95a5) starter and solution: "import seaborn as sns". The solution uses only `plt.hist` and `pd.cut`. content-rules section 4 says this import must go from both starter and solution.
- [minor] step 4 (stp_66e2dc95) starter and solution: "import seaborn as sns". It is unused for the same reason. Remove it.
- [minor] step 10 (stp_b93b2586) narration caution target `code:x="region"` with text "평균을 그리는 함수로 바꿔도 y의 열이 질문과 다르면 다른 그림이에요." The sentence is about y and the function, but the highlight lands on x. After the revert there is no y token, so highlight `code:sns.countplot` instead.
- [minor] student-visible unit premise: "시간은10,20,30,50이고 거리는1,2,3,4예요." is missing spaces. Write "시간은 10, 20, 30, 50이고 거리는 1, 2, 3, 4예요."
- [minor] PRD scope says "세 챕터·세 단원" but there are four units. This is PRD text only.

**Visualizer details.** Step 4 is HOLD-OPAQUE. The fix is `share = heights[0] * widths[0]`, and `widths` (ndarray [20., 40.]) is never printed or named in the narration ("첫 막대 높이에 너비 widths[0]을 곱해요"). An ndarray view showing shape (2,) and its values would let the learner see 0.0125 × 20. Short of a viewer change, the narration could say "너비는 20이에요". Step 7's list comprehension `minutes = [m for m in minutes if m < 100]` is plain Python, but "4 13" already shows the deletion, so NOT-APPLY.

**PLAN.**
- Consider merging steps 1 and 2 into one count-versus-mean step and using the freed slot for barplot `estimator` (the challenge's sum trap in step 11 relies on `estimator="sum"`, which is never introduced).

## 9. aice-features

**Goal and progression.** The objectives "단위·자료형·범주·날짜 변환의 의미를 구별해요", "변환 실패와 미지 범주가 남기는 값을 판단해요", "예측 시점에 아는 입력 열과 정답·식별자를 구별해요" are covered in order. Steps 1-4 cover new column, astype, to_numeric coerce and map with unknowns. Steps 5-7 cover get_dummies, dummy_na and to_datetime coerce. Step 8 selects X, and step 9 combines date coercion, -1 fill and column choice. Each step is a one-line edit with a clear before and after. The PRD's out_of_scope "모델·인코더fit·스케일러는 분리와 누수 원칙 뒤에 다뤄요" is honored, because scale comes at order 12. The manifest has prerequisites []. Errors are introduced in the intended order: KeyError (step 1), TypeError (step 2), silent failure (step 3), ValueError (step 7).

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 739265ff | distance_m 새 열 | code | ok | NOT-APPLY | both columns printed |
| 2 | 1.1.2 | 2d88b8a0 | astype("int64") | code | ok | NOT-APPLY | |
| 3 | 1.1.3 | cb512a3c | to_numeric(errors="coerce") | code | ok | NOT-APPLY | type, values and NaN count printed |
| 4 | 1.1.4 | 577645ef | map 결과 dropna 지우기 | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | 1d4d1c16 | get_dummies | code | ok | NOT-APPLY | columns and values printed |
| 6 | 2.1.2 | 542b3fa2 | dummy_na=True | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | 23953406 | to_datetime(errors="coerce") | code | ok | NOT-APPLY | |
| 8 | 2.1.4 | cc51dad9 | 예측할 때 아는 열 | code | minor | NOT-APPLY | vague 할 일, unused y, caution target |
| 9 | 2.2.1 | dd7ffb3c | 접수할 때 아는 입력 표 | code | minor | NOT-APPLY | unused y; three runs match |

**Defects.**
- [minor] step 8 (stp_cc51dad9) goal: "입력X의 두 열을 고치세요." is missing a space ("입력 X의"). The 할 일 "2. 문제가 말한 한 곳을 고치세요." is a guess-the-action instruction. Write "2. `X = df[[...]]` 줄의 두 열을 접수 때 아는 열로 고치세요."
- [minor] step 8 narration: "조심하세요. 맞힐 실제 시간은 입력에 섞지 않아요." uses target `output`. The warning is about the column list, so highlight `code:df[["distance", "region"]]`.
- [minor] steps 8 and 9 (stp_cc51dad9, stp_dd7ffb3c) solution: `y = df["minutes"]` is assigned and never used. It is a deliberate label for "정답 y", but by the course's own unused-code rule either print it (`print(y.tolist())`) or say in the comment that it is kept for the model in a later lesson.
- [minor] student-visible unit premise: "같은 네 배송의 거리km는1,2,3,4예요." is missing spaces ("거리 km는 1, 2, 3, 4예요").

**Visualizer details.** None of the steps needs it. Every step prints the column or list it changes. The intermediate in step 9 (`parsed.dt.dayofweek` floats with NaN) is already printed by the narration's middle run.

**PLAN.** none.

## 10. aice-split

**Goal and progression.** The objectives "X와y의 관측 대응·분할 크기·반환 순서를 이해해요", "재현성·층화·시간순서의 다른 조건을 구별해요", "훈련·검증·테스트의 목적을 나누고 실제 짝을 검증해요" are well matched. Chapter 1 covers pairing (index lookup), shuffle=False, ceil of test_size and seed reproducibility. Chapter 2 covers joint split, stratify and the stratify guard. Chapter 3 covers time order, validation-only selection and return order, then a stratified challenge. The data are plain Python lists, so this is the AICE lesson where the code-flow viewer fits best. The manifest has prerequisites []. The PRD prerequisite "리스트·같은 위치·길이·입력X와정답y를 알아요" is covered by python-start (1) and features (9).

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | a030d467 | X.index로 짝인 정답 | code | minor | APPLY | unused train_test_split import |
| 2 | 1.1.2 | c849475b | shuffle=False | code | ok | NOT-APPLY | zip pairs printed |
| 3 | 1.1.3 | dec76d8e | math.ceil 테스트 개수 | code | ok | NOT-APPLY | |
| 4 | 1.1.4 | 125d3f0b | random_state 재현 | code | minor | NOT-APPLY | unused y |
| 5 | 2.1.1 | 7d85ed0d | train_test_split(X, y) 함께 | code | ok | APPLY | output is only True/False |
| 6 | 2.1.2 | 8fca0f0f | stratify=y | code | ok | NOT-APPLY | counts printed |
| 7 | 2.1.3 | 2863adfd | 층화 가능 조건 | code | ok | NOT-APPLY | |
| 8 | 3.1.1 | c1e90236 | sorted 뒤 나누기 | code | ok | NOT-APPLY | train/test printed |
| 9 | 3.1.2 | 53e1abb6 | 검증 점수로 설정 | code | ok | NOT-APPLY | dicts are literals |
| 10 | 3.1.3 | 58dfc422 | 반환값 자리 | code | minor | NOT-APPLY | vague 할 일, caution target |
| 11 | 3.2.1 | 4664135d | 층화해 함께 나누기 | code | defect | NOT-APPLY | stratify edit changes nothing visible |

**Defects.**
- [defect] step 11 (stp_4664135d) narration and data. The real run outputs are "6 2\n2\nTrue" (starter), "4 4\n2\nTrue" (after test_size=test_count) and "4 4\n2\nTrue" (after stratify=labels). The stratify edit, which is the second of the two required changes, produces no visible difference. The narration covers this with "크기는 맞췄어요. 아직 범주별 비율은 고정하지 않았어요." while the output already shows the required "평가 중 지연은 2건". This breaks "조건 하나를 바꾼 뒤 실제 결과를 비교한다". Grading still rejects a non-stratified answer through the variants, so the learner cannot see why. Fix: pick a random_state for which the unstratified 4/4 split puts 1 or 3 delays in the test set (verify with the real run), and update the goal sentence and narration to the observed counts.
- [minor] step 11 narration patch says copy the student's imperative ("평가 크기를 test_count로 정하세요.", "정답 labels의 비율을 지키도록 층화하세요."). The teacher should narrate what they do ("평가 크기를 test_count로 바꿔요."). The caution "입력과 정답을 따로 섞으면 같은 위치가 다른 배송을 가리킬 수 있어요" repeats step 5's lesson while highlighting the stratify argument. Make it about stratify, for example that stratify=labels fails when a class has one row, as taught in step 7.
- [minor] step 1 (stp_a030d467) starter and solution: "from sklearn.model_selection import train_test_split" is never used. It violates content-rules section 4. Remove it.
- [minor] step 4 (stp_125d3f0b) starter and solution: `y = [10, 20, 30, 40, 50, 60]` is never used, because only X is split. Remove y and the comment "각 위치의 입력과 정답은 같은 배송을 나타내요" or split both.
- [minor] step 10 (stp_58dfc422) 할 일: "2. 문제가 말한 한 곳을 고치세요." is vague. Write "2. 마지막 두 반환 변수의 순서를 고치세요.", which the goal already states. The caution "변수 이름만 보고 맞다고 믿지 말고 짝도 확인해요." uses target `output`, but it is about the assignment line.
- [minor] student-visible text missing spaces: lesson objective "X와y의 관측 대응" and unit premise "거리1~6인 여섯 배송과 시간10~60이".

**Visualizer details.**
- APPLY step 1 (stp_a030d467). Use `code_flow` on line `print(answer)` with event step_line and target flow_memory, run on the solution after the patch. The viewer shows X = [3, 5, 1, 6, 2, 4] and y = [30, 50, 10, 60, 20, 40] element by element with answer = 50, so the learner sees that index 1 holds 5 in X and 50 in y. The printed "50" cannot show that pairing, and the starter's y[5] = 40 sits at the other end of the same lists. The tracer needs nothing new here because these are plain lists.
- APPLY step 5 (stp_7d85ed0d). Use `code_flow` on line `print(all(target == distance * 10 for distance, target in zip(X_test, y_test)))` with event step_line (nth 1) and target flow_memory, run on the starter before the patch. train_test_split returns plain lists for list input (verified: X_test = [1, 2], y_test = [40, 60]). The viewer shows X_test and y_test side by side, so the learner sees inputs 1 and 2 paired with answers 40 and 60, while the output is only "False\n2 2". Close the flow, patch, and optionally reopen to show [1, 2] with [10, 20].
- Not applied: step 10's swapped names (y_test = [10, 20, 30, 40]) would also show in the viewer, but the printed lengths and pairs "4 2 2 4" and "[(5, 10), (6, 20)]" already expose it.

**PLAN.**
- Step 11 needs a data or seed change so that stratify is observable (see defect).

## 11. aice-leakage

**Goal and progression.** The objectives "정답·미래 정보·평가 통계가 입력과 기준에 섞임을 구별해요", "행 분리와 그룹·시간 목표의 차이를 이해해요", "훈련에서 정한 기준을 평가 자료에 적용해요" are covered: target column (1), future column (2), train-only mean (3), train-only median fill (4), customer split with isin (5), GroupShuffleSplit (6), past-only mean (7), transfer (8), challenge (9). The repetition is heavy. Steps 3, 4, 7 and 8 are all "replace a statistic computed on more data with train.mean()/median()". Steps 3 and 8 use the same train [10, 20] and test [100]/[None, 100] numbers and the same `pd.concat([train, test]).mean()` starter, so step 8 adds only the mean-versus-median trap. The manifest has prerequisites []. The PRD audience "입력 선택·훈련/테스트 분리를 익힌" matches orders 9 and 10.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | b120ab2e | drop으로 정답 열 | code | ok | NOT-APPLY | columns printed |
| 2 | 1.1.2 | e9432c56 | delivered_at도 빼기 | code | ok | NOT-APPLY | |
| 3 | 1.1.3 | a5aebc2b | train.mean() | code | ok | NOT-APPLY | |
| 4 | 1.1.4 | ddedb308 | train.median() 채움 | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | 85918482 | isin 고객 단위 | code | ok | NOT-APPLY | minutes per side printed |
| 6 | 2.1.2 | 4dd87189 | GroupShuffleSplit | code | minor | HOLD-OPAQUE | unused ShuffleSplit import; index ndarrays |
| 7 | 2.1.3 | fdfa09bb | 과거만의 기준 | code | minor | NOT-APPLY | off-topic caution |
| 8 | 2.1.4 | 0fa722a5 | 훈련 기준 하나로 채워요 | code | ok | NOT-APPLY | transfer step, ends unsolved by design |
| 9 | 2.2.1 | aea6a5c7 | 접수 시점의 열과 훈련 기준 | code | minor | NOT-APPLY | imperative narration |

**Defects.**
- [minor] step 6 (stp_4dd87189) solution: "from sklearn.model_selection import ShuffleSplit, GroupShuffleSplit". ShuffleSplit is unused after the fix, which violates content-rules section 4. The starter needs it, so either accept the exception and document it, or have the starter use `GroupShuffleSplit(...).split(rows)` without groups, which treats every row as its own group, and make the edit add `groups=groups` and test_size=1.
- [minor] step 7 (stp_fdfa09bb) caution: "조심하세요. 날짜순으로 정렬했다고 미래 값이 기준에서 빠지지는 않아요. 시점으로 행을 걸러요." Nothing in the step sorts, and the starter's mistake is using `df` instead of the already filtered `train`. The contrast has no basis, the same pattern narration.md calls out for Bash 9. Suggested: "조심하세요. train을 걸러 놓고도 기준 줄에서 df를 쓰면 미래 관측이 다시 섞여요."
- [minor] step 9 (stp_aea6a5c7) narration patch says copy the student's 할 일 imperatives ("빈칸을 채울 평균은 훈련 자료에서만 구하세요.", "두 입력 표에서 정답과 미래 정보를 빼고 distance만 남기세요."). The teacher should narrate their own action. The opening say repeats the goal's first sentence verbatim ("예측 시점의 입력 열을 고르고 훈련에서 구한 기준을 평가에도 적용해요.").
- [minor] step 3 (stp_a5aebc2b) solution: `test` is assigned and unused after the fix. It is pedagogically intentional (the held-out value stays visible), so this is a nit only.

**Visualizer details.** Step 6 is HOLD-OPAQUE. `train` and `test` from `split()` are numpy index arrays (verified: ShuffleSplit gives test = [5 2] and train = [1 3 0 4]; GroupShuffleSplit gives test = [4 5]). The output shows only counts "2 2 / True". A small 1-D ndarray element view (shape (2,), values) next to the plain `groups` list would show rows 5 and 2 belonging to C and B, and after the fix rows 4 and 5 both belonging to C. Since these arrays are tiny, a "show ndarray values when size ≤ 20" rule in mq_pytrace.py would make this an APPLY.

**PLAN.**
- Collapse steps 3, 7 and 8 or vary them. Keep step 3 (train-only mean) and step 7 (time cut-off), and turn step 8 into the only fill step (merge it with step 4's median fill so the mean-versus-median trap stays). That frees one slot for a case the lesson lacks, such as a target-derived feature that is not named after the target (for example `minutes_bucket`).

## 12. aice-scale

**Goal and progression.** The objectives "fit·transform·fit_transform의 차이를 이해해요", "상수·결측·범위 밖 값과 미지 범주의 결과를 판단해요", "전처리 순서와 훈련 기준을 평가 자료에서도 유지해요" are well matched. Steps 1-4 cover fit, transform-only, constant-column scale and NaN passthrough. Steps 5-7 cover MinMax clip, RobustScaler and OneHotEncoder handle_unknown. Steps 8-10 cover Pipeline transform, a transfer and the challenge. The "don't refit on test" idea appears four times (steps 2, 8, 9, 10). Step 9 is nearly the same as step 2 on the same data ([[0], [2]], [[10]]). The manifest has prerequisites []. The PRD claims sklearn 1.3.2. `OneHotEncoder(sparse_output=...)` exists from 1.2, so this holds for the exam (it would fail on sklearn below 1.2).

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | ec7b214c | scaler.fit(train_values) | code | ok | NOT-APPLY | mean_ and scale_ printed |
| 2 | 1.1.2 | c105cd46 | transform만 | code | ok | NOT-APPLY | mean_ printed |
| 3 | 1.1.3 | bdd1f399 | 평균과 스케일로 직접 계산 | code | ok | NOT-APPLY | |
| 4 | 1.1.4 | e44ecbb2 | pd.isna로 결측 | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | 11b21559 | clip=False | code | ok | NOT-APPLY | |
| 6 | 2.1.2 | bf8bf644 | RobustScaler | code | minor | NOT-APPLY | unused StandardScaler import |
| 7 | 2.1.3 | e7107d01 | handle_unknown="ignore" | code | ok | NOT-APPLY | |
| 8 | 2.1.4 | 57e5b581 | prep.transform | code | ok | NOT-APPLY | statistics_ and mean_ printed |
| 9 | 2.1.5 | 8e6b11a1 | 학습한 기준으로만 변환 | code | minor | HOLD-OPAQUE | typo in objective; mean_ overwrite not visible |
| 10 | 2.2.1 | d9e36990 | 훈련 평균으로 채운 뒤 표준화 | code | minor | NOT-APPLY | imperative narration |

**Defects.**
- [minor] step 6 (stp_bf8bf644) solution: "from sklearn.preprocessing import StandardScaler, RobustScaler". StandardScaler is unused after the fix, which violates content-rules section 4. The same exception question applies as in leakage step 6.
- [minor] step 9 (stp_8e6b11a1) visible step objective: "fit한 스케일러를 평가에서 다시학습하지 않고 적용해요." is missing a space ("다시 학습하지").
- [minor] step 10 (stp_d9e36990) narration patch says copy imperatives ("훈련 평균으로 빈칸을 채우도록 바꾸세요.", "평가 자료에서는 fit 없이 transform만 사용하세요."). The opening say repeats the goal's first sentence verbatim. The second run prints "[8.0]\n[8.0]\n[[0.0], [0.0]]", but the narration ("빈칸 기준은 평균으로 바꿨어요. 평가에서 다시 fit하면 여전히 평가 기준이 돼요.") never names the 8 that proves the refit. Say "채움 값과 중심이 평가 평균 8이 됐어요."
- [minor] student-visible unit premise: "학습에 쓸 거리는0과2예요. 남겨둔 새 배송 거리10에는" is missing spaces ("거리는 0과 2예요. 남겨 둔 새 배송 거리 10에는").

**Visualizer details.** Step 9 is HOLD-OPAQUE. The bug is that the second `scaler.fit(test_values)` overwrites the learned mean, and the step prints only the final "[[0.0]]". A viewer that summarized a fitted estimator's attributes (mean_ [1.0] becoming [10.0], scale_, n_samples_seen_ 2 becoming 1) at line `scaler.fit(test_values)` (step_line, nth 1, then the next line) would show the overwrite directly. Today the StandardScaler is an opaque type name. Steps 1, 2 and 8 print the same attributes, so they do not need it.

**PLAN.**
- Cut the refit repetition. Step 9 duplicates step 2 on the same numbers. Either drop it, or make it the distinct "second fit overwrites" case by printing `scaler.mean_` before and after the second fit, which turns it into an observation step without any viewer change.


## 13. aice-regression

**Goal and progression.** The objectives ("수치 목표·단순 기준 모델·선형 회귀의 역할을 이해해요", "객체 생성·학습·예측과 입력 모양을 구별해요", "훈련 적합과 남겨둔 자료의 예측을 따로 검증해요") match the steps. Steps 1 to 4 each add one idea (baseline, LinearRegression, fit, 2D input). Steps 5 to 8 check the intercept, the input range, and held-out error. Step 9 combines baseline vs regression on held-out MAE. Every edit is one line. The PRD lists prerequisites ("입력X·정답y·훈련기준·행과열모양을알아요"), but the manifest has prerequisites []. Step 8 ("남겨둔 입력을 예측해요") is an easier repeat of step 7, which already predicts X_test, so it reads as a step backwards.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 086a54a7 | strategy="mean" baseline | code | ok | NOT-APPLY | output shows the constant |
| 2 | 1.1.2 | 1957de0a | LinearRegression | code | minor | NOT-APPLY | unused import |
| 3 | 1.1.3 | 6387f297 | model.fit before predict | code | ok | HOLD-OPAQUE | estimator before/after fit |
| 4 | 1.1.4 | cedb6bf5 | [[distance]] 2D input | code | ok | APPLY | nested list shape is invisible in output |
| 5 | 2.1.1 | c506900c | + intercept_ | code | ok | NOT-APPLY | both values printed |
| 6 | 2.1.2 | 1e92ac56 | 실행 성공과 현실의 타당성 | predict (choice + example_code) | ok | NOT-APPLY | |
| 7 | 2.1.3 | 5882472b | X_test/y_test error | code | ok | NOT-APPLY | |
| 8 | 2.1.4 | f34a161e | 남겨둔 입력을 예측해요 | code | minor | NOT-APPLY | repeat of 7, vague 할 일 |
| 9 | 2.2.1 | 8f967e0e | baseline vs regression MAE | code | minor | NOT-APPLY | goal pre-states result |

**Defects.**
- [minor] step 2 (stp_1957de0a) solution: keeps `from sklearn.dummy import DummyRegressor` after the fix replaces its only use with `LinearRegression()`. content-rules section 4 says the solution has no unused import. Drop it from the solution. The starter still needs it.
- [minor] step 8 (stp_f34a161e) goal: "남겨둔X_test를 예측하도록 인수만 고치세요." is missing a space. 할 일 item 2, "문제가 말한 한 곳을 고치세요.", is the vague wording voice.md forbids. Write "`model.predict(X_train)`의 `X_train`을 `X_test`로 고치세요."
- [minor] step 9 (stp_8f967e0e) goal: "지금 자료의 평가 예측은 7분과 9분이고 회귀의 MAE는 0이에요." gives away the expected output before the first run, which prints `[3.0, 3.0]` and `5.0`. Drop the sentence or move it into the narration.
- [minor] step 9 (stp_8f967e0e) narration: the last read, "같은 평가 배송에서 평균 기준과 회귀의 오차를 비교했어요.", names no value. The real run prints `5.0` and `0.0`, and those numbers are what the comparison is about.

**Visualizer details.**
- APPLY step 4. Line 10 is `model = LinearRegression()`. Use event step_line and target flow_objects, once before the patch and once after. Before the patch the viewer shows `X_test` as a list holding 4. After it, `X_test` is a list holding a list holding 4. That is the "한 행 한 열" shape the goal describes, and the printed output never shows it (the starter only prints a ValueError).
- HOLD-OPAQUE step 3. `model` is an estimator. A summary that lists fitted attributes would show what fit adds: no `coef_` before fit, then `coef_=[10.]` and `intercept_=0.0` after. Today the viewer shows only a type name.

**PLAN.**
- Replace step 8 with one new condition, or delete it. Two examples are predicting two held-out rows at once, or a held-out row whose answer is far off the line. As written, step 8 repeats step 7 in an easier form.

## 14. aice-regression-metrics

**Goal and progression.** The objectives (sign, MAE, MSE, RMSE, R² edge cases, alignment) map one to one onto steps 1 to 7. In each of those steps the student changes one expression and checks it against the sklearn function, which works well. Step 8 asks for RMSE again as a transfer step, although step 2 already taught it. Step 9 combines alignment with RMSE but brings in `pd.Series.reindex`, which no earlier step taught (step 7 aligned with `list.index`). On versions, `r2_score(force_finite=True)` exists from sklearn 1.1, so it works on the exam's 1.3.2, and `** 0.5` is version-safe where `squared=False` would not be.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | fd8637f1 | mean_absolute_error | code | ok | NOT-APPLY | errors list printed |
| 2 | 1.1.2 | 86d4e40b | ** 0.5 RMSE | code | ok | NOT-APPLY | |
| 3 | 1.1.3 | a47e998f | MSE picks candidate | code | ok | NOT-APPLY | |
| 4 | 1.1.4 | 1d5be83b | sst from mean, R² | code | ok | APPLY | sse/sst never printed |
| 5 | 2.1.1 | aa77cd65 | len(set(y_true)) constant | code | ok | NOT-APPLY | |
| 6 | 2.1.2 | 51c8e8eb | R² only if n>=2 | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | c1326c0e | align by pred_ids | code | ok | NOT-APPLY | aligned printed |
| 8 | 2.1.4 | 08c238c2 | 분 단위 오차로 보고해요 | code | minor | NOT-APPLY | narration stops before the fix |
| 9 | 2.2.1 | 8c2d0bff | align + three metrics | code | minor | HOLD-OPAQUE | Series order |

**Defects.**
- [minor] step 8 (stp_08c238c2) solution: `mean_absolute_error` stays imported, but `score = mean_squared_error(y_true, y_pred) ** 0.5` no longer uses it. Drop it from the solution.
- [minor] step 8 (stp_08c238c2) narration: it tries MSE (`12.0`), reverts to MAE, and ends on the caution. It never runs the `** 0.5` fix: the real outputs are only `'2.0' || '12.0'`. If this transfer slot is meant to leave the last edit to the student, record that in the PRD. Otherwise add the last patch and run (`3.464102`). content-rules section 1 asks for a run, a result read, and a submit after the last piece.
- [minor] step 9 (stp_8c2d0bff) goal: "지금 결과는 2.666667, 3.265986, 0.84예요." is false, because the starter prints `16.0 / 290.666667 / -3.36`. Write "목표 결과는", or drop the numbers.
- [minor] step 9 (stp_8c2d0bff) narration: the last read, "같은 배송끼리 비교한 세 지표가 각각 출력됐어요.", names no value.

**Visualizer details.**
- APPLY step 4. Line 10 is `print(round(1 - sse / sst, 6))`. Use event step_line and target flow_memory, before and after the patch. The viewer shows `mean=20.0` and `sse=19400`, and `sst` goes from 1400 (measured from 0) to 200 (measured from the mean). Only the final ratio is ever printed, so this is the one place the learner can see why the result jumps from -12.857143 to -96.0. The genexpr frames live in main.py and add a few trace steps per element, well inside the budget.
- HOLD-OPAQUE step 9. `predicted` and `aligned` are pandas Series. A summary view of index and values would show what `reindex` does: `103:34, 101:10, 102:16` becomes `101:10, 102:16, 103:34`. Today both show as opaque type names.

**PLAN.**
- Before the challenge, add a step that teaches only `Series.reindex`. The alternative is to rewrite step 9 around the list alignment from step 7, for example `[guesses[k] for k in truth]`.

## 15. aice-classification

**Goal and progression.** The objectives (regression vs classification, baseline/tree/logistic, proba columns, ties, a single class, train vs test) match the steps, with one new idea per step. Step 8 ("새 배송이 늦을 확률을 골라요") repeats step 3: same data, same fix `list(model.classes_).index("late")`, same expected output `"['late', 'on-time']\n[0.0, 1.0]"`. Its demo that renames the labels to early/late is a good counterexample, but the step adds no new requirement. Step 9 combines the proba column with an inclusive threshold.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 37f40162 | DummyClassifier | code | minor | NOT-APPLY | unused import |
| 2 | 1.1.2 | b62727bb | DecisionTreeClassifier | code | minor | NOT-APPLY | unused import |
| 3 | 1.1.3 | 4b0c2a3f | classes_ late column | code | ok | HOLD-OPAQUE | proba matrix |
| 4 | 1.1.4 | 3656e0c7 | predict_proba confidence | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | f450ad4f | LogisticRegression | code | minor | NOT-APPLY | unused import |
| 6 | 2.1.2 | 7a031f9d | len(set(y_train)) | code | ok | NOT-APPLY | branch message printed |
| 7 | 2.1.3 | 96f23ee4 | score on test | code | ok | NOT-APPLY | |
| 8 | 2.1.4 | a1d61609 | 늦을 확률 열 | code | minor | NOT-APPLY | duplicate of step 3 |
| 9 | 2.2.1 | 91a6a75b | late column + >= threshold | code | minor | NOT-APPLY | alarms printed |

**Defects.**
- [minor] steps 1, 2, 5 (stp_37f40162, stp_b62727bb, stp_f450ad4f) solution: after the fix removes their only use, these imports stay: `DummyRegressor` in step 1, `DummyClassifier` in step 2, `LinearRegression` in step 5 (content-rules section 4).
- [minor] step 8 (stp_a1d61609): it repeats step 3, and the narration never applies the fix. The two runs are the starter and the early/late demo.
- [minor] step 9 (stp_91a6a75b) goal: "지금 확률은 0과 1이고 경보는 False, True예요." does not match the starter, which prints `[1.0, 0.0]` and `[False, False]`. Write "목표 결과는".

**Visualizer details.**
- HOLD-OPAQUE step 3. The fix is about which column of the 2x2 ndarray from `predict_proba(X_test)` holds "late". A value view of the ndarray (shape (2, 2), rows `[1, 0]` and `[0, 1]`) next to `classes_=['late', 'on-time']` would show the column mapping directly. Two things block it. The viewer shows ndarrays as opaque, and the matrix is never bound to a name, so the code would also need `proba = model.predict_proba(X_test)`.

**PLAN.**
- Replace step 8 with a new condition, or delete it. Two options are a three-class problem with "late" in the middle column, or integer labels 1/2 where the column index differs from the label value.

## 16. aice-classification-metrics

**Goal and progression.** The PRD scope says "두 챕터·세 단원·열한 스텝", and the lesson has eleven steps. The order runs recall vs accuracy, the confusion matrix, hand-computed precision and recall checked against sklearn, F1, zero division, the weighted average, the threshold, AUC, and pos_label. That ladder adds one concept per step with one-line edits. Steps 3 to 5 check a hand computation against the library, which suits this lesson. Step 10 is a vague "한 곳" transfer step. Step 11 combines the threshold with pos_label.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 5b329bfe | recall vs accuracy | code | minor | NOT-APPLY | unit title says four deliveries |
| 2 | 1.1.2 | 2ffbd6d9 | matrix[0][1] | code | ok | NOT-APPLY | matrix printed |
| 3 | 1.1.3 | 2e612a83 | precision = hits/sum(y_pred) | code | ok | APPLY | hits never printed |
| 4 | 1.1.4 | b27cca7c | recall = hits/sum(y_true) | code | ok | NOT-APPLY | same flow as 3 |
| 5 | 1.1.5 | eed7aac5 | F1 harmonic mean | code | ok | NOT-APPLY | |
| 6 | 2.1.1 | aa3381bd | precision only if alarms | code | ok | NOT-APPLY | |
| 7 | 2.1.2 | 99dd345c | weighted recall | code | ok | NOT-APPLY | per_class, support printed |
| 8 | 2.1.3 | 94efe060 | threshold | code | ok | NOT-APPLY | predictions printed |
| 9 | 2.1.4 | 404f7997 | roc_auc_score | code | minor | NOT-APPLY | unused import |
| 10 | 2.1.5 | 992c4142 | pos_label | code | minor | NOT-APPLY | vague 할 일 |
| 11 | 2.2.1 | 208e0760 | threshold + late metrics | code | minor | APPLY | predicted never printed |

**Defects.**
- [minor] step 1 (stp_5b329bfe): the unit title "배송 경보 네 건의 검토" fits steps 2 to 5. Step 1 uses ten deliveries (`y_true = [0] * 9 + [1]`).
- [minor] step 9 (stp_404f7997) solution: `accuracy_score` stays imported after the fix (content-rules section 4).
- [minor] step 10 (stp_992c4142) 할 일: "문제가 말한 한 곳을 고치세요." is vague. Write "`pos_label=\"ok\"`를 `pos_label=\"late\"`로 고치세요."
- [minor] step 11 (stp_208e0760) goal: "현재 결과는 0.666667, 1.0, 0.8이에요." does not match the starter, which prints `0.5 / 0.5 / 0.5`. Write "목표 결과는".
- [minor] step 11 (stp_208e0760) narration: the last read never mentions the F1 value `0.8`.

**Visualizer details.**
- APPLY step 3. First, line 7 is `hits = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)`. Use event step_line inside the genexpr frame at the pair where t=1 and p=1, the fourth pair (nth about 4; confirm on the real trace), with target flow_memory. Then line 9 is `precision = hits / len(y_true)`. Use event step_line with flow_memory showing `hits=1`. The learner sees which pair counts as a hit, and that `hits` is 1 while the denominator is 4 in the starter and 2 after the fix. Neither value is printed. Skip step 4, which reuses the same line.
- APPLY step 11. Line 7 is `positive = "ok"`. Use event step_line and target flow_memory, before and after the first patch. The viewer shows `predicted = ['late', 'ok', 'late', 'ok']` becoming `['late', 'late', 'late', 'ok']`. That is the alarm list every metric is computed from, and it is never printed.

**PLAN.** none.

## 17. aice-models

**Goal and progression.** The objectives (settings vs learned state, target type, input units, API, training score, importance) match the steps. The steps cover the depth limit, forest size, regressor vs classifier, scaling for KNN, SVC decision_function, choosing on validation, and importance vs cause, then a transfer step and the challenge. Each step adds one concept with a one-line edit. The PRD scope says "두 챕터·두 단원·아홉 스텝", but the lesson has three units: one in chapter 1, plus "같은 후보의 검증 보고" and "마지막 도전" in chapter 2. Step 8 ("요청한 나무 수를 설정해요") tests the tree count from step 2 again.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | cffde00e | max_depth=1 | code | ok | NOT-APPLY | get_depth printed |
| 2 | 1.1.2 | 818da7c1 | len(estimators_) | code | ok | NOT-APPLY | |
| 3 | 1.1.3 | 227a9af7 | RandomForestRegressor | code | minor | NOT-APPLY | unused import |
| 4 | 1.1.4 | 7ba7284a | scaler + KNN pipeline | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | b186dda1 | SVC decision_function | code | ok | NOT-APPLY | |
| 6 | 2.1.2 | e1fc091c | validation choice | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | ba77c57b | 중요도는 원인 증명이 아니에요 | predict (choice + example_code) | minor | NOT-APPLY | example hides the split |
| 8 | 2.1.4 | 0964bcb0 | 요청한 나무 수 | code | minor | NOT-APPLY | repeat of 2, vague 할 일 |
| 9 | 2.2.1 | 8f1aa06f | validation MSE, min | code | minor | NOT-APPLY | scores dict printed |

**Defects.**
- [minor] step 3 (stp_227a9af7) solution: `RandomForestClassifier` stays imported after the fix.
- [minor] step 7 (stp_ba77c57b) interaction option: "아니요.학습 내부 중요도와 인과 증명은 달라요" is missing a space after the period.
- [minor] step 7 (stp_ba77c57b) example_code: it prints only `len(model.feature_importances_)` and the sum (`2`, `1.0`). The narration's claim "복제·상관된 정보가 나뉠 수 있고" therefore has no evidence on screen. A local run (sklearn 1.9.0) gives `[0.33333333 0.66666667]` for the two identical columns. Printing `model.feature_importances_.round(3).tolist()` would show two copies of the same information getting different importance. Recheck the value on 1.3.2.
- [minor] step 8 (stp_0964bcb0) 할 일: "문제가 말한 한 곳을 고치세요." is vague, and the problem repeats step 2.
- [minor] step 9 (stp_8f1aa06f) goal: "현재 mean의 MSE는 25, tree는 0이므로 tree를 골라야 해요." does not match the starter, which prints `{'mean': 25.0, 'tree': 50.0}`, and it gives away the answer. The starter also already prints `tree` as the winner, for the wrong reason (the max of the wrong scores). The caution "훈련 점수가 좋은 후보를 고르면 새 배송에서의 성능 비교가 빠져요" warns about a mistake this step does not contain. The real mistakes here are the wrong targets and max instead of min. A caution like "MSE는 작을수록 좋아요" fits.

**Visualizer details.** No APPLY. The `models` dict in step 9 holds opaque estimators, and the scores dict is printed.

**PLAN.**
- Fix the PRD unit count, or merge the units.
- Replace step 8 with a new condition, or delete it.

## 18. aice-boosting

**Goal and progression.** The objectives ("XGBoost 래퍼의 회귀·분류 학습을 실제 실행해요", "학습률·반복수·다중범주·평가기록의 역할을 구별해요", "버전 차이를 인식하고 실제 학습 상태로 결과를 검증해요") match the steps. Steps 3 and 4 have the student hand-compute one boosting step and the residual the second tree learns, which is a strong principle-first design. The PRD scope says "0.90과 현재 배포에 공통인 래퍼 호출만 써요", and its sources cite the 0.90 docs and the 2.1.4 source. I fetched v0.90 `python-package/xgboost/sklearn.py` and `core.py` from the GitHub tag. Two steps break the claim. Step 8 is a transfer step that repeats the learning-rate idea from step 3.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | f7586250 | model.fit | code | minor | NOT-APPLY | 0.90 error type differs |
| 2 | 1.1.2 | 7e3eb3df | XGBRegressor | code | defect | NOT-APPLY | starter passes on 0.90 |
| 3 | 1.1.3 | 9efe7d1f | rate * (m - 0.5) | code | ok | NOT-APPLY | both lists printed |
| 4 | 1.1.4 | d8241bd8 | residuals from predicted | code | ok | NOT-APPLY | residuals printed |
| 5 | 2.1.1 | 1348e253 | encoder.classes_ column | code | minor | HOLD-OPAQUE | encoded y_train |
| 6 | 2.1.2 | a655e001 | rounds * classes trees | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | 54004ba7 | best round from rmse | code | ok | NOT-APPLY | rmse list printed |
| 8 | 2.1.4 | 62892202 | 정한 반영 크기 | code | minor | NOT-APPLY | narration stops before the fix |
| 9 | 2.2.1 | a5d75177 | rounds + rate | code | defect | NOT-APPLY | API missing on 0.90 |

**Defects.**
- [defect] step 2 (stp_7e3eb3df) goal and narration: "1. 코드 실행을 눌러 ValueError가 나오는지 확인하세요." and "분류기는 범주 번호 0과 1을 기대했는데 2와 8을 받았어요." In xgboost 0.90, `XGBClassifier.fit` label-encodes y itself (sklearn.py line 701, `self._le = XGBLabelEncoder().fit(y)`), and `predict` returns `self._le.inverse_transform(column_indexes)` (line 801). On the exam's 0.90, the starter therefore raises no error and most likely prints the expected `[2.0, 2.0, 8.0, 8.0]`. This is inferred from the source; I did not run 0.90. The premise holds only on xgboost 1.6 and later (the runner has 2.1.4). Fix: teach regressor vs classifier with a signal both versions share, for example a target like 2.5 turning into its own class, or `predict_proba` existing only on the classifier. Otherwise, state the version difference in the goal.
- [defect] step 9 (stp_a5d75177) starter and solution: `print(model.get_booster().num_boosted_rounds())`. v0.90 `core.py` has no `num_boosted_rounds`, so both raise AttributeError on the exam version. Fix: use `len(model.get_booster().get_dump())`. Steps 6 and 7 already use it, and it exists in 0.90 (core.py line 1408).
- [minor] step 1 (stp_f7586250) goal: "NotFittedError가 나오는지 확인하세요". On 0.90, predicting before fit raises `XGBoostError('need to call fit or load_model beforehand')` (sklearn.py line 193). Describe the error without naming its class, or name both.
- [minor] step 5 (stp_1348e253) goal: "XGBClassifier는 0부터 센 범주 번호를 받아서, 문자 정답은 `LabelEncoder`로 번호를 만들어 넘겨요." This is required on 1.6 and later but optional on 0.90, which encodes internally. The code runs on both, so only the sentence needs a version qualifier.
- [minor] step 8 (stp_62892202) narration: it changes `rate` to show the model ignores it, reverts, and ends without running the `learning_rate=rate` fix. Both real outputs are `1.0\n[2.0, 8.0]`. This is the same pattern as aice-regression-metrics step 8.
- [minor] step 9 (stp_a5d75177) goal: "현재 두 번·0.5 비율이면 예측은 1.625와 6.125예요." states the target output up front.

**Visualizer details.**
- HOLD-OPAQUE step 5. `y_train = encoder.fit_transform(labels)` is the ndarray `[1, 1, 0, 0]`. A value view next to `labels` would show "late" becoming 0, which is why the late column is 0. The fitted `encoder` (its `classes_`) is opaque too.
- Every other step already prints the numbers the viewer would show (`leaf_means`, `expected`, the residuals, the `rmse` list), and the XGB models are opaque.

**PLAN.**
- Re-run the whole lesson on a real xgboost 0.90 (target/aice-exam-env, if 0.90 installs on Python 3.10). Default objectives also differ between versions (`reg:linear` on 0.90 vs `reg:squarederror`), and steps 1 to 4 and 7 leave `objective` unset. Record per step which behavior is version-specific, as the PRD's "실행기 버전과 실제 시험 환경의 일치 여부를 분리해서 기록한다" requires.
- Replace step 8 with a new condition, or delete it.

### Cross-lesson pattern (lessons 13-18)

- Each lesson's "x.1.4" or "2.1.5" transfer step has three weaknesses. It repeats an earlier step's concept (13-8 repeats 7, 14-8 repeats 2, 15-8 repeats 3, 16-10 repeats 1, 17-8 repeats 2, 18-8 repeats 3). Its 할 일 is vague ("문제가 말한 한 곳을 고치세요"). In 14-8, 15-8, and 18-8 the narration also stops before the fix. These look like a later template layer, since their REJECT reasons are long English sentences. PLAN: rewrite each one so it adds a real new condition and names the edit.
- Each final-challenge goal states the target result as "지금/현재 결과는…", which contradicts the starter's first run (13-9, 14-9, 15-9, 16-11, 17-9, 18-9). The final narration reads also skip the actual numbers.
- The solutions keep imports their only use no longer needs (13-2, 14-8, 15-1, 15-2, 15-5, 16-9, 17-3). Either the redesigned builder does not run `drop_unused_imports`, or it does not apply that rule to these imports.


## 19. aice-tuning

**Goal and progression.** Objectives "후보 수·교차검증·점수·최종 재학습의 흐름을 이해해요." and "음수 오차 점수와 Pipeline의 훈련 경계를 구별해요." map one to one onto steps 1-6 (ParameterGrid count, StratifiedKFold, cv mean, refit, neg MSE direction, Pipeline inside CV). Step 7 is the judgment check on the sealed test set and steps 8-9 combine the `model__` path with the sign flip, so introduce, practice, combine holds. Every step is a one-line edit on an 8-row toy table, one new concept each. The PRD prerequisite "훈련과 남겨둔 평가 자료의 구분을 알아요." relies on aice-split and aice-leakage, but the manifest lists prerequisites []. The PRD cites sklearn 1.3 docs and claims verification on 1.3.2. Nothing here is version-sensitive (refit=False then `best_estimator_` raises AttributeError on 1.3.2 too).

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | f9407ed7 | ParameterGrid 조합 수 | code | ok | NOT-APPLY | output prints 5 vs 6 |
| 2 | 1.1.2 | 3151ed86 | StratifiedKFold | code | minor | HOLD-OPAQUE | KFold unused after swap |
| 3 | 1.1.3 | 5aecea73 | scores.mean() | code | ok | NOT-APPLY | |
| 4 | 1.1.4 | 60ac6a4e | refit=True | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | e1171e0a | 음수 오차 점수 방향 | code | ok | NOT-APPLY | |
| 6 | 2.1.2 | 9651646a | Pipeline에 원래 X_train | code | ok | NOT-APPLY | X_scaled kept as contrast, fine |
| 7 | 2.1.3 | 128934cb | 최종 평가 표 선택 금지 | choice+predict (example_code) | minor | NOT-APPLY | option typos |
| 8 | 2.1.4 | d3301ce8 | 파이프라인 설정 이름 | code (representative) | minor | NOT-APPLY | vague 할 일, "이름 오류" |
| 9 | 2.2.1 | d425c897 | 마지막 도전 | code | ok | NOT-APPLY | |

**Defects.**
- [minor] step 7 (stp_128934cb) interaction.options: "네.이 표 점수가 좋아질 때까지 반복 선택해요", "아니요.결과를 보고하고 추가 개발에는 새 검증 계획을 세워요". Both options are missing the space after the period (also in courses/redesigned/aice-tuning.json:528,532). Fix: "네. 이 표…", "아니요. 결과를…".
- [minor] step 7 (stp_128934cb) goal: "코드에서 근거를 찾아 결과를 먼저 예상하세요". The question is a policy judgment, not an output prediction, so the predict framing fits poorly. Consider dropping `predict_before_run`.
- [minor] step 8 (stp_d3301ce8) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." It points back into the prose instead of naming the target, which voice.md forbids for guess-the-action items. Fix: "2. 그리드 키 `max_depth`에 단계 이름을 붙여 고치세요."
- [minor] step 8 (stp_d3301ce8) narration: "설정이 파이프라인 자체에 전달돼 이름 오류가 나요." The real error is `ValueError: Invalid parameter 'max_depth' for estimator Pipeline` (checked locally). "이름 오류" reads as NameError. Fix: "ValueError예요. Pipeline 자체에는 max_depth 설정이 없어요."
- [minor] step 2 (stp_3151ed86) solution: `from sklearn.model_selection import KFold, StratifiedKFold` leaves `KFold` unused after the swap (content-rules section 4). This is inherent to a swap exercise. Accept it, or drop `KFold` from the solution import.

**Visualizer details.** Step 2 is HOLD-OPAQUE. The fold loop `for train, valid in cv.split(X_train, y_train):` runs in main.py, but `train` and `valid` are ndarrays and show as opaque. A viewer that showed small 1-D ndarray values (valid = [0 1 2 3] under KFold vs [0 1 4 5] under StratifiedKFold) would make fold membership visible. The `labels` list does show per iteration, and the printed counts already carry the point, so this is low priority. Every other step ends in a printed scalar or list that already shows what matters.

**PLAN.** none.

## 20. aice-tensorflow

**Goal and progression.** Objectives "입력 특성·Dense 출력과 관측 수의 모양을 읽어요." and "구성·compile·fit·predict의 서로 다른 역할을 이해해요." are covered in order: Input shape (1), Dense units (2), predict before fit equals manual matmul (3), compile (4), fit epochs (5), validation_data (6), 2-D predict input (7), representative shape fix (8), challenge (9). It is clean with one concept per step and one-line edits. The manifest has prerequisites [] while the PRD assumes "행·열 모양과 훈련·검증 구분을 알아요.". The PRD itself says "시험 TF2.13.1과 자체 검증 TF2.15.1의 완전 일치를 주장하지 않아요". Steps 1 and 4 depend on Keras 2 behavior: an unbuilt Sequential raises AttributeError on `input_shape`, and `model.optimizer` is None before compile. Both hold on 2.13 and 2.15 and would differ on Keras 3. I did not run them because TF is absent locally.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 9959d907 | Input(shape=(features,)) | code | minor | NOT-APPLY | unused numpy import |
| 2 | 1.1.2 | 5a1d3d07 | Dense(outputs) | code | minor | NOT-APPLY | unused numpy import |
| 3 | 1.1.3 | 5a2c68d7 | X_test @ weights + bias | code | ok | HOLD-OPAQUE | weights/bias arrays |
| 4 | 1.1.4 | c4267d4b | compile SGD mse | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | 9aec3667 | fit epochs=rounds | code | ok | NOT-APPLY | |
| 6 | 2.1.2 | d09cae03 | validation_data | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | c166a1ea | [[d] for d in distances] | code | ok | HOLD-OPAQUE | X_test shape |
| 8 | 2.1.4 | dba81c77 | 입력 특성 수 맞추기 | code (representative) | minor | NOT-APPLY | vague 할 일 |
| 9 | 2.2.1 | 228a312c | 마지막 도전 | code | defect | NOT-APPLY | "현재" sentence false |

**Defects.**
- [defect] step 9 (stp_228a312c) goal and unit premise: "현재 입력은 [2], 예측은 [3, 1]이에요." The starter raises because `Input(shape=(len(rows),))` expects 3 features, and after the first fix the real output is "[2]\n[3, 2]\nTrue". [2] and [3, 1] are the targets, not the current state. Fix: "완성하면 입력 모양 [2], 예측 모양 [3, 1]이 나와야 해요." Lessons 21 and 22 have the same template defect.
- [minor] steps 1 (stp_9959d907) and 2 (stp_5a1d3d07) starter/solution: `import numpy as np` is never used (content-rules section 4). Drop it in both steps.
- [minor] step 8 (stp_dba81c77) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." It is the same vague pattern as lesson 19 step 8. Name the target: "2. `keras.Input`의 shape를 준비된 특성 수 변수로 고치세요."

**Visualizer details.** Step 3 is HOLD-OPAQUE. `weights, bias = model.get_weights()` returns ndarrays of shape (1, 1) and (1,) holding 1.0 and 0.0. A shape plus small-values summary would let the learner check the hand computation before running predict. Step 7 is HOLD-OPAQUE. `X_test = np.array([distances], dtype="float32")` has shape (1, 2) and the fixed version has shape (2, 1). Showing the ndarray shape at the step_line after that line would expose the mistake before predict raises. The comprehension `[[d] for d in distances]` runs in main.py, but its result goes straight into np.array, so only `d` would show. Steps 1, 2 and 4-6 print the shape or flag that carries their point.

**PLAN.** none.

## 21. aice-neural-regression

**Goal and progression.** Objectives "수치 목표 범위·출력 크기·손실을 맞춰요." and "예측 대응과 모델 저장·복원을 검증해요." map onto linear vs relu output (1), loss vs metric (2), history records (3), Dense units (4), evaluate vs predict (5), order alignment (6), saved scaler (7), relu for non-negative time (8, representative), and the relu+mse challenge (9). Steps 1 and 8 form a deliberate contrast pair, which is good leveling. Step 1's caution gives away step 8's answer, though. The manifest has prerequisites [] while the PRD assumes MSE/MAE and array shapes from aice-regression-metrics and aice-tensorflow.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 5db67446 | activation="linear" | code | minor | NOT-APPLY | caution spoils step 8 |
| 2 | 1.1.2 | 6b3988a8 | loss="mse" | code | minor | NOT-APPLY | caution off-target |
| 3 | 1.1.3 | d02c6e7e | history.history["loss"] | code | ok | APPLY | losses list |
| 4 | 1.1.4 | 58858333 | Dense(1) | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | 3e45b59c | evaluate | code | ok | NOT-APPLY | |
| 6 | 2.1.2 | c3856d24 | 배송 번호로 실제 시간 | code | ok | APPLY | dict order |
| 7 | 2.1.3 | f74a41e6 | 저장한 기준 saved | code | ok | HOLD-OPAQUE | scaled array |
| 8 | 2.1.4 | f3e0997f | 출력 막기 (relu) | code (representative) | minor | NOT-APPLY | narration stops before fix |
| 9 | 2.2.1 | 1e68bc14 | 마지막 도전 | code | defect | NOT-APPLY | "현재" sentence false |

**Defects.**
- [defect] step 9 (stp_1e68bc14) goal and unit premise: "현재 예측은 0분과 3분이고 MSE는 0이에요." The real starter output is "[[-3.0], [3.0]]\nbinary_crossentropy\n-15.942385". 0, 3 and MSE 0 are the targets. Fix: "완성하면 예측은 0분과 3분, MSE는 0이 나와야 해요."
- [minor] step 8 (stp_f3e0997f) narration: it runs once ("거리 1인 배송이 -3.0으로 나왔어요."), gives the caution, and ends with no patch_code, no second run and no submit. The PRD intends this ("음수 시간이 나오는 것을 보고 1번과 목표 범위가 반대임을 짚어요."), but lessons 19, 20 and 22 demonstrate their representative fix. See the course-level PLAN.
- [minor] step 8 (stp_f3e0997f) narration caution target: "code:kernel_initializer=keras.initializers.Constan". The caution is about the output activation but highlights the initializer token. Target `code:activation="linear"`.
- [minor] step 1 (stp_5db67446) narration: "조심하세요. … 시간처럼 음수가 없는 목표라면 그때는 ReLU가 맞아요." This hands over step 8's answer one step early, which flattens the 1-vs-8 contrast. End the caution at "출력 활성화는 목표가 허용하는 범위에 맞춰요."
- [minor] step 2 (stp_6b3988a8) narration: "조심하세요. accuracy는 종류를 맞힌 비율이라 숫자 예측의 손실이 아니에요." The step's real mistake is mae as the loss, not accuracy. Warn about swapping loss and metric instead, which is what the reject case "Swapping loss and metric" tests.

**Visualizer details.** Step 3 is APPLY: line `print(len(losses))`, event step_line, nth 1, target flow_memory, after the patch. The viewer shows `losses` as a list of ten Python floats falling epoch by epoch. The output shows only `10` and `True`, so this is the only place the learner sees one record per epoch and its decrease. Step 6 is APPLY: line `y_true = list(actual_by_order.values())`, event step_line, nth 1, target flow_memory, before the patch. The viewer shows `orders` ["A101", "A102"] next to `actual_by_order` {"A102": 5.0, "A101": 3.0}, which makes visible why `.values()` comes out misaligned. The output shows only the resulting lists. Both steps import TensorFlow, so the traced run pays TF start-up cost, which the root measures separately. Step 7 is HOLD-OPAQUE. `scaled` is an ndarray, either (new - 3.5)/2.0 or (new - 2)/1. A shape plus values view would put the two standardizations side by side. `saved` already shows as a dict.

**PLAN.** See the course-level representative-step item.

## 22. aice-neural-classification

**Goal and progression.** Objectives "이진 sigmoid·다중 softmax 출력의 의미와 모양을 읽어요." and "정수·원핫 정답과 손실 옵션을 맞춰요." are covered by threshold (1), from_logits (2), accuracy on new labels (3), softmax units (4), sparse loss (5), to_categorical (6), argmax to name (7), representative compile loss (8), and challenge (9). The order is sound and each step is a one-line edit. The challenge renames the classes to ["normal", "early", "late"], although the chapter premise says "같은 세 종류의 정답 표현" with ["normal", "late", "cancelled"]. The manifest has prerequisites [] while the PRD assumes "정답 범주·추정 확률·경보 임계값" from aice-classification-metrics.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 5895a5fa | 확률 >= threshold | code | minor | NOT-APPLY | narration rounds line 2 |
| 2 | 1.1.2 | a926ba50 | from_logits=False | code | defect | NOT-APPLY | wrong number |
| 3 | 1.1.3 | 89dc92b4 | y_new로 정확도 | code | ok | NOT-APPLY | |
| 4 | 1.1.4 | 996a2079 | softmax 범주 칸 | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | e4f42523 | SparseCategoricalCrossentropy | code | defect | HOLD-OPAQUE | wrong number |
| 6 | 2.1.2 | acd9b297 | to_categorical | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | 384c2fae | np.array(classes)[indices] | code | ok | HOLD-OPAQUE | indices (low value) |
| 8 | 2.1.4 | 361718b1 | 정답 형식 손실 | code (representative) | minor | NOT-APPLY | vague 할 일 |
| 9 | 2.2.1 | 6e8529c4 | 마지막 도전 | code | defect | NOT-APPLY | "현재" sentence false |

**Defects.**
- [defect] step 2 (stp_a926ba50) narration after the first run: "0.6436과 False예요." The real output is "0.6835\nFalse". Hand check: treating [0.5, 0.731] as logits gives sigmoid 0.6225 and 0.675, and the BCE against [0, 1] averages to 0.6835. Fix: "0.6835와 False예요."
- [defect] step 5 (stp_e4f42523) narration after the fix: "1.4076과 True예요." The real output is "0.9076\nTrue". 1.4076 is only row 1's -log(0.2447), and the mean with row 2's 0.4076 is 0.9076. Fix: "0.9076과 True예요."
- [defect] step 9 (stp_6e8529c4) goal and unit premise: "현재 두 배송의 예측 이름은 모두 late예요." The starter raises, and after the loss fix the real output is "['normal', 'normal']". 'late' is the target. Fix: "완성하면 두 배송의 예측 이름이 모두 late로 나와요."
- [minor] step 1 (stp_5895a5fa) narration: "두 줄 모두 [0.5, 0.731059]예요." The second line really prints [0.5, 0.7310585975646973]. Say that the second line shows the same probabilities unrounded.
- [minor] step 8 (stp_361718b1) goal 할 일: "2. 문제가 말한 한 곳을 고치세요." Same vague pattern as lesson 19 step 8.
- [minor] step 5 (stp_e4f42523) starter/solution: `classes = ["normal", "late", "cancelled"]` is never used. Drop it.
- [minor] step 9 (stp_6e8529c4) starter: `names = ["normal", "early", "late"]` breaks the chapter's "같은 세 종류" continuity. Reuse the chapter's classes or state the change.

**Visualizer details.** Step 5 is HOLD-OPAQUE. `probabilities` is a (2, 3) ndarray, and showing its rows would let the learner find the true-class probabilities 0.2447 and 0.665 that the loss averages, which is exactly where the narration's number went wrong. Step 7 is HOLD-OPAQUE. `indices` is the int64 ndarray [1, 2], which the output already prints, so it is low value. In step 9 the comprehension `[names[int(i)] for i in probabilities.argmax(axis=1)]` runs in main.py, but `i` is numpy.int64 and shows as opaque, and the printed list already shows the names, so it is NOT-APPLY.

**PLAN.** Only the course-level challenge-goal fix.

## 23. aice-training

**Goal and progression.** Objectives "epoch·batch·학습률의 역할을 구별해요." and "Dropout·L2·최고 모델 저장이 실제로 무엇을 바꾸는지 이해해요." map onto update count (1), train-vs-valid judgment (2, choice), restore_best_weights (3), Dropout training flag (4), L2 penalty (5), ModelCheckpoint load (6), learning-rate step (7), patience (8, representative), and patience+restore (9). Each technique gets its own step on the same 2-row model, and the challenge combines steps 3 and 8. Steps 1, 5 and 7 have the learner compute by hand what Keras did, which is strong for understanding. The manifest has prerequisites [] while the PRD assumes "작은 fit과 History·검증 손실" from aice-tensorflow.

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 6571abdd | epochs × batch 수 | code | ok | NOT-APPLY | |
| 2 | 1.1.2 | 51083364 | 훈련과 검증이 다르게 | choice+predict (example_code) | ok | NOT-APPLY | |
| 3 | 1.1.3 | cad01238 | restore_best_weights | code | ok | NOT-APPLY | |
| 4 | 1.1.4 | cf213a56 | training=False Dropout | code | ok | NOT-APPLY | |
| 5 | 2.1.1 | c41e053b | L2 규제 항 | code | ok | HOLD-OPAQUE | kernel weights |
| 6 | 2.1.2 | 3493a788 | load_model best.keras | code | ok | NOT-APPLY | |
| 7 | 2.1.3 | 3a6d96d0 | 학습률 × 기울기 | code | ok | APPLY | updated(rate) |
| 8 | 2.1.4 | 322608d1 | patience 정하기 | code (representative) | minor | NOT-APPLY | narration stops before fix |
| 9 | 2.2.1 | 99547a1f | 마지막 도전 | code | ok | NOT-APPLY | "현재 wait=2" is true |

**Defects.**
- [minor] step 8 (stp_322608d1) narration: it runs once ("두 epoch에서 멈췄어요."), gives the caution, and ends with no patch_code and no second run. The PRD intends this ("…기다릴 횟수를 세게 해요."). Same inconsistency as lesson 21 step 8.
- [minor] step 8 (stp_322608d1) narration caution target: "code:monitor=\"val_loss\"". The caution is about patience. Target `code:patience=0`.

**Visualizer details.** Step 7 is APPLY: line `    return 0.0 - rate * grad` after the patch, event return, nth 1, target flow_stack. The viewer shows the `updated` frame with `rate` 0.1 beside the global `grad` -10.0 and the return value 1.0. With nth 2 it shows rate 0.01 returning 0.1. The output never prints `grad`, though the narration says "기울기 -10", so the trace is the only place the learner sees the -10 and the per-call rate that produce both weights. Step 5 is HOLD-OPAQUE. `model.get_weights()[0]` is a (2, 1) ndarray of ones, and a values view would show what gets squared. Step 1's `make_model` call frames show only `rate=0.1`, which adds nothing.

**PLAN.** none.

## 24. aice-integration

**Goal and progression.** Objectives "실제 파일의 입력·정답·식별자를 구분하고 혼합 전처리를 구성해요." and "신경망 입력·결과 CSV·전처리 포함 저장복원을 검증해요." are covered by input selection (1), the ColumnTransformer cat branch (2), transform-only (3), Pipeline (4), Pipeline in CV (5), model__alpha (6), NN on the matrix (7), index=False (8), joblib on the whole pipeline (9), new-input columns (10, representative), and the challenge (11). It is a good capstone that reuses one earlier concept per step. Every starter reads the files through `pd.read_csv(...).to_dict(orient="list")` and then `pd.DataFrame(...)`, with the comment "그래서 다른 자료 목록을 넣어도 같은 코드가 돌아요". That is a grading hook a real AICE notebook would never contain. Step 11 silently switches files, to column `id` with zones a/b/c, after ten steps on `order_id` with north/south/west. The APIs fit the exam stack: `sparse_output` needs sklearn >= 1.2 (exam 1.3.2) and `lineterminator` needs pandas >= 1.5 (exam 1.5.3).

| # | position | step id | title (short) | kind | correctness | visualizer | note |
|---|---|---|---|---|---|---|---|
| 1 | 1.1.1 | 14110477 | df[["distance","zone"]] | code | minor | NOT-APPLY | 7 unused imports |
| 2 | 1.1.2 | e3c2ea13 | "cat" 갈래 | code | minor | HOLD-OPAQUE | matrix rows |
| 3 | 1.1.3 | b8f8c07c | transform(X_new) | code | minor | HOLD-OPAQUE | new_matrix rows |
| 4 | 1.1.4 | cc3e3728 | Pipeline prep | code | minor | NOT-APPLY | unused np |
| 5 | 1.1.5 | c637844f | cross_validate pipeline | code | minor | NOT-APPLY | unused np, X_new |
| 6 | 2.1.1 | 2c840b11 | model__alpha | code | minor | NOT-APPLY | unused np, LinearRegression |
| 7 | 2.1.2 | 2c9a7d60 | NN 숫자 행렬 | code | minor | NOT-APPLY | unused LinearRegression |
| 8 | 2.1.3 | 3257f998 | index=False | code | minor | NOT-APPLY | unused np |
| 9 | 2.1.4 | 623ed9ff | joblib pipeline | code | ok | NOT-APPLY | |
| 10 | 2.1.5 | 1cab4402 | 새 입력 열 | code (representative) | minor | NOT-APPLY | narration stops before fix, unused np |
| 11 | 2.2.1 | 86d1f031 | 마지막 도전 | code | minor | NOT-APPLY | silent file switch |

**Defects.**
- [minor] steps 1-8 and 10 (stp_14110477 … stp_1cab4402) starter/solution: the shared header imports names the step's solution never uses (content-rules section 4). Step 1 has `numpy, ColumnTransformer, Pipeline, SimpleImputer, StandardScaler, OneHotEncoder, LinearRegression`. Steps 2 and 3 have `numpy, LinearRegression`. Steps 4, 5, 8 and 10 have `numpy`. Step 6 has `numpy, LinearRegression`. Step 7 has `LinearRegression`. Trim each header to what the step uses. The KPC build's `drop_unused_imports` evidently does not run on redesigned lessons.
- [minor] steps 2, 3 and 5 starter: `y_train` (steps 2 and 3) and `X_new` (steps 2 and 5) are defined and never used. That is shared setup and adds reading load.
- [minor] step 10 (stp_1cab4402) narration: it runs once into the ValueError, gives the caution, and stops with no patch and no passing run. The PRD intends this ("오류 메시지에서 빠진 열을 찾고 훈련 입력과 비교하게 해요."), but it is inconsistent with lessons 19, 20 and 22.
- [minor] step 11 (stp_86d1f031) files: delivery.csv is now `id,distance,zone,minutes` with zones a/b, and new.csv has zone c. Steps 1-10 use `order_id` and north/south/west. Either state it in the goal ("이번 파일은 번호 열이 id예요") or keep the same files.

**Visualizer details.** Step 2 is HOLD-OPAQUE. `matrix` is a (6, 3) ndarray, and head rows would show the standardized distance column plus the 0/1 north/south columns, which the printed shape and names only describe. Step 3 is HOLD-OPAQUE. `new_matrix` is (3, 4) before the fix and (3, 3) after. Seeing the west row become [.., 0, 0] and the blank distance filled with the training mean is the clearest picture of "transform only", and only a shape-plus-head view gives it. In step 1, `train_rows` (a dict of column lists from `to_dict`) shows element by element, but that is the grading hook, not the lesson. DataFrames, Pipeline and the Keras model are all opaque, and the printed outputs carry each step's point.

**PLAN.** In the student-visible code, replace the `read_csv(...).to_dict(orient="list")` then `pd.DataFrame(...)` round trip with plain `pd.read_csv("delivery.csv")`. Move case injection to the grader (file substitution) so the capstone matches the exam notebook.

### Course-level notes for lessons 19-24

**PLAN.**
- Challenge-goal template. Step 9 in lessons 20, 21 and 22 states the target output as "현재 …". One template fix ("완성하면 …이 나와야 해요") resolves all three defects. Check the other AICE x.2.1 challenges for the same sentence.
- Representative-step policy. In lessons 19, 20 and 22 the representative step's narration demonstrates the fix and the passing run. In 21, 23 and 24 it stops after the first run, by PRD design. Pick one policy. If the narration must explain the problem through to the end (content-rules "해설은 문제를 설명한다" and "마지막 조각 뒤에 실행·결과·제출"), add the patch and final run to 21 step 8, 23 step 8 and 24 step 10.
- Visualizer. The three APPLY candidates (21.3, 21.6, 23.7) need the builder to accept Python `code_flow` narration, which is Java-only today at tools/build-redesigned-git.py:112. All three import TensorFlow, so use the root's measured traced-run cost. All nine HOLD-OPAQUE candidates need the same thing, an ndarray summary with shape, dtype and up to about 4x4 values. Small arrays dominate these lessons, so even a size-capped preview would unlock most of them. A DataFrame head view would add 24.2 and 24.3.
- Prerequisites. Every lesson has prerequisites [] while the PRDs name earlier lessons. Suggested: 19 after aice-split, aice-scale and aice-models. 20 after aice-regression. 21 after aice-tensorflow and aice-regression-metrics. 22 after aice-tensorflow and aice-classification-metrics. 23 after aice-tensorflow. 24 after aice-tuning and aice-scale.


## Summary

| Lessons | Steps | APPLY | HOLD-OPAQUE | Defects | Minors |
|---|---|---|---|---|---|
| 1-6 | 57 | 6 | 4 | 1 | 19 |
| 7-12 | 59 | 2 | 5 | 1 | 24 |
| 13-18 | 56 | 4 | 4 | 8 (2 + 6 promoted from minor, finding 1) | 19 |
| 19-24 | 56 | 3 | 9 | 5 | 23 |
| Total | 228 | 15 | 22 | 15 | 85 |

**APPLY candidates.** Every one needs the Python code_flow check in the builder opened first. Each entry gives the line, then the event and target where set, then what the viewer shows.
- **L1 s4.** `minutes = corrected` then `print(minutes)`. step_line, flow_memory. Shows minutes being rebound from 18 to 24.
- **L1 s8.** `print(minutes[len(minutes)])` after the try patch. exception, flow_objects. Shows list positions 0-4 and no position 5.
- **L2 s6.** `if minute > 30:` on the second pass. step_line. Shows the print being skipped.
- **L2 s7.** `delayed.append(minute)` on the second pass. step_line, flow_objects. Shows delayed growing.
- **L3 s3.** flow_objects. Shows a dict of 2 keys, each holding a 3-item list.
- **L3 s5.** `ordered = minutes`. flow_objects. Shows one shared list, then two separate lists after sorted.
- **L10 s1.** `print(answer)`. step_line, flow_memory. Shows X and y element by element.
- **L10 s5.** The `print(all(...zip(X_test, y_test)))` line. step_line nth 1, flow_memory. Shows X_test [1, 2] next to y_test [40, 60].
- **L13 s4.** Shows X_test as a list of lists.
- **L14 s4.** Shows sse and sst accumulating.
- **L16 s3.** Shows which pair counts as a hit. The nth value is unverified.
- **L16 s11.** Shows the predicted alarm list.
- **L21 s3.** `print(len(losses))`. step_line. Shows the list of 10 falling losses.
- **L21 s6.** `y_true = list(actual_by_order.values())`. step_line. Shows the dict's insertion order next to orders.
- **L23 s7.** `return 0.0 - rate * grad`. return. Shows grad = -10.0 on each call, a value never printed.

**HOLD-OPAQUE.** Each entry names the object and what a summary view would need to show.
- **L5 s2/s3.** DataFrame index labels next to positions, plus the head rows.
- **L5 s11 and L6 s11.** Shape and index of each reassigned table.
- **L7 s3/s5.** `joined`: shape, columns and head rows.
- **L8 s4.** The `widths` ndarray [20, 40].
- **L11 s6.** The index arrays from split().
- **L12 s9.** The scaler's mean_, which the second fit overwrites from [1.0] to [10.0].
- **The rest.** L13 s3, L14 s9, L15 s3, L18 s5, L19 s2, L20 s3/s7, L21 s7, L22 s5/s7, L23 s5 and L24 s2/s3. The details are in each lesson's section.

**Defects (15)**
- **L6 s10 (stp_22d818f2).** 할 일 says "2. 문제가 말한 한 곳을 고치세요.", but the solution needs two edits.
- **L10 s11 (stp_4664135d).** The `stratify=labels` edit changes nothing on screen. The output is '4 4\n2\nTrue' before and after, yet the narration says "아직 범주별 비율은 고정하지 않았어요".
- **L18 s2 (stp_7e3eb3df).** The claimed ValueError on targets 2 and 8 most likely does not occur on xgboost 0.90. Inferred from the source, not run.
- **L18 s9 (stp_a5d75177).** `get_booster().num_boosted_rounds()` does not exist in xgboost 0.90. Inferred from the source. Use `len(get_booster().get_dump())`, as steps 6-7 do.
- **Challenge goal states the target output as the current one (course-level finding 1).** This covers nine steps:
  - L20 s9 (stp_228a312c).
  - L21 s9 (stp_1e68bc14).
  - L22 s9 (stp_6e8529c4).
  - L13 s9, L14 s9, L15 s9, L16 s11, L17 s9 and L18 s9.
- **L22 s2 (stp_a926ba50).** The narration says "0.6436과 False예요", but the real output is '0.6835\nFalse'. Checked against lesson-cases.
- **L22 s5 (stp_e4f42523).** The narration says "1.4076과 True예요", but the real output is '0.9076\nTrue'. Checked against lesson-cases.

**Gaps.** No lesson went unreviewed. Two things were not checked by running them: behavior on the exam versions (pandas 1.5.3, sklearn 1.3.2, xgboost 0.90, TF 2.13.1), and the APPLY `nth` values on a real trace.
