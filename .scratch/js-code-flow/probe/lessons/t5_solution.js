const { Worker, isMainThread, parentPort } = require('node:worker_threads');

// 준비 값: 계산 반복 수예요.
const ROUNDS = 300000;

// 준비 코드: 결과를 검산할 수 있는 CPU 계산이에요. 같은 글자와 반복 수면 언제나 같은 값이에요.
function heavyHash(text, rounds) {
  let h = 7;
  for (let i = 0; i < rounds; i++) {
    for (let j = 0; j < text.length; j++) h = (Math.imul(h, 31) + text.charCodeAt(j) + i) >>> 0;
  }
  return h;
}

if (!isMainThread) {
  // 준비 코드(worker): 계산한 뒤 검증용 문(gate)이 열릴 때까지 최대 2초 기다렸다가 결과를 보내요.
  // 이 문은 "main이 ping을 먼저 처리했는가"를 확인하는 장치예요. 속도 측정이 아니에요.
  parentPort.on('message', ({ id, text, rounds, gate }) => {
    const result = heavyHash(text, rounds);
    const opened = Atomics.wait(new Int32Array(gate), 0, 0, 2000) !== 'timed-out';
    parentPort.postMessage({ id, result, opened });
  });
} else {
  main();
}

function main() {
  const log = [];
  const gate = new SharedArrayBuffer(4);
  // 준비 코드: worker가 최대 1개인 풀이에요. 처음 쓸 때 하나만 만들어요.
  let worker = null;
  let created = 0;
  let nextId = 0;
  const waiting = new Map();
  function runInPool(text, rounds) {
    if (!worker) {
      worker = new Worker(__filename);
      created++;
      worker.on('message', (m) => { waiting.get(m.id)(m); waiting.delete(m.id); });
    }
    return new Promise((resolve) => {
      const id = ++nextId;
      waiting.set(id, resolve);
      worker.postMessage({ id, text, rounds, gate });
    }).then((m) => {
      log.push('worker | 계산 끝 ' + (m.opened ? '검증 문이 열린 뒤 보냄' : '검증 문 2초 시간 초과'));
      return m.result;
    });
  }

  // 긴 계산 요청을 처리해요. async 함수라서 Promise를 돌려줘요.
  async function heavy(text) {
    // 고친 곳: async만 붙이면 계산은 여전히 main 스레드에서 돌아요.
    // 계산을 worker 풀에 보내면 main은 그동안 ping 같은 짧은 요청을 처리할 수 있어요.
    return runInPool(text, ROUNDS);
  }

  const text = require('node:fs').readFileSync(0, 'utf8').trim() || 'memo';
  const expected = heavyHash(text, ROUNDS);
  log.push('요청 | heavy ' + text);
  const done = heavy(text).then((result) => {
    log.push('응답 | heavy ' + (result === expected ? '검산 일치' : '검산 불일치'));
  });
  log.push('요청 | ping');
  setImmediate(() => {
    log.push('응답 | ping');
    const flag = new Int32Array(gate);
    Atomics.store(flag, 0, 1);
    Atomics.notify(flag, 0);
  });
  done.then(() => setImmediate(() => {
    for (const line of log) console.log(line);
    const ping = log.indexOf('응답 | ping');
    const heavyAt = log.findIndex((line) => line.startsWith('응답 | heavy'));
    console.log('ping이 heavy보다 먼저 응답 ' + (ping >= 0 && ping < heavyAt ? '예' : '아니요') + ', 만든 worker ' + created + '개');
    if (worker) worker.terminate();
  }));
}
