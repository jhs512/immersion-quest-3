# 표·그래프와 환경 진단

`scripts/setup-learning.ps1`을 실행하면 프로젝트 안에 학습용 Python 환경을 만듭니다. 운영 앱은 `MOLIP_PYTHON`에 해당 환경의 Python 실행 파일을 지정합니다. 개발 빌드는 프로젝트의 `target/ml-env` 환경을 자동으로 찾습니다.

실행 결과에 pandas DataFrame과 Series를 그리드로 표시합니다. 마지막 표현식, `display(df)` 호출, 변수에 저장된 DataFrame을 지원합니다. 최대 100행·30열 미리보기이며 전체 크기도 표시합니다. SQL DB 접속 관리 화면은 포함하지 않습니다.

matplotlib와 seaborn 그래프는 실행 결과의 이미지로 표시합니다. `plt.show()`와 실행 종료 시 남은 figure를 수집합니다. 최대 8개 그래프를 표시하며 일반 텍스트 출력과 에러도 함께 유지합니다. 실행 제한은 60초입니다.

**환경 진단**에서 Python, pandas, matplotlib, seaborn, scikit-learn, TensorFlow, openpyxl, BeautifulSoup, requests, FinanceDataReader, yfinance, Claude CLI 설치와 Claude 로그인 여부를 확인합니다. 그 옆의 **환경 설치**는 이 컴퓨터에 맞게 학습 환경을 처음부터 다시 만듭니다: uv가 없으면 astral.sh에서 받고(Windows는 PowerShell, macOS는 sh), 앱 데이터 폴더의 `ml-env`를 지우고 Python 3.13으로 새로 만든 뒤 `requirements-learning.txt`(실행 파일에 포함)를 설치합니다. 진행 로그가 패널에 흐르고 끝나면 진단을 다시 돌립니다. 개발 빌드는 저장소의 `target/ml-env`를 우선 쓰므로 설치 결과는 릴리스 빌드에서 쓰입니다. 인터넷이 필요한 미션은 둘입니다: 위키백과 KOSPI 표 크롤링(2-3)과 FinanceDataReader 실시간 시세(7-1). 검사는 값이 아니라 표의 모양을 봅니다. Claude 로그인 여부는 호출 가능 잔여량이나 모델 사용 권한을 보장하지 않습니다.

## C 실행 (저장소형 수업)

수업 문제의 `language`가 `c`이면 `main.c`를 실행합니다. Windows는 GNU Savannah의 TinyCC 0.9.27 공식 zip(sha256 `34a721949a2583fdff725312da092fa0f5f1f284b702e6f811c6954714faabb2`)을 처음 실행 때 앱 데이터 폴더의 `course-tools`에 받아 시스템 `tar.exe`로 풀고, `tcc -run main.c`로 메모리에서 컴파일·실행합니다(실행 파일을 쓰지 않음, 15초 제한). macOS·Linux는 `cc -std=c11`로 컴파일한 뒤 실행합니다. `MOLIP_TCC`·`MOLIP_CC`로 컴파일러를 바꿀 수 있습니다. 웹 미리보기는 C를 실행하지 않습니다.

채점은 `tests`의 입력·기대 출력을 비교합니다(입력은 stdin). 선택적으로 `variations`([{values: {변수명: C 리터럴}, expected}])를 주면 모든 tests를 통과한 뒤 각 변수의 첫 선언 초기값을 바꿔 다시 실행해 외운 출력을 거부합니다. 바꿀 선언이 사라졌으면 "준비 코드의 … 선언과 처음 값은 그대로 두세요."로 실패합니다. 저작 도구는 `tools/certification_course/kit.py`의 `c_task`, 빌드 실행은 `tools/principles_course/common.py`의 `execute`(같은 TinyCC 사용)입니다. 정의되지 않은 동작이나 주소 숫자 자체를 기대 출력으로 쓰지 않습니다.
