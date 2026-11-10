"""Write the Git worktree lesson's authored sources from one reviewed definition.

The written files (tools/redesigned_lessons/git_worktree/*) are the canonical sources; this script only
keeps the repeated start states and the PRD/preview/content layers consistent.
Run from the repository root after register_lesson.py:
    python .scratch/git-worktree-lesson/author_lesson.py
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from lesson_prd import approve, policy_revision, render  # noqa: E402

KEY = 'git-worktree'
FOLDER = ROOT / 'tools/redesigned_lessons/git_worktree'
LESSON_ID = 'lsn_411084da-1251-402b-accc-13a1a1c9e208'
COURSE_ID = 'crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf'
TITLE = 'Git · 워크트리: 작업을 둔 채 다른 브랜치를 옆 폴더에서 다뤄요'
CH = ['chp_d0d36c0c-d0cc-449c-81b3-59a957063532', 'chp_cddc34c5-fc4f-43e4-ac1b-6723e1698a9d',
      'chp_8d379c05-7781-45d3-9498-ecea30c9720a']
UN = ['unt_0e564959-4093-427e-81f1-83e5282285fc', 'unt_d0a578b6-fd5c-4b7b-af6f-fe818a53fbab',
      'unt_7fd44b94-67c9-443a-9259-a5a381e2c817', 'unt_d5533d84-79b4-49ab-9098-2d476a0320f0']
ST = ['stp_f1f3e53f-a712-44a5-b215-f6d6555e1dad', 'stp_c5aa27de-f47d-41b0-bd57-cfc98b864ec4',
      'stp_d953667b-0e93-46e8-a366-7b3dd04f7450', 'stp_8049e77f-598c-4a1b-95c9-acb14d26ea2d',
      'stp_320a39b7-bb3a-4cd1-b79c-6f0399749773', 'stp_25b9d9df-958d-487e-bfd2-93e2e897fb30',
      'stp_766d9f5c-ed41-48c5-bd20-7cf8246b240d']
TERM = '#git-demo-terminal'

# -- prepared repository -------------------------------------------------------------------
BASE = '안내: 메모를 남겨요\n문의: 기본 창구\n'
HOT = '안내: 메모를 남겨요\n문의: 긴급 창구\n'
WIP = BASE + '검색: 메모를 찾아요\n'
HOURS = '운영: 평일 9시부터'
HOT2 = HOT + HOURS + '\n'


def git(*args):
    return {'kind': 'git', 'args': list(args)}


def file(content):
    return {'kind': 'file', 'path': 'guide.txt', 'content': content}


def setup(hours_committed=False, worktree=False):
    """main: one commit + an uncommitted search line. hotfix: 지수's urgent contact commit."""
    steps = [git('add', 'guide.txt'), git('commit', '-m', '기본 안내'), git('branch', 'hotfix'), git('switch', 'hotfix'),
             file(HOT), git('add', 'guide.txt'), git('commit', '-m', '긴급 창구 안내')]
    if hours_committed:
        steps += [file(HOT2), git('add', 'guide.txt'), git('commit', '-m', '운영 시간 안내')]
    steps += [git('switch', 'main'), file(WIP)]
    if worktree:
        steps.append(git('worktree', 'add', '../hotfix', 'hotfix'))
    return steps


def terminal(goal, hours_committed=False, worktree=False):
    # The learner's half-written search line stays untouched in the practice folder in every step.
    protected = dict(current_branch='main', commit_count=1, head_files={'guide.txt': BASE}, working_files={'guide.txt': WIP})
    return {'initial_history': 'empty', 'files': {'guide.txt': BASE},
            'setup': setup(hours_committed, worktree), 'state_goal': dict(protected, **goal)}


def say(text, target):
    return {'action': 'say', 'text': text, 'target': target}


def run(args, line, exit_code=None):
    action = {'action': 'git_command', 'args': list(args), 'say': line, 'target': TERM}
    if exit_code is not None:
        action['expected_exit'] = exit_code
    return action


def bash(command, line):
    return {'action': 'bash_command', 'command': command, 'say': line, 'target': TERM}


START_FIRST = ('여러분은 메모 서비스 팀의 안내 담당이에요. 지금 `main`에서 `guide.txt`에 검색 안내 한 줄을 쓰는 중이에요. '
               '아직 커밋하지 않았어요.')
HOURS_ECHO = f'echo "{HOURS}" >> guide.txt'
HOURS_COMMIT = 'git commit -m "운영 시간 안내"'

STEPS = []

# 1 -----------------------------------------------------------------------------------------
STEPS.append(dict(
    id=ST[0], title='작업 중인 변경을 둔 채 hotfix의 안내를 읽으세요',
    objectives=['커밋하지 않은 변경이 있으면 다른 브랜치로 바꿔 일하기 어렵다는 것을 확인해요.'],
    goal=START_FIRST + '\n\n'
         '그때 동료 지수가 급한 수정을 부탁했어요. 지수는 `hotfix` 브랜치에 긴급 창구 안내를 커밋해 뒀어요.\n\n'
         '이번 문제는 이 상태로 준비돼 있어요. 터미널은 실습 저장소 폴더 `work`에서 열려요. '
         '쓰던 검색 안내는 지우거나 커밋하지 말고 그대로 두세요.\n\n'
         '**할 일**\n\n'
         '1. `git status`를 실행해 `guide.txt`가 수정된 상태인지 확인하세요.\n'
         '2. `git switch hotfix`를 실행해 브랜치를 바꿔 보세요. 거절 메시지를 읽으세요.\n'
         '3. `git show hotfix:guide.txt`를 실행해 브랜치를 바꾸지 않고 hotfix의 안내를 읽으세요.\n'
         '4. `cat guide.txt`를 실행해 쓰던 검색 안내가 그대로인지 확인하세요.\n'
         '5. 확인한 뒤 제출 버튼을 누르세요.',
    solution='# 쓰던 변경이 있어서 브랜치를 바꾸려 하면 거절돼요.\n'
             'git switch hotfix\n'
             '# 브랜치를 바꾸지 않고 hotfix에 기록된 안내만 읽어요.\n'
             'git show hotfix:guide.txt\n'
             '# 쓰던 검색 안내는 work 폴더에 그대로 있어요.\n'
             'cat guide.txt',
    terminal=dict(terminal({'worktrees': {'.': 'main'}}), commands=[['show', 'hotfix:guide.txt']]),
    narration=[
        say('main에는 아직 커밋하지 않은 검색 안내가 있어요. 이 상태로 hotfix를 보러 가 볼게요.', 'text:아직 커밋하지 않았어요.'),
        run(['status'], '먼저 지금 상태를 봐요.'),
        say('guide.txt가 modified예요. 커밋하지 않은 변경이 이 폴더에 있어요.', TERM),
        run(['switch', 'hotfix'], 'hotfix로 바꿔 볼게요.', exit_code=1),
        say('거절됐어요. 바꾸면 쓰던 guide.txt가 hotfix의 내용으로 덮인다고 알려 줘요.', TERM),
        say('조심하세요. switch -f로 밀어붙이면 쓰던 검색 안내가 지워져요. 거절됐다고 강제 옵션을 붙이지 마세요.',
            'text:쓰던 검색 안내는 지우거나 커밋하지 말고 그대로 두세요.'),
        run(['show', 'hotfix:guide.txt'], '읽기만 할 거면 show로 hotfix의 파일을 볼 수 있어요.'),
        say('문의: 긴급 창구가 보여요. 지수가 hotfix에 커밋한 안내예요.', TERM),
        bash('cat guide.txt', '이 폴더의 파일도 확인해요.'),
        say('검색: 메모를 찾아요가 그대로 있어요. 읽기는 됐지만 hotfix에서 고치고 커밋하지는 못했어요.', TERM),
        say('브랜치를 바꾸지 않고 hotfix에서 일하는 방법을 다음 문제에서 써 봐요.', 'text:그때 동료 지수가 급한 수정을 부탁했어요.'),
    ],
    core='수업의 문제 상황을 먼저 겪는다(원칙 9).\n\n'
         '시작: main 커밋 1개(기본 안내), guide.txt 끝에 커밋하지 않은 검색 안내. hotfix에는 지수의 긴급 창구 커밋이 있고 같은 파일의 둘째 줄이 다르다.\n'
         '행동: status → switch hotfix(실제 거절, 종료 코드 1) → show hotfix:guide.txt → cat guide.txt.\n'
         '관찰 근거: switch의 「Your local changes ... would be overwritten by checkout」 거절, show가 보여 준 문의: 긴급 창구, 그대로인 검색 안내.\n'
         '판정: show hotfix:guide.txt가 성공적으로 실행됐고, work의 브랜치·커밋·작업 파일·작업 폴더 목록이 시작 그대로다. '
         '시작 상태는 명령이 없어 실패한다. switch -f(쓰던 변경 삭제), 쓰던 변경 커밋, restore 뒤 전환은 실패한다.\n'
         '주의: 실패한 switch는 채점 근거가 아니다(실패한 명령은 기록하지 않는다). 거절은 할 일과 해설에서 직접 보인다.',
    complexity=dict(new_concepts=[], prerequisite_experience='git-branch의 switch·status, git-branch-advanced·git-remote의 git show <커밋>:<파일>.',
                    changed_condition='커밋하지 않은 변경이 있는 채로 내용이 다른 브랜치로 바꾸려 한다.',
                    observable_evidence='switch 거절 메시지, show 출력의 문의: 긴급 창구, cat 출력의 검색 안내.',
                    learner_edited_lines=0, new_external_services=0),
))

# 2 -----------------------------------------------------------------------------------------
STEPS.append(dict(
    id=ST[1], title='hotfix 브랜치를 옆 폴더에 꺼내세요',
    objectives=['git worktree add는 같은 저장소의 다른 브랜치를 새 폴더에 꺼내요. 지금 폴더의 변경은 그대로예요.'],
    goal='앞 문제와 같은 상태에서 다시 시작해요. `main`의 `guide.txt`에는 커밋하지 않은 검색 안내가 있어요. '
         '`hotfix`에는 지수의 커밋이 있어요.\n\n'
         '워크트리(worktree)는 같은 저장소에 붙은 또 하나의 작업 폴더예요. '
         '`git worktree add ../hotfix hotfix`는 `work` 옆에 `hotfix` 폴더를 만들어요. 그리고 그 폴더에 `hotfix` 브랜치를 꺼내요. '
         '지금 있는 `work`는 그대로 `main`이에요.\n\n'
         '**할 일**\n\n'
         '1. `git worktree add ../hotfix hotfix`를 실행해 hotfix를 옆 폴더에 꺼내세요.\n'
         '2. `git worktree list`를 실행해 두 폴더와 각 폴더의 브랜치를 확인하세요.\n'
         '3. `cat ../hotfix/guide.txt`를 실행해 새 폴더의 안내를 읽으세요.\n'
         '4. `git status`를 실행해 `work`가 여전히 `main`이고 `guide.txt`가 수정된 상태인지 확인하세요.\n'
         '5. 확인한 뒤 제출 버튼을 누르세요.',
    solution='# work 옆에 hotfix 폴더를 만들고 hotfix 브랜치를 꺼내요.\n'
             'git worktree add ../hotfix hotfix\n'
             '# 저장소 하나에 붙은 폴더 둘과 각 폴더의 브랜치를 봐요.\n'
             'git worktree list\n'
             '# 새 폴더에는 hotfix의 안내가 있어요.\n'
             'cat ../hotfix/guide.txt\n'
             '# work는 그대로 main이고 쓰던 변경도 남아 있어요.\n'
             'git status',
    terminal=terminal({'worktrees': {'.': 'main', '../hotfix': 'hotfix'}}),
    narration=[
        say('이번엔 브랜치를 바꾸지 않고, hotfix를 옆 폴더에 꺼내요.', 'text:그 폴더에 hotfix 브랜치를 꺼내요.'),
        run(['worktree', 'add', '../hotfix', 'hotfix'], 'worktree add에 폴더 자리와 브랜치를 차례로 줘요.'),
        say('Preparing worktree가 나왔어요. HEAD는 지수의 긴급 창구 안내 커밋이에요. work 옆에 hotfix 폴더가 생겼어요.', TERM),
        say('조심하세요. ../hotfix를 hotfix로 줄여 쓰면 work 안에 폴더가 생겨요. 그러면 main의 status에 낯선 hotfix/가 섞여요.',
            'text:work 옆에 hotfix 폴더를 만들어요.'),
        run(['worktree', 'list'], '이 저장소에 붙은 폴더를 봐요.'),
        say('줄이 둘이에요. work 끝에는 [main], hotfix 끝에는 [hotfix]가 붙어 있어요.', TERM),
        bash('cat ../hotfix/guide.txt', '새 폴더의 안내를 읽어요.'),
        say('문의: 긴급 창구예요. 새 폴더에는 hotfix에 기록된 파일이 꺼내져 있어요.', TERM),
        run(['status'], 'work의 상태를 다시 봐요.'),
        say('여기는 여전히 main이고, guide.txt도 수정된 그대로예요. 쓰던 검색 안내를 건드리지 않았어요.', TERM),
    ],
    core='새 개념 하나: 워크트리 = 같은 저장소의 다른 브랜치를 꺼낸 또 하나의 폴더.\n\n'
         '시작: 1번과 같은 상태(새로 준비).\n'
         '행동: worktree add ../hotfix hotfix → worktree list → cat ../hotfix/guide.txt → status.\n'
         '관찰 근거: worktree list의 두 줄([main]·[hotfix]), 새 폴더의 긴급 창구 안내, work의 수정된 guide.txt.\n'
         '판정: git worktree list의 폴더 집합이 정확히 {work=main, ../hotfix=hotfix}이고 work의 브랜치·커밋·작업 파일이 시작 그대로다. '
         'git worktree add ../hotfix(브랜치 생략, 같은 이름의 기존 브랜치)도 같은 상태라 통과한다. '
         'work 안의 hotfix 폴더, 분리된 HEAD(--detach), switch -f, 쓰던 변경 커밋은 실패한다.',
    complexity=dict(new_concepts=['워크트리: 같은 저장소의 브랜치를 꺼낸 또 하나의 폴더'],
                    prerequisite_experience='1번의 전환 거절, bash-basics의 ../ 경로와 cat.',
                    changed_condition='전환 대신 옆 폴더에 같은 저장소의 다른 브랜치를 꺼낸다.',
                    observable_evidence='worktree list의 두 폴더와 각 브랜치, 두 폴더의 서로 다른 guide.txt.',
                    learner_edited_lines=0, new_external_services=0),
))

# 3 -----------------------------------------------------------------------------------------
STEPS.append(dict(
    id=ST[2], title='hotfix 폴더에서 커밋하고 work에서 확인하세요',
    objectives=['다른 폴더에서 만든 커밋도 같은 저장소의 브랜치에 바로 남아요.'],
    goal='이번 문제는 `hotfix` 폴더를 꺼내 둔 상태에서 시작해요. `work` 옆의 `hotfix` 폴더에 `hotfix` 브랜치가 있어요. '
         '`work`의 `main`에는 커밋하지 않은 검색 안내가 있어요.\n\n'
         f'지수가 hotfix의 안내 끝에 `{HOURS}` 한 줄을 더해 달래요. '
         'clone으로 만든 복제본은 따로 떨어진 저장소예요. 워크트리에서 만든 커밋은 어디에 남는지 확인해요.\n\n'
         '**할 일**\n\n'
         '1. `cd ../hotfix`를 실행해 hotfix 폴더로 가세요.\n'
         '2. `git branch`를 실행해 별표가 `hotfix`에 있는지 확인하세요.\n'
         f'3. `{HOURS_ECHO}`를 실행해 안내 끝에 한 줄을 더하세요.\n'
         '4. `git add guide.txt`를 실행해 바꾼 안내를 준비 영역에 담으세요.\n'
         f'5. `{HOURS_COMMIT}`을 실행해 hotfix에 커밋하세요.\n'
         '6. `cd ../work`를 실행해 원래 폴더로 돌아오세요.\n'
         '7. `git log --oneline hotfix`를 실행해 방금 만든 커밋이 보이는지 확인하세요.\n'
         '8. `git status`를 실행해 main의 검색 안내가 그대로인지 확인하세요.\n'
         '9. 확인한 뒤 제출 버튼을 누르세요.',
    solution='# hotfix 브랜치를 꺼낸 옆 폴더로 가요.\n'
             'cd ../hotfix\n'
             '# 이 폴더의 현재 브랜치는 hotfix예요.\n'
             'git branch\n'
             '# 운영 시간 한 줄을 끝에 더하고 hotfix에 커밋해요.\n'
             f'{HOURS_ECHO}\n'
             'git add guide.txt\n'
             f'{HOURS_COMMIT}\n'
             '# work로 돌아와도 같은 저장소라 그 커밋이 보여요.\n'
             'cd ../work\n'
             'git log --oneline hotfix\n'
             '# main의 쓰던 변경은 그대로예요.\n'
             'git status',
    terminal=terminal({'worktrees': {'.': 'main', '../hotfix': 'hotfix'}, 'branch_files': {'hotfix': {'guide.txt': HOT2}}}, worktree=True),
    narration=[
        say('hotfix 폴더는 이미 꺼내져 있어요. 그 폴더에서 운영 시간 한 줄을 커밋해요.', f'text:지수가 hotfix의 안내 끝에 {HOURS} 한 줄을 더해 달래요.'),
        bash('cd ../hotfix', '먼저 hotfix 폴더로 가요.'),
        say('이제 터미널이 work 옆의 hotfix 폴더에 있어요.', TERM),
        run(['branch'], '이 폴더의 브랜치를 봐요.'),
        say('별표가 hotfix에 있어요. main 앞의 +는 다른 폴더에서 꺼내 쓰는 브랜치라는 표시예요.', TERM),
        say('조심하세요. cd ../hotfix를 빼먹으면 다음 명령이 work에서 실행돼요. 쓰던 검색 안내까지 main에 커밋돼요.',
            'text:cd ../hotfix를 실행해 hotfix 폴더로 가세요.'),
        bash(HOURS_ECHO, '안내 끝에 운영 시간을 더해요.'),
        say('출력은 없어요. hotfix 폴더의 guide.txt 끝에 한 줄이 붙었어요.', TERM),
        run(['add', 'guide.txt'], '바꾼 안내를 준비 영역에 담아요.'),
        say('출력 없이 끝났어요. 이제 커밋할 내용이 준비됐어요.', TERM),
        run(['commit', '-m', '운영 시간 안내'], '이 폴더에서 커밋해요.'),
        say('[hotfix 다음에 운영 시간 안내가 나와요. 커밋이 hotfix 브랜치에 남았어요.', TERM),
        bash('cd ../work', '원래 work 폴더로 돌아와요.'),
        say('터미널이 다시 main이 있는 work에 있어요.', TERM),
        run(['log', '--oneline', 'hotfix'], 'work에서 hotfix의 기록을 봐요.'),
        say('맨 위에 운영 시간 안내가 보여요. push나 fetch 없이 여기서 바로 보이죠?', TERM),
        say('두 폴더가 저장소 하나를 함께 쓰거든요. clone한 복제본이었다면 주고받아야 했을 거예요.',
            'text:clone으로 만든 복제본은 따로 떨어진 저장소예요.'),
        run(['status'], 'main의 상태도 확인해요.'),
        say('guide.txt는 여전히 수정된 상태예요. 쓰던 검색 안내는 커밋되지 않고 그대로 있어요.', TERM),
    ],
    core='새 개념 하나: 워크트리들은 저장소(커밋·브랜치) 하나를 함께 쓴다.\n\n'
         '시작: ../hotfix에 hotfix 워크트리가 이미 있다(준비 명령 git worktree add ../hotfix hotfix). work의 main에는 쓰던 검색 안내.\n'
         '행동: cd ../hotfix → branch(* hotfix, + main) → echo >> → add → commit → cd ../work → log --oneline hotfix → status.\n'
         '관찰 근거: 다른 폴더에서 만든 커밋이 push·fetch 없이 work의 log에 보인다. git-remote의 peer 복제본과 대조한다.\n'
         '판정: work 저장소에서 읽은 refs/heads/hotfix의 guide.txt가 운영 시간 줄까지 정확히 같고, 폴더 집합이 {work=main, ../hotfix=hotfix}이며 '
         'work의 브랜치·커밋·작업 파일이 그대로다. cd 없이 work에서 커밋하면 main 기록이 바뀌어 실패한다. 커밋하지 않고 파일만 고치면 실패한다.',
    complexity=dict(new_concepts=['여러 워크트리가 저장소 하나(커밋·브랜치)를 함께 써요'],
                    prerequisite_experience='2번의 worktree add, git-first의 add·commit, git-branch의 echo >>, git-remote의 cd ../work·peer 복제본.',
                    changed_condition='다른 폴더에서 커밋한 뒤 원래 폴더에서 그 브랜치를 본다.',
                    observable_evidence='hotfix 폴더의 git branch(+ main), work에서 본 log --oneline hotfix의 새 커밋, 그대로인 status.',
                    learner_edited_lines=1, new_external_services=0),
))

# 4 -----------------------------------------------------------------------------------------
STEPS.append(dict(
    id=ST[3], title='hotfix를 바탕으로 새 브랜치를 옆 폴더에 꺼내세요',
    objectives=['한 브랜치는 한 폴더에만 꺼낼 수 있어요. 같은 커밋이 하나 더 필요하면 새 브랜치로 꺼내요.'],
    goal='이번 문제도 `hotfix` 폴더를 꺼내 둔 상태에서 시작해요. `work`의 `main`에는 커밋하지 않은 검색 안내가 있어요.\n\n'
         '지수가 hotfix의 안내로 문구를 따로 실험해 보고 싶대요. `hotfix` 폴더는 그대로 둬요. `hotfix-try` 폴더를 하나 더 만들어야 해요.\n\n'
         '2번 명령의 `-b hotfix-try`는 새 브랜치 이름이에요. `hotfix`의 커밋에서 `hotfix-try`를 만들어 그 폴더에 꺼내요.\n\n'
         '**할 일**\n\n'
         '1. `git worktree add ../hotfix-try hotfix`를 실행해 hotfix를 한 번 더 꺼내 보세요. 거절 메시지를 읽으세요.\n'
         '2. `git worktree add -b hotfix-try ../hotfix-try hotfix`를 실행해 새 브랜치로 꺼내세요.\n'
         '3. `git worktree list`를 실행해 세 폴더의 브랜치를 확인하세요.\n'
         '4. 확인한 뒤 제출 버튼을 누르세요.',
    solution='# hotfix는 이미 ../hotfix 폴더에 꺼내져 있어서 거절돼요.\n'
             'git worktree add ../hotfix-try hotfix\n'
             '# -b로 hotfix의 커밋에서 새 브랜치 hotfix-try를 만들어 꺼내요.\n'
             'git worktree add -b hotfix-try ../hotfix-try hotfix\n'
             '# 폴더 셋이 각자 다른 브랜치를 꺼내고 있어요.\n'
             'git worktree list',
    terminal=terminal({'worktrees': {'.': 'main', '../hotfix': 'hotfix', '../hotfix-try': 'hotfix-try'},
                       'branch_files': {'hotfix': {'guide.txt': HOT}, 'hotfix-try': {'guide.txt': HOT}}}, worktree=True),
    narration=[
        say('hotfix 폴더는 그대로 두고, 같은 안내로 실험할 폴더를 하나 더 만들어요.', 'text:hotfix-try 폴더를 하나 더 만들어야 해요.'),
        run(['worktree', 'add', '../hotfix-try', 'hotfix'], '먼저 hotfix를 한 번 더 꺼내 볼게요.', exit_code=128),
        say('fatal이에요. hotfix는 이미 hotfix 폴더에서 쓰고 있다고 거절해요. 한 브랜치는 한 폴더에만 꺼내져요.', TERM),
        say('조심하세요. 여기서 -f를 붙이면 hotfix가 두 폴더에 함께 꺼내져요. 한쪽에서 커밋하면 다른 폴더의 상태가 어긋나요.',
            'text:hotfix를 한 번 더 꺼내 보세요.'),
        say('-b hotfix-try는 hotfix의 커밋에서 새 브랜치를 만들어 꺼내요.', 'text:hotfix의 커밋에서 hotfix-try를 만들어 그 폴더에 꺼내요.'),
        run(['worktree', 'add', '-b', 'hotfix-try', '../hotfix-try', 'hotfix'], '새 브랜치 이름, 폴더, 출발할 브랜치를 차례로 줘요.'),
        say('new branch hotfix-try가 나와요. HEAD는 hotfix와 같은 긴급 창구 안내 커밋이에요.', TERM),
        run(['worktree', 'list'], '폴더 목록을 다시 봐요.'),
        say('줄이 셋이에요. 폴더마다 [main], [hotfix], [hotfix-try]가 붙어 있어요.', TERM),
    ],
    core='새 개념 하나: 한 브랜치는 한 워크트리에만 꺼낸다. 같은 커밋이 더 필요하면 새 브랜치(-b)로 꺼낸다.\n\n'
         '시작: ../hotfix에 hotfix 워크트리, work의 main에는 쓰던 검색 안내.\n'
         '행동: worktree add ../hotfix-try hotfix(실제 거절, 종료 코드 128) → worktree add -b hotfix-try ../hotfix-try hotfix → worktree list.\n'
         '관찰 근거: 「hotfix is already used by worktree at …/hotfix」 거절과 세 줄의 worktree list.\n'
         '판정: 폴더 집합이 정확히 {work=main, ../hotfix=hotfix, ../hotfix-try=hotfix-try}이고 hotfix-try와 hotfix의 guide.txt가 긴급 창구 안내다. '
         '--force로 hotfix를 두 번 꺼내면(같은 브랜치 두 폴더) 실패한다. work 안의 폴더·다른 출발점은 실패한다.\n'
         '주의: --force로 같은 브랜치를 두 폴더에 꺼내면 한쪽 커밋 뒤 다른 폴더의 인덱스가 거꾸로 바뀐 상태로 보인다(실측).',
    complexity=dict(new_concepts=['한 브랜치는 한 워크트리에만 꺼내요(더 필요하면 -b로 새 브랜치)'],
                    prerequisite_experience='2·3번의 worktree add·list, git-branch의 새 브랜치 만들기.',
                    changed_condition='이미 꺼낸 브랜치를 두 번째 폴더에 또 꺼내려 한다.',
                    observable_evidence='already used by worktree 거절, 세 폴더의 서로 다른 브랜치.',
                    learner_edited_lines=0, new_external_services=0),
))

# 5 -----------------------------------------------------------------------------------------
STEPS.append(dict(
    id=ST[4], title='다 쓴 hotfix 폴더를 정리하세요',
    objectives=['git worktree remove는 꺼낸 폴더만 정리하고 브랜치와 커밋은 남겨요.'],
    goal='이번 문제는 hotfix 작업을 마친 상태에서 시작해요. `hotfix` 폴더에서 운영 시간 안내까지 커밋해 뒀어요. '
         '그 폴더에 커밋하지 않은 변경은 없어요. `work`의 `main`에는 쓰던 검색 안내가 있어요.\n\n'
         '다 쓴 폴더는 `git worktree remove`로 정리해요. 이 명령은 그 폴더와 저장소에 남은 폴더 기록을 함께 지워요.\n\n'
         '**할 일**\n\n'
         '1. `git worktree list`를 실행해 정리 전 폴더를 확인하세요.\n'
         '2. `git worktree remove ../hotfix`를 실행해 hotfix 폴더를 정리하세요.\n'
         '3. `git worktree list`를 실행해 `work`만 남았는지 확인하세요.\n'
         '4. `git log --oneline hotfix`를 실행해 hotfix의 커밋이 남아 있는지 확인하세요.\n'
         '5. 확인한 뒤 제출 버튼을 누르세요.',
    solution='# 정리 전에는 work와 hotfix 두 폴더가 있어요.\n'
             'git worktree list\n'
             '# 다 쓴 hotfix 폴더와 그 폴더의 기록을 함께 정리해요.\n'
             'git worktree remove ../hotfix\n'
             '# work만 남았어요.\n'
             'git worktree list\n'
             '# 폴더를 정리해도 hotfix 브랜치의 커밋은 남아요.\n'
             'git log --oneline hotfix',
    terminal=terminal({'worktrees': {'.': 'main'}, 'branch_files': {'hotfix': {'guide.txt': HOT2}}}, hours_committed=True, worktree=True),
    narration=[
        say('hotfix 일은 커밋까지 끝났어요. 이제 다 쓴 폴더를 정리해요.', 'text:hotfix 폴더에서 운영 시간 안내까지 커밋해 뒀어요.'),
        run(['worktree', 'list'], '정리 전 폴더 목록이에요.'),
        say('work와 hotfix, 두 줄이 있어요.', TERM),
        run(['worktree', 'remove', '../hotfix'], 'remove에 정리할 폴더를 줘요.'),
        say('출력 없이 끝났어요. hotfix 폴더가 지워졌어요.', TERM),
        run(['worktree', 'list'], '목록을 다시 봐요.'),
        say('work 한 줄만 남았어요. 저장소에 남아 있던 폴더 기록도 함께 지워졌어요.', TERM),
        run(['log', '--oneline', 'hotfix'], '브랜치의 기록을 확인해요.'),
        say('운영 시간 안내 커밋이 그대로 있어요. remove는 폴더만 정리하고 브랜치는 남겨요.', TERM),
        say('조심하세요. 그 폴더에 커밋하지 않은 변경이 있으면 remove가 거절해요. --force로 지우면 그 변경은 되찾을 수 없어요.',
            'text:그 폴더에 커밋하지 않은 변경은 없어요.'),
    ],
    core='새 개념 하나: worktree remove는 워크트리(폴더와 그 기록)만 지우고 브랜치·커밋은 남긴다.\n\n'
         '시작: hotfix에 운영 시간 안내까지 커밋돼 있고 ../hotfix 워크트리는 깨끗하다. work의 main에는 쓰던 검색 안내.\n'
         '행동: worktree list → worktree remove ../hotfix → worktree list → log --oneline hotfix.\n'
         '관찰 근거: 목록이 두 줄에서 한 줄로, hotfix의 커밋은 그대로.\n'
         '판정: 폴더 집합이 정확히 {work=main}이고 hotfix 브랜치의 guide.txt가 운영 시간 줄까지 같으며 work가 그대로다. '
         'rm -r ../hotfix만 하면 지운 폴더의 기록이 남아 실패한다. 브랜치를 지우면 실패한다.\n'
         '주의: 커밋하지 않은 변경이 있으면 remove가 거절하고(실측) --force는 그 변경을 지운다.',
    complexity=dict(new_concepts=['worktree remove: 폴더만 정리하고 브랜치·커밋은 남겨요'],
                    prerequisite_experience='2~4번의 worktree add·list, 3번의 log --oneline.',
                    changed_condition='일을 마친 워크트리를 정리한다.',
                    observable_evidence='worktree list의 줄 수 변화, log --oneline hotfix의 남은 커밋.',
                    learner_edited_lines=0, new_external_services=0),
))

# 6 -----------------------------------------------------------------------------------------
STEPS.append(dict(
    id=ST[5], title='손으로 지운 폴더의 남은 기록을 정리하세요',
    objectives=['폴더를 rm으로만 지우면 저장소에 그 폴더의 기록이 남아요. git worktree prune이 남은 기록을 지워요.'],
    goal='이번 문제도 hotfix 작업을 마친 상태에서 시작해요. `hotfix` 폴더에 운영 시간 안내까지 커밋돼 있어요. '
         '`work`의 `main`에는 쓰던 검색 안내가 있어요.\n\n'
         '이번에는 누군가 파일 탐색기에서 `hotfix` 폴더를 지운 상황을 직접 만들어요. '
         '폴더가 사라진 뒤 저장소가 그 폴더를 어떻게 기억하는지 확인해요. '
         '`git worktree prune`은 폴더가 사라진 기록을 찾아 정리해요.\n\n'
         '**할 일**\n\n'
         '1. `rm -r ../hotfix`를 실행해 hotfix 폴더를 지우세요.\n'
         '2. `git worktree list`를 실행해 지운 폴더가 어떻게 보이는지 확인하세요.\n'
         '3. `git worktree add ../hotfix hotfix`를 실행해 같은 자리에 다시 꺼내 보세요. 거절 메시지를 읽으세요.\n'
         '4. `git worktree prune`을 실행해 남은 기록을 정리하세요.\n'
         '5. `git worktree list`를 실행해 `work`만 남았는지 확인하세요.\n'
         '6. 확인한 뒤 제출 버튼을 누르세요.',
    solution='# 파일 탐색기에서 지운 것처럼 폴더만 지워요.\n'
             'rm -r ../hotfix\n'
             '# 저장소에는 그 폴더의 기록이 prunable로 남아 있어요.\n'
             'git worktree list\n'
             '# 남은 기록이 자리를 붙잡고 있어서 다시 꺼내기가 거절돼요.\n'
             'git worktree add ../hotfix hotfix\n'
             '# 폴더가 사라진 기록을 정리해요.\n'
             'git worktree prune\n'
             'git worktree list',
    terminal=terminal({'worktrees': {'.': 'main'}, 'branch_files': {'hotfix': {'guide.txt': HOT2}}}, hours_committed=True, worktree=True),
    narration=[
        say('이번엔 remove 대신 폴더를 직접 지운 상황을 만들어요.', 'text:누군가 파일 탐색기에서 hotfix 폴더를 지운 상황을 직접 만들어요.'),
        bash('rm -r ../hotfix', 'rm -r로 hotfix 폴더를 지워요.'),
        say('출력 없이 폴더가 사라졌어요.', TERM),
        run(['worktree', 'list'], '저장소는 이 폴더를 어떻게 기억할까요?'),
        say('hotfix 줄이 아직 있어요. 끝에 prunable이 붙었죠? 폴더는 없는데 기록만 남았다는 표시예요.', TERM),
        run(['worktree', 'add', '../hotfix', 'hotfix'], '같은 자리에 다시 꺼내 볼게요.', exit_code=128),
        say('거절됐어요. 지운 폴더가 아직 등록돼 있다고 알려 줘요. 남은 기록이 그 자리를 붙잡고 있어요.', TERM),
        say('조심하세요. 폴더만 지우고 끝내면 그 기록이 남아 같은 자리에 다시 꺼낼 수 없어요. 지운 뒤엔 prune으로 정리하세요.',
            'text:git worktree prune은 폴더가 사라진 기록을 찾아 정리해요.'),
        run(['worktree', 'prune'], 'prune으로 남은 기록을 정리해요.'),
        say('출력 없이 끝났어요.', TERM),
        run(['worktree', 'list'], '목록을 다시 봐요.'),
        say('work 한 줄만 남았어요. hotfix 브랜치와 커밋은 지우지 않았어요.', TERM),
    ],
    core='새 개념 하나: 폴더만 지우면 남는 워크트리 기록과 이를 지우는 worktree prune.\n\n'
         '시작: 5번과 같은 상태(새로 준비).\n'
         '행동: rm -r ../hotfix(bash-basics에서 배운 명령으로 손으로 지운 상황을 만든다) → worktree list(prunable) → '
         'worktree add ../hotfix hotfix(실제 거절, 종료 코드 128) → worktree prune → worktree list.\n'
         '관찰 근거: prunable 표시, 「missing but already registered worktree」 거절, 한 줄로 줄어든 목록.\n'
         '판정: 폴더 집합이 정확히 {work=main}이고(지운 폴더의 남은 기록은 다른 항목으로 보여 실패) hotfix 브랜치의 기록과 work가 그대로다. '
         '지운 뒤 worktree remove ../hotfix도 같은 기록을 지워 통과한다(실측). rm만 하거나 add -f로 다시 꺼내면 실패한다.',
    complexity=dict(new_concepts=['worktree prune: 폴더가 사라진 워크트리 기록을 지워요'],
                    prerequisite_experience='5번의 worktree remove·list, bash-basics의 rm -r.',
                    changed_condition='remove 대신 폴더를 직접 지운다.',
                    observable_evidence='worktree list의 prunable 표시, 다시 꺼내기 거절, prune 뒤 한 줄.',
                    learner_edited_lines=0, new_external_services=0),
))

# 7 -----------------------------------------------------------------------------------------
STEPS.append(dict(
    id=ST[6], title='쓰던 변경을 지키며 급한 수정을 마치세요',
    objectives=['쓰던 변경을 그대로 두고, 다른 폴더에서 hotfix를 커밋한 뒤 그 폴더를 정리해요.'],
    goal='마지막 문제예요. 처음과 같은 상태에서 시작해요. `main`의 `guide.txt`에는 커밋하지 않은 검색 안내가 있어요. '
         '`hotfix`에는 지수의 긴급 창구 안내가 있어요.\n\n'
         f'쓰던 검색 안내는 그대로 두세요. `hotfix`의 `guide.txt` 끝에 `{HOURS}`를 더해요. 그 한 줄을 hotfix에 커밋해야 해요. '
         '일이 끝나면 꺼낸 폴더를 정리해서 `work`만 남겨요. 앞에서 쓴 명령으로 충분해요.\n\n'
         '**할 일**\n\n'
         '1. `hotfix` 브랜치를 `work` 옆의 `hotfix` 폴더에 꺼내세요.\n'
         '2. 그 폴더로 가세요.\n'
         f'3. `guide.txt` 끝에 `{HOURS}` 한 줄을 더하세요.\n'
         '4. 바꾼 안내를 준비 영역에 담으세요.\n'
         '5. 담은 안내를 hotfix에 커밋하세요.\n'
         '6. `work`로 돌아오세요.\n'
         '7. `git log --oneline hotfix`를 실행해 새 커밋을 확인하세요.\n'
         '8. 다 쓴 `hotfix` 폴더를 정리하세요.\n'
         '9. `git worktree list`를 실행해 `work`만 남았는지 확인하세요.\n'
         '10. `git status`를 실행해 쓰던 검색 안내가 그대로인지 확인하세요.\n'
         '11. 확인한 뒤 제출 버튼을 누르세요.',
    solution='# 브랜치를 바꾸지 않고 hotfix를 옆 폴더에 꺼내요.\n'
             'git worktree add ../hotfix hotfix\n'
             '# 그 폴더에서 운영 시간 한 줄을 더해 hotfix에 커밋해요.\n'
             'cd ../hotfix\n'
             f'{HOURS_ECHO}\n'
             'git add guide.txt\n'
             f'{HOURS_COMMIT}\n'
             '# work로 돌아와 같은 저장소의 hotfix 기록을 봐요.\n'
             'cd ../work\n'
             'git log --oneline hotfix\n'
             '# 다 쓴 폴더는 remove로 폴더와 기록을 함께 정리해요.\n'
             'git worktree remove ../hotfix\n'
             'git worktree list\n'
             '# main의 쓰던 변경은 커밋되지 않고 그대로예요.\n'
             'git status',
    terminal=terminal({'worktrees': {'.': 'main'}, 'branch_files': {'hotfix': {'guide.txt': HOT2}}}),
    narration=[
        say('쓰던 검색 안내를 지키면서 hotfix에 한 줄을 커밋하고, 폴더까지 정리해요.', 'text:일이 끝나면 꺼낸 폴더를 정리해서 work만 남겨요.'),
        run(['worktree', 'add', '../hotfix', 'hotfix'], '브랜치를 바꾸는 대신 hotfix를 옆 폴더에 꺼내요.'),
        say('HEAD가 지수의 긴급 창구 안내 커밋에 있어요. hotfix 폴더가 생겼어요.', TERM),
        bash('cd ../hotfix', '그 폴더로 가요.'),
        say('이제 명령이 hotfix 폴더에서 실행돼요.', TERM),
        bash(HOURS_ECHO, '안내 끝에 운영 시간을 더해요.'),
        say('출력은 없어요. hotfix 폴더의 안내만 바뀌었어요.', TERM),
        run(['add', 'guide.txt'], '바꾼 안내를 담아요.'),
        say('출력 없이 준비 영역에 담겼어요.', TERM),
        run(['commit', '-m', '운영 시간 안내'], 'hotfix에 커밋해요.'),
        say('[hotfix로 시작하는 줄이 나와요. 커밋이 hotfix에 남았어요.', TERM),
        bash('cd ../work', 'work로 돌아와요.'),
        say('다시 main이 있는 work 폴더예요.', TERM),
        run(['log', '--oneline', 'hotfix'], 'hotfix의 기록을 봐요.'),
        say('운영 시간 안내가 맨 위에 있어요. 같은 저장소라 여기서도 보여요.', TERM),
        run(['worktree', 'remove', '../hotfix'], '다 쓴 폴더를 정리해요.'),
        say('출력 없이 폴더와 그 기록이 함께 지워졌어요.', TERM),
        run(['worktree', 'list'], '남은 폴더를 봐요.'),
        say('work 한 줄만 남았어요.', TERM),
        run(['status'], '마지막으로 main의 상태를 봐요.'),
        say('guide.txt는 수정된 그대로예요. 검색 안내를 지키면서 hotfix를 마쳤어요.', 'text:쓰던 검색 안내는 그대로 두세요.'),
    ],
    core='새 개념 없이 1~6번의 판단을 조합하는 마지막 수행이다.\n\n'
         '시작: 1번과 같은 상태(워크트리 없음, hotfix에는 긴급 창구 커밋, work의 main에는 쓰던 검색 안내).\n'
         '행동: worktree add → cd → echo >> → add → commit → cd ../work → log → worktree remove → list → status. 할 일은 목표 상태만 주고 명령은 학습자가 고른다(확인 명령만 명시).\n'
         '관찰 근거: log의 새 커밋, 한 줄 목록, 그대로인 status.\n'
         '판정: 폴더 집합이 정확히 {work=main}, hotfix 브랜치의 guide.txt가 운영 시간 줄까지 같고, work의 브랜치·커밋·작업 파일이 그대로다. '
         'main에 커밋, 폴더 정리 누락, rm만 하고 기록을 남김, switch -f로 쓰던 변경을 지움은 실패한다.',
    complexity=dict(new_concepts=[], prerequisite_experience='1~6번 전체.',
                    changed_condition='명령을 직접 골라 꺼내기·커밋·정리를 한 번에 한다.',
                    observable_evidence='log --oneline hotfix의 새 커밋, worktree list 한 줄, status의 수정된 guide.txt.',
                    learner_edited_lines=1, new_external_services=0),
))

# -- hierarchy --------------------------------------------------------------------------------
PREMISE = ('여러분은 메모 서비스 팀의 안내 담당이에요. main에서 guide.txt에 검색 안내를 쓰는 중이고 아직 커밋하지 않았어요. '
           '동료 지수는 hotfix 브랜치에 긴급 창구 안내를 커밋해 뒀어요. 문제마다 정해진 시작 상태로 새로 준비돼요.')
HIERARCHY = [
    dict(id=CH[0], title='작업을 둔 채 다른 브랜치를 꺼내요',
         objectives=['쓰던 변경 때문에 전환이 막히는 문제를 겪고, 워크트리로 다른 브랜치를 옆 폴더에 꺼내요.',
                     '다른 폴더에서 만든 커밋도 같은 저장소에 남는다는 것을 확인해요.'],
         units=[dict(id=UN[0], title='전환 대신 옆 폴더', steps=ST[0:3],
                     objectives=['브랜치를 바꾸지 않고 다른 브랜치에서 일하고, 그 커밋을 원래 폴더에서 확인해요.'],
                     premise=PREMISE)]),
    dict(id=CH[1], title='워크트리의 규칙을 지키고 정리해요',
         objectives=['한 브랜치는 한 폴더에만 꺼낸다는 규칙을 확인해요.', '다 쓴 폴더를 remove로, 손으로 지운 폴더의 기록을 prune으로 정리해요.'],
         units=[dict(id=UN[1], title='한 브랜치는 한 폴더에', steps=ST[3:4],
                     objectives=['이미 꺼낸 브랜치를 또 꺼내면 거절되는 것을 보고, 새 브랜치로 꺼내요.'],
                     premise='hotfix 폴더가 이미 꺼내져 있어요. work의 main에는 쓰던 검색 안내가 있어요. 문제마다 이 상태로 새로 준비돼요.'),
                dict(id=UN[2], title='다 쓴 폴더 정리', steps=ST[4:6],
                     objectives=['폴더를 정리해도 브랜치와 커밋이 남는 것을 확인하고, 남은 폴더 기록을 정리해요.'],
                     premise='hotfix 작업을 커밋까지 마쳤고 hotfix 폴더는 깨끗해요. work의 main에는 쓰던 검색 안내가 있어요. 문제마다 이 상태로 새로 준비돼요.')]),
    dict(id=CH[2], title='쓰던 변경을 지키며 급한 수정을 마쳐요',
         objectives=['앞에서 쓴 명령을 골라 꺼내기·커밋·정리를 한 번에 해요.'],
         units=[dict(id=UN[3], title='마지막 수행', steps=ST[6:7],
                     objectives=['새 개념 없이 1·2장의 판단을 조합해요.'],
                     premise='처음과 같은 상태예요. 워크트리는 없고, hotfix에는 지수의 커밋, work의 main에는 쓰던 검색 안내가 있어요.')]),
]

LEARN = ['커밋하지 않은 작업이 있을 때 브랜치 전환이 막히는 이유를 겪어요.',
         'git worktree로 다른 브랜치를 옆 폴더에 꺼내 커밋하고, 같은 저장소에 남는 것을 확인해요.',
         '한 브랜치는 한 폴더에만 꺼낸다는 규칙을 지키고, 다 쓴 폴더를 remove·prune으로 정리해요.']
CHALLENGE = (f'main의 커밋하지 않은 검색 안내를 그대로 둔 채, 옆 폴더에서 hotfix에 「{HOURS}」 한 줄을 커밋하세요. '
             '끝나면 꺼낸 폴더를 정리해 처음 폴더만 남겨야 해요.')
CONSTRAINTS = ['Git 첫 기록·브랜치·공유·브랜치 심화 수업의 status·switch·add·commit·show·log를 안다고 가정해요.',
               '실제 Git 저장소에서 실습해요. 채점은 터미널 출력이 아니라 저장소의 실제 폴더 목록과 브랜치 기록을 읽어요.',
               '문제마다 정해진 시작 상태로 새로 준비돼요. 앞 문제의 결과가 이어지지 않아요.',
               'stash, worktree의 move·lock·repair, 분리된 HEAD 워크트리는 다루지 않아요.']
QUESTION = '브랜치를 바꾸지 않고 다른 브랜치에서 일하려면 어떻게 할까요?'

OPENINGS = ['이 수업에서는 쓰던 변경을 그대로 두고, 다른 브랜치를 옆 폴더에서 함께 다뤄요.',
            '먼저 전환이 막히는 걸 겪어요. 그다음 워크트리로 꺼내 커밋하고, 한 브랜치는 한 폴더에만 꺼낸다는 규칙을 봐요.',
            '마지막엔 다 쓴 폴더를 remove와 prune으로 정리해요.']

SOURCES = [
    dict(url='https://git-scm.com/docs/git-worktree', checked_at='2026-11-11',
         finding='저장소 하나에 여러 작업 트리를 붙여 한 번에 여러 브랜치를 꺼낼 수 있다. git worktree add <path> <branch>로 기존 브랜치를, -b로 새 브랜치를 꺼낸다. '
                 'remove는 깨끗한 워크트리만 지우고(--force로 강제), 손으로 지운 워크트리의 관리 파일은 prune으로 정리한다. '
                 'add는 다른 워크트리에서 이미 쓰는 브랜치와, 지웠지만 등록이 남은 경로를 기본으로 거절한다(--force가 이를 넘는다).',
         certainty='설치된 Git 2.56.0의 git help worktree(같은 문서) 원문을 열어 확인했다. 웹 페이지는 같은 문서의 공개본이다.'),
    dict(url='https://git-scm.com/docs/git-switch', checked_at='2026-11-11',
         finding='switch는 작업 트리와 인덱스를 대상 브랜치에 맞춘다. 커밋하지 않은 변경이 덮일 때는 거절하고, -f(--discard-changes)는 쓰던 변경을 버린다.',
         certainty='Git 문서의 동작 설명이다. 거절 메시지와 종료 코드 1은 Git 2.56.0 임시 저장소에서 실측했다.'),
    dict(url='https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging', checked_at='2026-11-11',
         finding='Pro Git의 기본 분기 장은 hotfix 브랜치로 급한 수정을 하는 상황과, 커밋하지 않은 변경이 있으면 전환 전에 작업 상태를 깨끗이 해야 한다는 점을 설명한다.',
         certainty='상황 설정(hotfix)의 출처다. 이 수업은 stash 대신 워크트리를 다룬다.'),
]


def presentation():
    return dict(objectives=LEARN,
                chapters={c['id']: c['objectives'] for c in HIERARCHY},
                units={u['id']: dict(objectives=u['objectives'], premise=u['premise']) for c in HIERARCHY for u in c['units']},
                learning_strategy='먼저 전환이 막히는 것을 겪어요. 그다음 옆 폴더에 꺼내 커밋하고, 같은 저장소에 남는지 원래 폴더에서 확인해요.')


def content():
    tasks = []
    for s in STEPS:
        tasks.append(dict(id=s['id'], title=s['title'], goal=s['goal'], language='git', starter_code='', solution=s['solution'],
                          tests=[], required=True, git_terminal=s['terminal'], narration=s['narration']))
    return dict(description='쓰던 변경을 그대로 두고 다른 브랜치를 옆 폴더에 꺼내 커밋한 뒤, 다 쓴 폴더를 정리해요.',
                presentation=presentation(), tasks=tasks)


def policy():
    paths = ['AGENTS.md', 'docs/content-rules.md', 'docs/voice.md', 'docs/agents/narration.md', 'docs/lesson-prds.md']
    artifacts = [dict(path=path, text=(ROOT / path).read_text(encoding='utf-8')) for path in paths]
    rules = ['문제 상황(전환 거절)을 먼저 겪은 뒤 워크트리를 들인다. 한 스텝에 새 개념 하나(추가·공유·한 폴더 규칙·remove·prune).',
             '학생 수정은 0~1줄(안내 한 줄). 각 스텝은 정해진 시작 상태로 새로 준비하고 시작 상태를 먼저 알린다.',
             '실제 Git 저장소의 폴더 목록(git worktree list)·브랜치 기록·작업 파일로 채점한다. 터미널 출력과 커밋 메시지는 근거가 아니다.',
             '실전적인 쉬운 명령(status·switch·show·log --oneline·worktree add/list/remove/prune)만 학생 명령으로 쓰고 내부 검사 옵션은 노출하지 않는다.',
             '해설은 명령 하나의 실제 출력을 읽은 뒤 다음 명령으로 넘어가고, 실제로 흔한 실수(switch -f, cd 누락, --force, 폴더만 삭제)에서만 「조심하세요」를 쓴다.',
             '해설은 별도 시연 저장소에서 하고 학습자의 실습 폴더를 바꾸지 않는다.']
    return dict(revision=policy_revision(artifacts), artifacts=artifacts, rules=rules)


def prd(preview):
    chapters = []
    by_id = {s['id']: s for s in STEPS}
    for c in HIERARCHY:
        units = []
        for u in c['units']:
            units.append(dict(id=u['id'], title=u['title'], objectives=u['objectives'], premise=u['premise'],
                              steps=[dict(id=i, title=by_id[i]['title'], objectives=by_id[i]['objectives'], core_flow=by_id[i]['core'],
                                          complexity=by_id[i]['complexity']) for i in u['steps']]))
        chapters.append(dict(id=c['id'], title=c['title'], objectives=c['objectives'], units=units))
    rep = by_id[ST[1]]
    document = dict(
        schema_version=1, id=LESSON_ID, title=TITLE, course=COURSE_ID,
        audience='자바 과정에서 Git 첫 기록·브랜치·공유·브랜치 심화를 마친 학습자. GitLab MR 수업 앞의 선택 수업이다.',
        objectives=LEARN,
        prerequisites=['git-first', 'git-branch', 'git-remote', 'git-branch-advanced', 'bash-basics(cd ../, cat, echo >>, rm -r)'],
        scope=[s['title'] for s in STEPS],
        out_of_scope=['stash·커밋 되돌리기로 쓰던 변경을 치워 두는 방법',
                      'worktree move·lock·unlock·repair, 분리된 HEAD 워크트리(--detach), 원격 브랜치 추적(--track)',
                      '같은 브랜치를 --force로 두 폴더에 꺼내는 사용(위험을 말로만 짚는다), 서브모듈'],
        policy_snapshot=policy(), sources=SOURCES,
        strategy='1번에서 전환 거절을 직접 겪는다(원칙 9). 2·3번은 워크트리 추가와 저장소 공유를 한 개념씩 확인한다. '
                 '4번은 실제 거절을 본 뒤 -b로 새 브랜치를 꺼내고, 5·6번은 정리 두 방법을 나눈다. 마지막 수행은 새 개념 없이 조합한다.',
        chapters=chapters,
        grading=['채점기는 실습 저장소 work에서 git worktree list --porcelain을 읽어 폴더 집합을 「. 또는 ../이름 → 브랜치」로 비교한다. '
                 '지운 폴더의 남은 기록(prunable)과 다른 위치의 폴더는 다른 항목으로 보여 실패한다.',
                 '브랜치 기록은 work 저장소의 refs/heads/<브랜치> 트리의 파일 목록과 바이트로 비교한다. 다른 폴더에서 만든 커밋도 같은 저장소에서 읽는다.',
                 '모든 스텝은 work의 현재 브랜치 main·커밋 수 1·HEAD 파일·작업 파일(쓰던 검색 안내)을 함께 확인한다.',
                 '1번만 show hotfix:guide.txt의 성공 실행 기록을 함께 요구한다. 커밋 메시지·터미널 출력은 근거가 아니다.',
                 '이 채점 항목(worktrees, branch_files)과 준비 명령 git worktree add ../이름 브랜치는 이 수업과 함께 플레이어에 추가했다. 이 기능이 있는 플레이어 릴리스가 먼저 필요하다.'],
        reset=['스텝마다 빈 저장소에서 같은 준비 명령(기본 안내 커밋, hotfix의 긴급 창구 커밋, 필요하면 운영 시간 커밋과 git worktree add ../hotfix hotfix, '
               '마지막에 쓰던 검색 안내 파일)을 실행해 새로 만든다. 「초기화」는 새 실습 폴더에서 같은 준비를 다시 한다. 해설은 별도 시연 저장소에서 같은 준비로 시작한다.'],
        narration=['문제의 시작 상태와 제약 문장을 정확히 강조하고, 명령 하나의 실제 출력을 읽은 뒤 다음 명령으로 넘어간다. '
                   '거절되는 명령은 실제 종료 코드(switch 1, worktree add 128)로 시연하고 메시지를 읽는다. 실제 음성 동기화는 앱 확인이 필요하다.'],
        verification=['단위·수업 데이터: tests/git_worktree.rs가 공개 수업 JSON의 7개 스텝을 플레이어의 채점 경로(check_exercise)로 실행한다. '
                      '시작 상태 실패, 해설 재생 통과, 동등 풀이 통과, 흔한 오답 거절, 채점 항목 검증을 확인한다.',
                      'examples/validate_redesigned_git.rs git-worktree: 학생 저장소 시작 실패·해설 분리·연속 풀이·초기화 재생.',
                      'tests/final_terminal_challenges.rs: 마지막 수행의 정답·동등 풀이·오답.',
                      '빌드: build-redesigned-git --lesson, narration_review, build-redesigned-course-bundle --check, lesson_registry. 화면·실제 음성·Windows Git Bash는 별도 검증 범위로 남긴다.'],
        representative=dict(step_id=ST[1], prompt=rep['goal'],
                            starter_state='main 커밋 1개, guide.txt에 커밋하지 않은 검색 안내. hotfix에는 지수의 긴급 창구 커밋. 워크트리는 work 하나.',
                            expected_action='git worktree add ../hotfix hotfix로 hotfix를 옆 폴더에 꺼낸 뒤 list·cat·status로 확인한다.',
                            acceptance='폴더 집합이 정확히 {work=main, ../hotfix=hotfix}이고 work의 브랜치·커밋·작업 파일이 그대로다. work 안의 폴더·분리된 HEAD·switch -f·쓰던 변경 커밋은 실패한다.',
                            reset='「초기화」는 새 실습 폴더에서 같은 시작 상태를 다시 만든다.',
                            narration='worktree add의 실제 출력과 두 줄 목록, 두 폴더의 서로 다른 안내를 차례로 읽는다. 경로를 hotfix로 줄여 쓰는 실수를 짚는다.'),
        lesson_preview=preview,
        approval=dict(status='draft'),
        change_history=['2026-11-10 사용자 요청과 계획 승인: 「워크 트리에 대한 수업도 해야 하는데」, 「깃 워크 트리 수업도 적절히 구성해서 추가해줘」, 「다 수락할게」.',
                        '2026-11-11 승인 범위 안의 정식 제작: 계획의 다섯 경험(전환 문제, 추가, 공유, 같은 브랜치 거절, 정리)을 유지하고 '
                        '정리를 remove와 prune 두 스텝으로 나눴다(한 스텝 한 개념). 4번은 거절 뒤 -b 새 브랜치로 꺼내는 행동으로 채점한다. 새 개념 없는 마지막 수행을 더했다.',
                        '2026-11-11 실제 상태 채점을 위해 플레이어에 worktrees·branch_files 목표와 준비 명령 git worktree add ../이름 브랜치를 추가했다.'],
    )
    return approve(document, by='사용자(jhs512)',
                   evidence='2026-11-10 사용자: 「워크 트리에 대한 수업도 해야 하는데」, 「깃 워크 트리 수업도 적절히 구성해서 추가해줘」, 「다 수락할게」'
                            '(git-branch-advanced 뒤·github-pr 앞 배치, 작업 중 전환 문제 → worktree add → 각 폴더 커밋과 같은 저장소 확인 → 같은 브랜치 두 폴더 거절 → remove/prune 정리의 계획과 PRD를 수락). '
                            '2026-11-11 사용자가 음성 세션에서 승인된 Git 워크트리 수업 진행을 다시 확인했다. '
                            '생성된 정식 JSON이나 개별 문장을 사용자가 직접 검수했다고 주장하지 않는다.')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    from curriculum_authority import alignment_source, course_intent, digest
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    course = next(c for c in catalog['courses'] if c['key'] == 'java')
    preview_public = dict(learn=LEARN, challenge=CHALLENGE, scenario=[s['title'] for s in STEPS], constraints=CONSTRAINTS, question=QUESTION)
    preview = dict(preview_public, lesson_key=KEY, lesson_id=LESSON_ID, origin='plan_approved_2026-11-10',
                   course_intent_sha256=digest(course_intent(course)))
    write(FOLDER / 'lesson-preview.json', preview)
    document = prd(preview_public)
    write(FOLDER / 'approved-prd.json', document)
    (FOLDER / 'approved-prd.md').write_text(render(document) + '\n', encoding='utf-8', newline='\n')
    authored = content()
    write(FOLDER / 'content.json', authored)
    write(FOLDER / 'preview-alignment.json', dict(
        status='reviewed', source_sha256=digest(alignment_source(preview, document, authored)), reviewed_at='2026-11-11',
        reason='Claude Code가 승인된 계획의 경험 순서·범위·제외 항목과 예고·PRD·본편·채점 구성을 대조했다. 사용자의 개별 원고 검수는 아니다.',
        scope='PRD 계층·전제·채점·초기화와 모든 스텝 필드(준비 명령·목표 상태 포함). 해설은 자체 검토 계층에서 확인한다.',
        schema_version=2))
    openings_path = ROOT / 'tools/redesigned_lessons/narration-openings.json'
    openings = json.loads(openings_path.read_text(encoding='utf-8'))
    openings[KEY] = OPENINGS
    openings_path.write_text(json.dumps(openings, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('wrote', FOLDER.relative_to(ROOT))


if __name__ == '__main__':
    main()
