// The Docker CLI lesson in the real debug player (validation transport, private data folder):
// a real Bash terminal instead of commands.sh, real docker output after Enter, the real grader,
// then the 관리자 자동 풀이 chip in every state and both looks, measured in the app itself.
//   node tools/design-capture.cjs tools/design-scenarios/docker-terminal.cjs target/docker-terminal-ui
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
module.exports = async (context) => {
  try { return await scenario(context); }
  catch (error) {
    await context.shot('failure').catch(() => {});
    throw Error(`${error.message}
--- screen ---
${(await context.page.locator('body').innerText().catch(() => '')).slice(0, 2500)}`);
  }
};
async function scenario({page, shot, dataDir}) {
  const notes = [];
  const button = (name) => page.getByRole('button', {name, exact: true});
  fs.writeFileSync(path.join(dataDir, 'pilot-course-reviewer'), '');
  await page.setViewportSize({width: 1440, height: 900});
  await page.emulateMedia({colorScheme: 'light'});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 리').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForSelector('.lesson-card', {timeout: 60000});
  // A fresh validation folder always asks for the course name before 학습 시작 is enabled.
  await page.waitForSelector('#course-display-name', {timeout: 30000});
  await page.locator('#course-display-name').fill('도커검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button.primary')].some(b => !b.disabled), null, {timeout: 30000});
  await page.locator('.lesson-card').first().locator('button.primary').click();
  const owner = () => page.evaluate(() => document.querySelector('#git-student-terminal')?.dataset.terminalSession);
  const screen = async () => page.evaluate(o => window.mq3GitTerminal?.text(o) ?? '', await owner());
  const ready = async () => {
    try { await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 180000}); }
    catch (error) { await shot('failure-not-ready'); throw Error(`terminal not ready: ${await page.locator('.coding-pane').innerText().catch(() => '')} | screen: ${await screen().catch(() => '')}`); }
  };
  const type = async (command) => {
    await page.locator('#git-student-terminal').click();
    await page.keyboard.type(command, {delay: 15});
    await page.keyboard.press('Enter');
  };
  const until = async (pattern, seconds = 120) => {
    const deadline = Date.now() + seconds * 1000;
    for (;;) {
      const text = await screen();
      if (pattern.test(text) && /\$\s*$/.test(text.trimEnd() + ' ')) return text;
      if (Date.now() > deadline) throw Error(`terminal never showed ${pattern}: ${text}`);
      await page.waitForTimeout(150);
    }
  };
  // The result pane keeps the previous verdict, so wait for this submission's own busy cycle.
  const submit = async () => {
    await page.evaluate(() => {
      const task = document.querySelector('.repository-task');
      window.__mq3SubmitBusy = false;
      window.__mq3SubmitObserver?.disconnect();
      window.__mq3SubmitObserver = new MutationObserver(() => { if (task.dataset.busy === 'true') window.__mq3SubmitBusy = true; });
      window.__mq3SubmitObserver.observe(task, {attributes: true, attributeFilter: ['data-busy']});
    });
    await button('제출').click();
    await page.waitForFunction(() => window.__mq3SubmitBusy && document.querySelector('.repository-task')?.dataset.busy === 'false'
      && ['passed', 'incorrect', 'error'].includes(document.querySelector('.result-pane')?.dataset.feedback), null, {timeout: 120000});
    return page.locator('.result-pane').getAttribute('data-feedback');
  };
  const next = async () => {
    await page.locator('.task-passed-dialog button.primary').click();
    await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady !== 'true', null, {timeout: 10000}).catch(() => {});
  };

  // 1. pull: a terminal, not an editor or a run button.
  await page.waitForSelector('#git-student-terminal[aria-label="실제 Docker 터미널"]', {timeout: 60000});
  assert.equal(await page.locator('.repository-task textarea.code-editor').count(), 0, 'no commands.sh editor');
  assert.equal(await page.locator('.repository-task [data-shortcut-action="run"]').count(), 0, 'no 코드 실행 button');
  assert.match(await page.locator('.pane-heading strong').innerText(), /Docker 터미널/);
  assert.doesNotMatch(await page.locator('.problem-pane').innerText(), /commands\.sh|코드 실행 버튼/);
  await ready();
  await shot('1-terminal-ready');
  assert.equal(await submit(), 'incorrect', 'nothing typed yet does not pass');
  await type('docker pull nginx:1.28-alpine');
  const pulled = await until(/Status: .*nginx:1\.28-alpine/, 900);
  notes.push('pull output: ' + pulled.split('\n').filter(l => /Status:|Digest:/.test(l)).join(' | '));
  await shot('1-pull-output');
  assert.equal(await submit(), 'passed');
  await shot('1-pull-passed');
  await next();

  // 2. run, 3. ps: the real table, in the same lesson session.
  await ready();
  await type('docker run -d --name "$BOX" -p 127.0.0.1::80 nginx:1.28-alpine');
  await until(/^[0-9a-f]{64}\s*$/m);
  assert.equal(await submit(), 'passed');
  await next();
  await ready();
  await type('docker images');
  await until(/1\.28-alpine/);
  await type('docker ps');
  const table = await until(/CONTAINER ID[\s\S]*NAMES[\s\S]*mq3lab-[a-z0-9-]+-nginx/);
  notes.push('ps table: ' + table.split('\n').filter(l => /CONTAINER ID|mq3lab-/.test(l)).map(l => l.trim()).join(' | '));
  await shot('3-ps-table');
  assert.equal(await submit(), 'passed');
  await page.locator('.task-passed-dialog button').last().click();

  // The auto-run chip, in the real header: the state mark keeps clear of the chip edge.
  const measure = () => page.evaluate(() => {
    const chip = document.querySelector('.auto-run-control .auto-run-chip');
    const mark = chip?.querySelector('span');
    if (!chip || !mark) return null;
    const c = chip.getBoundingClientRect(), d = mark.getBoundingClientRect();
    return {state: document.querySelector('.auto-run-control').dataset.state, left: +(d.left - c.left).toFixed(1), width: +c.width.toFixed(1)};
  });
  for (const scheme of ['light', 'dark']) {
    await page.emulateMedia({colorScheme: scheme});
    await page.waitForSelector('#auto-run-start:not([disabled])', {timeout: 60000});
    await page.locator('#auto-run-start').click();
    await page.waitForSelector('.auto-run-control[data-state="running"]', {timeout: 30000});
    await page.waitForTimeout(800);
    const running = await measure();
    await shot(`chip-${scheme}-running`);
    await page.locator('#auto-run-pause').click();
    await page.waitForSelector('.auto-run-chip .auto-run-state.paused', {timeout: 10000});
    const paused = await measure();
    await shot(`chip-${scheme}-paused`);
    await page.keyboard.press('Escape');
    await page.waitForSelector('.auto-run-control[data-state="stopped"]', {timeout: 30000});
    const stopped = await measure();
    await page.locator('.auto-run-details > summary').click();
    await shot(`chip-${scheme}-stopped`);
    await page.locator('.auto-run-dismiss').click();
    for (const m of [running, paused, stopped]) {
      assert.ok(m && m.left >= 4, `${scheme}: mark ${JSON.stringify(m)} is clear of the chip edge`);
    }
    notes.push(`${scheme}: ${JSON.stringify([running, paused, stopped])}`);
    // Stopping keeps the learner's own terminal state: the step still passes as it was.
    await ready();
    assert.equal(await submit(), 'passed', 'stopping the run kept the learner state');
    await page.locator('.task-passed-dialog button').last().click();
  }
  // 4. logs: the narration types in its own Docker terminal; the learner's container stays as it was.
  await page.locator('.study-navigation [data-step-id]', {hasText: '문제 4 · '}).click();
  await ready();
  await until(/\$/, 30);
  const learnerBefore = await screen();
  await page.evaluate(() => window.molipAgent?.setVoice(false));
  await button('해설 재생').click();
  await page.waitForFunction(() => window.molipAgent?.running, null, {timeout: 20000});
  const demoText = () => page.evaluate(() => {
    const o = document.querySelector('#git-demo-terminal')?.dataset.terminalSession;
    return o ? window.mq3GitDemoTerminal?.text(o) ?? '' : '';
  });
  let demo = '';
  for (const deadline = Date.now() + 240000; Date.now() < deadline;) {
    demo = await demoText().catch(() => demo) || demo;
    if (/docker logs[\s\S]*(Configuration complete|start worker process)/.test(demo)) break;
    await page.waitForTimeout(200);
  }
  assert.match(demo, /docker logs[\s\S]*(Configuration complete|start worker process)/, 'the narration terminal shows the real logs');
  assert.equal(await page.locator('#git-demo-terminal').getAttribute('aria-label'), '해설용 별도 Docker 터미널');
  await shot('4-narration-terminal');
  notes.push('narration logs: ' + demo.split('\n').filter(l => /docker logs|Configuration complete/.test(l)).map(l => l.trim()).join(' | '));
  await page.waitForFunction(() => !window.molipAgent?.running, null, {timeout: 240000});
  await ready();
  assert.equal((await screen()).trimEnd(), learnerBefore.trimEnd(), 'the narration did not type in the learner terminal');

  // 관리자 자동 풀이 from step 4: it types the narration's commands in the learner terminal; the grader decides.
  await page.locator('#auto-run-start').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.study-navigation [data-step-id]')].find(b => b.textContent.includes('문제 4 · '))?.dataset.completed === 'true',
    null, {timeout: 300000});
  const typed = await screen();
  assert.match(typed, /docker logs[\s\S]*(Configuration complete|start worker process)/, 'auto-run typed docker logs in the learner terminal');
  await shot('4-auto-run-passed');
  notes.push('auto-run learner terminal: ' + typed.split('\n').filter(l => /\$ docker/.test(l)).map(l => l.trim()).join(' | '));
  await page.keyboard.press('Escape');
  await page.waitForSelector('.auto-run-control[data-state="stopped"]', {timeout: 60000});
  await page.locator('.auto-run-details > summary').click().catch(() => {});
  await page.locator('.auto-run-dismiss').click().catch(() => {});
  await page.setViewportSize({width: 760, height: 800});
  await shot('narrow-terminal');
  return notes;
}
