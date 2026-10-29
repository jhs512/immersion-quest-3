"""git-remote final challenge: a rejected push, fetch, conflicting merge, agreed resolution and a successful share."""
from _common import todo

STEP = 'stp_94d0da62-e0db-47a2-aaef-8ad0cf722e8a'
T = '#git-demo-terminal'
BASE = '운영: 오전 9시부터 오후 6시\n문의: 상담 창구\n'
PEER = '운영: 오전 10시부터 오후 6시\n문의: 상담 창구\n'
MINE = '운영: 오전 9시부터 오후 7시\n문의: 상담 창구\n'
AGREED = '운영: 오전 10시부터 오후 7시\n문의: 상담 창구\n'


def git(args, say):
    return dict(action='git_command', args=args, say=say, target=T)


def run(command, say):
    return dict(action='bash_command', command=command, say=say, target=T)


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. 내 운영 시간 커밋을 공유해야 하는데, 동료가 같은 줄을 고쳐 먼저 보냈어요.',
        'text:동료는 여는 시간을 오전 10시로 바꿔 먼저 보냈어요.'),
    dict(action='bash_command', command='git push origin main', expected_exit=1, say='먼저 그대로 보내 볼게요.', target=T),
    say('rejected가 나와요. 원격에 내가 받지 않은 커밋이 있어서 거절됐어요.'),
    git(['fetch', 'origin'], 'fetch로 동료의 커밋을 받아요.'),
    say('origin/main이 동료의 커밋으로 옮겨 갔어요. 내 main은 그대로예요.'),
    dict(action='bash_command', command='git merge origin/main', expected_exit=1, say='받은 기록을 내 main에 합쳐요.', target=T),
    say('CONFLICT가 나요. 같은 운영 줄을 둘이 다르게 고쳤어요.'),
    run('cat guide.txt', '충돌한 파일을 읽어요.'),
    say('충돌 표시 사이에 내 오후 7시와 동료의 오전 10시가 따로 보여요.'),
    run('echo "운영: 오전 10시부터 오후 7시" > guide.txt', '팀이 합의한 운영 줄로 파일을 다시 써요.'),
    say('첫 줄이 합의한 문구가 됐어요. 문의 줄은 아직 없어요.'),
    run('echo "문의: 상담 창구" >> guide.txt', '문의 줄도 다시 붙여요.'),
    say('충돌 표시 없이 두 줄이 됐어요.'),
    git(['add', 'guide.txt'], '해결한 파일을 준비 영역에 담아요.'),
    say('충돌이 해결된 것으로 표시돼요.'),
    git(['commit', '-m', '운영 시간 병합'], '병합 커밋으로 마쳐요.'),
    say('부모가 둘인 병합 커밋이 생겼어요.'),
    git(['push', 'origin', 'main'], '이제 다시 보내요.'),
    say('이번엔 main -> main으로 올라갔어요. 동료의 커밋 위에 내 병합이 쌓였거든요.'),
    say('조심하세요. 충돌 표시를 지우지 않고 add하면 그 표시까지 팀에 공유돼요.', T),
]

GOAL = ('자, 마지막 도전이에요. 팀 공유 저장소에 운영 시간 안내 guide.txt가 있어요. '
        '나는 닫는 시간을 오후 7시로 바꿔 커밋했지만 아직 보내지 않았어요. 동료는 여는 시간을 오전 10시로 바꿔 먼저 보냈어요.\n\n'
        '팀이 합의한 첫 줄은 `운영: 오전 10시부터 오후 7시`예요. 둘째 줄 `문의: 상담 창구`는 그대로 둬요. '
        '두 변경을 합쳐 이 내용을 팀 공유 저장소에 보내요. 동료의 커밋과 내 커밋은 둘 다 기록에 남아야 해요. '
        '보내는 명령은 이 수업처럼 `git push origin main`을 써요.\n\n'
        + todo('내 커밋을 보내 보고 거절된 이유를 확인하세요.',
               '동료의 커밋을 받아 내 main에 합치세요.',
               '충돌한 파일을 합의한 내용으로 고쳐 병합을 마치세요.',
               '`git push origin main`으로 공유하세요.',
               '공유한 뒤 제출하세요.'))

STATE = dict(current_branch='main', commit_count=4, parent_count=2, merge_in_progress=False, unmerged_paths=[], clean=True,
             head_files={'guide.txt': AGREED}, parent_files={'guide.txt': MINE}, working_files={'guide.txt': AGREED},
             remote_tracking_current=True)

SPEC = dict(
    key='git-remote', course='java', revision='git-remote-12',
    reason='push 거절 이유 읽기, fetch, 원격 기록 병합, 충돌을 합의 문구로 해결, 다시 push까지 공유 흐름 전체를 스스로 잇는 마지막 도전이에요.',
    grading='실제 Git에서 병합 커밋(부모 둘)의 guide.txt, 첫 부모가 내 커밋인지, 커밋 수, 병합 종료, 원격 추적 기록이 실제 원격과 같은지, push origin main 성공을 확인해요. '
            '충돌 표시 남김, 한쪽 변경만 남김, 공유 안 함, 강제 push는 실패해요.',
    unit=dict(id='unt_dbfb371d-eedf-440d-914d-228fcdacba5b', title='마지막 도전',
              objectives=['거절·받기·충돌 해결·공유를 스스로 이어요.'],
              premise='내 커밋 하나를 아직 보내지 않았고 동료가 같은 줄을 먼저 보낸 새 저장소예요. 앞 단계와 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='동료의 변경과 합쳐 내 운영 시간 커밋을 공유하세요',
              objectives=['거절된 push를 받기·병합·충돌 해결로 풀어 공유해요.'],
              core_flow='시작: 공통 커밋 위에 내 커밋(오후 7시)과 원격의 동료 커밋(오전 10시). 학생은 push 거절을 보고 fetch·merge(또는 pull origin main), '
                        '충돌 해결, add, commit, push origin main을 한다. 채점: 병합 커밋 내용·부모·원격 추적 일치·push 성공.'),
    task=dict(id=STEP, title='동료의 변경과 합쳐 내 운영 시간 커밋을 공유하세요', goal=GOAL, language='git', starter_code='', solution='', tests=[], required=True,
              git_terminal=dict(initial_history='empty', files={'guide.txt': BASE},
                                setup=[dict(kind='git', args=['add', 'guide.txt']), dict(kind='git', args=['commit', '-m', '운영 시간']),
                                       dict(kind='git', args=['push', 'origin', 'main']),
                                       dict(kind='remote_commit', files={'guide.txt': PEER}, message='여는 시간 변경'),
                                       dict(kind='file', path='guide.txt', content=MINE),
                                       dict(kind='git', args=['add', 'guide.txt']), dict(kind='git', args=['commit', '-m', '닫는 시간 변경'])],
                                state_goal=STATE, commands=[['push', 'origin', 'main']]),
              narration=NARRATION),
    review={
        '조심하세요. 충돌 표시를 지우지 않고 add하면 그 표시까지 팀에 공유돼요.':
            '14번에서 익힌 충돌 표시 정리를 공유 상황의 결과로 말해요. 채점의 병합 커밋 내용이 잡아요.',
    },
)

RESOLVE = ['echo "운영: 오전 10시부터 오후 7시" > guide.txt', 'echo "문의: 상담 창구" >> guide.txt']
CASES = dict(
    accept=[(['git push origin main', 'git fetch origin', 'git merge origin/main', *RESOLVE, 'git add guide.txt',
              'git commit -m "운영 시간 병합"', 'git push origin main'], 'teacher commands'),
            (['git fetch origin', 'git merge --no-edit origin/main', "printf '운영: 오전 10시부터 오후 7시\\n문의: 상담 창구\\n' > guide.txt", 'git add .',
              'git commit --no-edit', 'git push origin main'], 'no first push, printf resolution and the default message')],
    reject=[(['git fetch origin', 'git merge origin/main', 'git add guide.txt', 'git commit --no-edit', 'git push origin main'], 'conflict markers committed and shared'),
            (['git fetch origin', 'git merge origin/main', *RESOLVE, 'git add guide.txt', 'git commit -m merge'], 'resolved but never pushed'),
            (['git fetch origin', 'git merge origin/main', 'git checkout --theirs guide.txt', 'git add guide.txt', 'git commit --no-edit',
              'git push origin main'], "only the colleague's line kept"),
            (['git push -f origin main'], 'force push overwrites the colleague')],
)
