"""bash-basics final challenge: tidy a messy practice folder with copy, move, write and recursive delete."""
from _common import todo

STEP = 'stp_04bd4e0f-f236-4bc2-9b1d-5d6c13f74eac'
T = '#git-demo-terminal'
START = dict(files={'draft.txt': '회의 초안\n', 'notes/todo.txt': '할 일 목록\n', 'tmp/cache.txt': '임시 기록\n'},
             directories=['notes', 'tmp'], cwd='')
GOAL_STATE = dict(files={'backup/todo.txt': '할 일 목록\n', 'notes/todo.txt': '할 일 목록\n',
                         'notes/draft.txt': '회의 초안\n', 'notes/done.txt': '정리 끝\n'},
                  directories=['backup', 'notes'], cwd='notes')
COMMANDS = ['ls']


def run(command, say, fails=False):
    action = dict(action='bash_command', command=command, say=say, target=T)
    if fails:
        action['fails'] = True
    return action


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. 어지러운 연습 폴더를 정리해요. 옮길 것과 복사할 것과 지울 것을 먼저 구별해요.', 'text:어지러운 연습 폴더를 정리해요.'),
    run('ls', '지금 폴더부터 봐요.'),
    say('draft.txt, notes, tmp가 있어요. backup은 아직 없어요.'),
    run('mkdir backup', '사본을 둘 backup 폴더를 만들어요.'),
    say('출력 없이 폴더가 생겼어요.'),
    run('cp notes/todo.txt backup/', '할 일 목록은 원본을 남기고 cp로 사본만 둬요.'),
    say('출력이 없어요. 원본 notes/todo.txt도 그대로예요.'),
    run('mv draft.txt notes/', '초안은 mv로 notes에 옮겨요. 바깥에는 남지 않아요.'),
    say('출력이 없어요. 초안이 notes 안으로 들어갔어요.'),
    run('rmdir tmp', 'tmp를 rmdir로 지워 볼게요.', fails=True),
    say('Directory not empty가 나와요. 안에 cache.txt가 있어서 빈 폴더용 명령으로는 안 지워져요.'),
    run('rm -r tmp', '그래서 rm -r로 폴더와 안의 내용을 함께 지워요.'),
    say('출력 없이 tmp가 사라졌어요.'),
    run('cd notes', 'notes 안으로 들어가요.'),
    say('프롬프트는 그대로지만 지금 위치는 notes예요.'),
    run('echo "정리 끝" > done.txt', '여기서 완료 메모를 done.txt에 써요.'),
    say('출력이 없어요. 지금 위치인 notes에 done.txt가 생겼어요.'),
    run('ls', '마지막으로 notes 안을 확인해요.'),
    say('done.txt, draft.txt, todo.txt 세 파일이 보여요.'),
    say('조심하세요. cd 하기 전에 echo를 쓰면 done.txt가 바깥 폴더에 생겨요. 쓰기 전에 위치를 먼저 확인해요.',
        'text:완료 메모는 notes 안에 있어야 해요.'),
]

GOAL = ('자, 마지막 도전이에요. 어지러운 연습 폴더를 정리해요. 지금 폴더에는 `draft.txt`, `notes/todo.txt`, '
        '그리고 안에 파일이 든 `tmp` 폴더가 있어요.\n\n'
        '정리가 끝나면 이렇게 돼야 해요. `backup/todo.txt`는 할 일 목록의 사본이고 원본 `notes/todo.txt`도 남아 있어요. '
        '초안은 `notes/draft.txt`로 옮겨져 바깥에는 없어요. `tmp` 폴더는 안의 파일과 함께 사라져요. '
        '`notes/done.txt`에는 `정리 끝` 한 줄이 들어 있어요. 완료 메모는 notes 안에 있어야 해요. '
        '마지막 위치는 notes이고, 그 안에서 `ls`로 세 파일을 확인해요.\n\n'
        + todo('지금 폴더의 파일과 폴더를 확인하세요.',
               'backup 폴더를 만들고 할 일 목록의 사본을 두세요.',
               '초안을 notes 폴더로 옮기세요.',
               'tmp 폴더를 안의 파일과 함께 지우세요.',
               'notes 폴더로 이동해 `정리 끝`을 done.txt에 쓰세요.',
               '`ls`로 notes 안의 세 파일을 확인하세요.',
               '확인한 뒤 제출 버튼을 누르세요.'))

SPEC = dict(
    key='bash-basics', course='java', revision='bash-basics-7',
    reason='위치·경로, 폴더 만들기, 복사와 이동의 구별, 내용 있는 폴더 삭제, 파일 쓰기를 명령 없이 목표 상태만 보고 스스로 조합하는 마지막 도전이에요.',
    grading='실제 Bash에서 최종 파일 내용·폴더 목록·현재 위치와 notes 안의 ls 실행을 확인해요. 사본 대신 이동, rmdir 실패로 남은 tmp, 바깥에 쓴 메모, cp로 남긴 초안은 실패해요.',
    unit=dict(id='unt_a2ba0354-d57d-4481-b13b-732fc9ba5cc9', title='마지막 도전',
              objectives=['배운 명령을 골라 어지러운 폴더를 목표 상태로 정리해요.'],
              premise='새 연습 폴더예요. 앞 단계의 파일과 상관없이 이 단계의 시작 상태에서 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='어지러운 연습 폴더를 목표대로 정리하세요',
              objectives=['복사·이동·삭제와 위치를 구별해 목표 상태를 스스로 만들어요.'],
              commands=COMMANDS,
              core_flow='시작: draft.txt, notes/todo.txt, 내용 있는 tmp. 학생은 mkdir·cp·mv·rm -r·cd·echo >·ls를 골라 쓴다. '
                        '채점은 명령 철자가 아니라 최종 파일·폴더·위치와 notes 안의 ls다. 해설은 rmdir 실패를 실제로 보여 준다.'),
    task=dict(id=STEP, title='어지러운 연습 폴더를 목표대로 정리하세요', goal=GOAL, language='git',
              starter_code='', solution='\n'.join(['mkdir backup', 'cp notes/todo.txt backup/', 'mv draft.txt notes/', 'rm -r tmp', 'cd notes', 'echo "정리 끝" > done.txt', 'ls']),
              tests=[], required=True,
              git_terminal=dict(initial_history='uninitialized',
                                shell=dict(step_id=STEP, goal=GOAL_STATE, demo=START, start=START, commands=COMMANDS, requires_vim=False)),
              narration=NARRATION),
    review={
        '조심하세요. cd 하기 전에 echo를 쓰면 done.txt가 바깥 폴더에 생겨요. 쓰기 전에 위치를 먼저 확인해요.':
            '이 도전에서 가장 흔한 실수(위치를 바꾸기 전에 쓰기)를 실제 결과(바깥에 생긴 파일)로 말해요. 채점의 파일 목록이 잡아요.',
    },
)

# Real-runtime cases for tests/final_terminal_challenges.rs: command lists typed into the learner terminal.
CASES = dict(
    accept=[
        (['mkdir backup', 'cp notes/todo.txt backup/', 'mv draft.txt notes/', 'rm -r tmp', 'cd notes', 'echo "정리 끝" > done.txt', 'ls'], 'teacher order'),
        (['cd notes', 'mkdir ../backup', 'cp todo.txt ../backup/todo.txt', 'mv ../draft.txt .', 'rm -rf ../tmp', 'echo 정리 끝 > done.txt', 'ls'], 'relative paths from inside notes'),
    ],
    reject=[
        (['mkdir backup', 'mv notes/todo.txt backup/', 'mv draft.txt notes/', 'rm -r tmp', 'cd notes', 'echo "정리 끝" > done.txt', 'ls'], 'moving the list loses the original'),
        (['mkdir backup', 'cp notes/todo.txt backup/', 'mv draft.txt notes/', 'rmdir tmp', 'cd notes', 'echo "정리 끝" > done.txt', 'ls'], 'rmdir leaves tmp'),
        (['mkdir backup', 'cp notes/todo.txt backup/', 'mv draft.txt notes/', 'rm -r tmp', 'echo "정리 끝" > done.txt', 'cd notes', 'ls'], 'memo written outside notes'),
        (['mkdir backup', 'cp notes/todo.txt backup/', 'cp draft.txt notes/', 'rm -r tmp', 'cd notes', 'echo "정리 끝" > done.txt', 'ls'], 'copying the draft leaves it outside'),
        (['mkdir backup', 'cp notes/todo.txt backup/', 'mv draft.txt notes/', 'rm -r tmp', 'echo "정리 끝" > notes/done.txt', 'ls'], 'ending outside notes'),
    ],
)
