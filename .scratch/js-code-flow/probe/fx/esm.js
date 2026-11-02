import { readFileSync } from 'node:fs';
const words = readFileSync(0, 'utf8').trim().split(' ');
let count = 0;
for (const w of words) count += w.length;
console.log(count);
