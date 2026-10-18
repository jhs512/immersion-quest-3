# 저장소 기반 코스

플레이어는 `gh api`로 github.com의 현재 로그인 계정을 사용한다. 접근 토큰을 읽거나 별도 저장하지 않는다. 설치된 Git은 Git 실습에서 사용하고, 코스/수업 읽기와 이슈 기록에는 Git CLI가 필요하지 않다. 모든 학습 동작은 온라인 인증을 확인한다. 기존 KPC/자바 로컬 진도는 그대로 보존하며 개발 빌드의 `MOLIP_LEGACY=1`로 기존 화면을 열 수 있다.

## 코스와 수업

`src/repository_course.rs`가 JSON 계약을 정의한다. 코스의 `main/course.json`은 수업 참조, 순서, 선수 지식, 필수 여부만 가진다. 수업은 별도 리포의 `lesson.json`이며 버전 태그와 원문 바이트의 SHA-256으로 고정한다. 해시가 다르면 실행하지 않는다. 같은 수업을 여러 코스가 참조할 수 있다. 태그를 바꿔 기존 버전의 내용을 갱신하지 않는다.

풀모드는 본문과 문제를, 복습모드는 같은 ID의 문제를 바로 보여준다. 완료는 필수 문제의 실제 채점 통과로만 결정한다. `java`, `java_project`, `junit`, `git`, `javascript`, `web` 실행을 지원한다. 프로젝트의 지원 파일은 새 임시 폴더에 준비하고 학생의 편집 파일을 덮어쓴다. JUnit 테스트 작성 문제는 정상 구현 통과와 결함 구현 탐지를 함께 확인한다. 웹은 실제 Edge와 React/Tailwind를 사용한다. 격리된 앱 미리보기의 저장은 미리보기 안에서만 유지된다. 저장 후 새로고침 검사는 별도 브라우저의 실제 localStorage로 한다.

## 진도

숫자 GitHub 사용자 ID × 코스 ID × 수업 ID가 진도 이슈의 식별자다. 이슈는 코스 리포에 있고, 이벤트 댓글이 원본이며 본문은 요약이다. 이벤트는 학습 모드, 버전, 회차, 고유 ID를 포함한다. 다른 작성자의 댓글이나 다른 계정의 키는 반영하지 않는다. 같은 이벤트는 중복 집계하지 않는다. 동시 첫 시작으로 이슈가 두 개 만들어지면 가장 작은 번호를 대표 이슈로 선택하고 나머지는 닫는다. 닫힌 이슈의 이벤트도 합쳐 손실을 막는다.

필수 문제를 통과한 회차의 완료만 인정한다. 이전 버전 완료는 유지하고 새 버전 완료가 없으면 추가 학습을 표시한다. 계정이 바뀌면 기존 화면의 실행·기록을 거부하고 계정 재확인을 안내한다. 네트워크 실패는 완료로 표시하지 않는다. 편집 초안은 계정·코스·수업·회차·문제별로 로컬에 보존한다. 동기화 대기열은 없다.

## 코스 만들기

플레이어에서 공개 코스 리포를 추가하거나 새 코스를 구성할 수 있다. `owner/repo@version` 수업을 읽어 ID와 해시를 검증하고 순서를 정한다. 게시 전 현재 gh 계정, 새 공개 리포 이름, 수업 순서, 실제 JSON을 보여준다. 게시 버튼을 눌러야 리포를 만든다. 플레이어 계정과 gh 계정이 같아야 하며 기존 코스는 덮어쓰지 않는다. 사용자 계정의 기본 브랜치가 main이 아니면 기존 브랜치를 남기고 main을 추가한다.

## 콘텐츠 작성과 검증

학생 문장과 해설은 `docs/voice.md`, `docs/content-rules.md`, `docs/agents/narration.md`를 따른다. 원문 7개와 외부 자료 출처는 `.scratch/repo-curriculum/source-audit.md`에 기록했다. CodePen 전체 소스를 확보한 것으로 주장하지 않는다.

```powershell
python tools/narrate.py --backend
python tools/build-kpc-course.py
cargo test --locked --all-targets
cargo test --locked --test repository_lessons -- --ignored --nocapture --test-threads=1
```

`tools/backend_course/`가 자바 백엔드 24개 수업의 원본이다. 기존 자바 기초 콘텐츠는 재사용한다. 해설 캐시는 문제·정답·지원 파일·검사 전체 해시에 묶인다. 바뀐 문제만 다시 생성한다. 자바 프로젝트의 해설은 컴파일러 구문 트리로 메서드를 찾아 세 줄 이하의 편집 조각으로 채운다. 처음의 미구현 예외와 중간 테스트 실패는 의도한 단계로 명시한다. 실행 검사가 각 단계와 최종 코드 일치를 확인한다. KPC 자료와 그 캐시는 별도로 보존한다.

생성 결과는 `target/backend-course/`에 있고, 승인된 최초 게시에는 `python tools/publish-backend-course.py --publish`를 사용한다. 이 도구는 기존 태그를 이동하지 않으며 모든 수업의 게시된 해시를 확인한 뒤 코스 구성을 게시한다.

## 첫 기록 수업의 실제 Git 목표

`git_terminal.initial_history`는 생략하면 기존의 `recorded` 시작 상태를 유지한다. `empty`는 main 저장소와 전용 로컬 원격만 초기화하고 기본 파일·커밋·push를 만들지 않는다. `files`는 작업 파일로 남고 `setup`은 그 뒤에 적용한다. 초기화·저장소 재개는 동일한 규칙을 사용한다.

`git_terminal.state_goal`은 실제 상태 판정이다. `head_exists`, 정확한 `commit_count`, `clean`, 그리고 전체 경로·내용을 지정하는 `index`, `working_files`, `head_files`, `parent_files`를 선택한다. 파일 맵은 전체 경로 집합과 UTF-8 바이트를 비교하며 끝의 공백·개행도 의미가 있다. 부모 파일은 `HEAD^`의 트리다. 입력한 커밋 메시지나 add 명령 표기를 정답으로 고정하지 않는다. 명령 수행 자체가 목표이면 기존 `commands`와 함께 요구할 수 있다.

빈 목표·알 수 없는 목표 필드·준비 파일의 잘못된 경로를 거절한다. 작업 파일은 심볼릭 링크나 특수 파일을 읽지 않고, 예상 길이보다 큰 읽기를 제한한다. Git 명령을 사용자가 직접 실행하는 로컬 실습이며 OS 샌드박스라고 주장하지 않는다.


`git_terminal`과 `interaction.kind=choice`를 함께 쓰면 실제 저장소를 관찰한 뒤 설명을 고르는 문제다. 이때 `git_checks`, `state_goal`, 필수 `commands`를 함께 넣지 않는다. 선택 답안과 Git 완료 조건 중 하나가 조용히 무시되는 구성을 검증에서 거절한다. 초기화는 저장소와 선택 초안을 함께 되돌린다.

승인된 첫 Git 수업의 제작 원본은 `tools/redesigned_lessons/git_first/`다. 승인 PRD, 학습 콘텐츠, 스텝별 해설 캐시는 분리한다. `python tools/narrate.py --redesigned-git-first`로 변경된 캐시만 갱신하고 `--check`로 파생물 신선도를 확인한다. `courses/redesigned/git-first.json`에는 학습자용 자료만 들어가며 핵심 흐름·승인 근거는 배포하지 않는다. 이 로컬 제작물만으로 공개 코스 게시나 릴리스가 완료된 것은 아니다.


분기 수업의 `state_goal.current_branch`는 실제 HEAD가 연결된 브랜치 이름이다. `references`는 `refs/heads/feature` 같은 브랜치가 현재 HEAD 커밋을 가리키는 조건이며 현재 지원 값은 `HEAD`, `HEAD^`(첫 부모), `HEAD^1`, `HEAD^2`다. 이름을 만드는 것과 그 브랜치로 전환하는 것을 별도로 판정한다. 빈 참조 맵·지원하지 않는 대상·잘못된 이름은 제작 검증에서 거절한다. 생략한 새 필드는 직렬화하지 않아 기존 저장소 준비 상태의 식별값을 바꾸지 않는다.


`setup.kind=merge_conflict`는 지정한 브랜치를 실제로 병합해 충돌을 준비한다. 종료 코드1과 유효한 MERGE_HEAD, 실제 미병합 인덱스를 모두 확인한다. 단순 명령 오류나 충돌 없는 성공을 준비된 충돌로 취급하지 않는다. 초기화도 같은 과정을 다시 실행한다.

`state_goal.merge_in_progress`는 MERGE_HEAD의 존재를, `unmerged_paths`는 실제 미병합 경로 집합을 검사한다. 충돌 표시를 지우는 것과 add로 인덱스를 해결하는 것을 구분한다. `parent_count`는 현재 커밋의 정확한 부모 수이며, 두 부모 병합을 요구할 때 불필요한 추가 부모도 거절한다.


상호작용 문제는 선택 답안과 실행할 예제를 분리할 수 있다. 선택 문제에 `example_code`를 명시하면 `lesson_runner::run_example`으로 준비된 프로그램을 실행하고, 선택 답안은 기존 `check`로 따로 판정한다. 일반 `run`은 여전히 선택 답안을 실행하지 않는다. 빈 코드·64KB 초과·상호작용 없는 예제·Git 터미널과 중복된 예제를 거절한다. 현재 Java·Python·C·JavaScript 예제를 지원하는 런타임 경로이며, 새 화면 연결은 별도로 검증한다.
