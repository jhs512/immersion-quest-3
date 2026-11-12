"""Write the second Floci cloud lesson (server lifecycle and deletion order) from one reviewed definition.

The written files (tools/redesigned_lessons/cloud_ec2_lifecycle/*) are the canonical sources.
Shared helpers (prepared list-servers tab, copy blocks, narration actions, policy snapshot) come
from the first lesson's author script so both lessons stay consistent.
Run from the repository root: python .scratch/floci-course-wayfinder/second-lesson/author_lesson.py
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from lesson_prd import approve, render  # noqa: E402

_spec = importlib.util.spec_from_file_location('first', ROOT / '.scratch/floci-course-wayfinder/first-lesson/author_lesson.py')
first = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(first)
terminal, say, run, fence, write = first.terminal, first.say, first.run, first.fence, first.write
LIST_SERVERS, ENDPOINT_OPT, LIST_SUBNETS_CMD, TERM = first.LIST_SERVERS, first.ENDPOINT_OPT, first.LIST_SUBNETS_CMD, first.TERM

KEY = 'cloud-ec2-lifecycle'
FOLDER = ROOT / 'tools/redesigned_lessons/cloud_ec2_lifecycle'
LESSON_ID = 'lsn_81d67284-bfe0-49b9-ac29-33f9aea19c00'
COURSE_ID = first.COURSE_ID
TITLE = '클라우드 · 서버를 멈추고 다시 켜고 없애요'
CH = ['chp_8bd5ec7c-84b7-4c7b-8a89-09062c811a09', 'chp_92e0193d-d9f6-4650-9a3b-7afdf00fb315']
UN = ['unt_a2e41539-a3c0-49be-bdc9-7ac01e47813f', 'unt_9b9870ff-1a0e-4bfd-93c0-6c7d96444250',
      'unt_3fda7ab4-4d49-4c96-8dd8-8fb0ce64bcc8']
ST = ['stp_8501d14f-3b50-4c04-8fb6-c27fa6923577', 'stp_65e476ad-0cc4-4bed-a6e7-e80bd1c63bcf',
      'stp_25c6d982-502f-4aff-bf81-812df3e61cac', 'stp_fa217c4b-6db8-4c1d-9df0-483147439d4c',
      'stp_0cbeda4d-c73d-49e7-882f-88d6bc4c5480', 'stp_eb061d59-86eb-4cd6-a985-e05e8e9389d6']
VPC = '10.91.0.0/16'
TWO = [{'name': 'A', 'cidr': '10.91.1.0/24'}, {'name': 'B', 'cidr': '10.91.2.0/24'}]

SERVER_OPT = '--instance-ids "$LAB_SERVER_ID"'
SUBNET_B_OPT = '--subnet-id "$LAB_SUBNET_B_ID"'


def ec2(verb, *options):
    return ' '.join(['aws ec2', verb, ENDPOINT_OPT, *options])


STOP = ec2('stop-instances', SERVER_OPT)
START = ec2('start-instances', SERVER_OPT)
TERMINATE = ec2('terminate-instances', SERVER_OPT)
WRONG_STOP = ec2('stop-instances', '--instance-ids "$LAB_CLIENT_ID"')
DELETE_B = ec2('delete-subnet', SUBNET_B_OPT)
DELETE_A = ec2('delete-subnet', '--subnet-id "$LAB_SUBNET_A_ID"')
DELETE_VPC = ec2('delete-vpc', '--vpc-id "$LAB_VPC_ID"')
TERMINATE_BOTH = ec2('terminate-instances', '--instance-ids "$LAB_SERVER_ID" "$LAB_CLIENT_ID"')
DESCRIBE_VPC = ec2('describe-vpcs', '--vpc-ids "$LAB_VPC_ID"')
REQUEST = 'client-request "$LAB_SERVER_IP"'
LIST = 'bash list-servers.sh'


def wait(state, ids=SERVER_OPT):
    return ec2('wait', f'instance-{state}', ids)


def copy_block(*options):
    return ('**복사해서 쓰는 옵션**\n\n'
            '실습 주소와 준비된 자원의 ID는 아래 블록에서 언제든 복사해 붙여 넣을 수 있어요.\n\n'
            + '\n\n'.join(fence(o) for o in options))


SETUP = ('이번 문제는 새 실습 상태에서 시작해요. 실습 환경이 VPC 10.91.0.0/16 안에 서브넷 A 10.91.1.0/24와 서브넷 B 10.91.2.0/24를 만들어 뒀어요. '
         '서브넷 A에는 클라이언트 서버(`LAB_CLIENT_ID`), 서브넷 B에는 자바 서버(`LAB_SERVER_ID`)가 실행 중이에요. '
         '자바 서버의 사설 IP 주소는 `LAB_SERVER_IP`에 있어요.')
LIST_NOTE = '편집기의 `list-servers.sh` 탭(읽기 전용)은 서버의 ID·서브넷 ID·사설 IP 주소·상태를 표로 보여 주는 준비 명령이에요.'


def lifecycle(goal, **extra):
    return dict({'goal': goal, 'vpc_cidr': VPC, 'subnets': TWO, 'client_subnet': 'A', 'server_subnet': 'B'}, **extra)


def term(step, goal, **extra):
    return terminal(step, lifecycle(goal, **extra), {'list-servers.sh': LIST_SERVERS}, [], ['list-servers.sh'])


# -- steps -------------------------------------------------------------------------------
STEPS = []

STEPS.append(dict(
    id=ST[0], title='응답하는 서버를 멈추세요',
    objectives=['서버를 멈추면(stop) 상태가 stopping을 거쳐 stopped가 되고, 그동안 요청에 응답하지 않아요.'],
    goal='서버(인스턴스)는 멈췄다가 다시 켤 수 있어요. 멈추는 명령은 `aws ec2 stop-instances`예요. `--instance-ids`로 멈출 서버를 정해요.\n\n'
         + SETUP + '\n\n'
         + LIST_NOTE + '\n\n'
         + copy_block(ENDPOINT_OPT, SERVER_OPT) + '\n\n'
         '**할 일**\n\n'
         f'1. 터미널에 `{REQUEST}`를 입력하고 Enter를 누르세요. 자바 서버가 응답하는지 확인하세요.\n'
         f'2. 터미널에 `{STOP}`를 입력하고 Enter를 누르세요. 출력의 `CurrentState`를 읽으세요.\n'
         f'3. 터미널에 `{LIST}`를 입력하고 Enter를 누르세요. 자바 서버의 상태를 읽으세요.\n'
         f'4. 상태가 `stopped`가 아니면 잠시 뒤 `{LIST}`를 다시 실행하세요.\n'
         f'5. `stopped`가 되면 `{REQUEST}`를 다시 입력하세요. 응답이 오는지 확인하세요.\n'
         '6. 자바 서버가 `stopped`인 것을 확인했으면 제출 버튼을 누르세요.',
    solution=f'# 자바 서버를 멈춰요. 응답의 CurrentState는 아직 stopping이에요.\n{STOP}\n# stopped가 될 때까지 표를 다시 확인해요.\n{LIST}',
    terminal=term(ST[0], 'stop_server'),
    narration=[
        say('서브넷 B의 자바 서버가 실행 중이에요. 먼저 응답하는지 확인할게요.', 'text:서브넷 B에는 자바 서버(LAB_SERVER_ID)가 실행 중이에요.'),
        run(REQUEST, '클라이언트 서버에서 자바 서버로 요청해요.', wait=120),
        say('HTTP/1.1 200 OK가 왔어요. 자바 서버가 응답하고 있어요.', TERM),
        say('이제 stop-instances로 이 서버를 멈춰요. --instance-ids가 멈출 서버를 정해요.',
            'text:--instance-ids로 멈출 서버를 정해요.'),
        run(STOP, '서버를 멈추는 명령을 입력해요.'),
        say('PreviousState는 running, CurrentState는 stopping이에요. 아직 다 멈춘 게 아니에요.', TERM),
        say('조심하세요. 명령이 성공했다고 서버가 바로 멈춘 건 아니에요. 상태를 다시 확인해야 해요.',
            'text:상태가 stopped가 아니면 잠시 뒤 bash list-servers.sh를 다시 실행하세요.'),
        run(wait('stopped'), '해설은 stopped가 될 때까지 기다리는 명령을 써요.', wait=300),
        run(LIST, '표로 상태를 볼게요.'),
        say('자바 서버가 stopped예요. 사설 IP 주소와 서브넷은 그대로 표에 남아 있어요.', TERM),
        run(REQUEST, '멈춘 서버에 다시 요청해요.', fails=True, wait=120),
        say('이번에는 연결하지 못했어요. 멈춘 서버는 요청에 응답하지 않아요.', TERM),
    ],
    core='수업 예고의 1번째 경험이다.\n\n'
         '시작: VPC 10.91.0.0/16, 서브넷 A(클라이언트 running)·B(자바 서버 running, HTTP 응답). 준비 파일은 읽기 전용 list-servers.sh.\n'
         '행동: client-request로 응답 확인 → stop-instances 직접 입력 → 표로 stopping→stopped 확인 → client-request 다시.\n'
         '관찰 근거: 응답의 PreviousState·CurrentState, 표의 상태, 멈춘 뒤 연결 실패.\n'
         '판정: 초기 상태(running) 실패, 정답 통과. 종료 실패, 클라이언트를 멈추면 실패. stopping은 정해진 시간 안에서 기다린다.',
    complexity=dict(new_concepts=['stop-instances와 stopping→stopped 상태 변화'], prerequisite_experience='첫 클라우드 수업의 서버 배치와 client-request.',
                    changed_condition='응답하는 서버를 멈춘다.', observable_evidence='CurrentState, 표의 상태, client-request 연결 실패.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[1], title='멈춘 서버를 다시 켜세요',
    objectives=['멈춘 서버를 다시 켜면 같은 서버가 같은 사설 주소로 running이 돼요. 그 안의 프로그램은 저절로 다시 뜨지 않아요.'],
    goal='멈춘 서버는 `aws ec2 start-instances`로 다시 켤 수 있어요. 멈췄던 그 서버가 다시 실행돼요.\n\n'
         '이번 문제는 새 실습 상태에서 시작해요. 앞 문제와 같은 VPC·서브넷·클라이언트 서버가 있어요. '
         '서브넷 B의 자바 서버(`LAB_SERVER_ID`)는 응답하던 상태에서 실습 환경이 미리 멈춰 뒀어요(stopped). '
         '멈추기 전 사설 IP 주소는 `LAB_SERVER_IP`에 있어요.\n\n'
         + LIST_NOTE + '\n\n'
         + copy_block(ENDPOINT_OPT, SERVER_OPT) + '\n\n'
         '**할 일**\n\n'
         f'1. 터미널에 `{LIST}`를 입력하고 Enter를 누르세요. 자바 서버의 상태와 사설 IP 주소를 읽으세요.\n'
         f'2. 터미널에 `{START}`를 입력하고 Enter를 누르세요. 출력의 `CurrentState`를 읽으세요.\n'
         f'3. 터미널에 `{LIST}`를 다시 입력하세요. 상태가 `running`인지, 사설 IP 주소가 1번과 같은지 확인하세요.\n'
         f'4. 터미널에 `{REQUEST}`를 입력하고 Enter를 누르세요. 응답이 오는지 확인하세요.\n'
         '5. 자바 서버가 `running`인 것을 확인했으면 제출 버튼을 누르세요.',
    solution=f'# 멈춘 서버를 다시 켜요. 응답의 CurrentState는 pending이에요.\n{START}\n# running이 됐는지, 주소가 그대로인지 표로 확인해요.\n{LIST}',
    terminal=term(ST[1], 'start_server'),
    narration=[
        say('자바 서버는 미리 멈춰 둔 상태예요. 표로 먼저 확인할게요.', 'text:실습 환경이 미리 멈춰 뒀어요(stopped).'),
        run(LIST, '서버 표를 볼게요.', wait=120),
        say('자바 서버는 stopped이고, 사설 IP 주소는 10.91.2로 시작해요. 이 주소를 기억해 두세요.', TERM),
        run(START, 'start-instances로 다시 켜요.'),
        say('PreviousState는 stopped, CurrentState는 pending이에요. 켜지는 중이에요.', TERM),
        run(wait('running'), 'running이 될 때까지 기다려요.', wait=300),
        run(LIST, '다시 표를 볼게요.'),
        say('running이에요. 같은 ID의 서버가 처음과 같은 사설 IP 주소로 돌아왔어요.', TERM),
        run(REQUEST, '이제 요청을 보내 볼게요.', fails=True, wait=120),
        say('조심하세요. 서버는 running인데 연결이 거절됐어요. 자바 프로그램은 처음 켤 때만 시작했어요.',
            'text:멈췄던 그 서버가 다시 실행돼요.'),
        say('서버가 켜진 것과 그 안의 프로그램이 응답하는 것은 달라요. 이 수업은 서버의 상태만 채점해요.', TERM),
    ],
    core='수업 예고의 2번째 경험이다.\n\n'
         '시작: 1번과 같은 구성. 자바 서버는 HTTP 응답을 확인한 뒤 준비 단계에서 stopped로 만든다(시작 설명에서 먼저 알림).\n'
         '행동: 표로 stopped·주소 확인 → start-instances → 표로 running·같은 주소 확인 → client-request.\n'
         '관찰 근거: CurrentState pending, 표의 running과 같은 사설 주소, 연결 거절(user-data는 처음 실행 때만 돈다).\n'
         '판정: 초기 상태(stopped) 실패, 정답 통과. 새 서버를 만드는 우회는 「새 서버」로 실패. 종료하면 실패.\n'
         '주의: 프로그램 자동 기동(서비스 등록)은 다루지 않고 안 뜬다는 사실만 관찰한다.',
    complexity=dict(new_concepts=['start-instances와 재시작 뒤 사설 주소 유지'], prerequisite_experience='앞 스텝의 stop과 상태 읽기.',
                    changed_condition='서버가 멈춘 상태로 시작한다.', observable_evidence='표의 상태·사설 주소, 재시작 뒤 연결 거절.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[2], title='멈출 서버를 골라 멈추세요',
    objectives=['명령은 --instance-ids가 가리키는 서버에만 가요. 실행 전에 그 ID가 어느 서버인지 확인해요.'],
    goal='서버가 여러 대면 `--instance-ids`의 값이 어느 서버를 가리키는지가 중요해요.\n\n'
         + SETUP + '\n\n'
         '서브넷 B(10.91.2.0/24)의 자바 서버만 멈춰야 해요. 클라이언트 서버는 실행 중인 그대로 둬야 해요. '
         '그런데 아래 명령의 `--instance-ids`는 다른 서버를 가리켜요. 그대로 실행하면 엉뚱한 서버가 멈춰요. '
         '그때는 「초기화」로 처음 상태를 받으세요.\n\n'
         + fence(WRONG_STOP) + '\n\n'
         + LIST_NOTE + '\n\n'
         + copy_block(ENDPOINT_OPT, SERVER_OPT) + '\n\n'
         '**할 일**\n\n'
         f'1. 터미널에 `{LIST}`를 입력하고 Enter를 누르세요. 두 서버의 ID와 서브넷 ID를 읽으세요.\n'
         '2. 터미널에 `echo "$LAB_CLIENT_ID"`를 입력하고 Enter를 누르세요. 위 명령이 가리키는 ID가 표의 어느 서버인지 찾으세요.\n'
         '3. 위 명령을 복사해 터미널에 붙여 넣고, `--instance-ids` 값 한 곳을 서브넷 B의 자바 서버로 고친 뒤 Enter를 누르세요.\n'
         f'4. 터미널에 `{LIST}`를 입력하세요. 자바 서버만 `stopped`가 되고 클라이언트 서버는 `running`인지 확인하세요.\n'
         '5. 두 서버의 상태를 확인했으면 제출 버튼을 누르세요.',
    solution=f'# --instance-ids를 "$LAB_CLIENT_ID"에서 서브넷 B의 자바 서버 "$LAB_SERVER_ID"로 고쳐요.\n# 표의 자바 서버 ID(i-로 시작)를 그대로 적어도 같아요.\n{STOP}\n{LIST}',
    terminal=term(ST[2], 'stop_server'),
    narration=[
        say('자바 서버만 멈춰야 해요. 그런데 주어진 명령은 다른 서버를 가리켜요.',
            'text:그런데 아래 명령의 --instance-ids는 다른 서버를 가리켜요.'),
        run(LIST, '실행하기 전에 서버 표부터 볼게요.', wait=120),
        say('서버가 두 대예요. 서브넷 ID가 다른 두 자리에 한 대씩 있어요.', TERM),
        run('echo "$LAB_CLIENT_ID"', '주어진 명령의 ID가 어느 서버인지 출력해 볼게요.'),
        say('이 ID는 표에서 서브넷 A에 있는 서버예요. 자바 서버가 아니라 클라이언트 서버예요.', TERM),
        say('조심하세요. 그대로 실행하면 클라이언트 서버가 멈춰요. 명령은 ID가 가리키는 서버에만 가요.',
            'text:그대로 실행하면 엉뚱한 서버가 멈춰요.'),
        run(STOP, '--instance-ids 한 곳을 LAB_SERVER_ID로 고쳐 실행해요.'),
        say('CurrentState가 stopping이에요. 이번에는 자바 서버를 멈추는 중이에요.', TERM),
        run(wait('stopped'), 'stopped가 될 때까지 기다려요.', wait=300),
        run(LIST, '두 서버의 상태를 볼게요.'),
        say('자바 서버만 stopped이고, 클라이언트 서버는 running 그대로예요.', TERM),
    ],
    core='수업 예고의 3번째 경험이다.\n\n'
         '시작: 1번과 같은 구성. 본문의 시작 명령은 --instance-ids "$LAB_CLIENT_ID"(서브넷 A의 클라이언트 서버).\n'
         '행동: 표 → echo로 시작 명령의 ID 확인 → ID 한 곳을 자바 서버로 고쳐 실행 → 표.\n'
         '관찰 근거: 표의 두 서버 ID·서브넷, echo로 본 ID, 고친 뒤 두 서버의 상태.\n'
         '판정: 시작 명령 그대로 실행하면 클라이언트가 멈춰 실패(「초기화」로 복구). 둘 다 멈추면 실패. 자바 서버 ID를 문자 그대로 적어도 통과.',
    complexity=dict(new_concepts=['--instance-ids로 명령의 대상 고르기'], prerequisite_experience='1번의 stop과 표 읽기.',
                    changed_condition='시작 명령이 클라이언트 서버를 가리킨다.', observable_evidence='표의 ID·서브넷 ID·상태, echo 출력.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[3], title='서버를 종료하세요',
    objectives=['종료한 서버(terminated)는 다시 켤 수 없어요. 멈춘 서버와 달라요.'],
    goal='서버를 아예 없애는 명령은 `aws ec2 terminate-instances`예요. 이것을 종료(terminate)라고 해요. 종료한 서버는 다시 켤 수 없어요.\n\n'
         + SETUP + '\n\n'
         + LIST_NOTE + '\n\n'
         + copy_block(ENDPOINT_OPT, SERVER_OPT) + '\n\n'
         '**할 일**\n\n'
         f'1. 터미널에 `{TERMINATE}`를 입력하고 Enter를 누르세요. 출력의 `CurrentState`를 읽으세요.\n'
         f'2. 터미널에 `{LIST}`를 입력하세요. 자바 서버의 상태가 `terminated`가 될 때까지 다시 확인하세요.\n'
         f'3. 터미널에 `{START}`를 입력하고 Enter를 누르세요. 오류 메시지를 읽으세요.\n'
         '4. 자바 서버가 `terminated`이고 클라이언트 서버는 `running`인 것을 확인했으면 제출 버튼을 누르세요.',
    solution=f'# 자바 서버를 종료해요. 응답의 CurrentState는 shutting-down이에요.\n{TERMINATE}\n# terminated가 될 때까지 표를 확인해요.\n{LIST}',
    terminal=term(ST[3], 'terminate_server'),
    narration=[
        say('이번에는 서버를 멈추지 않고 아예 없애요. terminate-instances를 써요.',
            'text:서버를 아예 없애는 명령은 aws ec2 terminate-instances예요.'),
        run(TERMINATE, '자바 서버를 종료해요.', wait=120),
        say('CurrentState가 shutting-down이에요. 없어지는 중이에요.', TERM),
        run(wait('terminated'), 'terminated가 될 때까지 기다려요.', wait=300),
        run(LIST, '표를 볼게요.'),
        say('자바 서버가 terminated예요. 표에는 남아 있지만 이미 없어진 서버예요.', TERM),
        run(START, '다시 켜 볼게요.', fails=True),
        say('IncorrectInstanceState 오류예요. 종료한 서버는 켤 수 있는 상태가 아니에요.', TERM),
        say('조심하세요. 멈춤과 종료는 이름이 비슷하지만 달라요. 다시 쓸 서버면 멈추기만 해요.',
            'text:종료한 서버는 다시 켤 수 없어요.'),
    ],
    core='수업 예고의 4번째 경험이다.\n\n'
         '시작: 1번과 같은 구성.\n'
         '행동: terminate-instances → 표로 shutting-down→terminated 확인 → start-instances 시도.\n'
         '관찰 근거: CurrentState shutting-down, 표의 terminated, IncorrectInstanceState 거절.\n'
         '판정: 초기 상태 실패, 정답 통과. 멈추기만 하면 실패. 클라이언트를 종료하면 실패.',
    complexity=dict(new_concepts=['terminate-instances와 다시 켤 수 없는 terminated'], prerequisite_experience='1·2번의 stop·start.',
                    changed_condition='서버를 멈추지 않고 없앤다.', observable_evidence='CurrentState, 표의 terminated, IncorrectInstanceState.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[4], title='서브넷 B를 지우세요',
    objectives=['서버가 남아 있는 서브넷은 지울 수 없어요. 그 안의 서버부터 종료해야 해요.'],
    goal='서브넷은 `aws ec2 delete-subnet`으로 지워요. 그런데 안에 서버가 남아 있으면 거절돼요. 멈춘 서버도 남아 있는 거예요.\n\n'
         + SETUP + '\n\n'
         '서브넷 B를 지우세요. 서브넷 A와 클라이언트 서버는 그대로 둬야 해요.\n\n'
         + LIST_NOTE + '\n\n'
         + copy_block(ENDPOINT_OPT, SUBNET_B_OPT, SERVER_OPT) + '\n\n'
         '**할 일**\n\n'
         f'1. 터미널에 `{DELETE_B}`를 입력하고 Enter를 누르세요. 오류 메시지에서 오류 이름을 찾으세요.\n'
         f'2. 터미널에 `{LIST}`를 입력하세요. 서브넷 B(`LAB_SUBNET_B_ID`)에 남아 있는 서버를 찾으세요.\n'
         f'3. 그 서버를 `{TERMINATE}`로 종료하세요.\n'
         f'4. `{LIST}`를 다시 실행해 그 서버가 `terminated`가 될 때까지 확인하세요.\n'
         '5. ↑ 키로 1번 명령을 다시 불러와 Enter를 누르세요.\n'
         f'6. 터미널에 `{LIST_SUBNETS_CMD}`를 입력하세요. 서브넷 A만 남았는지 확인하고 제출 버튼을 누르세요.',
    solution=(f'# 서브넷 B에 서버가 남아 있으면 거절돼요(DependencyViolation).\n{DELETE_B}\n'
              f'# 그 서버부터 없애요. 멈추기(stop)만 하면 여전히 거절돼요.\n{TERMINATE}\n'
              f'# terminated가 된 뒤 같은 명령이 통과해요.\n{wait("terminated")}\n{DELETE_B}\n{LIST_SUBNETS_CMD}'),
    terminal=term(ST[4], 'delete_subnet', target_subnet='B'),
    narration=[
        say('서브넷 B를 지우는 문제예요. 먼저 그대로 지워 볼게요.', 'text:서브넷 B를 지우세요.'),
        run(DELETE_B, 'delete-subnet을 입력해요.', fails=True, wait=120),
        say('DependencyViolation 오류예요. 이 서브넷에 기대고 있는 자원이 있다는 뜻이에요.', TERM),
        run(LIST, '서브넷 B에 무엇이 있는지 표로 볼게요.'),
        say('자바 서버가 서브넷 B의 ID로 실행 중이에요. 이 서버가 서브넷을 붙잡고 있어요.', TERM),
        say('조심하세요. 서버를 멈추기만 해도 서브넷은 안 지워져요. 멈춘 서버도 자리를 차지해요.',
            'text:멈춘 서버도 남아 있는 거예요.'),
        run(TERMINATE, '그래서 자바 서버를 종료해요.'),
        run(wait('terminated'), 'terminated가 될 때까지 기다려요.', wait=300),
        run(DELETE_B, '같은 delete-subnet을 다시 실행해요.'),
        say('이번에는 오류가 없어요. 서버를 먼저 없애니 서브넷이 지워졌어요.', TERM),
        run(LIST_SUBNETS_CMD, '남은 서브넷을 볼게요.'),
        say('서브넷 A만 남았어요. 지우는 순서는 안에 든 서버부터예요.', TERM),
    ],
    core='수업 예고의 5번째 경험이자 대표 문제다.\n\n'
         '시작: 1번과 같은 구성.\n'
         '행동: delete-subnet(DependencyViolation) → 표로 남은 서버 확인 → terminate → terminated 확인 → 같은 delete-subnet → 서브넷 목록.\n'
         '관찰 근거: 실제 DependencyViolation, 표의 서브넷 ID, 삭제 뒤 서브넷 목록.\n'
         '판정: 초기 상태 실패, 정답 통과. 멈추기만 하면 삭제가 거절돼 실패. 서브넷 A 삭제·클라이언트 종료 실패. 출력 위조 실패.',
    complexity=dict(new_concepts=['delete-subnet의 DependencyViolation과 의존 자원부터 지우는 순서'], prerequisite_experience='4번의 terminate.',
                    changed_condition='지울 서브넷 안에 서버가 실행 중이다.', observable_evidence='DependencyViolation, 표, 서브넷 목록.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[5], title='실습 VPC를 모두 정리하세요',
    objectives=['거절 메시지를 따라 서버 → 서브넷 → VPC 순서로 모두 지워요.'],
    goal='VPC는 `aws ec2 delete-vpc`로 지워요. 안에 서브넷이 남아 있으면 거절돼요. 서브넷은 안에 서버가 남아 있으면 거절돼요.\n\n'
         + SETUP + '\n\n'
         '이 VPC를 모두 정리하세요. 마지막에는 VPC가 없어야 해요. 서버는 지운 뒤에도 `terminated`로 표에 남을 수 있어요. '
         'VPC를 지우는 명령은 아래와 같아요.\n\n'
         + fence(DELETE_VPC) + '\n\n'
         + LIST_NOTE + '\n\n'
         + copy_block(ENDPOINT_OPT, '--vpc-id "$LAB_VPC_ID"', '--instance-ids "$LAB_SERVER_ID" "$LAB_CLIENT_ID"',
                      SUBNET_B_OPT, '--subnet-id "$LAB_SUBNET_A_ID"') + '\n\n'
         '**할 일**\n\n'
         '1. 위 명령을 복사해 터미널에 붙여 넣고 Enter를 누르세요. 오류 메시지를 읽으세요.\n'
         f'2. `{LIST}`와 `{LIST_SUBNETS_CMD}`로 VPC 안에 남은 서버와 서브넷을 찾으세요.\n'
         '3. 서버 두 대를 `terminate-instances`로 종료하고, `terminated`가 될 때까지 확인하세요.\n'
         '4. 서브넷 두 개를 `delete-subnet`으로 하나씩 지우세요.\n'
         '5. ↑ 키로 1번 명령을 다시 불러와 Enter를 누르세요.\n'
         f'6. 터미널에 `{DESCRIBE_VPC}`를 입력하세요. VPC가 없다는 오류가 나오면 제출 버튼을 누르세요.',
    solution=(f'# VPC 안의 서버부터 종료해요.\n{TERMINATE_BOTH}\n{wait("terminated", "--instance-ids \"$LAB_SERVER_ID\" \"$LAB_CLIENT_ID\"")}\n'
              f'# 그다음 서브넷을 지워요.\n{DELETE_B}\n{DELETE_A}\n'
              f'# 마지막으로 VPC를 지워요.\n{DELETE_VPC}'),
    terminal=term(ST[5], 'delete_vpc'),
    narration=[
        say('이번에는 VPC 하나를 통째로 정리해요. 먼저 VPC부터 지워 볼게요.', 'text:이 VPC를 모두 정리하세요.'),
        run(DELETE_VPC, 'delete-vpc를 입력해요.', fails=True, wait=120),
        say('DependencyViolation이에요. VPC 안에 아직 자원이 남아 있어요.', TERM),
        run(LIST, '남은 서버부터 볼게요.'),
        say('서버가 두 대 실행 중이에요. 서브넷 A와 B에 한 대씩 있어요.', TERM),
        run(TERMINATE_BOTH, '두 서버를 한 번에 종료해요. ID를 공백으로 이어 써요.'),
        run(wait('terminated', '--instance-ids "$LAB_SERVER_ID" "$LAB_CLIENT_ID"'), '둘 다 terminated가 될 때까지 기다려요.', wait=300),
        run(DELETE_B, '이제 서브넷 B를 지워요.'),
        run(DELETE_A, '서브넷 A도 지워요.'),
        run(LIST_SUBNETS_CMD, '서브넷이 남았는지 볼게요.'),
        say('Subnets가 비어 있어요. 이제 VPC 안에 남은 게 없어요.', TERM),
        run(DELETE_VPC, '처음의 delete-vpc를 다시 실행해요.'),
        run(DESCRIBE_VPC, 'VPC를 조회해 볼게요.', fails=True),
        say('InvalidVpcID.NotFound예요. VPC가 지워졌어요.', TERM),
        say('조심하세요. 거꾸로 VPC부터 지우려 하면 계속 거절돼요. 안쪽부터 서버, 서브넷, VPC 순서예요.',
            'text:안에 서브넷이 남아 있으면 거절돼요.'),
    ],
    core='수업 예고의 6번째 경험이자 마지막 수행이다. 새 개념 없이 4·5번을 조합한다.\n\n'
         '시작: 1번과 같은 구성(서버 두 대 running, 서브넷 둘).\n'
         '행동: delete-vpc(거절) → 남은 자원 확인 → 서버 둘 종료 → 서브넷 둘 삭제 → delete-vpc → describe-vpcs.\n'
         '관찰 근거: DependencyViolation, 빈 서브넷 목록, InvalidVpcID.NotFound.\n'
         '판정: 소유 VPC가 목록에 없으면 통과. 서버를 멈추기만 하거나 서브넷 하나만 지우면 VPC가 남아 실패.',
    complexity=dict(new_concepts=[], prerequisite_experience='4·5번의 terminate와 delete-subnet. delete-vpc는 본문의 명령을 붙여 넣는다.',
                    changed_condition='VPC 하나를 통째로 정리한다.', observable_evidence='delete-vpc 거절, 빈 서브넷 목록, VPC 조회 오류.',
                    learner_edited_lines=3, new_external_services=0),
))

# -- hierarchy ---------------------------------------------------------------------------
HIERARCHY = [
    dict(id=CH[0], title='서버를 멈추고 다시 켜요',
         objectives=['멈춘 서버는 자리와 주소를 그대로 가지고 다시 켤 수 있어요. 상태가 바뀌는 데 시간이 걸려요.'],
         units=[dict(id=UN[0], title='멈추고 다시 켜기', steps=ST[0:3],
                     objectives=['stop·start의 상태 변화와 재시작 뒤 남는 것을 확인하고, 명령의 대상 서버를 ID로 골라요.'],
                     premise='실습 환경이 VPC 10.91.0.0/16에 서브넷 A·B를 만들고, A에 클라이언트 서버, B에 자바 서버를 실행해 둬요. '
                             '문제마다 새 실습 상태에서 시작하고, 서버를 준비하는 데 몇 분 걸릴 수 있어요. 모든 aws 명령은 이 컴퓨터의 로컬 실습 주소로만 가요.')]),
    dict(id=CH[1], title='없애고, 순서대로 지워요',
         objectives=['종료한 서버는 돌아오지 않아요. 지울 때는 안에 든 자원부터 서버 → 서브넷 → VPC 순서로 지워요.'],
         units=[dict(id=UN[1], title='종료와 삭제 의존성', steps=ST[3:5],
                     objectives=['terminate의 결과와, 서버가 남은 서브넷이 거절되는 이유를 실제 오류로 확인해요.'],
                     premise='앞 장과 같은 구성에서 시작해요. 서버를 없애거나 자원을 지우는 문제예요.'),
                dict(id=UN[2], title='마지막 수행', steps=ST[5:6],
                     objectives=['새 개념 없이 종료와 삭제 순서를 조합해 VPC 하나를 정리해요.'],
                     premise='서버 두 대와 서브넷 두 개가 든 VPC를 통째로 정리해요.')]),
]

LEARN = ['서버를 멈추고 다시 켜면 무엇이 남고 무엇이 사라지는지 실제 상태로 확인해요.',
         '상태가 바로 바뀌지 않는 것을 보고, 다음 명령 전에 원하는 상태가 됐는지 확인해요.',
         '자원을 지우는 순서를 거절 메시지로 찾아요. 서버 → 서브넷 → VPC 순서예요.']
CHALLENGE = ('준비된 VPC 10.91.0.0/16에는 서브넷 두 개와 서버 두 대가 있어요. '
             '거절 메시지를 읽으며 서버 → 서브넷 → VPC 순서로 모두 지우세요. 지운 뒤에는 그 VPC가 목록에 없어야 해요.')
CONSTRAINTS = ['첫 클라우드 수업(VPC·서브넷·서버 배치)을 마쳤다고 가정해요.',
               '모든 aws 명령은 이 컴퓨터의 로컬 실습 주소로만 가요. 실제 AWS 계정은 쓰지 않아요.',
               '문제마다 새 실습 상태에서 시작해요. 앞 문제의 결과가 이어지지 않아요.',
               '로컬 실습 환경은 실제 AWS와 같다는 보장이 없어요. 스냅샷·볼륨·과금·프로그램 자동 기동은 다루지 않아요.',
               'Docker Desktop의 Linux 엔진이 필요해요. 문제마다 서버를 준비하는 데 몇 분 걸릴 수 있어요.']
QUESTION = '멈춘 서버와 종료한 서버는 무엇이 다를까요?'

OPENINGS = ['배치한 서버를 멈추고, 다시 켜고, 없애요. 그리고 자원을 지우는 순서를 거절 메시지로 찾아요.',
            '멈춘 서버는 자리와 주소가 남고, 종료한 서버는 돌아오지 않아요. 상태가 바뀌는 데는 시간이 걸려요.',
            '모든 명령은 이 컴퓨터의 로컬 실습 API로만 가요. 실제 AWS 계정은 쓰지 않고, 직접 확인한 동작만 다뤄요.']

SOURCES = [
    dict(url='https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html', checked_at='2026-11-12',
         finding='인스턴스는 pending·running·stopping·stopped·shutting-down·terminated 상태를 거친다. 종료한 인스턴스는 다시 시작할 수 없다.',
         certainty='AWS 공식 문서의 상태 이름을 따른다. 로컬 실습에서 stop·start·terminate의 상태 변화를 실측했다.'),
    dict(url='https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html', checked_at='2026-11-12',
         finding='멈춘 인스턴스를 다시 시작하면 사설 IPv4 주소가 유지된다.',
         certainty='AWS 공식 문서 기준. 로컬 실습에서 같은 사설 주소를 관찰했다. 공인 주소는 다루지 않는다.'),
    dict(url='https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html', checked_at='2026-11-12',
         finding='user-data 셸 스크립트는 기본으로 인스턴스를 처음 시작할 때만 실행된다.',
         certainty='AWS 공식 문서 기준. 로컬 실습에서 재시작 뒤 자바 서버가 응답하지 않는 것을 관찰했다.'),
    dict(url='https://docs.aws.amazon.com/cli/latest/reference/ec2/delete-subnet.html', checked_at='2026-11-12',
         finding='서브넷을 지우려면 그 안의 실행 중인 인스턴스를 먼저 종료해야 한다. delete-vpc도 VPC 안의 서브넷 등을 먼저 지워야 한다(같은 CLI 참조).',
         certainty='AWS CLI 공식 참조 기준. 로컬 실습에서 DependencyViolation과 종료 뒤 삭제 성공을 실측했다.'),
    dict(url='https://github.com/floci-io/floci', checked_at='2026-11-12',
         finding='고정 Floci 이미지에서 stop·start·reboot·terminate의 상태 변화, 재시작 뒤 같은 사설 주소, terminated 서버의 start 거절, 서브넷·VPC 삭제 의존성을 실측했다.',
         certainty='실행 근거는 .scratch/floci-course-wayfinder/evidence/lifecycle-preflight/run-1.log에 있다. 실제 AWS의 소요 시간·과금은 주장하지 않는다.'),
]


def presentation():
    return dict(objectives=LEARN,
                chapters={c['id']: c['objectives'] for c in HIERARCHY},
                units={u['id']: dict(objectives=u['objectives'], premise=u['premise']) for c in HIERARCHY for u in c['units']},
                learning_strategy='명령 하나를 직접 입력하고 표로 상태가 바뀌는 것을 확인해요. 거절되면 오류 이름을 읽고 원인을 먼저 없애요.')


def content():
    tasks = [dict(id=s['id'], title=s['title'], goal=s['goal'], language='git', starter_code='', solution=s['solution'],
                  tests=[], required=True, narration=s['narration'], git_terminal=s['terminal']) for s in STEPS]
    return dict(description='서버를 멈추고 다시 켜고 없애며 남는 것을 확인하고, 서버 → 서브넷 → VPC 순서로 자원을 지워요.',
                presentation=presentation(), tasks=tasks)


def prd(preview):
    by_id = {s['id']: s for s in STEPS}
    chapters = [dict(id=c['id'], title=c['title'], objectives=c['objectives'],
                     units=[dict(id=u['id'], title=u['title'], objectives=u['objectives'], premise=u['premise'],
                                 steps=[dict(id=i, title=by_id[i]['title'], objectives=by_id[i]['objectives'], core_flow=by_id[i]['core'],
                                             complexity=by_id[i]['complexity']) for i in u['steps']]) for u in c['units']])
                for c in HIERARCHY]
    rep = by_id[ST[4]]
    document = dict(
        schema_version=1, id=LESSON_ID, title=TITLE, course=COURSE_ID,
        audience='첫 클라우드 수업(cloud-vpc-subnet-ec2)을 마친 자바 과정 학습자. 「클라우드」 분류의 두 번째 수업이다.',
        objectives=LEARN,
        prerequisites=['cloud-vpc-subnet-ec2', 'docker-image-container',
                       'Docker Desktop의 Linux 컨테이너 엔진(AWS CLI v2는 고정 공식 이미지로 실습 네트워크에서 실행)'],
        scope=[s['title'] for s in STEPS],
        out_of_scope=['reboot-instances(측정했지만 중지·재시작과 구별되는 관찰이 없다), 스냅샷·AMI·EBS',
                      '프로그램 자동 기동(서비스 등록·user-data 재실행 설정), 과금 실습',
                      'S3·RDS·DynamoDB·SQS·Lambda, 라우팅·IGW·NAT·NACL·보안 그룹, 실제 AWS 계정'],
        policy_snapshot=first.policy(), sources=SOURCES,
        strategy='명령은 직접 입력하고 자주 쓰는 옵션은 본문의 복사 블록으로 준다. 상태 변화는 읽기 전용 list-servers.sh 표로 반복 확인한다. '
                 '오류 수정 과제는 실행 전에 대상을 확인하거나(3) 실제 거절을 본 뒤 원인을 없앤다(5·6). 마지막 수행은 새 개념 없이 4·5를 조합한다.',
        chapters=chapters,
        grading=['채점기는 실습 소유 기록(VPC·준비 서브넷·준비 인스턴스 ID)과 실제 EC2 API 상태를 읽는다. 학생 셸 변수·명령 문자열·터미널 출력은 근거가 아니다.',
                 'pending·stopping·shutting-down은 정해진 시간 안에서 안정 상태가 될 때까지 기다려 판정한다. API가 더는 나열하지 않는 서버는 종료된 것으로 본다.',
                 '목표별로 준비 서버의 상태(stopped·running+같은 주소·terminated), 서버 서브넷 또는 VPC의 부재, 남겨 둘 서브넷·클라이언트 running, 새 서버 0대를 확인한다.',
                 '런타임 중단·준비 실패는 오답이 아니라 환경 오류다. 수명주기 목표는 준비 서버가 멈춰 있어도 환경 오류로 보지 않는다.'],
        reset=['스텝마다 소유 라벨의 새 Floci 상태에서 준비 자원을 만들고 시작 상태 설명에서 먼저 알린다. 2번은 응답을 확인한 서버를 준비 단계에서 멈춘다. 「초기화」는 이전 런타임만 정리하고 준비 파일을 되돌린다. 해설은 임시 실습 상태에서 시연한다.'],
        narration=['명령 하나의 실제 출력을 읽은 뒤 다음 행동으로 넘어간다. 기다림은 aws ec2 wait로 보여 주고, 학생에게는 표를 다시 확인하라고 한다. 실제 음성 동기화는 앱 확인이 필요하다.'],
        verification=['단위: cargo test --lib cloud_practice(목표 검증·수명주기 구성).',
                      '수업 데이터: 공개 수업 JSON의 6개 스텝을 네이티브 제출 경로(check_exercise)로 실행한다. 초기 실패, 해설 재생 통과, 대표 오답 실패를 확인한다.',
                      '빌드: build-redesigned-git --lesson, narration_review, build-redesigned-course-bundle --check, lesson_registry. 앱 파일럿과 맥 검증은 따로 기록한다.'],
        representative=dict(step_id=ST[4], prompt=rep['goal'], starter_state='VPC 10.91.0.0/16, 서브넷 A(클라이언트 running)·B(자바 서버 running).',
                            expected_action='delete-subnet의 DependencyViolation을 보고, 서브넷 B의 서버를 종료한 뒤 같은 delete-subnet을 다시 실행한다.',
                            acceptance='소유 VPC에 서브넷 B가 없고, 서브넷 A·클라이언트 running이 그대로이며 새 서버가 없다. 멈추기만 한 경우·A 삭제·클라이언트 종료는 실패한다.',
                            reset='「초기화」는 새 Floci 상태와 같은 준비 자원을 돌려준다.',
                            narration='실제 DependencyViolation을 읽고, 멈춘 서버도 자리를 차지한다는 「조심하세요」를 짚은 뒤 종료하고 다시 지운다.'),
        lesson_preview=preview,
        approval=dict(status='draft'),
        change_history=['2026-11-12 사용자 검토용 초안(.scratch/floci-course-wayfinder/second-lesson/prd.draft.md)과 사전 측정 run-1.',
                        '2026-11-12 승인 범위 안의 정식 제작: 첫 수업 피드백대로 명령은 직접 입력하고 옵션은 복사 블록으로 준다. list-servers.sh는 읽기 전용 탭이다. '
                        '자바 서버의 사설 주소는 첫 수업의 과제가 아니므로 LAB_SERVER_IP로 준다(수명주기 목표에서만).'],
    )
    return approve(document, by='Claude Code: 사용자 승인 초안에 따른 본편·해설 제작',
                   evidence='2026-11-12 사용자가 예고·PRD·대표 문제 초안(6스텝, reboot 제외 추천)을 보고 「너의 추천대로 가자」로 승인했다. '
                            '생성된 정식 JSON이나 개별 문장을 사용자가 직접 검수했다고 주장하지 않는다.')


def main():
    from curriculum_authority import alignment_source, course_intent, digest
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    course = next(c for c in catalog['courses'] if c['key'] == 'java')
    preview_public = dict(learn=LEARN, challenge=CHALLENGE, scenario=[s['title'] for s in STEPS], constraints=CONSTRAINTS, question=QUESTION)
    preview = dict(preview_public, lesson_key=KEY, lesson_id=LESSON_ID, origin='preview_first_2026-11-12',
                   course_intent_sha256=digest(course_intent(course)))
    write(FOLDER / 'lesson-preview.json', preview)
    document = prd(preview_public)
    write(FOLDER / 'approved-prd.json', document)
    (FOLDER / 'approved-prd.md').write_text(render(document) + '\n', encoding='utf-8', newline='\n')
    authored = content()
    write(FOLDER / 'content.json', authored)
    write(FOLDER / 'preview-alignment.json', dict(
        status='reviewed', source_sha256=digest(alignment_source(preview, document, authored)), reviewed_at='2026-11-12',
        reason='Claude Code가 승인 초안의 6개 실습·범위·제외 항목과 예고·PRD·본편·채점 구성을 대조했다. 사용자의 개별 원고 검수는 아니다.',
        scope='PRD 계층·전제·채점·초기화와 모든 스텝 필드(준비 파일·클라우드 구성 포함). 해설은 자체 검토 계층에서 확인한다.',
        schema_version=2))
    openings_path = ROOT / 'tools/redesigned_lessons/narration-openings.json'
    openings = json.loads(openings_path.read_text(encoding='utf-8'))
    openings[KEY] = OPENINGS
    openings_path.write_text(json.dumps(openings, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('wrote', FOLDER.relative_to(ROOT))


if __name__ == '__main__':
    main()
