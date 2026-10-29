"""git-branch final challenge: finish one feature on its branch, bring it into main, start the next from the merged main."""
from _common import todo

STEP = 'stp_2083b3dd-20f1-4b1c-9937-d2f70bfb6a1b'
T = '#git-demo-terminal'
BASE = '안내: 기본 안내\n'
MEMO = '안내: 기본 안내\n메모: 메모를 남겨요\n'
SEARCH = '안내: 기본 안내\n메모: 메모를 남겨요\n검색: 메모를 찾아요\n'


def git(args, say):
    return dict(action='git_command', args=args, say=say, target=T)


def run(command, say):
    return dict(action='bash_command', command=command, say=say, target=T)


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. 메모 기능은 memo 브랜치에서 만들어 main에 반영하고, 검색 기능은 반영된 main에서 search 브랜치로 시작해요.',
        'text:검색 기능은 메모 기능이 반영된 main에서 시작해야 해요.'),
    git(['branch', 'memo'], 'memo 브랜치를 만들어요.'),
    say('출력은 없어요. memo가 지금 main과 같은 커밋을 가리켜요.'),
    git(['switch', 'memo'], 'memo로 옮겨 가요.'),
    say("Switched to branch 'memo'가 나와요."),
    run('echo "메모: 메모를 남겨요" >> guide.txt', '메모 안내 한 줄을 더해요.'),
    say('출력 없이 guide.txt가 두 줄이 됐어요.'),
    git(['add', 'guide.txt'], '두 줄을 준비 영역에 담아요.'),
    say('출력은 없어요. 메모 줄이 준비됐어요.'),
    git(['commit', '-m', '메모 기능'], 'memo 브랜치에 커밋해요.'),
    say('memo 브랜치에만 새 기록이 생겼어요.'),
    git(['switch', 'main'], 'main으로 돌아가요.'),
    say('main의 guide.txt는 아직 한 줄이에요.'),
    git(['merge', 'memo'], 'memo를 main에 합쳐요.'),
    say('Fast-forward예요. main이 메모 기능 커밋으로 옮겨 갔어요.'),
    git(['branch', 'search'], '합쳐진 main에서 search 브랜치를 만들어요.'),
    say('search는 지금 main과 같은 커밋에서 출발해요.'),
    git(['switch', 'search'], 'search로 옮겨 가요.'),
    say("Switched to branch 'search'가 나와요."),
    run('echo "검색: 메모를 찾아요" >> guide.txt', '검색 안내 한 줄을 더해요.'),
    say('guide.txt가 세 줄이 됐어요.'),
    git(['add', 'guide.txt'], '세 줄을 담아요.'),
    say('출력은 없어요. 검색 줄이 준비됐어요.'),
    git(['commit', '-m', '검색 기능'], 'search에 커밋해요. main에는 아직 합치지 않아요.'),
    say('search만 한 커밋 앞서 있어요. main과 memo는 메모 기능 커밋에 있어요.'),
    git(['branch'], '브랜치 목록을 봐요.'),
    say('별표가 search에 있어요. memo, main도 함께 보여요.'),
    say('조심하세요. 병합하기 전에 search를 만들면 메모 안내가 없는 옛 main에서 출발해요.', T),
]

GOAL = ('자, 마지막 도전이에요. 기능 두 개를 차례로 개발해요. 지금은 main에 guide.txt `안내: 기본 안내` 한 줄만 기록돼 있어요.\n\n'
        '메모 기능은 memo 브랜치에서 `메모: 메모를 남겨요` 줄을 더해 커밋하고 main에 합쳐요. '
        '검색 기능은 메모 기능이 반영된 main에서 시작해야 해요. search 브랜치에서 `검색: 메모를 찾아요` 줄을 더해 커밋하고, main에는 아직 합치지 않아요. '
        '끝났을 때 서 있는 브랜치는 search예요. 명령과 커밋 설명은 직접 정해요.\n\n'
        + todo('memo 브랜치를 만들어 메모 줄을 커밋하세요.',
               'main에서 memo를 합치세요.',
               '합쳐진 main에서 search 브랜치를 만들어 검색 줄을 커밋하세요.',
               'search에 서 있는 채로 제출하세요.'))

STATE = dict(current_branch='search', commit_count=3, parent_count=1, clean=True, merge_in_progress=False,
             references={'refs/heads/main': 'HEAD^', 'refs/heads/memo': 'HEAD^', 'refs/heads/search': 'HEAD'},
             head_files={'guide.txt': SEARCH}, parent_files={'guide.txt': MEMO}, working_files={'guide.txt': SEARCH})

SPEC = dict(
    key='git-branch', course='java', revision='git-branch-11',
    reason='브랜치 만들기·전환·커밋·병합·병합된 main에서 다음 브랜치 시작을 목표 상태만 보고 스스로 이어 가는 마지막 도전이에요.',
    grading='실제 Git의 현재 브랜치, main·memo·search가 가리키는 커밋, 현재·직전 커밋의 guide.txt, 커밋 수를 확인해요. '
            'main에 직접 커밋, 병합 누락, 병합 전 search 시작, search까지 main에 합치기는 실패해요.',
    unit=dict(id='unt_c094c36e-651f-4558-b2cd-d57d5cdb1ff6', title='마지막 도전',
              objectives=['두 기능의 브랜치 흐름을 스스로 이어 가요.'],
              premise='main에 기본 안내 한 줄만 기록된 새 저장소예요. 앞 단계와 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='두 기능을 브랜치로 차례로 개발하세요',
              objectives=['병합된 main에서 다음 작업을 시작하는 흐름을 스스로 만들어요.'],
              core_flow='시작은 기본 안내 한 커밋. 학생은 memo 브랜치 커밋, main 병합, search 브랜치 커밋을 스스로 고른 명령으로 한다. '
                        '채점은 브랜치 위치와 기록 내용이다. 해설은 병합 전 브랜치 시작의 결과를 주의로 짚는다.'),
    task=dict(id=STEP, title='두 기능을 브랜치로 차례로 개발하세요', goal=GOAL, language='git', starter_code='', solution='', tests=[], required=True,
              git_terminal=dict(initial_history='empty', files={'guide.txt': BASE},
                                setup=[dict(kind='git', args=['add', 'guide.txt']), dict(kind='git', args=['commit', '-m', '기본 안내'])],
                                state_goal=STATE),
              narration=NARRATION),
    review={
        '조심하세요. 병합하기 전에 search를 만들면 메모 안내가 없는 옛 main에서 출발해요.':
            '이 도전에서 순서를 바꾸면 생기는 실제 결과(옛 main에서 출발)를 말해요. 채점의 직전 커밋 내용과 main 위치가 잡아요.',
    },
)

CASES = dict(
    accept=[(['git switch -c memo', 'echo "메모: 메모를 남겨요" >> guide.txt', 'git commit -am "메모 기능"', 'git switch main', 'git merge memo',
              'git switch -c search', 'echo "검색: 메모를 찾아요" >> guide.txt', 'git commit -am "검색 기능"'], 'teacher commands'),
            (['git branch memo', 'git checkout memo', 'echo "메모: 메모를 남겨요" >> guide.txt', 'git add guide.txt', 'git commit -m memo',
              'git checkout main', 'git merge memo', 'git checkout -b search', 'echo "검색: 메모를 찾아요" >> guide.txt', 'git add .', 'git commit -m search'],
             'branch plus checkout and other messages')],
    reject=[(['echo "메모: 메모를 남겨요" >> guide.txt', 'git commit -am memo', 'git switch -c search',
              'echo "검색: 메모를 찾아요" >> guide.txt', 'git commit -am search'], 'memo work committed on main without a memo branch'),
            (['git switch -c memo', 'echo "메모: 메모를 남겨요" >> guide.txt', 'git commit -am memo', 'git switch -c search',
              'echo "검색: 메모를 찾아요" >> guide.txt', 'git commit -am search'], 'memo never merged into main'),
            (['git switch -c search', 'git switch main', 'git switch -c memo', 'echo "메모: 메모를 남겨요" >> guide.txt', 'git commit -am memo',
              'git switch main', 'git merge memo', 'git switch search', 'echo "검색: 메모를 찾아요" >> guide.txt', 'git commit -am search'], 'search started before the merge'),
            (['git switch -c memo', 'echo "메모: 메모를 남겨요" >> guide.txt', 'git commit -am memo', 'git switch main', 'git merge memo',
              'git switch -c search', 'echo "검색: 메모를 찾아요" >> guide.txt', 'git commit -am search', 'git switch main', 'git merge search', 'git switch search'],
             'search already merged into main')],
)
