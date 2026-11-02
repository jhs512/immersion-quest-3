const log = [];
class MyError extends Error { get message() { log.push('message'); return 'm'; } }
const a = new MyError();
class NamedError extends Error { get name() { log.push('name'); return 'N'; } }
const b = new NamedError('x');
const c = new Error('own');
Object.defineProperty(c, 'message', { get() { log.push('own message'); return 'z'; } });
const tagged = { get [Symbol.toStringTag]() { log.push('tag'); return 'T'; } };
class Ctor { static get name() { log.push('static name'); return 'S'; } }
const inst = new Ctor();
const d = new Date(0);
d.toString = () => { log.push('date toString'); return 'x'; };
Date.prototype.toISOString = () => { log.push('date iso'); return 'x'; };
const plain = new Error('plain');
console.log(log.join(','));
