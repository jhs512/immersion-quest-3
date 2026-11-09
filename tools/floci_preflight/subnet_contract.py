"""Runtime/grader contract tests for the representative subnet step.

These drive real plain-Floci lanes with the real AWS CLI and real bash. They are not MQ
native integration tests: MQ has no Floci runner yet, so nothing here goes through MQ code.
Each scenario runs once; a failed scenario is reported, never retried into a pass.
"""
from __future__ import annotations

import difflib
import json
import traceback

from common import GIT_BASH, Run, compare_snapshots, host_snapshot
from subnet_lab import Lane, check, sha256

ALT_FIXTURE = {'vpc_cidr': '10.73.0.0/16', 'target_cidr': '10.73.2.0/24',
               'starter_cidr': '10.74.2.0/24'}


def student_bash(lane: Lane, script: str | None = None, env_overrides: dict | None = None, label='student'):
    """Run `bash create-subnet.sh` in the student workspace, like the terminal would."""
    path = lane.workspace / 'create-subnet.sh'
    if script is not None:
        path.write_bytes(script.encode('utf-8'))
    env = lane.student_env()
    env.update(env_overrides or {})
    return lane.run.cmd([GIT_BASH, 'create-subnet.sh'], cwd=str(lane.workspace), env=env,
                        check=False, label=f'{lane.name}:{label}')


def one_line_fix(lane: Lane, new_cidr: str) -> tuple[str, list[str]]:
    rec = lane.record()
    old = (lane.workspace / 'create-subnet.sh').read_text(encoding='utf-8')
    new = old.replace(f'--cidr-block {rec["starter_cidr"]}', f'--cidr-block {new_cidr}')
    changed = [ln for ln in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm='', n=0)
               if ln[:1] in '+-' and not ln.startswith(('+++', '---'))]
    return new, changed


def direct_create(lane: Lane, vpc_id: str, cidr: str, label='direct'):
    return lane.run.aws(lane.endpoint, 'ec2', 'create-subnet', '--vpc-id', vpc_id,
                        '--cidr-block', cidr, label=f'{lane.name}:{label}')


class Suite:
    def __init__(self, run: Run):
        self.run = run
        self.results: list[dict] = []

    def case(self, name: str, expected: str, actual: dict, extra_ok=True, expected_codes=(),
             evidence=None):
        ok = actual.get('verdict') == expected and extra_ok and \
            all(c in actual.get('codes', []) for c in expected_codes)
        self.results.append({'name': name, 'expected_verdict': expected,
                             'expected_codes': list(expected_codes), 'ok': ok,
                             'check': actual, 'evidence': evidence or {}})
        self.run.save('contract-results', self.results)
        print(f"  [{'OK ' if ok else 'BAD'}] {name}: {actual.get('verdict')} {actual.get('codes')}",
              flush=True)


def scenarios(s: Suite, student: Lane, explain: Lane, envlane: Lane):
    run = s.run
    rec = student.init()
    original = (student.workspace / 'create-subnet.sh').read_text(encoding='utf-8')

    # 1 initial state
    s.case('initial_state_fails', 'fail', check(student), expected_codes=['no_subnet_in_owned_vpc'])

    # 2 starter as-is: outside CIDR (10.92.2.0/24) is rejected by the API
    r = student_bash(student, label='starter-as-is')
    s.case('starter_outside_cidr_fails', 'fail', check(student),
           extra_ok=r['rc'] != 0 and 'InvalidSubnet.Range' in r['stderr'],
           expected_codes=['no_subnet_in_owned_vpc'],
           evidence={'script_rc': r['rc'], 'script_stderr': r['stderr'].strip()})
    r = direct_create(student, rec['vpc_id'], '10.0.2.0/24', label='outside-10.0')
    s.case('outside_cidr_10_0_fails', 'fail', check(student),
           extra_ok=r['rc'] != 0 and 'InvalidSubnet.Range' in r['stderr'],
           evidence={'rc': r['rc'], 'stderr': r['stderr'].strip()})

    # 3 one-line fix passes; running it again is rejected as overlap but state still passes
    new, changed = one_line_fix(student, rec['target_cidr'])
    r = student_bash(student, new, label='one-line-fix')
    s.case('correct_one_line_edit_passes', 'pass', check(student),
           extra_ok=r['rc'] == 0 and len(changed) == 2,
           evidence={'diff': changed, 'script_rc': r['rc'], 'script_stdout': r['stdout']})
    r = student_bash(student, label='same-fix-twice')
    s.case('same_command_twice_still_passes', 'pass', check(student),
           extra_ok=r['rc'] != 0 and 'InvalidSubnet.Conflict' in r['stderr'],
           evidence={'second_rc': r['rc'], 'second_stderr': r['stderr'].strip()})

    # 4 different VPC with the same CIDRs, reached by changing the student's own LAB_VPC_ID
    rec = student.reset()
    other = run.aws(student.endpoint, 'ec2', 'create-vpc', '--cidr-block', rec['vpc_cidr'],
                    label='student:own-vpc')
    other_id = json.loads(other['stdout'])['Vpc']['VpcId']
    new, _ = one_line_fix(student, rec['target_cidr'])
    r = student_bash(student, new, env_overrides={'LAB_VPC_ID': other_id}, label='other-vpc')
    s.case('different_vpc_same_cidr_fails', 'fail', check(student),
           extra_ok=r['rc'] == 0, expected_codes=['no_subnet_in_owned_vpc', 'target_cidr_in_other_vpc'],
           evidence={'student_vpc': other_id, 'owned_vpc': rec['vpc_id'], 'script_rc': r['rc']})

    # 5 other in-range CIDR
    rec = student.reset()
    new, _ = one_line_fix(student, '10.91.3.0/24')
    r = student_bash(student, new, label='in-range-other')
    s.case('other_in_range_cidr_fails', 'fail', check(student), extra_ok=r['rc'] == 0,
           expected_codes=['non_target_subnet_in_owned_vpc'])

    # 6 target plus an extra subnet
    r2 = direct_create(student, rec['vpc_id'], rec['target_cidr'], label='extra-target')
    s.case('extra_subnet_fails', 'fail', check(student), extra_ok=r2['rc'] == 0,
           expected_codes=['non_target_subnet_in_owned_vpc'])

    # 7 output-only fake: prints a success-shaped JSON without touching state
    rec = student.reset()
    fake = ('echo \'{"Subnet": {"SubnetId": "subnet-fake", "VpcId": "\'"$LAB_VPC_ID"\'", '
            f'"CidrBlock": "{rec["target_cidr"]}", "State": "available"}}}}\'\n')
    r = student_bash(student, fake, label='fake-output')
    s.case('output_only_fake_fails', 'fail', check(student),
           extra_ok=r['rc'] == 0 and rec['target_cidr'] in r['stdout'],
           expected_codes=['no_subnet_in_owned_vpc'], evidence={'stdout': r['stdout']})

    # 8 equivalent direct API solutions
    rec = student.reset()
    r = direct_create(student, rec['vpc_id'], rec['target_cidr'], label='direct-correct')
    s.case('direct_api_equivalent_passes', 'pass', check(student), extra_ok=r['rc'] == 0)
    rec = student.reset()
    wrong = json.loads(direct_create(student, rec['vpc_id'], '10.91.3.0/24', label='wrong-first')['stdout'])
    d = run.aws(student.endpoint, 'ec2', 'delete-subnet', '--subnet-id', wrong['Subnet']['SubnetId'],
                label='student:delete-wrong')
    r = direct_create(student, rec['vpc_id'], rec['target_cidr'], label='recreate')
    s.case('delete_then_recreate_passes', 'pass', check(student), extra_ok=d['rc'] == 0 and r['rc'] == 0)

    # 9 reset after a messy state: fresh VPC, no stray resources, starter restored byte-for-byte
    run.aws(student.endpoint, 'ec2', 'create-vpc', '--cidr-block', '10.95.0.0/16', label='student:stray-vpc')
    (student.workspace / 'create-subnet.sh').write_text('echo edited\n', encoding='utf-8')
    before_reset = rec
    rec = student.reset()
    vpcs = json.loads(run.aws(student.endpoint, 'ec2', 'describe-vpcs', label='after-reset')['stdout'])['Vpcs']
    starter_now = (student.workspace / 'create-subnet.sh').read_text(encoding='utf-8')
    unexpected = [v for v in vpcs if v['VpcId'] not in rec['preexisting_vpc_ids'] + [rec['vpc_id']]]
    c = check(student)
    s.case('reset_returns_fresh_state_and_starter', 'fail', c,
           extra_ok=(starter_now == original and sha256(starter_now) == rec['starter_sha256']
                     and not unexpected and c['observed']['owned_subnets'] == []),
           expected_codes=['no_subnet_in_owned_vpc'],
           evidence={'vpc_before_reset': before_reset['vpc_id'], 'vpc_after_reset': rec['vpc_id'],
                     'vpcs_after_reset': [(v['VpcId'], v['CidrBlock'], v.get('IsDefault')) for v in vpcs],
                     'starter_restored': starter_now == original})

    # 10 two lanes: explanation demo does not touch the student's lane
    new, _ = one_line_fix(student, '10.91.3.0/24')
    student_bash(student, new, label='student-progress')
    s_before = check(student)
    s_file = (student.workspace / 'create-subnet.sh').read_bytes()
    erec = explain.init()
    enew, _ = one_line_fix(explain, erec['target_cidr'])
    student_bash(explain, enew, label='explanation-demo')
    e_check = check(explain)
    explain.cleanup()
    s_after = check(student)
    s.case('explanation_lane_preserves_student_state', 'fail', s_after,
           extra_ok=(e_check['verdict'] == 'pass' and s_after['observed'] == s_before['observed']
                     and (student.workspace / 'create-subnet.sh').read_bytes() == s_file
                     and student.record()['vpc_id'] == rec['vpc_id']),
           expected_codes=['non_target_subnet_in_owned_vpc'],
           evidence={'explanation_check': e_check, 'student_before': s_before['observed'],
                     'student_endpoint': student.endpoint, 'explanation_endpoint': erec['endpoint']})

    # 11 changed CIDR fixture through the same contract
    arec = student.reset(ALT_FIXTURE)
    s.case('alt_fixture_initial_fails', 'fail', check(student), expected_codes=['no_subnet_in_owned_vpc'])
    r = student_bash(student, label='alt-starter')
    s.case('alt_fixture_starter_fails', 'fail', check(student),
           extra_ok=r['rc'] != 0 and 'InvalidSubnet.Range' in r['stderr'])
    r = direct_create(student, arec['vpc_id'], '10.91.2.0/24', label='alt-old-target')
    s.case('alt_fixture_old_target_rejected', 'fail', check(student),
           extra_ok=r['rc'] != 0 and 'InvalidSubnet.Range' in r['stderr'])
    new, changed = one_line_fix(student, ALT_FIXTURE['target_cidr'])
    r = student_bash(student, new, label='alt-fix')
    s.case('alt_fixture_correct_passes', 'pass', check(student),
           extra_ok=r['rc'] == 0 and len(changed) == 2)

    # 12 student deletes the owned VPC: a wrong state, not an environment error
    rec = student.reset()
    run.aws(student.endpoint, 'ec2', 'delete-vpc', '--vpc-id', rec['vpc_id'], label='student:delete-vpc')
    s.case('owned_vpc_deleted_fails_not_env_error', 'fail', check(student),
           expected_codes=['owned_vpc_missing'])

    # 13 environment error: the lane runtime is down
    erec = envlane.init()
    run.docker('stop', '-t', '2', envlane.container, label='envlane:stop')
    s.case('runtime_down_is_env_error', 'env_error', check(envlane),
           expected_codes=['endpoint_unreachable'])


def main(run_id: str) -> dict:
    run = Run(run_id, 'subnet')
    print(f'subnet contract run dir: {run.dir}', flush=True)
    before = host_snapshot(run, 'host-before')
    network = f'{run.id}-subnet'
    suite = Suite(run)
    lanes: list[Lane] = []
    fatal = None
    audit = None
    try:
        run.docker('network', 'create', '--label', run.label, network, label='network')
        student, explain, envlane = (Lane(run, n, network) for n in ('student', 'explanation', 'envcheck'))
        lanes = [student, explain, envlane]
        for lane in lanes:
            lane.start()
        audit = {lane.name: _audit_lane(run, lane) for lane in lanes}
        run.save('lane-isolation-audit', audit)
        scenarios(suite, student, explain, envlane)
    except BaseException:
        fatal = traceback.format_exc()
        run.save('fatal', {'traceback': fatal})
        print(fatal, flush=True)
    finally:
        for lane in lanes:
            try:
                run.docker('logs', lane.container, check=False, label=f'{lane.name}:final-log')
                lane.cleanup()
            except Exception as e:
                run.save(f'cleanup-error-{lane.name}', {'error': repr(e)})
        run.remove_owned('network', network)
        after = host_snapshot(run, 'host-after')
        diff = compare_snapshots(before, after)
        run.save('host-diff', diff)
    passed = sum(r['ok'] for r in suite.results)
    summary = {'part': 'subnet-contract', 'run_dir': str(run.dir), 'fatal': fatal is not None,
               'cases_total': len(suite.results), 'cases_ok': passed,
               'cases_bad': [r['name'] for r in suite.results if not r['ok']],
               'host_inventory_clean': diff['clean'], 'host_diff': diff,
               'lane_audit': audit}
    run.save('summary', summary)
    return summary


def _audit_lane(run: Run, lane: Lane) -> dict:
    obj = json.loads(run.docker('inspect', lane.container, label='audit')['stdout'])[0]
    hc = obj['HostConfig']
    return {
        'privileged': hc['Privileged'], 'mounts': obj['Mounts'], 'binds': hc.get('Binds'),
        'port_bindings': hc['PortBindings'], 'live_ports': obj['NetworkSettings']['Ports'],
        'cap_drop': hc.get('CapDrop'), 'security_opt': hc.get('SecurityOpt'),
        'nano_cpus': hc['NanoCpus'], 'memory': hc['Memory'], 'pids_limit': hc['PidsLimit'],
        'docker_socket_mounted': any('docker.sock' in (m.get('Source', '') + m.get('Destination', ''))
                                     for m in obj['Mounts']),
        'label': obj['Config']['Labels'].get('mq.lab'),
        'image': obj['Image'], 'image_ref': obj['Config']['Image'],
    }
