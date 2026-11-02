const p = Promise.reject(new Error('handled later'));
p.catch(() => {});
process.exitCode = 2;
