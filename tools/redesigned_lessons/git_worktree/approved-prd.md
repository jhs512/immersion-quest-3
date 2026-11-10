# Git · 워크트리: 작업을 둔 채 다른 브랜치를 옆 폴더에서 다뤄요

상태: approved
수업 코드: lsn_411084da-1251-402b-accc-13a1a1c9e208
코스: crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf

이 문서는 제작자용 PRD예요. 학생에게 핵심 흐름이나 정답을 직접 노출하지 않아요.

## 수업 교육 목표

- 커밋하지 않은 작업이 있을 때 브랜치 전환이 막히는 이유를 겪어요.
- git worktree로 다른 브랜치를 옆 폴더에 꺼내 커밋하고, 같은 저장소에 남는 것을 확인해요.
- 한 브랜치는 한 폴더에만 꺼낸다는 규칙을 지키고, 다 쓴 폴더를 remove·prune으로 정리해요.

## 대상과 선수 지식

- 자바 과정에서 Git 첫 기록·브랜치·공유·브랜치 심화를 마친 학습자. GitLab MR 수업 앞의 선택 수업이다.
- git-first
- git-branch
- git-remote
- git-branch-advanced
- bash-basics(cd ../, cat, echo >>, rm -r)

## 제작 범위

- 작업 중인 변경을 둔 채 hotfix의 안내를 읽으세요
- hotfix 브랜치를 옆 폴더에 꺼내세요
- hotfix 폴더에서 커밋하고 work에서 확인하세요
- hotfix를 바탕으로 새 브랜치를 옆 폴더에 꺼내세요
- 다 쓴 hotfix 폴더를 정리하세요
- 손으로 지운 폴더의 남은 기록을 정리하세요
- 쓰던 변경을 지키며 급한 수정을 마치세요

## 제외 범위

- stash·커밋 되돌리기로 쓰던 변경을 치워 두는 방법
- worktree move·lock·unlock·repair, 분리된 HEAD 워크트리(--detach), 원격 브랜치 추적(--track)
- 같은 브랜치를 --force로 두 폴더에 꺼내는 사용(위험을 말로만 짚는다), 서브모듈

## 근거와 확인 한계

- 저장소 하나에 여러 작업 트리를 붙여 한 번에 여러 브랜치를 꺼낼 수 있다. git worktree add <path> <branch>로 기존 브랜치를, -b로 새 브랜치를 꺼낸다. remove는 깨끗한 워크트리만 지우고(--force로 강제), 손으로 지운 워크트리의 관리 파일은 prune으로 정리한다. add는 다른 워크트리에서 이미 쓰는 브랜치와, 지웠지만 등록이 남은 경로를 기본으로 거절한다(--force가 이를 넘는다). — 설치된 Git 2.56.0의 git help worktree(같은 문서) 원문을 열어 확인했다. 웹 페이지는 같은 문서의 공개본이다.; 확인 2026-11-11. [원문](https://git-scm.com/docs/git-worktree)
- switch는 작업 트리와 인덱스를 대상 브랜치에 맞춘다. 커밋하지 않은 변경이 덮일 때는 거절하고, -f(--discard-changes)는 쓰던 변경을 버린다. — Git 문서의 동작 설명이다. 거절 메시지와 종료 코드 1은 Git 2.56.0 임시 저장소에서 실측했다.; 확인 2026-11-11. [원문](https://git-scm.com/docs/git-switch)
- Pro Git의 기본 분기 장은 hotfix 브랜치로 급한 수정을 하는 상황과, 커밋하지 않은 변경이 있으면 전환 전에 작업 상태를 깨끗이 해야 한다는 점을 설명한다. — 상황 설정(hotfix)의 출처다. 이 수업은 stash 대신 워크트리를 다룬다.; 확인 2026-11-11. [원문](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)

## 적용 교육 철학

- 적용 버전: sha256:62245c7bf57115b84825f3c0f6f04c612b4b40dd9b71fb31b515da1984030e1f
- 문제 상황(전환 거절)을 먼저 겪은 뒤 워크트리를 들인다. 한 스텝에 새 개념 하나(추가·공유·한 폴더 규칙·remove·prune).
- 학생 수정은 0~1줄(안내 한 줄). 각 스텝은 정해진 시작 상태로 새로 준비하고 시작 상태를 먼저 알린다.
- 실제 Git 저장소의 폴더 목록(git worktree list)·브랜치 기록·작업 파일로 채점한다. 터미널 출력과 커밋 메시지는 근거가 아니다.
- 실전적인 쉬운 명령(status·switch·show·log --oneline·worktree add/list/remove/prune)만 학생 명령으로 쓰고 내부 검사 옵션은 노출하지 않는다.
- 해설은 명령 하나의 실제 출력을 읽은 뒤 다음 명령으로 넘어가고, 실제로 흔한 실수(switch -f, cd 누락, --force, 폴더만 삭제)에서만 「조심하세요」를 쓴다.
- 해설은 별도 시연 저장소에서 하고 학습자의 실습 폴더를 바꾸지 않는다.

## 선택 교육 전략

- 1번에서 전환 거절을 직접 겪는다(원칙 9). 2·3번은 워크트리 추가와 저장소 공유를 한 개념씩 확인한다. 4번은 실제 거절을 본 뒤 -b로 새 브랜치를 꺼내고, 5·6번은 정리 두 방법을 나눈다. 마지막 수행은 새 개념 없이 조합한다.

## 챕터·단원·스텝과 핵심 흐름

### 작업을 둔 채 다른 브랜치를 꺼내요

교육 목표: 쓰던 변경 때문에 전환이 막히는 문제를 겪고, 워크트리로 다른 브랜치를 옆 폴더에 꺼내요. / 다른 폴더에서 만든 커밋도 같은 저장소에 남는다는 것을 확인해요.

#### 전환 대신 옆 폴더

교육 목표: 브랜치를 바꾸지 않고 다른 브랜치에서 일하고, 그 커밋을 원래 폴더에서 확인해요.

공통 전제: 여러분은 메모 서비스 팀의 안내 담당이에요. main에서 guide.txt에 검색 안내를 쓰는 중이고 아직 커밋하지 않았어요. 동료 지수는 hotfix 브랜치에 긴급 창구 안내를 커밋해 뒀어요. 문제마다 정해진 시작 상태로 새로 준비돼요.

**작업 중인 변경을 둔 채 hotfix의 안내를 읽으세요**

스텝 코드: stp_f1f3e53f-a712-44a5-b215-f6d6555e1dad

교육 목표: 커밋하지 않은 변경이 있으면 다른 브랜치로 바꿔 일하기 어렵다는 것을 확인해요.

수업의 문제 상황을 먼저 겪는다(원칙 9).

시작: main 커밋 1개(기본 안내), guide.txt 끝에 커밋하지 않은 검색 안내. hotfix에는 지수의 긴급 창구 커밋이 있고 같은 파일의 둘째 줄이 다르다.
행동: status → switch hotfix(실제 거절, 종료 코드 1) → show hotfix:guide.txt → cat guide.txt.
관찰 근거: switch의 「Your local changes ... would be overwritten by checkout」 거절, show가 보여 준 문의: 긴급 창구, 그대로인 검색 안내.
판정: show hotfix:guide.txt가 성공적으로 실행됐고, work의 브랜치·커밋·작업 파일·작업 폴더 목록이 시작 그대로다. 시작 상태는 명령이 없어 실패한다. switch -f(쓰던 변경 삭제), 쓰던 변경 커밋, restore 뒤 전환은 실패한다.
주의: 실패한 switch는 채점 근거가 아니다(실패한 명령은 기록하지 않는다). 거절은 할 일과 해설에서 직접 보인다.

**hotfix 브랜치를 옆 폴더에 꺼내세요**

스텝 코드: stp_c5aa27de-f47d-41b0-bd57-cfc98b864ec4

교육 목표: git worktree add는 같은 저장소의 다른 브랜치를 새 폴더에 꺼내요. 지금 폴더의 변경은 그대로예요.

새 개념 하나: 워크트리 = 같은 저장소의 다른 브랜치를 꺼낸 또 하나의 폴더.

시작: 1번과 같은 상태(새로 준비).
행동: worktree add ../hotfix hotfix → worktree list → cat ../hotfix/guide.txt → status.
관찰 근거: worktree list의 두 줄([main]·[hotfix]), 새 폴더의 긴급 창구 안내, work의 수정된 guide.txt.
판정: git worktree list의 폴더 집합이 정확히 {work=main, ../hotfix=hotfix}이고 work의 브랜치·커밋·작업 파일이 시작 그대로다. git worktree add ../hotfix(브랜치 생략, 같은 이름의 기존 브랜치)도 같은 상태라 통과한다. work 안의 hotfix 폴더, 분리된 HEAD(--detach), switch -f, 쓰던 변경 커밋은 실패한다.

**hotfix 폴더에서 커밋하고 work에서 확인하세요**

스텝 코드: stp_d953667b-0e93-46e8-a366-7b3dd04f7450

교육 목표: 다른 폴더에서 만든 커밋도 같은 저장소의 브랜치에 바로 남아요.

새 개념 하나: 워크트리들은 저장소(커밋·브랜치) 하나를 함께 쓴다.

시작: ../hotfix에 hotfix 워크트리가 이미 있다(준비 명령 git worktree add ../hotfix hotfix). work의 main에는 쓰던 검색 안내.
행동: cd ../hotfix → branch(* hotfix, + main) → echo >> → add → commit → cd ../work → log --oneline hotfix → status.
관찰 근거: 다른 폴더에서 만든 커밋이 push·fetch 없이 work의 log에 보인다. git-remote의 peer 복제본과 대조한다.
판정: work 저장소에서 읽은 refs/heads/hotfix의 guide.txt가 운영 시간 줄까지 정확히 같고, 폴더 집합이 {work=main, ../hotfix=hotfix}이며 work의 브랜치·커밋·작업 파일이 그대로다. cd 없이 work에서 커밋하면 main 기록이 바뀌어 실패한다. 커밋하지 않고 파일만 고치면 실패한다.

### 워크트리의 규칙을 지키고 정리해요

교육 목표: 한 브랜치는 한 폴더에만 꺼낸다는 규칙을 확인해요. / 다 쓴 폴더를 remove로, 손으로 지운 폴더의 기록을 prune으로 정리해요.

#### 한 브랜치는 한 폴더에

교육 목표: 이미 꺼낸 브랜치를 또 꺼내면 거절되는 것을 보고, 새 브랜치로 꺼내요.

공통 전제: hotfix 폴더가 이미 꺼내져 있어요. work의 main에는 쓰던 검색 안내가 있어요. 문제마다 이 상태로 새로 준비돼요.

**hotfix를 바탕으로 새 브랜치를 옆 폴더에 꺼내세요**

스텝 코드: stp_8049e77f-598c-4a1b-95c9-acb14d26ea2d

교육 목표: 한 브랜치는 한 폴더에만 꺼낼 수 있어요. 같은 커밋이 하나 더 필요하면 새 브랜치로 꺼내요.

새 개념 하나: 한 브랜치는 한 워크트리에만 꺼낸다. 같은 커밋이 더 필요하면 새 브랜치(-b)로 꺼낸다.

시작: ../hotfix에 hotfix 워크트리, work의 main에는 쓰던 검색 안내.
행동: worktree add ../hotfix-try hotfix(실제 거절, 종료 코드 128) → worktree add -b hotfix-try ../hotfix-try hotfix → worktree list.
관찰 근거: 「hotfix is already used by worktree at …/hotfix」 거절과 세 줄의 worktree list.
판정: 폴더 집합이 정확히 {work=main, ../hotfix=hotfix, ../hotfix-try=hotfix-try}이고 hotfix-try와 hotfix의 guide.txt가 긴급 창구 안내다. --force로 hotfix를 두 번 꺼내면(같은 브랜치 두 폴더) 실패한다. work 안의 폴더·다른 출발점은 실패한다.
주의: --force로 같은 브랜치를 두 폴더에 꺼내면 한쪽 커밋 뒤 다른 폴더의 인덱스가 거꾸로 바뀐 상태로 보인다(실측).

#### 다 쓴 폴더 정리

교육 목표: 폴더를 정리해도 브랜치와 커밋이 남는 것을 확인하고, 남은 폴더 기록을 정리해요.

공통 전제: hotfix 작업을 커밋까지 마쳤고 hotfix 폴더는 깨끗해요. work의 main에는 쓰던 검색 안내가 있어요. 문제마다 이 상태로 새로 준비돼요.

**다 쓴 hotfix 폴더를 정리하세요**

스텝 코드: stp_320a39b7-bb3a-4cd1-b79c-6f0399749773

교육 목표: git worktree remove는 꺼낸 폴더만 정리하고 브랜치와 커밋은 남겨요.

새 개념 하나: worktree remove는 워크트리(폴더와 그 기록)만 지우고 브랜치·커밋은 남긴다.

시작: hotfix에 운영 시간 안내까지 커밋돼 있고 ../hotfix 워크트리는 깨끗하다. work의 main에는 쓰던 검색 안내.
행동: worktree list → worktree remove ../hotfix → worktree list → log --oneline hotfix.
관찰 근거: 목록이 두 줄에서 한 줄로, hotfix의 커밋은 그대로.
판정: 폴더 집합이 정확히 {work=main}이고 hotfix 브랜치의 guide.txt가 운영 시간 줄까지 같으며 work가 그대로다. rm -r ../hotfix만 하면 지운 폴더의 기록이 남아 실패한다. 브랜치를 지우면 실패한다.
주의: 커밋하지 않은 변경이 있으면 remove가 거절하고(실측) --force는 그 변경을 지운다.

**손으로 지운 폴더의 남은 기록을 정리하세요**

스텝 코드: stp_25b9d9df-958d-487e-bfd2-93e2e897fb30

교육 목표: 폴더를 rm으로만 지우면 저장소에 그 폴더의 기록이 남아요. git worktree prune이 남은 기록을 지워요.

새 개념 하나: 폴더만 지우면 남는 워크트리 기록과 이를 지우는 worktree prune.

시작: 5번과 같은 상태(새로 준비).
행동: rm -r ../hotfix(bash-basics에서 배운 명령으로 손으로 지운 상황을 만든다) → worktree list(prunable) → worktree add ../hotfix hotfix(실제 거절, 종료 코드 128) → worktree prune → worktree list.
관찰 근거: prunable 표시, 「missing but already registered worktree」 거절, 한 줄로 줄어든 목록.
판정: 폴더 집합이 정확히 {work=main}이고(지운 폴더의 남은 기록은 다른 항목으로 보여 실패) hotfix 브랜치의 기록과 work가 그대로다. 지운 뒤 worktree remove ../hotfix도 같은 기록을 지워 통과한다(실측). rm만 하거나 add -f로 다시 꺼내면 실패한다.

### 쓰던 변경을 지키며 급한 수정을 마쳐요

교육 목표: 앞에서 쓴 명령을 골라 꺼내기·커밋·정리를 한 번에 해요.

#### 마지막 수행

교육 목표: 새 개념 없이 1·2장의 판단을 조합해요.

공통 전제: 처음과 같은 상태예요. 워크트리는 없고, hotfix에는 지수의 커밋, work의 main에는 쓰던 검색 안내가 있어요.

**쓰던 변경을 지키며 급한 수정을 마치세요**

스텝 코드: stp_766d9f5c-ed41-48c5-bd20-7cf8246b240d

교육 목표: 쓰던 변경을 그대로 두고, 다른 폴더에서 hotfix를 커밋한 뒤 그 폴더를 정리해요.

새 개념 없이 1~6번의 판단을 조합하는 마지막 수행이다.

시작: 1번과 같은 상태(워크트리 없음, hotfix에는 긴급 창구 커밋, work의 main에는 쓰던 검색 안내).
행동: worktree add → cd → echo >> → add → commit → cd ../work → log → worktree remove → list → status. 할 일은 목표 상태만 주고 명령은 학습자가 고른다(확인 명령만 명시).
관찰 근거: log의 새 커밋, 한 줄 목록, 그대로인 status.
판정: 폴더 집합이 정확히 {work=main}, hotfix 브랜치의 guide.txt가 운영 시간 줄까지 같고, work의 브랜치·커밋·작업 파일이 그대로다. main에 커밋, 폴더 정리 누락, rm만 하고 기록을 남김, switch -f로 쓰던 변경을 지움은 실패한다.

## 채점

- 채점기는 실습 저장소 work에서 git worktree list --porcelain을 읽어 폴더 집합을 「. 또는 ../이름 → 브랜치」로 비교한다. 지운 폴더의 남은 기록(prunable)과 다른 위치의 폴더는 다른 항목으로 보여 실패한다.
- 브랜치 기록은 work 저장소의 refs/heads/<브랜치> 트리의 파일 목록과 바이트로 비교한다. 다른 폴더에서 만든 커밋도 같은 저장소에서 읽는다.
- 모든 스텝은 work의 현재 브랜치 main·커밋 수 1·HEAD 파일·작업 파일(쓰던 검색 안내)을 함께 확인한다.
- 1번만 show hotfix:guide.txt의 성공 실행 기록을 함께 요구한다. 커밋 메시지·터미널 출력은 근거가 아니다.
- 이 채점 항목(worktrees, branch_files)과 준비 명령 git worktree add ../이름 브랜치는 이 수업과 함께 플레이어에 추가했다. 이 기능이 있는 플레이어 릴리스가 먼저 필요하다.

## 초기화

- 스텝마다 빈 저장소에서 같은 준비 명령(기본 안내 커밋, hotfix의 긴급 창구 커밋, 필요하면 운영 시간 커밋과 git worktree add ../hotfix hotfix, 마지막에 쓰던 검색 안내 파일)을 실행해 새로 만든다. 「초기화」는 새 실습 폴더에서 같은 준비를 다시 한다. 해설은 별도 시연 저장소에서 같은 준비로 시작한다.

## 해설

- 문제의 시작 상태와 제약 문장을 정확히 강조하고, 명령 하나의 실제 출력을 읽은 뒤 다음 명령으로 넘어간다. 거절되는 명령은 실제 종료 코드(switch 1, worktree add 128)로 시연하고 메시지를 읽는다. 실제 음성 동기화는 앱 확인이 필요하다.

## 검증과 완료

- 단위·수업 데이터: tests/git_worktree.rs가 공개 수업 JSON의 7개 스텝을 플레이어의 채점 경로(check_exercise)로 실행한다. 시작 상태 실패, 해설 재생 통과, 동등 풀이 통과, 흔한 오답 거절, 채점 항목 검증을 확인한다.
- examples/validate_redesigned_git.rs git-worktree: 학생 저장소 시작 실패·해설 분리·연속 풀이·초기화 재생.
- tests/final_terminal_challenges.rs: 마지막 수행의 정답·동등 풀이·오답.
- 빌드: build-redesigned-git --lesson, narration_review, build-redesigned-course-bundle --check, lesson_registry. 화면·실제 음성·Windows Git Bash는 별도 검증 범위로 남긴다.

## 대표 문제 초안

- step_id: stp_c5aa27de-f47d-41b0-bd57-cfc98b864ec4
- prompt: 앞 문제와 같은 상태에서 다시 시작해요. `main`의 `guide.txt`에는 커밋하지 않은 검색 안내가 있어요. `hotfix`에는 지수의 커밋이 있어요.

워크트리(worktree)는 같은 저장소에 붙은 또 하나의 작업 폴더예요. `git worktree add ../hotfix hotfix`는 `work` 옆에 `hotfix` 폴더를 만들어요. 그리고 그 폴더에 `hotfix` 브랜치를 꺼내요. 지금 있는 `work`는 그대로 `main`이에요.

**할 일**

1. `git worktree add ../hotfix hotfix`를 실행해 hotfix를 옆 폴더에 꺼내세요.
2. `git worktree list`를 실행해 두 폴더와 각 폴더의 브랜치를 확인하세요.
3. `cat ../hotfix/guide.txt`를 실행해 새 폴더의 안내를 읽으세요.
4. `git status`를 실행해 `work`가 여전히 `main`이고 `guide.txt`가 수정된 상태인지 확인하세요.
5. 확인한 뒤 제출 버튼을 누르세요.
- starter_state: main 커밋 1개, guide.txt에 커밋하지 않은 검색 안내. hotfix에는 지수의 긴급 창구 커밋. 워크트리는 work 하나.
- expected_action: git worktree add ../hotfix hotfix로 hotfix를 옆 폴더에 꺼낸 뒤 list·cat·status로 확인한다.
- acceptance: 폴더 집합이 정확히 {work=main, ../hotfix=hotfix}이고 work의 브랜치·커밋·작업 파일이 그대로다. work 안의 폴더·분리된 HEAD·switch -f·쓰던 변경 커밋은 실패한다.
- reset: 「초기화」는 새 실습 폴더에서 같은 시작 상태를 다시 만든다.
- narration: worktree add의 실제 출력과 두 줄 목록, 두 폴더의 서로 다른 안내를 차례로 읽는다. 경로를 hotfix로 줄여 쓰는 실수를 짚는다.

## 제작 승인

- PRD와 대표 문제의 승인을 함께 확인해요.
- 승인된 범위 안의 수정은 가능해요. 목표나 교육 기법 변경은 다시 승인받아요.
- 내용 식별 해시: 5e7340adbbf1c88897fca8e5a0c6808dec9f27bc9c3eaef864326c4e8fff04bc

