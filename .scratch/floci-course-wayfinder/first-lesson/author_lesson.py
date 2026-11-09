"""Write the first Floci cloud lesson's authored sources from one reviewed definition.

The written files (tools/redesigned_lessons/cloud_vpc_subnet_ec2/*) are the canonical sources;
this script only keeps the repeated prepared files and the PRD/preview/content layers consistent.
Run from the repository root: python .scratch/floci-course-wayfinder/first-lesson/author_lesson.py
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from lesson_prd import approve, policy_revision, render  # noqa: E402

KEY = 'cloud-vpc-subnet-ec2'
FOLDER = ROOT / 'tools/redesigned_lessons/cloud_vpc_subnet_ec2'
SNAPSHOT = ROOT / '.scratch/floci-course-wayfinder/policy-snapshot'
LESSON_ID = 'lsn_9684d378-1491-4707-8911-20a7753501f9'
COURSE_ID = 'crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf'
CH = ['chp_3af90387-0f71-4688-8610-b72057a60132', 'chp_ad344928-7502-4a61-bd1e-914d051497cb',
      'chp_55714e15-1931-473d-a983-ffe27518b0eb']
UN = ['unt_a183b451-d597-4c39-8bcd-5c748bad3737', 'unt_478d3126-fd55-47cb-bb26-424d43aa333f',
      'unt_9857746a-5a77-445f-837c-ae89b09febb9', 'unt_281e9e3e-6dec-4441-b1cc-db99a39998cf']
ST = ['stp_d40503e7-fca3-4193-b103-5d6c2acac9e4', 'stp_ed72ac2b-8f2c-4e8c-a8ce-5f3bacb80b20',
      'stp_6f9ee4ee-4568-406b-a2aa-1f47b58f75a8', 'stp_02cc396f-2056-440e-ba86-12dbdc694396',
      'stp_2327dda1-9ff1-4260-ba4f-eed3fc6a13e8', 'stp_b1ee75c5-0354-426e-8e03-60ebfd7fbe9b',
      'stp_6cb45d59-91d2-4bb7-b082-06523207af50']
TERM = '#git-demo-terminal'
VPC = '10.91.0.0/16'

# -- prepared files ------------------------------------------------------------------------
def create_subnet(block):
    return ('# 준비된 VPC 안에 서브넷 하나를 만드는 명령이에요.\n'
            '# --vpc-id는 어느 VPC에, --cidr-block은 그 안의 어느 범위에 만들지 정해요.\n'
            'aws ec2 create-subnet \\\n'
            '  --endpoint-url "$LAB_ENDPOINT" \\\n'
            '  --vpc-id "$LAB_VPC_ID" \\\n'
            f'  --cidr-block {block}\n')

LIST_SUBNETS = ('# 준비된 VPC에 있는 서브넷 목록을 보여 주는 명령이에요.\n'
                'aws ec2 describe-subnets \\\n'
                '  --endpoint-url "$LAB_ENDPOINT" \\\n'
                '  --filters Name=vpc-id,Values="$LAB_VPC_ID"\n')
LIST_SERVERS = ('# 이 실습의 서버(인스턴스) 목록을 표로 보여 주는 명령이에요.\n'
                '# 열은 차례로 인스턴스 ID, 서브넷 ID, 사설 IP 주소, 상태예요.\n'
                'aws ec2 describe-instances \\\n'
                '  --endpoint-url "$LAB_ENDPOINT" \\\n'
                "  --query 'Reservations[].Instances[].[InstanceId,SubnetId,PrivateIpAddress,State.Name]' \\\n"
                '  --output table\n')
SUBNET_ID = ('# 준비된 VPC에서 주어진 범위(CIDR)의 서브넷 ID를 찾아 출력해요.\n'
             '# 사용법: bash subnet-id.sh 10.91.1.0/24\n'
             'aws ec2 describe-subnets \\\n'
             '  --endpoint-url "$LAB_ENDPOINT" \\\n'
             '  --filters Name=vpc-id,Values="$LAB_VPC_ID" Name=cidr-block,Values="$1" \\\n'
             "  --query 'Subnets[0].SubnetId' \\\n"
             "  --output text | tr -d '\\r'\n")

def launch_server(subnet, how):
    return ('# 준비된 서버 이미지로 서버(인스턴스) 한 대를 실행하는 명령이에요.\n'
            f'# {how}\n'
            '# --user-data의 파일은 서버가 켜질 때 자바 HTTP 서버를 시작해요.\n'
            'aws ec2 run-instances \\\n'
            '  --endpoint-url "$LAB_ENDPOINT" \\\n'
            '  --image-id "$LAB_SERVER_AMI" \\\n'
            '  --instance-type t3.micro \\\n'
            f'  --subnet-id {subnet} \\\n'
            '  --user-data file://server-user-data.sh\n')

LAUNCH_HOW = '--subnet-id가 서버를 놓을 서브넷을 정해요.'
LAUNCH_FIND = 'subnet-id.sh가 $( ) 안의 범위로 서브넷 ID를 찾아 --subnet-id에 넣어요.'

DESCRIBE_VPC = 'aws ec2 describe-vpcs --endpoint-url "$LAB_ENDPOINT" --vpc-ids "$LAB_VPC_ID"'
REQUEST = 'client-request "$(cat server-address.txt)"'


def terminal(step, cloud, files, editable):
    cloud = dict(cloud, editable=editable)
    snapshot = {'files': files, 'directories': [], 'cwd': ''}
    return {'initial_history': 'uninitialized', 'cloud': cloud,
            'shell': {'step_id': step, 'start': copy.deepcopy(snapshot), 'demo': copy.deepcopy(snapshot),
                      'goal': {'files': {}, 'directories': [], 'cwd': ''}, 'commands': []}}


def say(text, target):
    return {'action': 'say', 'text': text, 'target': target}


def run(command, line, fails=False, wait=60):
    action = {'action': 'bash_command', 'command': command, 'say': line, 'target': TERM, 'wait_seconds': wait}
    if fails:
        action['fails'] = True
    return action


def patch(before, after, line, file):
    return {'action': 'patch_code', 'before': before, 'after': after, 'say': line, 'file': file}


# -- steps -------------------------------------------------------------------------------
STEPS = []

STEPS.append(dict(
    id=ST[0], title='준비된 명령으로 VPC 안에 서브넷을 만드세요',
    objectives=['서브넷은 VPC 안의 더 작은 주소 범위이고, 만든 서브넷은 그 VPC에 속해요.'],
    goal='VPC는 주소 공간 하나를 선언한 자원이에요. 서브넷(subnet)은 그 VPC 안의 더 작은 주소 범위예요. 서버는 나중에 서브넷 안에 놓여요.\n\n'
         '이번 문제는 새 실습 상태에서 시작해요. 실습 환경이 범위가 10.91.0.0/16인 VPC 하나만 만들어 뒀어요. 서브넷은 아직 없어요. '
         '`LAB_ENDPOINT`는 이 컴퓨터의 로컬 실습 주소이고, `LAB_VPC_ID`는 준비된 VPC의 ID예요. 실제 AWS에는 접속하지 않아요.\n\n'
         '편집기의 `create-subnet.sh`는 이 VPC 안에 서브넷 하나를 만드는 준비 명령이에요. 이번에는 고치지 않고 그대로 실행해요. '
         '터미널 폴더의 `list-subnets.sh`는 이 VPC의 서브넷 목록을 보여 줘요.\n\n'
         '**할 일**\n\n'
         f'1. 터미널에 `{DESCRIBE_VPC}`를 입력하고 Enter를 누르세요. `CidrBlock`이 VPC의 주소 공간이에요.\n'
         '2. 터미널에 `bash list-subnets.sh`를 입력하고 Enter를 누르세요. 아직 서브넷이 없는지 확인하세요.\n'
         '3. 편집기에서 `create-subnet.sh`의 `--vpc-id`와 `--cidr-block` 값을 읽으세요.\n'
         '4. 터미널에 `bash create-subnet.sh`를 입력하고 Enter를 누르세요. 출력에서 새 서브넷의 `SubnetId`와 `CidrBlock`을 읽으세요.\n'
         '5. 터미널에 `bash list-subnets.sh`를 입력하고 Enter를 누르세요. 새 서브넷의 `VpcId`가 준비된 VPC의 ID와 같은지 확인하세요.\n'
         '6. 서브넷이 생긴 것을 확인했으면 제출 버튼을 누르세요.',
    solution='# 준비 명령을 그대로 실행해요. 준비된 VPC 안에 10.91.1.0/24 서브넷이 생겨요.\nbash create-subnet.sh\n# 목록에서 새 서브넷의 VpcId와 CidrBlock을 확인해요.\nbash list-subnets.sh',
    terminal=terminal(ST[0], {'goal': 'create_subnet', 'vpc_cidr': VPC, 'target_cidr': '10.91.1.0/24'},
                      {'create-subnet.sh': create_subnet('10.91.1.0/24'), 'list-subnets.sh': LIST_SUBNETS},
                      ['create-subnet.sh']),
    narration=[
        say('준비된 VPC는 10.91.0.0/16이고 서브넷은 아직 없어요. 먼저 그 VPC를 API로 직접 읽어 볼게요.',
            'text:실습 환경이 범위가 10.91.0.0/16인 VPC 하나만 만들어 뒀어요.'),
        run(DESCRIBE_VPC, 'describe-vpcs로 준비된 VPC를 조회해요.', wait=120),
        say('CidrBlock이 10.91.0.0/16이에요. /16이라 앞 두 칸 10.91이 이 VPC의 주소 공간을 정해요.', TERM),
        say('조심하세요. 다른 터미널의 aws에서 --endpoint-url을 빼면 실제 AWS 주소로 요청해요. 이 실습 터미널만 로컬 실습 주소로 보내 줘요.',
            'text:실제 AWS에는 접속하지 않아요.'),
        run('bash list-subnets.sh', '서브넷 목록부터 볼게요.'),
        say('Subnets가 빈 목록이에요. 이 VPC에는 아직 서브넷이 없어요.', TERM),
        say('준비 명령은 이 VPC 안의 10.91.1.0/24를 쓰겠다고 선언해요. 10.91로 시작하니 VPC 범위 안이에요.',
            'code:--cidr-block 10.91.1.0/24'),
        run('bash create-subnet.sh', '준비 명령을 그대로 실행해요.'),
        say('새 서브넷이 생겼어요. 출력의 CidrBlock은 10.91.1.0/24이고 VpcId는 준비된 VPC의 ID예요.', TERM),
        run('bash list-subnets.sh', '목록을 다시 볼게요.'),
        say('목록에도 같은 서브넷이 하나 보여요. 채점도 이 목록 같은 실제 상태를 읽어요.', TERM),
    ],
    core='수업 예고의 1·2번째 경험이다. 읽기 전용 VPC 조회(예고 1)는 채점하지 않고 이 스텝의 첫 관찰과 단원 전제로 둔다.\n\n'
         '시작: VPC 10.91.0.0/16 하나, 서브넷 0개. 준비 명령은 이미 올바른 10.91.1.0/24.\n'
         '행동: describe-vpcs로 CidrBlock을 읽고, 준비 create-subnet을 그대로 실행한 뒤 목록을 읽는다.\n'
         '관찰 근거: 새 서브넷의 VpcId·CidrBlock.\n'
         '판정: 초기 상태(서브넷 0개) 실패, 준비 명령 실행 뒤 통과. 학생이 만든 다른 VPC의 같은 CIDR은 실패.\n'
         '주의: 정상 명령 자체가 실패했다고 쓰지 않는다. 실행 전 상태가 실패이고 실행하면 통과하는 실행 과제다.',
    complexity=dict(new_concepts=['서브넷 = VPC 안의 하위 주소 범위'], prerequisite_experience='network-ip의 CIDR 범위 판단, Docker로 서버를 실행한 경험.',
                    changed_condition='고칠 값 없음. 준비 명령을 실제로 실행한다.', observable_evidence='describe-vpcs의 CidrBlock, create-subnet과 describe-subnets의 VpcId·CidrBlock.',
                    learner_edited_lines=0, new_external_services=1),
))

STEPS.append(dict(
    id=ST[1], title='범위 밖 서브넷을 VPC 안으로 고치세요',
    objectives=['VPC 범위 밖의 서브넷은 거절되고, 범위를 VPC 안으로 고치면 만들어져요.'],
    goal='서브넷은 VPC 주소 공간의 일부여야 해요. VPC 밖의 범위로는 서브넷을 만들 수 없어요.\n\n'
         '이번 문제도 새 실습 상태에서 시작해요. 앞 문제에서 만든 서브넷은 없어요. 준비된 VPC의 범위는 10.91.0.0/16이에요.\n\n'
         '편집기의 `create-subnet.sh`는 서브넷을 만드는 준비 명령인데, `--cidr-block` 값이 틀렸어요. '
         '이 VPC 안에 10.91.2.0/24 서브넷 하나를 만들어야 해요. `--endpoint-url`과 `--vpc-id`는 그대로 두세요.\n\n'
         '**할 일**\n\n'
         '1. 편집기에서 `create-subnet.sh`의 `--cidr-block` 값을 VPC 범위 10.91.0.0/16과 비교하세요.\n'
         '2. 터미널에 `bash create-subnet.sh`를 입력하고 Enter를 누르세요. 오류 메시지를 읽으세요.\n'
         '3. 터미널에 `bash list-subnets.sh`를 입력하고 Enter를 누르세요. 서브넷이 생기지 않았는지 확인하세요.\n'
         '4. 편집기에서 `--cidr-block` 값 한 곳만 `10.91.2.0/24`로 고치세요.\n'
         '5. 터미널에 `bash create-subnet.sh`를 입력하고 Enter를 누르세요. 이번 출력의 `CidrBlock`과 `VpcId`를 읽으세요.\n'
         '6. 터미널에 `bash list-subnets.sh`를 입력하고 Enter를 누르세요. 고친 범위의 서브넷이 하나 있는지 확인하세요.\n'
         '7. 고친 뒤 상태를 확인했으면 제출 버튼을 누르세요.',
    solution='# create-subnet.sh의 --cidr-block을 10.92.2.0/24에서 10.91.2.0/24로 고쳐요.\n# /16 VPC 10.91.0.0/16 안이려면 앞 두 칸이 10.91이어야 해요.\nbash create-subnet.sh\nbash list-subnets.sh',
    terminal=terminal(ST[1], {'goal': 'create_subnet', 'vpc_cidr': VPC, 'target_cidr': '10.91.2.0/24'},
                      {'create-subnet.sh': create_subnet('10.92.2.0/24'), 'list-subnets.sh': LIST_SUBNETS},
                      ['create-subnet.sh']),
    narration=[
        say('VPC는 10.91.0.0/16이고, 그 안에 10.91.2.0/24를 만들어야 해요.',
            'text:이 VPC 안에 10.91.2.0/24 서브넷 하나를 만들어야 해요.'),
        say('준비 값은 10.92.2.0/24예요. 둘째 칸이 92라서 10.91로 시작하는 VPC 밖이에요.', 'code:10.92.2.0/24'),
        run('bash create-subnet.sh', '고치기 전에 그대로 실행해 볼게요.', fails=True),
        say('InvalidSubnet.Range 오류예요. VPC 밖의 범위라서 API가 거절했어요.', TERM),
        run('bash list-subnets.sh', '거절된 뒤의 목록을 볼게요.'),
        say('Subnets가 비어 있어요. 거절된 명령은 아무것도 만들지 않았어요.', TERM),
        say('조심하세요. 끝의 2.0/24만 맞춰 보고 둘째 칸을 놓치기 쉬워요. /16 VPC 안이려면 앞 두 칸이 같아야 해요.',
            'code:10.92.2.0/24'),
        patch('--cidr-block 10.92.2.0/24', '--cidr-block 10.91.2.0/24', '92를 91로 고쳐 VPC 안의 범위로 옮겨요.', 'create-subnet.sh'),
        run('bash create-subnet.sh', '고친 명령을 실행해요.'),
        say('이번에는 서브넷이 생겼어요. CidrBlock은 10.91.2.0/24이고 VpcId는 준비된 VPC예요.', TERM),
        run('bash list-subnets.sh', '고친 뒤 목록을 확인해요.'),
        say('목록에 10.91.2.0/24 서브넷이 하나 있어요. 고친 곳은 --cidr-block 한 줄뿐이에요.', 'code:--cidr-block 10.91.2.0/24'),
        say('조심하세요. VPC를 새로 만들어 같은 숫자의 서브넷을 만들면 준비된 VPC가 아니라서 통과하지 않아요.',
            'text:--endpoint-url과 --vpc-id는 그대로 두세요.'),
    ],
    core='수업 예고의 3번째 경험이자 대표 문제다.\n\n'
         '시작: VPC 10.91.0.0/16만 있음, 서브넷 0개. 준비 명령의 CIDR이 10.92.2.0/24.\n'
         '행동: 원본 실행(InvalidSubnet.Range 거절) → --cidr-block 한 곳을 10.91.2.0/24로 수정 → 재실행 → 목록.\n'
         '관찰 근거: 원본의 실제 오류, 수정 뒤 CidrBlock·VpcId.\n'
         '판정: 준비 코드 실패, 정답 통과, 출력 위조 실패, 다른 VPC의 같은 CIDR 실패, 범위 안의 다른 CIDR 실패, 추가 서브넷 실패, 직접 명령·삭제 후 재생성 통과, VPC 10.73.0.0/16 변형 통과.\n'
         '주의: 비트 계산을 다시 가르치지 않는다.',
    complexity=dict(new_concepts=['VPC 범위 밖 서브넷의 거절'], prerequisite_experience='network-ip의 범위 안/밖 판단, 앞 스텝의 서브넷 생성.',
                    changed_condition='준비 명령의 CIDR이 VPC 밖이다.', observable_evidence='InvalidSubnet.Range 오류, 수정 뒤 CidrBlock·VpcId.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[2], title='준비된 서브넷과 겹치지 않는 범위를 고르세요',
    objectives=['같은 VPC 안의 서브넷끼리는 범위가 겹칠 수 없어요. 겹치지 않는 범위를 직접 골라요.'],
    goal='같은 VPC 안의 서브넷끼리는 범위가 겹칠 수 없어요. 범위가 VPC 안에 있어도 이미 있는 서브넷과 겹치면 거절돼요.\n\n'
         '이번 문제는 새 실습 상태에서 시작해요. 실습 환경이 VPC 10.91.0.0/16 안에 서브넷 10.91.1.0/24를 미리 만들어 뒀어요. '
         '여러분이 만든 서브넷이 아니에요. 이 서브넷의 ID는 `LAB_SUBNET_A_ID`에 있어요.\n\n'
         '편집기의 `create-subnet.sh`는 /25 서브넷 하나를 만드는 준비 명령이에요. 준비된 서브넷은 그대로 두세요. '
         'VPC 안에서 준비된 서브넷과 겹치지 않는 /25 범위 하나를 직접 골라 만드세요.\n\n'
         '**할 일**\n\n'
         '1. 터미널에 `bash list-subnets.sh`를 입력하고 Enter를 누르세요. 준비된 서브넷의 `CidrBlock`을 읽으세요.\n'
         '2. 터미널에 `bash create-subnet.sh`를 입력하고 Enter를 누르세요. 오류 메시지를 읽으세요.\n'
         '3. 편집기에서 `--cidr-block` 값 한 곳을 VPC 안이면서 준비된 서브넷과 겹치지 않는 /25 범위로 고치세요.\n'
         '4. 터미널에 `bash create-subnet.sh`를 입력하고 Enter를 누르세요. 새 서브넷의 `CidrBlock`을 읽으세요.\n'
         '5. 터미널에 `bash list-subnets.sh`를 입력하고 Enter를 누르세요. 두 서브넷의 범위가 겹치지 않는지 확인하세요.\n'
         '6. 두 서브넷을 확인했으면 제출 버튼을 누르세요.',
    solution='# create-subnet.sh의 --cidr-block을 10.91.1.128/25에서 겹치지 않는 /25로 고쳐요.\n# 예: 10.91.2.0/25. VPC 안의 다른 빈 /25도 통과해요.\nbash create-subnet.sh\nbash list-subnets.sh',
    terminal=terminal(ST[2], {'goal': 'choose_subnet', 'vpc_cidr': VPC, 'subnets': [{'name': 'A', 'cidr': '10.91.1.0/24'}], 'new_prefix': 25},
                      {'create-subnet.sh': create_subnet('10.91.1.128/25'), 'list-subnets.sh': LIST_SUBNETS},
                      ['create-subnet.sh']),
    narration=[
        say('준비된 서브넷 10.91.1.0/24는 그대로 두고, /25 서브넷을 하나 더 만드는 문제예요.',
            'text:준비된 서브넷은 그대로 두세요.'),
        run('bash list-subnets.sh', '준비된 서브넷부터 볼게요.'),
        say('10.91.1.0/24 서브넷 하나가 있어요. 10.91.1.0부터 10.91.1.255까지를 차지해요.', TERM),
        say('준비 값 10.91.1.128/25는 VPC 안이에요. 그런데 10.91.1.128부터 255까지라 기존 범위의 안쪽이에요.',
            'code:10.91.1.128/25'),
        run('bash create-subnet.sh', '그대로 실행해 볼게요.', fails=True),
        say('InvalidSubnet.Conflict 오류예요. VPC 안의 범위인데도 기존 서브넷과 겹쳐서 거절됐어요.', TERM),
        say('조심하세요. 준비된 서브넷을 지우면 겹침은 사라져요. 하지만 준비 상태가 바뀌어 통과하지 않아요.',
            'text:여러분이 만든 서브넷이 아니에요.'),
        patch('--cidr-block 10.91.1.128/25', '--cidr-block 10.91.2.0/25', '셋째 칸을 2로 바꿔 10.91.2.0/25를 골라요.', 'create-subnet.sh'),
        run('bash create-subnet.sh', '고른 범위로 다시 실행해요.'),
        say('새 서브넷 10.91.2.0/25가 생겼어요. 이번에는 거절되지 않았어요.', TERM),
        run('bash list-subnets.sh', '두 서브넷의 범위를 나란히 볼게요.'),
        say('두 서브넷이 함께 있어요. 10.91.1.x와 10.91.2.0~127은 서로 겹치지 않아요.', TERM),
        say('10.91.3.0/25처럼 VPC 안의 다른 빈 /25를 골라도 통과해요. 정답이 하나로 정해진 문제가 아니에요.',
            'text:VPC 안에서 준비된 서브넷과 겹치지 않는 /25 범위 하나를 직접 골라 만드세요.'),
    ],
    core='수업 예고의 4번째 경험이다.\n\n'
         '시작: VPC + 준비 서브넷 A 10.91.1.0/24(시작 상태 설명에서 먼저 알림). 준비 명령의 CIDR은 10.91.1.128/25.\n'
         '행동: 목록 → 원본 실행(겹침 거절) → /25 값 한 곳을 겹치지 않는 범위로 수정 → 재실행 → 목록.\n'
         '관찰 근거: 겹침 오류, 두 서브넷의 범위.\n'
         '판정: 조건 검사. 준비 서브넷 유지 + 새 /25 정확히 하나. 특정 값 하나를 고정하지 않는다. 겹침 실패, /24 실패, 두 번째 새 서브넷 실패, 준비 서브넷 삭제 실패.',
    complexity=dict(new_concepts=['같은 VPC 안 서브넷 범위의 겹침 거절'], prerequisite_experience='앞 스텝의 범위 밖 거절(안이어도 거절되는 다른 이유).',
                    changed_condition='준비 서브넷이 있고 준비 명령의 범위가 그와 겹친다.', observable_evidence='겹침 오류, 수정 뒤 두 서브넷의 CidrBlock.',
                    learner_edited_lines=1, new_external_services=0),
))

TWO_SUBNETS = [{'name': 'A', 'cidr': '10.91.1.0/24'}, {'name': 'B', 'cidr': '10.91.2.0/24'}]

STEPS.append(dict(
    id=ST[3], title='지정한 서브넷에서 서버 한 대를 실행하세요',
    objectives=['서버(인스턴스)는 지정한 서브넷에 놓이고, 그 서브넷 범위에서 사설 IP 주소를 받아요.'],
    goal='인스턴스(instance)는 서브넷 하나에 놓이는 서버 자원이에요. 서버의 사설 IP 주소는 그 서브넷의 범위에서 받아요.\n\n'
         '이번 문제는 새 실습 상태에서 시작해요. 실습 환경이 VPC 10.91.0.0/16 안에 서브넷 A 10.91.1.0/24와 서브넷 B 10.91.2.0/24를 미리 만들어 뒀어요. '
         '두 서브넷의 ID는 `LAB_SUBNET_A_ID`와 `LAB_SUBNET_B_ID`에 있어요. 아직 서버는 없어요.\n\n'
         '편집기의 `launch-server.sh`는 서브넷 B에 서버 한 대를 실행하는 준비 명령이에요. 이번에는 고치지 않고 그대로 실행해요. '
         '`list-servers.sh`는 서버의 ID·서브넷 ID·사설 IP 주소·상태를 표로 보여 줘요.\n\n'
         '**할 일**\n\n'
         '1. 편집기에서 `launch-server.sh`의 `--subnet-id` 값을 읽으세요.\n'
         '2. 터미널에 `bash launch-server.sh`를 입력하고 Enter를 누르세요. 출력의 `SubnetId`와 `PrivateIpAddress`를 읽으세요.\n'
         '3. 터미널에 `bash list-servers.sh`를 입력하고 Enter를 누르세요. 서버의 상태를 읽으세요.\n'
         '4. 상태가 `running`이 아니면 잠시 뒤 `bash list-servers.sh`를 다시 실행하세요.\n'
         '5. 사설 IP 주소가 서브넷 B의 범위 10.91.2.0/24 안인지 확인하세요.\n'
         '6. 서버가 `running`인 것을 확인했으면 제출 버튼을 누르세요.',
    solution='# 준비 명령을 그대로 실행해요. 서버가 서브넷 B에 놓여요.\nbash launch-server.sh\n# 상태가 running이 될 때까지 표를 다시 확인해요.\nbash list-servers.sh',
    terminal=terminal(ST[3], {'goal': 'launch_server', 'vpc_cidr': VPC, 'subnets': TWO_SUBNETS, 'target_subnet': 'B'},
                      {'launch-server.sh': launch_server('"$LAB_SUBNET_B_ID"', LAUNCH_HOW), 'list-servers.sh': LIST_SERVERS, 'list-subnets.sh': LIST_SUBNETS},
                      ['launch-server.sh']),
    narration=[
        say('서버는 서브넷 하나에 놓이고, 주소도 그 서브넷의 범위에서 받아요.',
            'text:서버의 사설 IP 주소는 그 서브넷의 범위에서 받아요.'),
        say('준비 명령은 서브넷 B의 ID를 써요. 서브넷 B의 범위는 10.91.2.0/24예요.', 'code:"$LAB_SUBNET_B_ID"'),
        run('bash launch-server.sh', '준비 명령을 그대로 실행해요.', wait=240),
        say('요청이 받아들여졌어요. PrivateIpAddress가 10.91.2로 시작하고, 출력의 상태는 아직 pending이에요.', TERM),
        run('bash list-servers.sh', '표로 서버의 상태를 볼게요.'),
        say('상태 칸을 보세요. pending이면 아직 켜지는 중이고, running이면 다 켜진 거예요.', TERM),
        say('조심하세요. 실행 요청이 성공한 것과 서버가 다 켜진 것은 달라요. running을 확인한 뒤 제출하세요.',
            'text:상태가 running이 아니면 잠시 뒤 bash list-servers.sh를 다시 실행하세요.'),
        run('aws ec2 wait instance-running --endpoint-url "$LAB_ENDPOINT" --filters Name=subnet-id,Values="$LAB_SUBNET_B_ID"',
            '해설은 running이 될 때까지 기다리는 명령을 써요.', wait=300),
        run('bash list-servers.sh', '기다린 뒤 다시 표를 볼게요.'),
        say('이제 running이에요. 사설 IP 주소가 서브넷 B의 범위 10.91.2.0/24 안에 있어요.', TERM),
    ],
    core='수업 예고의 5번째 경험이다. EC2 게스트를 처음 쓴다.\n\n'
         '시작: VPC, 준비 서브넷 A·B, 인스턴스 0개. 준비 명령은 --subnet-id "$LAB_SUBNET_B_ID".\n'
         '행동: 준비 run-instances 실행 → list-servers로 상태 확인(running까지).\n'
         '관찰 근거: SubnetId, PrivateIpAddress(10.91.2.x), pending→running.\n'
         '판정: 초기 상태(서버 0대) 실패, 준비 명령 실행 뒤 통과. 채점은 pending이면 정해진 시간 안에서 기다린다.\n'
         '주의: API running과 HTTP 준비는 다르다. 이 스텝은 HTTP를 채점하지 않는다.',
    complexity=dict(new_concepts=['인스턴스 = 서브넷에 놓이는 서버 자원'], prerequisite_experience='Docker로 이미지에서 서버를 띄운 경험, 1장의 서브넷.',
                    changed_condition='고칠 값 없음. 준비 서브넷 두 개와 서버 이미지가 있다.', observable_evidence='run-instances의 SubnetId·PrivateIpAddress, 표의 상태.',
                    learner_edited_lines=0, new_external_services=0),
))

STEPS.append(dict(
    id=ST[4], title='엉뚱한 서브넷에 놓이는 명령을 고치세요',
    objectives=['같은 VPC 안에서도 어느 서브넷을 고르느냐가 서버의 자리와 주소를 정해요.'],
    goal='같은 VPC 안에서도 어느 서브넷에 놓느냐에 따라 서버의 자리와 주소가 달라져요.\n\n'
         '이번 문제는 새 실습 상태에서 시작해요. 앞 문제처럼 실습 환경이 VPC 10.91.0.0/16과 서브넷 A 10.91.1.0/24, 서브넷 B 10.91.2.0/24를 미리 만들어 뒀어요. 아직 서버는 없어요.\n\n'
         '서버를 10.91.2.0/24에 놓아야 해요. 그런데 편집기의 `launch-server.sh`는 다른 서브넷을 가리켜요. '
         '처음 명령으로 만든 서버가 남아 있으면 통과하지 않아요. 결과를 확인한 뒤 「초기화」로 처음 상태를 받고 고치세요.\n\n'
         '**할 일**\n\n'
         '1. 터미널에 `bash launch-server.sh`를 입력하고 Enter를 누르세요.\n'
         '2. 터미널에 `bash list-servers.sh`를 입력하고 Enter를 누르세요. 서버의 사설 IP 주소가 어느 서브넷 범위에 있는지 확인하세요.\n'
         '3. 「초기화」를 눌러 서버가 없는 처음 상태로 돌아가세요.\n'
         '4. 편집기에서 `launch-server.sh`의 `--subnet-id` 값 한 곳을 목표 서브넷의 변수로 고치세요.\n'
         '5. 터미널에 `bash launch-server.sh`를 입력하고 Enter를 누르세요.\n'
         '6. 터미널에 `bash list-servers.sh`를 입력하고 Enter를 누르세요. 서버가 한 대이고 사설 IP 주소가 10.91.2.0/24 안인지 확인하세요.\n'
         '7. 상태가 `running`인 것을 확인했으면 제출 버튼을 누르세요.',
    solution='# 처음 명령은 서브넷 A에 놓여요. 「초기화」로 처음 상태를 받은 뒤 고쳐요.\n# launch-server.sh의 --subnet-id를 "$LAB_SUBNET_A_ID"에서 "$LAB_SUBNET_B_ID"로 고쳐요.\nbash launch-server.sh\nbash list-servers.sh',
    terminal=terminal(ST[4], {'goal': 'launch_server', 'vpc_cidr': VPC, 'subnets': TWO_SUBNETS, 'target_subnet': 'B'},
                      {'launch-server.sh': launch_server('"$LAB_SUBNET_A_ID"', LAUNCH_HOW), 'list-servers.sh': LIST_SERVERS, 'list-subnets.sh': LIST_SUBNETS},
                      ['launch-server.sh']),
    narration=[
        say('목표 자리는 10.91.2.0/24, 곧 서브넷 B예요.', 'text:서버를 10.91.2.0/24에 놓아야 해요.'),
        say('준비 명령은 서브넷 A의 ID를 써요.', 'code:"$LAB_SUBNET_A_ID"'),
        run('bash list-subnets.sh', '두 서브넷의 ID와 범위를 볼게요.'),
        say('서브넷 A는 10.91.1.0/24, B는 10.91.2.0/24예요. 같은 VPC 안의 다른 범위예요.', TERM),
        say('조심하세요. 그대로 실행하면 서버가 서브넷 A에 놓여요. 그 서버를 남긴 채 B에 하나 더 띄우면 두 대라서 통과하지 않아요.',
            'text:처음 명령으로 만든 서버가 남아 있으면 통과하지 않아요.'),
        say('여러분은 처음 명령을 한 번 실행해 10.91.1로 시작하는 주소를 직접 보세요. 그다음 「초기화」로 서버를 없애요.',
            'text:「초기화」를 눌러 서버가 없는 처음 상태로 돌아가세요.'),
        say('해설 화면에는 「초기화」가 없어요. 그래서 처음 명령은 실행하지 않고 바로 고칠게요.',
            'text:결과를 확인한 뒤 「초기화」로 처음 상태를 받고 고치세요.'),
        patch('"$LAB_SUBNET_A_ID"', '"$LAB_SUBNET_B_ID"', '서브넷 변수 한 곳을 B로 고쳐요.', 'launch-server.sh'),
        run('bash launch-server.sh', '고친 명령으로 서버를 실행해요.', wait=240),
        say('출력의 PrivateIpAddress가 10.91.2로 시작해요. 서브넷 B의 범위에서 받은 주소예요.', TERM),
        run('aws ec2 wait instance-running --endpoint-url "$LAB_ENDPOINT" --filters Name=subnet-id,Values="$LAB_SUBNET_B_ID"',
            '서버가 다 켜질 때까지 기다려요.', wait=300),
        run('bash list-servers.sh', '서버 표를 확인해요.'),
        say('서버가 한 대이고 서브넷 B에서 running이에요. 바꾼 것은 서브넷 변수 하나예요.', TERM),
    ],
    core='수업 예고의 6번째 경험이다.\n\n'
         '시작: 앞 스텝과 같은 VPC·서브넷, 인스턴스 0개. 준비 명령은 --subnet-id "$LAB_SUBNET_A_ID". 목표는 10.91.2.0/24.\n'
         '행동: 원본 실행 → 10.91.1.x 관찰 → 「초기화」로 독립 초기 상태 복원 → 서브넷 변수 한 곳 수정 → 재실행.\n'
         '관찰 근거: 원본의 10.91.1.x, 수정 뒤 10.91.2.x.\n'
         '판정: 준비 명령 실패(목표 서브넷이 아닌 곳), 초기화 뒤 초기 실패, 수정 통과, A 서버를 남기면 두 대라 실패.\n'
         '주의: 종료 명령을 가르치지 않는다. 해설 시연에는 초기화가 없으므로 처음 명령을 실행하지 않고 말로 짚는다(해설 재생이 시작 상태에서 목표에 도달해야 한다).',
    complexity=dict(new_concepts=['같은 VPC 안 서브넷 선택이 서버의 자리를 정한다'], prerequisite_experience='앞 스텝의 인스턴스 조회와 사설 IP 범위 판단.',
                    changed_condition='준비 명령이 목표가 아닌 서브넷 A를 가리킨다.', observable_evidence='처음 10.91.1.x, 수정 뒤 10.91.2.x와 서버 한 대.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[5], title='다른 서브넷의 서버에 사설 주소로 요청하세요',
    objectives=['같은 VPC 안에서는 API가 알려 준 사설 IP 주소로 다른 서브넷의 서버에 요청할 수 있어요.'],
    goal='같은 VPC 안의 서버끼리는 사설 IP 주소로 연결해요. 연결할 주소는 API가 알려 준 서버의 사설 IP 주소예요.\n\n'
         '이번 문제는 새 실습 상태에서 시작해요. 실습 환경이 서브넷 A 10.91.1.0/24에 클라이언트 서버를, 서브넷 B 10.91.2.0/24에 자바 HTTP 서버를 미리 실행해 뒀어요. '
         '두 서버의 ID는 `LAB_CLIENT_ID`와 `LAB_SERVER_ID`에 있어요.\n\n'
         '`client-request <IPv4 주소>`는 클라이언트 서버 안에서 그 주소의 8080 포트로 HTTP 요청을 보내요. '
         '편집기의 `server-address.txt`에는 요청할 주소가 한 줄 있는데, 아직 서버의 주소가 아니에요. 이 파일의 주소를 서버의 사설 IP 주소로 고치세요.\n\n'
         '**할 일**\n\n'
         f'1. 터미널에 `{REQUEST}`를 입력하고 Enter를 누르세요. 결과를 읽으세요.\n'
         '2. 터미널에 `echo "$LAB_SERVER_ID"`를 입력하고 Enter를 누르세요. 서버의 ID를 읽으세요.\n'
         '3. 터미널에 `bash list-servers.sh`를 입력하고 Enter를 누르세요. 그 ID인 서버의 사설 IP 주소를 읽으세요.\n'
         '4. 편집기에서 `server-address.txt`의 주소를 그 사설 IP 주소로 고치세요.\n'
         f'5. 터미널에 `{REQUEST}`를 입력하고 Enter를 누르세요. 응답의 `served-on`과 `from`을 읽으세요.\n'
         '6. 응답을 확인했으면 제출 버튼을 누르세요.',
    solution='# list-servers.sh 표에서 LAB_SERVER_ID 서버의 사설 IP 주소를 읽어 server-address.txt에 적어요.\n# 클라이언트 서버 안에서 그 주소로 요청해요.\nclient-request "$(cat server-address.txt)"',
    terminal=terminal(ST[5], {'goal': 'request_server', 'vpc_cidr': VPC, 'subnets': TWO_SUBNETS, 'client_subnet': 'A',
                              'server_subnet': 'B', 'address_file': 'server-address.txt'},
                      {'server-address.txt': '10.91.2.99\n', 'list-servers.sh': LIST_SERVERS, 'list-subnets.sh': LIST_SUBNETS},
                      ['server-address.txt']),
    narration=[
        say('요청은 서브넷 A의 클라이언트에서 출발해요. 서브넷 B에 있는 서버의 주소를 알아내는 게 핵심이에요.',
            'text:연결할 주소는 API가 알려 준 서버의 사설 IP 주소예요.'),
        say('파일의 10.91.2.99는 서브넷 B의 범위 안이에요. 하지만 서버가 받은 주소인지는 아직 몰라요.', 'code:10.91.2.99'),
        run(REQUEST, '지금 파일의 주소로 요청해 볼게요.', fails=True),
        say('CONNECT_FAIL이에요. 10.91.2.99에는 응답하는 서버가 없어서 연결 시간이 지났어요.', TERM),
        run('echo "$LAB_SERVER_ID"', '서버의 ID부터 확인해요.'),
        say('이 ID가 서브넷 B의 자바 서버예요.', TERM),
        run('bash list-servers.sh', '서버 표를 볼게요.'),
        say('서버가 두 대예요. 그 ID의 줄에서 10.91.2로 시작하는 사설 IP 주소를 읽어요.', TERM),
        say('해설은 그 주소를 aws 명령으로 파일에 옮겨 적을게요. 여러분은 편집기에 직접 적으면 돼요.',
            'text:편집기에서 server-address.txt의 주소를 그 사설 IP 주소로 고치세요.'),
        run('aws ec2 describe-instances --endpoint-url "$LAB_ENDPOINT" --instance-ids "$LAB_SERVER_ID" '
            "--query 'Reservations[0].Instances[0].PrivateIpAddress' --output text > server-address.txt",
            'API가 알려 준 서버의 사설 주소를 파일에 적어요.'),
        say('편집기의 server-address.txt가 표에서 읽은 주소로 바뀌었어요.', 'editor'),
        run(REQUEST, '고친 주소로 다시 요청해요.', wait=120),
        say('200 OK 응답이에요. served-on은 서버의 사설 주소이고, from은 클라이언트의 주소예요.', TERM),
        say('from이 10.91.1로 시작해요. 서브넷 A의 클라이언트가 같은 VPC의 서브넷 B 서버에 닿았어요.', TERM),
        say('조심하세요. 표에는 클라이언트 줄도 있어요. 10.91.1로 시작하는 클라이언트 주소를 적으면 연결도 채점도 실패해요.',
            'text:이 파일의 주소를 서버의 사설 IP 주소로 고치세요.'),
    ],
    core='수업 예고의 7번째 경험이다.\n\n'
         '시작: VPC, 서브넷 A·B, 서브넷 B의 자바 서버, 서브넷 A의 준비 클라이언트(모두 준비 스크립트가 만듦). 주소 파일은 10.91.2.99.\n'
         '행동: 원본 주소로 요청(실패) → 서버 ID 확인 → 표에서 사설 주소 읽기 → 주소 파일 한 곳 수정 → client-request.\n'
         '관찰 근거: HTTP 응답의 instance·served-on·from·java.version.\n'
         '판정: 주소 파일 = 서버 API 사설 주소이고 채점기가 소유 클라이언트에서 직접 요청한 응답의 신원이 맞아야 한다. 자리표시 주소 실패, 같은 서버의 Docker 주소 실패, 응답 출력 위조 실패.\n'
         '주의: 다른 VPC로의 차단·라우팅 표·NACL·보안 그룹은 가르치지 않는다.',
    complexity=dict(new_concepts=['API가 알려 준 사설 주소 = 같은 VPC에서 연결할 주소'], prerequisite_experience='network-http의 요청·응답 읽기, network-routing의 다른 네트워크 구별, 앞 스텝의 사설 IP.',
                    changed_condition='주소 파일이 서버의 주소가 아니다.', observable_evidence='client-request의 연결 실패와 200 응답의 served-on·from.',
                    learner_edited_lines=1, new_external_services=0),
))

STEPS.append(dict(
    id=ST[6], title='자바 서버를 10.91.2.0/24에 배치하세요',
    objectives=['새 개념 없이 범위·자리·주소 판단을 조합해 자바 서버를 원하는 서브넷에 배치하고 응답을 받아요.'],
    goal='지금까지 확인한 범위·자리·주소를 한 번에 써요. 새로 배울 것은 없어요.\n\n'
         '이번 문제는 새 실습 상태에서 시작해요. 실습 환경이 VPC 10.91.0.0/16에 서브넷 A 10.91.1.0/24와 그 안의 클라이언트 서버만 미리 만들어 뒀어요. '
         '목표 서브넷 10.91.2.0/24는 아직 없어요. 새 서브넷에는 준비된 ID 변수가 없어요. 그래서 `launch-server.sh`는 `subnet-id.sh`로 범위에 맞는 서브넷 ID를 찾아요.\n\n'
         '서브넷 10.91.2.0/24를 만들고, 그 안에 준비된 자바 HTTP 서버 한 대를 실행하세요. 그리고 서브넷 A의 클라이언트에서 그 서버의 사설 IP 주소로 응답을 받으세요. '
         '편집기의 세 파일에는 아직 맞지 않는 값이 한 곳씩 있어요. 서버가 엉뚱한 자리에 생기면 「초기화」로 처음 상태를 받으세요.\n\n'
         '**할 일**\n\n'
         '1. 편집기에서 `create-subnet.sh`의 `--cidr-block` 값을 목표 범위로 고치세요.\n'
         '2. 터미널에 `bash create-subnet.sh`를 입력하고 Enter를 누르세요. 새 서브넷의 `CidrBlock`을 확인하세요.\n'
         '3. 편집기에서 `launch-server.sh`의 `subnet-id.sh` 뒤 범위를 새 서브넷의 범위로 고치세요.\n'
         '4. 터미널에 `bash launch-server.sh`를 입력하고 Enter를 누르세요. 출력의 `PrivateIpAddress`를 읽으세요.\n'
         '5. 터미널에 `bash list-servers.sh`를 입력하고 Enter를 누르세요. 새 서버가 `running`인지 확인하세요.\n'
         '6. 편집기에서 `server-address.txt`의 주소를 새 서버의 사설 IP 주소로 고치세요.\n'
         f'7. 터미널에 `{REQUEST}`를 입력하고 Enter를 누르세요. 연결에 실패하면 잠시 뒤 다시 실행하세요.\n'
         '8. 응답의 `served-on`과 `from`을 확인했으면 제출 버튼을 누르세요.',
    solution='# create-subnet.sh의 --cidr-block을 10.91.2.0/24로 고쳐 목표 서브넷을 만들어요.\nbash create-subnet.sh\n'
             '# launch-server.sh의 subnet-id.sh 뒤 범위를 10.91.2.0/24로 고쳐 새 서브넷에 서버를 실행해요.\nbash launch-server.sh\n'
             '# 새 서버의 사설 IP 주소를 server-address.txt에 적고, 서브넷 A의 클라이언트에서 요청해요.\nclient-request "$(cat server-address.txt)"',
    terminal=terminal(ST[6], {'goal': 'deploy_server', 'vpc_cidr': VPC, 'subnets': [{'name': 'A', 'cidr': '10.91.1.0/24'}],
                              'client_subnet': 'A', 'target_cidr': '10.91.2.0/24', 'address_file': 'server-address.txt'},
                      {'create-subnet.sh': create_subnet('10.91.1.0/24'),
                       'launch-server.sh': launch_server('"$(bash subnet-id.sh 10.91.1.0/24)"', LAUNCH_FIND),
                       'server-address.txt': '0.0.0.0\n', 'subnet-id.sh': SUBNET_ID,
                       'list-servers.sh': LIST_SERVERS, 'list-subnets.sh': LIST_SUBNETS},
                      ['create-subnet.sh', 'launch-server.sh', 'server-address.txt']),
    narration=[
        say('범위는 1장, 자리는 서브넷 선택, 주소는 요청 문제에서 확인했어요. 이번에는 셋을 이어서 써요.',
            'text:지금까지 확인한 범위·자리·주소를 한 번에 써요.'),
        say('준비 값 10.91.1.0/24는 서브넷 A와 같은 범위라 겹쳐요.', 'code:--cidr-block 10.91.1.0/24'),
        patch('--cidr-block 10.91.1.0/24', '--cidr-block 10.91.2.0/24', '목표 범위 10.91.2.0/24로 고쳐요.', 'create-subnet.sh'),
        run('bash create-subnet.sh', '목표 서브넷을 만들어요.'),
        say('10.91.2.0/24 서브넷이 생겼어요. 이 서브넷의 ID는 준비된 변수에 없어요.', TERM),
        patch('subnet-id.sh 10.91.1.0/24', 'subnet-id.sh 10.91.2.0/24', '서버를 놓을 자리를 새 서브넷의 범위로 고쳐요.', 'launch-server.sh'),
        say('subnet-id.sh가 이 범위로 새 서브넷의 ID를 찾아 --subnet-id에 넣어요.', 'code:subnet-id.sh 10.91.2.0/24'),
        say('조심하세요. 서브넷만 만들고 이 범위를 10.91.1.0/24로 두면 서버가 클라이언트와 같은 서브넷 A에 놓여요.',
            'text:서버가 엉뚱한 자리에 생기면 「초기화」로 처음 상태를 받으세요.'),
        run('bash launch-server.sh', '자바 서버를 새 서브넷에 실행해요.', wait=240),
        say('PrivateIpAddress가 10.91.2로 시작해요. 새 서브넷의 범위에서 주소를 받았어요.', TERM),
        run('aws ec2 wait instance-running --endpoint-url "$LAB_ENDPOINT" --filters Name=subnet-id,Values="$(bash subnet-id.sh 10.91.2.0/24)"',
            '서버가 running이 될 때까지 기다릴게요.', wait=300),
        run('bash list-servers.sh', '서버 표를 볼게요.'),
        say('새 서버가 10.91.2 주소로 running이에요. 클라이언트는 10.91.1 주소예요.', TERM),
        run('aws ec2 describe-instances --endpoint-url "$LAB_ENDPOINT" --filters Name=subnet-id,Values="$(bash subnet-id.sh 10.91.2.0/24)" '
            "--query 'Reservations[0].Instances[0].PrivateIpAddress' --output text > server-address.txt",
            '표에서 읽은 새 서버의 주소를 파일에 옮겨 적어요.'),
        say('server-address.txt에 새 서버의 사설 주소가 들어갔어요.', 'editor'),
        say('조심하세요. running은 API가 본 상태예요. 자바 프로그램이 요청을 받을 준비가 됐다는 뜻은 아니에요.',
            'text:연결에 실패하면 잠시 뒤 다시 실행하세요.'),
        run(f'until {REQUEST}; do sleep 3; done', '응답이 올 때까지 같은 요청을 다시 보내요.', wait=240),
        say('CONNECT_FAIL 줄은 자바 프로그램이 아직 켜지는 중이었다는 뜻이에요. 그 뒤에 200 OK 응답이 왔어요.', TERM),
        say('served-on은 10.91.2로, from은 10.91.1로 시작해요.', TERM),
        say('서브넷 A의 클라이언트가 새 서브넷의 자바 서버에서 응답을 받았어요.', 'text:그리고 서브넷 A의 클라이언트에서 그 서버의 사설 IP 주소로 응답을 받으세요.'),
    ],
    core='수업 예고의 8번째 경험이자 마지막 수행이다. 새 개념 없음.\n\n'
         '시작: VPC 10.91.0.0/16, 준비 서브넷 A와 클라이언트. 목표 서브넷 10.91.2.0/24는 없음(B ID 변수를 가정하지 않는다). '
         '세 파일에 한 곳씩: create-subnet.sh 10.91.1.0/24(A와 겹침), launch-server.sh의 subnet-id.sh 10.91.1.0/24(A), server-address.txt 0.0.0.0.\n'
         '행동: CIDR → 서버 자리 범위 → 요청 주소를 각각 한 곳씩 고치고 실행한다.\n'
         '관찰 근거: 새 서브넷, 10.91.2.x 서버, 클라이언트에서 받은 자바 서버 응답.\n'
         '판정: 새 서브넷 10.91.2.0/24 하나 + 그 안의 서버 한 대 + 주소 파일 일치 + 채점기 HTTP 신원 확인. 서브넷 A 배치 실패, 응답 출력 위조 실패.\n'
         '주의: API running과 HTTP 준비를 구별한다. 해설은 주소를 aws 명령으로 옮겨 적는다(동적 값).',
    complexity=dict(new_concepts=[], prerequisite_experience='1장 서브넷 생성, 2장 배치와 요청.',
                    changed_condition='목표 서브넷이 없고 세 파일의 값이 한 곳씩 맞지 않는다.', observable_evidence='새 서브넷의 CidrBlock, 서버의 10.91.2.x 주소, 200 응답의 served-on·from.',
                    learner_edited_lines=3, new_external_services=0),
))

# -- hierarchy ---------------------------------------------------------------------------
HIERARCHY = [
    dict(id=CH[0], title='주소 공간 안에 서브넷을 선언해요',
         objectives=['VPC 범위 안에서 겹치지 않는 서브넷을 만들고, 범위 밖·겹침이 거절되는 것을 확인해요.'],
         units=[dict(id=UN[0], title='VPC 안에 서브넷 만들기', steps=ST[0:3],
                     objectives=['서브넷이 VPC 범위의 일부여야 하고, 같은 VPC 안에서 겹칠 수 없다는 규칙을 생성 성공과 거절로 확인해요.'],
                     premise='실습 환경이 VPC 하나를 미리 만들어 둬요. VPC는 주소 공간 하나를 선언한 자원이고, 범위는 10.91.0.0/16이에요. '
                             '문제마다 새 실습 상태에서 시작해요. 모든 aws 명령은 이 컴퓨터의 로컬 실습 주소로만 가요.')]),
    dict(id=CH[1], title='서버 한 대를 서브넷에 놓아요',
         objectives=['서버는 서브넷 하나에 놓이고, 그 범위에서 사설 IP 주소를 받아요.',
                     '같은 VPC의 다른 서브넷에서 그 사설 주소로 HTTP 응답을 받아요.'],
         units=[dict(id=UN[1], title='서버의 자리는 서브넷이에요', steps=ST[3:5],
                     objectives=['run-instances의 서브넷 지정과 결과 서버의 서브넷·사설 IP 주소의 관계를 읽어요.'],
                     premise='실습 환경이 VPC 10.91.0.0/16에 서브넷 A 10.91.1.0/24와 서브넷 B 10.91.2.0/24를 미리 만들어 둬요. '
                             '서버 이미지는 network-http처럼 ServerSocket으로 응답하는 작은 자바 HTTP 서버예요. 서버를 준비하는 데 몇 분 걸릴 수 있어요.'),
                dict(id=UN[2], title='같은 VPC 안에서 서버에 요청해요', steps=ST[5:6],
                     objectives=['API가 알려 준 사설 주소로 같은 VPC의 다른 서버가 실제 HTTP 응답을 받아요.'],
                     premise='실습 환경이 서브넷 B의 자바 서버와 서브넷 A의 클라이언트 서버를 미리 실행해 둬요. '
                             'client-request는 클라이언트 서버 안에서 HTTP 요청을 보내요. 이 수업은 같은 VPC 안의 연결만 확인해요.')]),
    dict(id=CH[2], title='자바 서버를 원하는 자리에 배치해요',
         objectives=['앞에서 확인한 범위·자리·주소를 조합해 자바 서버를 지정한 서브넷에 배치하고 응답을 받아요.'],
         units=[dict(id=UN[3], title='마지막 수행', steps=ST[6:7],
                     objectives=['새 개념 없이 1·2장의 판단을 조합해요.'],
                     premise='VPC와 서브넷 A, 서브넷 A의 클라이언트 서버만 준비돼 있어요. 목표 서브넷은 직접 만들어요.')]),
]

LEARN = ['이미 아는 CIDR로 VPC와 서브넷의 포함 관계를 읽고 선언해요.',
         '서버 한 대를 원하는 서브넷에 놓고, 받은 주소가 그 범위 안인지 확인해요.',
         '같은 VPC 안의 다른 서버에서 그 주소로 HTTP 응답을 받아 배치를 확인해요.']
CHALLENGE = ('준비된 VPC 10.91.0.0/16 안에 서브넷 10.91.2.0/24를 만들고 준비된 자바 HTTP 서버 한 대를 배치하세요. '
             '같은 VPC의 다른 서브넷에 있는 클라이언트에서 그 사설 주소로 응답을 받아야 해요.')
CONSTRAINTS = ['자바 과정의 네트워크·Docker 수업을 마쳤다고 가정해요. CIDR 계산과 Docker 기초는 다시 배우지 않아요.',
               '모든 aws 명령은 이 컴퓨터의 로컬 실습 주소로만 가요. 실제 AWS 계정은 쓰지 않아요.',
               '문제마다 새 실습 상태에서 시작해요. 앞 문제의 결과가 이어지지 않아요.',
               '로컬 실습 환경은 실제 AWS와 같다는 보장이 없어요. 라우팅 표·NAT·NACL·피어링·보안 그룹은 다루지 않아요.',
               'Docker Desktop의 Linux 엔진과 AWS CLI v2가 필요해요. 서버 문제는 준비에 몇 분 걸릴 수 있어요.']
QUESTION = 'VPC 범위 밖의 서브넷은 왜 만들 수 없을까요?'

OPENINGS = ['이미 아는 CIDR로 VPC와 서브넷의 관계를 확인하고, 서버 한 대를 원하는 서브넷에 배치해요.',
            '서브넷을 만들고, 범위 밖과 겹침이 거절되는 것을 봐요. 그다음 서버의 자리를 정하고 다른 서브넷에서 요청해요.',
            '모든 명령은 이 컴퓨터의 로컬 실습 API로만 가요. 실제 AWS 계정은 쓰지 않고, 직접 확인한 동작만 다뤄요.']

SOURCES = [
    dict(url='https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html', checked_at='2026-11-10',
         finding='서브넷 CIDR은 VPC CIDR과 같거나 그 일부이고, 한 VPC의 서브넷 CIDR은 겹칠 수 없다. 각 서브넷의 처음 네 주소와 마지막 주소는 예약된다.',
         certainty='AWS 공식 문서를 열어 문장을 확인했다. 예약 주소는 이 수업에서 가르치지 않는다.'),
    dict(url='https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html', checked_at='2026-11-10',
         finding='VPC IPv4 CIDR은 /16에서 /28 사이다.', certainty='AWS 공식 문서를 열어 확인했다. 실습 VPC는 /16이다.'),
    dict(url='https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html', checked_at='2026-11-10',
         finding='인스턴스는 서브넷의 CIDR 범위에서 사설 IPv4 주소를 받고, 같은 VPC의 인스턴스끼리 사설 주소로 통신할 수 있다.',
         certainty='AWS 공식 문서를 열어 확인했다. 로컬 실습에서는 같은 VPC의 다른 서브넷 HTTP 응답만 실측했다.'),
    dict(url='https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html', checked_at='2026-11-10',
         finding='인스턴스는 시작할 때 pending 상태를 거친다.', certainty='AWS 공식 문서를 열어 확인했다. 수명주기의 나머지는 다음 수업 범위다.'),
    dict(url='https://docs.aws.amazon.com/cli/latest/reference/ec2/create-subnet.html', checked_at='2026-11-10',
         finding='create-subnet은 --vpc-id와 --cidr-block을 받는다. run-instances의 --subnet-id는 인스턴스를 실행할 서브넷이다(같은 CLI 참조).',
         certainty='AWS CLI 공식 참조를 열어 확인했다.'),
    dict(url='https://github.com/floci-io/floci', checked_at='2026-11-10',
         finding='Floci는 로컬 AWS 에뮬레이터다. 고정 이미지에서 VPC·서브넷 생성·조회, 범위 밖·겹침 거절, 실제 EC2 게스트의 사설 주소와 같은 VPC HTTP 응답을 실측했다.',
         certainty='저장소를 열어 확인했다. 실행 근거는 docs/floci-first-lesson-preflight.md와 docs/floci-cloud-native-runtime.md에 따로 있다. 라우팅·NACL·NAT·피어링·보안 그룹의 AWS 동등성은 입증하지 않았다.'),
]


def presentation():
    return dict(objectives=LEARN,
                chapters={c['id']: c['objectives'] for c in HIERARCHY},
                units={u['id']: dict(objectives=u['objectives'], premise=u['premise']) for c in HIERARCHY for u in c['units']},
                learning_strategy='먼저 준비 명령을 실행해 실제 API 결과를 봐요. 편집기에서 값 한 곳만 고치고 같은 명령으로 다시 확인해요.')


def content():
    tasks = []
    for s in STEPS:
        tasks.append(dict(id=s['id'], title=s['title'], goal=s['goal'], language='git', starter_code='', solution=s['solution'],
                          tests=[], required=True, narration=s['narration'], git_terminal=s['terminal']))
    return dict(description='VPC와 서브넷의 범위를 선언하고, 서버를 원하는 서브넷에 놓아 같은 VPC에서 응답을 받아요.',
                presentation=presentation(), tasks=tasks)


def policy():
    artifacts = [dict(path='docs/content-rules.md', text=(SNAPSHOT / 'content-rules.md').read_text(encoding='utf-8')),
                 dict(path='docs/voice.md', text=(SNAPSHOT / 'voice.md').read_text(encoding='utf-8')),
                 dict(path='docs/curriculum/source-of-truth.md', text=(SNAPSHOT / 'source-of-truth.md').read_text(encoding='utf-8')),
                 dict(path='docs/agents/narration.md', text=(ROOT / 'docs/agents/narration.md').read_text(encoding='utf-8'))]
    rules = ['수업 예고를 먼저 확정하고 목표·경험 순서·최종 수행을 PRD와 실행 문제에 연결한다.',
             '한 스텝에 새 관계 하나. 학생 수정은 0~3줄이고 대부분 값 한 곳이다. 준비 명령은 역할과 볼 곳을 밝힌다.',
             '정상 관찰 → 한 곳 수정 → 실행 → 변경 후 관찰을 할 일과 해설에 드러낸다.',
             '객관식·결과값 입력 없이 실제 명령과 실제 API 상태·채점기 자신의 HTTP 요청으로 판정한다.',
             '로컬 실습 환경이 확인한 동작만 가르치고 라우팅·NAT·NACL·피어링·보안 그룹의 AWS 동등성을 주장하지 않는다.',
             '문제마다 소유 라벨의 독립 실습 상태에서 시작하고, 해설은 별도 실습 상태에서 시연한다.']
    return dict(revision=policy_revision(artifacts), artifacts=artifacts, rules=rules)


def prd(preview):
    chapters = []
    by_id = {s['id']: s for s in STEPS}
    for c in HIERARCHY:
        units = []
        for u in c['units']:
            units.append(dict(id=u['id'], title=u['title'], objectives=u['objectives'], premise=u['premise'],
                              steps=[dict(id=i, title=by_id[i]['title'], objectives=by_id[i]['objectives'], core_flow=by_id[i]['core'],
                                          complexity=by_id[i]['complexity']) for i in u['steps']]))
        chapters.append(dict(id=c['id'], title=c['title'], objectives=c['objectives'], units=units))
    rep = by_id[ST[1]]
    document = dict(
        schema_version=1, id=LESSON_ID, title='클라우드 · 주소 공간 안에 서버 한 대를 배치해요', course=COURSE_ID,
        audience='자바 과정의 네트워크·Docker·Compose 수업을 마친 학습자. 자바 과정의 후속 클라우드 묶음 첫 수업이다.',
        objectives=LEARN,
        prerequisites=['network-ip', 'network-endpoints', 'network-routing', 'network-http', 'docker-image-container', 'docker-network-ports',
                       'Docker Desktop의 Linux 컨테이너 엔진과 AWS CLI v2'],
        scope=[s['title'] for s in STEPS],
        out_of_scope=['중지·재시작·종료·스냅샷·삭제 순서(다음 수업), S3·RDS·DynamoDB·SQS·Lambda',
                      '라우팅 표·인터넷 게이트웨이·NAT·NACL·피어링·보안 그룹, 다른 VPC 간 격리',
                      '실제 AWS 계정·과금·AWS SDK, CIDR 비트 계산 재교육, 서브넷 예약 주소·최소 크기 규칙'],
        policy_snapshot=policy(), sources=SOURCES,
        strategy='읽기 전용 VPC 도입은 단원 전제와 첫 스텝의 관찰로 두고 채점하지 않는다. 실행 과제(1·4)는 초기 상태가 실패하고 준비 명령을 실행하면 통과한다. '
                 '오류 수정 과제는 준비 명령의 실제 실패를 본 뒤 한 곳을 고친다. 마지막 수행은 새 개념 없이 세 값을 고친다.',
        chapters=chapters,
        grading=['채점기는 실습 소유 기록(VPC·준비 서브넷·준비 인스턴스 ID)과 실제 EC2 API 상태를 읽는다. 학생 셸 변수·명령 문자열·터미널 출력은 근거가 아니다.',
                 '서브넷은 VpcId로 직접 나누고 소유 VPC 밖의 같은 CIDR은 「다른 자리」로 실패한다. 조건형 스텝(3)은 조건을 검사한다.',
                 '서버는 소유 VPC의 새 인스턴스·준비 AMI·running·목표 서브넷·범위 안 IP로 판정하고 pending은 정해진 시간 안에서 기다린다. 요청 스텝은 주소 파일과 API 사설 주소를 비교한 뒤 채점기가 소유 클라이언트에서 직접 HTTP로 서버 신원(instance·served-on·from·java.version)을 확인한다.',
                 '런타임 중단·준비 실패는 오답이 아니라 환경 오류다.'],
        reset=['스텝마다 소유 라벨의 새 Floci 상태에서 준비 자원을 만들고 시작 상태 설명에서 먼저 알린다. 「초기화」는 이전 런타임만 정리하고 준비 파일을 바이트 그대로 되돌린다. 해설은 임시 실습 상태에서 시연하고 닫으면 그 자원만 지운다.'],
        narration=['문제의 목표 범위·준비 값·제약을 정확한 문장과 코드에 강조하고, 명령 하나의 실제 출력을 읽은 뒤 다음 행동으로 넘어간다. 동적 ID·주소는 aws 명령으로 옮겨 적고 그 사실을 말한다. 실제 음성 동기화는 앱 확인이 필요하다.'],
        verification=['단위: cargo test --lib cloud_practice(래퍼·주소 파일·편집 파일·스키마).',
                      '수업 데이터: 공개 수업 JSON의 7개 스텝을 네이티브 제출 경로(check_exercise)로 실행한다. 초기 실패, 준비 코드 실패, 해설 재생 통과, 오답·동등 풀이·변형, 초기화, 해설 분리를 확인한다.',
                      '빌드: build-redesigned-git --lesson, narration_review, build-redesigned-course-bundle --check, lesson_registry. macOS·화면·실제 음성은 별도 검증 범위로 남긴다.'],
        representative=dict(step_id=ST[1], prompt=rep['goal'], starter_state='VPC 10.91.0.0/16만 있고 서브넷 0개. create-subnet.sh의 --cidr-block은 10.92.2.0/24.',
                            expected_action='--cidr-block 한 곳을 10.91.2.0/24로 고치고 실행한다.',
                            acceptance='소유 VPC에 10.91.2.0/24 available 서브넷이 정확히 하나이고 다른 새 서브넷이 없다. 다른 VPC의 같은 CIDR·출력 위조·범위 안 다른 값은 실패한다.',
                            reset='「초기화」는 새 Floci 상태와 create-subnet.sh 원본을 돌려준다.',
                            narration='준비 명령의 실제 InvalidSubnet.Range 거절을 읽고, 둘째 칸 92와 91의 차이를 짚은 뒤 한 곳을 고쳐 다시 실행한다.'),
        lesson_preview=preview,
        approval=dict(status='draft'),
        change_history=['2026-11-09 사용자 검토용 초안(.scratch/floci-course-wayfinder/first-lesson/prd.draft.md).',
                        '2026-11-10 승인 범위 안의 정식 제작: 읽기 전용 VPC 조회(1.1.1)를 단원 전제와 첫 스텝 관찰로 옮겼다. 자바 게스트 게이트가 통과해 2장도 같은 자바 서버 이미지를 쓴다. 학생이 고치는 파일은 편집기에 둔다. 마지막 수행은 새 서브넷 ID 변수가 없으므로 subnet-id.sh가 범위로 ID를 찾는다. 학생의 「다시 시작」 표현은 실제 버튼 이름 「초기화」로 바꿨다.'],
    )
    return approve(document, by='Claude Code: 사용자 승인 초안에 따른 본편·해설 제작',
                   evidence='2026-11-09 사용자가 예고·PRD·대표 문제 초안을 확인한 뒤 「고고」로 다음 제작 단계를 승인했다. 2026-11-10 사용자: 승인된 예고·PRD·대표 문제를 바탕으로 첫 수업을 완성해, 방향 확인을 반복해서 묻지 말고 구현·검증까지 계속 진행해. 생성된 정식 JSON이나 개별 문장을 사용자가 직접 검수했다고 주장하지 않는다.')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    from curriculum_authority import alignment_source, course_intent, digest
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    course = next(c for c in catalog['courses'] if c['key'] == 'java')
    preview_public = dict(learn=LEARN, challenge=CHALLENGE, scenario=[s['title'] for s in STEPS], constraints=CONSTRAINTS, question=QUESTION)
    preview = dict(preview_public, lesson_key=KEY, lesson_id=LESSON_ID, origin='preview_first_2026-11-09',
                   course_intent_sha256=digest(course_intent(course)))
    write(FOLDER / 'lesson-preview.json', preview)
    document = prd(preview_public)
    write(FOLDER / 'approved-prd.json', document)
    (FOLDER / 'approved-prd.md').write_text(render(document) + '\n', encoding='utf-8', newline='\n')
    authored = content()
    write(FOLDER / 'content.json', authored)
    write(FOLDER / 'preview-alignment.json', dict(
        status='reviewed', source_sha256=digest(alignment_source(preview, document, authored)), reviewed_at='2026-11-10',
        reason='Claude Code가 승인 초안의 7개 실습·범위·제외 항목과 예고·PRD·본편·채점 구성을 대조했다. 사용자의 개별 원고 검수는 아니다.',
        scope='PRD 계층·전제·채점·초기화와 모든 스텝 필드(준비 파일·클라우드 구성 포함). 해설은 자체 검토 계층에서 확인한다.',
        schema_version=2))
    openings_path = ROOT / 'tools/redesigned_lessons/narration-openings.json'
    openings = json.loads(openings_path.read_text(encoding='utf-8'))
    openings[KEY] = OPENINGS
    openings_path.write_text(json.dumps(openings, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('wrote', FOLDER.relative_to(ROOT))


if __name__ == '__main__':
    main()
