// 준비 값: 변형 검사에서 값이 달라져요.
const VALUE = 6;
setImmediate(() => console.log("ping"));
let sum = 0;
for (let n = 1; n <= VALUE; n++) sum += n;
console.log("합계 " + sum);
