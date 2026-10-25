// Pronunciation audit: every command, subcommand, option, file name, extension, path, class name
// and acronym that a voice can say in the published lessons, with its context and the text the
// voice actually receives (assets/speech/pronunciation.js). See docs/speech-pronunciation.md.
//
//   node tools/speech-audit.mjs            print the summary
//   node tools/speech-audit.mjs --write    add new items to docs/speech-pronunciation-review.json as "unreviewed"
//                                          and drop items no longer in a lesson (decisions are kept)
//   node tools/speech-audit.mjs --accept   also re-pin example/spoken of existing items, after reviewing the
//                                          differences assets/speech/pronunciation-review.test.mjs printed
//
// Each item gets a decision by hand: lexicon (a rule or LEXICON entry converts it), as-written (reviewed, the
// voice reads it as written; say why in note) or unresolved (needs a decision; say what in note).
//
// The corpus is the speech-targeted text of the tracked lessons: narration (say.text and every
// action's say) and the lesson prose the 읽어주기 panel reads (titles, goals, questions, options,
// explanations, concept bodies; fenced code is skipped there, as the panel skips <pre>).
// Untracked drafts (courses/redesigned-courses/challenges, *.future.json) are not published and not read.
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import vm from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REVIEW = path.join(root, 'docs/speech-pronunciation-review.json');

export function loadPronunciation() {
  const context = { Intl, console };
  context.globalThis = context;
  vm.runInNewContext(readFileSync(path.join(root, 'assets/speech/pronunciation.js'), 'utf8'), context);
  return context.molipPronunciation;
}

// Published lesson files: the lessons the bundled courses reference, plus the built-in courses.
export function lessonFiles() {
  const dir = path.join(root, 'courses/redesigned');
  const files = readdirSync(dir).filter(name => name.endsWith('.json')).map(name => path.join(dir, name));
  const legacy = ['kpc-finance', 'java-basics', 'getting-started', 'morning-practice'].map(name => path.join(root, 'courses', name + '.json'));
  return [...files, ...legacy.filter(existsSync)];
}
export function referencedLessons() {
  const ids = new Set();
  const dir = path.join(root, 'courses/redesigned-courses');
  for (const name of readdirSync(dir).filter(n => n.endsWith('.json') && !n.includes('.future.'))) {
    for (const lesson of JSON.parse(readFileSync(path.join(dir, name), 'utf8')).lessons || []) ids.add(lesson.id);
  }
  return ids;
}

const PROSE_KEYS = new Set(['title', 'goal', 'question', 'premise', 'description', 'objectives', 'explanation', 'content', 'markdown',
  'body', 'prompt', 'prompt_why', 'hint', 'hints', 'tour', 'ask', 'success_conditions', 'label', 'message']);
// Speech-targeted strings of one lesson file: [kind, text].
export function speechTexts(lesson) {
  const out = [];
  const walk = (value, key, parent) => {
    if (Array.isArray(value)) { for (const item of value) walk(item, key, parent); return; }
    if (value && typeof value === 'object') {
      if (typeof value.action === 'string') {
        const said = value.action === 'say' ? value.text : value.say;
        if (typeof said === 'string' && said.trim()) out.push(['narration', said]);
      }
      // Choice options are read as prose.
      if (typeof value.text === 'string' && value.action === undefined && typeof value.id === 'string') out.push(['reading', value.text]);
      for (const [k, v] of Object.entries(value)) if (k !== 'say' && !(k === 'text' && typeof value.action === 'string')) walk(v, k, value);
      return;
    }
    if (typeof value === 'string' && PROSE_KEYS.has(key) && /[가-힣]/.test(value)) {
      out.push(['reading', value.replace(/```[\s\S]*?```/g, ' ').replace(/~~~[\s\S]*?~~~/g, ' ')]);
    }
  };
  walk(lesson, '', null);
  return out;
}

const SPAN = /``[^\n]+?``|`[^`\n]+`/g;
const URL = /\b(?:https?|ftp|file|ssh):\/\/[^\s'"`<>)]+|\bwww\.[^\s'"`<>)]+/g;
const TOKEN = /(?<![A-Za-z0-9_.\/~$@-])(?:--?[A-Za-z][\w-]*|[~.]?\/?[A-Za-z0-9_][\w.\/~+@-]*[A-Za-z0-9_\/]|[A-Za-z_])/g;
const COMMAND_LEAD = /^(\s*(?:\$\s+)?(?:sudo\s+)?)([a-z][a-z0-9_.-]*)(?=\s|$)/;
const SUBCOMMAND_OWNERS = new Set(['git', 'docker', 'gh', 'npm', 'npx', 'pip', 'conda', 'mvn', 'gradle', 'brew', 'apt', 'winget', 'kubectl', 'docker-compose', 'redis-cli', 'systemctl', 'wsl']);
// Shell programs a lesson may name. A code span starting with one of these, or with a word
// followed by an option, is a command line; anything else in backticks is code or a value.
const SHELL_PROGRAMS = ['echo', 'printf', 'cat', 'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv', 'touch', 'grep', 'sort', 'uniq', 'head',
  'tail', 'wc', 'cut', 'tr', 'find', 'sed', 'awk', 'tee', 'chmod', 'chown', 'ps', 'kill', 'curl', 'wget', 'git', 'gh', 'docker', 'docker-compose',
  'python', 'python3', 'pip', 'pip3', 'conda', 'java', 'javac', 'jar', 'jshell', 'node', 'npm', 'npx', 'gradle', 'gradlew', 'mvn', 'psql', 'mysql',
  'sqlite3', 'redis-cli', 'bash', 'sh', 'zsh', 'ssh', 'scp', 'tar', 'unzip', 'zip', 'date', 'which', 'where', 'env', 'export', 'source', 'sudo',
  'apt', 'brew', 'winget', 'vim', 'vi', 'nano', 'code', 'less', 'more', 'man', 'clear', 'exit', 'history', 'diff', 'jupyter', 'uv', 'wsl', 'nginx',
  'kubectl', 'systemctl', 'open', 'start', 'explorer', 'type', 'dir', 'set', 'gcc', 'make', 'cmake', 'ping', 'nslookup', 'ipconfig', 'ifconfig', 'netstat'];
// Extensions of real files; "df.shape" or "ax.bar" are attribute access, not file names.
const FILE_EXTENSIONS = new Set(['txt', 'csv', 'tsv', 'java', 'class', 'jar', 'py', 'ipynb', 'html', 'htm', 'css', 'js', 'mjs', 'ts', 'tsx', 'jsx', 'json',
  'joblib', 'pkl', 'sql', 'db', 'sqlite', 'xlsx', 'xls', 'md', 'log', 'yml', 'yaml', 'xml', 'sh', 'bat', 'ps1', 'conf', 'env', 'properties', 'gradle',
  'kts', 'kt', 'c', 'h', 'cpp', 'hpp', 'o', 'exe', 'out', 'toml', 'ini', 'lock', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf', 'zip', 'gz', 'tar',
  'mp3', 'mp4', 'bak', 'tmp', 'dat', 'err', 'git', 'gitignore', 'dockerignore', 'vimrc', 'bashrc', 'practice', 'keras', 'h5', 'whl']);

function categories(token, inCode) {
  const result = [];
  const ext = token.match(/(?:^|[\w-])\.([A-Za-z][A-Za-z0-9]{0,11})$/);
  const isFile = ext && FILE_EXTENSIONS.has(ext[1].toLowerCase());
  if (/^--?[A-Za-z]/.test(token)) result.push('option');
  else if (token.includes('/')) result.push('path');
  else if (isFile) result.push('file');
  else if (/^[A-Z][A-Z0-9]+s?$/.test(token) && /[A-Z].*[A-Z]|[A-Z][0-9]/.test(token)) result.push('acronym');
  else if (/^[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+$/.test(token) || /^[A-Z][a-z]+$/.test(token) && inCode) result.push('class');
  if (ext && !/^--?/.test(token)) result.push(isFile ? 'extension' : 'member');
  return result;
}
const tokenFor = (category, token) => (category === 'extension' || category === 'member' ? '.' + token.split('.').pop() : token);

export function audit(p = loadPronunciation()) {
  const commandWords = new Set(p.LEXICON.filter(g => g.scope === 'command').flatMap(g => g.entries.map(e => e[0])));
  const known = new Set([...SHELL_PROGRAMS, ...commandWords]);
  const referenced = referencedLessons();
  const items = new Map(), lessons = [];
  let texts = 0, sentences = 0;
  const add = (category, token, lesson, kind, text) => {
    token = tokenFor(category, token);
    const key = category + ':' + token;
    let item = items.get(key);
    if (!item) items.set(key, item = { key, category, token, count: 0, lessons: new Set(), contexts: [] });
    item.count++; item.lessons.add(lesson);
    if (item.contexts.length < 2 && !item.contexts.some(c => c.source === text)) item.contexts.push({ kind, source: text });
  };
  for (const file of lessonFiles()) {
    const lesson = JSON.parse(readFileSync(file, 'utf8'));
    const name = path.basename(file, '.json');
    const published = file.includes('redesigned') ? referenced.has(lesson.id) : true;
    const said = speechTexts(lesson);
    lessons.push({ name, published, texts: said.length });
    if (!published) continue;
    for (const [kind, raw] of said) {
      texts++;
      for (const sentence of raw.split(/\n+/).filter(s => /\S/.test(s))) {
        sentences++;
        const text = sentence.trim().slice(0, 400);
        const spans = [...text.matchAll(SPAN)].map(m => m[0].replace(/^``\s?|\s?``$|^`|`$/g, ''));
        const prose = text.replace(SPAN, ' ').replace(URL, ' ');
        for (const code of spans) {
          const clean = code.replace(URL, ' ');
          for (const part of clean.split(/\s*(?:\|\||&&|[|;])\s*/)) {
            const lead = part.match(COMMAND_LEAD);
            if (!lead) continue;
            const rest = part.slice(lead[0].length).trim().split(/\s+/).filter(Boolean);
            const command = lead[2];
            if (!(known.has(command) || /^-/.test(rest[0] || '') && !/[_.(]/.test(command))) continue;
            add('command', command, name, kind, text);
            if (SUBCOMMAND_OWNERS.has(command) && rest[0] && /^[a-z][a-z-]*$/.test(rest[0])) add('subcommand', command + ' ' + rest[0], name, kind, text);
            // The class argument of java (java Main, java -cp out Main).
            if (command === 'java') {
              const cls = rest.find((w, i) => /^[A-Z]\w*$/.test(w) && (!/^-/.test(rest[i - 1] || '') || /^-/.test(rest[i - 2] || '') && i >= 2));
              if (cls) add('class', cls, name, kind, text);
            }
          }
          for (const m of clean.matchAll(TOKEN)) for (const c of categories(m[0], true)) add(c, m[0], name, kind, text);
        }
        for (const m of prose.matchAll(TOKEN)) {
          const token = m[0];
          for (const c of categories(token, false)) add(c, token, name, kind, text);
          // A command named in prose: a lexicon command word, or a known program followed by an option or a particle.
          const after = prose.slice(m.index + token.length);
          if (known.has(token) && (commandWords.has(token) || /^\s+--?[a-z]|^[가-힣]/.test(after))) add('command', token, name, kind, text);
          const sub = after.match(/^\s+([a-z][a-z-]*)(?=[\s가-힣.,]|$)/);
          if (SUBCOMMAND_OWNERS.has(token) && sub) add('subcommand', token + ' ' + sub[1], name, kind, text);
          if (token === 'java') { const cls = after.match(/^\s+([A-Z]\w*)(?![\w.])/); if (cls) add('class', cls[1], name, kind, text); }
        }
      }
    }
  }
  const list = [...items.values()].map(item => {
    const context = item.contexts[0].source;
    return { ...item, lessons: [...item.lessons].sort(), contexts: item.contexts.map(c => ({ ...c, spoken: p.pronunciationText(c.source) })),
      spoken: p.pronunciationText(item.category === 'command' || item.category === 'subcommand' ? '`' + item.token + '`' : item.token),
      raw: p.pronunciationText(context).includes(item.token) };
  }).sort((a, b) => a.category.localeCompare(b.category) || b.count - a.count || a.token.localeCompare(b.token));
  return { lessons, texts, sentences, items: list };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = audit();
  const published = result.lessons.filter(l => l.published);
  const byCategory = {};
  for (const item of result.items) (byCategory[item.category] ||= []).push(item);
  console.log(`lesson files ${result.lessons.length}, published ${published.length}, speech texts ${result.texts} (${result.sentences} lines), unique items ${result.items.length}`);
  for (const [category, list] of Object.entries(byCategory)) console.log(`  ${category}: ${list.length} (passed raw to the voice in context: ${list.filter(i => i.raw).length})`);
  const unpublished = result.lessons.filter(l => !l.published).map(l => l.name);
  if (unpublished.length) console.log('  not referenced by a bundled course (skipped):', unpublished.join(', '));
  if (process.argv.includes('--dump')) writeFileSync(process.argv[process.argv.indexOf('--dump') + 1], JSON.stringify(result, null, 1));
  if (process.argv.includes('--write') || process.argv.includes('--accept')) {
    const review = existsSync(REVIEW) ? JSON.parse(readFileSync(REVIEW, 'utf8')) : { items: {} };
    const current = new Set(result.items.map(item => item.key));
    let added = 0, removed = 0, accepted = 0;
    for (const item of result.items) {
      const context = item.contexts[0];
      const entry = review.items[item.key];
      if (!entry) {
        review.items[item.key] = { decision: 'unreviewed', lessons: item.lessons.length, example: context.source, spoken: context.spoken };
        added++;
      } else if (process.argv.includes('--accept') && (entry.example !== context.source || entry.spoken !== context.spoken)) {
        // --accept: after reviewing the differences the test printed, keep the decision and pin the new text.
        Object.assign(entry, { lessons: item.lessons.length, example: context.source, spoken: context.spoken });
        accepted++;
      }
    }
    for (const key of Object.keys(review.items)) if (!current.has(key)) { delete review.items[key]; removed++; }
    review.items = Object.fromEntries(Object.entries(review.items).sort(([a], [b]) => a.localeCompare(b)));
    writeFileSync(REVIEW, JSON.stringify(review, null, 1) + '\n');
    console.log(`review file: ${Object.keys(review.items).length} items, ${added} new (unreviewed), ${removed} removed, ${accepted} re-pinned`);
  }
}
