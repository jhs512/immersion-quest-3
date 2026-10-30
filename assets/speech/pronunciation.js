// Central speech-only pronunciation policy. See docs/voice.md.
// Shared by narration and reading, for neural and device voices.
// Never use this output for captions, source code, answers or terminal input.
(function () {
  'use strict';
  if (globalThis.molipPronunciation) return;

  // Marks the end of a replaced word until particles are agreed (private-use character, never spoken).
  const JOSA_MARK = '\uE000';
  // Stand-ins for converted code spans while the sentence around them is converted (private use, never spoken).
  const SPAN_BASE = 0xE100, SPAN_MARKS = /[\uE100-\uEFFF]/g;
  // ---- Lexicon: the single authority for how words are spoken. ----
  // Each group says where its entries apply and why; each entry is [written token, spoken Korean, example].
  // Scopes:
  //   term       prose words (legacy boundary: not inside a longer ASCII word; may sit inside a path).
  //   strict     prose words not inside a path, URL, option, identifier, ENV name or file name.
  //   command    strict in prose, and in code at a command position (line start, after | ; && || $ sudo)
  //              or as the whole code span.
  //   after:<w>  only right after the command word <w> (prose and code), e.g. git commit.
  //   java-class a Java class name (Main) only as a .java/.class stem, the class argument of java, a declaration
  //              (class/new/extends Main) or a whole code span.
  //   extension  file extensions, read after a spoken dot (Main.class → 메인 점 클래스).
  // Readings follow how Korean developers say the word aloud; letter names are used when the word is
  // an abbreviation, so the original spelling stays recognisable. Add an entry with an example and
  // a test in assets/speech/symbols-lexicon.test.mjs; tools/speech-audit.mjs and
  // assets/speech/pronunciation-review.test.mjs check every command and file name the lessons speak.
  const LEXICON = Object.freeze([
    {
      id: 'course-terms', scope: 'term', caseSensitive: true,
      rationale: 'Course vocabulary the Edge voice spells or mangles; readings already used in class.',
      evidence: 'kpc-finance, AICE and Git courses (narration and lesson bodies).',
      example: 'pandas DataFrame의 groupby → 판다스 데이터프레임의 그룹바이',
      entries: [
        ['Python', '파이썬'], ['pandas', '판다스'], ['DataFrame', '데이터프레임'], ['Series', '시리즈'],
        ['NumPy', '넘파이'], ['numpy', '넘파이'], ['matplotlib', '맷플롯립'], ['seaborn', '시본'], ['sklearn', '에스케이런'],
        ['scikit-learn', '사이킷런'], ['Pipeline', '파이프라인'], ['Titanic', '타이타닉'], ['titanic', '타이타닉'],
        ['KPC', '케이피씨'], ['AI', '에이아이'], ['CSV', '씨에스브이'], ['HTML', '에이치티엠엘'], ['Excel', '엑셀'], ['JSON', '제이슨'],
        ['SQLite', '에스큐엘라이트'], ['URL', '유알엘'], ['MAE', '엠에이이'], ['RMSE', '알엠에스이'], ['R²', '알 제곱'], ['R2', '알 제곱'],
        ['F1', '에프원'], ['ID', '아이디'], ['IDE', '아이디이'], ['API', '에이피아이'], ['OS', '오에스'], ['PC', '피씨'], ['GUI', '지유아이'],
        ['One-hot', '원핫'], ['one-hot', '원핫'], ['Ridge', '릿지'], ['Lasso', '라쏘'], ['fit', '핏'], ['predict', '프리딕트'],
        ['int', '인트'], ['str', '스트링'], ['float', '플로트'], ['bool', '불'], ['list', '리스트'], ['dict', '딕트'], ['None', '넌'],
        ['True', '트루'], ['False', '폴스'], ['print', '프린트'], ['input', '인풋'], ['split', '스플릿'], ['map', '맵'], ['filter', '필터'], ['len', '렌'],
        ['sum', '섬'], ['round', '라운드'], ['append', '어펜드'], ['import', '임포트'], ['main', '메인'], ['py', '파이'],
        ['if', '이프'], ['else', '엘스'], ['for', '포'], ['in', '인'], ['def', '데프'], ['return', '리턴'], ['lambda', '람다'],
        ['groupby', '그룹바이'], ['mean', '민'], ['median', '미디언'], ['max', '맥스'], ['min', '민'], ['count', '카운트'], ['shape', '셰이프'],
        ['head', '헤드'], ['tail', '테일'], ['index', '인덱스'], ['columns', '컬럼스'], ['dropna', '드롭엔에이'], ['fillna', '필엔에이'],
        ['isna', '이즈엔에이'], ['sort_values', '소트 밸류스'], ['value_counts', '밸류 카운츠'], ['read_csv', '리드 씨에스브이'],
        ['read_html', '리드 에이치티엠엘'], ['to_numpy', '투 넘파이'], ['pct_change', '퍼센트 체인지'], ['rolling', '롤링'], ['shift', '시프트'],
        ['lag', '래그'], ['target', '타깃'], ['leakage', '리키지'], ['baseline', '베이스라인'], ['accuracy', '애큐러시'],
        ['precision', '프리시전'], ['recall', '리콜'], ['LogisticRegression', '로지스틱 리그레션'], ['DecisionTreeClassifier', '디시전 트리 클래시파이어'],
        ['RandomForestClassifier', '랜덤 포레스트 클래시파이어'], ['DummyClassifier', '더미 클래시파이어'], ['LinearRegression', '리니어 리그레션'],
        ['StandardScaler', '스탠다드 스케일러'], ['OneHotEncoder', '원핫 인코더'], ['SimpleImputer', '심플 임퓨터'], ['ColumnTransformer', '컬럼 트랜스포머'],
        ['train_test_split', '트레인 테스트 스플릿'], ['mean_absolute_error', '민 앱솔루트 에러'], ['accuracy_score', '애큐러시 스코어'],
        ['IndentationError', '인덴테이션 에러'], ['KeyError', '키 에러'], ['TypeError', '타입 에러'], ['ValueError', '밸류 에러'],
        ['NaN', '낸'], ['nan', '낸'], ['EOFError', '이오에프 에러'], ['BeautifulSoup', '뷰티풀 수프'], ['WebView', '웹뷰'], ['Android', '안드로이드'],
        ['Anaconda', '아나콘다'], ['Jupyter', '주피터'], ['Notebook', '노트북'], ['notebook', '노트북'], ['wheel', '휠'],
        ['requests', '리퀘스트'], ['Selenium', '셀레니움'], ['selenium', '셀레니움'], ['webdriver', '웹드라이버'], ['Chrome', '크롬'], ['soup', '수프'],
        ['timeout', '타임아웃'], ['headers', '헤더스'], ['select', '셀렉트'], ['select_one', '셀렉트 원'], ['get_text', '겟 텍스트'], ['wikitable', '위키테이블'],
        ['Wikipedia', '위키피디아'], ['KOSPI', '코스피'], ['KOSDAQ', '코스닥'], ['yfinance', '와이 파이낸스'], ['yf', '와이에프'], ['FinanceDataReader', '파이낸스 데이터 리더'],
        ['fdr', '에프디알'], ['DataReader', '데이터 리더'], ['download', '다운로드'], ['Open', '오픈'], ['High', '하이'], ['Low', '로우'], ['Close', '클로즈'], ['Volume', '볼륨'],
        ['Change', '체인지'], ['idxmax', '아이디엑스 맥스'], ['idxmin', '아이디엑스 민'], ['cut', '컷'], ['observed', '옵저브드'], ['joblib', '잡립'], ['VS', '브이에스'],
        ['Code', '코드'], ['wiki', '위키'], ['robots', '로봇츠'], ['http', '에이치티티피'], ['https', '에이치티티피에스'], ['www', '더블유 더블유 더블유'],
      ],
    },
    {
      id: 'shell-commands', scope: 'command', caseSensitive: true,
      rationale: 'Unix commands are abbreviations; the voice garbles them ("mkdir" is not a word). Letter names keep the spelling; real words keep their usual Korean reading.',
      evidence: 'bash_basics, bash_environment, git_* and docker lessons: mkdir 10, ls 36, cat 87, echo 57, rm 14, rmdir 15, pwd 13, curl 33 occurrences in speech text.',
      example: '`mkdir notes`로 폴더를 만들어요 → 엠케이디아이알 notes로 폴더를 만들어요',
      entries: [
        ['mkdir', '엠케이디아이알', '`mkdir notes`'], ['rmdir', '알엠디아이알', '`rmdir old`'], ['pwd', '피더블유디', '`pwd`로 위치를 봐요'],
        ['ls', '엘에스', '`ls -l`'], ['cd', '씨디', '`cd notes`'], ['cp', '씨피', '`cp memo.txt memo-copy.txt`'], ['mv', '엠브이', '`mv a.txt b.txt`'],
        ['rm', '알엠', '`rm memo.txt`'], ['touch', '터치', '`touch memo.txt`'], ['cat', '캣', '`cat memo.txt`'], ['echo', '에코', '`echo 안녕`'],
        ['grep', '그렙', '`grep 메모 memo.txt`'], ['chmod', '체모드', '`chmod +x run.sh`'], ['chown', '체오운', '`chown me file`'],
        ['ps', '피에스', '`ps`'], ['kill', '킬', '`kill 1234`'], ['curl', '컬', '`curl -s http://localhost:8080/`'], ['sudo', '수도', '`sudo apt install git`'],
        ['wc', '더블유씨', '`wc -l memo.txt`'], ['vim', '빔', '`vim memo.txt`'], ['nano', '나노', '`nano memo.txt`'], ['bash', '배시', '`bash run.sh`'],
        ['ssh', '에스에스에이치', '`ssh server`'], ['pip', '핍', 'pip install pandas'], ['conda', '콘다', '`conda activate`'], ['python', '파이썬', '`python main.py`'],
        ['java', '자바', '`java Main`'], ['javac', '자바 씨', '`javac Main.java` (two words: 자바씨 is heard as 자백)'], ['gradle', '그레이들', '`gradle build`'], ['mvn', '메이븐', '`mvn test`'],
        ['npm', '엔피엠', '`npm install`'], ['npx', '엔피엑스', '`npx vite`'], ['node', '노드', '`node app.js`'], ['docker', '도커', '`docker ps`'],
        ['docker-compose', '도커 컴포즈', '`docker-compose up`'], ['psql', '피에스큐엘', '`psql -U postgres`'], ['mysql', '마이에스큐엘', '`mysql -u root`'],
        ['sqlite3', '에스큐엘라이트 쓰리', '`sqlite3 shop.db`'], ['redis-cli', '레디스 씨엘아이', '`redis-cli -p 16379 GET key`'], ['gh', '지에이치', '`gh pr create`'],
        ['nginx', '엔진엑스', '`nginx -t`'], ['wsl', '더블유에스엘', '`wsl --install`'], ['jupyter', '주피터', '`jupyter notebook`'],
      ],
    },
    {
      id: 'git-subcommands', scope: 'after:git', caseSensitive: true,
      rationale: 'Spoken right after git; the course already says these in Korean (커밋, 푸시, 브랜치). Arguments after the subcommand stay as written.',
      evidence: 'git_* lessons: git status 21, commit 28, push 28, diff 26, branch 24, fetch 21, restore 16, revert 11, init 9.',
      example: '`git commit -m "첫 기록"` → 깃 커밋 -m 첫 기록',
      entries: [
        ['init', '이닛', 'git init'], ['status', '스테이터스', 'git status'], ['add', '애드', 'git add memo.txt'], ['commit', '커밋', 'git commit -m'],
        ['push', '푸시', 'git push'], ['pull', '풀', 'git pull'], ['fetch', '페치', 'git fetch'], ['clone', '클론', 'git clone'],
        ['log', '로그', 'git log --oneline'], ['diff', '디프', 'git diff'], ['show', '쇼', 'git show HEAD:guide.txt'], ['branch', '브랜치', 'git branch'],
        ['switch', '스위치', 'git switch feature'], ['checkout', '체크아웃', 'git checkout main'], ['merge', '머지', 'git merge feature'],
        ['rebase', '리베이스', 'git rebase main'], ['remote', '리모트', 'git remote add origin'], ['restore', '리스토어', 'git restore memo.txt'],
        ['reset', '리셋', 'git reset'], ['revert', '리버트', 'git revert HEAD'], ['stash', '스태시', 'git stash'], ['tag', '태그', 'git tag v1'],
        ['config', '컨피그', 'git config user.name'], ['rm', '알엠', 'git rm memo.txt'], ['mv', '엠브이', 'git mv a.txt b.txt'],
        ['cherry-pick', '체리픽', 'git cherry-pick abc123'], ['blame', '블레임', 'git blame memo.txt'], ['reflog', '리플로그', 'git reflog'],
      ],
    },
    {
      id: 'docker-subcommands', scope: 'after:docker', caseSensitive: true,
      rationale: 'Docker subcommands that are abbreviations; ordinary words (run, up, logs) are left to the voice.',
      evidence: 'docker lessons: docker ps, docker rm -f, docker exec, docker compose.',
      example: '`docker compose up` → 도커 컴포즈 up',
      entries: [['compose', '컴포즈', 'docker compose up'], ['ps', '피에스', 'docker ps'], ['rm', '알엠', 'docker rm -f mq-web'], ['rmi', '알엠아이', 'docker rmi image'], ['exec', '이그젝', 'docker exec -it db bash']],
    },
    {
      id: 'gh-subcommands', scope: 'after:gh', caseSensitive: true,
      rationale: 'GitHub CLI nouns that are abbreviations.', evidence: 'github_pr lesson: gh pr create, gh repo create.',
      example: '`gh pr create` → 지에이치 피알 create',
      entries: [['pr', '피알', 'gh pr create'], ['repo', '레포', 'gh repo create']],
    },
    {
      id: 'tech-names', scope: 'strict', caseSensitive: true,
      rationale: 'Abbreviations read by letter names and product names in their usual Korean form. Not applied inside paths, URLs, identifiers or file names.',
      evidence: 'SQL 89, PR 40, Redis 40, JDK 25, Vim 23, DB 18, PostgreSQL 11, JVM 8, HTTP 8 occurrences; upcoming DB/Spring course (JDBC, JPA, Spring Boot).',
      example: 'JDBC로 PostgreSQL에 붙어요 → 제이디비씨로 포스트그레스큐엘에 붙어요',
      entries: [
        ['SQL', '에스큐엘', 'SQL 조회'], ['NoSQL', '노에스큐엘', 'NoSQL 저장소'], ['MySQL', '마이에스큐엘', 'MySQL 서버'], ['PostgreSQL', '포스트그레스큐엘', 'PostgreSQL 컨테이너'],
        ['Postgres', '포스트그레스', 'Postgres 이미지'], ['MariaDB', '마리아디비', 'MariaDB'], ['Oracle', '오라클', 'Oracle DB'], ['Redis', '레디스', 'Redis 키'],
        ['MongoDB', '몽고디비', 'MongoDB'], ['H2', '에이치투', 'H2 데이터베이스'], ['DB', '디비', 'DB 연결'], ['DBMS', '디비엠에스', 'DBMS'], ['RDBMS', '알디비엠에스', 'RDBMS'],
        ['NULL', '널', 'NOT NULL 제약'], ['null', '널', 'null이면'], ['DDL', '디디엘', 'DDL'], ['DML', '디엠엘', 'DML'], ['CRUD', '크러드', 'CRUD'],
        ['JDBC', '제이디비씨', 'JDBC 드라이버'], ['JPA', '제이피에이', 'JPA 엔티티'], ['ORM', '오알엠', 'ORM'], ['DTO', '디티오', 'DTO'], ['DAO', '다오', 'DAO'],
        ['Java', '자바', 'Java 25'], ['JDK', '제이디케이', 'JDK 25'], ['JRE', '제이알이', 'JRE'], ['JVM', '제이브이엠', 'JVM'], ['JUnit', '제이유닛', 'JUnit 테스트'],
        ['Gradle', '그레이들', 'Gradle 빌드'], ['Maven', '메이븐', 'Maven'], ['Spring', '스프링', 'Spring 컨테이너'], ['Spring Boot', '스프링 부트', 'Spring Boot 앱'],
        ['Hibernate', '하이버네이트', 'Hibernate'], ['Tomcat', '톰캣', 'Tomcat'], ['Lombok', '롬복', 'Lombok'],
        ['HTTP', '에이치티티피', 'HTTP 요청'], ['HTTPS', '에이치티티피에스', 'HTTPS'], ['REST', '레스트', 'REST API'], ['RESTful', '레스트풀', 'RESTful'],
        ['YAML', '야믈', 'YAML 파일'], ['XML', '엑스엠엘', 'XML'], ['CSS', '씨에스에스', 'CSS'], ['JS', '제이에스', 'JS'], ['JSX', '제이에스엑스', 'JSX'],
        ['JavaScript', '자바스크립트', 'JavaScript'], ['TypeScript', '타입스크립트', 'TypeScript'], ['React', '리액트', 'React'],
        ['Docker', '도커', 'Docker Desktop'], ['Docker Compose', '도커 컴포즈', 'Docker Compose'], ['Compose', '컴포즈', 'Compose 파일'], ['Dockerfile', '도커파일', 'Dockerfile'],
        ['Kafka', '카프카', 'Kafka'], ['Nginx', '엔진엑스', 'Nginx'], ['NGINX', '엔진엑스', 'NGINX가 site1을 내보내요'], ['Vim', '빔', 'Vim'], ['Bash', '배시', 'Bash'],
        ['Linux', '리눅스', 'Linux'], ['Ubuntu', '우분투', 'Ubuntu'], ['WSL', '더블유에스엘', 'WSL'], ['PowerShell', '파워셸', 'PowerShell'],
        ['CLI', '씨엘아이', 'CLI'], ['PR', '피알', 'PR을 열어요'], ['IP', '아이피', 'IP 주소'], ['TCP', '티씨피', 'TCP'], ['UDP', '유디피', 'UDP'],
        ['DNS', '디엔에스', 'DNS'], ['SSH', '에스에스에이치', 'SSH'], ['CPU', '씨피유', 'CPU'], ['localhost', '로컬호스트', 'localhost'],
      ],
    },
    {
      id: 'sql-keywords', scope: 'strict', caseSensitive: true,
      rationale: 'Upper-case SQL words the Edge voice spells letter by letter (ROLLBACK → 알오엘엘비에이씨케이). Other upper-case keywords (SELECT, WHERE, JOIN …) are read as words and stay as written.',
      evidence: 'Audit of all published lessons + SunHi duration check (raw ≈ spelled, not ≈ lower-case word): .scratch/speech-command-audit/spec.md. engineer-sql-*, engineer-db-*, java-backend lessons.',
      example: 'ROLLBACK 뒤에는 → 롤백 뒤에는',
      entries: [
        ['ROLLBACK', '롤백', 'COMMIT과 ROLLBACK'], ['SAVEPOINT', '세이브포인트', 'SAVEPOINT sp1'], ['HAVING', '해빙', 'GROUP BY … HAVING'], ['EXISTS', '이그지스츠', 'WHERE EXISTS'],
        ['REVOKE', '리보크', 'REVOKE SELECT'], ['PRIVILEGES', '프리빌리지스', 'ALL PRIVILEGES'], ['REFERENCES', '레퍼런시스', 'REFERENCES items(id)'],
        ['PRECEDING', '프리시딩', '2 PRECEDING'], ['FOLLOWING', '팔로잉', 'UNBOUNDED FOLLOWING'], ['UNBOUNDED', '언바운디드', 'UNBOUNDED PRECEDING'], ['ROWS', '로우스', 'ROWS BETWEEN'],
        ['INTEGER', '인티저', 'id INTEGER'], ['APPEND', '어펜드', 'APPEND 모드'], ['DESC', '디에스씨', 'ORDER BY price DESC'],
      ],
    },
    {
      id: 'c-functions', scope: 'strict', caseSensitive: true,
      rationale: 'C library names that are not words; read the way Korean C classes say them.',
      evidence: 'engineer-c-start, engineer-c-* lessons (printf in narration and problems).', example: 'printf는 → 프린트에프는',
      entries: [['printf', '프린트에프', 'printf("%d", stock)']],
    },
    {
      id: 'java-classes', scope: 'java-class', caseSensitive: true,
      rationale: 'Java class names the voice misreads (Main is heard as 마인). Only where the word names a Java class: the stem of a .java or .class file, the class argument of java, a class declaration, or a code span holding only the name. Other words, longer identifiers (MainTest) and URLs keep their letters.',
      evidence: 'java-launch, java-arguments, java-files: Main.java 177, Main.class 12 narration lines, java Main 3; user report (Main.class heard as 마인).',
      example: '`javac Main.java` 다음 java Main → 자바 씨 메인 점 자바 다음 자바 메인',
      entries: [['Main', '메인', 'Main.class, java Main, class Main {']],
    },
    {
      id: 'file-extensions', scope: 'extension', caseSensitive: true,
      rationale: 'A file name read as one word is garbled ("main.py" → 마이노파이), so the dot is spoken and the extension is named. Extensions not listed here stay as written.',
      evidence: 'Audit of all published lessons (tools/speech-audit.mjs): .txt 229, .csv 64, .java 54, .py 18, .class 12, .html 10, .joblib 7, .sql 4, .xlsx 4.',
      example: 'Main.class → 메인 점 클래스',
      entries: [
        ['py', '파이', 'main.py'], ['csv', '씨에스브이', 'stock.csv'], ['xlsx', '엑셀', 'sales.xlsx'], ['xls', '엑셀', 'old.xls'], ['html', '에이치티엠엘', 'prices.html'],
        ['json', '제이슨', 'regions.json'], ['joblib', '잡립', 'model.joblib'], ['txt', '텍스트', 'memo.txt'], ['md', '엠디', 'README.md'], ['java', '자바', 'Main.java'],
        ['class', '클래스', 'Main.class'], ['sql', '에스큐엘', 'setup.sql'], ['sh', '에스에이치', 'run.sh'], ['yml', '야믈', 'compose.yml'], ['yaml', '야믈', 'app.yaml'],
        ['xml', '엑스엠엘', 'pom.xml'], ['log', '로그', 'app.log'], ['conf', '콘프', 'nginx.conf'],
      ],
    },
    {
      id: 'vim-commands', scope: 'vim-ex', caseSensitive: true,
      rationale: 'Vim command-line commands are letter names. Left as written the voice reads wq as 더벨유큐 (user report 2026-10-28). Only right after a colon that starts a word (:wq, `:w`, :q!); a bare w, q or wq, variables, paths and host:port keep their letters.',
      evidence: 'vim_basics narration: :w 6, :q 2, :q! 4, :wq 4 lines; user report 「wq를 더벨유큐라고 읽네? 더블유큐지」.',
      example: ':wq로 저장하고 끝내요 → 콜론 더블유큐로 저장하고 끝내요',
      entries: [['w', '더블유', ':w로 저장해요'], ['q', '큐', ':q만으로 끝나는지'], ['wq', '더블유큐', ':wq로 저장하고 끝내요']],
    },
    {
      id: 'brands', scope: 'brand', caseSensitive: false,
      rationale: 'Git and GitHub in any case; paths, domains and longer identifiers keep their letters (docs/voice.md).',
      evidence: 'Git courses.', example: 'Git과 GitHub → 깃과 깃허브',
      entries: [['git', '깃', 'Git, git, GIT'], ['github', '깃허브', 'GitHub']],
    },
  ]);

  // Derived views (kept for callers and tests).
  const groupEntries = predicate => LEXICON.filter(predicate).flatMap(group => group.entries);
  const pronunciations = Object.freeze(Object.fromEntries(groupEntries(g => ['term', 'strict', 'command'].includes(g.scope)).map(([w, s]) => [w, s])));
  const brandPronunciations = Object.freeze(Object.fromEntries(groupEntries(g => g.scope === 'brand').map(([w, s]) => [w, s])));
  const escapeRegExp = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const alternation = words => words.slice().sort((a, b) => b.length - a.length).map(escapeRegExp).join('|');
  const table = scope => Object.fromEntries(groupEntries(g => g.scope === scope).map(([w, s]) => [w, s]));
  const termTable = table('term'), strictTable = { ...table('strict'), ...table('command') }, commandTable = table('command');
  const subcommandTables = Object.fromEntries(LEXICON.filter(g => g.scope.startsWith('after:')).map(g => [g.scope.slice(6), Object.fromEntries(g.entries.map(([w, s]) => [w, s]))]));
  // Legacy boundary: not inside a longer ASCII word or a hyphenated name (py-2, data-code).
  const termPattern = new RegExp('(?<![A-Za-z0-9_$-])(' + alternation(Object.keys(termTable)) + ')(?![A-Za-z0-9_]|-[A-Za-z0-9])', 'g');
  // Strict boundary: also not part of a path, URL, option, ENV name, host:port or file name.
  const STRICT_BEFORE = '(?<![A-Za-z0-9_./\\\\@$%:#-])', STRICT_AFTER = '(?![A-Za-z0-9_/\\\\@:#-]|\\.[A-Za-z0-9_])';
  const strictPattern = new RegExp(STRICT_BEFORE + '(' + alternation(Object.keys(strictTable)) + ')' + STRICT_AFTER, 'g');
  // head and tail are course terms (pandas) that are also commands; at a command position they read the same.
  const commandWords = { ...commandTable, head: termTable.head, tail: termTable.tail };
  const commandPattern = new RegExp('(^|[|;&(]\\s*|\\$\\s+|\\b(?:sudo|xargs|time|exec)\\s+)(' + alternation(Object.keys(commandWords)) + ')(?=\\s|$|[;|&)])', 'g');
  const subcommandPattern = new RegExp(STRICT_BEFORE + '(' + alternation(Object.keys(subcommandTables)) + ')(\\s+)([a-z][a-z-]*)(?=\\s|$|[;|&)`]|[가-힣])', 'g');
  const subcommandText = text => text.replace(subcommandPattern, (match, command, space, sub) => {
    const spoken = subcommandTables[command][sub];
    return spoken ? command + space + spoken + JOSA_MARK : match;
  });
  // Java class names, only where the word is a class: java [options] Main, class Main {, new Main().
  // File stems (Main.java) are handled with the file names below.
  const javaClasses = table('java-class');
  const javaClassNames = alternation(Object.keys(javaClasses));
  const javaArgumentPattern = new RegExp('(?<![\\w./-])(java(?:\\s+-[\\w:.-]+(?:\\s+(?![-\\s])[^\\s|;&`]+)?)*\\s+)(' + javaClassNames + ')(?![\\w./\\\\-])', 'g');
  const javaDeclarationPattern = new RegExp('(?<![\\w.])((?:class|interface|enum|record|new|extends|implements)\\s+)(' + javaClassNames + ')(?![\\w./\\\\-])', 'g');
  const javaClassText = text => text.replace(javaArgumentPattern, (_, lead, name) => lead + javaClasses[name] + JOSA_MARK)
    .replace(javaDeclarationPattern, (_, lead, name) => lead + javaClasses[name] + JOSA_MARK);
  // Vim commands (:w, :q, :wq, :q!, :wq!): the colon starts a word and the command ends one. The letters are
  // named (wq → 더블유큐) and a trailing ! is 느낌표. Python slices ([:w]), host:port and identifiers are untouched.
  const vimCommands = table('vim-ex');
  const vimPattern = new RegExp('(^|[\\s(「『“‘]):(' + alternation(Object.keys(vimCommands)) + ')(!?)(?=$|[\\s.,?)」』”’]|[가-힣])', 'g');
  const vimText = text => text.replace(vimPattern, (_, lead, command, bang) => lead + '콜론 ' + vimCommands[command] + (bang ? ' 느낌표' : '') + JOSA_MARK);

  // ---- Numbers ----
  // Protect code, dates, versions and paths from prose conversion.
  const protectedSpans = /(``[^\n]+?``|`[^`\n]+`|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b[vV]\d+(?:\.\d+)+|\b\d+(?:\.\d+){2,}|\b\d{1,2}:\d{2}(?::\d{2})?|[A-Za-z]:\\[^\s]+)/g;
  const digits = ['영', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
  const symbols = {
    '×': '곱하기', '÷': '나누기', '−': '빼기', '±': '플러스 마이너스', '≤': '작거나 같다', '≥': '크거나 같다',
    '≠': '같지 않다', '≈': '거의 같다', '→': '화살표', '←': '왼쪽 화살표', '↔': '양방향 화살표', '∞': '무한대', '√': '루트',
  };
  // "3번" is read with the Sino-Korean numeral (삼번), as a question or option number is said
  // in class; the voice would otherwise count it 세번. Numbers 1–99.
  const tens = ['', '십', '이십', '삼십', '사십', '오십', '육십', '칠십', '팔십', '구십'];
  const sinoKorean = n => (n < 10 ? digits[n] : tens[Math.floor(n / 10)] + (n % 10 ? digits[n % 10] : ''));
  function koreanInteger(value) {
    const number = value.replaceAll(',', '').replace(/^0+(?=\d)/, '');
    if (number === '0') return '영';
    if (number.length > 20) return value;
    const groups = [], large = ['', '만', '억', '조', '경'], small = ['', '십', '백', '천'];
    for (let end = number.length, group = 0; end > 0; end -= 4, group++) {
      const chunk = number.slice(Math.max(0, end - 4), end);
      let spoken = '';
      for (let index = 0; index < chunk.length; index++) {
        const digit = Number(chunk[index]), place = chunk.length - index - 1;
        if (digit) spoken += (digit === 1 && place ? '' : digits[digit]) + small[place];
      }
      if (spoken) groups.unshift((group === 1 && spoken === '일' ? '' : spoken) + large[group]);
    }
    return groups.join(' ');
  }
  const formatPrices = text => String(text).replace(/(?<![A-Za-z0-9_.,])(\d{1,3}(?:,\d{3})+|\d+)(?=\s*원)/g,
    value => value.replaceAll(',', '').replace(/\B(?=(\d{3})+(?!\d))/g, ','));
  function numberSpeechText(input) {
    return input
      .replace(/(?<![A-Za-z0-9_.,])(\d{1,3}(?:,\d{3})+|\d+)\s*원/g, (_, n) => koreanInteger(n) + ' 원')
      // Thousands groups; "0,100" is a pair of numbers (a tuple), not a hundred.
      .replace(/(?<![\w.,])([1-9]\d{0,2}(?:,\d{3})+)(?![\w.,])/g, (_, n) => koreanInteger(n))
      .replace(/(?<![\d.,])(\d{1,2})번/g, (_, n) => sinoKorean(Number(n)) + '번')
      .replace(/(?<![A-Za-z0-9_])R²/g, '알 제곱')
      .replace(/([A-Za-z0-9])²/g, '$1 제곱').replace(/([A-Za-z0-9])³/g, '$1 세제곱')
      // Percent before decimals, so 38.20% stays a percentage and never reaches the modulus rule.
      .replace(/(?<![\w.])(\d+(?:,\d{3})*(?:\.\d+)?)\s*%/g, '$1 퍼센트')
      // A decimal, not a version tag (nginx:1.27-alpine).
      .replace(/(?<![\w.])(\d+)\.(\d+)(?![\w.]|-[A-Za-z])/g, (_, whole, fraction) => whole + ' 점 ' + [...fraction].map(d => digits[Number(d)]).join(' '))
      // A ratio in prose: 8:2 → 8 대 2 (times like 8:20 are protected spans).
      .replace(/(?<![\w.:])(\d{1,2}):(\d{1,2})(?![\w.:])/g, '$1 대 $2')
      // Subtraction only as "5 - 3", spaced on both sides. A hyphen inside a name or id stays (app2-127-0-0-1.nip.io,
      // stream id 1-1, key attend:2026-10), and "0 -1" is a minus sign (LRANGE 0 -1).
      .replace(/(?<=(?<![\w.:-])\d+) - (?=\d+(?![\w.-]))/g, ' 빼기 ')
      // 0/1 is a pair of labels (생존 0/1), never the fraction zero.
      .replace(/(?<![\w./])0\/1(?![\w./])/g, '0 또는 1')
      .replace(/(?<![\w./])(\d+)\s*\/\s*(\d+)(?![\w./])/g, '$2분의 $1')
      .replace(/(?<![\w.\-])-(\d+)/g, '마이너스 $1');
  }

  // ---- Symbols: operators and code punctuation, by context. ----
  // expr: between two operands (a > b). noun: the symbol itself is talked about (">는", "`>=`", "답은 |.").
  const OPS = {
    '>': ['크다', '크다 기호'], '<': ['작다', '작다 기호'], '>=': ['크거나 같다', '크거나 같다 기호'], '<=': ['작거나 같다', '작거나 같다 기호'],
    '==': ['같다', '등호 두 개'], '!=': ['같지 않다', '느낌표 등호'], '<>': ['같지 않다', '같지 않다 기호'], '===': ['등호 세 개'], '!==': ['느낌표 등호 두 개'],
    '=': ['이퀄', '등호'], '+': ['더하기', '플러스'], '-': ['빼기', '마이너스'], '*': ['곱하기', '별표'], '/': ['나누기', '슬래시'],
    '%': ['나머지', '퍼센트 기호'], '**': ['제곱', '별표 두 개'], '//': ['몫 나누기', '슬래시 두 개'],
    '+=': ['플러스 이퀄'], '-=': ['마이너스 이퀄'], '*=': ['곱하기 이퀄'], '/=': ['나누기 이퀄'], '%=': ['나머지 이퀄'],
    '**=': ['제곱 이퀄'], '//=': ['몫 나누기 이퀄'], '&=': ['앰퍼샌드 이퀄'], '|=': ['파이프 이퀄'], '^=': ['캐럿 이퀄'],
    '<<=': ['왼쪽 시프트 이퀄'], '>>=': ['오른쪽 시프트 이퀄'], '++': ['플러스 플러스'], '--': ['마이너스 마이너스'],
    '&&': ['앤드', '앰퍼샌드 두 개'], '||': ['오어', '파이프 두 개'], '!': ['낫', '느낌표'], '&': ['앰퍼샌드'], '|': ['파이프'], '^': ['캐럿'],
    '<<': ['왼쪽 시프트'], '>>': ['오른쪽 시프트'], '->': ['화살표'], '=>': ['화살표'], '::': ['콜론 콜론'],
    ':': ['콜론'], ';': ['세미콜론'], '(': ['여는 괄호'], ')': ['닫는 괄호'], '()': ['괄호'], '[]': ['대괄호'], '{}': ['중괄호'],
    "'": ['작은따옴표'], '"': ['큰따옴표'], '`': ['백틱'],
  };
  // In shell commands < and > redirect; they are named, not compared.
  const SHELL_OPS = { '>': '꺾쇠', '>>': '꺾쇠 두 개', '<': '왼쪽 꺾쇠', '<<': '왼쪽 꺾쇠 두 개' };
  const PUNCTUATION = new Set([':', ';', '(', ')', '()', '[]', '{}', "'", '"', '`']);
  const UNARY = new Set(['-', '+', '*', '**', '&', '!', '++', '--']);
  const COMPARISON = new Set(['>', '<', '>=', '<=']);
  const TOKEN = /!==|===|\*\*=|\/\/=|>>=|<<=|->|=>|::|&&|\|\||==|!=|<=|>=|<>|\+=|-=|\*=|\/=|%=|&=|\|=|\^=|\+\+|--|\*\*|\/\/|<<|>>|\(\)|\[\]|\{\}|[<>=+\-*/%!&|^:;()'"`]/g;
  const PARTICLE = /^(?:이에요|예요|이라|이고|이면|이나|이랑|으로|처럼|부터|까지|보다|하고|라고|와|과|는|은|가|이|를|을|로|도|만|의|에|죠|요|면|랑|나)/;
  const PARTICLE_WORD = new RegExp(PARTICLE.source + '(?=[\\s.,?!]|$)');
  const BARE_PARTICLE = /^\s(?:으로|이에요|예요|는|은|를|을|로|와|과|가|이|도|만|에|의)(?=[\s.,?!]|$)/;
  const OPERAND_LEFT = /[A-Za-z0-9_)\]}'"`가-힣\uE100-\uEFFF]/, OPERAND_RIGHT = /[A-Za-z0-9_(\[{'"`$가-힣\uE100-\uEFFF]/;
  const ENDS_WITH_PARTICLE = /[가-힣\s](?:은|는|이|가|을|를|와|과|로|면|도|의|에)$/;
  // A chunk that talks about writing files: a bare > or >> there is the redirection.
  const SHELL_HINT = /(파일|덮어|덧붙|이어 ?붙|끝에 붙|새로 써|사본|화면 대신|화면에는|리다이렉|리디렉|\becho\b|\bcat\b|\b[\w-]+\.(?:txt|log|out)\b)/;
  const SHELL_START = /^\s*(?:\$\s+)?(?:sudo\s+)?(?:echo|printf|cat|ls|cd|pwd|mkdir|rmdir|rm|cp|mv|touch|grep|sort|uniq|head|tail|wc|cut|tr|find|sed|awk|tee|chmod|chown|ps|kill|curl|wget|git|gh|docker|docker-compose|python3?|pip|java|javac|node|npm|npx|gradle|mvn|psql|mysql|sqlite3|redis-cli|bash|sh|ssh|tar|unzip|date|which|env|export|source|\.\/\S+)(?=\s|$)/;
  const FILE_TARGET = /^\s*(?:\/dev\/null|\.[\w-]+(?:\.[\w-]+)*\s|\.[\w-]+(?:\.[\w-]+)*$|[\w.~-]*\/[\w./-]*|[\w-]+\.(?:txt|md|log|csv|tsv|out|err|json|py|java|c|sh|html|xml|ya?ml|dat|bak|sql|conf)\b)/;
  const URL_PATTERN = /\b(?:https?|ftp|file|ssh):\/\/[^\s'"`<>)]+|\bwww\.[^\s'"`<>)]+/g;
  // When prose already names the symbol, the symbol is not spoken again: 화살표(->), 세미콜론 `;`.
  const ALIASES = {
    '->': ['화살표'], '=>': ['화살표'], ';': ['세미콜론'], ':': ['콜론'], '==': ['등호 두 개'], '=': ['등호', '등호 하나', '이퀄'],
    '!': ['느낌표'], '*': ['별표', '애스터리스크'], '&': ['앰퍼샌드'], '|': ['파이프', '세로 막대'], '%': ['퍼센트', '퍼센트 기호'],
    '^': ['캐럿'], '>': ['꺾쇠', '크다 기호'], '<': ['작다 기호'], '`': ['백틱'], "'": ['작은따옴표'], '"': ['큰따옴표'], '()': ['괄호'],
  };
  const aliasPatterns = Object.entries(ALIASES).sort((a, b) => b[0].length - a[0].length).map(([token, names]) => [
    new RegExp('(' + names.map(escapeRegExp).join('|') + ')(?:\\s*\\(\\s*(`?)' + escapeRegExp(token) + '\\2\\s*\\)|\\s+(`?)' + escapeRegExp(token) + '\\3(?![^\\s.,?!가-힣]))', 'g'), '$1' + JOSA_MARK]);
  const suppressAliases = text => aliasPatterns.reduce((result, [pattern, replacement]) => result.replace(pattern, replacement), text);
  const COUNT = { 4: '네', 5: '다섯', 6: '여섯', 7: '일곱', 8: '여덟', 9: '아홉', 10: '열' };
  const HTML_TAGS = new Set(('html head body title meta link script style div span p a ul ol li dl dt dd table thead tbody tfoot tr td th '
    + 'h1 h2 h3 h4 h5 h6 img br hr form input button label select option textarea pre code strong em b i u small sub sup '
    + 'section article header footer nav main aside figure figcaption template iframe canvas svg video audio source').split(' '));
  const RUN_NAMES = { '<': '왼쪽 꺾쇠', '>': '꺾쇠', '=': '등호' };
  // Spaces around a spoken symbol; a noun keeps its particle attached ("크다 기호는").
  const pad = (name, before, after, kind) => (before && !/[\s(\[「『]$/.test(before) ? ' ' : '') + name
    + (after && !/^[\s.,?!:;)\]」』]/.test(after) && !(kind === 'noun' && /^[가-힣]/.test(after)) ? ' ' : '');
  const pickName = (token, shell) => (shell && SHELL_OPS[token]) || null;

  function classify(token, s, offset, options) {
    const before = s.slice(0, offset), after = s.slice(offset + token.length);
    const prev = before.slice(-1), next = after.charAt(0);
    const spaceBefore = /\s/.test(prev), spaceAfter = /\s/.test(next);
    const prevNon = before.trimEnd().slice(-1), nextNon = after.trimStart().charAt(0);
    // An opening quote right before the symbol ("'%{…}'") is not an operand.
    const openingQuote = /['"`]/.test(prevNon) && /(^|[\s(=,])['"`]$/.test(before.trimEnd());
    const leftOperand = !!prevNon && OPERAND_LEFT.test(prevNon) && !openingQuote && !(spaceBefore && ENDS_WITH_PARTICLE.test(before.trimEnd()));
    // A closing quote right after the symbol ("'%o%'로") is not an operand either.
    const closingQuote = /['"`]/.test(nextNon) && /^\s*['"`](?:[\s.,)?!:;가-힣]|$)/.test(after);
    const rightOperand = !!nextNon && !closingQuote && (OPERAND_RIGHT.test(nextNon) || /^\s*(?:-\d|[*&!~-]+[A-Za-z_(])/.test(after));
    const leftAttached = !spaceBefore && !!prev && OPERAND_LEFT.test(prev) && !openingQuote;
    const quotedAlone = /['"`‘“「]/.test(prev) && /['"`’”」]/.test(next);
    // Korean glued to the right of a symbol (">는", ">일 때") or a lone particle after it ("> 로"): the symbol is talked about.
    const particle = (!spaceAfter && /[가-힣]/.test(next) && (!PUNCTUATION.has(token) || PARTICLE_WORD.test(after))) || BARE_PARTICLE.test(after);
    const isolated = (!prev || spaceBefore) && (!next || spaceAfter);
    const punctuation = PUNCTUATION.has(token);
    if (quotedAlone || options.alone) return 'noun';
    // Punctuation is named only when it stands as its own word (";를", "(는"), never inside "COUNT(*)로".
    if (particle && !leftAttached && (!punctuation || ((!prev || spaceBefore) && [':', ';', '(', ')', '()'].includes(token)))) return 'noun';
    if (punctuation) {
      if (token === ':' && (prev === '[' || prev === ',' || next === ']') && !rightOperand) return 'noun';
      if (token === ':' && !leftAttached && !spaceAfter && /[A-Za-z0-9]/.test(next)) return 'prefix';
      if ((token === ':' || token === '::') && leftAttached && /[A-Za-z0-9_^)\]]/.test(prev) && /[A-Za-z0-9_]/.test(next)) return 'expr';
      // A JSON key ("stream":false) reads like the unquoted stream:false a second pass would see.
      if (token === ':' && /[A-Za-z0-9_]["']$/.test(before) && /^["']?[A-Za-z0-9_]/.test(after)) return 'expr';
      if (token === '::' && !spaceAfter && rightOperand) return 'prefix';
      return isolated && token !== "'" && token !== '"' && token !== ':' ? 'noun' : null;
    }
    if (leftAttached && !spaceAfter && /[가-힣]/.test(next) && ['++', '--', '%', '^', '!'].includes(token)) return 'postfix'; // i++는, HEAD^는
    // "60+" (60 and over) is a number with a plus after it, also before a particle: 60+예요.
    if (token === '+' && /(?<![\w.])\d+$/.test(before) && (!next || /[\s가-힣.,)`'"]/.test(next))) return 'postfix';
    // A block follows: "location / {" names the path, it does not divide.
    if (['/', '-', '%', '//'].includes(token) && nextNon === '{') return 'noun';
    if (leftOperand && rightOperand) {
      // Uneven spacing is a sign, pointer, path or option, not arithmetic: "a -b", "int *p", " /git/x".
      if ((UNARY.has(token) || ['/', '//', '%'].includes(token)) && spaceBefore !== spaceAfter) return spaceBefore ? 'prefix' : 'postfix';
      if (!spaceBefore && !spaceAfter) return ['-', '/', '//', '!'].includes(token) ? null : 'expr';
      // In prose a spaced - or / between words is a dash or "or" ("훈련 / 테스트"); it is arithmetic between
      // code-like operands or next to a bracket: "(오늘 - 어제) / 어제".
      const codeLike = /[A-Za-z0-9_)\]]/.test(prevNon) && /[A-Za-z0-9_(]/.test(nextNon);
      if (['-', '/', '%', '//'].includes(token) && !options.code && !codeLike && prevNon !== ')' && nextNon !== '(') return null;
      return 'expr';
    }
    if (!leftOperand && rightOperand) {
      if (!spaceAfter) return 'prefix';
      return COMPARISON.has(token) ? 'expr' : 'noun';
    }
    if (leftOperand && !rightOperand) return spaceBefore ? 'noun' : 'postfix';
    return 'noun';
  }
  function spokenToken(token, kind, s, offset, options) {
    const shellName = pickName(token, options.shell);
    const [expr, noun = expr] = OPS[token];
    const after = s.slice(offset + token.length);
    if (kind === 'noun') return shellName || noun;
    if (kind === 'expr') return shellName || (token === ':' ? '콜론' : expr);
    if (kind === 'prefix') {
      if (token === '-' || token === '+') return /^\d/.test(after) && !options.shell ? noun : null;
      if (token === '%') return /^(?:[a-z]\b|\{)/.test(after) ? '퍼센트' : null; // printf %d, curl %{http_code}
      if (token === '--' || token === '/' || token === '//' || token === '^') return null;
      if (token === '!') return '낫';
      if (COMPARISON.has(token) || token === '=' || token === '==' || token === '!=') return shellName || expr;
      return shellName || noun;
    }
    if (kind === 'postfix') return ['+', '++', '--', '%', '^', '*', '&', '->', '='].includes(token) ? (token === '%' ? '퍼센트' : token === '=' ? expr : noun) : null;
    return null;
  }
  function symbolTokens(text, options) {
    return text.replace(TOKEN, (token, offset, s) => {
      // Inside a double-quoted shell argument (psql -c "… stock > 0") a symbol is the quoted language's, not a redirection.
      const quotedArgument = options.shell && (s.slice(0, offset).match(/"/g) || []).length % 2 === 1;
      const tokenOptions = quotedArgument ? { ...options, shell: false } : options;
      const kind = classify(token, s, offset, tokenOptions);
      const spoken = kind && spokenToken(token, kind, s, offset, tokenOptions);
      // A symbol quoted on its own (')') keeps its quotes tight, so dropping the quotes adds no space.
      const quoted = /['"`‘“「]/.test(s.charAt(offset - 1)) && /['"`’”」]/.test(s.charAt(offset + token.length))
        && !/\w/.test(s.charAt(offset - 2)) && !/\w/.test(s.charAt(offset + token.length + 1));
      const padded = spoken && (quoted ? spoken : pad(spoken, s.slice(0, offset), s.slice(offset + token.length), kind === 'postfix' ? 'noun' : kind));
      return spoken ? (/[가-힣]$/.test(padded) ? padded + JOSA_MARK : padded) : token;
    });
  }
  function symbolSpeechText(input, options = {}) {
    const code = !!options.code;
    // Callers that already translated the command word pass shell: true.
    const shell = !!options.shell || (code ? SHELL_START.test(input) || !!options.shellHint && /^\s*(?:>>?|<)\s*$/.test(input) : !!options.shellHint);
    const alone = code && /^[^\w가-힣\s]+$/.test(input.trim());
    const convert = segment => {
      let text = segment
        .replace(/([<>=])\1{3,}/g, run => ' ' + RUN_NAMES[run[0]] + ' ' + (COUNT[run.length] || String(run.length)) + ' 개 ')
        .replace(/(?<![\w<])<(\/?)([a-z][a-z0-9-]*)((?:\s+[\w:-]+(?:=(?:"[^"]*"|'[^']*'|[^\s"'<>]+))?)*)\s*\/?>/g, (tag, close, name, attrs, offset, s) => !HTML_TAGS.has(name) ? tag
          : ' ' + (close ? '닫는 ' : '') + name + attrs + ' 태그' + (PARTICLE.test(s.slice(offset + tag.length)) ? '' : ' '))
        // A placeholder in angle brackets (<값>, <unset>, <branch>) is read as its word; HTML tags are named above.
        .replace(/(?<![\w<])<([가-힣][\w가-힣 -]*|[a-z][\w-]*)>(?![=>])/g, '$1')
        .replace(/<([\w/]+\.h(?:pp)?)>/g, '$1');
      // The Java diamond (new ArrayList<>()) is silent, like the type arguments it stands for.
      text = text.replace(/([A-Za-z_][\w.]*)<>(?=\s*\()/g, '$1');
      // Generic type arguments, innermost first: Map<String, List<Integer>> → Map String, List Integer.
      for (let i = 0; i < 3; i++) text = text.replace(/([A-Za-z_][\w.]*)<([A-Z?][\w.?]*(?:(?:\s*,\s*|\s+)[A-Z?][\w.?]*)*)>/g, '$1 $2');
      text = text
        .replace(/(?<![\w<])<([A-Z]\w*(?:\s*,\s*[A-Z]\w*)*)>(?!=)/g, '$1')
        .replace(/(?<![\w./])\/(\d{1,2})(?![\w./])/g, ' 슬래시 $1')
        .replace(/([A-Za-z0-9_)\]]+)( *)\*\*\2([A-Za-z0-9_]+)/g, '$1의 $3 제곱')
        .replace(/(\d)>&(\d)/g, ' $1 꺾쇠 앰퍼샌드 $2 ')
        .replace(/(^|\s):([a-z]+)!(?=[\s가-힣.,?]|$)/g, '$1콜론 $2 느낌표') // Vim :q!
        .replace(/(?<![<>=\-!])(>>|>|<)(?![<>=])(?=\s*\S)/g, (token, _same, offset, s) => {
          if (!FILE_TARGET.test(s.slice(offset + token.length))) return token;
          return pad(SHELL_OPS[token], s.slice(0, offset), s.slice(offset + token.length));
        });
      return symbolTokens(text, { code, shell, alone });
    };
    // URLs are spoken as written; only the text around them is converted.
    let result = '', last = 0;
    for (const match of input.matchAll(URL_PATTERN)) {
      result += convert(input.slice(last, match.index)) + match[0];
      last = match.index + match[0].length;
    }
    return (result + convert(input.slice(last))).replace(/[ \t]{2,}/g, ' ');
  }
  // Prose that reached us HTML-escaped (once or twice) or with Markdown escapes is spoken as its characters.
  function decodeEntities(text) {
    const named = { gt: '>', lt: '<', amp: '&', quot: '"', apos: "'", '#39': "'", '#x27': "'", '#34': '"', '#62': '>', '#60': '<' };
    for (let i = 0; i < 2; i++) text = text.replace(/&(gt|lt|amp|quot|apos|#39|#x27|#34|#62|#60);/g, (_, name) => named[name]);
    return text;
  }
  // Markdown bullets, blockquote marks and **bold** are layout, not speech (C pointers such as **pp stay).
  // A leading ">" is a quote mark only before ordinary Korean text; "> 0으로", "> 로", "> 기호",
  // "> memo.txt" keep it as the comparison or redirection being talked about.
  const stripMarkdown = text => text
    .replace(/(^|\n)[ \t]*[-*+][ \t]+/g, '$1')
    .replace(/(^|\n)[ \t]*>[ \t]+(?=[가-힣*`])(?!(?:으로|이에요|예요|는|은|를|을|로|와|과|가|이|도|만|에|의)(?:[\s.,?!]|$))(?!(?:기호|부호|연산자|표시|꺾쇠))/g, '$1')
    .replace(/\*\*(?=[^\s*])([^*\n]+?)(?<=\S)\*\*(?![\w*])/g, '$1');
  const unescapeMarkdown = text => text.replace(/\\([\\`*_{}[\]()#+\-.!<>|~=])/g, '$1');
  // A particle right after the symbol stays attached to its name ("−를" → 빼기를).
  const mathSymbolText = text => text.replace(/[×÷−±≤≥≠≈→←↔∞√]/g, (s, offset, all) =>
    ' ' + symbols[s] + (PARTICLE_WORD.test(all.slice(offset + 1).replace(/^['"’”]/, '')) ? JOSA_MARK : ' '));
  function mathSpeechText(input, options = {}) {
    return mathSymbolText(symbolSpeechText(numberSpeechText(input), options)).replace(/[ \t]{2,}/g, ' ');
  }

  // ---- Files, quotes, brands ----
  // File names: "main.py" read as a word is garbled ("마이노파이"), so the dot is spoken and the
  // extension is named. Applied to code spans too, since file names mostly sit in backticks.
  const extensions = table('extension');
  const filePattern = new RegExp('\\b([A-Za-z_][\\w-]*)\\.(' + Object.keys(extensions).join('|') + ')(?![\\w.])', 'g');
  const gitDirectoryPattern = /(?<![A-Za-z0-9_./\\@-])\.git(?![A-Za-z0-9_./\\@-])/gi;
  // A Java file's stem is a class name (Main.java, out/Main.class). A stem that is a whole lexicon word
  // reads as that word (nginx.conf → 엔진엑스 점 콘프, as the stem would read on its own); others stay as written.
  const fileStem = (stem, ext) => ((ext === 'java' || ext === 'class') && javaClasses[stem])
    || (has(strictTable, stem) && strictTable[stem]) || (/^git(?:hub)?$/i.test(stem) && brandPronunciations[stem.toLowerCase()]) || stem;
  // An extension or dot-file named on its own (".java를 붙이지 않아요", ".practice 파일") says its dot.
  const dotNamePattern = /(?<=^|[\s`'"(\[「])\.([A-Za-z][\w-]*)(?![\w./\\])/g;
  const fileSpeechText = input => input.replace(gitDirectoryPattern, '깃')
    .replace(filePattern, (_, stem, ext) => fileStem(stem, ext) + ' 점 ' + extensions[ext] + JOSA_MARK)
    .replace(dotNamePattern, (_, name) => '점 ' + (extensions[name] ? extensions[name] + JOSA_MARK : name));
  // Quotes around a token are read as a prime by the Edge voice ('30000' → "삼만분"), so the
  // spoken text drops them: the caption keeps the written form.
  const quotedToken = /(['"])([^'"\n]{1,60})\1/g;
  // Nested quotes (f'{row['name']}') are dropped from the inside out.
  const unquote = input => {
    for (let i = 0, last; i < 3 && last !== input; i++) { last = input; input = input.replace(quotedToken, '$2'); }
    return input;
  };
  // An empty string literal ('' or "") in code is named; left as two quotes it would be heard as a prime.
  const emptyStringText = code => code.replace(/(?<![\w'"])(['"])\1(?![\w'"])/g, '빈 문자열');
  // Brands are case-insensitive in prose. Paths, domains and longer identifiers stay intact.
  const brandPattern = /(?<![A-Za-z0-9_./\\@-])(github|git)(?![A-Za-z0-9_./\\@-])/gi;
  const brandText = text => text.replace(brandPattern, term => brandPronunciations[term.toLowerCase()] + JOSA_MARK);
  const strictText = text => text.replace(strictPattern, (_, term) => strictTable[term] + JOSA_MARK);

  const has = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
  // Owner's readings (2026-10-30): the parent folder `..` on its own is said "점점" (cd ..; a path such as
  // ../memo.txt stays as written, like every path) and the option `-a` is said "대시에이" (ls -a,
  // git commit -a). Only the standalone tokens: a range such as 1..10, an ellipsis ... and longer
  // options (-al, --all) keep their other readings. Runs before the symbol rules.
  const ownerTokenText = text => text
    .replace(/(?<![.\w\/])\.\.(?![.\w\/\\])/g, '점점' + JOSA_MARK)
    .replace(/(?<![\w-])-a(?![\w-])/g, '대시에이' + JOSA_MARK);
  const termText = text => text.replace(termPattern, (_, term) => termTable[term] + JOSA_MARK);
  // Numbers in code, with dates, versions and times kept as in prose.
  const codeNumberText = text => text.split(protectedSpans).map((part, index) => (index % 2 ? part : numberSpeechText(part))).join('');
  function codeSpeechText(text, shellHint) {
    const fence = text.startsWith('``') ? 2 : 1;
    const code = fence === 2 ? text.slice(2, -2).trim() : text.slice(1, -1);
    if (/^git(?:hub)?$/i.test(code)) return brandPronunciations[code.toLowerCase()] + JOSA_MARK;
    if (has(strictTable, code)) return strictTable[code] + JOSA_MARK;
    if (has(javaClasses, code)) return javaClasses[code] + JOSA_MARK;
    // Code-specific readings first: command words where a command starts, subcommands, Java class
    // arguments, and symbols read with code context (shell redirection, options).
    const commands = vimText(javaClassText(subcommandText(ownerTokenText(code))))
      .replace(commandPattern, (_, lead, command) => lead + commandWords[command] + JOSA_MARK)
      .replace(/^(\s*(?:\$\s+)?)git(?=\s|$)/i, (_, space) => space + brandPronunciations.git);
    const shell = SHELL_START.test(code);
    // Then the same word readings as prose, with the same whole-token boundaries (identifiers such as
    // print_total, paths and file names keep their letters). A word reads the same in backticks and
    // in prose, and speaking the result again changes nothing.
    const spoken = outsideUrls(commands, part => termText(fileSpeechText(brandText(strictText(
      mathSymbolText(codeNumberText(symbolSpeechText(part, { code: true, shellHint, shell }))))))));
    // Quotes are dropped within this span only, so a quote never pairs with one in another span.
    return unquote(emptyStringText(spoken)).replace(/[ \t]{2,}/g, ' ');
  }
  function proseSpeechText(text, shellHint) {
    return outsideUrls(unescapeMarkdown(decodeEntities(text)), part => {
      const words = strictText(subcommandText(javaClassText(vimText(ownerTokenText(part)))));
      return termText(fileSpeechText(brandText(mathSpeechText(words, { shellHint }))));
    });
  }
  // URLs are spoken exactly as written; every rule runs on the text around them.
  function outsideUrls(text, convert) {
    let result = '', last = 0;
    for (const match of text.matchAll(URL_PATTERN)) {
      result += convert(text.slice(last, match.index)) + match[0];
      last = match.index + match[0].length;
    }
    return result + convert(text.slice(last));
  }
  // Korean particles follow the spoken word: authors write them for the symbol or the English word
  // (":는", "rm로"); after "콜론", "알엠" the voice needs "콜론은", "알엠으로". Only a particle glued to a
  // replaced word and ending a word is changed.
  const JOSA_PAIRS = [['이에요', '예요'], ['으로', '로'], ['은', '는'], ['을', '를'], ['이', '가'], ['과', '와']];
  function agreeParticles(text) {
    return text.replace(new RegExp('([가-힣])' + JOSA_MARK + '(이에요|예요|으로|로|은|는|을|를|이|가|과|와)(?![가-힣])', 'g'), (_, last, particle) => {
      const final = (last.charCodeAt(0) - 0xAC00) % 28;
      const [consonant, vowel] = JOSA_PAIRS.find(pair => pair.includes(particle));
      return last + (consonant === '으로' ? (final === 0 || final === 8 ? vowel : consonant) : final ? consonant : vowel);
    }).replaceAll(JOSA_MARK, '');
  }
  function pronunciationText(text) {
    const source = suppressAliases(stripMarkdown(String(text)));
    const shellHint = SHELL_HINT.test(source);
    // Code spans and dates are converted on their own; the sentence around them is converted in one
    // piece with a placeholder operand in their place, so "(`X`)는" keeps its ")" silent.
    const spans = [];
    const prose = source.split(protectedSpans).map((part, index) => {
      if (!(index % 2)) return part;
      spans.push(part.startsWith('`') ? codeSpeechText(part, shellHint) : fileSpeechText(part));
      return String.fromCharCode(SPAN_BASE + spans.length - 1);
    }).join('');
    const spoken = unquote(proseSpeechText(prose, shellHint)).replace(SPAN_MARKS, mark => spans[mark.charCodeAt(0) - SPAN_BASE] ?? mark);
    return agreeParticles(spoken).replace(/[ \t]{2,}/g, ' ')
      // Padding added around a spoken symbol never adds space at the very start or end.
      .replace(/^ (?=\S)/, /^\s/.test(text) ? ' ' : '').replace(/(?<=\S) $/, /\s$/.test(text) ? ' ' : '');
  }

  // Exported helpers return finished speech text (particles agreed, no internal marks).
  globalThis.molipPronunciation = Object.freeze({
    LEXICON, pronunciations, brandPronunciations, pronunciationText, formatPrices,
    fileSpeechText: input => agreeParticles(fileSpeechText(input)),
    mathSpeechText: (input, options) => agreeParticles(mathSpeechText(input, options)),
    symbolSpeechText: (input, options) => agreeParticles(symbolSpeechText(input, options)),
  });
})();
