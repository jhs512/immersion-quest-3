const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const context=vm.createContext({});
vm.runInContext(fs.readFileSync('assets/speech/pronunciation.js','utf8'),context);
vm.runInContext(fs.readFileSync('assets/speech/speech.js','utf8'),context);
const {pronunciationText,formatPrices}=context.molipSpeech;
test('won prices use grouping in text and Korean place values in speech',()=>{
 assert.equal(formatPrices('무료배송은 20000원, 주문은 19999원이에요.'),'무료배송은 20,000원, 주문은 19,999원이에요.');
 assert.equal(formatPrices('19,999원과 3.19999원, id19999원'),'19,999원과 3.19999원, id19999원');
 for(const price of ['19999원','19,999원','19,999'])assert.equal(pronunciationText(price),price.endsWith('원')?'만 구천구백구십구 원':'만 구천구백구십구');
 assert.equal(pronunciationText('0원, 1000원, 20000원, 100000000원'),'영 원, 천 원, 이만 원, 일억 원');
 assert.equal(pronunciationText('`amount = 19999`'),'amount 이퀄 19999'); // digits in code stay verbatim
});
