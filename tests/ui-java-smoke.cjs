// npm.cmd install --prefix target/ui-tests playwright-core --no-audit --no-fund
// node tests/ui-java-smoke.cjs (after cargo build --locked --bin molip-quest)
const { chromium } = require('../target/ui-tests/node_modules/playwright-core');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const course = JSON.parse(fs.readFileSync(path.join(root, 'courses/java-basics.json'), 'utf8'));
const data = fs.mkdtempSync(path.join(root, 'target', 'java-ui-data-'));
const port = Number(process.env.MOLIP_UI_TEST_PORT || 9245);
const app = spawn(path.join(root, 'target', 'debug', 'molip-quest.exe'), [], {
  cwd: root, windowsHide: true,
  env: { ...process.env, MOLIP_DATA_DIR: data, WEBVIEW2_USER_DATA_FOLDER: path.join(data, 'webview'),
    WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS: `--remote-debugging-port=${port}` },
  stdio: 'ignore',
});
let browser;
async function edit(page, code) {
  await page.locator('.cm-content').click();
  await page.keyboard.press('Control+A');
  await page.keyboard.insertText(code);
}
async function waitMessage(page, text) {
  await page.waitForFunction(text => document.querySelector('.execution-status')?.textContent.includes(text), text);
}
async function screenshot(page, name) {
  await page.screenshot({ path: path.join(root, 'target', name), fullPage: false });
}
(async () => {
  for (let i = 0; i < 40; i++) {
    try { browser = await chromium.connectOverCDP(`http://127.0.0.1:${port}`); break; }
    catch { await new Promise(resolve => setTimeout(resolve, 250)); }
  }
  assert(browser, 'Local WebView did not open');
  const page = browser.contexts()[0].pages()[0];
  await page.getByRole('button', { name: '학습 시작 · 이어하기', exact: true }).waitFor();
  assert.match(await page.locator('body').innerText(), /3챕터 · 12단원/);
  await screenshot(page, 'java-home.png');
  await page.getByRole('button', { name: '환경 진단 · JDK 25', exact: true }).click();
  await page.locator('.doctor-check.ready').waitFor();
  assert.match(await page.locator('.doctor-check.ready').innerText(), /Main.java 컴파일·실행 확인 완료/);
  await page.getByRole('button', { name: '닫기', exact: true }).click();
  await page.getByRole('button', { name: '기존 샘플 · 금융 데이터 분석', exact: true }).click();
  await page.getByRole('heading', { name: /KPC · 머신러닝/ }).first().waitFor();
  assert.match(await page.locator('body').innerText(), /7챕터 · 20단원/);
  await page.getByRole('button', { name: '자바 기초 · JDK 25', exact: true }).click();
  await page.getByRole('button', { name: '학습 시작 · 이어하기', exact: true }).click();
  const check = page.getByRole('textbox', { name: '출력 후 줄을 바꾸는 메서드 이름은 무엇인가요?', exact: true });
  await check.fill('print');
  await page.getByRole('button', { name: '제출', exact: true }).click();
  await page.getByText('0 / 1 정답 · 오답 문항만 다시 풀어보세요.', { exact: true }).waitFor();
  await check.fill('println');
  await page.getByRole('button', { name: '제출', exact: true }).click();
  await page.getByRole('button', { name: '다음 미션 ›', exact: true }).click();
  await page.getByRole('textbox', { name: 'Java 코드 편집기', exact: true }).waitFor();
  assert.equal(await page.locator('[data-code-editor]').getAttribute('data-code-editor'), 'java');
  await edit(page, 'class Main { public static void main(String[] args) { System.out.println(0); } }');
  await page.getByRole('button', { name: '제출', exact: true }).click();
  await waitMessage(page, '검사를 통과하지 못했습니다');
  // Exercise the real WebView patch handler for every authored Java explanation.
  for (const activity of course.chapters.flatMap(c => c.units).flatMap(u => u.activities)) {
    if (!activity.narration.some(a => a.action === 'patch_code')) continue;
    const actions = activity.narration.filter(a => ['set_code', 'patch_code'].includes(a.action))
      .map(({say, ...a}) => a);
    await page.evaluate(async actions => {
      window.molipAgent.setVoice(false);
      await window.molipAgent.run(actions);
    }, actions);
    assert.equal(await page.evaluate(() => window.molipCodeEditors.getValue()), activity.problem.solution);
  }
  await page.getByText('정답과 풀이 보기', { exact: true }).click();
  assert.match(await page.locator('.problem-pane').innerText(), /System.out.println/);
  await edit(page, course.chapters[0].units[0].activities[1].problem.solution);
  await page.getByRole('button', { name: '코드 실행', exact: true }).click();
  await waitMessage(page, '실행 완료');
  assert.match(await page.locator('.result-pane').innerText(), /안녕\nJDK 25/);
  await page.getByRole('button', { name: '제출', exact: true }).click();
  await page.getByRole('button', { name: '다음 미션 ›', exact: true }).waitFor();
  await screenshot(page, 'java-code-passed.png');
  await page.getByRole('button', { name: '다음 미션 ›', exact: true }).click();
  const quiz = page.locator('.quiz-question').first();
  await quiz.getByRole('radio').first().check();
  const recall = course.chapters[0].units[0].activities.at(-1).questions[1];
  await page.getByRole('textbox', { name: recall.prompt, exact: true }).fill(recall.accepted[0]);
  await page.getByRole('button', { name: '제출', exact: true }).click();
  await page.getByRole('button', { name: '다음 미션 ›', exact: true }).waitFor();
  await page.getByRole('button', { name: '여기 머물기', exact: true }).click();
  await page.getByRole('button', { name: '여기 머물기', exact: true }).waitFor({ state: 'hidden' });
  await page.getByText('완료 1 / 12 단원', { exact: true }).waitFor();
  assert.match(await page.locator('body').innerText(), /완료 1 \/ 12 단원/);
  await screenshot(page, 'java-unit-complete.png');
  console.log('UI PASS: default Java path; JDK25 diagnosis; sample switching; concept retry; Java editor; every progressive narration patch; wrong answer; run; submit; quiz; unit completion.');
})().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  if (browser) await browser.close();
  app.kill();
});
