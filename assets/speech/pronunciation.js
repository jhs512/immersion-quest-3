// Central speech-only pronunciation policy. See docs/voice.md.
// Shared by narration and reading, for neural and device voices.
// Never use this output for captions, source code, answers or terminal input.
(function () {
  'use strict';
  if (globalThis.molipPronunciation) return;
  // ---- Pronunciation: exact technical terms from the course, spoken text only. ----
  const pronunciations = Object.freeze({
    Python: '파이썬', python: '파이썬', pandas: '판다스', DataFrame: '데이터프레임', Series: '시리즈',
    NumPy: '넘파이', numpy: '넘파이', matplotlib: '맷플롯립', seaborn: '시본', sklearn: '에스케이런',
    'scikit-learn': '사이킷런', Pipeline: '파이프라인', Titanic: '타이타닉', titanic: '타이타닉',
    KPC: '케이피씨', AI: '에이아이', CSV: '씨에스브이', HTML: '에이치티엠엘', Excel: '엑셀', JSON: '제이슨',
    SQLite: '에스큐엘라이트', URL: '유알엘', MAE: '엠에이이', RMSE: '알엠에스이', 'R²': '알 제곱', R2: '알 제곱',
    F1: '에프원', ID: '아이디', IDE: '아이디이', API: '에이피아이', OS: '오에스', PC: '피씨', GUI: '지유아이',
    'One-hot': '원핫', 'one-hot': '원핫', Ridge: '릿지', Lasso: '라쏘', fit: '핏', predict: '프리딕트',
    int: '인트', str: '스트링', float: '플로트', bool: '불', list: '리스트', dict: '딕트', None: '넌',
    True: '트루', False: '폴스', print: '프린트', input: '인풋', split: '스플릿', map: '맵', len: '렌',
    sum: '섬', round: '라운드', append: '어펜드', import: '임포트', main: '메인', py: '파이',
    if: '이프', else: '엘스', for: '포', in: '인', def: '데프', return: '리턴', lambda: '람다',
    groupby: '그룹바이', mean: '민', median: '미디언', max: '맥스', min: '민', count: '카운트', shape: '셰이프',
    head: '헤드', tail: '테일', index: '인덱스', columns: '컬럼스', dropna: '드롭엔에이', fillna: '필엔에이',
    isna: '이즈엔에이', sort_values: '소트 밸류스', value_counts: '밸류 카운츠', read_csv: '리드 씨에스브이',
    read_html: '리드 에이치티엠엘', to_numpy: '투 넘파이', pct_change: '퍼센트 체인지', rolling: '롤링', shift: '시프트',
    lag: '래그', target: '타깃', leakage: '리키지', baseline: '베이스라인', accuracy: '애큐러시',
    precision: '프리시전', recall: '리콜', LogisticRegression: '로지스틱 리그레션', DecisionTreeClassifier: '디시전 트리 클래시파이어',
    RandomForestClassifier: '랜덤 포레스트 클래시파이어', DummyClassifier: '더미 클래시파이어', LinearRegression: '리니어 리그레션',
    StandardScaler: '스탠다드 스케일러', OneHotEncoder: '원핫 인코더', SimpleImputer: '심플 임퓨터', ColumnTransformer: '컬럼 트랜스포머',
    train_test_split: '트레인 테스트 스플릿', mean_absolute_error: '민 앱솔루트 에러', accuracy_score: '애큐러시 스코어',
    IndentationError: '인덴테이션 에러', KeyError: '키 에러', TypeError: '타입 에러', ValueError: '밸류 에러',
    NaN: '낸', nan: '낸', EOFError: '이오에프 에러', BeautifulSoup: '뷰티풀 수프', WebView: '웹뷰', Android: '안드로이드',
    // Tools and names the course mentions (the Edge voice spells or mangles these otherwise).
    pip: '핍', conda: '콘다', Anaconda: '아나콘다', Jupyter: '주피터', Notebook: '노트북', notebook: '노트북', wheel: '휠',
    requests: '리퀘스트', Selenium: '셀레니움', selenium: '셀레니움', webdriver: '웹드라이버', Chrome: '크롬', soup: '수프',
    timeout: '타임아웃', headers: '헤더스', select: '셀렉트', select_one: '셀렉트 원', get_text: '겟 텍스트', wikitable: '위키테이블',
    Wikipedia: '위키피디아', KOSPI: '코스피', KOSDAQ: '코스닥', yfinance: '와이 파이낸스', yf: '와이에프', FinanceDataReader: '파이낸스 데이터 리더',
    fdr: '에프디알', DataReader: '데이터 리더', download: '다운로드', Open: '오픈', High: '하이', Low: '로우', Close: '클로즈', Volume: '볼륨',
    Change: '체인지', idxmax: '아이디엑스 맥스', idxmin: '아이디엑스 민', cut: '컷', observed: '옵저브드', joblib: '잡립', VS: '브이에스',
    Code: '코드', wiki: '위키', robots: '로봇츠', URL: '유알엘', http: '에이치티티피', https: '에이치티티피에스', www: '더블유 더블유 더블유',
  });
  const escapeRegExp = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const termPattern = new RegExp(
    '(?<![A-Za-z0-9_])(' + Object.keys(pronunciations).sort((a, b) => b.length - a.length).map(escapeRegExp).join('|') + ')(?![A-Za-z0-9_])',
    'g'
  );
  // Protect code, dates, versions and paths from prose conversion. Code has a narrow Git-command exception below.
  const protectedSpans = /(`[^`\n]+`|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b[vV]\d+(?:\.\d+)+|\b\d+(?:\.\d+){2,}|\b\d{1,2}:\d{2}(?::\d{2})?|[A-Za-z]:\\[^\s]+)/g;
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
  function mathSpeechText(input) {
    return input
      .replace(/(?<![A-Za-z0-9_.,])(\d{1,3}(?:,\d{3})+|\d+)\s*원/g, (_, n) => koreanInteger(n) + ' 원')
      .replace(/(?<![\w.,])(\d{1,3}(?:,\d{3})+)(?![\w.,])/g, (_, n) => koreanInteger(n))
      .replace(/(?<![\d.,])(\d{1,2})번/g, (_, n) => sinoKorean(Number(n)) + '번')
      .replace(/(?<![A-Za-z0-9_])R²/g, '알 제곱')
      .replace(/([A-Za-z0-9])²/g, '$1 제곱').replace(/([A-Za-z0-9])³/g, '$1 세제곱')
      .replace(/(?<![\w.])(\d+)\.(\d+)(?![\w.])/g, (_, whole, fraction) => whole + ' 점 ' + [...fraction].map(d => digits[Number(d)]).join(' '))
      .replace(/(?<![\w.])(\d+(?:,\d{3})*)\s*%/g, '$1 퍼센트')
      .replace(/<=|>=|!=|==|\+=|-=|\*=|\/=/g, s => ' ' + { '<=': '작거나 같다', '>=': '크거나 같다', '!=': '같지 않다', '==': '같다', '+=': '플러스 이퀄', '-=': '마이너스 이퀄', '*=': '곱하기 이퀄', '/=': '나누기 이퀄' }[s] + ' ')
      .replace(/(?<=[\dA-Za-z가-힣)\]])\s*([+*=<>])\s*(?=[\dA-Za-z가-힣(\[])/g, (_, op) => ' ' + { '+': '더하기', '*': '곱하기', '=': '이퀄', '<': '작다', '>': '크다' }[op] + ' ')
      .replace(/(?<=\d)\s*-\s*(?=\d)/g, ' 빼기 ')
      .replace(/(?<![\w./])(\d+)\s*\/\s*(\d+)(?![\w./])/g, '$2분의 $1')
      .replace(/(?<![\w.])-(\d+)/g, '마이너스 $1')
      .replace(/[×÷−±≤≥≠≈→←↔∞√]/g, s => ' ' + symbols[s] + ' ')
      .replace(/[ \t]{2,}/g, ' ');
  }
  // File names: "main.py" read as a word is garbled ("마이노파이"), so the dot is spoken and the
  // extension is named. Applied to code spans too, since file names mostly sit in backticks.
  const extensions = { py: '파이', csv: '씨에스브이', xlsx: '엑셀', xls: '엑셀', html: '에이치티엠엘', json: '제이슨', joblib: '잡립', txt: '텍스트', md: '엠디' };
  const filePattern = /\b([A-Za-z_][\w-]*)\.(py|csv|xlsx|xls|html|json|joblib|txt|md)(?![\w.])/g;
  const gitDirectoryPattern = /(?<![A-Za-z0-9_./\\@-])\.git(?![A-Za-z0-9_./\\@-])/gi;
  const fileSpeechText = input => input.replace(gitDirectoryPattern, '깃').replace(filePattern, (_, stem, ext) => stem + ' 점 ' + extensions[ext]);
  // Quotes around a token are read as a prime by the Edge voice ('30000' → "삼만분"), so the
  // spoken text drops them: the caption keeps the written form.
  const quotedToken = /(['"])([^'"\n]{1,60})\1/g;
  const unquote = input => input.replace(quotedToken, '$2');
  // Brands are case-insensitive in prose. Paths, domains and longer identifiers stay intact.
  const brandPronunciations = Object.freeze({ git: '깃', github: '깃허브' });
  const brandPattern = /(?<![A-Za-z0-9_./\\@-])(github|git)(?![A-Za-z0-9_./\\@-])/gi;
  const brandText = text => text.replace(brandPattern, term => brandPronunciations[term.toLowerCase()]);
  function codeSpeechText(text) {
    const code = text.slice(1, -1);
    if (/^git(?:hub)?$/i.test(code)) return brandPronunciations[code.toLowerCase()];
    // Only the command name is pronounced; arguments, options and file names stay intact.
    return fileSpeechText(code).replace(/^(\s*)git(?=\s|$)/i, (_, space) => space + brandPronunciations.git);
  }
  function pronunciationText(text) {
    return unquote(text.split(protectedSpans).map((part, index) => {
      if (index % 2) return part.startsWith('`') ? codeSpeechText(part) : fileSpeechText(part);
      return fileSpeechText(brandText(mathSpeechText(part))).replace(termPattern, (_, term) => pronunciations[term]);
    }).join(''));
  }

  globalThis.molipPronunciation = Object.freeze({ pronunciations, brandPronunciations, pronunciationText, formatPrices, fileSpeechText, mathSpeechText });
})();
