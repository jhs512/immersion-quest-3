let n = 0;
const e = new Error('x');
Object.defineProperty(e, 'stack', { get: Object.prototype.toString });
Object.defineProperty(e, Symbol.toStringTag, { get() { n++; return 'T'; } });
console.log('n', n);
