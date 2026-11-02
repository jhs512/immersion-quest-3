'use strict';
// 코드 흐름 보기 for JavaScript (src/js_trace.rs). Runs the learner's UNMODIFIED main.js with the same
// Node.js that runs this file, the way the grader does (`node main.js` in the task workspace, input on a
// stdin pipe), adding only `--inspect-brk=127.0.0.1:0 --inspect-publish-uid=stderr`. This controller is a
// separate process: it attaches over the Chrome DevTools Protocol, stops at every breakable location of
// main.js and reads the paused program's frames and objects. Values come from Runtime.getProperties,
// which returns accessors and Proxy internals without running them. Object identity comes from a
// WeakMap the controller creates in the program's realm before main.js runs; the program cannot reach
// it. Writes the trace document (the Java core's trace format) to <out.json>.
//
// node mq_jstrace.cjs <workspace> <stdin file> <capture dir> <out.json> <step budget> <deadline ms>
const { spawn, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const [workspace, stdinPath, captureDir, outPath, budgetArg, deadlineArg] = process.argv.slice(2);
const BUDGET = Number(budgetArg) || 1000;
const DEADLINE_MS = Number(deadlineArg) || 20000;
const RAW_PAUSE_CAP = 10000;
const MAX_OBJECTS = 300;
const MAX_ITEMS = 100;
const MAX_ARRAY_OPEN = 1000;
const MAX_STRING = 2000;
const OUTPUT_LIMIT = 65536;
const DOCUMENT_LIMIT = 24 * 1024 * 1024;
const CJS_WRAPPER_NAMES = new Set(['exports', 'require', 'module', '__filename', '__dirname']);
const DEBUGGER_LINES = [
  /^Debugger listening on ws:\/\/\S+$/,
  /^For help, see: https:\/\/nodejs\.org\/\S+$/,
  /^Debugger attached\.$/,
  /^Waiting for the debugger to disconnect\.\.\.$/,
  /^Debugger ending on ws:\/\/\S+$/,
];

const mainFile = path.join(workspace, 'main.js');
const source = fs.readFileSync(mainFile, 'utf8');
const input = fs.readFileSync(stdinPath, 'utf8');
const doc = {
  code: source, stdin: input, problems: [], status: 'ok', language: 'javascript', runtime: process.version,
  stepBudget: BUDGET, options: { objects: false }, heapTruncated: false, trace: [], stdout: '', stderr: '',
  exitCode: null, notes: [],
};
const outFile = path.join(captureDir, 'stdout.txt');
const errFile = path.join(captureDir, 'stderr.txt');

function write(status, message) {
  if (status) doc.status = status;
  if (message) doc.message = message;
  fs.writeFileSync(outPath, JSON.stringify(doc));
}

if (typeof WebSocket !== 'function') {
  write('runtime_unavailable', `JavaScript 코드 흐름 보기에는 Node.js 22 이상이 필요해요. 지금 Node.js는 ${process.version}이에요.`);
  process.exit(0);
}

const started = Date.now();
const child = spawn(process.execPath, ['--inspect-brk=127.0.0.1:0', '--inspect-publish-uid=stderr', 'main.js'], {
  cwd: workspace,
  stdio: ['pipe', fs.openSync(outFile, 'w'), fs.openSync(errFile, 'w')],
  windowsHide: true,
  // Unix: its own process group, so ending it ends exactly what it started and nothing else.
  detached: process.platform !== 'win32',
});
let exited = null;
const exitedPromise = new Promise((resolve) => child.on('exit', (code, signal) => { exited = { code, signal }; resolve(); }));
child.on('error', () => {});
fs.writeFileSync(path.join(captureDir, 'debuggee.pid'), String(child.pid));
child.stdin.on('error', () => {});
child.stdin.end(input);

function killTree() {
  if (process.platform === 'win32') {
    if (exited) return;
    const taskkill = path.join(process.env.SystemRoot || 'C:\\Windows', 'System32', 'taskkill.exe');
    spawnSync(taskkill, ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
  } else {
    try { process.kill(-child.pid, 'SIGKILL'); } catch {}
  }
}

const readText = (file) => { try { return fs.readFileSync(file, 'utf8'); } catch { return ''; } };
const programStdout = () => readText(outFile);
const programStderr = () => readText(errFile).replace(/\r\n/g, '\n').split('\n')
  .filter((line) => !DEBUGGER_LINES.some((re) => re.test(line))).join('\n');

let ws = null;
let nextMessage = 0;
const pending = new Map();
const listeners = {};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== 1) { reject(new Error('inspector closed')); return; }
    const id = ++nextMessage;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
function connect(url) {
  ws = new WebSocket(url);
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.id) {
      const waiter = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) waiter?.reject(new Error(message.error.message)); else waiter?.resolve(message.result);
    } else listeners[message.method]?.(message.params);
  };
  ws.onclose = () => { for (const { reject } of pending.values()) reject(new Error('inspector closed')); pending.clear(); finish(); };
  ws.onerror = () => {};
  ws.onopen = () => start().catch((error) => fail(error));
}

let finished = false;
let stopReason = null; // status that ends the run early: step_limit, output_limit, timeout, unsupported, tool_error
function stop(status) {
  if (stopReason || finished) return;
  stopReason = status;
  killTree();
}
const watchdog = setTimeout(() => stop('timeout'), DEADLINE_MS);
const poller = setInterval(() => {
  const err = readText(errFile);
  if (!ws) {
    const url = err.match(/^Debugger listening on (ws:\/\/127\.0\.0\.1:\d+\/[\w-]+)/m);
    if (url) connect(url[1]);
  }
  // Node keeps a finished program alive while a debugger is attached; detaching lets it exit.
  if (err.includes('Waiting for the debugger to disconnect...')) ws?.close();
  try { if (fs.statSync(outFile).size > OUTPUT_LIMIT) stop('output_limit'); } catch {}
}, 15);
exitedPromise.then(() => { if (!ws) finish(); else ws.close(); });

function fail(error) {
  doc.message = `코드 흐름 도구가 멈췄어요: ${error.message}`;
  stop('tool_error');
}

async function finish() {
  if (finished) return;
  finished = true;
  clearInterval(poller);
  clearTimeout(watchdog);
  await Promise.race([exitedPromise, new Promise((r) => setTimeout(r, 3000))]);
  killTree();
  await Promise.race([exitedPromise, new Promise((r) => setTimeout(r, 2000))]);
  doc.stdout = programStdout();
  doc.stderr = programStderr();
  doc.exitCode = exited ? exited.code : null;
  doc.timing = { runMs: Date.now() - started, pauses: rawPauses, snapshotMs: Math.round(snapshotMs) };
  if (stopReason === 'unsupported') {
    doc.trace = [];
    doc.status = 'unsupported';
  } else if (stopReason) {
    doc.status = stopReason === 'output_limit' ? 'step_limit' : stopReason;
    if (stopReason === 'output_limit') doc.notes.push(`출력이 ${OUTPUT_LIMIT}바이트를 넘어 실행을 멈췄어요.`);
    if (['step_limit', 'output_limit'].includes(stopReason) && doc.trace.length) {
      const last = { ...doc.trace.at(-1), event: 'instruction_limit_reached', stdout: doc.stdout };
      delete last.exception_msg;
      doc.trace.push(last);
    }
  } else if (!sawUserCode && doc.exitCode === 0) {
    // A run that ended without one stop in main.js was not observed; an empty `ok` would claim it was.
    doc.status = 'tool_error';
    doc.message = `코드 흐름 도구가 main.js에서 멈추지 못했어요. 찾은 이름: ${otherMainUrls.join(', ') || '없음'}`;
  } else if (!sawUserCode && doc.exitCode !== 0) {
    const problem = compileProblem(doc.stderr);
    if (problem) { doc.status = 'compile_error'; doc.problems.push(problem); }
    else doc.status = 'runtime_error';
  } else if (doc.exitCode !== 0) {
    if (lastException && doc.trace.length) {
      doc.trace.push({ ...doc.trace.at(-1), event: 'uncaught_exception', exception_msg: lastException, stdout: doc.stdout });
      doc.status = 'uncaught_exception';
    } else doc.status = 'runtime_error';
  }
  if (workers) doc.notes.push(`worker 스레드 ${workers}개의 코드는 단계로 기록하지 않았어요. 기록한 것은 main 스레드예요.`);
  write();
  process.exit(0);
}

// `node main.js` reports a syntax error as "<path>:<line>", the source line, a caret, then "<Name>: <message>".
function compileProblem(stderr) {
  const at = stderr.match(/main\.js:(\d+)\s*$/m);
  const error = stderr.match(/^(SyntaxError|ReferenceError): (.+)$/m);
  if (!at || !error || error[1] !== 'SyntaxError') return null;
  return { line: Number(at[1]), error: true, message: `${error[1]}: ${error[2]}` };
}

let mainScriptId = null;
let registry = null; // objectId of the identity function in the program's realm
let armed = false;
let sawUserCode = false;
let rawPauses = 0;
let lastException = null;
let documentBytes = 0;
let workers = 0;
let snapshotMs = 0;
let previousFrames = []; // [{key, id}] of the last recorded step, bottom first
let nextFrameId = 1;
let queue = Promise.resolve();

async function start() {
  listeners['Debugger.scriptParsed'] = (p) => {
    if (mainUrls.has(p.url)) mainScriptId = p.scriptId;
    else if (/[\\/]main\.js$/.test(p.url)) otherMainUrls.push(p.url);
  };
  listeners['Debugger.paused'] = (p) => { queue = queue.then(() => paused(p)).catch((error) => fail(error)); };
  // A worker inherits --inspect-brk and would wait for a debugger forever: release it, then let go.
  listeners['NodeWorker.attachedToWorker'] = async (p) => {
    workers++;
    const message = JSON.stringify({ id: 1, method: 'Runtime.runIfWaitingForDebugger' });
    await send('NodeWorker.sendMessageToWorker', { sessionId: p.sessionId, message }).catch(() => {});
    await send('NodeWorker.detach', { sessionId: p.sessionId }).catch(() => {});
  };
  await send('Runtime.enable');
  await send('Debugger.enable', { maxScriptsCacheSize: 10_000_000 });
  await send('Debugger.setPauseOnExceptions', { state: 'all' });
  await send('NodeWorker.enable', { waitForDebuggerOnStart: false }).catch(() => {});
  // Before main.js is compiled, so V8 places these while parsing it, before its first statement runs.
  const lines = source.split('\n').length;
  await Promise.all([...mainUrls].flatMap((url) => Array.from({ length: lines }, (_, lineNumber) =>
    send('Debugger.setBreakpointByUrl', { url, lineNumber, columnNumber: 0 }).catch(() => {}))));
  await send('Runtime.runIfWaitingForDebugger');
}
// Node names the entry by its real path (a macOS temp dir sits behind /var -> /private/var, a Windows
// temp dir can be a junction) and leaves `~` unescaped where pathToFileURL writes %7E (an 8.3 name such
// as C:\Users\RUNNER~1), so each spelling of this file's path is a name it may report.
const mainUrls = new Set([mainFile, fs.realpathSync(mainFile), fs.realpathSync.native(mainFile)]
  .flatMap((file) => { const href = pathToFileURL(file).href; return [file, href, href.replace(/%7E/gi, '~')]; }));
const otherMainUrls = [];

const resume = () => send('Debugger.resume').catch(() => {});
const isUser = (frame) => frame.location.scriptId === mainScriptId;

async function paused(p) {
  if (stopReason || finished) return;
  const exception = p.reason === 'exception' || p.reason === 'promiseRejection';
  const userFrames = p.callFrames.filter(isUser);
  const top = p.callFrames[0];
  await guardErrors([p.data, ...p.callFrames.flatMap((f) => [f.this, f.returnValue])]);
  if (stopReason) return;
  // Node's own code (module loading, timers) and exceptions it throws and catches itself.
  if (!userFrames.length || (!isUser(top) && !(exception && p.data?.uncaught))) return resume();
  if (!armed) await arm(top);
  sawUserCode = true;
  if (++rawPauses > RAW_PAUSE_CAP) {
    doc.notes.push(`같은 줄 안에서 ${RAW_PAUSE_CAP}번 넘게 멈춰 기록을 멈췄어요. 기록한 단계는 ${doc.trace.length}개예요.`);
    return stop('step_limit');
  }

  const frames = identify(userFrames);
  const current = frames.at(-1);
  const returning = isUser(top) && top.returnValue && !current.module;
  const event = exception ? 'exception' : returning ? 'return' : current.fresh ? 'call' : 'step_line';
  const previous = doc.trace.at(-1);
  if (event === 'step_line' && previous && previous.event === 'step_line'
      && previous.line === current.line && previous.stack_to_render.at(-1)?.frame_id === current.id) return resume();

  if (doc.trace.length >= BUDGET) return stop('step_limit');
  const t = performance.now();
  const step = await snapshot(event, frames, userFrames, returning ? top.returnValue : undefined);
  snapshotMs += performance.now() - t;
  if (!step || stopReason) return;
  if (exception) {
    step.exception_msg = exceptionText(p.data);
    if (p.data?.uncaught) lastException = step.exception_msg;
  }
  documentBytes += JSON.stringify(step).length;
  doc.trace.push(step);
  previousFrames = frames;
  if (documentBytes > DOCUMENT_LIMIT) { doc.notes.push('기록이 너무 커서 여기서 멈췄어요.'); return stop('step_limit'); }
  return resume();
}

// At the first stop in main.js nothing of it has run yet: place a breakpoint on every breakable location,
// and create the identity WeakMap with the builtins as they are now (main.js may replace them later).
async function arm(top) {
  armed = true;
  const { locations } = await send('Debugger.getPossibleBreakpoints', { start: { scriptId: mainScriptId, lineNumber: 0, columnNumber: 0 } });
  // A call position in the middle of a line would only ever be merged into that line's step; skipping it
  // keeps a tight one-line loop from costing a round trip per call.
  const kept = locations.filter((l, i) => l.type !== 'call' || locations[i - 1]?.lineNumber !== l.lineNumber);
  await Promise.all(kept.map((location) => send('Debugger.setBreakpoint', { location }).catch(() => {})));
  const made = await send('Debugger.evaluateOnCallFrame', {
    callFrameId: top.callFrameId, objectGroup: 'mq-registry', silent: true,
    expression: `(() => { const ids = new WeakMap(), get = WeakMap.prototype.get, set = WeakMap.prototype.set,
      apply = Reflect.apply, global = globalThis; let next = 1;
      return function (value) { if (value === global) return 0; let id = apply(get, ids, [value]);
        if (id === undefined) { id = next++; apply(set, ids, [value, id]); } return id; }; })()`,
  });
  registry = made.result.objectId;
}

const SYNTHETIC_NAMES = { '<instance_members_initializer>': '필드 초기화', '<static_initializer>': 'static 초기화' };
const frameName = (f) => SYNTHETIC_NAMES[f.functionName] || f.functionName || '(익명 함수)';
// main.js's top level: the CommonJS wrapper function, or an ES module's module scope.
const isModuleFrame = (f) => f.scopeChain.some((s) => s.type === 'module')
  || (!f.functionName && f.functionLocation?.lineNumber === 0 && f.functionLocation?.columnNumber === 0);

// CDP call frame ids are valid for one pause only. A frame keeps its id while it and every frame under it
// are the same function as at the last recorded step; anything else is a new activation.
function identify(userFrames) {
  const bottomFirst = [...userFrames].reverse();
  let same = true;
  return bottomFirst.map((f, i) => {
    const key = `${f.functionName}@${f.functionLocation?.scriptId}:${f.functionLocation?.lineNumber}:${f.functionLocation?.columnNumber}`;
    same = same && previousFrames[i]?.key === key;
    const id = same ? previousFrames[i].id : nextFrameId++;
    return { key, id, fresh: !same, frame: f, line: f.location.lineNumber + 1, module: isModuleFrame(f) };
  });
}

function exceptionText(data) {
  if (!data) return '예외';
  if (data.type === 'object' && data.subtype === 'error') return (data.description || data.className || 'Error').split('\n')[0];
  if (data.type === 'string') return `throw "${data.value}"`;
  return `throw ${data.unserializableValue ?? data.description ?? JSON.stringify(data.value)}`;
}

async function snapshot(event, frames, userFrames, returnValue) {
  const heap = {};
  const encode = (value) => encodeValue(value, heap);
  const stack = [];
  for (const entry of frames) {
    const f = entry.frame;
    const names = [], values = {};
    const put = (name, value) => { if (!(name in values)) { names.push(name); values[name] = value; } };
    for (const scope of f.scopeChain) {
      const local = ['local', 'block', 'catch', 'module'].includes(scope.type);
      if (!local && scope.type !== 'closure') continue;
      if (scope.type === 'closure' && entry.module) continue;
      const { result } = await props(scope.object.objectId);
      if (stopReason) return null;
      for (const d of result) {
        if (entry.module && CJS_WRAPPER_NAMES.has(d.name)) continue;
        // A function the closure captured is a declaration, not state; its own frame shows it if it runs.
        if (scope.type === 'closure' && d.value?.type === 'function') continue;
        const label = local ? d.name : `${d.name} (클로저)`;
        // A let/const/class binding before its declaration runs has no value: the temporal dead zone.
        put(label, 'value' in d ? await encode(d.value) : ['C_NOTE', '초기화 전 (TDZ)']);
      }
    }
    if (!entry.module && f.this?.type === 'object' && f.this.subtype !== 'null') {
      const self = await encode(f.this);
      if (!(Array.isArray(self) && self[0] === 'C_NOTE' && self[1] === 'globalThis')) put('this', self);
    }
    if (entry === frames.at(-1) && returnValue) put('__return__', await encode(returnValue));
    stack.push({
      func_name: entry.module ? '전역 코드' : frameName(f), frame_id: entry.id, line: entry.line,
      is_highlighted: entry === frames.at(-1), encoded_locals: values, ordered_varnames: names,
    });
  }
  const current = frames.at(-1);
  return {
    event, line: current.line, func_name: stack.at(-1).func_name, stdout: programStdout(),
    globals: {}, ordered_globals: [], stack_to_render: stack, heap,
  };
}

// Every value CDP hands back comes with a description V8 has already made. For an Error, V8 makes it by
// reading `stack`, `message` and `name` with ordinary [[Get]], so a getter the program defined for one of
// them has just run inside the program. Nothing in CDP prevents that; what can be done is to notice it
// and refuse the trace, because the program it shows is no longer the program that would have run.
const NATIVE_FUNCTION = /\{\s*\[native code\]\s*\}$/;
async function guardErrors(values) {
  for (const v of values) {
    if (v?.type !== 'object' || v.subtype !== 'error' || stopReason) continue;
    const { result } = await send('Runtime.getProperties', { objectId: v.objectId, ownProperties: false, accessorPropertiesOnly: true, generatePreview: false });
    for (const d of result) {
      if (!['stack', 'message', 'name'].includes(d.name) || d.get?.type !== 'function') continue;
      const bound = NATIVE_FUNCTION.test(d.get.description)
        && (await send('Runtime.getProperties', { objectId: d.get.objectId, ownProperties: true })).internalProperties?.some((p) => p.name === '[[TargetFunction]]');
      if (!NATIVE_FUNCTION.test(d.get.description) || bound) {
        doc.message = `오류 객체의 ${d.name}을(를) 읽는 getter가 코드에 있어요. 흐름을 그리면 그 getter가 실행돼요.`;
        stop('unsupported');
        return;
      }
    }
  }
}
async function props(objectId) {
  const found = await send('Runtime.getProperties', { objectId, ownProperties: true, generatePreview: false });
  await guardErrors([...found.result.map((d) => d.value), ...(found.internalProperties || []).map((d) => d.value), ...(found.privateProperties || []).map((d) => d.value)]);
  return found;
}
const sizeOf = (description) => Number((description || '').match(/\((\d+)\)$/)?.[1] ?? 0);
const isIndex = (name) => /^(0|[1-9]\d*)$/.test(name);
const firstLine = (text, limit = 60) => { const line = String(text).split(/\r?\n/)[0]; return line.length > limit ? `${line.slice(0, limit)}…` : line; };

async function identity(objectId) {
  const { result } = await send('Runtime.callFunctionOn', { objectId: registry, functionDeclaration: 'function (value) { return this(value); }', arguments: [{ objectId }], returnByValue: true, silent: true });
  return result.value;
}

async function encodeValue(v, heap) {
  switch (v.type) {
    case 'undefined': return ['C_NOTE', 'undefined'];
    case 'boolean': return v.value;
    case 'string': return v.value.length > MAX_STRING ? `${v.value.slice(0, MAX_STRING)}…` : v.value;
    case 'number': return v.unserializableValue ? ['SPECIAL_FLOAT', v.unserializableValue] : v.value;
    case 'bigint': return ['SPECIAL_FLOAT', v.unserializableValue];
    case 'symbol': return ['C_NOTE', v.description];
    case 'function': return ['C_NOTE', firstLine(v.description, 40).replace(/\s*\{.*$/, '') || 'function'];
  }
  if (v.subtype === 'null') return null;
  // Shown as text: no box of fields would be true for these.
  switch (v.subtype) {
    case 'proxy': return ['C_NOTE', `${v.description} · 트랩을 실행하지 않으려고 열지 않음`];
    case 'regexp': case 'date': return ['C_NOTE', firstLine(v.description)];
    case 'error': return ['C_NOTE', firstLine(v.description)];
    case 'weakmap': case 'weakset': case 'weakref': case 'arraybuffer': case 'dataview': case 'generator':
    case 'iterator': case 'wasmvalue': case 'webassemblymemory': case 'typedarray':
      if (v.subtype !== 'typedarray') return ['C_NOTE', `${v.description} · 내용은 표시하지 않음`];
  }
  if ((v.subtype === 'array' || v.subtype === 'typedarray') && sizeOf(v.description) > MAX_ARRAY_OPEN) {
    return ['C_NOTE', `${v.description} · 칸이 많아 펼치지 않음`];
  }
  const id = await identity(v.objectId);
  if (id === 0) return ['C_NOTE', 'globalThis'];
  if (String(id) in heap) return ['REF', id];
  if (Object.keys(heap).length >= MAX_OBJECTS) { doc.heapTruncated = true; return ['C_NOTE', '표시 한도를 넘은 객체']; }
  heap[id] = null; // reserved before its contents, so a cycle refers back to it
  heap[id] = await objectEntry(v, heap);
  return ['REF', id];
}

const descriptorValue = (d, heap) => 'value' in d ? encodeValue(d.value, heap)
  : ['C_NOTE', d.get ? 'getter · 실행하지 않음' : d.set ? 'setter만 있음' : '값 없음'];

async function objectEntry(v, heap) {
  const { result, internalProperties = [], privateProperties = [] } = await props(v.objectId);
  const internal = Object.fromEntries(internalProperties.map((p) => [p.name, p.value]));
  if (v.subtype === 'array' || v.subtype === 'typedarray') {
    const length = sizeOf(v.description);
    const byIndex = new Map(result.filter((d) => isIndex(d.name)).map((d) => [Number(d.name), d]));
    const items = [];
    for (let i = 0; i < Math.min(length, MAX_ITEMS); i++) {
      items.push(byIndex.has(i) ? await descriptorValue(byIndex.get(i), heap) : ['C_NOTE', '빈 칸']);
    }
    if (length > MAX_ITEMS) items.push(['C_NOTE', `… ${length - MAX_ITEMS}칸 더`]);
    return ['ARRAY', v.description, ...items];
  }
  if (v.subtype === 'map' || v.subtype === 'set') {
    const entries = internal['[[Entries]]'] ? (await props(internal['[[Entries]]'].objectId)).result.filter((d) => isIndex(d.name)) : [];
    const rows = [];
    for (const e of entries.slice(0, MAX_ITEMS)) {
      const fields = Object.fromEntries((await props(e.value.objectId)).result.map((d) => [d.name, d.value]));
      rows.push(v.subtype === 'map' ? [await encodeValue(fields.key, heap), await encodeValue(fields.value, heap)] : await encodeValue(fields.value, heap));
    }
    return v.subtype === 'map' ? ['MAP', v.description, rows] : ['COLLECTION', v.description, rows];
  }
  const fields = [];
  if (v.subtype === 'promise') {
    fields.push(['[[PromiseState]]', internal['[[PromiseState]]']?.value ?? '?']);
    if (internal['[[PromiseResult]]']) fields.push(['[[PromiseResult]]', await encodeValue(internal['[[PromiseResult]]'], heap)]);
  }
  for (const d of [...result, ...privateProperties]) {
    if (fields.length >= MAX_ITEMS) { fields.push(['…', ['C_NOTE', '속성이 더 있음']]); break; }
    if (d.isOwn === false || d.name === '__proto__') continue;
    fields.push([d.name, await descriptorValue(d, heap)]);
  }
  return ['INSTANCE', v.className || 'Object', ...fields];
}
