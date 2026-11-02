let n = 0;
Error.prepareStackTrace = () => { n++; return 's'; };
const e = new Error('x');
console.log('n', n);
