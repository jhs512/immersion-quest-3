const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

function report({ failure, readyAfter, answers = [{ textReturned: '', buttonReturned: '보내기' }], retryHangs = false } = {}) {
  let elapsed = 0;
  let retries = 0;
  let terminated = false;
  const messages = [];
  const draft = { kind: 'bug', repository: 'fixture/player', location: {}, include_screen: true };
  const files = new Map([['/fixture/draft.json', JSON.stringify(draft)]]);
  if (failure) files.set('/fixture/capture-status.json', JSON.stringify(failure));
  const objc = value => ({ value, writeToFileAtomicallyEncodingError: path => files.set(path, value) });
  objc.import = () => {};
  objc.unwrap = value => value;
  const app = { displayDialog: (text, options) => {
    messages.push({ text, options });
    const answer = answers.shift();
    if (!answer) throw Error('unexpected dialog');
    if (answer instanceof Error) throw answer;
    return answer;
  } };
  const context = {
    ObjC: objc,
    Application: { currentApplication: () => app },
    $: Object.assign(objc, {
      NSUTF8StringEncoding: 4,
      NSApplication: { sharedApplication: { activateIgnoringOtherApps() {} } },
      NSString: { stringWithContentsOfFileEncodingError: path => files.get(path) },
      NSFileManager: { defaultManager: {
        fileExistsAtPath: path => files.has(path) || (path.endsWith('screen.png') && readyAfter !== undefined && elapsed >= readyAfter),
        removeItemAtPathError: path => files.delete(path),
      } },
      NSThread: { sleepForTimeInterval: seconds => { elapsed += seconds; } },
      NSTask: { launchedTaskWithLaunchPathArguments: (executable, args) => {
        assert.equal(executable, '/fixture/MQ');
        assert.deepEqual(Array.from(args.value), ['--capture-report', '123', '/fixture/screen.png']);
        assert.equal(files.has('/fixture/capture-status.json'), false);
        retries++;
        if (!retryHangs) files.set('/fixture/screen.png', 'captured');
        return { isRunning: retryHangs, get terminate() { terminated = true; } };
      } },
    }),
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('assets/diagnostics/report.js', 'utf8'), context);
  return { run: () => context.run(['/fixture/draft.json', '/fixture/MQ', '123']), files, messages,
    result: () => ({ elapsed, retries, terminated, response: JSON.parse(files.get('/fixture/response.json') || 'null') }) };
}

test('macOS report includes a capture that becomes ready after one second', () => {
  const dialog = report({ readyAfter: 1.5 });
  dialog.run();
  assert.equal(dialog.result().response.include_screen, true);
});

test('macOS report explains a known capture failure and offers retry without permission settings', () => {
  const dialog = report({ failure: { reason: 'failed', detail: 'MQ window unavailable' } });
  dialog.run();
  assert.equal(dialog.result().elapsed, 0);
  assert.equal(dialog.result().response.include_screen, false);
  assert.match(dialog.messages[0].text, /MQ window unavailable/);
  assert.deepEqual(Array.from(dialog.messages[0].options.buttons), ['취소', '다시 캡처', '보내기']);
  assert.doesNotMatch(dialog.messages[0].text, /권한|수업:|단계:/);
});

test('macOS report distinguishes a capture timeout from an unavailable window', () => {
  const dialog = report({ failure: { reason: 'timeout' } });
  dialog.run();
  assert.match(dialog.messages[0].text, /제때 답하지 않아/);
  assert.equal(dialog.result().elapsed, 0);
  assert.equal(dialog.result().response.include_screen, false);
});

test('macOS retry captures the window and preserves the written description', () => {
  const dialog = report({ failure: { reason: 'failed' }, answers: [
    { textReturned: 'my report', buttonReturned: '다시 캡처' },
    { textReturned: 'my report', buttonReturned: '보내기' },
  ] });
  dialog.run();
  assert.equal(dialog.result().retries, 1);
  assert.match(dialog.messages[1].text, /화면 캡처는 확인 후/);
  assert.equal(dialog.messages[1].options.defaultAnswer, 'my report');
  assert.deepEqual(dialog.result().response, { description: 'my report', include_screen: true });
});

test('macOS retry timeout still lets the report send without a screen', () => {
  const dialog = report({ failure: { reason: 'failed' }, retryHangs: true, answers: [
    { textReturned: '', buttonReturned: '다시 캡처' },
    { textReturned: 'still hung', buttonReturned: '보내기' },
  ] });
  dialog.run();
  assert.equal(dialog.result().terminated, true);
  assert.match(dialog.messages[1].text, /제때 답하지 않아/);
  assert.equal(dialog.result().response.include_screen, false);
});

test('macOS cancel writes no response or capture request', () => {
  const dialog = report({ failure: { reason: 'failed' }, answers: [Error('User canceled. (-128)')] });
  assert.throws(dialog.run, /User canceled/);
  assert.equal(dialog.result().response, null);
  assert.equal(dialog.result().retries, 0);
});
