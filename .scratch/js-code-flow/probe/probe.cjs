// Throwaway probe: answers empirical inspector questions before the controller is written.
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const dir = path.resolve(process.argv[2]);
const err = fs.openSync(path.join(dir, 'err.txt'), 'w');
const out = fs.openSync(path.join(dir, 'out.txt'), 'w');
const t0 = Date.now();
const child = spawn(process.execPath, ['--inspect-brk=127.0.0.1:0', '--inspect-publish-uid=stderr', 'main.js'], { cwd: dir, stdio: ['pipe', out, err] });
child.stdin.end('hello input\n');
child.on('exit', (c) => console.log('EXIT', c, Date.now() - t0));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const poll = setInterval(() => {
  const text = fs.readFileSync(path.join(dir, 'err.txt'), 'utf8');
  const m = text.match(/ws:\/\/127\.0\.0\.1:\d+\/[\w-]+/);
  if (m && !ws) { console.log('URL', m[0]); connect(m[0]); }
  if (text.includes('Waiting for the debugger to disconnect')) { console.log('WAITING seen', Date.now() - t0); clearInterval(poll); ws.close(); }
}, 20);
let n = 0, mainId = null, armed = false;
const show = (v) => !v ? 'NOVALUE' : [v.type, v.subtype || '', v.className || '', v.unserializableValue ?? JSON.stringify(v.value) ?? (v.description || '').slice(0, 40)].join('/');
function connect(url) {
  ws = new WebSocket(url);
  ws.onmessage = async (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id) { pending.get(msg.id)(msg); return; }
    if (msg.method === 'Debugger.scriptParsed' && msg.params.url.endsWith('/main.js')) { mainId = msg.params.scriptId; console.log('SCRIPT', msg.params.url, mainId); }
    if (msg.method === 'Runtime.executionContextDestroyed') console.log('CTX DESTROYED', Date.now() - t0);
    if (msg.method !== 'Debugger.paused') return;
    const P = msg.params, f = P.callFrames[0];
    if (P.reason === 'exception') console.log('EXC', P.callFrames.map(c => c.location.scriptId + ':' + c.functionName).join(' > ').slice(0, 200), 'uncaught=', P.data.uncaught, show(P.data));
    if (f.location.scriptId !== mainId) { send('Debugger.resume'); return; }
    n++;
    if (!armed) {
      armed = true;
      const bps = await send('Debugger.getPossibleBreakpoints', { start: { scriptId: mainId, lineNumber: 0, columnNumber: 0 } });
      console.log('locations', bps.result.locations.length, JSON.stringify(bps.result.locations.slice(0, 8)));
      await Promise.all(bps.result.locations.map((loc) => send('Debugger.setBreakpoint', { location: loc })));
    }
    const info = { n, reason: P.reason, line: f.location.lineNumber + 1, col: f.location.columnNumber, fn: f.functionName, frames: P.callFrames.filter((c) => c.location.scriptId === mainId).map((c) => c.functionName || '(anon)').join('>'), ret: f.returnValue && show(f.returnValue) };
    const scopes = [];
    for (const s of f.scopeChain) {
      if (s.type === 'global') continue;
      const p = await send('Runtime.getProperties', { objectId: s.object.objectId, ownProperties: true, generatePreview: false });
      scopes.push(s.type + ':' + p.result.result.map((d) => d.name + '=' + show(d.value)).join(','));
      if (s.type === 'local' || s.type === 'block') for (const d of p.result.result) if (d.value?.objectId && d.value.type === 'object' && !['module', 'exports'].includes(d.name)) {
        const h = await send('HeapProfiler.getHeapObjectId', { objectId: d.value.objectId });
        info['heap_' + d.name] = h.result?.heapSnapshotObjectId ?? JSON.stringify(h.error);
        const props = await send('Runtime.getProperties', { objectId: d.value.objectId, ownProperties: true, generatePreview: false });
        info['props_' + d.name] = JSON.stringify(props.result.result.map((x) => [x.name, x.get ? 'GET:' + show(x.get) : show(x.value)])).slice(0, 300) + ' internal=' + JSON.stringify((props.result.internalProperties || []).map((x) => x.name + '=' + show(x.value)));
      }
    }
    info.scopes = scopes.filter(s=>!s.startsWith('local:exports')).join(' | ').slice(0, 300); for (const k of Object.keys(info)) if (k.startsWith('props_') && !['props_nums','props_m','props_st','props_p','props_cyc'].includes(k)) delete info[k];
    console.log(JSON.stringify(info));
    if (n > 400) { console.log('cap'); child.kill(); process.exit(); }
    send('Debugger.resume');
  };
  ws.onopen = async () => {
    await send('Runtime.enable'); await send('Debugger.enable'); await send('HeapProfiler.enable'); await send('HeapProfiler.startTrackingHeapObjects', { trackAllocations: false });
    await send('Debugger.setPauseOnExceptions', { state: 'all' });
    const lines = fs.readFileSync(path.join(dir, 'main.js'), 'utf8').split('\n').length;
    const url = require('node:url').pathToFileURL(path.join(dir, 'main.js')).href;
    for (let i = 0; i < lines; i++) await send('Debugger.setBreakpointByUrl', { url, lineNumber: i, columnNumber: 0 });
    await send('Runtime.runIfWaitingForDebugger');
  };
}
