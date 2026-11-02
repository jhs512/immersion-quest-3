# 코스·수업·스텝 inventory

`python tools/course_audit/inventory.py`가 만든다. 손으로 고치지 않는다.

- 고유 수업 파일 107개, 스텝 1073개.
- 코스 참조 98개. 어느 코스에도 없는 수업: java-parser, node-cpu-offload, socket-partial-frames, sys-buffer-pool, sys-cache-locality, sys-interleavings, sys-interpreter-env, sys-page-table, sys-sliding-window.
- manifest 대조 문제: 0건.

## 코드 흐름 보기 상태(스텝 수)

| 언어 | 스텝 | Windows ready | macOS ready | Linux ready | 숨김 | 해설 code_flow |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| python | 436 | 258 | 258 | 258 | 178 | 5 |
| java | 266 | 237 | 237 | 237 | 29 | 10 |
| git | 126 | 0 | 0 | 0 | 126 | 0 |
| c | 79 | 79 | 79 | 0 | 0 | 4 |
| docker | 63 | 0 | 0 | 0 | 20 | 0 |
| web | 46 | 0 | 0 | 0 | 0 | 0 |
| sql | 40 | 0 | 0 | 0 | 2 | 0 |
| java_libraries | 9 | 0 | 0 | 0 | 0 | 0 |
| javascript | 5 | 0 | 0 | 0 | 0 | 0 |
| junit | 3 | 0 | 0 | 0 | 0 | 0 |

## 자바 백엔드 과정 (`java-backend`)

| # | 수업 | revision | 스텝 | 언어 | ready(Win/Mac) | 해설 code_flow | caution 스텝 | PRD | cases | 선수 |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 1 | `bash-basics` Bash · 파일과 폴더를 다루는 기본 명령 | bash-basics-7 | 24 | git:24 | 0/0 | 0 | 6 | O | X | 없음 |
| 2 | `java-values` 자바 · 값이 계산되고 표시되는 과정 | java-values-9 | 10 | java:10 | 10/10 | 0 | 8 | O | O | 없음 |
| 3 | `vim-basics` Vim · 직접 편집하며 익히는 기본 조작 | vim-basics-5 | 15 | git:15 | 0/0 | 0 | 4 | O | X | bash-basics |
| 4 | `java-launch` 자바 · 파일 하나를 실행하고 다시 빌드해요 | java-launch-7 | 9 | java:9 | 0/0 | 0 | 2 | O | X | bash-basics, java-values |
| 5 | `java-conditions` 자바 · 비교로 배송비를 고르는 과정 | java-conditions-10 | 9 | java:9 | 9/9 | 1 | 8 | O | O | java-values |
| 6 | `java-arrays` 자바 · 배열을 따라 가격을 더해요 | java-arrays-10 | 9 | java:9 | 9/9 | 1 | 9 | O | O | java-conditions |
| 7 | `java-methods` 자바 · 계산을 메서드로 나눠요 | java-methods-9 | 9 | java:9 | 9/9 | 1 | 9 | O | O | java-arrays |
| 8 | `java-arguments` 자바 · 실행할 때 값을 전달해요 | java-arguments-8 | 9 | java:9 | 0/0 | 0 | 6 | O | X | java-launch, java-arrays |
| 9 | `bash-variables` Bash · 변수에 값을 담고 꺼내요 | bash-variables-1 | 7 | git:7 | 0/0 | 0 | 2 | O | X | bash-basics |
| 10 | `bash-environment` Bash · export로 자식 프로세스에 값을 전해요 | bash-environment-1 | 6 | git:6 | 0/0 | 0 | 2 | O | X | bash-variables |
| 11 | `bash-command-env-args` Bash · 명령 한 번의 환경 값과 실행 인자 | bash-command-env-args-1 | 5 | git:4/java:1 | 0/0 | 0 | 3 | O | X | bash-environment, java-arguments |
| 12 | `git-first` Git · 내 파일이 기록이 되는 과정 | git-first-9 | 7 | git:7 | 0/0 | 0 | 7 | O | X | bash-basics |
| 13 | `java-references` 자바 · 객체와 참조를 나눠 봐요 | java-references-11 | 11 | java:11 | 11/11 | 1 | 11 | O | O | java-methods |
| 14 | `java-static` 자바 · 객체의 값과 static을 나눠요 | java-static-10 | 9 | java:9 | 9/9 | 1 | 9 | O | O | java-references |
| 15 | `java-roles` 상태를 지키고 객체의 역할을 나눠요 | java-roles-8 | 9 | java:9 | 9/9 | 1 | 9 | O | O | java-references |
| 16 | `java-collections` 주문 목록·태그·상품 수를 다뤄요 | java-collections-8 | 11 | java:11 | 11/11 | 0 | 11 | O | O | java-references |
| 17 | `java-class-objects` 클래스와 객체 · 상태를 가진 객체가 스스로 규칙을 지켜요 | java-class-objects-3 | 9 | java:9 | 9/9 | 0 | 8 | O | O | java-collections, java-roles |
| 18 | `java-inheritance-composition` 상속과 컴포지션 · 호출할 메서드는 실제 객체가 정해요 | java-inheritance-composition-3 | 8 | java:8 | 8/8 | 0 | 6 | O | O | java-class-objects |
| 19 | `java-streams` 자바 스트림 · 가격을 고르고 바꾸고 합산해요 | java-streams-8 | 11 | java:11 | 11/11 | 0 | 11 | O | O | java-collections |
| 20 | `java-files` 글을 파일에 남기고 실패도 처리해요 | java-files-9 | 11 | java:11 | 3/3 | 0 | 11 | O | O | java-roles |
| 21 | `java-testing` 배송비 변경을 작은 테스트로 검증해요 | java-testing-8 | 9 | java:6/junit:3 | 6/6 | 0 | 9 | O | O | java-roles |
| 22 | `java-oop-patterns` 객체지향 패턴 · 바뀌는 부분을 객체로 떼어 내요 | java-oop-patterns-3 | 7 | java:7 | 7/7 | 0 | 5 | O | O | java-inheritance-composition, java-streams, java-testing |
| 23 | `git-branch` Git · 브랜치 기본: 작업을 나누고 합쳐요 | git-branch-11 | 15 | git:15 | 0/0 | 0 | 13 | O | X | git-first |
| 24 | `git-remote` 공유 기록을 받고 비교하고 되돌려요 | git-remote-13 | 23 | git:23 | 0/0 | 0 | 22 | O | X | git-branch |
| 25 | `git-branch-advanced` Git · 브랜치 심화: 갈라진 기록과 충돌을 해결해요 | git-branch-advanced-10 | 6 | git:6 | 0/0 | 0 | 6 | O | X | git-remote |
| 26 | `github-pr` GitLab · MR로 변경을 검토하고 합쳐요 | gitlab-mr-1 | 9 | git:9 | 0/0 | 0 | 0 | O | X | git-branch-advanced |
| 27 | `java-regex` 정규식 · 문자열을 나누고 형식을 확인해요 | java-regex-6 | 8 | java:8 | 8/8 | 0 | 8 | O | O | java-collections, java-roles |
| 28 | `java-rq` Rq · 요청에서 명령과 값을 꺼내요 | java-rq-7 | 13 | java:13 | 13/13 | 0 | 12 | O | O | java-regex, java-streams |
| 29 | `java-calculator` 계산기 · 연산 순서와 괄호를 해석해요 | java-calculator-7 | 11 | java:11 | 11/11 | 0 | 11 | O | O | java-regex, java-methods |
| 30 | `java-crud` 같은 글 앱에서 추가·조회·수정·삭제를 연결해요 | java-crud-10 | 11 | java:11 | 9/9 | 0 | 11 | O | O | java-files, java-collections, java-testing |
| 31 | `docker-image-container` 이미지와 컨테이너 · 지워도 남는 것과 사라지는 것 | docker-image-container-7 | 13 | docker:13 | 0/0 | 0 | 11 | O | O | bash-basics |
| 32 | `gitlab-ci` GitLab CI/CD · 검사와 산출물을 자동으로 이어 가요 | gitlab-ci-1 | 10 | git:10 | 0/0 | 0 | 0 | O | X | github-pr, docker-image-container |
| 33 | `docker-network-ports` Docker 네트워크 · localhost는 누구인가요 | docker-network-ports-4 | 4 | docker:4 | 0/0 | 0 | 4 | O | O | docker-image-container |
| 34 | `sql-first` SQL 기초 · 행을 고르고 값을 바꾼다는 것 | sql-first-6 | 18 | docker:18 | 0/0 | 0 | 18 | O | O | docker-image-container |
| 35 | `sql-tables-constraints` MySQL · 화면을 우회해도 데이터 규칙을 지켜요 | sql-tables-constraints-5 | 6 | docker:6 | 0/0 | 0 | 6 | O | O | sql-first |
| 36 | `sql-join-group` JOIN·집계 · 사라진 행과 늘어난 합계를 찾아요 | sql-join-group-5 | 6 | docker:6 | 0/0 | 0 | 6 | O | O | sql-tables-constraints |
| 37 | `sql-transactions` 트랜잭션 · 절반만 끝난 이체를 막아요 | sql-transactions-5 | 5 | docker:5 | 0/0 | 0 | 5 | O | O | sql-tables-constraints |
| 38 | `h2-memory-file` H2 · 연결을 닫는 것과 프로그램을 끄는 것은 달라요 | h2-memory-file-4 | 5 | java_libraries:5 | 0/0 | 0 | 5 | O | O | sql-first, java-files |
| 39 | `java-jdbc` JDBC · 코드와 데이터베이스 사이의 계약 | java-jdbc-4 | 4 | java_libraries:4 | 0/0 | 0 | 4 | O | O | h2-memory-file, sql-transactions |
| 40 | `sql-index-plan` 인덱스 · 답은 같은데 찾는 경로가 달라요 | sql-index-plan-5 | 4 | docker:4 | 0/0 | 0 | 4 | O | O | sql-join-group |
| 41 | `sql-isolation-locks` 격리·잠금 · 동시에 읽은 값이 서로를 덮어요 | sql-isolation-locks-4 | 4 | docker:4 | 0/0 | 0 | 4 | O | O | java-jdbc, sql-transactions |
| 42 | `docker-compose-db` Compose·DB · 컨테이너를 바꿔도 데이터는 남겨요 | docker-compose-db-5 | 3 | docker:3 | 0/0 | 0 | 3 | O | O | docker-network-ports, sql-tables-constraints |
| 43 | `java-tailwind` CSS에서 Tailwind까지 · 규칙과 배치를 이해해요 | java-tailwind-6 | 24 | web:24 | 0/0 | 0 | 11 | O | O | 없음 |
| 44 | `java-react` React 원리 · 직접 DOM을 고치던 코드가 상태에서 화면을 계산하기까지 | java-react-6 | 22 | web:22 | 0/0 | 0 | 3 | O | O | java-tailwind |

## 정보처리기사 실기 과정 (`engineer-practical`)

| # | 수업 | revision | 스텝 | 언어 | ready(Win/Mac) | 해설 code_flow | caution 스텝 | PRD | cases | 선수 |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 1 | `engineer-c-start` C 값과 대입을 순서대로 읽어요 | engineer-c-start-8 | 7 | c:7 | 7/7 | 0 | 7 | O | O | 없음 |
| 2 | `engineer-c-conditions` C 연산과 조건을 읽어요 | engineer-c-conditions-8 | 9 | c:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 3 | `engineer-c-arrays` C 반복과 배열을 읽어요 | engineer-c-arrays-8 | 11 | c:11 | 11/11 | 0 | 11 | O | O | 없음 |
| 4 | `engineer-c-functions` C 함수와 재귀를 따라가요 | engineer-c-functions-9 | 11 | c:11 | 11/11 | 1 | 11 | O | O | 없음 |
| 5 | `engineer-c-pointers` C · 주소와 가리키는 값을 나눠 봐요 | engineer-c-pointers-9 | 11 | c:11 | 11/11 | 1 | 11 | O | O | 없음 |
| 6 | `engineer-c-double-pointers` C · 다중 포인터의 층을 따라가요 | engineer-c-double-pointers-8 | 9 | c:9 | 9/9 | 2 | 9 | O | O | 없음 |
| 7 | `engineer-c-structures` C · 구조체와 계산 규칙을 골라요 | engineer-c-structures-9 | 19 | c:19 | 19/19 | 0 | 19 | O | O | 없음 |
| 8 | `engineer-java-flow` Java · 재고 계산의 실행 순서를 읽어요 | engineer-java-flow-9 | 9 | java:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 9 | `engineer-java-references` Java · 같은 객체와 다른 이름을 구별해요 | engineer-java-references-8 | 9 | java:9 | 9/9 | 2 | 9 | O | O | 없음 |
| 10 | `engineer-java-static` Java · 공유 번호와 생성 순서를 읽어요 | engineer-java-static-8 | 9 | java:9 | 9/9 | 1 | 9 | O | O | 없음 |
| 11 | `engineer-java-polymorphism` Java · 호출 규칙과 예외 뒤 순서를 읽어요 | engineer-java-polymorphism-7 | 9 | java:9 | 9/9 | 1 | 9 | O | O | 없음 |
| 12 | `engineer-python-values` Python · 같은 창고 자료를 골라 읽어요 | engineer-python-values-9 | 9 | python:9 | 9/9 | 1 | 9 | O | O | 없음 |
| 13 | `engineer-python-calls` Python · 같은 재고 함수의 호출을 읽어요 | engineer-python-calls-9 | 11 | python:11 | 11/11 | 2 | 11 | O | O | 없음 |
| 14 | `engineer-db-model` DB · 같은 물건을 표와 키로 구별해요 | engineer-db-model-7 | 9 | python:5/sql:4 | 5/5 | 0 | 9 | O | O | 없음 |
| 15 | `engineer-sql-select` SQL · 같은 재고의 조건과 연결을 읽어요 | engineer-sql-select-7 | 11 | sql:11 | 0/0 | 0 | 11 | O | O | 없음 |
| 16 | `engineer-sql-group` SQL · 같은 재고의 그룹과 순서를 읽어요 | engineer-sql-group-8 | 11 | sql:11 | 0/0 | 0 | 11 | O | O | 없음 |
| 17 | `engineer-sql-change` SQL · 같은 재고의 변경과 권한을 구별해요 | engineer-sql-change-7 | 11 | sql:11 | 0/0 | 0 | 10 | O | O | 없음 |
| 18 | `engineer-db-storage` DB · 종속·저장·조회 로직의 역할을 읽어요 | engineer-db-storage-6 | 19 | python:19 | 0/0 | 0 | 18 | O | O | 없음 |
| 19 | `engineer-requirements` 요구사항 · 같은 재고 규칙을 확인해요 | engineer-requirements-5 | 9 | python:9 | 0/0 | 0 | 8 | O | O | 없음 |
| 20 | `engineer-design` 설계 · 같은 창구의 모델과 패턴을 구별해요 | engineer-design-6 | 28 | python:28 | 0/0 | 0 | 26 | O | O | 없음 |
| 21 | `engineer-server` 서버 · 같은 업무의 책임과 실행을 나눠요 | engineer-server-6 | 23 | python:23 | 0/0 | 0 | 21 | O | O | 없음 |
| 22 | `engineer-interfaces` 연계 · 같은 창고 요청의 약속을 읽어요 | engineer-interfaces-6 | 11 | python:11 | 0/0 | 0 | 10 | O | O | 없음 |
| 23 | `engineer-ui` 화면 · 같은 정정 요청을 끝까지 이어 봐요 | engineer-ui-4 | 9 | python:9 | 0/0 | 0 | 8 | O | O | 없음 |
| 24 | `engineer-test-cases` 테스트 · 같은 수량 규칙의 반례를 찾아요 | engineer-test-cases-6 | 9 | python:9 | 0/0 | 0 | 7 | O | O | 없음 |
| 25 | `engineer-test-integration` 테스트 · 같은 서비스의 연결과 범위를 읽어요 | engineer-test-integration-6 | 11 | python:11 | 0/0 | 0 | 9 | O | O | 없음 |
| 26 | `engineer-security` 보안 · 같은 재고 서비스의 경계를 지켜요 | engineer-security-6 | 15 | python:15 | 0/0 | 0 | 13 | O | O | 없음 |
| 27 | `engineer-os` 운영체제 · 같은 작업의 시간과 자원을 읽어요 | engineer-os-8 | 15 | python:15 | 1/1 | 0 | 14 | O | O | 없음 |
| 28 | `engineer-network` 네트워크 · 같은 창고의 주소와 전송을 읽어요 | engineer-network-7 | 15 | python:15 | 1/1 | 0 | 12 | O | O | 없음 |
| 29 | `engineer-build` 배포 · 같은 수정의 출처와 버전을 남겨요 | engineer-build-6 | 11 | python:11 | 0/0 | 0 | 9 | O | O | 없음 |
| 30 | `engineer-mixed` 종합 · 같은 재고 보고의 답안을 연결해요 | engineer-mixed-7 | 15 | python:8/sql:3/c:2/java:2 | 7/7 | 0 | 15 | O | O | 없음 |

## AICE Associate 과정 (`aice-associate`)

| # | 수업 | revision | 스텝 | 언어 | ready(Win/Mac) | 해설 code_flow | caution 스텝 | PRD | cases | 선수 |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 1 | `aice-python-start` 표를 다루기 위한 파이썬 첫 걸음 | aice-python-start-8 | 8 | python:8 | 8/8 | 0 | 8 | O | O | 없음 |
| 2 | `aice-python-conditions` 조건에 따라 배송 자료를 골라요 | aice-python-conditions-10 | 9 | python:9 | 9/9 | 1 | 8 | O | O | 없음 |
| 3 | `aice-python-api` 묶은 자료와 라이브러리 기능을 읽어요 | aice-python-api-8 | 9 | python:9 | 9/9 | 1 | 9 | O | O | 없음 |
| 4 | `aice-table-csv` 배송 표를 보고 CSV로 읽어요 | aice-table-csv-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 5 | `aice-selection` 필요한 배송을 고르고 요약해요 | aice-selection-7 | 11 | python:11 | 11/11 | 0 | 11 | O | O | 없음 |
| 6 | `aice-quality` 비거나 중복된 배송 자료를 살펴봐요 | aice-quality-7 | 11 | python:11 | 11/11 | 0 | 10 | O | O | 없음 |
| 7 | `aice-join` 여러 배송 파일을 같은 키로 연결해요 | aice-join-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 8 | `aice-plots` 그림의 높이와 원래 자료를 비교해요 | aice-plots-7 | 11 | python:11 | 11/11 | 0 | 11 | O | O | 없음 |
| 9 | `aice-features` 예측에 쓸 열의 의미를 확인해요 | aice-features-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 10 | `aice-split` 입력과 정답을 함께 나눠요 | aice-split-8 | 11 | python:11 | 11/11 | 0 | 11 | O | O | 없음 |
| 11 | `aice-leakage` 남겨둔 정보가 새어 들어오는지 봐요 | aice-leakage-6 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 12 | `aice-scale` 훈련에서 배운 전처리 기준을 적용해요 | aice-scale-7 | 10 | python:10 | 10/10 | 0 | 10 | O | O | 없음 |
| 13 | `aice-regression` 거리에서 배송 시간을 예측해요 | aice-regression-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 14 | `aice-regression-metrics` 예측 오차를 목적에 맞게 읽어요 | aice-regression-metrics-8 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 15 | `aice-classification` 배송의 지연 종류를 예측해요 | aice-classification-8 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 16 | `aice-classification-metrics` 지연 경보의 성능을 판단해요 | aice-classification-metrics-8 | 11 | python:11 | 11/11 | 0 | 11 | O | O | 없음 |
| 17 | `aice-models` 같은 배송 자료로 여러 모델을 비교해요 | aice-models-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 18 | `aice-boosting` 부스팅의 학습 설정과 예측을 읽어요 | aice-boosting-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 19 | `aice-tuning` 검증 자료를 지키며 설정을 비교해요 | aice-tuning-6 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 20 | `aice-tensorflow` TensorFlow의 구성·학습·예측을 구별해요 | aice-tensorflow-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 21 | `aice-neural-regression` 신경망 회귀의 출력과 평가를 맞춰요 | aice-neural-regression-8 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 22 | `aice-neural-classification` 신경망 분류의 출력과 정답을 맞춰요 | aice-neural-classification-8 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 23 | `aice-training` 학습 기록을 보고 개선 방법을 판단해요 | aice-training-7 | 9 | python:9 | 9/9 | 0 | 9 | O | O | 없음 |
| 24 | `aice-integration` 파일부터 전처리·모델·결과까지 연결해요 | aice-integration-7 | 11 | python:11 | 11/11 | 0 | 11 | O | O | 없음 |
