const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

function report({ failure, failureAfter, readyAfter, answers = [{ textReturned: '', buttonReturned: '보내기' }], retryHangs = false } = {}) {
  let elapsed = 0;
  let retries = 0;
  let terminated = false;
  const messages = [];
  const draft = { kind: 'bug', repository: 'fixture/player', location: {}, include_screen: true };
  const files = new Map([['/fixture/draft.json', JSON.stringify(draft)]]);
  if (failure && failureAfter === undefined) files.set('/fixture/capture-status.json', JSON.stringify(failure));
  const objc = value => ({ value, writeToFileAtomicallyEncodingError: path => files.set(path, value) });
  objc.import = () => {};
  objc.unwrap = value => value;
  const answerDialog = (text, options) => {
    messages.push({ text, options });
    const answer = answers.shift();
    if (!answer) throw Error('unexpected dialog');
    if (answer instanceof Error) throw answer;
    return answer;
  };
  const app = { openLocation() {} };
  const application = { activateIgnoringOtherApps() {}, setMainMenu() {}, setActivationPolicy(value) { this.activationPolicy = value; } };
  const alert = () => {
    let title, message, input;
    const labels = [];
    const panel = { setTitle() {}, setHidesOnDeactivate() {}, setInitialFirstResponder() {}, orderOut() {}, setCollectionBehavior(value) { this.collectionBehavior = value; }, windowNumber: 1 };
    return { setMessageText(value) { title = value; }, setInformativeText(value) { message = value; },
      addButtonWithTitle(label) { labels.push(label); return { setKeyEquivalent() {} }; },
      setAccessoryView(value) { input = value; }, window: panel,
      get runModal() {
        const answer = answerDialog(message, { withTitle: title, buttons: labels.slice().reverse(), defaultAnswer: input?.stringValue });
        if (input) input.setStringValue(answer.textReturned || '');
        return 1000 + labels.indexOf(answer.buttonReturned);
      },
    };
  };
  const context = {
    ObjC: objc,
    Application: { currentApplication: () => app },
    $: Object.assign(objc, {
      NSUTF8StringEncoding: 4,
      NSApplication: { sharedApplication: application },
      NSMenu: { alloc: { initWithTitle: () => ({ addItem() {} }) } },
      NSMenuItem: { alloc: { initWithTitleActionKeyEquivalent: () => ({ setSubmenu() {}, setKeyEquivalentModifierMask() {} }) } },
      NSEventModifierFlagCommand: 1 << 20,
      NSApplicationActivationPolicyAccessory: 1,
      NSWindowCollectionBehaviorCanJoinAllSpaces: 1,
      NSWindowCollectionBehaviorFullScreenAuxiliary: 256,
      NSAlertFirstButtonReturn: 1000,
      NSAlert: { alloc: { get init() { return alert(); } } },
      NSMakeRect: () => ({}),
      NSTextField: { alloc: { initWithFrame() {
        return { stringValue: '', setStringValue(value) { this.stringValue = value; } };
      } } },
      NSString: { stringWithContentsOfFileEncodingError: path => files.get(path) },
      NSFileManager: { defaultManager: {
        fileExistsAtPath: path => files.has(path) || (path.endsWith('screen.png') && readyAfter !== undefined && elapsed >= readyAfter),
        removeItemAtPathError: path => files.delete(path),
      } },
      NSThread: { sleepForTimeInterval: seconds => {
        elapsed += seconds;
        if (failureAfter !== undefined && elapsed >= failureAfter) files.set('/fixture/capture-status.json', JSON.stringify(failure));
      } },
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

test('macOS report waits for the helper timeout that arrives after six seconds', () => {
  const dialog = report({ failure: { reason: 'timeout' }, failureAfter: 6.5 });
  dialog.run();
  assert.match(dialog.messages[0].text, /제때 답하지 않아/);
  assert.ok(dialog.result().elapsed >= 6.5 && dialog.result().elapsed < 7);
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
  const dialog = report({ failure: { reason: 'failed' }, answers: [{ buttonReturned: '취소' }] });
  assert.throws(dialog.run, /User canceled/);
  assert.equal(dialog.result().response, null);
  assert.equal(dialog.result().retries, 0);
});

test('macOS report can exclude a confirmed capture and retain the description', () => {
  const dialog = report({ readyAfter: 0, answers: [
    { textReturned: 'keep my explanation', buttonReturned: '캡처 확인' },
    { buttonReturned: '제외' },
    { textReturned: 'keep my explanation', buttonReturned: '보내기' },
  ] });
  dialog.run();
  assert.equal(dialog.messages[2].options.defaultAnswer, 'keep my explanation');
  assert.deepEqual(dialog.result().response, { description: 'keep my explanation', include_screen: false });
});
