"""git-branch-advanced final challenge: a merge with one automatic change and one real conflict, resolved by both intents."""
from _common import todo

STEP = 'stp_6b96f92f-1312-42a2-8b23-7f4eb545dae5'
T = '#git-demo-terminal'
REST = '\n\n항목: 계정\n항목: 저장\n항목: 기록\n\n'
BASE = '안내: 기본 안내' + REST + '문의: 기본 창구\n'
MAIN = '안내: 먼저 로그인해요' + REST + '문의: 기본 창구\n'
FEATURE = '안내: 메모를 남겨요' + REST + '문의: 상담 창구\n'
AGREED = '안내: 먼저 로그인하고 메모를 남겨요' + REST + '문의: 상담 창구\n'

AGREED_PRINTF = "printf '안내: 먼저 로그인하고 메모를 남겨요\\n\\n항목: 계정\\n항목: 저장\\n항목: 기록\\n\\n문의: 상담 창구\\n' > guide.txt"


def git(args, say):
    return dict(action='git_command', args=args, say=say, target=T)


def run(command, say, **extra):
    return dict(action='bash_command', command=command, say=say, target=T, **extra)


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. main과 feature가 갈라졌어요. 첫 줄은 둘 다 고쳤고, 문의 줄은 feature만 고쳤어요.',
        'text:첫 줄은 두 브랜치가 다르게 고쳤고, 문의 줄은 feature만 고쳤어요.'),
    git(['branch'], '지금 서 있는 브랜치를 확인해요.'),
    say('별표가 main에 있어요. 여기서 feature를 합쳐요.'),
    run('git merge feature', 'feature를 main에 합쳐요.', expected_exit=1),
    say('Auto-merging guide.txt 뒤에 CONFLICT가 나와요. 첫 줄은 Git이 고르지 못했어요.'),
    run('cat guide.txt', '충돌한 파일을 읽어요.'),
    say('첫 줄에만 충돌 표시가 있어요. 문의 줄은 이미 상담 창구로 합쳐져 있어요.'),
    run(AGREED_PRINTF, 'printf로 합의한 전체 내용을 다시 써요. 역슬래시 n 자리에서 줄이 바뀌어요.'),
    say('출력은 없어요. 충돌 표시가 사라지고 첫 줄과 문의 줄이 합의한 내용이 됐어요.'),
    run('cat guide.txt', '고친 파일을 다시 읽어요.'),
    say('첫 줄은 먼저 로그인하고 메모를 남겨요, 문의 줄은 상담 창구예요. 나머지 줄은 그대로예요.'),
    git(['add', 'guide.txt'], '해결한 파일을 준비 영역에 담아요.'),
    say('충돌이 해결된 것으로 표시돼요.'),
    git(['commit', '-m', '안내 병합'], '병합 커밋으로 마쳐요.'),
    say('부모가 둘인 병합 커밋이 생겼어요.'),
    git(['log', '--oneline', '--graph', '-4'], '그래프로 기록을 봐요.'),
    say('두 선이 병합 커밋에서 만나요.'),
    say('조심하세요. 파일 전체를 한쪽 내용으로 다시 쓰면 자동으로 합쳐진 문의 줄 변경까지 사라져요.', T),
]

GOAL = ('자, 마지막 도전이에요. guide.txt를 main과 feature가 각각 고쳤어요. 첫 줄은 두 브랜치가 다르게 고쳤고, 문의 줄은 feature만 고쳤어요.\n\n'
        '- main: `안내: 먼저 로그인해요`\n- feature: `안내: 메모를 남겨요`, `문의: 상담 창구`\n\n'
        'main에서 feature를 합쳐요. 첫 줄은 두 의도를 함께 담은 `안내: 먼저 로그인하고 메모를 남겨요`로 정해요. '
        'feature가 바꾼 문의 줄과 나머지 줄은 그대로 남아야 해요. 파일 편집 방법은 자유예요.\n\n'
        + todo('main에서 feature를 병합하세요.',
               '충돌한 첫 줄을 합의한 문구로 고치세요.',
               '해결한 파일을 준비하고 커밋해 병합을 마치세요.',
               'main에 서 있는 채로 제출하세요.'))

STATE = dict(current_branch='main', merge_in_progress=False, unmerged_paths=[], references={'refs/heads/feature': 'HEAD^2'},
             parent_count=2, commit_count=4, clean=True, head_files={'guide.txt': AGREED}, parent_files={'guide.txt': MAIN},
             working_files={'guide.txt': AGREED})

SPEC = dict(
    key='git-branch-advanced', course='java', revision='git-branch-advanced-10',
    reason='자동 병합과 실제 충돌이 한 파일에 섞인 병합을 두 의도를 살려 해결하고 준비·커밋으로 마치는 마지막 도전이에요.',
    grading='실제 Git의 병합 커밋(부모 둘·둘째 부모 feature), 병합 종료, 미병합 경로 없음, 병합 커밋과 첫 부모의 guide.txt를 확인해요. '
            '충돌 표시 남김, 한쪽 문구만 선택, 자동 병합된 문의 줄 잃기, feature에서 병합은 실패해요.',
    unit=dict(id='unt_22181bb6-078f-4a12-a3b6-df4dd1f201bc', title='마지막 도전',
              objectives=['자동 병합과 충돌이 섞인 병합을 스스로 마쳐요.'],
              premise='main과 feature가 갈라진 새 저장소예요. 앞 단계와 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='두 의도를 살려 갈라진 안내를 병합하세요',
              objectives=['충돌 구간만 합의 문구로 고치고 자동 병합된 변경은 지켜요.'],
              core_flow='시작: 기본 안내에서 main(첫 줄)과 feature(첫 줄·문의 줄)가 갈라짐. 학생은 merge, 충돌 해결, add, commit을 한다. '
                        '채점: 병합 커밋 구조와 내용. 해설은 printf로 합의한 전체 내용을 쓰고 cat으로 문의 줄이 남았는지 확인한다.'),
    task=dict(id=STEP, title='두 의도를 살려 갈라진 안내를 병합하세요', goal=GOAL, language='git', starter_code='', solution='', tests=[], required=True,
              git_terminal=dict(initial_history='empty', files={'guide.txt': BASE},
                                setup=[dict(kind='git', args=['add', '--', 'guide.txt']), dict(kind='git', args=['commit', '-m', '기본 안내']),
                                       dict(kind='git', args=['branch', 'feature']),
                                       dict(kind='file', path='guide.txt', content=MAIN),
                                       dict(kind='git', args=['add', '--', 'guide.txt']), dict(kind='git', args=['commit', '-m', '접속 안내']),
                                       dict(kind='git', args=['switch', 'feature']),
                                       dict(kind='file', path='guide.txt', content=FEATURE),
                                       dict(kind='git', args=['add', '--', 'guide.txt']), dict(kind='git', args=['commit', '-m', '메모와 문의 안내']),
                                       dict(kind='git', args=['switch', 'main'])],
                                state_goal=STATE),
              narration=NARRATION),
    review={
        '조심하세요. 파일 전체를 한쪽 내용으로 다시 쓰면 자동으로 합쳐진 문의 줄 변경까지 사라져요.':
            '이 도전에서 충돌 해결을 파일 덮어쓰기로 하면 생기는 실제 결과를 말해요. 채점의 병합 커밋 내용이 잡아요.',
    },
)

CASES = dict(
    accept=[(['git merge feature', AGREED_PRINTF, 'git add guide.txt', 'git commit -m "안내 병합"'], 'teacher commands'),
            (['git merge feature', 'sed -i "/^<<<<<<< /,/^>>>>>>> /c\\\\안내: 먼저 로그인하고 메모를 남겨요" guide.txt', 'git add .',
              'git commit --no-edit'], 'only the conflict block replaced, default message')],
    reject=[(['git merge feature', 'git add guide.txt', 'git commit --no-edit'], 'conflict markers committed'),
            (['git merge feature', 'git checkout --ours guide.txt', 'git add guide.txt', 'git commit --no-edit'], "main's side only: loses the contact change"),
            (['git merge feature', "printf '안내: 먼저 로그인하고 메모를 남겨요\\n\\n항목: 계정\\n항목: 저장\\n항목: 기록\\n\\n문의: 기본 창구\\n' > guide.txt",
              'git add guide.txt', 'git commit --no-edit'], 'agreed first line but the contact change lost'),
            (['git merge feature', 'sed -i "/^<<<<<<< /,/^>>>>>>> /c\\\\안내: 먼저 로그인하고 메모를 남겨요" guide.txt'], 'resolved but merge not finished'),
            (['git switch feature', 'git merge main'], 'merging from the feature side')],
)
