# AICE 22수업 전체 범위·실행 호환성 근거

확인일: **2026-10-19**, 한국 시간. 목적: 기존 `aice-course-map.md`의22수업을 완성할 때 필요한 공식 범위, API 의미, 로컬 환경 선택 근거를 정리한다. **공식 문서 열람·공개 메타데이터 확인**이며 실제 응시 커널 테스트가 아니다. production 콘텐츠·PRD·실행 코드는 변경하지 않았다. 후보 상황은 자체 설계 메모이며 공식 시험 문제·정답·데이터가 아니다.

## 1. 시험 근거와 확인 수준

- Python 코드 작성 중심 실기이며 일부 결과 단답,14문항·90분·80점 이상 합격. 범위는 정형 데이터 분석·전처리·머신러닝과 딥러닝·평가다. 문서의 분석30/전처리30/모델링40점 표와 과거 공개 샘플 배점은 구별한다. 확인2026-10-19. [공식 가이드북 Associate](https://www.aice.team/guidebook)
- 이번에는 공식사이트 공지 **「AICE Associate 시험 환경 버전 안내(26년8월)」**, 게시일2026-08-18을 실제 Edge에서 열어 **공지 본문과200 API응답을 직접 확인**했다. 이전18일 조사에서 미재확인으로 남긴 환경 표를 이번에는 아래 공식 공개 명세로 확인했다. 확인2026-10-19. [공식 공지](https://aice.study/board/notice/detail/16322), [페이지 자신의 공개 API](https://restapi.ktaidu.kt.co.kr/hub-api/api/v1/board/notice/16322)
- 공지는 오픈북을 아래7개 라이브러리 공식 문서로 제한하고 다른 라이브러리/외부자료 참고를 불허한다. 설치된 모든 패키지 목록이나 추가pip설치 허용 여부를 뜻하지 않는다. 확인2026-10-19. [동일 공식 공지](https://aice.study/board/notice/detail/16322)
- 현재 수험자 가이드의 서버 자원 이미지는 Jupyter Notebook·CPU2코어·16GB를 기재한다. 연결 가이드북의1CPU 표기와 차이가 있다. 이미지는 이전 조사에서 직접 확인했으며 이번에는 새 커널/자원 측정을 하지 않았다. [공식 수험자 가이드](https://aice.study/certi/examGuide), [공식 이미지](https://restapi.ktaidu.kt.co.kr/hub-api/api/v1/files/images/d25dbdcd-c260-4424-9535-d3a205e0e596.png)

| 구성 | 공식8월 공지: 이번 직접 확인 | 가이드북과 비교·한계 |
| --- | --- | --- |
| Python | 3.10.13 | 같은 표기. 실제커널 미실행 |
| NumPy / pandas | 1.23.5 / 1.5.3 | 같은 표기 |
| matplotlib | 3.7.0 | 가이드북은3.7.1. 충돌 보존 |
| seaborn | 0.12.1 | 같은 표기 |
| scikit-learn | 1.3.2 | 가이드북 환경표에는 없음 |
| TensorFlow | 2.13.1 | 같은 표기. 실제Keras 별도 버전 미확인 |
| XGBoost | 0.90 | 환경·공식문서 목록에 있음. 특정 모델 문제가 반드시 출제된다는 뜻은 아님 |
| Jupyter/ipykernel, GPU, 추가패키지 | 미기재/미확인 | 추정 버전이나 GPU 제공을 확정하지 않음 |

표의 확인일은 전부2026-10-19이며 [공식 공지](https://aice.study/board/notice/detail/16322)와 [공식 가이드북](https://www.aice.team/guidebook)을 직접 대조했다. 접수·로그인·시험 세션·결제는 하지 않았다.

## 2. Python3.11 로컬 환경 후보

아래는 **시험과 다른 자체 학습 환경 후보**다. 현재NumPy1.26.4/pandas1.5.3을 유지하되 TensorFlow를 도입할 때 생기는 충돌을 피하기 위한 선택이다. 패키지 설치·모델 실행은 이번 조사에서 수행하지 않았다. 실제 설치 후 `pip check`, 버전 출력, 표처리·sklearn학습·TensorFlow학습·그림·저장/복원 검증이 별도로 필요하다.

| 후보 핀 | 공식 메타데이터에서 확인한 호환 근거 | 출처·확인일 |
| --- | --- | --- |
| Python3.11 x64 + NumPy1.26.4 | NumPy는Python>=3.9, cp311 Windows x64 wheel 존재 | [NumPy1.26.4](https://pypi.org/pypi/numpy/1.26.4/json),2026-10-19 |
| pandas1.5.3 | Python>=3.8, Python3.11에서NumPy>=1.23.2, cp311 Windows wheel 존재 | [pandas1.5.3](https://pypi.org/pypi/pandas/1.5.3/json),2026-10-19 |
| scikit-learn1.3.2 | Python>=3.8, NumPy>=1.17.3,<2, SciPy>=1.5, joblib>=1.1.1, threadpoolctl>=2; cp311 Windows wheel 존재 | [sklearn1.3.2](https://pypi.org/pypi/scikit-learn/1.3.2/json),2026-10-19 |
| SciPy1.11.4 | Python>=3.9, NumPy>=1.21.6,<1.28; cp311 Windows wheel 존재 | [SciPy1.11.4](https://pypi.org/pypi/scipy/1.11.4/json),2026-10-19 |
| matplotlib3.7.1 | Python>=3.8, cp311 Windows wheel 존재. PyPI JSON의 requires_dist는 null이므로 전체 의존성 검증으로 표현하지 않는다. | [matplotlib3.7.1](https://pypi.org/pypi/matplotlib/3.7.1/json),2026-10-19 |
| seaborn0.12.1 | NumPy>=1.17, pandas>=0.25, matplotlib>=3.1 및 !=3.6.1. 범용 wheel 존재. | [seaborn0.12.1](https://pypi.org/pypi/seaborn/0.12.1/json),2026-10-19 |
| TensorFlow2.15.1 | Python>=3.9, NumPy>=1.23.5,<2, Keras>=2.15,<2.16. Windows에서는 tensorflow-intel==2.15.1에 의존하며 둘 다 cp311 Windows wheel 존재. | [TensorFlow2.15.1](https://pypi.org/pypi/tensorflow/2.15.1/json), [tensorflow-intel](https://pypi.org/pypi/tensorflow-intel/2.15.1/json),2026-10-19 |
| joblib1.3.2 / threadpoolctl3.2.0 | Python>=3.7 / >=3.8, 범용 wheel. sklearn1.3.2의 최소 버전을 충족한다. | [joblib](https://pypi.org/pypi/joblib/1.3.2/json), [threadpoolctl](https://pypi.org/pypi/threadpoolctl/3.2.0/json),2026-10-19 |

**충돌 확정:** TensorFlow2.13.1은NumPy>=1.22,<=1.24.3을 요구한다. 따라서 **NumPy1.26.4와TF2.13.1을 한venv에 정상 의존성으로 묶을 수 없다**. `--no-deps`로 억지 설치하는 것은 검증된 호환성을 만들지 않는다. 확인2026-10-19. [공식 TF2.13.1 메타데이터](https://pypi.org/pypi/tensorflow/2.13.1/json)

TensorFlow 공식 설치 안내는Windows native GPU 지원의 마지막을2.10으로 설명한다.2.15.1 Windows 학습환경은CPU 기준으로 설계하고 GPU필수 실습을 두지 않는 편이 맞다. 확인2026-10-19. [TensorFlow 공식 설치](https://www.tensorflow.org/install/pip)

환경 선택 결론은 조건부다. `tensorflow.keras`와Keras2문서를 기본 근거로 쓰고 독립Keras3 최신 API를 섞지 않는다. 기존 실행 중인venv를 바꾸지 않고 새venv를 검증한다. TF2.15.1후보가 동작해도 **공식 시험커널과 같다고 표시하지 않는다**.

## 3. 22수업 커버리지 매트릭스

아래 연결은 제작자가 정한 자체 분할이다. 공식은 수업22개나 특정 수업명을 지정하지 않는다. 날짜는 모든 행2026-10-19다. 기초1~4수업은 기존Python/pandas 기초 조사와 이어지며 여기서는5~22의 누락을 특히 점검했다.

| 지도 순서 | 다루어야 할 수행·원리 | 작은 비교 상황 후보(자체) | 공식 근거 |
| --- | --- | --- | --- |
| 1 Python 첫걸음 | 이름·리스트·길이·출력 | 표의열이름목록과실제열수비교 | [Python기초 기존조사](aice-python-foundations-2026-10-19.md) |
| 2 조건으로 고르기 | 비교·불리언·짧은반복 | 30이상/30초과 경계1행차이 | [pandas인덱싱](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/indexing.html) |
| 3 자료와 기능 | dict·인자·import·속성/메서드 | 속성shape와호출head구별 | [기초연결 조사](aice-python-bridge-2026-10-19.md) |
| 4 CSV | DataFrame·dtype·파일읽기 | 코드열001을숫자와문자열로읽기 | [pandas기초 조사](aice-pandas-foundations-2026-10-19.md) |
| 5 선택·요약 | loc/iloc,필터,정렬,집계,상관 | 비연속인덱스;결측있는그룹의크기/개수 | [인덱싱](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/indexing.html), [groupby](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.groupby.html) |
| 6 품질 | 결측·중복·이상치와처리영향 | 결측0개/전부결측열;경계이상치;정상극단값 | [missing data](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/missing_data.html) |
| 7 그림 | 분포·빈도·변수관계·축/범례해석 | 범주별개수와평균을혼동한차트비교 | [공식 시각화범위](https://www.aice.team/guidebook) |
| 8 입력과정답 | X/y,범주인코딩,목표제외 | 미래에알수없는열;미지범주;훈련/검증열불일치 | [LabelEncoder](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.LabelEncoder.html), [OneHotEncoder](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.OneHotEncoder.html) |
| 9 자료분리 | 함께분리·반환순서·seed·계층화 | X/y개별shuffle로정답뒤섞임;희소클래스 | [train_test_split](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.train_test_split.html) |
| 10 누수 | 훈련/검증/테스트역할,fit/transform | test에만극단값추가시훈련평균변경감지 | [공식 pitfalls](https://scikit-learn.org/1.3/common_pitfalls.html) |
| 11 스케일 | Standard/Robust의통계기준과순서 | 평균/표준편차와중앙값/IQR;상수열 | [StandardScaler](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.StandardScaler.html), [RobustScaler](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.RobustScaler.html) |
| 12 회귀모델 | 연속목표,fit/predict,기준모델 | 전부평균예측과학습모델;입력1열2차원 | [모델링범위](https://www.aice.team/guidebook), [sklearn평가](https://scikit-learn.org/1.3/modules/model_evaluation.html) |
| 13 회귀평가 | MAE/MSE/RMSE/R²해석 | 오차하나만큰두모델;상수정답R² | [MSE1.3API](https://scikit-learn.org/1.3/modules/generated/sklearn.metrics.mean_squared_error.html), [평가지표](https://scikit-learn.org/1.3/modules/model_evaluation.html) |
| 14 분류모델 | label/proba/classes_와임계값 | classes_가문자열인모델;확률열선택오류 | [GridSearchCV proba/classes_](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.GridSearchCV.html) |
| 15 분류평가 | 혼동행렬·양성의미·precision/recall/F1 | 불량10/정상90에서모두정상예측 | [confusion_matrix](https://scikit-learn.org/1.3/modules/generated/sklearn.metrics.confusion_matrix.html), [classification_report](https://scikit-learn.org/1.3/modules/generated/sklearn.metrics.classification_report.html) |
| 16 모델비교 | 같은분리·같은지표에서트리/RF비교 | train점수1.0인데validation악화 | [모델선택·평가](https://scikit-learn.org/1.3/modules/model_evaluation.html) |
| 17 튜닝 | CV·GridSearchCV·scorer·테스트보호 | neg_MAE의큰값이낮은오차;pipeline내전처리 | [GridSearchCV](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.GridSearchCV.html), [pitfalls](https://scikit-learn.org/1.3/common_pitfalls.html) |
| 18 TF흐름 | Input→Dense→compile→fit→predict | 입력열수와출력행수/열수비교 | [Dense](https://keras.io/2/api/layers/core_layers/dense/), [학습API](https://keras.io/2/api/models/model_training_apis/) |
| 19 NN회귀 | 선형출력·회귀손실·스케일연결 | 음수/100넘는목표에sigmoid출력제약 | [회귀손실](https://keras.io/2/api/losses/regression_losses/), [Dense](https://keras.io/2/api/layers/core_layers/dense/) |
| 20 NN분류 | binary/multiclass·labelshape·loss·output | 3개라벨을1/2/3그대로sparse손실에넣는오류 | [분류손실](https://keras.io/2/api/losses/probabilistic_losses/) |
| 21 학습곡선 | train/val·Dropout·EarlyStopping·저장 | validation_split맨뒤라벨편향;최고epoch와마지막epoch | [학습API](https://keras.io/2/api/models/model_training_apis/), [EarlyStopping](https://keras.io/2/api/callbacks/early_stopping/), [저장](https://keras.io/2/api/models/model_saving_apis/model_saving_and_loading/) |
| 22 통합 | 자체회귀/분류자료의전과정·요구산출물 | 입력CSV순서변경,미지범주,잘못된파일명 | [공식시험 수행범위](https://www.aice.team/guidebook), [pandasmerge](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/merging.html) |

누락점검: JSON/두표결합은 현재22수업 제목에 명시되지 않았다. 필요하면4~5또는22에서 작은연결단원으로 다루되 모든시험필수라고 단정하지 않는다. many-to-many키는행수를증식시키므로 단순행수보존가정을깨는자체경계사례로좋다. 확인2026-10-19. [pandas merging](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/merging.html)

XGBoost는공식환경명세에있어완전히삭제할근거는부족하다. 다만이번22지도는sklearn/TF핵심완성을우선하고XGBoost wrapper의필요범위를16~17확장또는후속으로명시한다. **XGBoost가항상나온다/안나온다**고단정하지않는다. 확인2026-10-19. [공식환경공지](https://aice.study/board/notice/detail/16322)

## 4. API 함정: PRD에 남길 검증 기준

다음은공식API의미다. 각행확인일은2026-10-19. 시나리오는이의미를드러내기위한자체제안이다.

| 주제 | 확인한 의미·함정 | 공식 근거 |
| --- | --- | --- |
| pandas불리언 | Series조건은괄호와`&`/`|`를사용. loc는라벨,iloc는위치. chained assignment는피한다. | [pandas1.5 indexing](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/indexing.html) |
| 결측 | 결측판정은isna/notna. `NaN==NaN`으로찾지않는다. 평균채움이정답인경우에도평균을학습하는모델전처리는훈련자료에서만추정한다. | [missing data](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/missing_data.html), [leakage](https://scikit-learn.org/1.3/common_pitfalls.html) |
| 인코딩 | LabelEncoder는목표y용. OneHotEncoder는입력특성용이며기본미지범주오류,ignore이면해당특성출력모두0.1.3에서는sparse_output이기본True. | [LabelEncoder](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.LabelEncoder.html), [OneHotEncoder](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.OneHotEncoder.html) |
| get_dummies | 1.5기본dtype는np.uint8. 숫자처럼보이는순서없는범주를연속수치로암묵취급하지않는다.훈련/검증을따로더미화할때열이다를수있으므로정렬기준을보존한다(후자는제작상추론). | [get_dummies1.5](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.get_dummies.html) |
| split | 함께넣은X/y는같은행기준으로나뉘며반환순서는Xtrain,Xtest,ytrain,ytest. float test_size는비율,int는행수. random_state정수는분할재현용. shuffle=False는stratify와병행불가. | [train_test_split1.3](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.train_test_split.html) |
| 누수 | 분리후훈련에만fit/fit_transform,검증·테스트에는그기준transform. feature selection/대체/스케일추정에도동일. CV전전체자료fit도누수라pipeline을CV안에둔다. | [pitfalls](https://scikit-learn.org/1.3/common_pitfalls.html) |
| 스케일 | StandardScaler는훈련평균/분산기준,이상치에민감. RobustScaler는중앙값/분위범위기준. 스케일러가이상치를삭제하는것은아니다. | [StandardScaler](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.StandardScaler.html), [RobustScaler](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.RobustScaler.html) |
| 회귀점수 | MAE/MSE는작을수록좋고단위가다름. sklearn1.3의RMSE는MSE(squared=False)로가능. R²는음수가능하고상수정답이면force_finite처리주의. | [평가](https://scikit-learn.org/1.3/modules/model_evaluation.html), [MSE1.3](https://scikit-learn.org/1.3/modules/generated/sklearn.metrics.mean_squared_error.html) |
| 분류점수 | 혼동행렬은실제라벨이행/예측라벨이열. labels순서를명시해양성을보존. macro와weighted평균,0분모정책을구별. | [confusion_matrix](https://scikit-learn.org/1.3/modules/generated/sklearn.metrics.confusion_matrix.html), [classification_report](https://scikit-learn.org/1.3/modules/generated/sklearn.metrics.classification_report.html) |
| 확률 | predict_proba열순서는classes_와대응.두번째열이항상업무상양성이라고암기하지않는다. | [GridSearchCV predict_proba](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.GridSearchCV.html) |
| 탐색 | scorer는대체로큰값우수라손실은neg_접두어. GridSearchCV(refit=True)는선정파라미터로fit에준전체학습자료에재학습. best_score_는테스트성능이아님. | [평가scoring](https://scikit-learn.org/1.3/modules/model_evaluation.html), [GridSearchCV](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.GridSearchCV.html) |
| NN모양 | Dense(units)는출력마지막축을units로만든다. 보통표입력은(batch,features),회귀1출력은(batch,1). squeeze/reshape없이(batch,)정답과연산하면의도치않은broadcast를검토해야한다(검증설계제안). | [Dense](https://keras.io/2/api/layers/core_layers/dense/) |
| binary NN | 0/1정답,1출력sigmoid+binary_crossentropy(from_logits=False). linear logits이면from_logits=True.확률과logit설정을반대로연결하지않는다. | [Keras2분류손실](https://keras.io/2/api/losses/probabilistic_losses/) |
| multiclass NN | 배타적K분류는K출력softmax와정답형식에맞는손실. 정수라벨은SparseCategoricalCrossentropy,원핫은CategoricalCrossentropy. raw라벨/열순서와모델출력인덱스의매핑을기록한다. | [Keras2분류손실](https://keras.io/2/api/losses/probabilistic_losses/) |
| validation_split | 배열입력의마지막비율을shuffle전에분리한다. 계층화랜덤분할이아니다. validation_data가있으면validation_split보다우선한다. | [Keras2 training API](https://keras.io/2/api/models/model_training_apis/) |
| Dropout | 학습시에만확률적으로입력을0으로하고나머지를보정. `trainable=False`로추론동작이되는것이아니며training인자를구별한다. | [Keras2 Dropout](https://keras.io/2/api/layers/regularization_layers/dropout/) |
| EarlyStopping | monitor/min_delta/patience/mode와validation지표존재를확인.기본restore_best_weights=False라최고epoch자동복원이아님.최고가중치복원과파일저장은다르다. | [Keras2 EarlyStopping](https://keras.io/2/api/callbacks/early_stopping/) |
| 저장 | model.save/load_model은모델전체저장/복원.가중치만저장과구별.확장자·save_format·콜백인자지원은Keras버전별확인하며최신Keras3규칙을2.15에그대로옮기지않는다. | [Keras2 saving](https://keras.io/2/api/models/model_saving_apis/model_saving_and_loading/) |

## 5. 완성 판정에 남겨야 할 경계

이 문서는API와범위를조사했지교육효과·공식채점재현·실제시험환경일치를입증하지않는다. 각수업의PRD에는위행에서선택한목표·핵심흐름·관찰출력·실패조건·초기화조건을연결할수있다. 설명을길게쓰거나직접작성량을늘리는대신다음독립후보를추천한다.

1. **같은수치,다른뜻:** accuracy가높아도양성을전부놓친데이터,MAE와MSE가모델순위를달리보이는데이터.
2. **같은코드,달라진조건:** 비연속행라벨,미지범주,한클래스만남은작은검증셋,수치처럼보이는식별자.
3. **실행은되지만잘못된절차:** 정답열포함,전체자료fit후분할,테스트로하이퍼파라미터선택,훈련X로예측하고검증y와비교.
4. **신경망연결확인:** 결과shape/labelmapping/loss정합성,monitor키오타,검증자료누락,마지막epoch와최고epoch구별.
5. **도전은짧되판단은학생에게:** 준비코드는주고어디를고칠지는숨긴다.2~3개의원리를조합하되새API를설명없이동시에요구하지않는다.이는사용자교육원칙의적용제안이다.

실행확인시버전·shape·누수없는분리·선정지표·저장복원·그래프산출을확인한다.신경망의정확한한숫자/동일로그를강제하기보다요구구조와절차및허용오차를검증하는방식은자체채점제안이다.공식부분점수/채점알고리즘과혼동하지않는다.사용자가이번에위임한전체제작권한의범위는부모작업에서기록하며이조사문서로개별수업재승인절차를새로만들지않는다.
