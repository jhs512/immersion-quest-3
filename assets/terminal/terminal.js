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
    term.textarea?.setAttribute('aria-label', host.dataset.vim === 'true' ? 'Vim 편집기 입력' : host.dataset.shell === 'true' ? 'Bash 실습 터미널 입력' : inputLabel);
    let nativeKorean = false, nativeEditable = 0, composing = false, replacement;
    const events = new AbortController();
    const listen = (type, callback) => host.addEventListener(type, callback, {capture: true, signal: events.signal});
    listen('compositionstart', () => { composing = true; nativeKorean = false; nativeEditable = 0; });
    listen('compositionend', () => { composing = false; });
    const hangul = /[\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]/u;

    // Native macOS Korean can use insertText/insertReplacementText without any
    // composition events. Mirror its tail edits with Readline's Unicode erase,
    // rather than leaving only the initial jamo in the PTY.
    listen('beforeinput', event => {
      replacement = undefined;
      if (event.target !== term.textarea || composing) return;
      if ((event.inputType === 'insertText' && hangul.test(event.data || '')) ||
          (event.inputType === 'insertReplacementText' && nativeKorean)) {
        // The helper textarea can still contain an ASCII key already sent to
        // the PTY. An initial insertText may replace that helper value; it must
        // not backspace the user's committed quote (or any preceding command).
        replacement = {value: term.textarea.value.normalize('NFC'),
          erasable: event.inputType === 'insertReplacementText' ? nativeEditable : 0};
        nativeKorean = true;
      } else if (event.inputType !== 'insertReplacementText') {
        nativeKorean = false; nativeEditable = 0;
      }
    });
    listen('input', event => {
      if (event.target !== term.textarea || replacement === undefined) return;
      const before = Array.from(replacement.value), after = Array.from(term.textarea.value.normalize('NFC'));
      const erasable = replacement.erasable;
      replacement = undefined;
      let common = 0;
      while (common < before.length && common < after.length && before[common] === after[common]) common++;
      event.stopImmediatePropagation();
      const removed = Math.min(before.length - common, erasable);
      const inserted = after.slice(common);
      nativeEditable = Math.max(0, nativeEditable - removed) + inserted.length;
      const edit = '\x7f'.repeat(removed) + inserted.join('');
      if (edit) term.input(edit, true);
    });
    // Preserve standard composition even when keyCode is not 229. For the native
    // replacement path, avoid xterm's delayed textarea-diff fallback sending twice.
    term.attachCustomKeyEventHandler(event => !event.isComposing && !(nativeKorean && event.keyCode === 229));
    // macOS IMEs may commit conjoining Hangul jamo; send complete syllables to Readline.
    const data = term.onData(value => {
      // Keyboard, IME and clipboard input all use ordinary token separators.
      const input = value.replaceAll('\u00a0',' ');
      send({kind: 'input', data: input.normalize('NFC')});
    });
    const resize = term.onResize(size => send({kind: 'resize', rows: size.rows, cols: size.cols}));
    const observer = new ResizeObserver(() => fit.fit()); observer.observe(host);
    session = {owner, term, fit, data, resize, observer, done, decoder: new TextDecoder(), events};
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
  updateVimState(progress,owner) {if(session && (owner===undefined||session.owner===owner))session.vimProgress=progress;},
  vimState(owner) {return session && (owner===undefined||session.owner===owner) ? session.vimProgress : null;},
  text(owner) {if(!session || (owner!==undefined && session.owner!==owner))return '';const buffer=session.term.buffer.active;return Array.from({length:buffer.length},(_,index)=>buffer.getLine(index)?.translateToString(true)||'').join('\n');},
  async typeKeys(keys, owner) {
    const current=session;if(!current || (owner!==undefined && current.owner!==owner))return false;
    for(const character of keys.normalize('NFC')){if(session!==current)return false;current.term.input(character);await new Promise(resolve=>setTimeout(resolve,40));}
    return session===current;
  },
  async typeCommand(command, owner) {
    const current=session;if(!current || (owner!==undefined && current.owner!==owner))return false;
    for(const character of command.normalize('NFC')){if(session!==current)return false;current.term.input(character);await new Promise(resolve=>setTimeout(resolve,25));}
    if(session===current){current.term.input('\r');return true;}return false;
  },
  dispose(owner) {
    if (!session || (owner!==undefined && session.owner!==owner)) return;
    const old = session; session = null;
    old.events.abort(); old.observer.disconnect(); old.data.dispose(); old.resize.dispose(); old.term.dispose(); old.done();
  },
};

}
window.mq3SetupTerminal=terminalBridge('gh-setup-terminal','설정 터미널 입력');
window.mq3GitTerminal=terminalBridge('git-student-terminal','Git 실습 터미널 입력');
window.mq3GitDemoTerminal=terminalBridge('git-demo-terminal','Git 해설 터미널 입력');
