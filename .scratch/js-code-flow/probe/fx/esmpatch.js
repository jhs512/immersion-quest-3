import 'data:text/javascript,globalThis.n=0;const g=WeakMap.prototype.get;WeakMap.prototype.get=function(k){globalThis.n++;return g.call(this,k)}';
const a = [1];
const b = { a };
console.log('n', globalThis.n);
