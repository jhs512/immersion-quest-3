// JavaScript for Automation: an OS-native dialog, not the player's WebView.
ObjC.import('Foundation');
ObjC.import('AppKit');
function run(args) {
  const app = Application.currentApplication();
  app.includeStandardAdditions = true;
  ObjC.registerSubclass({name: 'MQReportWindowObserver', superclass: 'NSObject', methods: {
    'windowBecameKey:': {types: ['void', ['id']], implementation: function (notification) {
      const panel = notification.object;
      panel.collectionBehavior = $.NSWindowCollectionBehaviorCanJoinAllSpaces | $.NSWindowCollectionBehaviorFullScreenAuxiliary;
      panel.orderFrontRegardless;
    }}
  }});
  const observer = $.MQReportWindowObserver.alloc.init;
  const notifications = $.NSNotificationCenter.defaultCenter;
  notifications.addObserverSelectorNameObject(observer, 'windowBecameKey:', $.NSWindowDidBecomeKeyNotification, null);
  $.NSApplication.sharedApplication.activateIgnoringOtherApps(true);
  const read = path => ObjC.unwrap($.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null));
  const draft = JSON.parse(read(args[0]));
  const directory = args[0].slice(0, args[0].lastIndexOf('/'));
  const screenshot = directory + '/screen.png';
  const statusPath = directory + '/capture-status.json';
  const files = $.NSFileManager.defaultManager;
  // MQ writes screen.png or capture-status.json for every helper it starts, the timeout too.
  // The timeout status has arrived 6 s after the helper started on a CI Mac, so 4 s was too short.
  const wait = () => {
    for (let i=0; !files.fileExistsAtPath(screenshot) && !files.fileExistsAtPath(statusPath) && i<100; i++) $.NSThread.sleepForTimeInterval(0.1);
  };
  // Runs the same capture helper MQ started, for a student who closed a covering window or waited for MQ.
  const retry = () => {
    files.removeItemAtPathError(statusPath, null);
    const task = $.NSTask.launchedTaskWithLaunchPathArguments(args[1], $(['--capture-report', args[2], screenshot]));
    for (let i=0; task.isRunning && i<30; i++) $.NSThread.sleepForTimeInterval(0.1);
    if (task.isRunning) {
      task.terminate;
      $(JSON.stringify({reason: 'timeout'})).writeToFileAtomicallyEncodingError(statusPath, true, $.NSUTF8StringEncoding, null);
    }
  };
  wait();
  let description = draft.description || '';
  let include = null;
  const location = [draft.location.lesson_title, draft.location.task_title].filter(Boolean).join(' · ');
  while (true) {
    const exists = files.fileExistsAtPath(screenshot);
    let failure = {};
    if (!exists && files.fileExistsAtPath(statusPath)) {
      try { failure = JSON.parse(read(statusPath)); } catch (_) {}
    }
    const captureMessage = exists ? '화면 캡처는 확인 후 포함하거나 제외할 수 있어요.'
      : failure.reason === 'timeout' ? 'MQ가 화면 캡처에 제때 답하지 않아 중단했어요. 다시 캡처하거나 기록과 설명만 보낼 수 있어요.'
      : 'MQ 창을 캡처하지 못했어요' + (failure.detail ? ' (' + failure.detail + ')' : '') + '. 다시 캡처하거나 기록과 설명만 보낼 수 있어요.';
    const message = '보낼 저장소: ' + draft.repository + (location ? '\n위치: ' + location : '') + '\n' + captureMessage + '\n\n최근 한 시간의 상세 기록과 이동 이력을 보내요. 진단 파일은 링크로 접근할 수 있는 GitHub Gist에 저장해요. 아래에 추가 설명을 적어주세요.';
    const answer = app.displayDialog(message, {withTitle: draft.kind === 'content' ? 'MQ · 문제 신고' : 'MQ · 앱 오류 신고',
      defaultAnswer: description, buttons: exists ? ['취소', '캡처 확인', '보내기'] : ['취소', '다시 캡처', '보내기'], defaultButton: '보내기', cancelButton: '취소'});
    description = answer.textReturned;
    if (answer.buttonReturned === '다시 캡처') {
      retry();
      continue;
    }
    if (answer.buttonReturned === '캡처 확인') {
      app.openLocation('file://' + encodeURI(screenshot));
      const choice = app.displayDialog('화면 캡처를 포함할까요?', {buttons:['제외','포함'], defaultButton:'포함'});
      include = choice.buttonReturned === '포함';
      continue;
    }
    const data = $(JSON.stringify({description, include_screen: exists && (include === null ? draft.include_screen : include)}));
    data.writeToFileAtomicallyEncodingError(directory + '/response.json', true, $.NSUTF8StringEncoding, null);
    notifications.removeObserver(observer);
    return 'sent';
  }
}
