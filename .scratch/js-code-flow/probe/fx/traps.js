let effects = 0;
class Account {
  #balance = 10;
  static get name() { effects++; return 'X'; }
  get [Symbol.toStringTag]() { effects++; return 'Tag'; }
  get balance() { effects++; return this.#balance; }
}
const acct = new Account();
const err = new Error('boom');
Object.defineProperty(err, 'stack', { get() { effects++; return 'S'; } });
const tagged = { get [Symbol.toStringTag]() { effects++; return 'T'; } };
const p = new Proxy([1, 2], { get() { effects++; return 1; }, ownKeys() { effects++; return []; }, getOwnPropertyDescriptor() { effects++; } });
Array.prototype.map = function () { effects++; return []; };
WeakMap.prototype.get = function () { effects++; };
const list = [acct, tagged];
console.log('effects', effects);
