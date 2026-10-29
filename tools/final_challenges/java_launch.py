"""java-launch final challenge: ship a changed message as a compiled class, so source, class and run agree."""
from _common import todo

STEP = 'stp_6367375b-819a-4934-8cc8-2214882a9b50'
T = '#git-demo-terminal'


def source(text):
    return ('public class Main {\n    public static void main(String[] args) {\n        // 가게 문에 붙일 안내 문구예요.\n'
            f'        System.out.println("{text}");\n    }}\n}}\n')


START, GOAL_SOURCE = source('점검 중'), source('영업 중')
COMMANDS = ['javac Main.java', 'java Main']


def run(command, say, fails=False):
    action = dict(action='bash_command', command=command, say=say, target=T)
    if fails:
        action['fails'] = True
    return action


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. 안내 문구를 바꿔 클래스 파일로 배포해요. 소스, 클래스, 실행 결과가 모두 같은 문구여야 해요.',
        'text:소스와 클래스와 실행 결과가 모두 영업 중이어야 해요.'),
    say('지금 소스는 점검 중을 출력해요. 폴더에는 아직 Main.class가 없어요.', 'code:System.out.println("점검 중");'),
    dict(action='patch_code', before='점검 중', after='영업 중', say='출력 문구를 영업 중으로 바꿀게요.'),
    say('바꾼 소스는 같은 폴더에 저장됐어요.', 'code:System.out.println("영업 중");'),
    run('java Main', '클래스로 바로 실행해 볼게요.', fails=True),
    say('Main 클래스를 찾지 못한다는 오류가 나요. 소스만 있고 클래스 파일은 아직 없어요.'),
    run('javac Main.java', 'javac로 지금 소스를 컴파일해요.'),
    say('출력 없이 끝났어요. 지금 소스로 Main.class가 생겼어요.'),
    run('java Main', '다시 클래스로 실행해요.'),
    say('영업 중이 나와요. 소스, 클래스, 실행 결과가 같아졌어요.'),
    say('조심하세요. 컴파일한 뒤 소스를 다시 고치면 Main.class는 옛 문구 그대로라서 소스와 어긋나요.',
        'code:System.out.println("영업 중");'),
]

GOAL = ('자, 마지막 도전이에요. 가게 안내 프로그램의 문구를 `점검 중`에서 `영업 중`으로 바꿔 클래스 파일로 배포해요. '
        '배포는 `java Main`으로 클래스를 실행하는 방식이에요.\n\n'
        '소스와 클래스와 실행 결과가 모두 영업 중이어야 해요. 어떤 순서로 무엇을 실행할지는 이 수업에서 배운 대로 직접 정해요.\n\n'
        + todo('코드 편집기에서 출력 문구를 `영업 중`으로 바꾸세요.',
               '바꾼 소스가 클래스 파일에 들어가게 하세요.',
               '`java Main`으로 실행해 `영업 중`이 나오는지 확인하세요.',
               '파일을 그대로 둔 채 제출하세요.'))

SPEC = dict(
    key='java-launch', course='java', revision='java-launch-7',
    reason='소스 수정·컴파일·클래스 실행의 순서를 명령 안내 없이 스스로 정해 셋을 일치시키는 마지막 도전이에요.',
    grading='실제 JDK 실행 기록에서 지금 소스와 지금 클래스로 java Main을 실행해 영업 중이 나왔는지, 클래스 파일만 실행해도 영업 중인지 확인해요. '
            'java Main.java만 실행, 고치기 전 컴파일, 컴파일 뒤 소스 재수정은 실패해요.',
    unit=dict(id='unt_87ae3d47-c57f-498f-ac31-97c7f3d81d80', title='마지막 도전',
              objectives=['소스·클래스·실행 결과를 스스로 일치시켜요.'],
              premise='새 실습 폴더의 Main.java예요. 클래스 파일은 없어요. 앞 단계와 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='바꾼 문구를 클래스 파일로 배포하세요',
              objectives=['수정·컴파일·클래스 실행 순서를 스스로 정해 셋을 일치시켜요.'],
              core_flow='시작 소스는 점검 중, 클래스 없음. 학생은 문구를 고치고 javac와 java Main을 스스로 고른다. '
                        '채점: 실제 java Main 기록의 출력·소스 지문·클래스 지문과 클래스 단독 실행 결과. 해설은 클래스가 없을 때의 실제 오류를 보여 준다.',
              complexity=dict(new_concepts=[], prerequisite_experience='소스 실행, javac, java Main, 재컴파일을 각각 해 봤어요.',
                              changed_condition='명령 안내 없이 목표 상태만 주어져요.',
                              observable_evidence='java Main의 실제 출력과 클래스 단독 실행 결과',
                              learner_edited_lines=1, new_external_services=0)),
    task=dict(id=STEP, title='바꾼 문구를 클래스 파일로 배포하세요', goal=GOAL, language='java', starter_code='',
              required=True, tests=[], solution='javac Main.java\njava Main',
              git_terminal=dict(initial_history='uninitialized',
                                shell=dict(step_id=STEP, goal=dict(files={'Main.java': GOAL_SOURCE}), demo=dict(files={'Main.java': START}),
                                           start=dict(files={'Main.java': START}), commands=COMMANDS),
                                java_build=dict(command=['java', 'Main'], stdout='영업 중\n', class_output='영업 중\n', class_relation='', demo_class_source=None)),
              narration=NARRATION),
    review={
        '조심하세요. 컴파일한 뒤 소스를 다시 고치면 Main.class는 옛 문구 그대로라서 소스와 어긋나요.':
            '6번에서 실제로 본 현상(소스만 고치면 클래스는 그대로)을 배포 상황의 위험으로 말해요. 채점의 소스 지문 비교가 잡아요.',
    },
)

# Sequences for tests/final_terminal_challenges.rs. "SAVE:<name>" saves that source in the editor; others are typed.
SOURCES = {'goal': GOAL_SOURCE, 'start': START, 'later': source('영업 종료')}
CASES = dict(
    accept=[(['SAVE:goal', 'javac Main.java', 'java Main'], 'edit, compile, run the class'),
            (['SAVE:goal', 'java Main.java', 'javac Main.java', 'java Main'], 'check with the source launcher first'),
            (['javac Main.java', 'SAVE:goal', 'javac Main.java', 'java Main'], 'an early compile followed by a recompile')],
    reject=[(['SAVE:goal', 'java Main.java'], 'only the source launcher, no class'),
            (['javac Main.java', 'SAVE:goal', 'java Main'], 'compiled before editing: the class prints the old text'),
            (['SAVE:goal', 'javac Main.java', 'java Main', 'SAVE:later'], 'source edited again after compiling'),
            (['javac Main.java', 'java Main'], 'text never changed')],
)
