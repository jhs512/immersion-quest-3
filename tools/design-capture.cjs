// Design review captures from the real debug player in its isolated validation mode.
// It starts its own app process with a private temp data/WebView folder and a DevTools port the OS
// picks (port 0, loopback), runs one scenario, and stops only the process it started.
//   node tools/design-capture.cjs <scenario.cjs> <output-dir>
// The validation transport never calls gh or GitHub; no real account or progress is touched.
const {chromium} = require('../target/ui-tests/node_modules/playwright-core');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawn, execFileSync} = require('node:child_process');

const root = path.resolve(__dirname, '..');
const [scenarioPath, outArg] = process.argv.slice(2);
if (!scenarioPath || !outArg) { console.error('usage: design-capture.cjs <scenario.cjs> <output-dir>'); process.exit(2); }
const output = path.resolve(outArg);
fs.mkdirSync(output, {recursive: true});
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'mq3-design-capture-'));
const profile = path.join(scratch, 'webview');
// The validation transport keeps its remote fixture here; the owner marker proves this run created it.
const dataDir = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'mq3-player-pilot-installed-')));
const owner = require('node:crypto').randomBytes(16).toString('hex');
fs.writeFileSync(path.join(dataDir, '.mq3-pilot-owner'), owner);
const app = spawn(path.join(root, 'target', 'debug', 'molip-quest.exe'), [], {
  cwd: root, windowsHide: false, stdio: 'ignore',
  env: {...process.env, MOLIP_PILOT: '1', MOLIP_PILOT_DIRECTORY: '\\\\?\\' + dataDir, MOLIP_PILOT_OWNER: owner,
    WEBVIEW2_USER_DATA_FOLDER: profile,
    WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS: '--remote-debugging-port=0 --remote-debugging-address=127.0.0.1'},
});
const stop = () => {
  try { execFileSync('taskkill', ['/PID', String(app.pid), '/T', '/F'], {stdio: 'ignore'}); } catch {}
};
process.on('exit', stop);

async function endpoint() {
  const file = path.join(profile, 'EBWebView', 'DevToolsActivePort');
  for (let i = 0; i < 240; i++) {
    for (const candidate of [file, path.join(profile, 'DevToolsActivePort')]) {
      if (fs.existsSync(candidate)) {
        const port = Number(fs.readFileSync(candidate, 'utf8').split(/\r?\n/)[0]);
        if (port > 0) return `http://127.0.0.1:${port}`;
      }
    }
    await new Promise(r => setTimeout(r, 250));
  }
  throw Error('WebView DevTools port did not appear');
}

(async () => {
  const browser = await chromium.connectOverCDP(await endpoint());
  const page = browser.contexts()[0].pages()[0];
  page.setDefaultTimeout(20000);
  const shots = [];
  // PNG for full inspection plus a small JPEG preview for low-bandwidth viewers.
  const shot = async (name, options = {}) => {
    await page.waitForTimeout(options.settle ?? 350);
    const png = path.join(output, `${name}.png`);
    await page.screenshot({path: png, fullPage: false});
    await page.screenshot({path: path.join(output, `${name}.jpg`), type: 'jpeg', quality: 62, fullPage: false});
    shots.push(png);
  };
  const scenario = require(path.resolve(scenarioPath));
  const notes = await scenario({page, shot, output, dataDir});
  fs.writeFileSync(path.join(output, 'capture.json'), JSON.stringify({app_pid: app.pid, shots, notes}, null, 2));
  await browser.close().catch(() => {});
  stop();
  console.log(`captured ${shots.length} screens into ${output} (app pid ${app.pid} stopped)`);
})().catch(error => { console.error(error); stop(); process.exit(1); });
