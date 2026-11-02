let n = 0;
const e = new Error('x');
Object.setPrototypeOf(e, new Proxy(Error.prototype, { get(t, k, r) { n++; return Reflect.get(t, k, r); } }));
console.log('n', n);
