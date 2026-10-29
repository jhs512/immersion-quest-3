# 마지막 도전 실제 채점 증거 (이번 변경 78수업)

`python tools/final_challenges/_evidence_summary.py`가 `target/final-challenges/<키>.json`과 지금 수업 바이트를 비교해 만든 표예요. 자바 코드 수업은 `cargo run --example validate_redesigned_lesson -- tests/lesson-cases/<키>.json target/final-challenges/<키>.json`, 터미널 수업은 `cargo test --test final_terminal_challenges`, GitHub 수업은 `cargo test --test github_pr real_github_final_challenge -- --ignored`가 증거를 써요. 기존 백엔드 코드 증거는 수업 전체 사례, 터미널 및 새 두 과정 증거는 도전 하나의 사례를 셀 수 있어요. 새 두 과정의 기존 문제는 게시 도구가 공개 버전과 바이트 단위로 동일한지 검사해요. 이 표는 실제 음성을 들었다거나 화면 검수를 끝냈다는 뜻이 아니에요.

| 수업 | 버전 | 도전 스텝 | 제목 | 실행 | 동등 풀이 통과 | 오답·우회 거절 | 상태 | 수업 sha256 앞 16자 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bash-basics | bash-basics-7 | `stp_04bd4e0f-f236-4bc2-9b1d-5d6c13f74eac` | 어지러운 연습 폴더를 목표대로 정리하세요 | bash | 2 | 5 | 통과·해시 일치 | `6d4df77f8df596d4` |
| java-values | java-values-8 | `stp_4c1b8f0e-6d2a-4f57-9a3e-0b7c5d81e2a4` | 합계를 출력하고 저장한 수량도 출력하세요 | 실제 JDK | 11 | 22 | 통과·해시 일치 | `804994033ad2eb79` |
| vim-basics | vim-basics-5 | `stp_b4149a72-f735-446d-b970-05187441ef62` | 장보기 목록을 고쳐 저장하고 끝내세요 | vim | 2 | 3 | 통과·해시 일치 | `cdec8b183d1dc1cf` |
| java-launch | java-launch-7 | `stp_6367375b-819a-4934-8cc8-2214882a9b50` | 바꾼 문구를 클래스 파일로 배포하세요 | bash+jdk | 3 | 4 | 통과·해시 일치 | `c14589808e815ef8` |
| java-conditions | java-conditions-9 | `stp_7d2e9a41-3c58-4b1f-8e06-a95c2d17f3b8` | 세 구간 배송비와 안내 문구를 직접 정하세요 | 실제 JDK | 9 | 20 | 통과·해시 일치 | `aee958ccef4331fe` |
| java-arrays | java-arrays-9 | `stp_5e8a1d36-92c4-4f7b-a1d0-3c6b8e27f94a` | 2,000원 이상 가격의 합계와 개수를 구하세요 | 실제 JDK | 9 | 20 | 통과·해시 일치 | `765a118aeb49e93e` |
| java-methods | java-methods-8 | `stp_3a9f6c28-e1d4-4b85-9f72-6d0e8b13a5c9` | 합계와 배송비 메서드를 완성해 결제 금액을 출력하세요 | 실제 JDK | 7 | 17 | 통과·해시 일치 | `daac8c65196e258e` |
| java-arguments | java-arguments-8 | `stp_86e157bf-bbb1-4709-8ddf-7032baca1f96` | 메모와 주문 코드를 제자리에서 읽게 하세요 | bash+jdk | 3 | 4 | 통과·해시 일치 | `569449cae263ee58` |
| git-first | git-first-9 | `stp_b752762e-e893-4042-9135-c43787c64719` | 빈 폴더에서 할 일 목록을 두 번 기록하세요 | git+bash | 2 | 4 | 통과·해시 일치 | `e4154f342786571b` |
| java-references | java-references-10 | `stp_8b3e5a19-4c72-4d06-a9f1-2e6c7b04d38f` | 별칭으로 바꾸고 복사본은 지키세요 | 실제 JDK | 8 | 17 | 통과·해시 일치 | `ba8923c570c494ec` |
| java-static | java-static-9 | `stp_6c2f8e15-9a47-4b3d-b8e0-5d1a3f72c94e` | 주문별 금액과 공유 주문 수를 직접 나누세요 | 실제 JDK | 7 | 16 | 통과·해시 일치 | `a659196eefc38625` |
| java-roles | java-roles-7 | `stp_2d8b4f61-7e39-4a52-9c16-b0e3d5a8f7c2` | 회원 배송비 정책을 끼우고 지갑의 규칙을 지키세요 | 실제 JDK | 5 | 15 | 통과·해시 일치 | `644a1ece5408eea8` |
| java-collections | java-collections-8 | `stp_9e4c7a83-2b15-4f6d-8a39-c5d0e6b21f74` | 상품 종류 수와 상품별 개수를 함께 구하세요 | 실제 JDK | 8 | 13 | 통과·해시 일치 | `5d52f898e2c453a1` |
| java-inheritance-composition | java-inheritance-composition-3 | `stp_4f9d2b67-8c31-4e5a-b7d0-1a6e3c94f825` | 새 배송 두 종류의 배송비가 영수증에 반영되게 하세요 | 실제 JDK | 5 | 10 | 통과·해시 일치 | `f3be84512608d24c` |
| java-streams | java-streams-8 | `stp_1c7e4a92-5b38-4d6f-9e21-8a0d3f6b5c47` | 기준 이상 가격의 개수·할인 합계·최고가를 구하세요 | 실제 JDK | 10 | 20 | 통과·해시 일치 | `6ffd9e56dbe8abfb` |
| java-files | java-files-8 | `stp_7a5d3e18-6f92-4c4b-a0d7-2b8e1c96f43d` | 방문 기록을 덧붙이고 잘못된 줄을 건너뛰며 합계를 내세요 | 실제 JDK | 7 | 20 | 통과·해시 일치 | `e310bc4a4f8393b8` |
| java-testing | java-testing-8 | `stp_5b0e8c43-1d76-4a29-b3f8-9c2d6e75a1f0` | 새 적립 규칙의 테스트를 직접 쓰세요 | 실제 채점기 | 7 | 14 | 통과·해시 일치 | `ad22d9f1e1736f1f` |
| git-branch | git-branch-11 | `stp_2083b3dd-20f1-4b1c-9937-d2f70bfb6a1b` | 두 기능을 브랜치로 차례로 개발하세요 | git+bash | 2 | 4 | 통과·해시 일치 | `d0306f1085a09eb0` |
| git-remote | git-remote-12 | `stp_94d0da62-e0db-47a2-aaef-8ad0cf722e8a` | 동료의 변경과 합쳐 내 운영 시간 커밋을 공유하세요 | git+bash | 2 | 4 | 통과·해시 일치 | `193d167c5c931327` |
| git-branch-advanced | git-branch-advanced-10 | `stp_6b96f92f-1312-42a2-8b23-7f4eb545dae5` | 두 의도를 살려 갈라진 안내를 병합하세요 | git+bash | 2 | 5 | 통과·해시 일치 | `15cfe49bb437fcd0` |
| github-pr | github-pr-6 | `stp_2d42bbda-b942-4f8a-ba7a-beeceb7e8086` | 새 저장소에서 GitHub Flow 전체를 혼자 마치세요 | 실제 채점기 |  |  | 증거 없음 | `6f7060e086e10801` |
| java-rq | java-rq-7 | `stp_3d6b9f52-8a17-4e4c-b9a5-1c0e7d82f36b` | 빈 Rq를 완성해 목록 요청을 해석하세요 | 실제 JDK | 8 | 17 | 통과·해시 일치 | `fdcdd9d531866db9` |
| java-calculator | java-calculator-7 | `stp_8f1a6c34-7e29-4d5b-a3c8-0b9d2e64f71a` | 뺄셈을 덧셈과 같은 단계에서 왼쪽부터 계산하세요 | 실제 JDK | 6 | 14 | 통과·해시 일치 | `33a4a3ec70438b63` |
| java-crud | java-crud-9 | `stp_6a2e8d71-4f39-4b6c-8d05-7c1f3b94e2a8` | 네 동작의 규칙을 지키는 글 서비스를 완성하세요 | 실제 JDK | 9 | 15 | 통과·해시 일치 | `49e56aa593395649` |
| aice-python-start | aice-python-start-6 | `stp_5b8e2c47-1d93-4f6a-a2e0-7c4b9d31f8e6` | 건수가 바뀌는 목록의 처음과 끝을 읽으세요 | 실제 Python | 1 | 3 | 통과·해시 일치 | `b33328a5fca71f0f` |
| aice-python-conditions | aice-python-conditions-7 | `stp_981a0d0f-555b-492d-87c6-b668734543df` | 기준 이상인 배송을 모아 건수를 세세요 | 실제 Python | 1 | 3 | 통과·해시 일치 | `22d379ce12288344` |
| aice-python-api | aice-python-api-6 | `stp_3ec1a5c3-b2a2-46e2-83c1-6d6ad7ebf28a` | 배송 기록에서 건수·평균·정렬 목록을 꺼내세요 | 실제 Python | 1 | 3 | 통과·해시 일치 | `2653f645ebedb3a8` |
| aice-table-csv | aice-table-csv-6 | `stp_85c153cc-a269-4604-a699-06c7cd6342dc` | 배송 파일의 크기를 보고 두 열만 남기세요 | 실제 Python | 1 | 3 | 통과·해시 일치 | `bd379af8f912f5b8` |
| aice-selection | aice-selection-6 | `stp_5f220155-e726-403c-bb0c-82bc73056881` | 두 조건으로 고르고 정렬해 요약하세요 | 실제 Python | 1 | 4 | 통과·해시 일치 | `655b3f20beab9d4c` |
| aice-quality | aice-quality-6 | `stp_57fb87ab-7ab9-48e8-94d2-5cb5e2869448` | 측정 못한 시간과 옛 수정본을 정리하세요 | 실제 Python | 1 | 3 | 통과·해시 일치 | `633739080f88a922` |
| aice-join | aice-join-6 | `stp_b05f4187-a8de-4b39-9235-d20c619977f6` | 두 달 배송을 붙이고 지역별로 세세요 | 실제 Python | 1 | 3 | 통과·해시 일치 | `f3228f27cec32264` |
| aice-plots | aice-plots-6 | `stp_037eb885-a668-43ed-9619-6e48c0f3c20e` | 끝난 배송으로 지역별 평균 시간 막대를 만드세요 | 실제 Python | 1 | 4 | 통과·해시 일치 | `03a06d08e7e0dfe2` |
| aice-features | aice-features-6 | `stp_dd7ffb3c-b10c-483d-a1a1-e7a41d7f5563` | 접수할 때 아는 입력 표를 만드세요 | 실제 Python | 1 | 4 | 통과·해시 일치 | `da2e3484b12aa4b5` |
| aice-split | aice-split-6 | `stp_4664135d-7073-47a2-9c52-b0081fafd1f9` | 배송 번호와 정답을 층화해 함께 나누세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `a79c106a1ffd4ea4` |
| aice-leakage | aice-leakage-5 | `stp_aea6a5c7-61a8-48bd-b46f-891d15963afb` | 접수 시점의 열과 훈련 기준만 남기세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `c9e07ea5b7df36d3` |
| aice-scale | aice-scale-6 | `stp_d9e36990-e641-4647-b0f0-ea0bdc24acf5` | 훈련 평균으로 채운 뒤 같은 척도로 바꾸세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `7d89b3a26655420e` |
| aice-regression | aice-regression-5 | `stp_8f967e0e-fb58-44c3-b9ba-2b94b21bb01b` | 남겨둔 배송으로 기준 모델과 회귀를 비교하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `ae03aeabc345d02b` |
| aice-regression-metrics | aice-regression-metrics-6 | `stp_8c2d0bff-a5ed-444e-9b9d-811d3b88f5b2` | 배송 번호를 맞추고 세 오차를 보고하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `86633e0d65d4fcb7` |
| aice-classification | aice-classification-6 | `stp_91a6a75b-ce1e-47e5-9d88-de2b221813f0` | 지연 확률의 열을 찾아 기준 이상을 알리세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `53b8b500124f9b27` |
| aice-classification-metrics | aice-classification-metrics-6 | `stp_208e0760-9120-4546-a215-6633fba1ea5a` | 기준 경보의 지연 정밀도와 재현율을 구하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `a6546f11a625d83f` |
| aice-models | aice-models-5 | `stp_8f1aa06f-612a-433b-986b-d09b20cc2c46` | 같은 검증 오차로 두 후보 중 하나를 고르세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `a0821a9fbc3da8bd` |
| aice-boosting | aice-boosting-5 | `stp_a5d75177-1ef8-4bf6-a518-1e1a0697176d` | 반영 비율과 반복 횟수를 학습에 연결하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `556bdc93c48c1459` |
| aice-tuning | aice-tuning-5 | `stp_d425c897-1d63-4d4d-b506-2a6226b835eb` | 파이프라인 후보를 연결하고 오차 방향을 맞추세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `c5eb716cde61a842` |
| aice-tensorflow | aice-tensorflow-5 | `stp_228a312c-44f8-4f1f-bab3-2aaa29978f5c` | 배송 특성 수와 예측 한 칸을 연결하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `7cab9a3ee077b983` |
| aice-neural-regression | aice-neural-regression-6 | `stp_1e68bc14-fc5b-4c8d-b02f-50f1b0a61b82` | 음수가 없는 시간 예측과 회귀 오차를 맞추세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `8415b73382e360d5` |
| aice-neural-classification | aice-neural-classification-6 | `stp_6e8529c4-201c-4b8d-b922-550464a4336e` | 정수 정답과 다중 확률을 종류 이름에 연결하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `03894041f863573b` |
| aice-training | aice-training-6 | `stp_99547a1f-d0b3-4cd7-87e9-3658ad90b2f3` | 정한 횟수만 기다리고 가장 좋던 가중치를 복원하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `1ebc11d1b95659e7` |
| aice-integration | aice-integration-6 | `stp_86d1f031-ffaa-4e3d-8aef-d112f66496fd` | 처음 보는 지역도 예측하고 주문번호와 함께 내보내세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `6a06c80d88bb632b` |
| engineer-c-start | engineer-c-start-6 | `stp_403cbc4b-4f0b-45f6-b4ba-8e4e237d2f5d` | 출고 전후의 값을 서로 다른 변수에 기록하세요 | 실제 C | 1 | 1 | 통과·해시 일치 | `fd40a51007648ac3` |
| engineer-c-conditions | engineer-c-conditions-6 | `stp_dc7e47b4-96cc-49e9-9865-af75a871cc94` | 완성 상자와 추가로 필요한 낱개를 계산하세요 | 실제 C | 1 | 1 | 통과·해시 일치 | `a5d4f10b700e1fec` |
| engineer-c-arrays | engineer-c-arrays-6 | `stp_23473fd3-7d92-4ed4-bcb7-382927ce49c1` | 모든 재고의 합과 첫 최대 위치를 구하세요 | 실제 C | 1 | 1 | 통과·해시 일치 | `23e2ccdf582e25de` |
| engineer-c-functions | engineer-c-functions-6 | `stp_dba636c3-ea11-4e6d-9eca-5d3006fb7b12` | 재귀가 돌려준 부분 합에 현재 수를 더하세요 | 실제 C | 1 | 1 | 통과·해시 일치 | `af5d25527088af0d` |
| engineer-c-pointers | engineer-c-pointers-6 | `stp_72d91c6d-4814-4b28-90c8-92f78ba9f667` | 두 원래 재고를 포인터로 교환하세요 | 실제 C | 1 | 1 | 통과·해시 일치 | `cd7aa1706688d658` |
| engineer-c-double-pointers | engineer-c-double-pointers-6 | `stp_91b12cbe-e1be-4225-a7da-ff05510ff2a4` | 최소 재고를 가리키도록 호출자의 포인터를 바꾸세요 | 실제 C | 1 | 1 | 통과·해시 일치 | `24b7dcedee0cb839` |
| engineer-c-structures | engineer-c-structures-6 | `stp_9be10228-3f66-4600-876e-589546f4a886` | 구조체 배열에 선택한 가격 규칙을 적용하세요 | 실제 C | 1 | 1 | 통과·해시 일치 | `c558ab2a7c540e32` |
| engineer-java-flow | engineer-java-flow-6 | `stp_81d6934e-8cf9-47b5-bf45-4ae4beb83506` | 건너뛸 값과 종료 표시를 구별해 합산하세요 | 실제 JDK | 1 | 1 | 통과·해시 일치 | `0dcca7645f515fa9` |
| engineer-java-references | engineer-java-references-5 | `stp_386c6124-e3ed-4cab-8223-61ef33179153` | 주문별 수량 배열을 독립적으로 보관하세요 | 실제 JDK | 1 | 1 | 통과·해시 일치 | `40b151ae96e48336` |
| engineer-java-static | engineer-java-static-5 | `stp_1b79ae00-24ed-4ce1-bc83-5ee7121d3a93` | 생성된 객체에만 다음 발급 번호를 부여하세요 | 실제 JDK | 1 | 1 | 통과·해시 일치 | `8fc50daa2d5906eb` |
| engineer-java-polymorphism | engineer-java-polymorphism-5 | `stp_045de1e3-6968-4517-b056-6ef2e6b13549` | 필드·재정의·finally의 결과를 나눠 적으세요 | 실행 예제 + 직접 답 입력 | 0 | 3 | 통과·해시 일치 | `75379c8f375a85ee` |
| engineer-python-values | engineer-python-values-6 | `stp_db97db2a-0c84-44da-947f-0cce41a180db` | 중첩 목록을 독립적으로 고치고 없는 키를 읽으세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `7869a4541d3c7cca` |
| engineer-python-calls | engineer-python-calls-5 | `stp_a474fa8a-a0c0-4eaa-99c8-31d2a5b908cf` | 생략한 기록 목록은 호출마다 새로 만드세요 | 실제 Python | 1 | 1 | 통과·해시 일치 | `7bb44d80ef9e7ada` |
| engineer-db-model | engineer-db-model-6 | `stp_73e5ef52-9e58-4426-9b17-b8437b6262ca` | 배송 표에 식별·필수값·참조 규칙을 선언하세요 | 실제 Python | 1 | 2 | 통과·해시 일치 | `54c8f98ed721c0d1` |
| engineer-sql-select | engineer-sql-select-6 | `stp_ef3e9f35-932e-48d2-9d3f-6e8ff8368305` | 재주문할 물건은 공급처가 없어도 남기세요 | 실제 SQLite | 1 | 2 | 통과·해시 일치 | `47c9700db053ff9d` |
| engineer-sql-group | engineer-sql-group-6 | `stp_5c00ddd4-5de1-497b-85d6-15f8c7989885` | 양수 재고만 모아 기준을 넘는 분류를 보고하세요 | 실제 SQLite | 1 | 2 | 통과·해시 일치 | `c0d641640207e4d5` |
| engineer-sql-change | engineer-sql-change-6 | `stp_c373e085-db0d-4fab-8d0a-a8e7258d7699` | 확인 안 된 재고를 정정한 다음 빈 재고 행을 지우세요 | 실제 SQLite | 1 | 1 | 통과·해시 일치 | `45a827f712bff010` |
| engineer-db-storage | engineer-db-storage-6 | `stp_9d105c9e-0967-4781-9898-a32f4a72ac59` | 주문 표의 종속·조회·변경 사건을 판단하세요 | 사례별 직접 답 입력 | 2 | 3 | 통과·해시 일치 | `1289d7c27d6f5de3` |
| engineer-requirements | engineer-requirements-5 | `stp_0fb235ea-afe4-4401-9087-c04d884d4fb8` | 배송 요구와 검증·변경 영향을 연결하세요 | 사례별 직접 답 입력 | 3 | 3 | 통과·해시 일치 | `50e928bbdf978dce` |
| engineer-design | engineer-design-6 | `stp_154f7326-498e-4759-8140-67bb19c69a35` | 배송 서비스의 세 변경 지점에 패턴을 고르세요 | 사례별 직접 답 입력 | 3 | 3 | 통과·해시 일치 | `88003937eb3fedbd` |
| engineer-server | engineer-server-6 | `stp_01911fdc-baf2-4b3e-92a6-3444aaf1f152` | 모듈 의존과 야간 묶음 작업을 판단하세요 | 사례별 직접 답 입력 | 3 | 3 | 통과·해시 일치 | `010edf4b9249807b` |
| engineer-interfaces | engineer-interfaces-6 | `stp_4a7a35bf-e1df-402e-9d56-9c53914a714f` | 단위와 중복 요청의 효과를 계약으로 정하세요 | 사례별 직접 답 입력 | 3 | 3 | 통과·해시 일치 | `ca157368750b41a3` |
| engineer-ui | engineer-ui-4 | `stp_1dae794b-7426-4280-8001-5a135fb88242` | 수량 입력 오류에서 다음 행동을 찾게 하세요 | 사례별 직접 답 입력 | 1 | 3 | 통과·해시 일치 | `99186802f6c3adfe` |
| engineer-test-cases | engineer-test-cases-6 | `stp_857c59d1-be37-44d1-87fb-1ff207e08415` | 허용 범위의 양쪽 경계 밖 시험을 설계하세요 | 사례별 직접 답 입력 | 1 | 3 | 통과·해시 일치 | `edc0c03be519a384` |
| engineer-test-integration | engineer-test-integration-6 | `stp_2b70a79d-3d78-4fbb-b3d0-d4161348c5df` | 분기 커버리지와 통합 대역을 판단하세요 | 사례별 직접 답 입력 | 3 | 3 | 통과·해시 일치 | `0870a666c4592346` |
| engineer-security | engineer-security-6 | `stp_f46227a0-03c2-45de-a669-e8cc41328e4b` | 주문 조회 경계에서 보안 검사를 구별하세요 | 사례별 직접 답 입력 | 3 | 3 | 통과·해시 일치 | `d04b3af583ead5ce` |
| engineer-os | engineer-os-6 | `stp_7890e0b4-4fbe-4227-8b8b-16a903154e97` | 작업 대기와 페이지 교체를 끝까지 추적하세요 | 실행 예제 + 직접 답 입력 | 2 | 3 | 통과·해시 일치 | `e3525a2ee80f3ee5` |
| engineer-network | engineer-network-6 | `stp_8514f6bd-9f51-4c34-872d-b69b2be1b559` | 서브넷의 시작·끝·일반 호스트 수를 계산하세요 | 실행 예제 + 직접 답 입력 | 0 | 3 | 통과·해시 일치 | `1170f501a3347406` |
| engineer-build | engineer-build-6 | `stp_5dae5ecf-7b32-4d4c-b3c9-c400919a6c11` | 각 변경에 맞는 다음 릴리즈 버전을 정하세요 | 사례별 직접 답 입력 | 0 | 3 | 통과·해시 일치 | `b54d2039a857ac86` |
| engineer-mixed | engineer-mixed-6 | `stp_bcbe58d4-35f4-4f8d-b899-992f20c12b4c` | 코드·집계·테스트 경계를 한 번에 추적하세요 | 실행 예제 + 직접 답 입력 | 1 | 3 | 통과·해시 일치 | `8ede75c18dfd76a5` |
