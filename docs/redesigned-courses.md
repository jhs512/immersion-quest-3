# 새 세 과정의 구성과 제작 기준

세 과정은 서로 독립된 수업과 진도를 갖는다. 추천 순서로 배열하지만 수업은 자유롭게 선택한다. 기본 목록은 공개 GitHub 코스 저장소를 읽으며 기존 사용자가 추가한 코스도 보존한다.

## 학습 경험

- 수업 → 챕터 → 단원 → 스텝 구조와 각 단계의 명확한 교육 목표를 제공한다.
- 단원마다 하나의 상황이 이어지고 각 스텝에는 새 조건을 짧게 제시한다.
- 작은 문제를 풀며 원리를 이해한다. 선택·순서·짧은 답안·코드 수정·실제 Git 실습을 목표에 맞게 사용한다.
- 해설은 학생 답안을 보관한 별도 시연이다. 작은 변경→실행→결과 확인을 연결하고 설명하는 버튼·줄·결과를 강조한다. 해설 열람만으로 성공시키지 않는다.
- 문제의 본질이 달라지면 기존 문제를 비활성화하고 새 ID를 만든다. 기존 완료 기록은 보존한다.

## 과정별 범위

자바의 상위 목표는 기초가 탄탄한 자바·Spring Boot 백엔드 개발자 양성이다. 이번 공개 묶음은 Git·자바·작은 앱·테스트와 가벼운 React·Tailwind 기초까지다. Spring Boot와 DB 실무 수업은 이 묶음에 포함된 것으로 주장하지 않는다.

에이스는 Python·pandas·시각화·전처리·누수 방지·scikit-learn·TensorFlow·성능 개선·통합 분석을 연결한다. 선택형은 이해 확인에 쓰며 직접 코드 수정·실행과 결과 해석도 포함한다. 시험 커널의 패치 버전과 동일하다고 주장하지 않는다. 강제 시간 제한 모의고사는 제공하지 않는다.

정처기는 C·Java·Python의 결과 읽기, SQL과 DB, 요구·설계·서버·연계·화면·테스트·보안·운영체제·네트워크·배포를 연결한다. 실행으로 원리를 확인한 뒤 짧은 필답과 조건 판단으로 이어진다. 공식 출제 범위와 사설 복원은 근거 문서에서 구분한다.

## 수업 목록

### 자바 백엔드 과정

18수업 · 150스텝

[코스 구성](../courses/redesigned-courses/java-backend.json) · [코스 PRD](../tools/redesigned_courses/java/course-prd.json)

| 순서 | 수업 | 스텝 |
| --- | --- | --- |
| 1 | [Git · 내 파일이 기록이 되는 과정](../tools/redesigned_lessons/git_first/approved-prd.json) | 6 |
| 2 | [Git · 작업을 나누고 다시 합치는 과정](../tools/redesigned_lessons/git_branch/approved-prd.json) | 9 |
| 3 | [공유 기록을 받고 비교하고 되돌려요](../tools/redesigned_lessons/git_remote/approved-prd.json) | 8 |
| 4 | [자바 · 값이 계산되고 표시되는 과정](../tools/redesigned_lessons/java_values/approved-prd.json) | 9 |
| 5 | [자바 · 비교로 배송비를 고르는 과정](../tools/redesigned_lessons/java_conditions/approved-prd.json) | 8 |
| 6 | [자바 · 배열을 따라 가격을 더해요](../tools/redesigned_lessons/java_arrays/approved-prd.json) | 8 |
| 7 | [자바 · 계산을 메서드로 나눠요](../tools/redesigned_lessons/java_methods/approved-prd.json) | 8 |
| 8 | [자바 · 객체와 참조를 나눠 봐요](../tools/redesigned_lessons/java_references/approved-prd.json) | 10 |
| 9 | [자바 · 객체의 값과 static을 나눠요](../tools/redesigned_lessons/java_static/approved-prd.json) | 8 |
| 10 | [상태를 지키고 객체의 역할을 나눠요](../tools/redesigned_lessons/java_roles/approved-prd.json) | 8 |
| 11 | [주문 목록·태그·상품 수를 다뤄요](../tools/redesigned_lessons/java_collections/approved-prd.json) | 10 |
| 12 | [가격을 고르고 바꾸고 합산해요](../tools/redesigned_lessons/java_streams/approved-prd.json) | 10 |
| 13 | [글을 파일에 남기고 실패도 처리해요](../tools/redesigned_lessons/java_files/approved-prd.json) | 10 |
| 14 | [같은 글 앱에서 추가·조회·수정·삭제를 연결해요](../tools/redesigned_lessons/java_crud/approved-prd.json) | 10 |
| 15 | [배송비 변경을 작은 테스트로 검증해요](../tools/redesigned_lessons/java_testing/approved-prd.json) | 8 |
| 16 | [요청을 나누고 계산의 규칙을 검증해요](../tools/redesigned_lessons/java_parser/approved-prd.json) | 8 |
| 17 | [AI가 만든 작은 React 화면을 읽고 고쳐요](../tools/redesigned_lessons/java_react/approved-prd.json) | 6 |
| 18 | [작은 Tailwind 화면의 배치를 읽고 고쳐요](../tools/redesigned_lessons/java_tailwind/approved-prd.json) | 6 |

### AICE Associate 과정

24수업 · 204스텝

[코스 구성](../courses/redesigned-courses/aice-associate.json) · [코스 PRD](../tools/redesigned_courses/aice/course-prd.json)

| 순서 | 수업 | 스텝 |
| --- | --- | --- |
| 1 | [표를 다루기 위한 파이썬 첫 걸음](../tools/redesigned_lessons/aice_python_start/approved-prd.json) | 7 |
| 2 | [조건에 따라 배송 자료를 골라요](../tools/redesigned_lessons/aice_python_conditions/approved-prd.json) | 8 |
| 3 | [묶은 자료와 라이브러리 기능을 읽어요](../tools/redesigned_lessons/aice_python_api/approved-prd.json) | 8 |
| 4 | [배송 표를 보고 CSV로 읽어요](../tools/redesigned_lessons/aice_table_csv/approved-prd.json) | 8 |
| 5 | [필요한 배송을 고르고 요약해요](../tools/redesigned_lessons/aice_selection/approved-prd.json) | 10 |
| 6 | [비거나 중복된 배송 자료를 살펴봐요](../tools/redesigned_lessons/aice_quality/approved-prd.json) | 10 |
| 7 | [여러 배송 파일을 같은 키로 연결해요](../tools/redesigned_lessons/aice_join/approved-prd.json) | 8 |
| 8 | [그림의 높이와 원래 자료를 비교해요](../tools/redesigned_lessons/aice_plots/approved-prd.json) | 10 |
| 9 | [예측에 쓸 열의 의미를 확인해요](../tools/redesigned_lessons/aice_features/approved-prd.json) | 8 |
| 10 | [입력과 정답을 함께 나눠요](../tools/redesigned_lessons/aice_split/approved-prd.json) | 10 |
| 11 | [남겨둔 정보가 새어 들어오는지 봐요](../tools/redesigned_lessons/aice_leakage/approved-prd.json) | 8 |
| 12 | [훈련에서 배운 전처리 기준을 적용해요](../tools/redesigned_lessons/aice_scale/approved-prd.json) | 9 |
| 13 | [거리에서 배송 시간을 예측해요](../tools/redesigned_lessons/aice_regression/approved-prd.json) | 8 |
| 14 | [예측 오차를 목적에 맞게 읽어요](../tools/redesigned_lessons/aice_regression_metrics/approved-prd.json) | 8 |
| 15 | [배송의 지연 종류를 예측해요](../tools/redesigned_lessons/aice_classification/approved-prd.json) | 8 |
| 16 | [지연 경보의 성능을 판단해요](../tools/redesigned_lessons/aice_classification_metrics/approved-prd.json) | 10 |
| 17 | [같은 배송 자료로 여러 모델을 비교해요](../tools/redesigned_lessons/aice_models/approved-prd.json) | 8 |
| 18 | [부스팅의 학습 설정과 예측을 읽어요](../tools/redesigned_lessons/aice_boosting/approved-prd.json) | 8 |
| 19 | [검증 자료를 지키며 설정을 비교해요](../tools/redesigned_lessons/aice_tuning/approved-prd.json) | 8 |
| 20 | [TensorFlow의 구성·학습·예측을 구별해요](../tools/redesigned_lessons/aice_tensorflow/approved-prd.json) | 8 |
| 21 | [신경망 회귀의 출력과 평가를 맞춰요](../tools/redesigned_lessons/aice_neural_regression/approved-prd.json) | 8 |
| 22 | [신경망 분류의 출력과 정답을 맞춰요](../tools/redesigned_lessons/aice_neural_classification/approved-prd.json) | 8 |
| 23 | [학습 기록을 보고 개선 방법을 판단해요](../tools/redesigned_lessons/aice_training/approved-prd.json) | 8 |
| 24 | [파일부터 전처리·모델·결과까지 연결해요](../tools/redesigned_lessons/aice_integration/approved-prd.json) | 10 |

### 정보처리기사 실기 과정

30수업 · 335스텝

[코스 구성](../courses/redesigned-courses/engineer-practical.json) · [코스 PRD](../tools/redesigned_courses/engineer/course-prd.json)

| 순서 | 수업 | 스텝 |
| --- | --- | --- |
| 1 | [C 값과 대입을 순서대로 읽어요](../tools/redesigned_lessons/engineer_c_start/approved-prd.json) | 6 |
| 2 | [C 연산과 조건을 읽어요](../tools/redesigned_lessons/engineer_c_conditions/approved-prd.json) | 8 |
| 3 | [C 반복과 배열을 읽어요](../tools/redesigned_lessons/engineer_c_arrays/approved-prd.json) | 10 |
| 4 | [C 함수와 재귀를 따라가요](../tools/redesigned_lessons/engineer_c_functions/approved-prd.json) | 10 |
| 5 | [C · 주소와 가리키는 값을 나눠 봐요](../tools/redesigned_lessons/engineer_c_pointers/approved-prd.json) | 10 |
| 6 | [C · 다중 포인터의 층을 따라가요](../tools/redesigned_lessons/engineer_c_double_pointers/approved-prd.json) | 8 |
| 7 | [C · 구조체와 계산 규칙을 골라요](../tools/redesigned_lessons/engineer_c_structures/approved-prd.json) | 18 |
| 8 | [Java · 재고 계산의 실행 순서를 읽어요](../tools/redesigned_lessons/engineer_java_flow/approved-prd.json) | 8 |
| 9 | [Java · 같은 객체와 다른 이름을 구별해요](../tools/redesigned_lessons/engineer_java_references/approved-prd.json) | 8 |
| 10 | [Java · 공유 번호와 생성 순서를 읽어요](../tools/redesigned_lessons/engineer_java_static/approved-prd.json) | 8 |
| 11 | [Java · 호출 규칙과 예외 뒤 순서를 읽어요](../tools/redesigned_lessons/engineer_java_polymorphism/approved-prd.json) | 8 |
| 12 | [Python · 같은 창고 자료를 골라 읽어요](../tools/redesigned_lessons/engineer_python_values/approved-prd.json) | 8 |
| 13 | [Python · 같은 재고 함수의 호출을 읽어요](../tools/redesigned_lessons/engineer_python_calls/approved-prd.json) | 10 |
| 14 | [DB · 같은 물건을 표와 키로 구별해요](../tools/redesigned_lessons/engineer_db_model/approved-prd.json) | 8 |
| 15 | [SQL · 같은 재고의 조건과 연결을 읽어요](../tools/redesigned_lessons/engineer_sql_select/approved-prd.json) | 10 |
| 16 | [SQL · 같은 재고의 그룹과 순서를 읽어요](../tools/redesigned_lessons/engineer_sql_group/approved-prd.json) | 10 |
| 17 | [SQL · 같은 재고의 변경과 권한을 구별해요](../tools/redesigned_lessons/engineer_sql_change/approved-prd.json) | 10 |
| 18 | [DB · 종속·저장·조회 로직의 역할을 읽어요](../tools/redesigned_lessons/engineer_db_storage/approved-prd.json) | 18 |
| 19 | [요구사항 · 같은 재고 규칙을 확인해요](../tools/redesigned_lessons/engineer_requirements/approved-prd.json) | 8 |
| 20 | [설계 · 같은 창구의 모델과 패턴을 구별해요](../tools/redesigned_lessons/engineer_design/approved-prd.json) | 27 |
| 21 | [서버 · 같은 업무의 책임과 실행을 나눠요](../tools/redesigned_lessons/engineer_server/approved-prd.json) | 22 |
| 22 | [연계 · 같은 창고 요청의 약속을 읽어요](../tools/redesigned_lessons/engineer_interfaces/approved-prd.json) | 10 |
| 23 | [화면 · 같은 정정 요청을 끝까지 이어 봐요](../tools/redesigned_lessons/engineer_ui/approved-prd.json) | 8 |
| 24 | [테스트 · 같은 수량 규칙의 반례를 찾아요](../tools/redesigned_lessons/engineer_test_cases/approved-prd.json) | 8 |
| 25 | [테스트 · 같은 서비스의 연결과 범위를 읽어요](../tools/redesigned_lessons/engineer_test_integration/approved-prd.json) | 10 |
| 26 | [보안 · 같은 재고 서비스의 경계를 지켜요](../tools/redesigned_lessons/engineer_security/approved-prd.json) | 14 |
| 27 | [운영체제 · 같은 작업의 시간과 자원을 읽어요](../tools/redesigned_lessons/engineer_os/approved-prd.json) | 14 |
| 28 | [네트워크 · 같은 창고의 주소와 전송을 읽어요](../tools/redesigned_lessons/engineer_network/approved-prd.json) | 14 |
| 29 | [배포 · 같은 수정의 출처와 버전을 남겨요](../tools/redesigned_lessons/engineer_build/approved-prd.json) | 10 |
| 30 | [종합 · 같은 재고 보고의 답안을 연결해요](../tools/redesigned_lessons/engineer_mixed/approved-prd.json) | 14 |

## 제작·업데이트

제작 기준은 각 수업의 `approved-prd.json`이다. 정책 원문 스냅샷, 정확한 승인 해시, 대표 문제와 상세 핵심 흐름을 포함한다. 이번 제작은 사용자의 전체 재설계 위임 범위에서 진행했으며 각 PRD를 사용자가 직접 검토했다는 뜻은 아니다.

학생에게 보여 주는 원본은 해당 수업의 `content.json`이다. 바뀐 원본의 인접 레이어만 검토하고, 필요한 해설 캐시만 다시 만든다. 수업 생성물은 `courses/redesigned/`에 있으며 코스는 수업 저장소의 불변 revision과 SHA-256을 참조한다.

```powershell
python tools/build-redesigned-git.py --lesson all --check
python tools/build-redesigned-course-bundle.py --check
python tools/test_lesson_prd.py
python tools/test_redesigned_highlights.py
python tools/build-kpc-course.py
```

게시 계획은 `python tools/publish-redesigned-courses.py`로 확인한다. `--publish`는 새 공개 저장소에만 게시하며 이미 게시한 다른 내용이나 불변 태그는 덮어쓰지 않는다. 기존 코스 저장소와 진도 이슈를 변경하지 않는다.

### 최초 게시 후 개정

위 도구는 최초 게시와 동일 바이트의 재실행 전용이다. 후속 개정은 수업 저장소의 일반 Git 변경으로 게시한다.

1. 수정할 수업의 PRD·핵심 흐름·콘텐츠를 인접 변경 전파 규칙으로 검토한다. 목표나 교수법이 바뀌면 승인을 갱신한다. 문제의 본질이 달라지면 기존 스텝을 비활성화하고 새 코드를 부여한다.
2. `tools/build-redesigned-git.py`의 해당 수업 revision을 새 값으로 올리고 필요한 파생물만 재생성한다. 기존 revision 태그와 리소스 코드는 이동하거나 재사용하지 않는다.
3. 실행·채점·해설 검증을 마친 `lesson.json`을 해당 수업 저장소에 커밋하고 새 불변 태그를 만든다. 그 태그에서 읽은 바이트와 로컬 SHA-256이 같은지 확인한다.
4. 코스 묶음을 재생성해 변경된 수업의 revision·SHA-256만 새 값으로 참조한다. 새 태그가 실제로 조회되는 것을 확인한 뒤 해당 코스 저장소의 `course.json`을 커밋한다. 코스와 수업의 제작 변경 이력도 남긴다.
5. 플레이어는 시작 시와 5분 간격으로 코스의 새 구성을 확인한다. 학습자가 업데이트를 누르면 전체 후보를 검증하고 답안을 백업한 뒤 적용한다. 잘못된 후보는 거절하고 기존 설치본과 완료 기록을 유지한다.

수업 저장소의 main만 바꿔서는 기존 고정 태그를 참조하는 코스가 바뀌지 않는다. 반드시 새 태그와 코스 참조를 함께 게시해야 한다.

## 실행 환경 검증

자바 실행은 JDK25, C는 실제 컴파일러, SQL은 격리된 SQLite 환경을 사용한다. 공급사별 SQL·권한·프로시저 개념은 SQLite로 해당 제품의 동작을 흉내 내었다고 주장하지 않는다. Python은 기준 환경과 배포 패키지 환경을 따로 검사한다.

Windows와 macOS ARM/Intel의 CI는 실제 앱에서 풀이·해설·초기화·답안 복원을 검사한다. 음성 다운로드 검사와 실제 음성 청취는 별도 증거다. DOM 단축키나 UTF-8 검사를 물리 IME 조합 검사로 표현하지 않는다.

작업별 자세한 증거와 미확인 범위는 로컬 `.scratch/player-content-redesign/implementation-log.md`와 `target/player-pilot-audit/`에 보관한다.
