let n = 0;
const inner = new Error('inner');
Object.defineProperty(inner, 'message', { get() { n++; return 'm'; } });
const outer = new Error('outer', { cause: inner });
console.log('n', n);
