# JavaScript 코드 흐름 보기: work log and integration contract

Branch `feat/js-code-flow`, base `4ced962a`. Scope is the JavaScript tracer only:

- `src/js_trace.rs`
- `assets/js-trace/mq_jstrace.cjs`
- `pub mod js_trace` in `src/lib.rs`
- the CI experiment `.github/workflows/js-trace-experiment.yml`

The root integrates `src/player_ui.rs`, `src/repository_course.rs` and the shared viewer assets. None of
those were touched here.

## Contract for the root

```rust
pub async fn molip_quest::js_trace::trace(source: &str, input: &str, files: &BTreeMap<String, String>)
    -> Result<String, String>
pub const molip_quest::js_trace::STEP_BUDGET: u32 = 1000;
```

This is the same shape as `python_trace::trace`. `source` becomes `main.js`. `files` are written next to it
with the grader's `safe_file` rule. `input` is fed on a stdin pipe and then closed, as the grader does.
The learner's code runs once per call.

`Ok(document)` is the Java core trace format, with `language: "javascript"`. Its `status` is one of:

| status | meaning | steps |
| --- | --- | --- |
| `ok` | exit code 0 | yes |
| `uncaught_exception` | Node ended on an exception; the last step is `uncaught_exception` with `exception_msg` | yes |
| `runtime_error` | nonzero exit without an uncaught exception (`process.exit(2)`, `process.exitCode`) | yes |
| `step_limit` | a limit stopped it; the last step is `instruction_limit_reached`, and `notes` says which limit | yes |
| `compile_error` | `problems: [{line, error: true, message}]` from Node's SyntaxError | none |
| `unsupported` | drawing would have run learner code; `message` gives the reason | none |

`Err(message)` is returned when nothing can be drawn:

- No Node.js was found (`node_tools::executable()` is not a file).
- Node.js has no `WebSocket` (older than 22). The controller writes `runtime_unavailable` with the version.
- The controller's 20 s deadline passed. The message is "코드 흐름을 20초 안에 기록하지 못했어요…".
- The Rust 30 s outer limit passed.
- The controller itself failed (`tool_error`). This includes a run that never stopped in main.js; an
  empty `ok` is never returned.

Extra document fields:

- `exitCode`
- `notes[]`: learner-facing sentences, for example worker threads or forked processes that were not
  traced, or which limit fired.
- `message`
- `timing {runMs, pauses, snapshotMs}`
- `runtime` (the Node version)

Value tags are only the ones `render.js` already draws. There are no `OPAQUE` boxes.

| JavaScript | tag |
| --- | --- |
| number | number |
| NaN, ±Infinity, -0, bigint `10n` | `SPECIAL_FLOAT` |
| undefined | `C_NOTE "undefined"` |
| TDZ binding | `C_NOTE "초기화 전 (TDZ)"` |
| function, class | `C_NOTE` with the first source line |
| getter | `C_NOTE "getter · 실행하지 않음"` |
| Proxy | `C_NOTE` (not opened, traps are not run) |
| Error, Date, RegExp | `C_NOTE` with V8's description |
| Array, TypedArray | `ARRAY` (holes are `C_NOTE "빈 칸"`; over 1000 items, a note) |
| Map | `MAP "Map"` |
| Set | `COLLECTION "Set"` |
| Promise | `INSTANCE` with `[[PromiseState]]` and `[[PromiseResult]]` |
| object, class instance | `INSTANCE className` with own fields and `#private` fields |
| WeakMap, WeakSet, ArrayBuffer, generator, … | `C_NOTE "… · 내용은 표시하지 않음"` |

Other naming:

- The top-level frame is `전역 코드`. Anonymous functions are `(익명 함수)`.
- Class field initializers are `필드 초기화`.
- Closure variables are listed in the frame as `name (클로저)`. Function-valued captures are left out.
- REF ids are small integers, stable for the whole run.

## Root integration, in order

1. `src/player_ui.rs`, the `code_flow_ready` condition (around line 933): add `TaskLanguage::Javascript`.
   It is supported on every platform; Windows and macOS are checked in CI.
2. `src/player_ui.rs`, the trace dispatch (around line 1236): for Javascript, call
   `molip_quest::js_trace::trace(&source, &input, &files).await`. Update the comment that lists tracers.
3. `assets/java-trace/code-flow.js`:
   - The `runtime` label (around line 95) needs a `javascript` branch, for example
     `수업과 같은 Node.js ${doc.runtime}(코드를 고치지 않은 원본)`. Today it would say JDK 25.
   - Show `doc.notes` with the trace. Worker and fork notes are part of being honest about scope.
   - Optionally add a `STATUS.runtime_error` text.
4. `assets/java-trace/core/render.js`, line 159: treat `javascript` like `python`/`c`, so events read
   `함수 호출` instead of `메서드 호출`. Escaping is already correct, because every name, key and title
   goes through `esc()`.
5. Content: set `code_flow: true` on the JavaScript tasks that should offer the button. The only five
   today are in `node-cpu-offload`, which is not in the registered catalog. The test reads that file
   directly.
6. The CI experiment workflow can be dropped, or folded into the pilot validation, when this lands.

## Observed before the design was fixed (Windows 11, Node v24.13.1)

- `--inspect-brk` first stops inside Node's loader, before any learner module, ES imports included.
  The identity WeakMap, the realm's own Error accessors and `Error.prepareStackTrace` are captured at
  that stop.
- CJS main.js never triggers `beforeScriptExecution`. Instead, `setBreakpointByUrl` per line is sent
  before `runIfWaitingForDebugger`. The first main.js stop then sets every `getPossibleBreakpoints`
  location, except mid-line `call` positions.
- Node names the entry by its real path, with a literal `~`. A macOS `/var` → `/private/var` symlink, a
  Windows junction, or an 8.3 name (`C:\Users\RUNNER~1` on GitHub runners) broke URL matching in CI
  until every spelling was registered. `pathToFileURL` writes `%7E`.
- `CallFrame.url` is empty on this V8, so frames are matched by `scriptId`.
- A `return` break location carries `returnValue`. A TDZ binding comes back without `value`.
- `HeapProfiler.getHeapObjectId` returns `0` for new objects. With tracking turned on, the program
  never exits. That is why identity uses the WeakMap.
- `getProperties` never calls getters or Proxy traps. V8 does describe every Error by reading `stack`,
  `message`, `name` and `Symbol.toStringTag`, and formatting `stack` calls `Error.prepareStackTrace`. CDP
  cannot stop this. Every Error value, including nested ones such as `cause`, is checked along its
  prototype chain against the captured intrinsics. A Proxy prototype or any learner hook refuses the trace
  (`unsupported`, program killed).
- `new Worker` and `fork()` inherit `--inspect-brk`. Workers are released through `NodeWorker`; forked
  processes are released through their own inspector URL. Neither is traced.
- Killing only the controller on Windows ends the debuggee and its grandchild, through libuv's
  kill-on-close job. Checked with `tasklist`.

## Scope: what is not traced, or is shown as unknown

- **worker_threads**: only the main thread is traced. Code inside a worker, including `new Worker(__filename)`
  re-running main.js in a worker, runs untraced. Its output still reaches stdout. A note gives the count.
- **child processes** (`fork`, `cluster`, `spawn(process.execPath)`): they run untraced and are noted.
  A child whose stderr is redirected away hides its inspector URL and would wait until the deadline.
- Modules other than main.js, code from `eval`/`new Function`, and Node internals are hidden.
- Globals assigned without a declaration are not shown. Closure variables V8 optimized away are not shown.
- An `async` function resuming after `await` appears as a new activation with a `call` step.
- The program is paused while it is drawn. Timing-dependent code (`Atomics.wait` with a timeout,
  `Date.now()` races) can take a different branch than in the grader. The trace shows the run it observed.
- stdout goes to a file, not a pipe. `process.exit()` right after a large write cannot lose output here.
- On Unix, if MQ itself dies without dropping the request, the debuggee's process group is not ended.
  On Windows the job object covers this case.
- A program that prints Node's `Waiting for the debugger to disconnect...` line itself only ends its own
  trace early.

## Limits (the controller's, all before the Rust 30 s)

| limit | value |
| --- | --- |
| deadline | 20 s, then Err |
| recorded steps | 1000 |
| raw pauses | 10000 |
| stdout | 64 KB |
| objects per step | 300 |
| items per object | 100 |
| array opened up to | 1000 items |
| document | 24 MB |

Cleanup is scoped to what the controller started:

- Windows: `taskkill /PID <its child> /T /F` while that child is alive.
- Unix: its own process group.
- Rust's drop guard runs `killpg` on Unix only.

## Verification

Reproduce with:

```
cargo test --locked --no-default-features --lib js_trace -- --ignored --test-threads=1
```

The fixtures live in `probe/fx`. Run one with `probe/run.sh <file> [stdin]`, then summarize the output
with `node probe/show.cjs <json>`.

Local, Windows 11, Node 24.13.1: 5/5 passed.

The five tests are:

- **All JavaScript tasks.** Starter and solution, every test input, compared with a separate
  `lesson_runner::run`. Tasks 1 to 4 give identical stdout and status. Task 5 hashes 300000 rounds and
  stops at a limit, and its stdout is a prefix of the grader's.
- **Identity and values.** Aliasing, a cycle, the call stack and return value, a closure seen from a
  later callback, TDZ, NaN/-0/Infinity/10n/undefined/null, stdin, and an uncaught async error compared
  with the grader.
- **No learner code runs while drawing.** Plain getters, Proxy traps, a replaced `WeakMap.prototype.get`
  (also from an ES import) and `toStringTag` are untouched. Six Error routes are refused:
  - a `message` getter
  - a `stack` getter
  - `prepareStackTrace` on a caught TypeError
  - a `toStringTag` getter on an Error
  - a Proxy prototype
  - `cause`
- **Activations and endings.** Separate activations for `f(1); f(2)` and `.map`, a forked child
  completing (and noted), a rejection handled later reported as `runtime_error`, and a Set drawn as a Set.
- **Runaway programs.** The syntax error line, an output flood, an infinite loop whose spawned grandchild
  is gone afterwards, and a prompt normal exit.

CI (`js-trace-experiment.yml`, windows-latest and macos-15, Node 22 and 24, plus Node 20 refusing):

- `41381606758` on `c435b30c`: failed. Path spelling.
- `41386734513` on `06937393`: macOS green; Windows failed. `RUNNER~1`.
- `41387347403` on `c48d087f`: all green, 4/4 tests per job, Node 20 refusal ok.
- `41388592126` on `0c88b113` (review fixes): all green.

| job | Node | result |
| --- | --- | --- |
| windows-latest | v22.23.4 | 5/5 |
| windows-latest | v24.22.1 | 5/5 |
| macos-15 | v22.23.4 | 5/5 |
| macos-15 | v24.22.1 | 5/5 |
| ubuntu | v20.20.2 | `runtime_unavailable`, version named in the message |

## Independent review

A thermo-nuclear review subagent (opus) reviewed `4ced962a..c48d087f`.

- **Medium.** Error-description side effects, fork hang, and frame ids. All three were reproduced, then
  fixed and tested.
- **Low.**
  - stale `uncaught`: fixed
  - Windows PID-reuse in the drop guard: fixed by removing the Windows path
  - `kill --` on macOS: replaced by `killpg`
  - Map size title: fixed
  - unclear Node-version message: fixed
- **Documented as limits.** Unix orphan if MQ dies, and file versus pipe stdout.
