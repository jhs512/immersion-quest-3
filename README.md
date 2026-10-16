# 몰입 퀘스트 3

기본 과정은 **자바 기초 · JDK 25**예요. 앱을 열고 **학습 시작 · 이어하기**를 누르면 자바 과정으로 들어가요. 기존 금융 데이터 분석 과정은 사이드바의 **기존 샘플 · 금융 데이터 분석**에서 열 수 있어요. 아래 원본 안내와 기존 수업 파일은 보존했어요.

## 자바 기초 과정

3챕터 · 12단원 · 39미션이에요. 코딩 문제는 15개예요. 객체 단원에서 생성자, 두 객체, 참조 공유, static 필드를 직접 비교해요. 마지막 도전은 배열·객체·생성자·메서드를 함께 사용해요. 복습 퀴즈는 총 24문항이에요.

| 챕터 | 단원 |
| --- | --- |
| 자바의 첫걸음 | 출력, 변수와 자료형, 몫과 나머지, 입력 |
| 조건과 반복 | if, for와 누적, while과 종료 조건, 배열 |
| 값을 묶고 동작 나누기 | 메서드, 문자열 비교, 클래스와 객체, 점수 요약 도전 |

코딩 미션은 `Main.java`를 편집하고 **코드 실행**으로 출력부터 확인해요. **제출**은 다른 입력도 검사해요. 실패하면 입력·예상 출력·실제 출력·오류를 보여 줘요. **정답과 풀이 보기**에는 주석을 넣은 정답 코드가 있어요. 개념과 퀴즈는 틀린 문항을 다시 풀 수 있어요. 완료 기록과 작성 코드는 이 컴퓨터에 저장해요. 자바와 기존 샘플의 과정 ID는 달라요.

## 자바 실행 준비

JDK **25**를 설치하세요. 다른 주 버전은 자바 미션 실행에서 거부해요. `java --version`과 `javac --version`으로 확인하세요. 앱의 **환경 진단 · JDK 25**는 버전 확인 뒤 작은 소스를 실제로 컴파일하고 실행해요.

앱은 `MOLIP_JAVA` 실행 파일 경로, `JAVA_HOME/bin/java`, PATH의 `java` 순으로 찾아요. 실행마다 임시 폴더에서 `java --source 25 Main.java`를 사용해요. preview 옵션은 사용하지 않아요. 입력과 출력은 UTF-8이에요. 입력·코드는 각각 64KB 이하, 출력은 스트림별 64KB 이하이며 실행 제한은 20초예요. 실습 코드는 로컬 사용자 권한으로 실행돼요.

```powershell
java --version
javac --version
cargo build --locked --bin molip-quest
.\target\debug\molip-quest.exe
```

JDK 설치를 앱에서 자동으로 수행하지는 않아요. [Temurin JDK 25](https://adoptium.net/temurin/releases/?version=25)에서 준비할 수 있어요. 문법과 실행 방식은 [JDK 25 java 명령 문서](https://docs.oracle.com/en/java/javase/25/docs/specs/man/java.html), 입력 처리는 [JDK 25 Scanner 문서](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Scanner.html)를 기준으로 확인했어요.

## 콘텐츠 생성과 검사

자바 과정의 제작 원본은 `tools/build-java-course.py`와 `tools/java_strengthening.py`예요. 개념·예제·주석 있는 정답·입출력 검사·해설을 함께 관리해요. 생성 결과는 `courses/java-basics.json`이며 단원 원본 해시는 `courses/java-basics.sources.json`에 남겨요. `python tools/narrate.py --java`는 바뀐 자바 코딩 해설만 다시 만들어요. 캐시는 `tools/java_course/narration_cache/`에 원본 해시와 함께 남겨요.

메서드·객체 문제는 입출력 검사와 실행 계약을 함께 사용해요. 자바 컴파일러가 찾은 메서드 본문이나 참조 초기화를 바꿔 다시 실행해요. 출력이 그대로면 실제 풀이에서 그 개념을 사용했는지 확인해요. 주석이나 사용하지 않는 메서드를 넣는 것만으로는 통과할 수 없어요. 이 검사는 지정된 API와 예제 실행에 대한 검사예요. 모든 자바 프로그램의 의미를 증명하지는 않아요. 강화한 기존 코딩 미션은 revision 2로 다시 풀도록 기록을 구분해요.

```powershell
python tools/build-java-course.py --verify
cargo test --locked --lib --test java_basics
npm.cmd ci --prefix assets/editor
node -e "require('./assets/editor/node_modules/esbuild').buildSync({entryPoints:['assets/editor/editor.js'],bundle:true,minify:true,format:'iife',outfile:'assets/editor/editor.bundle.js',nodePaths:['assets/editor/node_modules']})"
```

`--verify`는 예제 12개와 정답 입력 사례 46개를 실제 실행해요. Rust 검사는 정상 답안과 개념을 생략한 편법 답안, 39미션의 저장 후 재열기, 기존 샘플 진도 분리를 확인해요. Windows UI 검사는 별도 임시 데이터와 WebView 프로필에서 모든 새 해설의 코드 조각을 재생해요.

```powershell
npm.cmd install --prefix target/ui-tests playwright-core --no-audit --no-fund
node tests/ui-java-smoke.cjs
```

`MOLIP_COURSE_PATH`로 다른 과정 JSON을 지정할 수 있어요. `MOLIP_DATA_DIR`는 별도 로컬 저장 위치를 지정해요. Android는 기존 방식대로 코딩 미션 열람만 지원해요. Firebase 연결과 데이터 이전은 이번 변경에 포함하지 않았어요.

## 보존된 원본 안내

아래는 기존 몰입 퀘스트 KPC 과정의 안내예요. 기본 자바 과정에는 위 실행 방법을 적용하세요. 아래 설치·배포 링크는 원본 프로젝트를 가리켜요.

### 몰입 퀘스트 KPC 금융 데이터 분석

KPC 「머신러닝을 활용한 금융데이터 분석」 수업 전용 Rust + Dioxus 설치형 앱입니다. 7개 챕터·20개 단원·148개 미션을 순서대로 클리어합니다. 로그인·AI 연결 없이 로컬 Python과 SQLite로 학습하며, 필요한 데이터와 HTML은 앱에 포함되어 있습니다. 환경 준비 후 학습에는 인터넷이 필요하지 않습니다.

## 학습 기능

main에 커밋이 올라갈 때마다 GitHub Releases에 **Windows x64 설치 EXE·macOS Apple Silicon DMG·Android APK** 세 파일이 자동으로 첨부됩니다. Android는 코드 실행 없이 개념·퀴즈를 풀고 코딩 미션은 읽고 넘어가는 열람 모드입니다. 설치 방법과 서명·검증 상태는 [릴리즈 문서](docs/releases.md)를 확인하세요.

- 단원마다 개념·코딩 미션·퀴즈의 수와 순서를 다르게 배치 (개념 반복, 문제 중심, 중간 퀴즈 등)
- 개념마다 단답형 확인 문제 정확히 한 개, 정답이면 클리어
- 객관식·단답형 혼합 퀴즈, 맞힌 문항 유지 및 오답만 재도전
- 한글·영문·약어 복수 인정 답안, 공백·영문 대소문자 처리
- 모든 단원과 미션으로 자유롭게 이동해 미리 보기. 클리어는 제출 통과·퀴즈 정답으로만 기록되고, 단원은 아직 클리어하지 않은 첫 미션에서 이어짐
- 단원 진도 막대는 미션별 칸: 클리어한 칸은 채워지고 지금 보는 칸은 테두리로 구분되며, 칸을 누르면 그 미션으로 이동
- 자료 보기: 문제가 쓰는 data/ 파일마다 버튼이 생기고, CSV·Excel은 앞 100행 표로, HTML은 원문으로 전체 화면에서 확인
- 단계적 시각화(explorable explanation): 빈 그림에서 "다음 단계"마다 요소가 하나씩 더해지고 슬라이더로 직접 움직여 보는 위젯. 트리 깊이와 과적합(훈련·테스트 오차), 기준값(정밀도·재현율·비용), 시간 분리(테스트 구간과 경계 하루), 층화 분할(다시 나누기·stratify 토글), 누수(구명보트 열 토글과 시점), MAE(오차 막대 쌓기), 이동평균(창 크기), 히스토그램(구간 수)
- 자료의 열 이름과 범주 값은 한글(객실등급·생존·성별·나이·요금 …, 신용한도·상환_9월·다음달 부도, 날짜·종가·거래량). 변수 이름과 함수는 영어 그대로이고, 그래프의 한글은 실행 환경이 글꼴을 골라 줌
- main.py 하나로 푸는 독립 코딩 문제 105개, 실행과 자동 검사
- 챕터마다 마지막에 ★ 도전 과제 1개: 그 챕터의 기술을 전부 써야 풀리는 독립 문제(빵 공장 생산 계획표, 크루아상 판매 기록 정리, 가족 동반 생존, 한 장에 두 그림, 네 모델 비교, 기준값과 비용, 창을 바꾼 재실험)
- 개념·문제·슬라이드 안의 1~3컷 만화 50편 (Comic Gen YAML, 내장 SDK로 오프라인 렌더링). 흐름·순서가 핵심인 곳은 컷 안에 머메이드 다이어그램(내장 Mermaid)
- 「표에서 고르기」 퀴즈 13벌 43문항: 타이타닉·신용카드·주가·빵 공장 자료에서 뽑은 실제 표를 띄우고 행이나 열을 체크해 답한다. 타깃 열 고르기, 사고 뒤에 채워지는(누수) 열과 사람마다 다 다른 열 빼기, 빈칸 있는 열과 글자 열 가려내기, 비율의 분모와 분자 행, 그래프 질문에 필요한 열, 입력 X 일곱 열 고르기, 생존·사망을 같은 수로 뽑기(stratify), 정답이 빈 행 가려내기, 예측과 정답을 맞대 놓고 맞힌 행·놓친 행, 확률 표에서 기준값 0.3으로 가르기, 시간 경계에서 훈련·테스트·버리는 하루 가르기. 각 단원의 첫 개념 바로 뒤에 들어가 코드보다 눈을 먼저 훈련한다. 틀리면 어느 조건이 어긋났는지 먼저 알려 준다
- 인터넷이 필요한 미션 둘: 위키백과 KOSPI 문서의 연도별 종가 표를 requests·BeautifulSoup으로 긁어 가장 많이 오른 해를 찾는 크롤링 미션(2-3), FinanceDataReader로 지금 삼성전자 시세를 받아 마지막 종가와 5일 평균을 구하는 미션(7-1, yfinance도 가능). 숫자가 날마다 바뀌므로 검사는 표의 모양(열, 행 수, 날짜 범위, 값의 일관성)을 본다. 학습 환경에 requests·finance-datareader·yfinance가 들어가고 환경 진단이 셋을 확인한다
- 자동 업데이트(Windows·macOS): 앱이 GitHub Releases의 최신 빌드와 자기 빌드 번호를 비교한다. 시작할 때 새 빌드가 있으면 묻지 않고 받아서 설치하고 다시 열고, 실행 중에 새 빌드가 나오면 상단 배너로 알린다(지금 업데이트 / 나중에). 설치 파일은 앱이 직접 받으므로 맥에서도 격리 경고 없이 열린다. 사이드바에 빌드 번호가 보이고, 개발 빌드는 확인하지 않는다 (`docs/development.md`)
- 번호: 챕터 `1.`, 단원 `1-1`, 미션 `1-1-1`을 빌드가 제목 앞에 붙인다. 목차, 미션 띠, 모아보기, AI 문맥에 같은 번호가 보인다
- 퀴즈 167문항 중 40문항은 "프롬프트 고르기": 상황과 후보 프롬프트 4개, 해설은 보기마다 왜 아닌지를 적음. 모든 객관식 해설에 "다른 보기는 왜 아닌가"
- 강사용 슬라이드 덱 30벌 (Marp Markdown, 내장 Marp Core로 오프라인 렌더링). 덱마다 중심 주제 하나, 장마다 메시지 하나이고, 교시마다 그 교시의 개념을 여는 덱이 있다. 장마다 강사 스크립트(강사의 말투로 쓴 2~4문장)가 Marp 발표자 노트로 붙어 있어 슬라이드에서 우클릭(또는 「스크립트」 버튼, N 키)하면 그 장의 대사와 다음 장 첫 문장이 뜬다. 첫 덱: 왜 3일을 배우나(AI 시대의 데이터 분석과 비용 절감 사례), 표는 왜 pandas로(2차원 리스트와의 차이, NumPy가 빠른 이유, 콘다가 필요했던 시절), 머신러닝은 표에서 규칙 찾기, 기준·과적합·모델 저장, 시간은 섞지 않는다. 이전·다음·전체 화면, 마지막 장까지 보면 미션 완료. 슬라이드 안에도 만화·머메이드·그림이 들어감
- 하이퍼파라미터 튜닝(파라미터는 공부 내용, 하이퍼파라미터는 공부법. 교차 검증으로 max_depth 고르기, AutoML 소개)과 한 번 만든 모델을 `joblib`으로 저장하고 불러와 다시 쓰는 개념·미션 (2일차 6교시)
- 클래스룸 첫 화면의 모아보기 4종: PPT·만화·발전적 시각화·개념(문제·퀴즈 제외). 각각 제목 목록이 먼저 나오고, 제목을 누르면 그 내용이 열리며 이전·다음으로 넘어감. PPT는 덱 뷰어 그대로(이전·다음 장, 전체 화면)
- 글꼴 내장: 본문 Pretendard, 코드 JetBrains Mono (`assets/fonts/`, base64로 앱에 포함). 창 메뉴 막대 없음
- 경험치와 레벨: 미션 종류와 상관없이(코딩, 퀴즈, 개념 확인, 슬라이드) 완료마다 100 XP, 500 XP마다 레벨 업. 정답 카드의 XP 막대와 불꽃, 레벨업 때 아바타가 바뀌는 연출과 효과음(Web Audio로 합성, 파일 없음)이 있고, 홈의 「애니메이션」「효과음」 버튼으로 끄고 켠다(`prefs.json`에 저장). 앱 설정이 OS의 '동작 줄이기'보다 우선한다.
- 「AI에게 물어보기」 핵심 훑기: `/tour-all`을 치면 미션마다 핵심 1~3문장만 말하고 답을 넣어 끝낸 뒤 다음 미션으로 넘어가며 과정 끝까지 갑니다(`/auto-all`의 빠른 판. 문장은 빌드 때 해설에서 뽑은 `courses/*.json`의 `tour`). Space로 일시정지, Esc나 「해제」로 멈춥니다.
- 「AI에게 물어보기」 해설 모드: `/auto`를 치면 지금 미션을 설명하며 풀어 줍니다. 미션마다 해설 대본이 빌드 때 미리 컴파일되어 있어(`courses/*.json`의 `narration`, 출처는 `tools/kpc_course/narration_*.py`와 덱의 강사 스크립트·퀴즈 해설) 기다림 없이 바로 시작하고 대본이 패널에 먼저 뜹니다. 개념은 설명하는 문단·코드·만화로 화면을 천천히 내려가며 비춥니다. 대본이 없는 미션만 AI가 즉석에서 만듭니다. 건드리는 곳(문제, 예제, 에디터, 실행·제출 버튼, 결과, 퀴즈 보기)에 보라색 표시와 말풍선이 뜨고, 코드는 한 글자씩 입력되며, Edge 자연 음성(선히·인준·현수, 설정에서 선택)이 읽어 줍니다. `/auto-all`은 지금부터 과정 끝까지 미션마다 이어서 진행하는 교육 영상 같은 모드이고 Esc나 「해제」로 멈춥니다. 본문 더블 클릭 읽어주기도 같은 음성을 씁니다.
- 「AI에게 물어보기」(학습 화면 상단): 지금 보는 미션의 내용(슬라이드 전체, 개념 본문, 문제·힌트·학생이 쓴 코드, 퀴즈 문항)과 대화를 한 프롬프트로 묶어, 이 컴퓨터에 설치·로그인된 Claude Code(`claude -p`, 기본) 또는 Codex CLI(`codex exec -o`)에 묻는 조교 챗봇. API 키 없음. 오버레이 창에 대화·대화 지우기·다시 시도·설정(답하는 쪽과 명령 이름, `assistant.json`에 저장). 정답을 통째로 주지 않고 힌트 위주로 답하도록 지시. "해 줘"라고 부탁하면 답 끝에 동작 목록(코드 넣기·실행·제출·퀴즈 답 선택과 채점·이전/다음·슬라이드 넘기기)을 붙이고 앱이 그대로 실행한 뒤 결과를 돌려줘, 통과할 때까지 최대 네 번 스스로 고쳐 다시 시도(`assets/layout/agent.js`)
- 한글 입력 보호: 입력창·텍스트 영역의 값 쓰기를 IME 조합 중에는 건너뛰어(`assets/layout/ime.js`) 안녕이 안ㄴ녕으로 깨지지 않음. 앱의 모든 입력창에 공통 적용
- 단축키 한 벌(Windows는 Ctrl, 맥은 ⌘): Ctrl+←/→ 이전·다음 단계, Ctrl+↑/↓ 이전·다음 단원, Ctrl+K 목차, Ctrl+I AI 창, Ctrl+Enter 실행(두 번 연타 제출), Ctrl+Shift+Enter 제출, Enter 주관식 채점, Space 해설 일시정지, Esc 해제·정지, Ctrl+/ 전체 단축키 안내 창(`assets/layout/shortcuts.js`). 글자 입력 칸과 코드 편집기 안에서는 편집 키 의미를 지킨다
- 앱은 시작부터 전체 화면. F11(맥 ⌃⌘F)로 전환, 첫 화면에 단축키 안내. 슬라이드의 「전체 화면」은 발표 모드: 화면 전부를 덱이 쓰고 마우스를 움직일 때만 하단에 조작 바가 나타나며 Esc로 나감
- 본문을 Ctrl(맥 ⌘)+더블 클릭하면 그 문단부터 미션 끝까지 읽어 주는 한국어 음성 (Esc로 정지, 한 번 더 누르면 창이 닫힘) (기기의 ko-KR 음성 사용, 속도 조절·일시정지)
- 표·그래프 출력과 오류 피드백, 코드·답안·결과·진도 로컬 저장
- 프롬프트 복사 · 인간 버전: 문제마다 손으로 쓴, 사람이 실제로 치는 2~5줄 프롬프트(`tools/kpc_course/prompts.py`). 분석가의 용어(stratify, temporal split, 누수, 기준선 …)가 답을 바꾸는 자리에만 들어가고 "코드만 줘"로 끝남
- 프롬프트 복사 · 기계 버전: 같은 요청을 최소 명세로 쓴 것. 과제, 출력 형식, (실제 코드가 있을 때만) 기본 코드, 지금 쓴 코드, 예시, 채점 조건만
- 프롬프트 해설: 전체 화면 레이어. 인간 버전의 어떤 단어가 왜 들어갔는지, 이 단원에서 AI에게 꼭 말해야 하는 것, 짧게 쓰는 요령, 기계 버전과의 차이. 앱은 AI를 호출하지 않음
- 코딩 화면의 문제/코드, 편집기/실행 결과 사이 드래그 핸들 (더블 클릭으로 초기화, 크기는 기기에 저장)
- 제출 정답 팝업과 다음 미션 자동 이동, 이전·다음 복습 (단원 간 이동 포함)
- 코드 실행에 예제 입력을 기본 제공, 입력값을 바꿔 연습 가능
- Markdown 설명·문항·해설, Python 코드 블록 색상 표시
- CodeMirror 6 코드 편집기
- Python·수업 패키지 환경 진단, 그리고 「환경 설치」 한 번으로 OS에 맞는 학습 환경(uv + Python 3.13 + 수업 패키지) 재설치

각 실행은 새 프로세스와 별도 작업 폴더에서 시작합니다. data/titanic.csv, data/credit.csv, data/stock.csv, data/prices.html은 매번 원본으로 준비하므로 이전 문제의 변수·파일·수정에 의존하지 않습니다. Jupyter Notebook은 사용하지 않습니다.

범용 수업 플랫폼이나 중앙 서버를 제공하지 않습니다. 이전 서버 기반 명세·티켓은 과거 결정 기록이며 현재 KPC 설계는 `.scratch/kpc-learning/`에 있습니다.

## 설치 및 실행

### 설치 파일로 설치 (학생용)

main의 모든 커밋이 [GitHub Releases](https://github.com/jhs512/molip-quest/releases/latest)에 Windows·macOS·Android 설치 파일을 올립니다. 자세한 내용은 `docs/releases.md`에 있습니다.

- **macOS (Apple Silicon)**: 터미널에 아래 한 줄을 붙여 넣습니다. 최신 앱을 `/Applications`에 넣고 학습용 Python 환경(pandas·scikit-learn 등)까지 만든 뒤 앱을 엽니다. 이렇게 받은 앱에는 격리 속성이 없어 Gatekeeper의 "열지 않음" 창이 뜨지 않습니다. DMG를 직접 받았다면 안에 든 `먼저 읽어 주세요.txt`를 따릅니다.

  ```bash
  curl -fsSL https://raw.githubusercontent.com/jhs512/molip-quest/main/packaging/macos/install.sh | bash
  ```

- **Windows**: `molip-quest-windows-x64-setup.exe`를 실행합니다. Python은 아래 Windows 절차의 uv 명령으로 따로 준비하고, 앱의 「환경 진단」으로 확인합니다.

### 소스에서 빌드

아래는 **소스에서 빌드하는 설치 방법**입니다. 비공개 저장소라 복제하려면 GitHub 접근 권한이 필요합니다. 최초 도구·패키지 다운로드와 빌드에는 인터넷이 필요하지만, 준비가 끝난 앱의 학습 기능은 인터넷 없이 동작합니다. uv는 Python 환경을 준비하기 위한 도구이며 앱 실행 자체의 필수 구성요소는 아닙니다.

### macOS (터미널)

이미 설치한 도구는 건너뜁니다. Homebrew가 없다면 다음 공식 설치 명령을 실행하고 안내를 따릅니다. 이 명령은 필요한 Xcode 명령줄 도구 설치도 안내합니다.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Homebrew를 PATH에 등록합니다. Apple Silicon과 Intel 설치 위치를 자동으로 구분합니다. 설치 안내에 다른 경로가 표시됐다면 그 안내를 따릅니다.

```bash
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi
brew install git uv
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

Homebrew가 지원하지 않는 구형 macOS에서는 [uv 공식 독립 설치](https://docs.astral.sh/uv/getting-started/installation/)를 사용합니다: `curl -LsSf https://astral.sh/uv/install.sh | sh`. 현재 Homebrew 지원 범위는 [공식 안내](https://brew.sh/)를 확인합니다.

터미널을 다시 연 뒤 저장소와 Python 실습 환경을 준비하고 앱을 빌드합니다.

```bash
git clone https://github.com/jhs512/molip-quest.git
cd molip-quest
uv python install 3.13
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -r requirements-learning.txt
cargo build --release --locked --bin molip-quest
export MOLIP_PYTHON="$PWD/.venv/bin/python"
./target/release/molip-quest
```

다음 실행부터는 저장소 폴더에서 마지막 두 명령만 실행하면 됩니다. `MOLIP_PYTHON`을 두지 않으면 앱은 한 줄 설치가 만든 `ml-env`, 그다음 로그인 셸이 아는 `python3` 순으로 찾습니다.

### Windows (PowerShell)

Git, Rust 빌드 도구, Rust, uv를 준비합니다. 설치 중 관리자 권한 요청이나 재시작 안내가 나오면 완료한 뒤 이어서 진행합니다. `winget`이 없다면 Microsoft의 [앱 설치 관리자](https://learn.microsoft.com/windows/package-manager/winget/)를 먼저 설치합니다.

```powershell
winget install --id Git.Git --exact
winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
winget install --id Rustlang.Rustup --exact
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

WebView2가 없는 PC에서는 다음 명령도 실행합니다.

```powershell
winget install --id Microsoft.EdgeWebView2Runtime --exact
```

PowerShell을 다시 연 뒤 저장소와 Python 실습 환경을 준비하고 앱을 빌드합니다.

```powershell
rustup default stable
git clone https://github.com/jhs512/molip-quest.git
cd molip-quest
uv python install 3.13
uv venv .venv --python 3.13
uv pip install --python .venv/Scripts/python.exe -r requirements-learning.txt
cargo build --release --locked --bin molip-quest
$env:MOLIP_PYTHON = Join-Path (Get-Location) '.venv/Scripts/python.exe'
./target/release/molip-quest.exe
```

다음 실행부터는 저장소 폴더에서 마지막 두 명령만 실행하면 됩니다. Python 경로 설정은 현재 터미널에 적용되므로 새 터미널에서는 다시 설정합니다.

Python이 이미 준비돼 있다면 `MOLIP_PYTHON`을 해당 실행 파일의 경로로 설정하여 사용할 수 있습니다. 기본 입출력 문제는 Python만으로 풀 수 있고, 표·그래프·ML 수업은 `requirements-learning.txt`의 실습 패키지를 사용합니다. 이 KPC 과정은 전체 패키지를 처음 한 번에 준비하며 문제별 설치는 없습니다. 환경 진단 버튼으로 준비 상태를 확인합니다. AI 해설 모드의 자연스러운 한국어 음성(선히·인준·현수)은 앱이 Microsoft Edge의 읽어 주기 서비스에서 직접 받아 오므로 패키지가 필요 없고 인터넷만 있으면 됩니다. 오프라인이면 기기 음성으로 읽습니다.

설치 명령 참고: [Homebrew 설치](https://brew.sh/), [Rust 설치](https://www.rust-lang.org/tools/install), [Windows Rust 빌드 도구](https://learn.microsoft.com/windows/dev-environment/rust/setup), [uv 설치](https://docs.astral.sh/uv/getting-started/installation/), [Dioxus 데스크톱 준비](https://dioxuslabs.com/learn/0.7/getting_started/).

### 개발 실행

```powershell
cargo run --bin molip-quest
```

Windows 데모 실행은 `cargo build --bin molip-quest` 이후 `./scripts/start-demo.ps1`로도 가능합니다.

## 수업과 저장

기본 수업은 `courses/kpc-finance.json`입니다. `MOLIP_COURSE_PATH`로 다른 JSON 수업 파일을 선택할 수 있습니다. 파일을 불러오지 못하면 오류를 표시합니다. 저장 위치는 OS별 사용자 앱 데이터 폴더의 MolipQuest이며 코드 초안은 drafts.sqlite3, 실행 검사·완료 기록은 learning.sqlite3에 보관합니다.

단원의 `activities`는 순서가 있는 미션 배열입니다. `concept`는 설명과 단답형 `check` 한 개, `coding`은 독립된 `problem`, `quiz`는 `questions` 배열, `slides`는 Marp `markdown`을 담습니다. 단답형은 `accepted` 배열로 여러 인정 답안을 등록합니다.

코딩 문제의 `tests`는 input·expected 배열입니다. `blanks`는 starter_code의 {{name}} 자리만 수정하도록 지정합니다. `checker`는 학생 파일 경로를 첫 번째 인자로 받는 Python 코드입니다. 성공 종료는 통과, AssertionError 또는 종료 상태 1은 오답, 다른 예외나 종료 상태는 검사 오류입니다. 본질적으로 변경한 단원의 revision을 올리면 이전 완료가 현재 진도로 집계되지 않고 기존 검사 기록은 보존됩니다.

## 환경 진단

환경 진단 버튼은 Python 실행, pandas·matplotlib·seaborn·scikit-learn·openpyxl·BeautifulSoup 설치를 확인합니다. 모든 수업이 모든 패키지를 필요로 하는 것은 아닙니다.

- `MOLIP_PYTHON`: Python 실행 파일 경로

## 검증

```powershell
cargo fmt --check
cargo test
```

실제 Python 실행·입출력·사용자 정의 검사·표와 그래프·로컬 저장과 함께 개념 확인, 20문항 혼합 퀴즈 누적 정답·재시작·프롬프트를 검사합니다. 제공 코딩 문제 102개는 각각 참조 답안으로 독립 실행·검사합니다. 읽어주기의 문장 분할·발음 변환·재생 제어는 `node --test assets/speech/speech.test.mjs`로 검사합니다.

콘텐츠를 수정할 때는 `python tools/build-kpc-course.py`로 과정 및 참조 답안을 재생성합니다. 학생용 화면은 참조 답안을 자동으로 표시하지 않습니다.

현재 Windows 11에서 개발 실행을 확인했습니다. Windows 10은 Rust 및 WebView2 지원 대상이지만 이 앱의 실기기 검증은 남아 있습니다. macOS 실행·설치 패키지 검증도 아직 완료하지 않았습니다.
