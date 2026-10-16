"""Coverage before content: prerequisites, exam domains and observable outcomes."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AICE_SOURCES=['https://aice.study/info/aice/asso','https://aice.study/certi/examGuide','https://aice.study/certi/practice','https://www.aice.team/guidebook']
ENGINEER_SOURCES=['https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=991','https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=1453']
ENGINEER_DOMAINS={
 'E01':'요구사항 확인','E02':'데이터 입출력 구현','E03':'통합 구현','E04':'서버프로그램 구현',
 'E05':'인터페이스 구현','E06':'화면 설계','E07':'애플리케이션 테스트 관리','E08':'SQL 응용',
 'E09':'소프트웨어 개발 보안 구축','E10':'프로그래밍 언어 활용','E11':'응용 SW 기초 기술 활용','E12':'제품소프트웨어 패키징'}
AICE_DOMAINS={'A00':'출발점과 시험 환경','A01':'데이터 분석','A02':'데이터 전처리','A03':'모델링·평가·개선'}


def unit(id,title,domains,topics,evidence,prerequisites=None):
    return dict(id=id,title=title,domains=domains.split(),topics=topics.split('|'),evidence=evidence,
                prerequisites=prerequisites, status='planned',required=True,
                learning_loop=['관찰·예상','실행·변화 확인','작은 수정','새 자료·입력','선택 도전'],
                production_gate=['선수 개념 먼저 소개','독립 실행 자료','실제 정답 검사','준비 코드와 대표 오답 거부','실제 출력 해설','새 입력 전이'])


def build():
    aice=[
      unit('aice-python-first','분석을 시작하는 Python 첫 실행','A00','출력|따옴표|계산|변수|실행 순서','표 분석을 시작하기 전에 코드의 값과 이름을 작은 수정으로 구별한다.'),
      unit('aice-python-values','분석 코드의 값·목록·자리','A00','숫자/글자 변환|실수 나눗셈|리스트|인덱스|딕셔너리|len|비교','작은 분석 자료의 값과 목록을 고르고 간단한 조건을 계산한다.'),
      unit('aice-data-first','처음 만나는 코드와 데이터 표','A01','CSV 준비 코드|행·열|head|열 선택|shape','새 표에서도 앞부분과 필요한 열을 고르고 크기를 읽는다.'),
      unit('aice-python-tools','분석 코드를 읽고 이어 쓰기','A00','함수·인자|반환값|import|오류 메시지|문자열 메서드','API 예시의 인자와 반환값을 이해해 한 줄을 고친다.'),
      unit('aice-data-types','CSV를 읽고 자료형 점검하기','A01 A02','read_csv|info|dtypes|to_numeric|astype|열 이름|저장 경로','숫자로 읽히지 않은 열을 찾아 변환하고 파일을 다시 읽는다.'),
      unit('aice-data-join','여러 파일을 읽어 하나의 표로','A01 A02','read_json|merge on·how|concat|키 자료형 맞추기|병합 뒤 행 수 확인','키와 결합 방식이 바뀌어도 병합 결과의 행 수와 빈칸을 설명한다.'),
      unit('aice-row-conditions','조건으로 원하는 기록 고르기','A01','비교 결과|참/거짓|행 필터|경계값|두 조건|loc/iloc','여러 조건과 경계값을 포함한 표를 정확히 선택한다.'),
      unit('aice-data-summary','개수·분포·그룹별 비교','A01','describe|count|value_counts|합계/평균/중앙값|groupby|정렬','분모와 자료 수를 구별하여 질문에 맞는 요약을 만든다.'),
      unit('aice-visualization','그래프로 분포와 관계 확인하기','A01','축·단위|막대|히스토그램|상자그림|산점도|상관·히트맵','질문에 맞는 그래프와 읽을 수 있는 축을 구성한다.'),
      unit('aice-data-quality','빈칸·중복·이상치 진단하기','A02','isna|중복|삭제/대체|분포·중앙값|이상치 기준','자료가 바뀌어도 처리 근거와 행 수 변화가 맞는다.'),
      unit('aice-target-features','입력 X와 정답 y 정하기','A02 A03','회귀/분류|타깃|drop|입력 열|정답 누수','예측 시점에 알 수 있는 정보만 입력으로 선택한다.'),
      unit('aice-data-split','훈련·검증·테스트를 구분하기','A02 A03','train_test_split|random_state|stratify|분할 비율|시간순 자료','분리된 인덱스의 겹침과 클래스 비율을 실제로 검사한다.'),
      unit('aice-encoding','범주를 모델 입력으로 바꾸기','A02','라벨 인코딩|원핫|순서 인코딩|훈련/테스트 열 정렬|미지 범주','새 범주가 있는 테스트 자료에도 입력 열 구성이 일치한다.'),
      unit('aice-scaling','훈련 자료로만 변환 기준 익히기','A02','fit/transform|StandardScaler|RobustScaler|누수 방지','테스트 값이 바뀌어도 훈련 기준이 바뀌지 않는다.'),
      unit('aice-regression','숫자를 예측하는 기준과 모델','A03','평균 기준|fit/predict|선형회귀|결정트리|RandomForest|MAE/RMSE','고정 숫자가 아니라 예측 배열과 실제 지표 계산을 검사한다.'),
      unit('aice-classification','종류를 예측하고 오류 읽기','A03','기준 분류|로지스틱/트리/RF|accuracy|혼동행렬|정밀도·재현율','클래스 불균형에서 정확도만 높은 오답을 진단한다.'),
      unit('aice-model-improvement','공정하게 모델을 비교하고 개선하기','A03','과적합|검증|하이퍼파라미터|GridSearchCV|교차검증|특성 중요도','테스트 자료를 튜닝에 쓰지 않고 새 검증 결과를 비교한다.'),
      unit('aice-xgboost','XGBoost로 회귀·분류하기','A03','XGBRegressor/XGBClassifier|n_estimators·learning_rate·max_depth|objective 지정|특성 중요도|다른 모델과 같은 잣대로 비교','같은 분할에서 XGBoost를 학습·평가하고 다른 모델과 공정하게 비교한다.'),
      unit('aice-neural-network','신경망의 입력·출력 맞추기','A03','TensorFlow/Keras|Dense|활성화|입력 차원|회귀/이진/다중 분류 출력|손실함수','출력 크기·활성화·정답 형식·손실함수의 조합을 실제 검사한다.'),
      unit('aice-training-control','학습 곡선과 일반화 개선하기','A03','compile/fit|epoch/batch|validation|Dropout|EarlyStopping|학습 곡선','학습을 실제 수행하고 과적합 징후와 중단 시점을 해석한다.'),
      unit('aice-regression-project','회귀 분석을 처음부터 끝까지','A01 A02 A03','새 합성 자료|탐색→전처리→분리→모델→평가|저장·재실행','빈 환경에서 전체 분석을 재실행하고 예측·지표·파일을 검사한다.'),
      unit('aice-classification-project','분류 분석을 처음부터 끝까지','A01 A02 A03','다른 합성 자료|ML/딥러닝 비교|클래스별 오류|모델 개선','앞 프로젝트의 숫자를 외워 풀 수 없는 자료로 완성한다.'),
      unit('aice-exam-workflow','노트북·파일·제한적 참고자료 사용','A00','라이브러리 설치·불러오기|한글 폰트 셀|셀 순서|커널 재시작|전체 재실행|CSV 파일명|참고자료 규정','공식 환경 안내를 따라 셀 의존성과 제출 파일을 점검한다.'),
      unit('aice-mock-a','자체 실전 모의 A','A01 A02 A03','90분|14문항|현재 기준 30/30/40|힌트 없는 평가','처음 보는 자료의 독립 답안과 결과물을 제한 시간 안에 만든다.'),
      unit('aice-mock-b','자체 실전 모의 B','A01 A02 A03','독립 문항·자료|다른 문제 순서|회귀/분류 전이','앞 모의의 정답 코드를 그대로 재사용하면 통과하지 못한다.'),
      unit('aice-mock-c','자체 실전 모의 C·약점 재확인','A01 A02 A03','독립 문항·자료|딥러닝 개선|약점별 새 문제','힌트 없이 연속 모의 성적과 약점 재평가 결과를 확인한다.'),
    ]
    engineer=[
      unit('engineer-program-first','출력·변수·대입을 처음 읽어요','E10','프로그램·출력|실행 순서|숫자/글자|int|변수|대입','한 줄씩 실행되는 코드에서 값의 변화를 읽고 확인한다.'),
      unit('engineer-java-first','자바의 값과 연산 규칙','E10','int/double·정수 나눗셈|나머지 %|문자열 연결 순서|복합 대입·증감|형 변환·char','준비 값을 바꾼 코드에서도 자료형과 연산 순서로 출력을 예측한다.'),
      unit('engineer-control-first','조건·반복·함수의 공통 원리','E10','조건 경계|AND/OR|반복|누적|인자·반환|호출 순서','중간 상태표와 최종 결과를 새 입력으로 확인한다.'),
      unit('engineer-java-objects','자바의 객체·상속·호출','E10','생성자|this/super|오버로딩/오버라이딩|static|접근 제어','실제 객체 타입·참조 타입·호출 대상을 구별한다.'),
      unit('engineer-java-state','자바 실행 원리의 혼합 연습','E10','참조·복사|정수 나눗셈|문자열 비교|재귀|조건·반복','앞에서 배운 원리를 혼합한 준비 코드를 수정한다.'),
      unit('engineer-c-first','C의 값·배열·문자열','E10','printf|정수 연산|배열|문자열 끝|조건·반복','C 실행 환경과 문법을 명시하고 정의된 동작만 정답으로 쓴다.'),
      unit('engineer-c-memory','C의 주소·포인터·구조체','E10','주소/역참조|포인터 연산|배열과 포인터|구조체|전달 방식','그림의 주소 관계와 코드 결과를 대응한다.'),
      unit('engineer-c-calls','C의 함수 포인터·재귀','E10','호출 스택|재귀 종료|함수 포인터|배열 인자','여러 원리가 섞인 짧은 코드의 결과와 호출 순서를 푼다.'),
      unit('engineer-python-collections','파이썬의 목록·복사·반복','E10','슬라이싱|얕은/깊은 복사|함수 인자|컬렉션|문자열|예외','같은 자료를 공유하는 이름과 독립 복사를 구분한다.'),
      unit('engineer-language-written','세 언어의 필답 결과·빈칸 연습','E10','C/Java/Python|출력·빈칸|상태표|실행 후 확인과 시험 모드','새 문제는 답을 먼저 적고 제출 전 실행·힌트 없이 푼다.'),
      unit('engineer-db-model','관계·키·제약조건·정규화','E02 E11','ERD|관계 모델|키|함수 종속|정규화|관계대수','작은 테이블의 이상 현상을 보고 키와 분해 결과를 적는다.'),
      unit('engineer-sql-first','SQL 조회·조건·정렬의 첫 실험','E08 E11','SELECT/FROM/WHERE|별칭|DISTINCT|ORDER BY|NULL','표와 중간 행을 비교하고 새 자료에서도 같은 질의를 작성한다.'),
      unit('engineer-sql-join','조인·집계·서브쿼리','E08','INNER/OUTER JOIN|GROUP BY/HAVING|집계·NULL|EXISTS|서브쿼리','중복·빈칸·없는 행이 포함된 결과를 정확히 구한다.'),
      unit('engineer-db-storage','논리·물리 저장소와 성능','E02','자료형·제약|테이블/인덱스|저장 공간|프로시저 연결·읽기·쓰기|병목 측정','논리 설계를 실제 저장 구조로 바꾸고 비용 차이를 비교한다.'),
      unit('engineer-sql-procedural','DDL·DML·DCL·절차형 SQL','E02 E08','DDL/DML/DCL/TCL|트랜잭션|윈도우·그룹 함수|프로시저|사용자 정의함수|트리거|권한','명시한 SQL 방언에서 실행하고 필답 빈칸·문장으로 전이한다.'),
      unit('engineer-requirements','현행 시스템과 요구사항','E01','개발 방법론|플랫폼/기술 타당성|기능/비기능|요구 도출·분석·검증|분석 모델','짧은 사례의 요구와 검증 누락을 구별한다.'),
      unit('engineer-design','설계·모듈·객체 모델','E01 E04','UML|설계 패턴|공통 모듈|응집/결합|업무 프로세스','구조를 조금 바꾸어 어떤 설계 성질이 달라지는지 판단한다.'),
      unit('engineer-server-batch','개발 환경·서버·배치 구현','E04 E11','도구·서버 설정|형상관리|업무 모듈|배치|예외·보안·테스트','설정·업무 순서·단위 테스트의 결함을 찾아 고친다.'),
      unit('engineer-integration','연계 데이터와 송수신','E03','연계 요구|데이터 표준|EAI/ESB|송수신 주기|실패 복구|무결성|보안','명세와 메시지·실패 사례를 연결한다.'),
      unit('engineer-interface','인터페이스 명세·구현·검증','E05','XML/JSON|인터페이스 표준|공통 기능|예외·보안|감시|결함 보고','주어진 명세와 응답의 불일치를 확인한다.'),
      unit('engineer-ui','화면 요구와 흐름 설계','E06','UI/UX 원칙|표준·지침|프로토타입|화면/폼 흐름|메뉴|제약','짧은 화면 사례에서 요구 위배와 올바른 흐름을 적는다.'),
      unit('engineer-testing','테스트 설계·통합·성능 개선','E07','동등/경계|구조 기반·커버리지|수준·통합|결함 추이|시작/종료|성능·품질','입력 구간과 상태 그림에서 테스트 자료·기대 결과를 만든다.'),
      unit('engineer-security','보안 설계와 안전한 구현','E09','보안 요구|접근 제어|인증|암호·해시|입력 검증|취약점·대응|결함 관리','교육용 국소 사례에서 취약점 이름과 방어 수정안을 대응한다.'),
      unit('engineer-os','운영체제·프로세스·메모리','E11','OS·기본 명령|프로세스·스레드|스케줄링|교착|페이징|우선순위','작은 시간표와 메모리 상태를 계산하고 근거를 확인한다.'),
      unit('engineer-network','네트워크·주소·프로토콜','E11','계층|TCP/UDP|IP·서브넷|라우팅|패킷 교환|프로토콜','주소 범위·전송 절차를 새 숫자로 풀어 확인한다.'),
      unit('engineer-packaging','패키징·배포·매뉴얼·버전','E12','빌드|설치/배포|릴리즈 노트|DRM·저작권|설치/사용 매뉴얼|버전·백업','변경 이력과 패키지·릴리즈 기록을 연결한다.'),
      unit('engineer-written-mix','전 영역 혼합 필답과 약점 진단','E01 E02 E03 E04 E05 E06 E07 E08 E09 E10 E11 E12','출력|SQL 작성|용어·빈칸|계산|유사 개념 구분','실행·힌트 없이 답한 후 분야별 오답 원인을 분류한다.'),
      unit('engineer-mock-a','자체 실전 모의 A','E01 E02 E03 E04 E05 E06 E07 E08 E09 E10 E11 E12','150분|자체 구성 20문항|필답|수험 조건','첫 독립 모의를 풀고 정확한 답·오답 분류를 남긴다.'),
      unit('engineer-mock-b','자체 실전 모의 B','E01 E02 E03 E04 E05 E06 E07 E08 E09 E10 E11 E12','독립 문항|다른 언어/SQL·이론 조합|필답','수치·보기만 바꾼 복제가 아닌 새 문제에서 원리를 적용한다.'),
      unit('engineer-mock-c','자체 실전 모의 C·취약 영역 재검사','E01 E02 E03 E04 E05 E06 E07 E08 E09 E10 E11 E12','독립 문항|시간 배분|새 약점 문제','재응시에서 외운 답이 아닌 새로운 문제로 준비도를 판단한다.'),
    ]
    # Sequential recommendations are metadata; the player still permits free lesson choice.
    for items in [aice,engineer]:
        for i,item in enumerate(items):
            if item['prerequisites'] is None:item['prerequisites']=[] if i==0 else [items[i-1]['id']]
        ids=[x['id'] for x in items]
        assert len(ids)==len(set(ids))
        for i,item in enumerate(items):assert all(p in ids[:i] for p in item['prerequisites'])
    courses=[dict(id='aice-associate',title='에이스 Associate',domains=AICE_DOMAINS,sources=AICE_SOURCES,
        exam=dict(format='Python 실기',minutes=90,questions=14,pass_score=80,weights={'A01':30,'A02':30,'A03':40}),
        readiness=dict(kind='자체 학습 기준·공식 합격 조건과 구분',independent_mocks=3,target_score=90,requires_all_domains=True),lessons=aice),
      dict(id='engineer-practical',title='정보처리기사 실기',domains=ENGINEER_DOMAINS,sources=ENGINEER_SOURCES,
        exam=dict(format='필답형',minutes=150,pass_score=60,criteria=['2026','2027–2029']),
        readiness=dict(kind='자체 학습 기준·공식 합격 조건과 구분',independent_mocks=3,target_score=80,requires_all_domains=True),lessons=engineer)]
    for course in courses:
        covered={d for item in course['lessons'] for d in item['domains']}
        assert set(course['domains'])<=covered
        for item in course['lessons']:
            path=ROOT/'target/certification-foundations'/item['id']/'lesson.json'
            pilot={'aice-data-first':'aice-associate','engineer-java-state':'engineer-practical'}.get(item['id'])
            if not path.exists() and pilot:path=ROOT/'target/certification-pilots'/pilot/'lesson.json'
            if path.exists():
                content=json.loads(path.read_text(encoding='utf8'))
                item.update(status='implemented',task_count=len(content['tasks']),revision=content['revision'])
    return dict(schema_version=1,verified_on='2026-10-16',goal='다른 교재 없이 두 시험을 준비할 수 있는 전체 과정',
        rules=['초보자에게 필요한 선수 지식을 생략하지 않기','읽기보다 작은 실습과 문제로 배우기','도전은 배운 원리의 조합','전체 범위와 실제 구현 상태를 구분','복습모드는 수업별 선택','필답 연습과 실행 실습을 구분','모의 문항·자료는 자체 제작'],courses=courses)


def write():
    plan=build()
    path=ROOT/'courses/certification-roadmaps.json'
    path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    for course in plan['courses']:
        print(f"PLAN {course['id']}: {len(course['lessons'])} lessons; {len(course['domains'])} mapped domains",flush=True)
    return plan


if __name__=='__main__':write()
