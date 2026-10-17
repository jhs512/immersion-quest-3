import {Terminal} from '@xterm/xterm';
import {FitAddon} from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

// The bridge exists only while the local gh setup component is mounted.
let session;
window.mq3SetupTerminal = {
  mount(send, done) {
    this.dispose();
    const host = document.getElementById('gh-setup-terminal');
    if (!host) { done(); return; }
    const term = new Terminal({cursorBlink: true, fontFamily: 'Consolas, monospace', fontSize: 14,
      scrollback: 1500, convertEol: false, allowProposedApi: false,
      theme: {background: '#0c1722', foreground: '#dce9f5', cursor: '#9be0c8', selectionBackground: '#3a536d'}});
    const fit = new FitAddon(); term.loadAddon(fit); term.open(host);
    term.textarea?.setAttribute('aria-label', '설정 터미널 입력');
    const data = term.onData(value => send({kind: 'input', data: value}));
    const resize = term.onResize(size => send({kind: 'resize', rows: size.rows, cols: size.cols}));
    const observer = new ResizeObserver(() => fit.fit()); observer.observe(host);
    session = {term, fit, data, resize, observer, done, decoder: new TextDecoder()};
    fit.fit(); term.focus();
    send({kind: 'resize', rows: term.rows, cols: term.cols});
  },
  write(encoded) {
    if (!session) return;
    const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
    session.term.write(session.decoder.decode(bytes, {stream: true}));
  },
  command(command) {
    if (!session) return;
    session.term.input(command + '\r'); session.term.focus();
  },
  dispose() {
    if (!session) return;
    const old = session; session = null;
    old.observer.disconnect(); old.data.dispose(); old.resize.dispose(); old.term.dispose(); old.done();
  },
};
