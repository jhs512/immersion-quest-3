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

## 6. 수업6 보강: 결측·중복·이상치

추가 확인일: **2026-10-19**. 아래 API는 pandas1.5.3 공식 문서에서 직접 확인했다. **표의 자체 입력과 예상 결과는 문서 의미에서 계산한 추론이며 이번에 Python으로 실행하지 않았다.** 공식 시험에서 해당 API가 항상 나온다는 근거로 사용하지 않는다. 생산 콘텐츠나 PRD는 변경하지 않았다.

### 6.1 결측 발견과 처리의 의미

| API·구별 | 공식 확인 내용 | 작은 자체 비교와 예상 결과(미실행 추론) | 근거 |
| --- | --- | --- | --- |
| isna와0 | pandas는None/NaN 등을 결측으로 다룬다. 숫자0과 빈 문자열을 무조건 결측으로 묶지 않는다. 문자열 등의 결측 인식은 읽기 설정도 확인한다. | float열 `[0,NaN,10]`은3행, 결측1개. `==0`으로 삭제하면 정상0행을 없애며 NaN은 남는다. | [missing data](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/missing_data.html) |
| dropna 기본과subset | 기본행제거는선택범위에하나라도결측이면제거(`how='any'`). `subset`은결측검사할열을한정. `how='all'`과`thresh`는다른정책이다. | 3행 `(weight,note)=(10,NaN),(NaN,'ok'),(30,'ok')`. 기본dropna→1행. subset=['weight']→2행. how='all'→3행. | [DataFrame.dropna](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.dropna.html) |
| fillna0와median | fillna(value)는기존결측위치에지정값을넣는다. median은기본skipna=True. 이API만으로그값이업무상옳다는결론은나지않는다. | `[10,NaN,30]`에서0채움→`[10,0,30]`,중앙값채움→`[10,20,30]`. 둘다3행/결측0이지만의미와평균이다르다. 숫자0이실제미사용량인지,미측정값인지조건을먼저준다. | [fillna](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.fillna.html), [Series.median](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.Series.median.html) |
| 전부NaN인열 | skipna가관측값을새로만들지는않는다. pandas1.5.3의nanmedian은유효값을고른뒤NumPy nanmedian을쓰며빈집합은NaN을반환한다. | float열 `[NaN,NaN]`은중앙값NaN. `fillna(그중앙값)`후에도2행/결측2개가남을것으로예상한다. 별도업무기준의대체값·열제외·오류보고중하나를정해야한다. | [median](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.Series.median.html), [pandas v1.5.3 nanmedian 원문](https://github.com/pandas-dev/pandas/blob/v1.5.3/pandas/core/nanops.py), [missing data의빈합계·중앙값 설명](https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/missing_data.html) |
| 그룹size와count | GroupBy.size는그룹행수,GroupBy.count는결측을제외한항목수를센다. 그룹키자체결측을어떻게다룰지는groupby의dropna와별개다. | `(group,value)=(A,10),(A,NaN),(B,20)`에서size는A2/B1, value.count는A1/B1. 전체3행인데count합2만보고1행이사라졌다고해석하지않는다. | [GroupBy.size](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.core.groupby.GroupBy.size.html), [GroupBy.count](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.core.groupby.GroupBy.count.html), [groupby dropna](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.groupby.html) |

제작상 구별: 학습자가알아야할것은“결측을0개로만들었다”와“타당하게처리했다”가다르다는점이다. median추정이모델전처리라면훈련자료에서만계산하고검증/테스트에는그값을적용한다. API의미와별도로개입의근거를보여주는설계제안이다. [공식 데이터누수 설명](https://scikit-learn.org/1.3/common_pitfalls.html), 확인2026-10-19.

### 6.2 중복은 어떤 열을 같다고 보는가

`duplicated(subset=None,keep='first')`는불리언마스크를돌려준다. 기본은전체열,first는첫행을False로남기고뒤중복만True. last는마지막을남기며False는중복묶음의모든행을True로표시한다. `drop_duplicates`는해당정책으로행을제거한다. 인덱스는중복판정에포함하지않으며`ignore_index=True`는결과라벨을0부터다시붙인다. 확인2026-10-19. [duplicated](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.duplicated.html), [drop_duplicates](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.drop_duplicates.html)

자체입력은순서대로5행 `(id,amount)=(A,10),(A,10),(A,12),(B,20),(C,30)`이다. 다음예상은미실행추론이다.

| 판정 | 예상 마스크·남은 행 | 드러내는 원리 |
| --- | --- | --- |
| 전체열,keep='first' | 중복마스크 F,T,F,F,F; 제거후4행 | 같은id라도amount가다르면전체행중복은아님 |
| subset=['id'],keep='first' | 마스크 F,T,T,F,F; 제거후3행,A10보존 | 업무키중복과전체행중복구별 |
| subset=['id'],keep='last' | 마스크 T,T,F,F,F; 제거후3행,A12보존 | last는현재순서의마지막이며시간상최신보장은아님 |
| subset=['id'],keep=False | 마스크 T,T,T,F,F; 제거후2행,B/C만남음 | False는한개남기기가아니라중복묶음전부제거 |

같은고객의서로다른정상주문을고객id만으로중복삭제하면정보가사라질수있다. 이것은위API의업무적용상추론이다. “중복은항상삭제”대신수집단위·키·순서기준을조건으로제시해야한다.

### 6.3 IQR은 오류 확정 규칙이 아니다

pandas `Series.quantile`의기본은linear보간이며q는0~1. matplotlib3.7.1의boxplot기본whis=1.5는Q1−1.5IQR과Q3+1.5IQR안의실제데이터까지수염을그린다. 한계선수치자체와실제수염끝은다를수있다. 확인2026-10-19. [quantile](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.Series.quantile.html), [matplotlib boxplot3.7.1](https://matplotlib.org/3.7.1/api/_as_gen/matplotlib.pyplot.boxplot.html)

다음은“후보검토범위밖이면표시”라는**자체정책**의미실행계산이다.

- 기준표`[0,2,4,6,8]`은Q1=2,Q3=6,IQR=4,하한−4/상한12. 이기준을고정한별도관측`[-5,-4,12,13]`에서`x<−4 or x>12`후보는−5와13,2개다. 경계−4와12는유지한다. `<=`/`>=`로바꾸면4개가후보가되므로경계정책을명시한다. 검토관측까지합쳐quantile을다시계산하면동일문제가아니다.
- 정상검증된주문금액`[10,11,12,13,100]`은Q1=11,Q3=13,IQR=2,상한16이므로100이후보다. 그러나정상고액주문이라는조건에서100을자동삭제하면진짜거래를잃는다. 후보1개,검토전보존5행이라는결과가합리적인비교다.
- `[5,5,5,5,20]`은Q1=Q3=5,IQR=0이될수있다. 넓이가0인기준을업무판단없이통상범위라고부르면안된다. boxplot의autorange옵션과우리가정한필터정책도분리한다.

IQR계수1.5는보편적정답·센서오류확정·삭제의무가아니다. 그림의후보표시와실제처리결정은별개이며분포·업무조건·훈련자료기준을함께검토한다. 이교육적결론은공식API로부터의자체설계추론이다.

## 7. 수업7 보강: 그림이 무엇을 세고 무엇을 숨기는가

추가확인일: **2026-10-19**. matplotlib은3.7.1문서를직접읽었다. seaborn의공식`archive/0.12`문서는페이지표제가**0.12.2**다. 그러므로0.12.1과정확히일치한다고쓰지않고,중요기본값·시그니처는공식저장소**v0.12.1태그소스**도직접확인했다. 아래자체수치·렌더예상은직접실행하지않은추론이다.

| 비교 | 버전별 공식 사실 | 작은 자체 입력·예상과 선택 조건 | 근거 |
| --- | --- | --- | --- |
| countplot와barplot | 0.12.1 countplot은개수,size기준. barplot기본estimator='mean',errorbar=('ci',95). 0.13의countplot(stat='percent')을0.12.1에옮기면안됨. | A가격10,20,30/B가격100이면개수막대는A3/B1,평균막대는A20/B100. “주문많은곳”과“평균금액높은곳”은답이다름. | [countplot0.12문서](https://seaborn.pydata.org/archive/0.12/generated/seaborn.countplot.html), [barplot0.12문서](https://seaborn.pydata.org/archive/0.12/generated/seaborn.barplot.html), [v0.12.1 categorical소스](https://github.com/mwaskom/seaborn/blob/v0.12.1/seaborn/categorical.py) |
| hist구간경계 | matplotlib의마지막제외각bin은왼쪽포함/오른쪽제외,마지막bin만양끝포함. 범위밖자료는지정범위집계에서제외될수있다. | 값0,1,2,3,4에bins=[0,2,4]이면개수2/3. 2는두번째,4도두번째. 범위를[0,2]로축소해전체5개분포처럼설명하지않음. | [hist3.7.1](https://matplotlib.org/3.7.1/api/_as_gen/matplotlib.pyplot.hist.html) |
| density와확률 | density는총막대면적1이며높이합1이아니다. seaborn probability는높이합1. | 값0.5,2,3/bins=[0,1,5]이면개수1/2,probability1/3와2/3,밀도1/3와1/6. 폭이다르므로높이만으로관측수가많다고해석하면안됨. | [matplotlib hist](https://matplotlib.org/3.7.1/api/_as_gen/matplotlib.pyplot.hist.html), [histplot0.12문서](https://seaborn.pydata.org/archive/0.12/generated/seaborn.histplot.html) |
| hue정규화의분모 | histplot은기본common_norm=True. False이면각조건그룹을독립정규화. common_bins로구간도같이맞출수있다. 0.12.1시그니처확인. | A세개/B한개가모두같은한bin에있을때probability+공통분모는A0.75/B0.25. common_norm=False면A1/B1. “전체구성비”와“각그룹안분포”를구별. | [histplot0.12문서](https://seaborn.pydata.org/archive/0.12/generated/seaborn.histplot.html), [v0.12.1 distributions소스](https://github.com/mwaskom/seaborn/blob/v0.12.1/seaborn/distributions.py) |
| scatter겹침 | scatterplot은x/y위치와hue/size/style의의미를연결한다. 하나의색이나모양만으로모든변수를표현하지않는다. | 점(1,10)이두개,(2,20),(3,30)이각하나면4행이3위치에겹친다. 보이는점3개를관측3개라고세지않도록행수/중복좌표를확인. alpha를줄여겹침관찰은돕되정확한빈도계산은별도로. | [scatterplot0.12](https://seaborn.pydata.org/archive/0.12/generated/seaborn.scatterplot.html) |
| heatmap의입력 | heatmap은주어진2차원자료를색으로표현하며자체로상관계수를계산하는함수가아님. vmin/vmax/center/annot/색막대가해석기준. | 원시매출표heatmap과상관행렬heatmap을같은뜻으로읽지않음. 상관비교라면범위−1~1,중심0등을고정하고행/열이름확인. 대각선자기상관의큰색을새로운발견이라고하지않음. | [heatmap0.12](https://seaborn.pydata.org/archive/0.12/generated/seaborn.heatmap.html) |
| boxplot의후보 | 중앙값/Q1/Q3/수염과fliers를구별. showfliers=False는점표시를숨기며원데이터정제와다름. | 수업6의정상고액100을숨겨그려도원래5행은그대로다. 그림표시변경과행삭제를각각확인. | [boxplot3.7.1](https://matplotlib.org/3.7.1/api/_as_gen/matplotlib.pyplot.boxplot.html) |

### 제작 시 실행 증거로 바꾸어야 할 항목

수업을만들때에는부모작업의격리환경에서예상행수/마스크/통계/그래프산출을실행확인해야한다. 다음은구현제안이며이번조사완료주장이아니다.

- 중복판정은남은행수뿐아니라어떤A행이남았는지검사한다. 입력순서를바꿔first/last암기풀이를구별한다.
- 결측판정은전체NaN열,0관측값,검사대상밖메모열을포함해기계적dropna/0채움의부작용을드러낸다.
- IQR은기준자료와판정자료를분리하고경계포함조건을검사한다. “삭제후몇행”만정답으로두면정상극단값문제를숨길수있다.
- 그래프는파일존재만검사하지않고필요축·통계·분모·구간·범주이름을확인한다. 랜덤부트스트랩오차막대를픽셀전체일치로채점하지않는다.
- 긴그림해설읽기대신같은자료에서개수/평균,빈도/비율,표시숨김/자료삭제를한곳수정하며비교하는후보가사용자의원리·작은작성량원칙에맞는다.

## 8. 특성·자료 분리·누수·스케일 수업 보강

추가 확인일: **2026-10-19**. pandas **1.5.3**, scikit-learn **1.3.2**의 버전 고정 공식 문서를 직접 열었다. 정확한 층화 분할의 실패 조건과 반올림은 scikit-learn **1.3.2 태그 소스**로 추가 확인했다. 아래 자체 입력·출력은 **문서와 소스에서 계산한 미실행 예상**이다. 실제 시험 커널·로컬 패키지 실행·공식 채점 일치를 확인한 것이 아니다. 제작 코드·PRD는 수정하지 않았다.

### 8.1 pandas: 자료형 변경과 새 특성이 숨기는 조건

| API | 버전 고정 문서에서 확인한 의미 | 자체 작은 비교·예상(미실행) | 출처·확인일 |
| --- | --- | --- | --- |
| to_datetime | 기본errors='raise'. coerce는파싱실패를NaT, ignore는변환실패시입력반환. format으로형식지정. dayfirst=True는엄격검사가아님. 숫자는unit과origin의의미를명시. utc=True는naive입력을UTC로간주하고aware입력을UTC로변환. | `['2026-10-01','bad','2026-10-03']`에format='%Y-%m-%d',coerce면3행을유지하며NaT1개. 그다음날짜열dropna를해야2행. 변환만으로잘못된행이삭제된다고쓰지않음. | [to_datetime1.5.3](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.to_datetime.html),2026-10-19 |
| Series.map | 일반dict에없는키는NaN. 반환Series의인덱스는호출Series와같음. na_action='ignore'는기존NaN에함수를적용하지않는것이며미지키를자동복구하지않음. __missing__을정의한dict서브클래스는예외. | `['low','high','other',None]`과{'low':0,'high':1}은4행,새결측2개예상. low/high순서에근거가있을때만0/1의순서를의도한다. 'other'를무작정0으로채우면진짜low와합쳐짐. | [Series.map1.5.3](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.Series.map.html),2026-10-19 |
| get_dummies | columns미지정시object/string/category열변환. 기본dummy_na=False,drop_first=False,dtype=np.uint8. dummy_na=True는결측표시열추가. 숫자형범주열은columns등으로의도를명시. | Series `['A','B',NaN]`은기본3×2(A/B),NaN행은[0,0]. dummy_na=True는3×3이며NaN행[0,0,1]. drop_first=True와기본dummy_na=False를함께쓰면기준범주와결측이같은0벡터가될수있으므로구별조건필요. | [get_dummies1.5.3](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.get_dummies.html),2026-10-19 |
| astype | dtype또는열별dict를받고기본copy=True,errors='raise'. errors='ignore'는오류를억제하고원래객체를반환할수있음. 의미정규화·오타정정·미지범주정책을대신하지않음. | 코드열`['001','002']`을int로바꾸면[1,2],문자열이갖던앞자리0은보존되지않음. `['12','bad']`를int변환하고ignore면변환성공을가정하지말고dtype/값을확인. | [astype1.5.3](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.DataFrame.astype.html),2026-10-19 |

같은조건을적용하는고정변환과자료에서기준을**학습**하는변환을구별한다. 예컨대명시된날짜형식이나사전에정한등급사전은자료의평균을추정하는것과다르다. 그러나데이터전체에서등급순서·희귀도·대체통계를추정하면훈련밖의정보가들어갈수있다. 날짜특성도예측시점에알수있는발송예정일과결과가나온뒤의실제도착일은다르다. 이는API만으로보장되지않는자체설계판단이다. 근거: [sklearn1.3 데이터누수](https://scikit-learn.org/1.3/common_pitfalls.html),확인2026-10-19.

학습/검증을각각get_dummies하면학습A/B열과검증B/C열처럼열구성이달라질수있다. 훈련열로검증을reindex하고빈열을0으로맞추는것은호환정책의한후보지만미지C의정보를잃는다는점을기록해야한다. 전체자료를합쳐더미열을발견하는방식을무조건누수없다고부르지않는다. 고정스키마를외부에서받았는지,검증자료로스키마를학습했는지구별한다. 이단락은[get_dummies](https://pandas.pydata.org/pandas-docs/version/1.5/reference/api/pandas.get_dummies.html)와[누수원칙](https://scikit-learn.org/1.3/common_pitfalls.html)에서의도출이며미실행추론이다(2026-10-19).

### 8.2 train_test_split: 층화·경계·시간순서

| 확인 사실 | 자체 입력·예상 또는 제작 경계 | 공식 근거·확인일 |
| --- | --- | --- |
| 입력들은동일한행수여야하며함께분리. float test_size는비율,int는개수. 기본shuffle=True,random_state정수로같은호출조건의분할재현. 반환은입력마다train/test쌍. | X6행/y6행을같이넣어test_size=2면train4/test2. X/y를따로shuffle하거나마스크를따로만들면표와정답대응이깨질수있음. | [train_test_split1.3.2](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.train_test_split.html),2026-10-19 |
| float test_size에대해n_test=ceil(test_size*n_samples),float train_size에는floor. | 7행,test_size=0.25면test2/train5. 1.75행이없으므로“25%니까1행”은틀림. 둘을동시에작게지정하면모든행이양쪽중하나에들어간다는조건이항상성립하지않음. | [1.3.2 splitter소스](https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.3.2/sklearn/model_selection/_split.py),2026-10-19 |
| stratify는지정한클래스라벨기준층화. shuffle=False와병행불가. 최소클래스2개이상,train/test개수가각각클래스수이상이어야함. | y=[0,0,0,0,1]은소수클래스1개라stratify=y오류예상. 클래스당2개씩인3클래스6행에서test_size=2도test개수<클래스수라오류. | [API](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.train_test_split.html), [StratifiedShuffleSplit1.3.2소스](https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.3.2/sklearn/model_selection/_split.py),2026-10-19 |
| 계층화는반올림과표본제약안에서클래스비율을가깝게유지. 연속회귀목표의각실숫값을그대로클래스로보는정책은아님. | 8개0/2개1,test_size=0.5에서는각측5행에0네개/1한개예상. 매우희소클래스/작은test에서각측모든클래스가항상존재한다고약속하지않음. | [분할API·층화소스](https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.3.2/sklearn/model_selection/_split.py),2026-10-19 |
| shuffle=False는입력행순서를보존할뿐날짜를자동정렬하지않음. TimeSeriesSplit은연속누적훈련구간과뒤의평가구간으로시계열분할을제공하며gap을둘수있음. | 날짜가1/3,1/1,1/4,1/2순서인데shuffle=False여도시간분리보장없음. 먼저예측시각기준정렬. 같은날짜묶음이경계양쪽에있는경우시각·엔터티단위정책을추가. | [split API](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.train_test_split.html), [TimeSeriesSplit1.3.2](https://scikit-learn.org/1.3/modules/generated/sklearn.model_selection.TimeSeriesSplit.html),2026-10-19 |

시계열에서단순random split과“seed고정이니누수없음”을동일시하지않는다. 재현성과정보이용가능성은다른조건이다. TimeSeriesSplit도입력시점·그룹경계·불규칙기간을자동해결한다고일반화하지않는다. 자기데이터의예측목표와평가기간정책은별도설계이며공식시험의지정조건이있으면그조건을따르는연습과구별한다.

### 8.3 Pipeline·ColumnTransformer·OneHotEncoder

| API | 공식 의미와 함정 | 자체 작은 비교·예상(미실행) | 출처·확인일 |
| --- | --- | --- | --- |
| Pipeline | 중간단계는fit/transform,마지막은estimator. 학습단계들을순서대로적용하고`단계이름__파라미터`로설정. CV에전처리와모델을함께넣으면각훈련fold안에서fit가능. | scaler를전체X에먼저fit한뒤모델만Pipeline에넣어도이미생긴누수는사라지지않음. pipeline을test까지포함해fit해도누수. | [Pipeline1.3.2](https://scikit-learn.org/1.3/modules/generated/sklearn.pipeline.Pipeline.html), [pitfalls](https://scikit-learn.org/1.3/common_pitfalls.html),2026-10-19 |
| ColumnTransformer | (name,transformer,columns)목록을열별적용후결합. 기본remainder='drop'. scalar열선택은1D,목록은2D. passthrough는fit당시남은열을그대로넘김. | 수치1열+범주1열+id1열에서수치/범주만명시하면id제외. remainder='passthrough'로바꾸면id가추가됨. y나미래정보가X에남아있다면이정책이누수를만들수있음. | [ColumnTransformer1.3.2](https://scikit-learn.org/1.3/modules/generated/sklearn.compose.ColumnTransformer.html),2026-10-19 |
| 출력자료형 | OneHotEncoder1.3은sparse_output=True가기본. ColumnTransformer는희소출력포함시전체밀도와기본sparse_threshold=0.3에따라결합자료형선택. | OneHotEncoder가sparse라고전체결합이항상sparse인것은아님. 표표시/TF입력연결에서shape와sparse/dense를확인. 수업에서작은dense결과를의도한다면해당설정을명시. | [OHE1.3.2](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.OneHotEncoder.html), [ColumnTransformer](https://scikit-learn.org/1.3/modules/generated/sklearn.compose.ColumnTransformer.html),2026-10-19 |
| 알수없는범주 | handle_unknown기본error. ignore는해당특성블록을모두0,역변환은None. infrequent_if_exist는희귀그룹이있을때그그룹에합치고없으면ignore처럼동작. | 훈련A/B,검증C에서error는실패,ignore는학습2열유지후C=[0,0]. 자동으로C새열을만들지않음. drop='first'와ignore를같이쓰면기준범주와미지범주의표현이겹칠수있음. | [OHE1.3.2](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.OneHotEncoder.html),2026-10-19 |

인코더의categories_/feature_names와변환열순서를보존해야다른범주를같은수치열로착각하지않는다. 미지범주를허용했다는것은그범주예측이검증되었다는뜻이아니다. 자체검증은미지범주1개만추가하는작은입력으로열수보존·오류정책·사용자에게설명할정보손실을따로관찰하는방식이좋다. 이는공식API의미에기초한연구제안이다.

### 8.4 StandardScaler의 기준·NaN·상수열

scikit-learn1.3.2 `StandardScaler`는훈련의각특성평균과분산을저장하며표준편차는ddof=0이다. 기본with_mean/with_std=True. 분산0의scale_는1,fit에서NaN은제외하고transform에서는NaN을남긴다. sparse행렬은with_mean=True일때오류가발생하므로희소원핫전체를중심화하는구성에주의한다. 이상치제거·결측대체·최소최대[0,1]정규화와다르다. 확인2026-10-19. [StandardScaler1.3.2](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.StandardScaler.html)

다음은미실행수학적예상이다.

- 훈련한열`[0,2]`는평균1/표준편차1 → 변환`[-1,1]`. 검증`[10]`은같은기준으로`[9]`이며[0,1]밖이어도오류가아니다.
- 검증`[10]`에다시fit_transform하면평균10/scale1로`[0]`. 실행은되어도훈련과기준이다르므로올바른검증이아니다.
- 훈련상수열`[5,5]`는평균5/scale1 → `[0,0]`. 검증`[7]`은`[2]`. “훈련에서상수였으니미래값도무조건0”이아니다.
- NaN이있는변환결과는NaN을유지하므로“스케일러적용했으니모든모델에바로입력가능”이라고하지않는다. 결측대체를결합할때도대체통계는훈련범위에서학습한다.

이절의예상은다음제작단계에서격리환경으로확인해야한다. 단순출력동일성뿐아니라train/test행겹침,기준통계변경,목표열/미래열포함,인코더열순서,unknown정책,시간경계의미를검증대상으로남긴다. 승인이나제작범위를이문서에서새로제한하지않는다.


## 9. 전처리·회귀 입문 제작에서 추가 확인한 경계

확인2026-10-19. 아래 API 의미는 공식 sklearn1.3.2 문서를 직접 확인했고, 자체 사례는 별도 Python3.11/sklearn1.3.2 학습 환경에서 실제 실행했다. 공식 응시 커널이나 시험 문제 실행이라는 뜻은 아니다.

- [MinMaxScaler](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.MinMaxScaler.html)는 기본 clip=False다. 훈련0/2에서 평가10은5, clip=True면1로 변환됐다. 지정 범위는 훈련 기준이며 미래 관측을 항상 범위 안에 넣는다고 말하지 않는다.
- [RobustScaler](https://scikit-learn.org/1.3/modules/generated/sklearn.preprocessing.RobustScaler.html)는 중앙값과 기본25~75분위수 범위를 저장한다. 훈련0/1/2/3/100의 center2/scale2와 새 값4/100의1/49를 실제 확인했다. 이 작은 표의 마지막100을1000으로 바꿔도 해당 두 통계는 같았지만, 모든 자료의 변경에 불변이라는 일반화는 하지 않는다. 극단값 삭제·클리핑과 다르다.
- [LinearRegression](https://scikit-learn.org/1.3/modules/generated/sklearn.linear_model.LinearRegression.html)은 최소제곱 계수·절편을 학습하고 행×특성 모양의 새 입력을 예측한다. 거리1/2/3,시간10/20/30을 학습한 새 거리4는40이었다. 미학습 호출과1차원 입력은 각각NotFittedError와ValueError로 확인했다.
- [DummyRegressor](https://scikit-learn.org/1.3/modules/generated/sklearn.dummy.DummyRegressor.html)의 mean 기준은 훈련 정답 평균을 예측한다. 같은 세 정답의 평균20을 두 새 입력에 똑같이 예측했다. 이는 실제 배송 성능 보장이나 공식 시험의 특정 정답이 아니다.

실행 증거: target/player-pilot-audit/aice-scale/public-final-cases.json, aice-regression/public-cases.json. 증거는 정확한 수업 해시·독립 예상 출력·오답 거절을 포함하며 native_ui_verified/voice_listened는 별도로False다. 앱·세 OS 검증은 해당 head의 CI와 native 결과로 따로 확인해야 한다.
