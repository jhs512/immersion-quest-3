const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

test('macOS report waits for a capture that becomes ready after one second', () => {
  let elapsed = 0;
  let response;
  const draft = { kind: 'bug', repository: 'fixture/player', location: {}, include_screen: true };
  const objc = value => ({ writeToFileAtomicallyEncodingError: () => { response = JSON.parse(value); } });
  objc.import = () => {};
  objc.unwrap = value => value;
  const app = { displayDialog: () => ({ textReturned: 'fixture', buttonReturned: '보내기' }) };
  const context = {
    ObjC: objc,
    Application: { currentApplication: () => app },
    $: Object.assign(objc, {
      NSUTF8StringEncoding: 4,
      NSApplication: { sharedApplication: { activateIgnoringOtherApps() {} } },
      NSString: { stringWithContentsOfFileEncodingError: () => JSON.stringify(draft) },
      NSFileManager: { defaultManager: { fileExistsAtPath: path => path.endsWith('screen.png') && elapsed >= 1.5 } },
      NSThread: { sleepForTimeInterval: seconds => { elapsed += seconds; } },
    }),
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('assets/diagnostics/report.js', 'utf8'), context);
  context.run(['/fixture/draft.json']);
  assert.equal(response.include_screen, true);
});

test('macOS report explains missing permission without empty lesson labels', () => {
  let message;
  let options;
  const draft = { kind: 'bug', repository: 'fixture/player', location: {}, include_screen: true };
  const objc = value => ({ writeToFileAtomicallyEncodingError() {} });
  objc.import = () => {};
  objc.unwrap = value => value;
  const context = {
    ObjC: objc,
    Application: { currentApplication: () => ({ displayDialog: (text, value) => {
      message = text;
      options = value;
      return { textReturned: '', buttonReturned: '보내기' };
    } }) },
    $: Object.assign(objc, {
      NSUTF8StringEncoding: 4,
      NSApplication: { sharedApplication: { activateIgnoringOtherApps() {} } },
      NSString: { stringWithContentsOfFileEncodingError: path => JSON.stringify(path.endsWith('capture-status.json') ? { reason: 'permission' } : draft) },
      NSFileManager: { defaultManager: { fileExistsAtPath: path => path.endsWith('capture-status.json') } },
      NSThread: { sleepForTimeInterval() { throw Error('known failure must not wait'); } },
    }),
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('assets/diagnostics/report.js', 'utf8'), context);
  context.run(['/fixture/draft.json']);
  assert.match(message, /화면 기록 권한/);
  assert.equal(options.buttons.includes('권한 설정'), true);
  assert.doesNotMatch(message, /수업:|단계:/);
  assert.equal((message.match(/캡처하지 못했어요/g) || []).length, 1);
});
