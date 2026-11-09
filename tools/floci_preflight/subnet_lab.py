"""Runtime prototype for the representative step (draft 1.2.2): one subnet inside the owned VPC.

A *lane* is one plain Floci process in EC2 mock mode (no Docker socket, not privileged,
loopback-only API on a Docker-allocated port). The student lane and the explanation lane
are separate processes, so a demonstration can never touch the student's state.

The grader trusts only the owned record written by init (control/owned.json, outside the
student workspace). It never reads command strings, shell variables or terminal output.
"""
from __future__ import annotations

import datetime
import hashlib
import ipaddress
import json
import pathlib
import urllib.request

from common import FLOCI, Run, wait_until

STARTER_TEMPLATE = '''# 준비된 VPC 안에 서브넷 하나를 만드는 명령이에요.
# 실행 전에 --cidr-block 값을 VPC 범위와 비교해 보세요.
aws ec2 create-subnet \\
  --endpoint-url "$LAB_ENDPOINT" \\
  --vpc-id "$LAB_VPC_ID" \\
  --cidr-block {starter_cidr}
'''

DEFAULT_FIXTURE = {'vpc_cidr': '10.91.0.0/16', 'target_cidr': '10.91.2.0/24',
                   'starter_cidr': '10.92.2.0/24'}


class EnvError(Exception):
    """The lab runtime, not the student's answer, prevented a judgement."""

    def __init__(self, code: str, detail: str):
        super().__init__(f'{code}: {detail}')
        self.code, self.detail = code, detail


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class Lane:
    def __init__(self, run: Run, name: str, network: str):
        self.run, self.name, self.network = run, name, network
        self.container = f'{run.id}-{name}'
        self.root = run.dir / 'lanes' / name
        self.workspace = self.root / 'workspace'
        self.control = self.root / 'control'
        for d in (self.workspace, self.control):
            d.mkdir(parents=True, exist_ok=True)
        self.endpoint: str | None = None

    # -- runtime ---------------------------------------------------------
    def start(self):
        self.run.docker(
            'run', '-d', '--name', self.container, '--label', self.run.label,
            '--label', f'mq.lab.lane={self.name}', '--network', self.network,
            '-p', '127.0.0.1::4566', '--cpus', '1', '--memory', '1g', '--pids-limit', '512',
            # Start as the image's unprivileged floci uid so the entrypoint skips its
            # root-only `chroot --userspec` step; that step needs CAP_SYS_CHROOT.
            '--user', '1001:0', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
            # The image declares VOLUME /app/data; without an explicit mount Docker creates an
            # unlabelled anonymous volume that `rm -f` leaves behind.
            '--tmpfs', '/app/data:rw,size=64m,uid=1001,gid=0,mode=0700',
            '-e', 'FLOCI_STORAGE_MODE=memory', '-e', 'FLOCI_SERVICES_EC2_MOCK=true',
            FLOCI, label=f'{self.name}:start')
        port = self.run.published_port(self.container)
        self.endpoint = f'http://127.0.0.1:{port}'
        wait_until(lambda: self._api('ec2', 'describe-vpcs', label='ready').get('Vpcs') is not None,
                   seconds=120)
        inspect = json.loads(self.run.docker('inspect', self.container, label='inspect')['stdout'])[0]
        self.run.save(f'lane-{self.name}-inspect', inspect)
        return inspect

    def _api(self, service, action, *args, label=None):
        """Call the lane API; raise EnvError for transport/runtime failures."""
        r = self.run.aws(self.endpoint, service, action, *args, label=f'{self.name}:{label or action}')
        if r['rc'] == 0:
            try:
                return json.loads(r['stdout']) if r['stdout'].strip() else {}
            except json.JSONDecodeError as e:
                raise EnvError('malformed_response', str(e))
        err = r['stderr']
        if r['rc'] == 'timeout' or 'Could not connect' in err or 'Connection was closed' in err \
                or 'Read timeout' in err or 'Connect timeout' in err:
            raise EnvError('endpoint_unreachable', err.strip()[-300:])
        return {'_error': err.strip(), '_rc': r['rc']}

    def floci_reset(self):
        req = urllib.request.Request(self.endpoint + '/_floci/state/reset', method='POST', data=b'')
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
        self.run.events.append({'label': f'{self.name}:floci-reset', 'status': resp.status, 'body': body})
        return resp.status

    # -- lesson lifecycle -------------------------------------------------
    def init(self, fixture: dict | None = None) -> dict:
        fx = dict(DEFAULT_FIXTURE, **(fixture or {}))
        before = self._api('ec2', 'describe-vpcs', label='init-before')
        out = self._api('ec2', 'create-vpc', '--cidr-block', fx['vpc_cidr'], label='init-create-vpc')
        if '_error' in out:
            raise EnvError('init_failed', out['_error'])
        vpc_id = out['Vpc']['VpcId']
        vpc = wait_until(lambda: [v for v in self._api('ec2', 'describe-vpcs', '--vpc-ids', vpc_id,
                                                       label='init-wait').get('Vpcs', [])
                                  if v.get('State') == 'available'], seconds=60)[0]
        starter = STARTER_TEMPLATE.format(starter_cidr=fx['starter_cidr'])
        (self.workspace / 'create-subnet.sh').write_bytes(starter.encode('utf-8'))
        record = {
            'schema': 'mq.floci.subnet-step.v1', 'lane': self.name, 'endpoint': self.endpoint,
            'container': self.container, 'region': 'us-east-1',
            'vpc_id': vpc_id, 'vpc_cidr': vpc['CidrBlock'], 'target_cidr': fx['target_cidr'],
            'starter_cidr': fx['starter_cidr'], 'starter_sha256': sha256(starter),
            'preexisting_vpc_ids': sorted(v['VpcId'] for v in before.get('Vpcs', [])),
            'initialized_at': datetime.datetime.now().isoformat(timespec='seconds'),
        }
        (self.control / 'owned.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
        return record

    def record(self) -> dict:
        return json.loads((self.control / 'owned.json').read_text(encoding='utf-8'))

    def student_env(self) -> dict:
        """What the student shell receives. The owned record itself is never exported."""
        rec = self.record()
        env = dict(self.run.env)
        # LAB_ENDPOINT is also exported as AWS_ENDPOINT_URL so a deleted --endpoint-url still
        # stays local. That is a safety net, not the product's external-AWS block.
        env.update(LAB_ENDPOINT=rec['endpoint'], LAB_VPC_ID=rec['vpc_id'],
                   AWS_ENDPOINT_URL=rec['endpoint'])
        return env

    def reset(self, fixture: dict | None = None) -> dict:
        """「다시 시작」: wipe this lane's Floci state in place, then init and restore the starter."""
        self.floci_reset()
        return self.init(fixture)

    def cleanup(self):
        self.run.remove_owned('container', self.container)


# -- grader ---------------------------------------------------------------
def check(lane: Lane) -> dict:
    """Judge the owned VPC's actual state. Returns pass / fail / env_error with reasons."""
    try:
        rec = lane.record()
    except (OSError, json.JSONDecodeError) as e:
        return {'verdict': 'env_error', 'codes': ['owned_record_unreadable'], 'detail': str(e)}
    try:
        return _judge(lane, rec)
    except EnvError as e:
        return {'verdict': 'env_error', 'codes': [e.code], 'detail': e.detail,
                'feedback': ['실습 환경에 연결하지 못했어요. 「다시 시작」을 눌러 보세요.']}


def _judge(lane: Lane, rec: dict) -> dict:
    target = ipaddress.ip_network(rec['target_cidr'])
    vpcs = lane._api('ec2', 'describe-vpcs', '--vpc-ids', rec['vpc_id'], label='check-vpc')
    if '_error' in vpcs:
        if 'InvalidVpcID.NotFound' in vpcs['_error']:
            return {'verdict': 'fail', 'codes': ['owned_vpc_missing'], 'observed': {},
                    'feedback': ['준비된 VPC가 없어졌어요. 「다시 시작」으로 처음 상태를 다시 받으세요.']}
        raise EnvError('describe_vpcs_failed', vpcs['_error'])
    owned = vpcs.get('Vpcs', [])
    if len(owned) != 1 or owned[0].get('VpcId') != rec['vpc_id']:
        raise EnvError('owned_vpc_ambiguous', json.dumps(owned))
    subnets_out = lane._api('ec2', 'describe-subnets', label='check-subnets')
    if '_error' in subnets_out:
        raise EnvError('describe_subnets_failed', subnets_out['_error'])
    # Partition by the VpcId each subnet reports instead of trusting a server-side filter.
    all_subnets = subnets_out.get('Subnets', [])
    mine = [s for s in all_subnets if s.get('VpcId') == rec['vpc_id']]
    elsewhere = [s for s in all_subnets if s.get('VpcId') != rec['vpc_id']
                 and s.get('CidrBlock') == rec['target_cidr']]
    observed = {
        'owned_vpc': {'VpcId': owned[0]['VpcId'], 'CidrBlock': owned[0].get('CidrBlock'),
                      'State': owned[0].get('State')},
        'owned_subnets': [{k: s.get(k) for k in ('SubnetId', 'VpcId', 'CidrBlock', 'State')} for s in mine],
        'target_cidr_in_other_vpcs': [{k: s.get(k) for k in ('SubnetId', 'VpcId', 'CidrBlock')}
                                      for s in elsewhere],
    }
    codes, feedback = [], []
    if owned[0].get('CidrBlock') != rec['vpc_cidr']:
        codes.append('owned_vpc_cidr_changed')
        feedback.append('준비된 VPC의 주소 범위가 처음과 달라요.')
    hits = [s for s in mine if s.get('CidrBlock') == rec['target_cidr']]
    others = [s for s in mine if s.get('CidrBlock') != rec['target_cidr']]
    if not mine:
        codes.append('no_subnet_in_owned_vpc')
        feedback.append('준비된 VPC에 서브넷이 없어요.')
    if others:
        codes.append('non_target_subnet_in_owned_vpc')
        feedback.append(f'{rec["target_cidr"]}가 아닌 서브넷이 있어요: '
                        + ', '.join(s['CidrBlock'] for s in others))
    if len(hits) > 1:  # Floci rejects overlaps; kept so the contract does not depend on it.
        codes.append('duplicate_target_subnet')
    for s in hits:
        if s.get('State') != 'available':
            codes.append('target_subnet_not_available')
            feedback.append('서브넷이 아직 준비 중이에요. 잠시 뒤 다시 제출하세요.')
        if not ipaddress.ip_network(s['CidrBlock']).subnet_of(ipaddress.ip_network(rec['vpc_cidr'])):
            codes.append('target_outside_vpc')  # cannot happen if the API validated it
    if elsewhere and not hits:
        codes.append('target_cidr_in_other_vpc')
        feedback.append('준비된 VPC가 아닌 곳에 만들었어요. 같은 숫자라도 다른 자리예요.')
    verdict = 'pass' if (len(hits) == 1 and not others and not codes) else 'fail'
    if verdict == 'pass':
        feedback = [f'준비된 VPC 안에 {target} 서브넷이 하나 있어요.']
    return {'verdict': verdict, 'codes': codes, 'feedback': feedback, 'observed': observed}
