let n = 0;
Error.prepareStackTrace = () => { n++; return 's'; };
try { null.x; } catch {}
console.log('n', n);
