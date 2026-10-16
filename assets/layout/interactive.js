// Stepwise interactive pictures ("explorable explanations") from ```interactive fences.
//
//   ```interactive
//   위젯: overfit
//   ```
//
// A widget starts as an almost empty canvas and adds one idea per step when the student
// presses "다음 단계"; some steps hand over a slider or a button so the student can move
// the picture and watch the numbers change. Everything is plain SVG and runs offline.
(function () {
  'use strict';
  if (globalThis.molipInteractive || typeof document === 'undefined') return;
  const NS = 'http://www.w3.org/2000/svg';
  const el = (name, attrs, parent) => {
    const node = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    if (parent) parent.append(node);
    return node;
  };
  const text = (parent, x, y, content, attrs) => { const t = el('text', { x, y, ...(attrs || {}) }, parent); t.textContent = content; return t; };
  const show = node => { node.classList.add('on'); };
  const hide = node => { node.classList.remove('on'); };
  // Deterministic pseudo random numbers so every student sees the same picture.
  function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

  // ---- shared frame: canvas, caption, controls, step button ----
  function frame(container, title, height) {
    const root = document.createElement('div'); root.className = 'interactive';
    const head = document.createElement('div'); head.className = 'interactive-head';
    const h = document.createElement('strong'); h.textContent = title; head.append(h);
    const stepLabel = document.createElement('span'); stepLabel.className = 'interactive-step'; head.append(stepLabel);
    root.append(head);
    const svg = el('svg', { viewBox: `0 0 720 ${height}`, role: 'img', 'aria-label': title });
    root.append(svg);
    const caption = document.createElement('p'); caption.className = 'interactive-caption'; root.append(caption);
    const controls = document.createElement('div'); controls.className = 'interactive-controls'; root.append(controls);
    const next = document.createElement('button'); next.type = 'button'; next.className = 'interactive-next'; next.textContent = '다음 단계 →'; controls.append(next);
    const extra = document.createElement('div'); extra.className = 'interactive-extra'; controls.append(extra);
    container.append(root);
    let index = -1, steps = [];
    function go(i) {
      index = i;
      steps[i].enter();
      caption.textContent = steps[i].text;
      stepLabel.textContent = `${i + 1} / ${steps.length}`;
      next.textContent = i + 1 < steps.length ? '다음 단계 →' : '처음부터';
    }
    next.onclick = () => { if (index + 1 < steps.length) go(index + 1); else { steps.forEach(s => s.reset && s.reset()); go(0); } };
    return { svg, caption, extra, start(list) { steps = list; go(0); } };
  }
  function slider(extra, label, min, max, step, value, onInput) {
    const wrap = document.createElement('label'); wrap.className = 'interactive-slider';
    const name = document.createElement('span'); name.textContent = label; wrap.append(name);
    const input = document.createElement('input'); input.type = 'range'; input.min = min; input.max = max; input.step = step; input.value = value; wrap.append(input);
    const out = document.createElement('output'); out.textContent = value; wrap.append(out);
    input.oninput = () => { out.textContent = input.value; onInput(Number(input.value)); };
    wrap.hidden = true; extra.append(wrap);
    return { wrap, input, out, enable() { wrap.hidden = false; }, set(v) { input.value = v; out.textContent = v; } };
  }

  // ---- widget 1: overfitting — a 1-D regression tree whose depth the student controls ----
  function overfit(container) {
    const H = 360, W = 720, L = 60, R = 700, T = 30, B = 290;
    const f = frame(container, '트리 깊이와 과적합', H);
    const random = rng(7);
    const truth = x => 0.5 + 0.35 * Math.sin(x * 6.2);
    const make = n => Array.from({ length: n }, () => { const x = random(); return { x, y: Math.min(0.98, Math.max(0.02, truth(x) + (random() - 0.5) * 0.25)) }; });
    const train = make(24), test = make(12);
    const sx = x => L + x * (R - L), sy = y => B - y * (B - T);
    // Regression tree on one feature: split where squared error drops most, up to a depth.
    function fit(points, depth) {
      const mean = pts => pts.reduce((a, p) => a + p.y, 0) / pts.length;
      function node(pts, d) {
        if (d === 0 || pts.length <= 2) return { leaf: mean(pts) };
        const sorted = [...pts].sort((a, b) => a.x - b.x);
        let best = null;
        for (let i = 1; i < sorted.length; i++) {
          const left = sorted.slice(0, i), right = sorted.slice(i);
          const err = pts => { const m = mean(pts); return pts.reduce((a, p) => a + (p.y - m) ** 2, 0); };
          const score = err(left) + err(right);
          if (!best || score < best.score) best = { score, cut: (sorted[i - 1].x + sorted[i].x) / 2, left, right };
        }
        return { cut: best.cut, left: node(best.left, d - 1), right: node(best.right, d - 1) };
      }
      const tree = node(points, depth);
      const predict = x => { let n = tree; while (n.leaf === undefined) n = x < n.cut ? n.left : n.right; return n.leaf; };
      return predict;
    }
    const mae = (pts, predict) => pts.reduce((a, p) => a + Math.abs(p.y - predict(p.x)), 0) / pts.length;
    // Static scenery.
    el('line', { x1: L, y1: B, x2: R, y2: B, class: 'axis' }, f.svg);
    el('line', { x1: L, y1: T, x2: L, y2: B, class: 'axis' }, f.svg);
    text(f.svg, (L + R) / 2, B + 28, '입력 (예: 요금)', { class: 'label', 'text-anchor': 'middle' });
    text(f.svg, 18, (T + B) / 2, '정답', { class: 'label', 'text-anchor': 'middle', transform: `rotate(-90 18 ${(T + B) / 2})` });
    const gTrain = el('g', { class: 'fade' }, f.svg), gTest = el('g', { class: 'fade' }, f.svg), gModel = el('g', { class: 'fade' }, f.svg);
    for (const p of train) el('circle', { cx: sx(p.x), cy: sy(p.y), r: 5, class: 'train' }, gTrain);
    for (const p of test) el('path', { d: `M${sx(p.x) - 5},${sy(p.y) - 5} l10,10 m0,-10 l-10,10`, class: 'test' }, gTest);
    const line = el('path', { class: 'model' }, gModel);
    const scoreTrain = text(f.svg, R, T + 4, '', { class: 'score train-score', 'text-anchor': 'end' });
    const scoreTest = text(f.svg, R, T + 24, '', { class: 'score test-score', 'text-anchor': 'end' });
    let depth = 1, showTest = false;
    function draw() {
      const predict = fit(train, depth);
      let d = '';
      for (let i = 0; i <= 200; i++) { const x = i / 200; d += (i ? 'L' : 'M') + sx(x).toFixed(1) + ',' + sy(predict(x)).toFixed(1); }
      line.setAttribute('d', d);
      scoreTrain.textContent = `훈련 오차 ${mae(train, predict).toFixed(3)}`;
      scoreTest.textContent = showTest ? `테스트 오차 ${mae(test, predict).toFixed(3)}` : '';
    }
    const s = slider(f.extra, '트리 깊이 (max_depth)', 1, 8, 1, 1, v => { depth = v; draw(); });
    f.start([
      { text: '훈련 자료 24개입니다. 가로가 입력, 세로가 맞혀야 할 숫자입니다.', enter() { show(gTrain); hide(gModel); hide(gTest); s.wrap.hidden = true; showTest = false; }, reset() { depth = 1; s.set(1); } },
      { text: '깊이 1인 트리는 질문 한 번으로 두 구간을 나눕니다. 선이 모델의 답입니다.', enter() { depth = 1; s.set(1); draw(); show(gModel); } },
      { text: '슬라이더로 깊이를 올려 보세요. 훈련 오차가 계속 내려갑니다. 점을 전부 외워 가는 중입니다.', enter() { s.enable(); draw(); } },
      { text: '처음 보는 테스트 자료 12개(×)가 들어왔습니다. 깊이를 다시 움직여 보세요. 훈련 오차는 내려가는데 테스트 오차는 어느 깊이부터 다시 올라갑니다. 그 지점이 과적합의 시작입니다.', enter() { showTest = true; show(gTest); draw(); } },
    ]);
  }

  // ---- widget 2: threshold — probabilities become yes/no where the student puts the line ----
  function threshold(container) {
    const H = 330, W = 720, L = 50, R = 690, T = 40, B = 240, N = 40;
    const f = frame(container, '기준값: 확률을 경고로 바꾸는 선', H);
    const random = rng(11);
    // Defaults are more likely at high probabilities but also hide among the low ones, so the
    // threshold trades missed defaults against false alarms instead of just adding alarms.
    const customers = Array.from({ length: N }, (_, i) => { const p = (i + 0.5) / N; return { p, bad: random() < 0.15 + 0.75 * p }; });
    const sx = p => L + p * (R - L), bw = (R - L) / N - 2;
    el('line', { x1: L, y1: B, x2: R, y2: B, class: 'axis' }, f.svg);
    for (const v of [0, 0.5, 1]) text(f.svg, sx(v), B + 20, v.toFixed(1), { class: 'label', 'text-anchor': 'middle' });
    text(f.svg, (L + R) / 2, B + 40, '모델이 말한 부도 확률', { class: 'label', 'text-anchor': 'middle' });
    const bars = customers.map(c => el('rect', { x: sx(c.p) - bw / 2, y: B - 20 - c.p * (B - T - 30), width: bw, height: 20 + c.p * (B - T - 30), class: 'bar fade' }, f.svg));
    const marks = customers.map(c => el('circle', { cx: sx(c.p), cy: B - 10, r: 4, class: 'bad fade', style: c.bad ? '' : 'display:none' }, f.svg));
    const cut = el('line', { x1: sx(0.5), y1: T - 10, x2: sx(0.5), y2: B, class: 'cut fade' }, f.svg);
    const cutLabel = text(f.svg, sx(0.5), T - 16, '기준값 0.50', { class: 'label cut-label fade', 'text-anchor': 'middle' });
    const summary = text(f.svg, L, H - 12, '', { class: 'score' });
    const cost = text(f.svg, R, H - 12, '', { class: 'score', 'text-anchor': 'end' });
    let t = 0.5, showCost = false;
    function draw() {
      let tp = 0, fp = 0, fn = 0, tn = 0;
      customers.forEach((c, i) => {
        const warn = c.p >= t;
        bars[i].classList.toggle('warn', warn);
        if (warn && c.bad) tp++; else if (warn) fp++; else if (c.bad) fn++; else tn++;
      });
      cut.setAttribute('x1', sx(t)); cut.setAttribute('x2', sx(t)); cutLabel.setAttribute('x', sx(t)); cutLabel.textContent = `기준값 ${t.toFixed(2)}`;
      const precision = tp + fp ? tp / (tp + fp) : 0, recall = tp + fn ? tp / (tp + fn) : 0;
      summary.textContent = `경고 ${tp + fp}명 · 맞음 ${tp} 틀림 ${fp} · 놓침 ${fn} · 정밀도 ${precision.toFixed(2)} 재현율 ${recall.toFixed(2)}`;
      cost.textContent = showCost ? `비용 ${(fn * 100 + fp * 5).toLocaleString()}만 원 (놓침 100만, 헛경고 5만)` : '';
    }
    const s = slider(f.extra, '기준값', 0.05, 0.95, 0.05, 0.5, v => { t = v; draw(); });
    f.start([
      { text: '고객 40명을 모델이 말한 부도 확률 순서로 세웠어요. 막대가 높을수록 부도 확률이 커요.', enter() { bars.forEach(show); marks.forEach(hide); hide(cut); hide(cutLabel); s.wrap.hidden = true; showCost = false; t = 0.5; s.set(0.5); draw(); summary.textContent = ''; } },
      { text: '점이 찍힌 사람이 실제로 부도를 낸 고객이에요. 확률이 높은 쪽에 많지만 낮은 쪽에도 있어요.', enter() { marks.forEach(show); } },
      { text: '기준값 0.5보다 오른쪽이면 경고를 보내요. 경고 중 맞은 비율이 정밀도, 실제 부도 중 잡은 비율이 재현율이에요.', enter() { show(cut); show(cutLabel); draw(); } },
      { text: '선을 움직여 보세요. 왼쪽으로 가면 놓치는 부도(FN)는 줄고 헛경고(FP)는 늘어요. 어디에 둘지는 비용을 아는 사람이 정해요.', enter() { s.enable(); showCost = true; draw(); } },
    ]);
  }

  // ---- widget 3: temporal split — a date strip, the test window, and the boundary day ----
  function temporal(container) {
    const H = 300, N = 30, L = 30, R = 690, T = 70, cell = (R - L) / N;
    const f = frame(container, '시간 분리와 경계의 하루', H);
    const cells = [], labels = [];
    for (let i = 0; i < N; i++) {
      cells.push(el('rect', { x: L + i * cell + 1, y: T, width: cell - 2, height: 40, class: 'day fade' }, f.svg));
      if (i % 5 === 0) labels.push(text(f.svg, L + i * cell + cell / 2, T + 60, `${i + 1}일`, { class: 'label fade', 'text-anchor': 'middle' }));
    }
    const testStart = N - 8;
    const bracket = el('rect', { x: L + testStart * cell, y: T - 14, width: 8 * cell, height: 68, class: 'window fade' }, f.svg);
    const windowLabel = text(f.svg, L + (testStart + 4) * cell, T - 20, '테스트 기간 (마지막 8일)', { class: 'label fade', 'text-anchor': 'middle' });
    const arrow = el('path', { d: `M${L + (testStart - 1) * cell + cell / 2},${T + 40} q${cell / 2},40 ${cell},0`, class: 'arrow fade' }, f.svg);
    const arrowLabel = text(f.svg, L + (testStart - 0.5) * cell, T + 100, '이 행의 정답은 테스트 첫날 종가', { class: 'label fade', 'text-anchor': 'middle' });
    const shuffled = el('g', { class: 'fade' }, f.svg);
    const random = rng(3);
    const order = Array.from({ length: N }, (_, i) => i).sort(() => random() - 0.5);
    order.forEach((day, slot) => { el('rect', { x: L + slot * cell + 1, y: T + 150, width: cell - 2, height: 30, class: day >= testStart ? 'day test' : 'day' }, shuffled); });
    text(shuffled, L, T + 200, '무작위로 섞으면: 미래(진한 칸)로 과거를 맞히게 됩니다', { class: 'label' });
    f.start([
      { text: '거래일 30일을 날짜순으로 세웠습니다. 시간 자료는 순서가 있습니다.', enter() { cells.forEach(c => { show(c); c.classList.remove('test', 'boundary'); }); labels.forEach(show); hide(bracket); hide(windowLabel); hide(arrow); hide(arrowLabel); hide(shuffled); } },
      { text: '뒤쪽 8일을 테스트로 떼어 둡니다. 앞 기간으로 훈련하고 뒤 기간으로 채점합니다.', enter() { show(bracket); show(windowLabel); cells.forEach((c, i) => c.classList.toggle('test', i >= testStart)); } },
      { text: '경계 바로 앞 하루를 보세요. 입력 날짜는 훈련이지만 그 행의 정답은 테스트 첫날의 종가입니다. 그래서 훈련에서 뺍니다.', enter() { show(arrow); show(arrowLabel); cells[testStart - 1].classList.add('boundary'); } },
      { text: '비교: 승객처럼 무작위로 섞어 나누면 어떻게 될까요. 6월 가격으로 배워 3월을 맞히는 셈이 됩니다.', enter() { show(shuffled); } },
    ]);
  }

  // ---- widget 4: stratified split — a random split can skew the survivor share; stratify keeps it ----
  function stratify(container) {
    const H = 330, N = 100, SURV = 38, COLS = 20, cell = 14;
    const f = frame(container, '층화 분할: 비율을 지키며 나누기', H);
    const random = rng(21);
    const people = Array.from({ length: N }, (_, i) => ({ i, survived: i < SURV }));
    const gAll = el('g', { class: 'fade' }, f.svg), gSplit = el('g', { class: 'fade' }, f.svg);
    const dots = people.map(p => el('circle', { cx: 60 + (p.i % COLS) * cell, cy: 40 + Math.floor(p.i / COLS) * cell, r: 5, class: p.survived ? 'train' : 'dead' }, gAll));
    text(gAll, 60, 24, '승객 100명 · 생존 38명 (38%)', { class: 'label' });
    const trainBox = el('rect', { x: 60, y: 150, width: 300, height: 130, rx: 8, class: 'box' }, gSplit);
    const testBox = el('rect', { x: 400, y: 150, width: 260, height: 130, rx: 8, class: 'box' }, gSplit);
    const trainLabel = text(gSplit, 70, 170, '', { class: 'score' });
    const testLabel = text(gSplit, 410, 170, '', { class: 'score test-score' });
    const trainDots = [], testDots = [];
    let useStratify = false;
    function split() {
      const shuffled = [...people].sort(() => random() - 0.5);
      let test;
      if (useStratify) {
        const s = shuffled.filter(p => p.survived).slice(0, Math.round(SURV * 0.2)), d = shuffled.filter(p => !p.survived).slice(0, 20 - Math.round(SURV * 0.2));
        test = new Set([...s, ...d].map(p => p.i));
      } else test = new Set(shuffled.slice(0, 20).map(p => p.i));
      for (const d of [...trainDots, ...testDots]) d.remove();
      trainDots.length = 0; testDots.length = 0;
      let ti = 0, si = 0, tSurv = 0, sSurv = 0;
      for (const p of people) {
        if (test.has(p.i)) { testDots.push(el('circle', { cx: 410 + (si % 10) * cell, cy: 190 + Math.floor(si / 10) * cell, r: 5, class: p.survived ? 'train' : 'dead' }, gSplit)); si++; sSurv += p.survived; }
        else { trainDots.push(el('circle', { cx: 70 + (ti % 20) * cell, cy: 190 + Math.floor(ti / 20) * cell, r: 5, class: p.survived ? 'train' : 'dead' }, gSplit)); ti++; tSurv += p.survived; }
      }
      trainLabel.textContent = `훈련 80명 · 생존 ${tSurv}명 (${Math.round(tSurv / 80 * 100)}%)`;
      testLabel.textContent = `테스트 20명 · 생존 ${sSurv}명 (${Math.round(sSurv / 20 * 100)}%)`;
      dots.forEach(d => d.classList.toggle('dim', true));
    }
    const again = document.createElement('button'); again.type = 'button'; again.className = 'interactive-action'; again.textContent = '랜덤 나누기'; again.hidden = true; again.onclick = split; f.extra.append(again);
    const toggle = document.createElement('label'); toggle.className = 'interactive-toggle'; toggle.hidden = true;
    const box = document.createElement('input'); box.type = 'checkbox'; toggle.append(box, document.createTextNode(' stratify=y')); box.onchange = () => { useStratify = box.checked; split(); }; f.extra.append(toggle);
    f.start([
      { text: '승객 100명 중 38명이 생존(초록)입니다. 이 비율이 정답의 비율입니다.', enter() { show(gAll); hide(gSplit); again.hidden = true; toggle.hidden = true; box.checked = false; useStratify = false; dots.forEach(d => d.classList.remove('dim')); } },
      { text: '무작위로 20명을 테스트로 떼어 냈습니다. 테스트 쪽 생존 비율을 보세요. "랜덤 나누기"를 눌러 보면 매번 다릅니다.', enter() { show(gSplit); again.hidden = false; split(); } },
      { text: 'stratify=y를 켜고 다시 나눠 보세요. 생존자와 사망자를 각각 20%씩 떼어 내므로 테스트 비율이 전체 비율 38%에서 거의 벗어나지 않습니다.', enter() { again.hidden = true; toggle.hidden = false; } },
    ]);
  }

  // ---- widget 5: leakage — add the lifeboat column and watch the score lie ----
  function leakage(container) {
    const H = 300, f = frame(container, '누수: 답을 알려 주는 열', H);
    const features = ['객실등급', '성별', '나이', '형제배우자', '부모자녀', '요금', '탑승항구'];
    const gList = el('g', { class: 'fade' }, f.svg), gBar = el('g', { class: 'fade' }, f.svg), gBoat = el('g', { class: 'fade' }, f.svg), gTime = el('g', { class: 'fade' }, f.svg);
    features.forEach((name, i) => { el('rect', { x: 40, y: 30 + i * 26, width: 130, height: 20, rx: 5, class: 'chip' }, gList); text(gList, 105, 45 + i * 26, name, { class: 'label', 'text-anchor': 'middle' }); });
    const boatChip = el('rect', { x: 40, y: 30 + 7 * 26, width: 130, height: 20, rx: 5, class: 'chip leak' }, gBoat);
    text(gBoat, 105, 45 + 7 * 26, '구명보트 번호', { class: 'label', 'text-anchor': 'middle' });
    el('rect', { x: 260, y: 40, width: 60, height: 200, class: 'track' }, gBar);
    const bar = el('rect', { x: 260, y: 240, width: 60, height: 0, class: 'acc' }, gBar);
    const accText = text(gBar, 290, 30, '', { class: 'score', 'text-anchor': 'middle' });
    text(gBar, 290, 262, '테스트 정확도', { class: 'label', 'text-anchor': 'middle' });
    // Timeline: when each piece of information exists.
    el('line', { x1: 380, y1: 150, x2: 690, y2: 150, class: 'axis' }, gTime);
    for (const [x, label] of [[400, '승선'], [535, '사고'], [670, '구조 뒤']]) { el('circle', { cx: x, cy: 150, r: 5, class: 'tick' }, gTime); text(gTime, x, 175, label, { class: 'label', 'text-anchor': 'middle' }); }
    text(gTime, 400, 120, '등급·성별·나이·요금', { class: 'label', 'text-anchor': 'middle' });
    text(gTime, 535, 120, '맞혀야 하는 순간', { class: 'label cut-label', 'text-anchor': 'middle' });
    text(gTime, 670, 120, '구명보트 번호 기록', { class: 'label', 'text-anchor': 'middle', fill: '#ff6b6b' });
    function setAcc(v) { bar.setAttribute('height', 200 * v); bar.setAttribute('y', 240 - 200 * v); accText.textContent = `${Math.round(v * 100)}%`; bar.classList.toggle('leak', v > 0.95); }
    const toggle = document.createElement('label'); toggle.className = 'interactive-toggle'; toggle.hidden = true;
    const box = document.createElement('input'); box.type = 'checkbox'; toggle.append(box, document.createTextNode(' 구명보트 열 포함')); box.onchange = () => { if (box.checked) show(gBoat); else hide(gBoat); setAcc(box.checked ? 0.99 : 0.78); }; f.extra.append(toggle);
    f.start([
      { text: '배를 타기 전에 알 수 있는 일곱 열로 생존을 맞힙니다.', enter() { show(gList); hide(gBar); hide(gBoat); hide(gTime); toggle.hidden = true; box.checked = false; } },
      { text: '테스트 정확도는 78% 근처입니다. 재료가 이 정도면 이 정도가 실력입니다.', enter() { show(gBar); setAcc(0.78); } },
      { text: '구명보트 번호 열을 넣어 보세요. 정확도가 99%로 뜁니다. 좋아진 걸까요?', enter() { toggle.hidden = false; } },
      { text: '시점을 보세요. 구명보트 번호는 구조된 뒤에 적힙니다. 맞혀야 하는 순간에는 없는 정보라 답을 보고 답을 맞힌 셈입니다. 이것이 누수입니다.', enter() { show(gTime); box.checked = true; show(gBoat); setAcc(0.99); } },
    ]);
  }

  // ---- widget 6: MAE — error bars stack up one day at a time and average out ----
  function maeWidget(container) {
    const H = 340, L = 60, R = 560, T = 30, B = 260, days = 10;
    const f = frame(container, 'MAE: 하루하루 빗나간 만큼의 평균', H);
    const random = rng(5);
    const actual = []; let v = 50;
    for (let i = 0; i < days; i++) { v += (random() - 0.5) * 12; actual.push(Math.round(v * 10) / 10); }
    const baseline = actual.map((_, i) => (i ? actual[i - 1] : actual[0]));
    const sx = i => L + i * (R - L) / (days - 1), lo = Math.min(...actual) - 8, hi = Math.max(...actual) + 8, sy = y => B - (y - lo) / (hi - lo) * (B - T);
    el('line', { x1: L, y1: B, x2: R, y2: B, class: 'axis' }, f.svg);
    text(f.svg, (L + R) / 2, B + 24, '테스트 기간의 거래일', { class: 'label', 'text-anchor': 'middle' });
    const gActual = el('g', { class: 'fade' }, f.svg), gPred = el('g', { class: 'fade' }, f.svg), gErr = el('g', {}, f.svg), gMean = el('g', { class: 'fade' }, f.svg);
    const pathActual = el('path', { class: 'model actual' }, gActual), pathPred = el('path', { class: 'model pred' }, gPred);
    actual.forEach((y, i) => el('circle', { cx: sx(i), cy: sy(y), r: 4, class: 'train' }, gActual));
    const errBars = actual.map((y, i) => el('line', { x1: sx(i), y1: sy(y), x2: sx(i), y2: sy(baseline[i]), class: 'err fade' }, gErr));
    const errLabels = actual.map((y, i) => text(gErr, sx(i) + 6, (sy(y) + sy(baseline[i])) / 2, '', { class: 'label err-label fade' }));
    el('rect', { x: 600, y: T, width: 50, height: B - T, class: 'track' }, gMean);
    const meanBar = el('rect', { x: 600, y: B, width: 50, height: 0, class: 'acc' }, gMean);
    const meanText = text(gMean, 625, T - 8, '', { class: 'score', 'text-anchor': 'middle' });
    text(gMean, 625, B + 24, 'MAE', { class: 'label', 'text-anchor': 'middle' });
    let offset = 0;
    function draw(revealUpTo) {
      const pred = baseline.map(p => p + offset);
      pathActual.setAttribute('d', actual.map((y, i) => (i ? 'L' : 'M') + sx(i) + ',' + sy(y)).join(''));
      pathPred.setAttribute('d', pred.map((y, i) => (i ? 'L' : 'M') + sx(i) + ',' + sy(y)).join(''));
      let sum = 0;
      actual.forEach((y, i) => {
        const e = Math.abs(y - pred[i]); sum += e;
        errBars[i].setAttribute('y1', sy(y)); errBars[i].setAttribute('y2', sy(pred[i]));
        errLabels[i].setAttribute('y', (sy(y) + sy(pred[i])) / 2 + 4); errLabels[i].textContent = e.toFixed(1);
        if (i < revealUpTo) { show(errBars[i]); show(errLabels[i]); } else { hide(errBars[i]); hide(errLabels[i]); }
      });
      const mae = sum / days, scale = (B - T) / 20;
      meanBar.setAttribute('height', Math.min(B - T, mae * scale)); meanBar.setAttribute('y', B - Math.min(B - T, mae * scale));
      meanText.textContent = `MAE ${mae.toFixed(2)}`;
    }
    let timer;
    const s = slider(f.extra, '예측을 위아래로 이동', -10, 10, 1, 0, val => { offset = val; draw(days); });
    f.start([
      { text: '테스트 기간 10일의 실제 종가입니다.', enter() { clearTimeout(timer); offset = 0; s.set(0); s.wrap.hidden = true; hide(gPred); hide(gMean); draw(0); show(gActual); } },
      { text: '기준 예측 "내일 종가 = 오늘 종가"를 겹쳤습니다. 하루 늦게 따라가는 선입니다.', enter() { show(gPred); draw(0); } },
      { text: '날마다 실제와 예측의 차이를 재서 세웁니다. 부호는 버리고 크기만 봅니다.', enter() { let i = 0; const tick = () => { i++; draw(i); if (i < days) timer = setTimeout(tick, 220); }; timer = setTimeout(tick, 100); } },
      { text: '열 개 차이의 평균이 MAE입니다. 슬라이더로 예측을 위아래로 옮겨 보세요. 한쪽으로 치우칠수록 평균 오차가 커집니다.', enter() { clearTimeout(timer); draw(days); show(gMean); s.enable(); } },
    ]);
  }

  // ---- widget 7: moving average — the window slides and the line smooths ----
  function movingAverage(container) {
    const H = 320, L = 50, R = 690, T = 30, B = 250, N = 40;
    const f = frame(container, '이동평균: 창 안의 평균을 이어 그리기', H);
    const random = rng(9);
    const price = []; let v = 50;
    for (let i = 0; i < N; i++) { v += (random() - 0.48) * 8; price.push(v); }
    const sx = i => L + i * (R - L) / (N - 1), lo = Math.min(...price) - 5, hi = Math.max(...price) + 5, sy = y => B - (y - lo) / (hi - lo) * (B - T);
    el('line', { x1: L, y1: B, x2: R, y2: B, class: 'axis' }, f.svg);
    const gPrice = el('g', { class: 'fade' }, f.svg), gWin = el('g', { class: 'fade' }, f.svg), gMa = el('g', { class: 'fade' }, f.svg);
    el('path', { d: price.map((y, i) => (i ? 'L' : 'M') + sx(i) + ',' + sy(y)).join(''), class: 'model actual' }, gPrice);
    const win = el('rect', { x: 0, y: T, width: 0, height: B - T, class: 'window-fill' }, gWin);
    const winDot = el('circle', { r: 6, class: 'ma-dot' }, gWin);
    const winLabel = text(gWin, 0, T - 8, '', { class: 'label cut-label', 'text-anchor': 'middle' });
    const maPath = el('path', { class: 'model ma' }, gMa);
    let window = 5;
    function ma(i) { if (i < window - 1) return null; let s = 0; for (let k = i - window + 1; k <= i; k++) s += price[k]; return s / window; }
    function draw() {
      const i = 20, m = ma(i);
      win.setAttribute('x', sx(i - window + 1) - 6); win.setAttribute('width', sx(i) - sx(i - window + 1) + 12);
      winDot.setAttribute('cx', sx(i)); winDot.setAttribute('cy', sy(m));
      winLabel.setAttribute('x', (sx(i - window + 1) + sx(i)) / 2); winLabel.textContent = `최근 ${window}일 평균 ${m.toFixed(1)}`;
      let d = '', started = false;
      for (let k = 0; k < N; k++) { const y = ma(k); if (y === null) continue; d += (started ? 'L' : 'M') + sx(k) + ',' + sy(y); started = true; }
      maPath.setAttribute('d', d);
    }
    const s = slider(f.extra, '창 크기 (거래일)', 2, 20, 1, 5, val => { window = val; draw(); });
    f.start([
      { text: '40거래일의 종가입니다. 하루하루 흔들립니다.', enter() { window = 5; s.set(5); s.wrap.hidden = true; show(gPrice); hide(gWin); hide(gMa); } },
      { text: '어느 날의 이동평균은 그날까지 최근 5일(창)의 평균입니다. 창 안의 값 다섯 개를 더해 5로 나눈 점입니다.', enter() { draw(); show(gWin); } },
      { text: '창을 하루씩 밀며 같은 계산을 하면 선이 됩니다. 처음 4일은 5개가 안 모여 비어 있습니다.', enter() { show(gMa); } },
      { text: '창 크기를 바꿔 보세요. 창이 클수록 선이 부드러워지고 비는 날도 늘어납니다.', enter() { s.enable(); draw(); } },
    ]);
  }

  // ---- widget 8: histogram bins — the same ages, coarser or finer ----
  function histogram(container) {
    const H = 320, L = 50, R = 690, T = 40, B = 240;
    const f = frame(container, '히스토그램: 구간 수는 보는 방식일 뿐', H);
    const random = rng(13);
    // Ages shaped like the Titanic distribution: many in their twenties, a few children and elderly.
    const ages = Array.from({ length: 300 }, () => { const u = random(); const base = u < 0.1 ? random() * 12 : u < 0.8 ? 16 + random() * 30 : 40 + random() * 40; return Math.min(80, Math.max(0, Math.round(base))); });
    const sx = a => L + a / 80 * (R - L);
    el('line', { x1: L, y1: B, x2: R, y2: B, class: 'axis' }, f.svg);
    for (const a of [0, 20, 40, 60, 80]) text(f.svg, sx(a), B + 20, String(a), { class: 'label', 'text-anchor': 'middle' });
    text(f.svg, (L + R) / 2, B + 40, '나이', { class: 'label', 'text-anchor': 'middle' });
    const gRug = el('g', { class: 'fade' }, f.svg), gBars = el('g', { class: 'fade' }, f.svg);
    for (const a of ages) el('line', { x1: sx(a) + (random() - 0.5) * 4, y1: B, x2: sx(a) + (random() - 0.5) * 4, y2: B - 10, class: 'rug' }, gRug);
    const countText = text(f.svg, R, T - 10, '', { class: 'score', 'text-anchor': 'end' });
    let bins = 5;
    function draw() {
      while (gBars.firstChild) gBars.firstChild.remove();
      const counts = Array(bins).fill(0);
      for (const a of ages) counts[Math.min(bins - 1, Math.floor(a / 80 * bins))]++;
      const max = Math.max(...counts), w = (R - L) / bins;
      counts.forEach((c, i) => { const h = c / max * (B - T - 30); el('rect', { x: L + i * w + 1, y: B - 12 - h, width: w - 2, height: h, class: 'hist' }, gBars); if (bins <= 12) text(gBars, L + i * w + w / 2, B - 16 - h, String(c), { class: 'label', 'text-anchor': 'middle' }); });
      countText.textContent = `구간 ${bins}개 · 막대 높이의 합은 늘 300명`;
    }
    const s = slider(f.extra, '구간 수 (bins)', 3, 40, 1, 5, val => { bins = val; draw(); });
    f.start([
      { text: '승객 300명의 나이를 바닥에 눈금처럼 찍었습니다. 어디에 몰려 있는지 보이나요?', enter() { bins = 5; s.set(5); s.wrap.hidden = true; show(gRug); hide(gBars); countText.textContent = ''; } },
      { text: '나이를 다섯 구간으로 잘라 구간마다 몇 명인지 세우면 히스토그램입니다.', enter() { draw(); show(gBars); } },
      { text: '구간 수를 바꿔 보세요. 자료는 그대로인데 모양이 달라집니다. 그래서 보고할 때 구간 수를 적습니다.', enter() { s.enable(); draw(); } },
    ]);
  }

  const WIDGETS = { overfit, threshold, temporal, stratify, leakage, mae: maeWidget, moving: movingAverage, histogram };
  const seen = new WeakSet();
  function render(root) {
    if (!(root instanceof Element) && root !== document) return;
    const codes = [...root.querySelectorAll('pre > code.language-interactive')];
    if (root instanceof Element && root.matches('pre > code.language-interactive')) codes.push(root);
    for (const code of codes) {
      const pre = code.parentElement;
      if (!pre || !pre.isConnected || seen.has(pre)) continue;
      seen.add(pre);
      const name = (code.textContent.match(/위젯:\s*(\w+)/) || [])[1];
      const figure = document.createElement('figure'); figure.className = 'interactive-strip';
      if (WIDGETS[name]) { try { WIDGETS[name](figure); } catch (error) { figure.textContent = '그림을 그리지 못했습니다: ' + error.message; } }
      else figure.textContent = '알 수 없는 위젯: ' + name;
      pre.replaceWith(figure);
    }
  }
  new MutationObserver(records => { for (const r of records) for (const n of r.addedNodes) if (n instanceof Element) render(n); }).observe(document.body, { childList: true, subtree: true });
  render(document);
  globalThis.molipInteractive = { render, WIDGETS };
})();
