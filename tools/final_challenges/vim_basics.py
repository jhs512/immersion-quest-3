"""vim-basics final challenge: fix a shopping list with movement, line edits, search, save and quit."""
from _common import todo

STEP = 'stp_b4149a72-f735-446d-b970-05187441ef62'
T = '#git-demo-terminal'
START_LINES = ['장보기 목록', '우유 2개', '라면 5개', '계란 10개']
FINAL = ['장보기 목록', '우유 1개', '계란 10개', '사과 3개']
SNAPSHOT = dict(lines=START_LINES, file_lines=START_LINES, mode='n', line=1, column=1, modified=False, search='')


def keys(value, say, wait_prompt=False):
    return dict(action='vim_keys', keys=value, wait_prompt=wait_prompt, say=say, target=T)


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. 장보기 목록에서 틀린 줄은 고치고, 필요 없는 줄은 지우고, 빠진 줄은 더한 뒤 저장하고 끝내요.',
        'text:장보기 목록을 고쳐 저장하고 Vim을 끝내요.'),
    dict(action='vim_wait', target=T),
    keys('j', 'j로 둘째 줄 우유 2개로 내려가요.'),
    say('커서가 우유 2개 줄에 있어요.'),
    keys('cc', 'cc로 이 줄을 비우고 입력 모드가 돼요.'),
    say('줄이 비고 INSERT가 보여요.'),
    keys('우유 1개', '우유 1개를 입력해요.'),
    say('둘째 줄이 우유 1개가 됐어요.'),
    keys('\x1b', 'Esc로 일반 모드로 돌아와요.'),
    say('INSERT 표시가 사라졌어요.'),
    keys('/라면\r', '지울 줄은 /라면으로 찾아가요.'),
    say('커서가 라면 5개 줄로 옮겨 갔어요.'),
    keys('dd', 'dd로 그 줄을 지워요.'),
    say('라면 줄이 사라지고 계란 10개가 셋째 줄이 됐어요.'),
    keys('G', 'G로 계란 10개가 있는 마지막 줄로 가요.'),
    say('계란 10개 줄이에요.'),
    keys('o', 'o로 아래에 새 줄을 열어요.'),
    say('새 줄이 생기고 입력 모드예요.'),
    keys('사과 3개', '사과 3개를 입력해요.'),
    say('마지막 줄에 사과 3개가 들어갔어요.'),
    keys('\x1b', 'Esc로 나와요.'),
    say('일반 모드예요. 화면의 네 줄이 목표와 같아요.'),
    say('조심하세요. 여기서 :q!로 나가면 고친 네 줄이 파일에 하나도 남지 않아요.', 'text:저장하지 않고 끝내면 실패예요.'),
    keys(':wq\r', ':wq로 저장하고 끝내요.', wait_prompt=True),
    say('파일에 저장한 뒤 Vim이 끝났어요.'),
    dict(action='vim_wait', passed=True, say='확인 항목을 봐요.', target='.vim-live-panel'),
    say('목록 변경, 저장, 종료가 모두 확인됐어요.', '.vim-live-panel'),
]

GOAL = ('자, 마지막 도전이에요. 장보기 목록을 고쳐 저장하고 Vim을 끝내요. 지금 memo.txt는 이래요.\n\n'
        '```\n' + '\n'.join(START_LINES) + '\n```\n\n'
        '고친 뒤에는 이렇게 네 줄이어야 해요. 우유는 1개로 고치고, 라면 줄은 지우고, 맨 끝에 사과 3개를 더해요.\n\n'
        '```\n' + '\n'.join(FINAL) + '\n```\n\n'
        '어떤 키로 이동하고 고칠지는 직접 골라요. 저장하지 않고 끝내면 실패예요.\n\n'
        + todo('우유 줄을 `우유 1개`로 고치세요.',
               '라면 줄을 지우세요.',
               '맨 끝에 `사과 3개` 줄을 더하세요.',
               '저장하고 Vim을 끝내세요.',
               '실시간 확인 항목이 모두 완료되면 제출 버튼을 누르세요.'))

SPEC = dict(
    key='vim-basics', course='java', revision='vim-basics-5',
    reason='이동·검색·줄 바꾸기·줄 삭제·새 줄·저장 종료를 목표 파일만 보고 스스로 골라 조합하는 마지막 도전이에요.',
    grading='실제 Vim의 버퍼 상태, 저장 기록, 저장 뒤 종료 기록과 저장된 memo.txt를 확인해요. :q!로 버린 편집, 저장만 하고 열어 둔 상태, 다른 줄 삭제는 실패해요.',
    unit=dict(id='unt_338c421f-a369-4849-bd4b-af88f4882808', title='마지막 도전',
              objectives=['배운 키를 골라 파일 하나를 목표대로 고치고 저장해 끝내요.'],
              premise='새 장보기 목록 파일이에요. 앞 단계의 메모와 상관없이 이 단계에서 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='장보기 목록을 고쳐 저장하고 끝내세요',
              objectives=['이동·편집·저장·종료 키를 스스로 골라 목표 파일을 만들어요.'],
              core_flow='시작 파일 네 줄. 학생은 j·/검색·cc·dd·G·o·Esc·:wq 등을 골라 쓴다. 채점은 키 철자가 아니라 버퍼 네 줄, 저장 기록, '
                        '저장 뒤 종료, 저장 파일이다. 해설은 :q!의 결과를 주의로 짚는다.'),
    task=dict(id=STEP, title='장보기 목록을 고쳐 저장하고 끝내세요', goal=GOAL, language='git', starter_code='',
              solution='j\ncc 우유 1개 Esc\n/라면 Enter\ndd\nG\no 사과 3개 Esc\n:wq Enter',
              tests=[], required=True,
              git_terminal=dict(initial_history='uninitialized', vim=dict(
                  step_id=STEP,
                  checks=[dict(label='목록 네 줄을 목표대로 고쳤어요', state=dict(lines=FINAL)),
                          dict(label='고친 목록을 파일에 저장했어요', state=dict(event='write', lines=FINAL, modified=False)),
                          dict(label='저장한 뒤 Vim을 끝냈어요', state=dict(event='exit', exited=True, modified=False))],
                  demo=SNAPSHOT, start=SNAPSHOT, final_file=FINAL)),
              narration=NARRATION),
    review={
        '조심하세요. 여기서 :q!로 나가면 고친 네 줄이 파일에 하나도 남지 않아요.':
            '13번에서 익힌 :q!의 실제 결과를 이 도전의 목표 파일로 다시 말해요. 채점의 저장 기록 항목이 잡아요.',
    },
)

# Key sequences typed into the learner's real Vim (tests/final_terminal_challenges.rs).
CASES = dict(
    accept=[(['j', 'cc', '우유 1개', '\x1b', '/라면\r', 'dd', 'G', 'o', '사과 3개', '\x1b', ':wq\r'], 'teacher keys'),
            (['j', 'j', 'dd', 'gg', 'j', 'cc', '우유 1개', '\x1b', 'G', 'o', '사과 3개', '\x1b', ':w\r', ':q\r'], 'other movement, then :w and :q')],
    reject=[(['j', 'cc', '우유 1개', '\x1b', '/라면\r', 'dd', 'G', 'o', '사과 3개', '\x1b', ':q!\r'], 'quitting without saving'),
            (['j', 'cc', '우유 1개', '\x1b', '/라면\r', 'dd', 'G', 'o', '사과 3개', '\x1b', ':w\r'], 'saved but still open'),
            (['j', 'cc', '우유 1개', '\x1b', 'G', 'dd', 'o', '사과 3개', '\x1b', ':wq\r'], 'deleting the wrong line')],
)
