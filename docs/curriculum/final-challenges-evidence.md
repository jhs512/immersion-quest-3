# 마지막 도전 실제 채점 증거 (백엔드 24수업)

`python tools/final_challenges/_evidence_summary.py`가 `target/final-challenges/<키>.json`과 지금 수업 바이트를 비교해 만든 표예요. 자바 코드 수업은 `cargo run --example validate_redesigned_lesson -- tests/lesson-cases/<키>.json target/final-challenges/<키>.json`, 터미널 수업은 `cargo test --test final_terminal_challenges`, GitHub 수업은 `cargo test --test github_pr real_github_final_challenge -- --ignored`가 증거를 써요. 자바 코드 수업의 동등/거절 수는 수업 전체 사례 수이고, 터미널 수업은 도전 하나의 사례 수예요.

| 수업 | 버전 | 도전 스텝 | 제목 | 실행 | 동등 풀이 통과 | 오답·우회 거절 | 상태 | 수업 sha256 앞 16자 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bash-basics | bash-basics-7 | `stp_04bd4e0f-f236-4bc2-9b1d-5d6c13f74eac` | 어지러운 연습 폴더를 목표대로 정리하세요 | bash | 2 | 5 | 통과·해시 일치 | `6d4df77f8df596d4` |
| java-values | java-values-8 | `stp_4c1b8f0e-6d2a-4f57-9a3e-0b7c5d81e2a4` | 합계를 출력하고 저장한 수량도 출력하세요 | real JDK (validate_redesigned_lesson) | 11 | 22 | 통과·해시 일치 | `804994033ad2eb79` |
| vim-basics | vim-basics-5 | `stp_b4149a72-f735-446d-b970-05187441ef62` | 장보기 목록을 고쳐 저장하고 끝내세요 | vim | 2 | 3 | 통과·해시 일치 | `cdec8b183d1dc1cf` |
| java-launch | java-launch-7 | `stp_6367375b-819a-4934-8cc8-2214882a9b50` | 바꾼 문구를 클래스 파일로 배포하세요 | bash+jdk | 3 | 4 | 통과·해시 일치 | `c14589808e815ef8` |
| java-conditions | java-conditions-9 | `stp_7d2e9a41-3c58-4b1f-8e06-a95c2d17f3b8` | 세 구간 배송비와 안내 문구를 직접 정하세요 | real JDK (validate_redesigned_lesson) | 9 | 20 | 통과·해시 일치 | `aee958ccef4331fe` |
| java-arrays | java-arrays-9 | `stp_5e8a1d36-92c4-4f7b-a1d0-3c6b8e27f94a` | 2,000원 이상 가격의 합계와 개수를 구하세요 | real JDK (validate_redesigned_lesson) | 9 | 20 | 통과·해시 일치 | `765a118aeb49e93e` |
| java-methods | java-methods-8 | `stp_3a9f6c28-e1d4-4b85-9f72-6d0e8b13a5c9` | 합계와 배송비 메서드를 완성해 결제 금액을 출력하세요 | real JDK (validate_redesigned_lesson) | 7 | 17 | 통과·해시 일치 | `daac8c65196e258e` |
| java-arguments | java-arguments-8 | `stp_86e157bf-bbb1-4709-8ddf-7032baca1f96` | 메모와 주문 코드를 제자리에서 읽게 하세요 | bash+jdk | 3 | 4 | 통과·해시 일치 | `569449cae263ee58` |
| git-first | git-first-9 | `stp_b752762e-e893-4042-9135-c43787c64719` | 빈 폴더에서 할 일 목록을 두 번 기록하세요 | git+bash | 2 | 4 | 통과·해시 일치 | `e4154f342786571b` |
| java-references | java-references-10 | `stp_8b3e5a19-4c72-4d06-a9f1-2e6c7b04d38f` | 별칭으로 바꾸고 복사본은 지키세요 | real JDK (validate_redesigned_lesson) | 8 | 17 | 통과·해시 일치 | `ba8923c570c494ec` |
| java-static | java-static-9 | `stp_6c2f8e15-9a47-4b3d-b8e0-5d1a3f72c94e` | 주문별 금액과 공유 주문 수를 직접 나누세요 | real JDK (validate_redesigned_lesson) | 7 | 16 | 통과·해시 일치 | `a659196eefc38625` |
| java-roles | java-roles-7 | `stp_2d8b4f61-7e39-4a52-9c16-b0e3d5a8f7c2` | 회원 배송비 정책을 끼우고 지갑의 규칙을 지키세요 | real JDK (validate_redesigned_lesson) | 5 | 15 | 통과·해시 일치 | `644a1ece5408eea8` |
| java-collections | java-collections-8 | `stp_9e4c7a83-2b15-4f6d-8a39-c5d0e6b21f74` | 상품 종류 수와 상품별 개수를 함께 구하세요 | real JDK (validate_redesigned_lesson) | 8 | 13 | 통과·해시 일치 | `5d52f898e2c453a1` |
| java-inheritance-composition | java-inheritance-composition-3 | `stp_4f9d2b67-8c31-4e5a-b7d0-1a6e3c94f825` | 새 배송 두 종류의 배송비가 영수증에 반영되게 하세요 | real JDK (validate_redesigned_lesson) | 5 | 10 | 통과·해시 일치 | `f3be84512608d24c` |
| java-streams | java-streams-8 | `stp_1c7e4a92-5b38-4d6f-9e21-8a0d3f6b5c47` | 기준 이상 가격의 개수·할인 합계·최고가를 구하세요 | real JDK (validate_redesigned_lesson) | 10 | 20 | 통과·해시 일치 | `6ffd9e56dbe8abfb` |
| java-files | java-files-8 | `stp_7a5d3e18-6f92-4c4b-a0d7-2b8e1c96f43d` | 방문 기록을 덧붙이고 잘못된 줄을 건너뛰며 합계를 내세요 | real JDK (validate_redesigned_lesson) | 7 | 20 | 통과·해시 일치 | `e310bc4a4f8393b8` |
| java-testing | java-testing-8 | `stp_5b0e8c43-1d76-4a29-b3f8-9c2d6e75a1f0` | 새 적립 규칙의 테스트를 직접 쓰세요 | real JDK (validate_redesigned_lesson) | 7 | 14 | 통과·해시 일치 | `ad22d9f1e1736f1f` |
| git-branch | git-branch-11 | `stp_2083b3dd-20f1-4b1c-9937-d2f70bfb6a1b` | 두 기능을 브랜치로 차례로 개발하세요 | git+bash | 2 | 4 | 통과·해시 일치 | `d0306f1085a09eb0` |
| git-remote | git-remote-12 | `stp_94d0da62-e0db-47a2-aaef-8ad0cf722e8a` | 동료의 변경과 합쳐 내 운영 시간 커밋을 공유하세요 | git+bash | 2 | 4 | 통과·해시 일치 | `193d167c5c931327` |
| git-branch-advanced | git-branch-advanced-10 | `stp_6b96f92f-1312-42a2-8b23-7f4eb545dae5` | 두 의도를 살려 갈라진 안내를 병합하세요 | git+bash | 2 | 5 | 통과·해시 일치 | `15cfe49bb437fcd0` |
| github-pr | github-pr-6 | `stp_2d42bbda-b942-4f8a-ba7a-beeceb7e8086` | 새 저장소에서 GitHub Flow 전체를 혼자 마치세요 |  |  |  | 증거 없음 | `6f7060e086e10801` |
| java-rq | java-rq-7 | `stp_3d6b9f52-8a17-4e4c-b9a5-1c0e7d82f36b` | 빈 Rq를 완성해 목록 요청을 해석하세요 | real JDK (validate_redesigned_lesson) | 8 | 17 | 통과·해시 일치 | `fdcdd9d531866db9` |
| java-calculator | java-calculator-7 | `stp_8f1a6c34-7e29-4d5b-a3c8-0b9d2e64f71a` | 뺄셈을 덧셈과 같은 단계에서 왼쪽부터 계산하세요 | real JDK (validate_redesigned_lesson) | 6 | 14 | 통과·해시 일치 | `33a4a3ec70438b63` |
| java-crud | java-crud-9 | `stp_6a2e8d71-4f39-4b6c-8d05-7c1f3b94e2a8` | 네 동작의 규칙을 지키는 글 서비스를 완성하세요 | real JDK (validate_redesigned_lesson) | 9 | 15 | 통과·해시 일치 | `49e56aa593395649` |
