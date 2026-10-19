import {Terminal} from '@xterm/xterm';
import {FitAddon} from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

// The bridge exists only while the local gh setup component is mounted.
function terminalBridge(hostId,inputLabel) {
let session;
return {
  mount(send, done, owner) {
    this.dispose();
    const host = document.getElementById(hostId);
    if (!host) { done(); return; }
    const term = new Terminal({cursorBlink: true, fontFamily: 'Consolas, monospace', fontSize: 14,
      scrollback: 1500, convertEol: false, allowProposedApi: false,
      theme: {background: '#0c1722', foreground: '#dce9f5', cursor: '#9be0c8', selectionBackground: '#3a536d'}});
    const fit = new FitAddon(); term.loadAddon(fit); term.open(host);
    term.textarea?.setAttribute('aria-label', inputLabel);
    // macOS IMEs may commit conjoining Hangul jamo; send complete syllables to Readline.
    const data = term.onData(value => send({kind: 'input', data: value.normalize('NFC')}));
    const resize = term.onResize(size => send({kind: 'resize', rows: size.rows, cols: size.cols}));
    const observer = new ResizeObserver(() => fit.fit()); observer.observe(host);
    session = {owner, term, fit, data, resize, observer, done, decoder: new TextDecoder()};
    fit.fit(); term.focus();
    send({kind: 'resize', rows: term.rows, cols: term.cols});
  },
  write(encoded, owner) {
    if (!session || (owner!==undefined && session.owner!==owner)) return;
    const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
    session.term.write(session.decoder.decode(bytes, {stream: true}));
  },
  command(command) {
    if (!session) return;
    session.term.input(command + '\r'); session.term.focus();
  },
  text(owner) {if(!session || (owner!==undefined && session.owner!==owner))return '';const buffer=session.term.buffer.active;return Array.from({length:buffer.length},(_,index)=>buffer.getLine(index)?.translateToString(true)||'').join('\n');},
  async typeCommand(command, owner) {
    const current=session;if(!current || (owner!==undefined && current.owner!==owner))return false;
    for(const character of command.normalize('NFC')){if(session!==current)return false;current.term.input(character);await new Promise(resolve=>setTimeout(resolve,25));}
    if(session===current){current.term.input('\r');return true;}return false;
  },
  dispose(owner) {
    if (!session || (owner!==undefined && session.owner!==owner)) return;
    const old = session; session = null;
    old.observer.disconnect(); old.data.dispose(); old.resize.dispose(); old.term.dispose(); old.done();
  },
};

}
window.mq3SetupTerminal=terminalBridge('gh-setup-terminal','설정 터미널 입력');
window.mq3GitTerminal=terminalBridge('git-student-terminal','Git 실습 터미널 입력');
window.mq3GitDemoTerminal=terminalBridge('git-demo-terminal','Git 해설 터미널 입력');
