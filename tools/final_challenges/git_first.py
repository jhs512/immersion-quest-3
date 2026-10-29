"""git-first final challenge: from an empty folder, record two versions and keep a third line unrecorded."""
from _common import todo

STEP = 'stp_b752762e-e893-4042-9135-c43787c64719'
T = '#git-demo-terminal'
FIRST, SECOND, THIRD = '장보기\n', '장보기\n빨래\n', '장보기\n빨래\n청소\n'


def git(args, say):
    return dict(action='git_command', args=args, say=say, target=T)


def run(command, say):
    return dict(action='bash_command', command=command, say=say, target=T)


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. 빈 폴더에서 할 일 목록을 두 번 기록하고, 셋째 줄은 파일에만 남겨요.',
        'text:셋째 줄 청소는 파일에만 있고 기록에도 준비 영역에도 없어야 해요.'),
    git(['init'], 'git init으로 저장소를 만들어요.'),
    say('.git 폴더가 생겼어요. 아직 커밋은 없어요.'),
    run('echo "장보기" > todo.txt', '첫 줄을 todo.txt에 써요.'),
    say('출력 없이 파일이 생겼어요.'),
    git(['add', 'todo.txt'], '지금 내용을 준비 영역에 담아요.'),
    say('출력은 없어요. 장보기 한 줄이 준비됐어요.'),
    git(['commit', '-m', '첫 할 일'], '첫 커밋으로 남겨요.'),
    say('root-commit이라는 표시와 함께 첫 기록이 생겼어요.'),
    run('echo "빨래" >> todo.txt', '둘째 줄을 덧붙여요.'),
    say('파일은 두 줄이 됐어요. 기록은 아직 한 줄이에요.'),
    git(['add', 'todo.txt'], '두 줄을 다시 담아요.'),
    say('준비 영역도 두 줄이 됐어요.'),
    git(['commit', '-m', '둘째 할 일'], '둘째 커밋으로 남겨요.'),
    say('두 번째 기록이 생겼어요.'),
    run('echo "청소" >> todo.txt', '셋째 줄은 파일에만 덧붙여요.'),
    say('파일은 세 줄이에요.'),
    git(['status'], 'git status로 확인해요.'),
    say('modified: todo.txt가 Changes not staged for commit 아래에 있어요. 셋째 줄은 아직 준비하지 않았어요.'),
    say('조심하세요. 습관처럼 여기서 다시 git add를 하면 청소 줄까지 준비 영역에 올라가요.', T),
]

GOAL = ('자, 마지막 도전이에요. 빈 폴더에서 할 일 목록 todo.txt를 Git으로 관리해요. 저장소도 파일도 아직 없어요.\n\n'
        '끝났을 때 이래야 해요. 첫 커밋의 todo.txt는 `장보기` 한 줄이에요. 둘째 커밋은 `장보기`, `빨래` 두 줄이에요. '
        '그 뒤 파일에 `청소`를 셋째 줄로 덧붙여요. 셋째 줄 청소는 파일에만 있고 기록에도 준비 영역에도 없어야 해요. '
        '커밋 설명은 자유예요.\n\n'
        + todo('이 폴더에 저장소를 만드세요.',
               '`장보기` 한 줄로 todo.txt를 만들어 첫 커밋으로 남기세요.',
               '`빨래`를 덧붙여 두 줄을 둘째 커밋으로 남기세요.',
               '`청소`를 덧붙이고 기록하지 마세요.',
               '`git status`로 세 곳의 상태를 확인한 뒤 제출하세요.'))

STATE = dict(head_exists=True, commit_count=2, clean=False, head_files={'todo.txt': SECOND}, parent_files={'todo.txt': FIRST},
             index={'todo.txt': SECOND}, working_files={'todo.txt': THIRD})

SPEC = dict(
    key='git-first', course='java', revision='git-first-9',
    reason='저장소 만들기부터 작업 파일·준비 영역·커밋 세 곳을 스스로 다뤄 두 기록과 기록하지 않은 변경을 함께 만드는 마지막 도전이에요.',
    grading='실제 Git 저장소의 커밋 수, 현재·직전 커밋의 todo.txt, 준비 영역, 작업 파일을 확인해요. 셋째 줄 커밋·준비, 한 커밋에 몰기, 저장소 없음은 실패해요.',
    unit=dict(id='unt_ebce52c8-9071-44dc-8ecb-b4a9d1f10e23', title='마지막 도전',
              objectives=['빈 폴더에서 세 곳의 상태를 스스로 만들어요.'],
              premise='새 빈 폴더예요. 앞 단계의 메모 저장소와 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='빈 폴더에서 할 일 목록을 두 번 기록하세요',
              objectives=['작업 파일·준비 영역·커밋을 구별해 목표 상태를 스스로 만들어요.'],
              core_flow='시작은 저장소 없는 빈 폴더. 학생은 init, echo, add, commit을 골라 두 커밋을 만들고 셋째 줄은 파일에만 둔다. '
                        '채점은 명령 철자가 아니라 커밋 수와 세 곳의 내용이다. 해설은 status로 준비하지 않은 변경을 보여 준다.'),
    task=dict(id=STEP, title='빈 폴더에서 할 일 목록을 두 번 기록하세요', goal=GOAL, language='git', starter_code='',
              solution='git init\necho "장보기" > todo.txt\ngit add todo.txt\ngit commit -m "첫 할 일"\necho "빨래" >> todo.txt\ngit add todo.txt\ngit commit -m "둘째 할 일"\necho "청소" >> todo.txt\ngit status',
              tests=[], required=True,
              git_terminal=dict(initial_history='uninitialized', files={}, setup=[], state_goal=STATE, commands=[['status']]),
              narration=NARRATION),
    review={
        '조심하세요. 습관처럼 여기서 다시 git add를 하면 청소 줄까지 준비 영역에 올라가요.':
            '이 도전의 마지막 상태를 깨는 가장 흔한 행동(add 반복)을 실제 결과로 말해요. 채점의 준비 영역 항목이 잡아요.',
    },
)

CASES = dict(
    accept=[(['git init', 'echo "장보기" > todo.txt', 'git add todo.txt', 'git commit -m "첫 할 일"', 'echo "빨래" >> todo.txt',
              'git add todo.txt', 'git commit -m "둘째 할 일"', 'echo "청소" >> todo.txt', 'git status'], 'teacher commands'),
            (['git init', 'echo 장보기 > todo.txt', 'git add .', 'git commit -m one', 'echo 빨래 >> todo.txt', 'git commit -am two',
              'echo 청소 >> todo.txt', 'git status -s'], 'add . and commit -a with other messages')],
    reject=[(['git init', 'echo "장보기" > todo.txt', 'git add todo.txt', 'git commit -m a', 'echo "빨래" >> todo.txt', 'git commit -am b',
              'echo "청소" >> todo.txt', 'git commit -am c', 'git status'], 'third line committed'),
            (['git init', 'echo "장보기" > todo.txt', 'git add todo.txt', 'git commit -m a', 'echo "빨래" >> todo.txt', 'git commit -am b',
              'echo "청소" >> todo.txt', 'git add todo.txt', 'git status'], 'third line staged'),
            (['git init', 'echo "장보기" > todo.txt', 'echo "빨래" >> todo.txt', 'git add todo.txt', 'git commit -m both',
              'echo "청소" >> todo.txt', 'git status'], 'both lines in one commit'),
            (['echo "장보기" > todo.txt', 'echo "빨래" >> todo.txt', 'echo "청소" >> todo.txt'], 'no repository')],
)
