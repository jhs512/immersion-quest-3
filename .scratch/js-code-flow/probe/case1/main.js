let counter = 0;
const watched = { get spy() { counter++; console.log('GETTER RAN'); return 1; }, plain: 2 };
const prox = new Proxy({}, { ownKeys() { console.log('TRAP RAN'); return []; }, get() { console.log('GET TRAP'); return 1; } });
const a = [1, 2];
const b = a;
const cyc = { name: 'c' };
cyc.self = cyc;
const nums = [NaN, -0, Infinity, 10n, undefined, null];
function add(x, y) {
  const s = x + y;
  return s;
}
const r = add(2, 3);
console.log(r, require('node:fs').readFileSync(0, 'utf8').trim());
let later = 5;
setImmediate(() => { console.log('imm', a.length); });
try { JSON.parse('{'); } catch (e) { console.log('caught'); }
const m = new Map([['k', a]]);
const st = new Set([1]);
const p = Promise.resolve(4);
console.log(counter);
