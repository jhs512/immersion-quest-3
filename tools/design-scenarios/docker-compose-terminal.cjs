// The Compose/Dockerfile steps of the Docker lesson in the real debug player (validation transport,
// private data folder): a file editor above the real Docker terminal, keyboard edits saved into the
// terminal's folder, real docker compose output after Enter, the real grader, narration in its own
// editor and terminal, and 관리자 자동 풀이 editing the learner's files and typing in the learner terminal.
// Leaving the lesson at the end must remove exactly the Docker projects this run created.
//   node tools/design-capture.cjs tools/design-scenarios/docker-compose-terminal.cjs target/docker-compose-terminal-ui
// MQ3_STEPS=9,10,13,leave picks phases. Every phase appends a checkpoint to <output>/progress.jsonl as
// it finishes, and the automatic solve logs its stage every 10 s, so a cut-off run still shows how far it got.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
module.exports = async (context) => {
  try { return await scenario(context); }
  catch (error) {
    await context.shot('failure').catch(() => {});
    throw Error(`${error.message}
--- screen ---
${(await context.page.locator('body').innerText().catch(() => '')).slice(0, 2500)}`);
  }
};
// The learner's real practice folder for a step: the newest practice-* whose work/ has this file.
function practiceFile(dataDir, name, includes) {
  const root = path.join(dataDir, 'git-practices');
  const folders = fs.existsSync(root) ? fs.readdirSync(root).filter(f => f.startsWith('practice-')) : [];
  const found = folders.map(f => path.join(root, f, 'work', name)).filter(p => fs.existsSync(p))
    .map(p => ({p, text: fs.readFileSync(p, 'utf8'), at: fs.statSync(p).mtimeMs})).filter(f => f.text.includes(includes));
  found.sort((a, b) => b.at - a.at);
  return found[0];
}
// Read-only Docker queries: resources carrying one of these projects' labels, by kind.
function owned(projects) {
  const found = [];
  for (const project of projects) {
    for (const [kind, args] of [['container', ['ps', '-aq']], ['volume', ['volume', 'ls', '-q']], ['network', ['network', 'ls', '-q']], ['image', ['image', 'ls', '-q']]]) {
      for (const label of ['com.docker.compose.project', 'io.mq3.project']) {
        let out = '';
        try { out = execFileSync('docker', [...args, '--filter', `label=${label}=${project}`], {encoding: 'utf8', timeout: 30000}); } catch {}
        for (const id of out.split(/\s+/).filter(Boolean)) found.push(`${kind}:${project}:${id}`);
      }
    }
  }
  return [...new Set(found)];
}
// Projects the app registered (its .owned receipt) since `since`: this run's, not the user's.
function projectsSince(since) {
  const dir = path.join(os.tmpdir(), 'mq3-docker-labs');
  return fs.existsSync(dir) ? fs.readdirSync(dir).filter(f => f.endsWith('.owned') && fs.statSync(path.join(dir, f)).mtimeMs >= since).map(f => f.slice(0, -'.owned'.length)) : [];
}
async function scenario({page, shot, dataDir, output}) {
  const notes = [];
  const started = Date.now();
  const steps = new Set((process.env.MQ3_STEPS || '9,10,13,leave').split(',').map(s => s.trim()));
  const progress = (phase, data = {}) => fs.appendFileSync(path.join(output, 'progress.jsonl'),
    JSON.stringify({at: new Date().toISOString(), seconds: Math.round((Date.now() - started) / 1000), phase, ...data}) + '\n');
  progress('start', {data_dir: dataDir, steps: [...steps]});
  const button = (name) => page.getByRole('button', {name, exact: true});
  fs.writeFileSync(path.join(dataDir, 'pilot-course-reviewer'), '');
  await page.setViewportSize({width: 1440, height: 900});
  await page.emulateMedia({colorScheme: 'light'});
  await page.waitForSelector('.pilot-toolbox', {timeout: 60000});
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = true; });
  await button('버전 리').click();
  await page.evaluate(() => { document.querySelector('.pilot-toolbox').open = false; });
  await page.waitForSelector('.lesson-card', {timeout: 60000});
  await page.waitForSelector('#course-display-name', {timeout: 30000});
  await page.locator('#course-display-name').fill('도커검증');
  await page.locator('.course-identity button[type=submit]').click();
  await page.waitForFunction(() => [...document.querySelectorAll('.lesson-card button.primary')].some(b => !b.disabled), null, {timeout: 30000});
  await page.locator('.lesson-card').first().locator('button.primary').click();
  const owner = () => page.evaluate(() => document.querySelector('#git-student-terminal')?.dataset.terminalSession);
  const screen = async () => page.evaluate(o => window.mq3GitTerminal?.text(o) ?? '', await owner());
  const ready = async () => {
    try { await page.waitForFunction(() => document.querySelector('.repository-task')?.dataset.gitReady === 'true', null, {timeout: 300000}); }
    catch (error) { await shot('failure-not-ready'); throw Error(`terminal not ready: ${await page.locator('.coding-pane').innerText().catch(() => '')} | screen: ${await screen().catch(() => '')}`); }
  };
  let lastTyped = '';
  const type = async (command) => {
    lastTyped = command;
    await page.locator('#git-student-terminal').click();
    await page.keyboard.type(command, {delay: 12});
    await page.keyboard.press('Enter');
  };
  // Wait until the latest command's output matches and the prompt is back.
  const until = async (pattern, seconds = 180) => {
    const deadline = Date.now() + seconds * 1000;
    for (;;) {
      const text = await screen();
      // The output of the command typed last: from its own prompt line to the end.
      const last = text.slice(Math.max(0, text.lastIndexOf('$ ' + lastTyped)));
      if (pattern.test(last) && /\$\s*$/.test(text.trimEnd() + ' ')) return last;
      if (Date.now() > deadline) throw Error(`terminal never showed ${pattern}: ${text.slice(-1500)}`);
      await page.waitForTimeout(150);
    }
  };
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
      && ['passed', 'incorrect', 'error'].includes(document.querySelector('.result-pane')?.dataset.feedback), null, {timeout: 180000});
    return page.locator('.result-pane').getAttribute('data-feedback');
  };
  // The notes above a Compose editor never run under its file tabs (a short pane shrank them once).
  const notesClear = async (where) => {
    const gap = await page.evaluate(() => {
      const notes = document.querySelector('.compose-workspace>.docker-notes')?.getBoundingClientRect();
      const source = document.querySelector('.compose-workspace>.compose-source')?.getBoundingClientRect();
      return notes && source ? Math.round(source.top - notes.bottom) : null;
    });
    assert.ok(gap !== null && gap >= 0, `${where}: Docker notes overlap the file tabs by ${-gap}px`);
    notes.push(`${where} notes-to-tabs gap: ${gap}px`);
  };
  const goto = async (number) => {
    await page.locator('.study-navigation [data-step-id]', {hasText: `문제 ${number} · `}).click();
    await ready();
    await until(/\$/, 30);
  };

  // 9. pid1-lifetime: compose.yaml editor above the real terminal, no run button, no lab.sh.
  if (steps.has('9')) {
  await goto(9);
  const learner = page.locator('.repository-task .coding-pane, .repository-task .editor-pane').first();
  await page.waitForSelector('textarea[data-editor-file="compose.yaml"]', {state: 'attached', timeout: 30000});
  assert.equal(await page.locator('#git-student-terminal').getAttribute('aria-label'), '실제 Docker 터미널');
  assert.equal(await page.locator('.repository-task [data-shortcut-action="run"]').count(), 0, 'no 코드 실행 button');
  assert.match(await page.locator('.pane-heading strong').innerText(), /compose\.yaml · Docker 터미널/);
  assert.doesNotMatch(await page.locator('.problem-pane').innerText(), /lab\.sh|코드 실행 버튼|commands\.sh/);
  assert.equal(await page.locator('[data-editor-tab="compose.yaml"]').getAttribute('aria-selected'), 'true');
  await shot('9-editor-and-terminal');
  assert.equal(await submit(), 'incorrect', 'nothing typed yet does not pass');
  await type('docker compose up -d');
  notes.push('9 up: ' + (await until(/memo-1\s+Started/, 900)).split('\n').filter(l => /memo-1/.test(l)).map(l => l.trim()).join(' | '));
  await type('docker compose ps -a');
  const exited = await until(/Exited/);
  notes.push('9 ps before: ' + exited.split('\n').filter(l => /memo-1/.test(l)).map(l => l.trim()).join(' | '));
  await shot('9-exited');
  // A real keyboard edit in the editor: delete " &" at the end of the command.
  const line = page.locator('.compose-source .cm-line', {hasText: 'sleep 3600 &'});
  await line.click();
  await page.keyboard.press('End');
  await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('Backspace');
  await page.keyboard.press('Backspace');
  await page.waitForTimeout(400);
  const saved = practiceFile(dataDir, 'compose.yaml', 'echo 메모 서버 시작');
  assert.ok(saved && saved.text.includes('sleep 3600"]') && !saved.text.includes('3600 &'), `the editor saved the real file: ${saved?.p}`);
  notes.push(`9 saved file: ${saved.p}`);
  await type('grep sleep compose.yaml');
  assert.match(await until(/sleep 3600"\]/), /sleep 3600"\]/, 'the terminal reads the edited file in its folder');
  await type('docker compose up -d');
  await until(/memo-1\s+Recreated[\s\S]*memo-1\s+Started/);
  await type('docker compose ps -a');
  notes.push('9 ps after: ' + (await until(/Up /)).split('\n').filter(l => /memo-1/.test(l)).map(l => l.trim()).join(' | '));
  await type('docker compose logs memo');
  await until(/메모 서버 시작/);
  await shot('9-up-and-logs');
  assert.equal(await submit(), 'passed');
  await shot('9-passed');
  await page.locator('.task-passed-dialog button').last().click();
  // Changing the file after the commands: the grader no longer counts them.
  const fixedLine = page.locator('.compose-source .cm-line', {hasText: 'sleep 3600'});
  await fixedLine.click();
  await page.keyboard.press('End');
  await page.keyboard.type(' ');
  await page.waitForTimeout(400);
  assert.equal(await submit(), 'incorrect', 'commands typed before the file changed do not count');
  notes.push('9 after edit: ' + (await page.locator('.result-pane').innerText()).split('\n').filter(l => /바꾸기 전|지금/.test(l)).slice(0, 3).join(' | '));
  await shot('9-changed-file-incorrect');
  // Focus is on the submit button now: return to the same line and remove the added space.
  await fixedLine.click();
  await page.keyboard.press('End');
  await page.keyboard.press('Backspace');
  await page.waitForTimeout(400);
  assert.equal(await submit(), 'passed', 'the same file content as when the commands ran counts again');
  await page.locator('.task-passed-dialog button').last().click();
  progress('9 passed', {notes: notes.filter(n => n.startsWith('9'))});
  }

  // 10. narration plays in its own editor and terminal; the learner's files and terminal stay.
  if (steps.has('10')) {
  await goto(10);
  const learnerBefore = await screen();
  const fileBefore = practiceFile(dataDir, 'compose.yaml', '/memo/list.txt')?.text;
  await page.evaluate(() => window.molipAgent?.setVoice(false));
  await button('해설 재생').click();
  await page.waitForFunction(() => window.molipAgent?.running, null, {timeout: 20000});
  const demoText = () => page.evaluate(() => {
    const o = document.querySelector('#git-demo-terminal')?.dataset.terminalSession;
    return o ? window.mq3GitDemoTerminal?.text(o) ?? '' : '';
  });
  let demo = '';
  for (const deadline = Date.now() + 600000; Date.now() < deadline;) {
    demo = await demoText().catch(() => demo) || demo;
    if (/No such file or directory/.test(demo)) break;
    await page.waitForTimeout(200);
  }
  assert.match(demo, /No such file or directory/, 'the narration shows the real missing file after recreate');
  assert.equal(await page.locator('#git-demo-terminal').getAttribute('aria-label'), '해설용 별도 Docker 터미널');
  await shot('10-narration-before-fix');
  for (const deadline = Date.now() + 600000; Date.now() < deadline;) {
    demo = await demoText().catch(() => demo) || demo;
    if (/volumes:[\s\S]*memo:\/memo/.test(await page.evaluate(() => window.molipCodeEditors?.getValue() ?? '')) && /cat \/memo\/list\.txt[\s\S]*cat \/memo\/list\.txt\s*\n우유/.test(demo)) break;
    await page.waitForTimeout(300);
  }
  assert.match(demo, /cat \/memo\/list\.txt\s*\n우유/, 'after the narration edit the real memo survives the recreate');
  await shot('10-narration-after-fix');
  notes.push('10 narration: ' + demo.split('\n').filter(l => /\$ docker|우유|No such/.test(l)).map(l => l.trim()).join(' | '));
  await page.waitForFunction(() => !window.molipAgent?.running, null, {timeout: 600000});
  await ready();
  assert.equal((await screen()).trimEnd(), learnerBefore.trimEnd(), 'the narration did not type in the learner terminal');
  assert.equal(practiceFile(dataDir, 'compose.yaml', '/memo/list.txt')?.text, fileBefore, 'the narration did not edit the learner file');
  notes.push('10 learner untouched: terminal text and compose.yaml identical before/after narration');
  progress('10 narration done', {notes: notes.filter(n => n.startsWith('10'))});
  }

  // 13. 관리자 자동 풀이: edits the learner's show.sh and compose.yaml tabs and types the commands.
  if (steps.has('13')) {
  await goto(13);
  assert.deepEqual(await page.locator('[data-editor-tab]').allInnerTexts(), ['compose.yaml', 'show.sh']);
  await page.locator('[data-editor-tab="show.sh"]').click();
  await page.waitForSelector('textarea[data-editor-file="show.sh"]', {state: 'attached'});
  assert.match(await page.evaluate(() => window.molipCodeEditors?.getValue() ?? ''), /\[v1\]/);
  await page.locator('[data-editor-tab="compose.yaml"]').click();
  await notesClear('13 at 1440px');
  await shot('13-two-files');
  const learnerFilesBefore = ['compose.yaml', 'show.sh'].map(n => practiceFile(dataDir, n, '')?.text);
  await page.evaluate(() => { window.molipAgent?.setVoice(false); window.molipVoice?.setRate?.('3'); });
  await page.locator('#auto-run-start').click();
  // Bounded: the stage, learner terminal tail and learner files every 10 s; a stopped run fails now.
  const run = () => page.evaluate(() => {
    const c = document.querySelector('.auto-run-control');
    const step = [...document.querySelectorAll('.study-navigation [data-step-id]')].find(b => b.textContent.includes('문제 13 · '));
    return {state: c?.dataset.state, stage: c?.dataset.stage, reason: c?.dataset.reason, passed: c?.dataset.passed, completed: step?.dataset.completed === 'true'};
  });
  let status = {}, lastLog = 0;
  const sawStages = [];
  for (const deadline = Date.now() + Number(process.env.MQ3_AUTORUN_SECONDS || 900) * 1000;;) {
    status = await run();
    if (status.stage && sawStages.at(-1) !== status.stage) { sawStages.push(status.stage); progress('13 auto-run stage', status); }
    if (status.completed) break;
    if (status.state && !['running', 'paused'].includes(status.state)) break;
    if (Date.now() - lastLog > 10000) {
      lastLog = Date.now();
      progress('13 auto-run poll', {...status, learner_tail: (await screen().catch(() => '')).slice(-400),
        compose_v2: !!practiceFile(dataDir, 'compose.yaml', 'memos:/data'), show_v2: !!practiceFile(dataDir, 'show.sh', '[v2]')});
    }
    if (Date.now() > deadline) { await shot('13-auto-run-timeout'); throw Error(`auto-run did not finish in time: ${JSON.stringify(status)} stages=${sawStages.join(' > ')}`); }
    await page.waitForTimeout(500);
  }
  notes.push('13 auto-run stages: ' + sawStages.join(' > '));
  if (!status.completed) { await shot('13-auto-run-stopped'); throw Error(`auto-run stopped: ${JSON.stringify(status)} stages=${sawStages.join(' > ')}`); }
  const typed = await screen();
  assert.match(typed, /\[v2\] \(없음\)[\s\S]*\[v2\] 우유/, 'auto-run typed the commands in the learner terminal and the memo survived');
  const compose = practiceFile(dataDir, 'compose.yaml', 'memos:/data');
  const show = practiceFile(dataDir, 'show.sh', '[v2]');
  assert.ok(compose && show, 'auto-run edited the learner files in the terminal folder');
  await shot('13-auto-run-passed');
  notes.push('13 auto-run: ' + typed.split('\n').filter(l => /\$ docker|\[v/.test(l)).map(l => l.trim()).join(' | '));
  notes.push(`13 learner files changed by auto-run: compose.yaml ${learnerFilesBefore[0] !== compose.text}, show.sh ${learnerFilesBefore[1] !== show.text} (${compose.p}, ${show.p})`);
  assert.ok(learnerFilesBefore[0] !== compose.text && learnerFilesBefore[1] !== show.text, 'auto-run changed both learner files');
  progress('13 auto-run passed', {notes: notes.filter(n => n.startsWith('13'))});
  await page.keyboard.press('Escape');
  await page.waitForSelector('.auto-run-control[data-state="stopped"]', {timeout: 60000}).catch(() => {});
  await page.locator('.auto-run-dismiss').click().catch(() => {});
  await page.emulateMedia({colorScheme: 'dark'});
  await page.setViewportSize({width: 760, height: 800});
  await notesClear('13 at 760px');
  await shot('13-narrow-dark');
  await page.setViewportSize({width: 1440, height: 900});
  await page.emulateMedia({colorScheme: 'light'});
  }

  // Leaving the lesson removes exactly the projects this run created (learner and narration).
  if (steps.has('leave')) {
  const mine = projectsSince(started - 1000);
  const before = owned(mine);
  progress('leave before', {projects: mine, resources: before});
  assert.ok(before.length > 0, `this run left Docker resources to clean up: ${mine.join(', ')}`);
  await page.locator('.course-back').click();
  await page.waitForSelector('.lesson-card', {timeout: 60000});
  let after = before;
  for (const deadline = Date.now() + 120000; Date.now() < deadline && after.length; await page.waitForTimeout(1000)) after = owned(mine);
  progress('leave after', {remaining: after});
  assert.deepEqual(after, [], 'leaving the lesson removed every resource of this run');
  notes.push(`leave: ${mine.length} owned projects, ${before.length} resources before leaving, ${after.length} after`);
  }
  progress('done', {notes});
  return notes;
}
