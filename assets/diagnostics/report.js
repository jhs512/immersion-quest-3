// JavaScript for Automation: an OS-native dialog, not the player's WebView.
ObjC.import('Foundation');
ObjC.import('AppKit');
function run(args) {
  const app = Application.currentApplication();
  app.includeStandardAdditions = true;
  $.NSApplication.sharedApplication.activateIgnoringOtherApps(true);
  const read = path => ObjC.unwrap($.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null));
  const draft = JSON.parse(read(args[0]));
  const directory = args[0].slice(0, args[0].lastIndexOf('/'));
  const screenshot = directory + '/screen.png';
  const statusPath = directory + '/capture-status.json';
  let exists = $.NSFileManager.defaultManager.fileExistsAtPath(screenshot);
  for (let i=0; !exists && i<40; i++) {
    if ($.NSFileManager.defaultManager.fileExistsAtPath(statusPath)) break;
    $.NSThread.sleepForTimeInterval(0.1);
    exists=$.NSFileManager.defaultManager.fileExistsAtPath(screenshot);
  }
  let failure = {};
  if (!exists && $.NSFileManager.defaultManager.fileExistsAtPath(statusPath)) {
    try { failure = JSON.parse(read(statusPath)); } catch (_) {}
  }
  let include = draft.include_screen && exists;
  let description = draft.description || '';
  const location = [draft.location.lesson_title, draft.location.task_title].filter(Boolean).join(' · ');
  const captureMessage = exists ? '화면 캡처는 확인 후 포함하거나 제외할 수 있어요.' : failure.reason === 'permission'
    ? '화면 기록 권한이 없어 캡처하지 못했어요. 시스템 설정에서 MQ의 화면 기록을 허용한 뒤 MQ를 다시 열어주세요. 기록과 설명만 보낼 수도 있어요.'
    : failure.reason === 'timeout' ? '화면 캡처 응답이 늦어 중단했어요. 기록과 설명은 보낼 수 있어요.'
    : 'MQ 창을 캡처하지 못했어요. 기록과 설명은 보낼 수 있어요.';
  const message = '보낼 저장소: ' + draft.repository + (location ? '\n위치: ' + location : '') + '\n' + captureMessage + '\n\n최근 한 시간의 상세 기록과 이동 이력을 보내요. 진단 파일은 링크로 접근할 수 있는 GitHub Gist에 저장해요. 아래에 추가 설명을 적어주세요.';
  while (true) {
    const answer = app.displayDialog(message, {withTitle: draft.kind === 'content' ? 'MQ · 문제 신고' : 'MQ · 앱 오류 신고',
      defaultAnswer: description, buttons: include ? ['취소', '캡처 확인', '보내기'] : failure.reason === 'permission' ? ['취소', '권한 설정', '보내기'] : ['취소', '보내기'], defaultButton: '보내기', cancelButton: '취소'});
    description = answer.textReturned;
    if (answer.buttonReturned === '권한 설정') {
      app.openLocation('x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture');
      continue;
    }
    if (answer.buttonReturned === '캡처 확인') {
      app.openLocation('file://' + encodeURI(screenshot));
      const choice = app.displayDialog('화면 캡처를 포함할까요?', {buttons:['제외','포함'], defaultButton:'포함'});
      include = choice.buttonReturned === '포함';
      continue;
    }
    const data = $(JSON.stringify({description, include_screen: include}));
    data.writeToFileAtomicallyEncodingError(directory + '/response.json', true, $.NSUTF8StringEncoding, null);
    return 'sent';
  }
}
