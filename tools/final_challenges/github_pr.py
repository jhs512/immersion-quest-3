"""github-pr final challenge: the whole GitHub Flow alone, from a new private repository to the merged main pulled back."""
from _common import todo

STEP = 'stp_2d42bbda-b942-4f8a-ba7a-beeceb7e8086'
T = '#git-demo-terminal'


def say(text, target=T):
    return dict(action='say', text=text, target=target)


# GitHub writes are never automated in an explanation: the narration only explains the flow.
NARRATION = [
    say('마지막 도전이에요. 새 실습 폴더에서 GitHub Flow 전체를 혼자 처음부터 끝까지 해요.',
        'text:새 폴더에서 GitHub Flow 전체를 처음부터 혼자 해요.'),
    say('먼저 MQ3_REPO 이름으로 본인 계정에 비공개 저장소를 만들고 origin으로 연결해요. 그다음 main을 보내야 PR이 비교할 기준이 생겨요.',
        'text:main은 직접 고치지 않고 feature 브랜치에서 바꿔요.'),
    say('변경은 feature 브랜치에서 커밋하고 feature도 GitHub에 보내요. PR은 feature를 main에 합치자는 요청이에요.'),
    say('PR을 병합하면 GitHub의 main만 바뀌어요. 내 main으로 받아야 끝나요.', 'text:병합한 기록을 내 컴퓨터의 main으로 받아 끝내요.'),
    say('조심하세요. main에서 바로 고쳐 push하면 PR이 없어서 검토 기록이 남지 않아요.', 'text:main은 직접 고치지 않고 feature 브랜치에서 바꿔요.'),
]

GOAL = ('자, 마지막 도전이에요. 새 폴더에서 GitHub Flow 전체를 처음부터 혼자 해요. '
        'main에는 memo.txt `기본 메모`가 커밋돼 있고, GitHub 저장소와 origin은 아직 없어요. `MQ3_REPO`에는 이번 도전의 새 저장소 이름이 들어 있어요.\n\n'
        '끝났을 때 이래야 해요. 본인 계정에 `MQ3_REPO` 이름의 비공개 저장소가 있고 origin이 그곳을 가리켜요. '
        'main은 직접 고치지 않고 feature 브랜치에서 바꿔요. feature에서 memo.txt를 `함께 읽는 메모`로 바꿔 커밋하고, feature를 main에 합치는 PR을 만들어 GitHub에서 병합해요. '
        '병합한 기록을 내 컴퓨터의 main으로 받아 끝내요. 명령은 앞 단계에서 쓴 것을 직접 골라 써요.\n\n'
        '이 도전은 실제 GitHub에 새 비공개 저장소와 PR을 만들어요. 실제 GitHub 실습이라 중간 초기화는 지원하지 않아요. 앱은 저장소를 지우지 않아요. 끝나면 Settings → General → Danger Zone에서 직접 지울 수 있어요.\n\n'
        + todo('`MQ3_REPO` 이름으로 비공개 저장소를 만들어 origin으로 연결하고 main을 보내세요.',
               'feature 브랜치에서 memo.txt를 `함께 읽는 메모`로 바꿔 커밋하고 GitHub에 보내세요.',
               'feature를 main에 합치는 PR을 만들고 GitHub에서 병합하세요.',
               'main으로 옮겨 병합한 기록을 받으세요.',
               '`cat memo.txt`로 확인한 뒤 제출하세요.'))

SOLUTION = '\n'.join([
    '# 저장소를 만들고 main을 보내요.',
    'gh repo create "$MQ3_REPO" --private --source . --remote origin',
    'git push -u origin main',
    '# 변경은 feature에서 해요.',
    'git switch -c feature',
    'echo "함께 읽는 메모" > memo.txt',
    'git add memo.txt',
    'git commit -m "메모 안내 개선"',
    'git push -u origin feature',
    '# PR을 만들고 병합한 뒤 main으로 받아요.',
    'gh pr create --base main --head feature --title "메모 안내 개선" --body "메모 문구를 바꿨어요."',
    'gh pr merge --merge',
    'git switch main',
    'git pull',
    'cat memo.txt',
])

SPEC = dict(
    key='github-pr', course='java', revision='github-pr-6',
    reason='저장소 생성·main 보내기·브랜치 커밋·브랜치 보내기·PR 생성·병합·로컬 main 받기를 새 실습 저장소에서 혼자 잇는 마지막 도전이에요.',
    grading='실제 GitHub API로 본인 계정의 비공개 저장소, origin, GitHub main과 로컬 main의 커밋, feature에서 만든 PR의 병합, '
            '로컬 main이 병합 커밋이고 memo.txt가 함께 읽는 메모인지 확인해요. PR 없이 main에 push, 열린 채 둔 PR, 병합 뒤 받지 않은 main은 실패해요.',
    unit=dict(id='unt_6baf8f39-2642-4cdb-ad45-bef5d3797b7d', title='마지막 도전',
              objectives=['GitHub Flow 전체를 새 저장소에서 혼자 마쳐요.'],
              premise='기본 메모만 커밋된 새 실습 폴더예요. 앞 단계의 저장소와 상관없이 새 GitHub 저장소로 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='새 저장소에서 GitHub Flow 전체를 혼자 마치세요',
              objectives=['저장소 생성부터 병합한 main 받기까지 혼자 이어요.'],
              core_flow='시작: 기본 메모 한 커밋, origin 없음, 새 MQ3_REPO. 학생은 gh repo create, push, switch -c, commit, push, gh pr create, gh pr merge, '
                        'switch, pull을 스스로 고른다. 채점은 실제 GitHub 상태와 로컬 main이다. 해설은 GitHub를 바꾸지 않고 흐름과 주의만 말한다.',
              complexity=dict(new_concepts=[], prerequisite_experience='이 수업의 여덟 단계를 각각 한 번씩 해 봤어요.',
                              changed_condition='새 저장소에서 단계 안내 없이 전체를 한 번에 해요.',
                              observable_evidence='GitHub의 병합된 PR과 병합 커밋을 가리키는 로컬 main',
                              learner_edited_lines=0, new_external_services=0)),
    task=dict(id=STEP, title='새 저장소에서 GitHub Flow 전체를 혼자 마치세요', goal=GOAL, language='git', starter_code='',
              solution=SOLUTION, tests=[], required=True,
              git_terminal=dict(github_pr='merged', files={'memo.txt': '기본 메모\n'}, setup=[]),
              narration=NARRATION),
    review={
        '조심하세요. main에서 바로 고쳐 push하면 PR이 없어서 검토 기록이 남지 않아요.':
            '이 도전의 핵심 규칙(main 직접 수정 금지)을 어겼을 때의 실제 결과를 말해요. 채점의 PR 조회가 잡아요.',
    },
)
