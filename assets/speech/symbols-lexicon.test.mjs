// Spoken symbols and the pronunciation lexicon. Run: node --test assets/speech/
// These check the speech input text (what is sent to a voice), not how a voice sounds.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const context = { Intl, console };
context.globalThis = context;
vm.runInNewContext(readFileSync(new URL('./pronunciation.js', import.meta.url), 'utf8'), context);
vm.runInNewContext(readFileSync(new URL('./speech.js', import.meta.url), 'utf8'), context);
const { pronunciationText: say, LEXICON } = context.molipPronunciation;
const speech = context.molipSpeech;
const cases = list => { for (const [input, expected] of list) assert.equal(say(input), expected, input); };

test('mkdir and other shell commands are spoken in Korean in code spans and prose', () => {
  cases([
    ['`mkdir notes`: notes 폴더를 만드세요.', '엠케이디아이알 notes: notes 폴더를 만드세요.'],
    ['mkdir 결과를 ls로 봐요.', '엠케이디아이알 결과를 엘에스로 봐요.'],
    ['`mkdir`', '엠케이디아이알'],
    ['`cd ..`: 한 단계 위로', '씨디 점점: 한 단계 위로'],
    ['`pwd`로 위치를 봐요', '피더블유디로 위치를 봐요'],
    ['`rmdir empty`', '알엠디아이알 empty'],
    ['`cp memo.txt memo-copy.txt`', '씨피 memo 점 텍스트 memo-copy 점 텍스트'],
    ['`mv notes-copy archive`', '엠브이 notes-copy archive'],
    ['`rm -rf build`', '알엠 -rf build'],
    ['`chmod +x run.sh`', '체모드 +x run 점 에스에이치'],
    ['`curl -s http://127.0.0.1:18085/`', '컬 -s http://127.0.0.1:18085/'],
    ['`redis-cli -p 16379 PING`으로 확인', '레디스 씨엘아이 -p 16379 PING으로 확인'],
    ['`docker compose up`', '도커 컴포즈 up'],
    ['`docker exec`는 실행 중인 컨테이너', '도커 이그젝은 실행 중인 컨테이너'],
    ['`mkdir a && cd a`', '엠케이디아이알 a 앤드 씨디 a'],
    ['`ls | grep memo`', '엘에스 파이프 그렙 memo'],
  ]);
});

// Reported: "filter" was heard as 필더 (the word reached the voice unconverted; no lexicon entry).
test('filter is read 필터 in prose, Java streams and Python; longer identifiers and URLs stay as written', () => {
  cases([
    ['filter로 걸러요', '필터로 걸러요'],
    ['`.filter(...)`', '점 필터(...)'],
    ['`list.stream().filter(n -> n % 2 == 0)`', '리스트.stream().필터(n 화살표 n 나머지 2 같다 0)'],
    ['Python의 filter(함수, 리스트)', '파이썬의 필터(함수, 리스트)'],
    ['`filter(lambda x: x > 0, nums)`', '필터(람다 x: x 크다 0, nums)'],
    ['map, filter, reduce', '맵, 필터, reduce'],
    ['filtered', 'filtered'], ['filterNotNull', 'filterNotNull'], ['https://example.com/filter', 'https://example.com/filter'],
  ]);
  for (const text of ['filter', '`.filter(...)`']) assert.equal(say(say(text)), say(text), 'converted once: ' + text);
});

test('git subcommands follow git; arguments, options and paths stay as written', () => {
  cases([
    ['`git status`', '깃 스테이터스'],
    ['`git commit -m "첫 기록"`', '깃 커밋 -m 첫 기록'],
    ['`git branch -r`를 실행하세요.', '깃 브랜치 -r를 실행하세요.'],
    ['`git show HEAD:guide.txt`', '깃 쇼 HEAD 콜론 guide 점 텍스트'],
    ['git init으로 저장소를 만들어요', '깃 이닛으로 저장소를 만들어요'],
    ['`git switch feature`', '깃 스위치 feature'],
    ['`git add status`', '깃 애드 status'], // the argument named status is not a subcommand
  ]);
});

test('technical names and abbreviations use the lexicon; longer names win', () => {
  cases([
    ['JDBC로 PostgreSQL에 붙어요', '제이디비씨로 포스트그레스큐엘에 붙어요'],
    ['Spring Boot 앱과 JPA', '스프링 부트 앱과 제이피에이'],
    ['Docker Compose 파일', '도커 컴포즈 파일'],
    ['JDK 25와 JVM', '제이디케이 25와 제이브이엠'],
    ['NOT NULL 제약', 'NOT 널 제약'],
    ['HTTP 요청과 REST API', '에이치티티피 요청과 레스트 에이피아이'],
    ['SQL과 MySQL, Redis', '에스큐엘과 마이에스큐엘, 레디스'],
    ['18080의 NGINX가', '18080의 엔진엑스가'],
    ['PR을 열어요', '피알을 열어요'],
  ]);
});

test('identifiers, paths, URLs, ENV names, options and ordinary words are not rewritten', () => {
  cases([
    ['https://github.com/user/repo.git', 'https://github.com/user/repo.git'],
    ['www.example.com/a?b=c', 'www.example.com/a?b=c'],
    ['/usr/bin/mkdir', '/usr/bin/mkdir'],
    ['mkdir_count와 git_status', 'mkdir_count와 git_status'],
    ['$JAVA_HOME과 SQL_MODE', '$JAVA_HOME과 SQL_MODE'],
    ['`ls -la`', '엘에스 -la'],
    ['`head -1 memo.txt`', '헤드 마이너스 1 memo 점 텍스트'], // as prose reads -1, so a second pass agrees
    ['Java.util.List', 'Java.util.List'],
    ['catalog와 scdn', 'catalog와 scdn'],
    ['localhost:8080', 'localhost 콜론 8080'], // the host is kept; the port colon is spoken,
    ['nginx.conf', '엔진엑스 점 콘프'],
    ['a-b와 no-error', 'a-b와 no-error'],
    ['../inbox/guide.txt', '../inbox/guide 점 텍스트'],
    ['훈련 / 테스트', '훈련 / 테스트'],
  ]);
});

test('comparison symbols are spoken as expressions or by name, never dropped', () => {
  cases([
    ['`>`', '크다 기호'], ['`>=`', '크거나 같다 기호'], ['`<`', '작다 기호'], ['`<=`', '작거나 같다 기호'],
    ['`==`', '등호 두 개'], ['`!=`', '느낌표 등호'], ['`===`', '등호 세 개'], ['`!==`', '느낌표 등호 두 개'],
    ['>는 같은 값을 포함하지 않아요.', '크다 기호는 같은 값을 포함하지 않아요.'],
    ['60도 포함하려면 >=를 사용하세요.', '60도 포함하려면 크거나 같다 기호를 사용하세요.'],
    ['이상이면 >=, 초과면 >죠?', '이상이면 크거나 같다 기호, 초과면 크다 기호죠?'],
    ['그건 >일 때 이야기예요.', '그건 크다 기호일 때 이야기예요.'],
    ['price >= 10000', 'price 크거나 같다 10000'],
    ['`count > max`', '카운트 크다 맥스'],
    ['`x != y`', 'x 같지 않다 y'],
    ['qty<=2만 두면', 'qty 작거나 같다 2만 두면'],
    ['> 0으로 되돌려요.', '크다 0으로 되돌려요.'],
    ['구현은 경계를 > 로 잘못 썼고', '구현은 경계를 크다 기호 로 잘못 썼고'],
    ['a &gt; b와 a &amp;gt; b', 'a 크다 b와 a 크다 b'],
  ]);
});

test('Bash redirection is named, not compared', () => {
  cases([
    ['`echo "첫 메모" > memo.txt`', '에코 첫 메모 꺾쇠 memo 점 텍스트'],
    ['`echo "둘째 줄" >> memo.txt`', '에코 둘째 줄 꺾쇠 두 개 memo 점 텍스트'],
    ['같은 echo 뒤에 > memo.txt를 붙이면', '같은 에코 뒤에 꺾쇠 memo 점 텍스트를 붙이면'],
    ['첫 메모 아래에 둘째 줄이 있어요. >> 는 덧붙이고, > 는 덮어써요.', '첫 메모 아래에 둘째 줄이 있어요. 꺾쇠 두 개 는 덧붙이고, 꺾쇠 는 덮어써요.'],
    ['`echo 설정 > .practice`', '에코 설정 꺾쇠 점 practice'],
    ['`ls 2>&1`', '엘에스 2 꺾쇠 앰퍼샌드 1'],
    ['`sort < names.txt`', '소트 왼쪽 꺾쇠 names 점 텍스트'.replace('소트', 'sort')],
  ]);
});

test('arithmetic, assignment, logic and code punctuation by context', () => {
  cases([
    ['`a + b`', 'a 더하기 b'], ['`a - b`', 'a 빼기 b'], ['`a * b`', 'a 곱하기 b'], ['`a / b`', 'a 나누기 b'],
    ['`7 % 2`', '7 나머지 2'], ['`a ** 2`', 'a의 2 제곱'], ['`a // 2`', 'a 몫 나누기 2'],
    ['`total += price`', 'total 플러스 이퀄 price'], ['`x -= 1`', 'x 마이너스 이퀄 1'], ['`i++`', 'i 플러스 플러스'],
    ['`a && b`', 'a 앤드 b'], ['`a || b`', 'a 오어 b'], ['`!done`', '낫 done'],
    ['&&는 두 조건이 모두 true인지 확인해요.', '앰퍼샌드 두 개는 두 조건이 모두 true인지 확인해요.'],
    ['||는 하나만 참이어도 참이에요.', '파이프 두 개는 하나만 참이어도 참이에요.'],
    ['=는 저장, !는 참과 거짓을 뒤집어요.', '등호는 저장, 느낌표는 참과 거짓을 뒤집어요.'],
    ['%는 나눗셈의 나머지를 구해요.', '퍼센트 기호는 나눗셈의 나머지를 구해요.'],
    ['`1 << 3`', '1 왼쪽 시프트 3'],
    ['p->count와 `x => x * 2`', 'p 화살표 카운트와 x 화살표 x 곱하기 2'], // count is a course term,
    ['map(Rq::pair)', '맵(Rq 콜론 콜론 pair)'],
    ['*pp = &other;는', '별표 pp 이퀄 앰퍼샌드 other;는'],
    ['int *p = &stock;', '인트 별표 p 이퀄 앰퍼샌드 stock;'],
    ['COUNT(*)>=2로', 'COUNT(별표) 크거나 같다 2로'],
    ['`;`과 `:`', '세미콜론과 콜론'],
    ['`()`', '괄호'],
    ['`` ` ``', '백틱'],
    ['HEAD^는 이전 커밋', 'HEAD 캐럿은 이전 커밋'],
    [':2는 0번과 1번까지예요.', '콜론 2는 영번과 일번까지예요.'],
    ['느낌표를 붙여 :q!로 끝내요.', '느낌표를 붙여 콜론 큐 느낌표로 끝내요.'],
    ['printf는 %d 자리에', '프린트에프는 퍼센트 d 자리에'],
  ]);
});

test('percentages, ratios, generics, HTML tags and conflict markers', () => {
  cases([
    ['생존율 38.20%가 나왔죠?', '생존율 38 점 이 영 퍼센트가 나왔죠?'],
    ['50%와 100%', '50 퍼센트와 100 퍼센트'],
    ['「8:2로」 나눠요', '「8 대 2로」 나눠요'],
    ['List<String>과 Map<String, List<Integer>>', 'List String과 Map String, List Integer'],
    ['<li data-code="A">처럼', 'li data-code 이퀄 A 태그처럼'],
    ['`</ul>`', '닫는 ul 태그'],
    ['#include <stdio.h>', '#include stdio.h'],
    ['<<<<<<< HEAD 아래, ======= 아래, >>>>>>> 줄까지', '왼쪽 꺾쇠 일곱 개 HEAD 아래, 등호 일곱 개 아래, 꺾쇠 일곱 개 줄까지'],
    ['/29를 /30으로 나누면', '슬래시 29를 슬래시 30으로 나누면'],
  ]);
});

test('natural punctuation stays silent and prose that names a symbol is not doubled', () => {
  cases([
    ['Hello, KPC!가 나왔죠?', 'Hello, 케이피씨!가 나왔죠?'],
    ['Unnamed: 0이라는 열', 'Unnamed: 0이라는 열'],
    ['입력이에요: 객실등급, 성별', '입력이에요: 객실등급, 성별'],
    ['int stock = 2;는', '인트 stock 이퀄 2;는'],
    ['md:가 두 열로', 'md:가 두 열로'],
    ["don't", "don't"],
    ['구조체 포인터에서는 화살표(->)로 필드를 골라요.', '구조체 포인터에서는 화살표로 필드를 골라요.'],
    ['정답은 세미콜론 ;예요.', '정답은 세미콜론이에요.'],
    ['문장 끝에는 세미콜론 `;`을 붙여요.', '문장 끝에는 세미콜론을 붙여요.'],
    ['비교는 ==, 등호 하나(=)는 대입이에요', '비교는 등호 두 개, 등호 하나는 대입이에요'],
    ['0~100 범위', '0~100 범위'],
  ]);
});

test('particles agree with the spoken word, not the written symbol', () => {
  cases([
    [':는 문장 끝 표시가 아니에요.', '콜론은 문장 끝 표시가 아니에요.'],
    ['`rm`로 지워요', '알엠으로 지워요'],
    ['`;`를 빠뜨리면', '세미콜론을 빠뜨리면'],
    ['cd로 notes 안에', '씨디로 notes 안에'],
    ['rmdir로 지워요.', '알엠디아이알로 지워요.'],
    ['>가 들어가요', '크다 기호가 들어가요'],
    ["무늬를 '%o%'로 바꿔 볼게요.", '무늬를 퍼센트 o 퍼센트 로 바꿔 볼게요.'],
    ['SQL는데', '에스큐엘는데'], // only a word-final particle is changed
  ]);
});

test('Markdown layout is not spoken; a leading > before a value or particle is', () => {
  cases([
    ['- 「거짓이라 건너뛴다」: 그건 `>`일 때 이야기예요.', '「거짓이라 건너뛴다」: 그건 크다 기호일 때 이야기예요.'],
    ['**다른 보기는 왜 아닌가**', '다른 보기는 왜 아닌가'],
    ['> 다음 커밋에 담을 내용', '다음 커밋에 담을 내용'],
    ['> `echo "첫 메모" > memo.txt`는 파일에 글을 써요.', '에코 첫 메모 꺾쇠 memo 점 텍스트는 파일에 글을 써요.'],
    ['> 로 저장해서 화면에는 아무것도 나오지 않아요.', '꺾쇠 로 저장해서 화면에는 아무것도 나오지 않아요.'],
    ['a \\> b와 C:\\work 폴더', 'a 크다 b와 C:\\work 폴더'], // a Markdown escape is dropped, a Windows path is kept
  ]);
});

// Reported 2026-10-28: 「wq를 더벨유큐라고 읽네? 더블유큐지」. wq reached the voice as written after 콜론.
test('Vim commands after a colon name their letters; other w, q and colons keep their letters', () => {
  cases([
    [':wq로 저장하고 끝내요.', '콜론 더블유큐로 저장하고 끝내요.'],
    ['`:wq`', '콜론 더블유큐'],
    [':wq!', '콜론 더블유큐 느낌표'],
    ['남겨야 하는 수정이면 :wq를 써요.', '남겨야 하는 수정이면 콜론 더블유큐를 써요.'],
    [':w로 저장해요.', '콜론 더블유로 저장해요.'],
    ['5. "`:w`"를 입력하고 Enter를 눌러 저장하세요.', '5. 콜론 더블유를 입력하고 Enter를 눌러 저장하세요.'],
    ['먼저 :q만으로 끝나는지 봐요.', '먼저 콜론 큐만으로 끝나는지 봐요.'],
    ['조심하세요. :q!는 저장 안 한 내용을 버려요.', '조심하세요. 콜론 큐 느낌표는 저장 안 한 내용을 버려요.'],
    ['(:wq)', '(콜론 더블유큐)'],
    // Not Vim commands: bare letters, slices, host:port style pairs, URLs and other ex commands stay as before.
    ['wq와 `w`, w = 3', 'wq와 w, w 이퀄 3'],
    ['a[:w]와 x:q', 'a[콜론 w]와 x 콜론 q'],
    ['http://x:wq/와 ws://x:wq', 'http://x:wq/와 ws://x 콜론 wq'], // a colon glued to a word is not a Vim command
    [':x로 끝내요', '콜론 x로 끝내요'],
  ]);
  for (const text of [':wq!', '`:q!`는', ':w로']) assert.equal(say(say(text)), say(text), text);
});

test('lexicon entries are unique, Korean, documented and ordered longest first', () => {
  const seen = new Map();
  for (const group of LEXICON) {
    assert.ok(group.id && group.scope && group.rationale && group.evidence && group.example, group.id);
    for (const entry of group.entries) {
      const [token, spoken, example] = entry;
      const key = group.scope.startsWith('after:') || ['extension', 'java-class', 'vim-ex'].includes(group.scope) ? group.scope + ' ' + token : (group.caseSensitive ? token : token.toLowerCase());
      assert.ok(!seen.has(key), `duplicate ${token} in ${group.id} and ${seen.get(key)}`);
      seen.set(key, group.id);
      assert.ok(spoken && spoken !== token, token);
      if (group.id !== 'course-terms') {
        assert.ok(example, `example for ${token}`);
        assert.doesNotMatch(spoken, /[A-Za-z]/, `${token} is spoken in Korean letters`);
      }
    }
  }
  // Longer entries win over their prefixes, and nothing is replaced twice.
  assert.equal(say('docker-compose up'), '도커 컴포즈 up');
  assert.equal(say('redis-cli와 Redis'), '레디스 씨엘아이와 레디스');
  assert.equal(say('Spring Boot'), '스프링 부트');
});

test('speech text is idempotent and leaves the source sentence unchanged', () => {
  const corpus = [
    '`mkdir notes`로 폴더를 만들고 `echo "첫 메모" > memo.txt`를 실행해요.', '>는 같은 값을 포함하지 않아요.',
    '`git commit -m "첫 기록"`', 'price >= 10000이면 i++해요.', 'JDBC와 Spring Boot, NULL', '*pp = &other;는',
    '<<<<<<< HEAD 아래', '생존율 38.20%', 'List<String>', '`a ** 2`', 'Hello, KPC!',
  ];
  for (const source of corpus) {
    const copy = source.slice();
    const once = say(source);
    assert.equal(say(once), once, source);
    assert.equal(source, copy);
    assert.doesNotMatch(once, /^\s|\s$/, source);
  }
});

test('the device and neural voices receive the same speech text; offsets still index the raw text', async () => {
  const source = '`mkdir notes`에 `echo hi > memo.txt`. >=는 이상이에요.';
  const device = [];
  const synth = { getVoices: () => [{ lang: 'ko-KR' }], cancel() {}, resume() {}, speak(u) { device.push(u.text); } };
  const controller = new speech.StorySpeech(synth, class { constructor(text) { this.text = text; } }, () => {}, { setTimeout: () => 0, clearTimeout() {} });
  controller.chunks = [source];
  controller.start();
  const bodies = [];
  const voiceContext = { console, URL, JSON, Map, Promise, String, Number, Object, setTimeout, clearTimeout,
    CustomEvent: class {}, document: {}, window: { addEventListener() {}, dispatchEvent() {} }, location: { protocol: 'http:' },
    molipPronunciation: context.molipPronunciation,
    fetch: (_url, init) => { bodies.push(JSON.parse(init.body)); return Promise.resolve({ ok: true, headers: { get: () => '' }, blob: async () => new Blob(['mp3']) }); } };
  vm.runInNewContext(readFileSync(new URL('../layout/voice.js', import.meta.url), 'utf8'), voiceContext);
  URL.revokeObjectURL(await voiceContext.molipVoice.synthesize(source));
  assert.equal(device[0], bodies[0].text);
  assert.equal(device[0], '엠케이디아이알 notes에 에코 hi 꺾쇠 memo 점 텍스트. 크거나 같다 기호는 이상이에요.');
  for (const sentence of speech.speechSentences(source)) assert.equal(source.slice(sentence.start, sentence.end), sentence.text);
});

// User reports: "Main.class" heard as 마인…, "javac" heard as 자백.
test('Java commands, class names and class files: javac, java Main, Main.java, Main.class', () => {
  cases([
    ['javac Main.java', '자바 씨 메인 점 자바'], ['`javac Main.java`', '자바 씨 메인 점 자바'],
    ['java Main', '자바 메인'], ['`java Main`', '자바 메인'], ['Main.class', '메인 점 클래스'], ['`Main.class`', '메인 점 클래스'],
    ['Main.java', '메인 점 자바'], ['javac', '자바 씨'], ['`javac`로 컴파일해요', '자바 씨로 컴파일해요'], ['JAVAC와 Java', 'JAVAC와 자바'],
    ['방금 만든 Main.class를 java Main으로 실행해요. 이번엔 .java를 붙이지 않아요.', '방금 만든 메인 점 클래스를 자바 메인으로 실행해요. 이번엔 점 자바를 붙이지 않아요.'],
    ['`java -cp out Main`', '자바 -cp out 메인'], ['`javac -d out src/Main.java`', '자바 씨 -d out src/메인 점 자바'], ['`out/Main.class`', 'out/메인 점 클래스'],
    ['`java Main.java Hello World`', '자바 메인 점 자바 Hello World'], ['class Main {', 'class 메인 {'], ['`new Main()`', 'new 메인()'],
    ['`Main`', '메인'], ['Main.class를 확인해요', '메인 점 클래스를 확인해요'], ['javac는 조용히 끝나요', '자바 씨는 조용히 끝나요'],
  ]);
});

test('Main is changed only where it names a Java class; other names, identifiers, URLs and prose keep their letters', () => {
  cases([
    ['MainTest.java', 'MainTest 점 자바'], ['MainActivity', 'MainActivity'], ['`Main_backup.java`', 'Main_backup 점 자바'],
    ['https://example.com/Main.class', 'https://example.com/Main.class'], ['Main 안의 다른 위치', 'Main 안의 다른 위치'],
    ['`java App.java`', '자바 App 점 자바'], ['`java Hello`', '자바 Hello'], ['Hello.class', 'Hello 점 클래스'],
    ['Main.unknownext', 'Main.unknownext'], ['javascript와 javadoc', 'javascript와 javadoc'], ['`String.class`', 'String 점 클래스'],
    ['main.py', '메인 점 파이'], ['`Main.java`의 main 메서드', '메인 점 자바의 메인 메서드'],
  ]);
});

test('Java examples reach the device and neural voices as the same text; the caption source is unchanged', async () => {
  const source = '`javac Main.java` 다음 `java Main`이면 Main.class를 실행해요.';
  const copy = source.slice();
  const device = [];
  const synth = { getVoices: () => [{ lang: 'ko-KR' }], cancel() {}, resume() {}, speak(u) { device.push(u.text); } };
  const controller = new speech.StorySpeech(synth, class { constructor(text) { this.text = text; } }, () => {}, { setTimeout: () => 0, clearTimeout() {} });
  controller.chunks = [source];
  controller.start();
  const bodies = [];
  const voiceContext = { console, URL, JSON, Map, Promise, String, Number, Object, setTimeout, clearTimeout,
    CustomEvent: class {}, document: {}, window: { addEventListener() {}, dispatchEvent() {} }, location: { protocol: 'http:' },
    molipPronunciation: context.molipPronunciation,
    fetch: (_url, init) => { bodies.push(JSON.parse(init.body)); return Promise.resolve({ ok: true, headers: { get: () => '' }, blob: async () => new Blob(['mp3']) }); } };
  vm.runInNewContext(readFileSync(new URL('../layout/voice.js', import.meta.url), 'utf8'), voiceContext);
  URL.revokeObjectURL(await voiceContext.molipVoice.synthesize(source));
  const expected = '자바 씨 메인 점 자바 다음 자바 메인이면 메인 점 클래스를 실행해요.';
  assert.equal(device[0], expected);
  assert.deepEqual(bodies, [{ text: expected, voice: 'ko-KR-SunHiNeural' }]);
  assert.equal(source, copy);
  // Narration (agent.js) speaks with the device voice through the same function.
  assert.match(readFileSync(new URL('../layout/agent.js', import.meta.url), 'utf8'), /molipPronunciation\.pronunciationText\(sentence\)/);
});

test('code spans next to prose: the sentence is converted in one piece', () => {
  cases([
    ['**결정 트리**(`DecisionTreeClassifier`)는 스무고개예요.', '결정 트리(디시전 트리 클래시파이어)는 스무고개예요.'],
    ['`a` > `b`이면', 'a 크다 b이면'], ["조심하세요. accept(')')는 닫는 괄호가 없어도", '조심하세요. accept(닫는 괄호)는 닫는 괄호가 없어도'],
    ["`price_text.replace(',', '')`가 쉼표를 빈 글자로 바꿔요. 그다음 `int('10,000')`", 'price_text.replace(,, 빈 문자열)가 쉼표를 빈 글자로 바꿔요. 그다음 인트(만)'],
    ['`"stream":false`면', 'stream 콜론 false면'], ['구간은 `60+`예요.', '구간은 60 플러스예요.'], ['`<값>`으로 출력하고 없으면 `<unset>`', '값으로 출력하고 없으면 unset'],
    ['`<li>`', 'li 태그'], ['`new ArrayList<>()`', 'new ArrayList()'], ["`WHERE status <> 'done'`", 'WHERE status 같지 않다 done'],
    ['`LRANGE mq:list:jobs 0 -1`', 'LRANGE mq 콜론 리스트 콜론 jobs 0 마이너스 1'], ['`SETBIT attend:2026-10 1 1`', 'SETBIT attend 콜론 2026-10 1 1'],
    ['`server_name app2-127-0-0-1.nip.io;`', 'server_name app2-127-0-0-1.nip.io;'], ['`nginx:1.27-alpine`', '엔진엑스 콜론 1.27-alpine'],
    ['`plt.ylim(0,100)`', 'plt.ylim(0,100)'], ['생존(0/1) 열', '생존(0 또는 1) 열'], ['5 - 3', '5 빼기 3'],
    ['`psql -c "UPDATE items SET stock = stock - 1 WHERE stock > 0" > a.txt`', '피에스큐엘 -c UPDATE items SET stock 이퀄 stock 빼기 1 WHERE stock 크다 0 꺾쇠 a 점 텍스트'],
    ["- `'−'를 '-'로` → 위키의 음수 기호", '빼기를 마이너스로 화살표 위키의 음수 기호'],
  ]);
});

test('SQL words the voice spells letter by letter, C names and dot-files', () => {
  cases([
    ['ROLLBACK과 COMMIT', '롤백과 COMMIT'], ['GROUP BY 뒤 HAVING', 'GROUP BY 뒤 해빙'], ['NOT EXISTS', 'NOT 이그지스츠'], ['ORDER BY price DESC', 'ORDER BY price 디에스씨'],
    ['`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`', '로우스 BETWEEN 언바운디드 프리시딩 AND CURRENT ROW'], ['id INTEGER PRIMARY KEY', 'id 인티저 PRIMARY KEY'],
    ['rollback_count와 DESCRIPTION', 'rollback_count와 DESCRIPTION'], ['printf는', '프린트에프는'], ['`jupyter notebook`', '주피터 노트북'],
    ['.practice 파일을 만들어요.', '점 practice 파일을 만들어요.'], ['종목 코드 뒤의 `.KS`는', '종목 코드 뒤의 점 KS는'], ['끝.Next', '끝.Next'],
  ]);
});

test('owner readings: the parent folder .. is 점점 and the option -a is 대시에이 (2026-10-30)', () => {
  cases([
    ['cd ..로 올라가요', '씨디 점점으로 올라가요'], ['`cd ..`를 실행하세요', '씨디 점점을 실행하세요'],
    ['git commit -a -m 메모', '깃 커밋 대시에이 -m 메모'], ['`ls -a`로 숨김 파일까지 봐요', '엘에스 대시에이로 숨김 파일까지 봐요'],
    ['-a 옵션은 모든 파일', '대시에이 옵션은 모든 파일'],
    // Other tokens keep their readings: longer options, a range, an ellipsis and arithmetic.
    ['`cd ../practice`', '씨디 ../practice'], ['`ls -al`', '엘에스 -al'], ['`ls --all`', '엘에스 --all'], ['1..10', '1..10'], ['그리고...', '그리고...'], ['5 - 3', '5 빼기 3'],
  ]);
});
