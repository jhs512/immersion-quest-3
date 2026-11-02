// 준비 값: 변형 검사에서 값이 달라져요.
const VALUE = 6;
const {Worker} = require("node:worker_threads");
const source = `require("node:worker_threads").parentPort.postMessage(${VALUE} * 2);`;
const worker = new Worker(source, {eval:true});
worker.on("exit", value => console.log("계산 결과 " + value));
