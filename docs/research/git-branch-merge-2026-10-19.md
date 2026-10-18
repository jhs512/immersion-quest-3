# Git 브랜치·병합 수업 PRD 사실 조사

확인일: 2026-10-19 (한국 시간). git-scm 공식 명령 문서와 용어집을 직접 열었다. 수업 본문·문제·스크립트는 만들지 않았다. 실제 연습 저장소의 생성이나 병합 실행 없이 문서와 로컬 `git --version`만 확인했다. 설치된 Git은 `2.54.0.windows.1`이며 공식 최신 문서의 버전과 일치한다고 가정하지 않는다.

## 원자료와 확인 범위

[원글 14148](https://slog.gg/p/14148)은 이번 웹 도구에서 접근 불가였다. 본문·예제·순서·초보자 전제는 확인하지 못했다. 아래 사실을 원글 내용으로 귀속하면 안 된다.

## 구분해야 하는 상태

- 브랜치는 개발 이력의 흐름이고 브랜치 끝의 커밋을 가리키는 이름 있는 ref가 있다. 일반 로컬 브랜치 `refs/heads/name`은 커밋을 가리킨다. 보통 `HEAD`는 이 브랜치 ref를 가리키는 **symbolic ref**다. 브랜치 이름 자체와 symbolic ref를 동일시하면 안 된다. detached HEAD에서는 HEAD가 커밋을 직접 가리킬 수 있다. [공식 용어집: branch, head, HEAD, symref](https://git-scm.com/docs/gitglossary)
- 커밋은 인덱스 상태로 만든 프로젝트 스냅샷을 이력에 저장한다. 작업 트리는 실제 체크아웃한 파일이며 커밋하지 않은 변경도 포함한다. 브랜치 이름·커밋·작업 중 파일을 각각 별도 상태로 관찰해야 한다. [공식 용어집: commit, working tree](https://git-scm.com/docs/gitglossary)

## 명령과 관찰 가능한 결과

- `git branch name`은 기본적으로 현재 HEAD에서 브랜치를 만들지만 전환하지 않는다. 인자 없는 `git branch`는 목록과 현재 브랜치 표시를 제공한다. [git-branch DESCRIPTION](https://git-scm.com/docs/git-branch#_description)
- `git switch name`은 해당 브랜치로 전환하며 인덱스와 작업 트리를 갱신한다. `git switch -c name`은 생성과 전환을 함께 한다. 전환이 항상 미커밋 변경을 지우거나 항상 거부되는 것은 아니다. 손실을 일으킬 전환은 기본적으로 거부한다. [git-switch DESCRIPTION, OPTIONS](https://git-scm.com/docs/git-switch)
- `git merge other`는 **현재 브랜치**에 다른 쪽 이력을 합친다. fast-forward 가능 시 브랜치 끝을 이동하고 별도 병합 커밋을 만들지 않는다. 일반적인 분기 후 병합은 두 부모를 가진 커밋을 만든다. [git-merge DESCRIPTION, FAST-FORWARD MERGE, TRUE MERGE](https://git-scm.com/docs/git-merge)
- 같은 파일을 양쪽에서 수정했다고 항상 충돌하지 않는다. 겹치지 않은 영역은 자동 결합되고 같은 방식의 변경도 자동 해결될 수 있다. 서로 다른 변경을 자동 조정할 수 없을 때 사람이 결정해야 한다. 수정/삭제·양쪽 추가 같은 다른 충돌도 있다. [git-merge HOW CONFLICTS ARE PRESENTED](https://git-scm.com/docs/git-merge#_how_conflicts_are_presented), [git-status Short Format](https://git-scm.com/docs/git-status#_short_format)
- 충돌 시 인덱스에는 최대 세 버전이 있다. stage 1은 공통 조상, 2는 HEAD, 3은 MERGE_HEAD다. `git ls-files -u`로 확인할 수 있다. 충돌 표시는 작업 트리 파일에 있으며 인덱스 상태와 다르다. [git-merge TRUE MERGE](https://git-scm.com/docs/git-merge#_true_merge)
- 파일을 원하는 결과로 고친 뒤 `git add`로 인덱스에 반영하고 `git commit` 또는 `git merge --continue`로 병합을 마친다. 충돌 표시를 지운 것만으로 병합 완료가 되지 않는다. [git-merge HOW TO RESOLVE CONFLICTS](https://git-scm.com/docs/git-merge#_how_to_resolve_conflicts)
- `git status`는 HEAD↔인덱스, 인덱스↔작업 트리, 추적하지 않는 파일을 구분해 보여 준다. 충돌 상태의 `UU`는 양쪽 수정의 미병합 상태다. 자동 판정에는 출력이 안정적으로 정의된 `--porcelain=v1`이 근거가 된다. [git-status DESCRIPTION, Short Format, Porcelain Format Version 1](https://git-scm.com/docs/git-status)

## 중단과 독립 재시작의 한계

`git merge --abort`는 병합 전 상태 복원을 **시도**한다. 병합 시작 전 미커밋 변경, 특히 병합 시작 후 더 고친 변경은 원상 복구하지 못하는 경우가 있다. 따라서 이를 모든 파일·이력을 초기 연습 상태로 되돌리는 보장으로 쓰면 안 된다. [git-merge DESCRIPTION](https://git-scm.com/docs/git-merge#_description)

실제 Git을 쓰는 독립 연습 요구를 구현할 때 확인할 조건은 다음과 같다. 이는 재현성 검토 항목이며 교육 방법 채택이나 구현 완료를 뜻하지 않는다.

- 사용자가 소유한 전용 임시 디렉터리에 연습별 독립 저장소와 시작 커밋·브랜치 상태가 필요하다. 기존 프로젝트의 현재 브랜치나 개인 작업을 연습의 초기 상태로 쓰지 않는다. 새 저장소 초기화와 초기 브랜치 지정은 `git init -b name directory`로 가능하다. [git-init](https://git-scm.com/docs/git-init)
- 재시작은 알려진 초기 fixture를 다시 제공하는 기능으로 별도 검증해야 한다. 기존 디렉터리에 `git init`만 다시 실행하는 것은 변경·커밋·브랜치를 초기화하지 않는다. [git-init DESCRIPTION](https://git-scm.com/docs/git-init#_description)
- 연습용 이름·이메일 등 설정을 쓴다면 저장소 로컬 설정 범위를 쓸 수 있다. 개인 전역 설정 변경을 전제로 삼지 않는다. [git-config --local](https://git-scm.com/docs/git-config#Documentation/git-config.txt---local)
- 충돌 재현은 공통 시작 커밋에서 분기한 두 쪽이 같은 텍스트 영역을 서로 다르게 수정한 fixture로 검증할 수 있다. 비충돌 결합과 fast-forward는 각각 다른 이력·파일 조건이다. 이 조건들의 실제 재현, 줄바꿈/인코딩, 훅·서명·에디터 설정 영향은 아직 실행 검증하지 않았다.

## 미확정 사항

명령을 직접 실행하는 사용자 요구와 별개로 선수 지식·문제 수·상호작용·채점 방식·플레이어 명령 실행 경계·재시작 구현은 결정하지 않았다. 원격 저장소·인증·push·rebase·복잡한 충돌 전략은 이 조사에서 필수 수업 범위로 채택하지 않았다. 원글 확인과 실제 연습 fixture 실행 검증이 남아 있다.
