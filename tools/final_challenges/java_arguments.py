"""java-arguments final challenge: read the right argument positions and pass a spaced memo and a zero-padded code."""
from _common import todo

STEP = 'stp_86e157bf-bbb1-4709-8ddf-7032baca1f96'
T = '#git-demo-terminal'


def source(code_index):
    return ('public class Main {\n    public static void main(String[] args) {\n        // 첫 인자는 메모, 둘째 인자는 주문 코드예요.\n'
            '        System.out.println("인자 수: " + args.length);\n'
            '        System.out.println("메모: " + args[0]);\n'
            f'        System.out.println("코드: " + args[{code_index}]);\n    }}\n}}\n')


START, GOAL_SOURCE = source(0), source(1)
COMMANDS = ['cat Main.java']
STDOUT = '인자 수: 2\n메모: buy milk\n코드: 007\n'


def run(command, say):
    return dict(action='bash_command', command=command, say=say, target=T)


def say(text, target=T):
    return dict(action='say', text=text, target=target)


NARRATION = [
    say('마지막 도전이에요. 공백이 든 메모와 0으로 시작하는 주문 코드를 함께 넘겨요. 두 값이 각자 제자리에서 그대로 나와야 해요.',
        'text:메모 buy milk와 주문 코드 007을 실행 인자로 넘겨요.'),
    run('cat Main.java', '먼저 cat으로 코드가 어느 칸을 읽는지 봐요.'),
    say('메모도 코드도 args[0]을 읽어요. 코드 줄이 틀렸어요.'),
    say('이 줄이 둘째 인자를 읽어야 해요.', 'code:System.out.println("코드: " + args[0]);'),
    run('java Main.java buy milk 007', '따옴표 없이 넘겨 볼게요.'),
    say('인자 수가 3이에요. 공백에서 나뉘어 buy, milk, 007 세 칸이 됐어요.'),
    dict(action='patch_code', before='"코드: " + args[0]', after='"코드: " + args[1]', say='코드 줄이 둘째 칸 args[1]을 읽게 고쳐요.'),
    say('메모는 첫 칸, 코드는 둘째 칸이에요.', 'code:System.out.println("코드: " + args[1]);'),
    run('java Main.java "buy milk" 007', '이번엔 메모를 따옴표로 묶어 하나로 넘겨요.'),
    say('인자 수 2, 메모 buy milk, 코드 007이 나와요. 앞의 0도 그대로예요.'),
    say('조심하세요. 코드를 Integer.parseInt로 바꿔 출력하면 앞의 0이 사라져 7이 돼요.', 'code:String[] args'),
]

GOAL = ('자, 마지막 도전이에요. 주문 메모 프로그램이 메모와 주문 코드를 실행 인자로 받아요. '
        '메모 buy milk와 주문 코드 007을 실행 인자로 넘겨요.\n\n'
        '실행하면 이렇게 나와야 해요.\n\n```\n' + STDOUT + '```\n\n'
        '지금 코드는 한 줄이 잘못된 칸을 읽어요. 그 줄만 고치고, 실행 명령은 직접 정해 `java Main.java`로 실행해요.\n\n'
        + todo('`cat Main.java`로 각 줄이 어느 인자를 읽는지 확인하세요.',
               '코드 편집기에서 잘못된 칸을 읽는 줄을 고치세요.',
               '메모와 주문 코드를 실행 인자로 넘겨 `java Main.java`를 실행하세요.',
               '세 줄이 위와 같은지 확인한 뒤 제출하세요.'))

SPEC = dict(
    key='java-arguments', course='java', revision='java-arguments-8',
    reason='인자 위치, 공백과 따옴표로 정해지는 인자 개수, 문자열로 받는 숫자 모양 값을 한 실행에서 함께 맞추는 마지막 도전이에요.',
    grading='실제 JDK가 받은 인자 배열이 정확히 [buy milk, 007]이고 출력 세 줄이 맞는지, 저장한 소스가 둘째 칸을 읽는지 확인해요. '
            '따옴표 없이 세 인자, 첫 칸 읽기, 셋째 칸 읽기는 실패하고 작은따옴표·역슬래시로 묶은 실행도 통과해요.',
    unit=dict(id='unt_4af969e6-9910-4a3f-8346-4019f1038abd', title='마지막 도전',
              objectives=['인자 위치와 개수와 문자열 값을 한 실행에서 함께 맞춰요.'],
              premise='새 실습 폴더의 Main.java예요. 앞 단계와 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='메모와 주문 코드를 제자리에서 읽게 하세요',
              objectives=['인자 위치·따옴표·문자열 값을 함께 맞춰 실행해요.'],
              core_flow='시작 코드는 코드 줄이 args[0]을 읽는다. 학생은 args[1]로 고치고 공백 있는 메모를 따옴표로 묶어 007과 함께 넘긴다. '
                        '채점: 실제 JDK 인자 배열과 출력, 저장한 소스, 첫 확인 명령 cat. 따옴표 종류는 자유다.',
              complexity=dict(new_concepts=[], prerequisite_experience='args.length, args[0]과 args[1], 따옴표로 묶은 인자, 007을 각각 해 봤어요.',
                              changed_condition='세 규칙이 한 실행에 함께 걸려요.',
                              observable_evidence='실제 JDK가 받은 인자 배열과 세 줄 출력',
                              learner_edited_lines=1, new_external_services=0)),
    task=dict(id=STEP, title='메모와 주문 코드를 제자리에서 읽게 하세요', goal=GOAL, language='java', starter_code='',
              required=True, tests=[], solution='cat Main.java\njava Main.java "buy milk" 007',
              git_terminal=dict(initial_history='uninitialized',
                                shell=dict(step_id=STEP, goal=dict(files={'Main.java': GOAL_SOURCE}), demo=dict(files={'Main.java': START}),
                                           start=dict(files={'Main.java': START}), commands=COMMANDS),
                                java_build=dict(command=['java', 'Main.java', 'buy milk', '007'], stdout=STDOUT, class_output=None)),
              narration=NARRATION),
    review={
        '조심하세요. 코드를 Integer.parseInt로 바꿔 출력하면 앞의 0이 사라져 7이 돼요.':
            '8번에서 확인한 문자열 인자의 성질을 이 도전의 주문 코드에 적용해 말해요. 채점의 출력 비교가 잡아요.',
    },
)

SOURCES = {'goal': GOAL_SOURCE, 'start': START, 'third': source(2)}
CASES = dict(
    accept=[(['cat Main.java', 'SAVE:goal', 'java Main.java "buy milk" 007'], 'double quotes'),
            (['SAVE:goal', 'cat Main.java', "java Main.java 'buy milk' 007"], 'single quotes'),
            (['cat Main.java', 'SAVE:goal', 'java Main.java buy\\ milk 007'], 'escaped space')],
    reject=[(['cat Main.java', 'SAVE:goal', 'java Main.java buy milk 007'], 'unquoted memo becomes two arguments'),
            (['cat Main.java', 'java Main.java "buy milk" 007'], 'code line still reads the first argument'),
            (['cat Main.java', 'SAVE:third', 'java Main.java "buy milk" 007'], 'reading a third argument that does not exist'),
            (['SAVE:goal', 'java Main.java "buy milk" 007'], 'the required first look at the source was skipped')],
)
