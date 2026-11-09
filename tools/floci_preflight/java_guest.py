"""Java 25 EC2 guest preflight (PRD draft step 3.1.1 gate).

Owned privileged DIND (experiment boundary only) -> official Floci 2.4.0 with an external
image catalog (FLOCI_SERVICES_EC2_IMAGE_CATALOG_PATH) -> real EC2 guest containers from a
prepared image built on the pinned Temurin 25 base. The server starts only from user-data.
Floci gets the nested engine's socket, never the host's.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import shutil
import subprocess
import time
import traceback

from common import (DIND, FLOCI, FLOCI_SOURCE_COMMIT, REPO, TEMURIN, Run, compare_snapshots,
                    host_snapshot, wait_until)

GUEST_SRC = REPO / 'tools' / 'floci_preflight' / 'guest'
AMI = 'ami-0e0000000000a0025'
AMI_ALIAS = 'ami-mq-java25-http'
BUNDLED_AMI = 'ami-0abcdef1234567891'  # bundled catalog's AL2023 entry; must vanish with ours
VPC_CIDR, SUBNET_A, TARGET = '10.91.0.0/16', '10.91.1.0/24', '10.91.2.0/24'
PORT = 8080

CATALOG = """defaultDockerImage: {image}
images:
  - imageId: {ami}
    aliases:
      - {alias}
    dockerImage: {image}
    name: mq-java25-http-preflight
    description: MQ preflight Java 25 HTTP guest (eclipse-temurin 25-jdk-alpine + HelloServer.java)
    state: available
    ownerId: "000000000000"
    architecture: x86_64
    rootDeviceType: ebs
    rootDeviceName: /dev/xvda
    virtualizationType: hvm
    creationDate: "2026-11-09T00:00:00.000Z"
    provenance: "built in nested engine FROM {base}"
"""


class Lab:
    def __init__(self, run: Run):
        self.run = run
        self.dind = f'{run.id}-dind'
        self.network = f'{run.id}-java'
        self.volume = f'{run.id}-docker'
        self.endpoint = None
        self.obs: dict = {}
        self.cases: list[dict] = []

    # -- plumbing -----------------------------------------------------------
    def inner(self, *args, **kw):
        return self.run.docker('exec', self.dind, 'docker', *args, **kw)

    def api(self, action, *args, label=None):
        r = self.run.aws(self.endpoint, 'ec2', action, *args, label=label or action)
        if r['rc'] != 0:
            return {'_error': r['stderr'].strip(), '_rc': r['rc']}
        return json.loads(r['stdout']) if r['stdout'].strip() else {}

    def note(self, key, value):
        self.obs[key] = value
        self.run.save('observations', self.obs)

    def case(self, name, ok, detail):
        self.cases.append({'name': name, 'ok': bool(ok), 'detail': detail})
        self.run.save('cases', self.cases)
        print(f"  [{'OK ' if ok else 'BAD'}] {name}", flush=True)

    # -- bootstrap ------------------------------------------------------------
    def bootstrap(self):
        run = self.run
        run.docker('network', 'create', '--label', run.label, self.network, label='outer-network')
        run.docker('volume', 'create', '--label', run.label, self.volume, label='outer-volume')
        run.docker('run', '-d', '--name', self.dind, '--label', run.label, '--privileged',
                   '--cgroupns=host', '--cpus', '4', '--memory', '6g', '--pids-limit', '2048',
                   '--network', self.network, '-p', '127.0.0.1::4566',
                   '-v', f'{self.volume}:/var/lib/docker', '--entrypoint', 'dockerd', DIND,
                   '--host=unix:///var/run/docker.sock', '--storage-driver=overlay2', label='outer-dind')
        self.endpoint = f'http://127.0.0.1:{run.published_port(self.dind)}'
        wait_until(lambda: self.inner('info', check=False, label='inner-info')['rc'] == 0, 90)
        empty = {k: self.inner(*a, label='inner-empty')['stdout'].split()
                 for k, a in (('images', ('images', '-q')), ('containers', ('ps', '-aq')))}
        self.note('inner_engine_initially_empty', empty)
        self.note('inner_version', json.loads(self.inner('version', '--format', '{{json .}}')['stdout']))
        for ref in (FLOCI, TEMURIN):
            self.transfer_image(ref)

    def transfer_image(self, ref):
        """Pull inside the nested engine; on failure copy the host's cached image by save/load."""
        host = json.loads(self.run.docker('image', 'inspect', ref, label='host-image')['stdout'])[0]
        pulled = self.inner('pull', ref, check=False, timeout=420, label='inner-pull')
        method = 'inner-pull'
        if pulled['rc'] != 0:
            method = 'host-save-load'
            save = subprocess.Popen(['docker', 'save', '--platform', 'linux/amd64', ref],
                                    stdout=subprocess.PIPE, env=self.run.env)
            load = subprocess.run(['docker', 'exec', '-i', self.dind, 'docker', 'load'],
                                  stdin=save.stdout, capture_output=True, text=True, env=self.run.env,
                                  timeout=600)
            save.stdout.close()
            save.wait()
            self.run.events.append({'label': 'save-load', 'ref': ref, 'save_rc': save.returncode,
                                    'load_rc': load.returncode, 'stdout': load.stdout, 'stderr': load.stderr})
            if save.returncode or load.returncode:
                raise RuntimeError(f'save/load failed for {ref}: {load.stderr[-500:]}')
        inner = json.loads(self.inner('image', 'inspect', ref, label='inner-image')['stdout'])[0]
        self.note(f'image:{ref.split("@")[0]}', {
            'method': method, 'pull_stderr_tail': pulled['stderr'][-400:],
            # Host Docker Desktop uses the containerd store (Id = index digest); the nested
            # engine reports the config digest, so Ids differ by design. Pull/load by digest
            # is content-addressed: the pinned digest must appear in the inner RepoDigests.
            'host_id': host['Id'], 'inner_id': inner['Id'],
            'pinned_digest_in_inner_repo_digests': ref in (inner.get('RepoDigests') or []),
            'inner_repo_digests': inner.get('RepoDigests'), 'architecture': inner['Architecture'],
            'os': inner['Os'], 'rootfs_layers': inner['RootFS'].get('Layers')})

    def build_guest_image(self):
        stage = self.run.dir / 'input'
        stage.mkdir()
        for name in ('Dockerfile', 'HelloServer.java', 'HttpCheck.java'):
            shutil.copyfile(GUEST_SRC / name, stage / name)
        ud = (GUEST_SRC / 'server-user-data.sh').read_bytes().replace(b'\r\n', b'\n')
        (self.run.dir / 'server-user-data.sh').write_bytes(ud)
        self.user_data_sha = hashlib.sha256(ud).hexdigest()
        self.run.docker('cp', str(stage), f'{self.dind}:/mq-input', label='copy-inputs')
        tag = f'mq-lab/java25-http-guest:{self.run.id}'
        self.inner('build', '--pull=false', '--label', self.run.label, '-t', tag, '/mq-input',
                   timeout=300, label='guest-build')
        img = json.loads(self.inner('image', 'inspect', tag, label='guest-image')['stdout'])[0]
        base = self.obs[f'image:{TEMURIN.split("@")[0]}']
        base_layers = base['rootfs_layers'] or []
        self.guest_image = img['Id']
        self.note('guest_image', {
            'tag': tag, 'id': img['Id'], 'architecture': img['Architecture'], 'os': img['Os'],
            'cmd': img['Config'].get('Cmd'), 'entrypoint': img['Config'].get('Entrypoint'),
            'labels': img['Config'].get('Labels'),
            'base_layers_are_prefix': img['RootFS']['Layers'][:len(base_layers)] == base_layers,
            'extra_layers': len(img['RootFS']['Layers']) - len(base_layers),
            'dockerfile_sha256': hashlib.sha256((GUEST_SRC / 'Dockerfile').read_bytes()).hexdigest()})
        catalog = CATALOG.format(image=img['Id'], ami=AMI, alias=AMI_ALIAS, base=TEMURIN)
        (self.run.dir / 'image-catalog.yaml').write_text(catalog, encoding='utf-8')
        self.run.docker('cp', str(self.run.dir / 'image-catalog.yaml'),
                        f'{self.dind}:/mq-input/image-catalog.yaml', label='copy-catalog')

    def start_floci(self):
        floci_ref = FLOCI
        self.inner('run', '-d', '--name', 'floci', '--label', self.run.label, '--cpus', '2',
                   '--memory', '2g', '--pids-limit', '512', '--network', 'host',
                   '-v', '/var/run/docker.sock:/var/run/docker.sock',
                   '-v', '/mq-input/image-catalog.yaml:/etc/floci/image-catalog.yaml:ro',
                   '--tmpfs', '/app/data:rw,size=256m',
                   '-e', f'FLOCI_DOCKER_RESOURCE_NAMESPACE={self.run.id}',
                   '-e', 'FLOCI_STORAGE_MODE=memory',
                   '-e', 'FLOCI_SERVICES_EC2_PUBLISH_SECURITY_GROUP_PORTS=false',
                   '-e', 'FLOCI_SERVICES_EC2_IMAGE_CATALOG_PATH=/etc/floci/image-catalog.yaml',
                   floci_ref, label='inner-floci')
        wait_until(lambda: self.api('describe-vpcs', label='ready').get('Vpcs') is not None, 180, 2)

    # -- guests ---------------------------------------------------------------
    def guest_container(self, instance_id):
        ids = self.inner('ps', '-aq', '--no-trunc', label='guest-find')['stdout'].split()
        for cid in ids:
            obj = json.loads(self.inner('inspect', cid, label='guest-find')['stdout'])[0]
            if f'AWS_EC2_INSTANCE_ID={instance_id}' in (obj['Config'].get('Env') or []):
                return obj
        return None

    def launch(self, subnet_id, label, user_data=True):
        args = ['--image-id', AMI, '--instance-type', 't3.micro', '--count', '1', '--subnet-id', subnet_id]
        if user_data:
            args += ['--user-data', f'file://{self.run.dir / "server-user-data.sh"}']
        t0 = time.time()
        out = self.api('run-instances', *args, label=f'launch:{label}')
        if '_error' in out:
            raise RuntimeError(f'run-instances {label}: {out["_error"]}')
        iid = out['Instances'][0]['InstanceId']
        states = []

        def running():
            inst = self.describe(iid)
            states.append([round(time.time() - t0, 2), inst['State']['Name']])
            return inst if inst['State']['Name'] == 'running' else None
        inst = wait_until(running, 240, 1)
        return {'id': iid, 'launched_at': t0, 'api_running_after_s': round(time.time() - t0, 2),
                'state_trace': states, 'private_ip': inst['PrivateIpAddress'], 'subnet': inst['SubnetId']}

    def describe(self, iid):
        return self.api('describe-instances', '--instance-ids', iid, label='describe')['Reservations'][0]['Instances'][0]

    def http_probe(self, client_cid, ip, label='probe'):
        r = self.inner('exec', client_cid, 'java', '/opt/mq/HttpCheck.java', ip, str(PORT),
                       check=False, timeout=60, label=label)
        body = dict(ln.split('=', 1) for ln in r['stdout'].splitlines() if '=' in ln and not ln.startswith('HTTP'))
        return {'rc': r['rc'], 'stdout': r['stdout'], 'fields': body}

    def wait_http(self, client_cid, server):
        attempts = []
        end = time.time() + 180
        while time.time() < end:
            p = self.http_probe(client_cid, server['private_ip'], label='readiness')
            attempts.append([round(time.time() - server['launched_at'], 2), p['rc'], p['stdout'][:120]])
            if p['rc'] == 0:
                break
            time.sleep(1)
        server['http_attempts'] = attempts
        server['http_ready_after_s'] = attempts[-1][0] if attempts and attempts[-1][1] == 0 else None
        server['first_probe_after_api_running'] = attempts[0] if attempts else None
        return server['http_ready_after_s'] is not None

    # -- grader for the 3.1.1 gate ----------------------------------------------
    def check(self, rec):
        """State + independent HTTP check, from the owned record only."""
        codes, obs = [], {}
        subnets = [s for s in self.api('describe-subnets', label='check-subnets').get('Subnets', [])
                   if s['VpcId'] == rec['vpc_id']]
        target = [s for s in subnets if s['CidrBlock'] == rec['target_cidr'] and s['State'] == 'available']
        stray = [s for s in subnets if s['SubnetId'] != rec['subnet_a'] and s['CidrBlock'] != rec['target_cidr']]
        if len(target) != 1:
            codes.append('target_subnet_missing')
        if stray:
            codes.append('extra_subnet')
        insts = [i for res in self.api('describe-instances', label='check-instances').get('Reservations', [])
                 for i in res['Instances'] if i.get('VpcId') == rec['vpc_id']
                 and i['State']['Name'] not in ('terminated', 'shutting-down')
                 and i['InstanceId'] != rec['client_id']]
        obs['servers'] = [{k: i.get(k) for k in ('InstanceId', 'SubnetId', 'PrivateIpAddress', 'ImageId')}
                          | {'State': i['State']['Name']} for i in insts]
        good = [i for i in insts if target and i['SubnetId'] == target[0]['SubnetId']
                and i['ImageId'] == rec['ami'] and i['State']['Name'] == 'running'
                and ipaddress.ip_address(i['PrivateIpAddress']) in ipaddress.ip_network(rec['target_cidr'])]
        if not insts:
            codes.append('no_server')
        if any(i['SubnetId'] == rec['subnet_a'] for i in insts):
            codes.append('server_in_wrong_subnet')
        if len(insts) != len(good):
            codes.append('misplaced_or_extra_server')
        if len(good) == 1:
            client = self.guest_container(rec['client_id'])
            if client is None:
                return {'verdict': 'env_error', 'codes': ['client_container_missing'], 'observed': obs}
            p = self.http_probe(client['Id'], good[0]['PrivateIpAddress'], label='grader-http')
            obs['http'] = p
            f = p['fields']
            if not (p['rc'] == 0 and f.get('instance') == good[0]['InstanceId']
                    and f.get('served-on') == good[0]['PrivateIpAddress']
                    and f.get('java.version', '').startswith('25')):
                codes.append('http_check_failed')
        verdict = 'pass' if not codes and len(good) == 1 else 'fail'
        return {'verdict': verdict, 'codes': codes, 'observed': obs}

    # -- evidence ---------------------------------------------------------------
    def guest_evidence(self, iid, name):
        c = self.guest_container(iid)
        cid = c['Id']

        def sh(script, label):
            return self.inner('exec', cid, 'sh', '-c', script, check=False, label=label)
        jv = self.inner('exec', cid, 'java', '-version', check=False, label='java-version')
        ev = {
            'container': c['Name'], 'image': c['Image'], 'image_matches_guest_build': c['Image'] == self.guest_image,
            'cmd': c['Config']['Cmd'], 'privileged': c['HostConfig']['Privileged'],
            'memory': c['HostConfig']['Memory'], 'nano_cpus': c['HostConfig']['NanoCpus'],
            'cpu_shares': c['HostConfig']['CpuShares'], 'pids_limit_at_creation': c['HostConfig']['PidsLimit'],
            'port_bindings_inside_nested': c['HostConfig']['PortBindings'],
            'networks': {k: v.get('IPAddress') for k, v in c['NetworkSettings']['Networks'].items()},
            'java_version': (jv['stdout'] + jv['stderr']).strip(),
            'user_data_file_sha256': sh('sha256sum /var/lib/user-data.sh 2>&1', 'ud-sha')['stdout'].split()[:1],
            'user_data_marker': sh('cat /var/log/mq/user-data.marker 2>&1', 'ud-marker')['stdout'].strip(),
            'server_pid_cmdline': sh('p=$(cat /var/log/mq/server.pid 2>/dev/null) && tr "\\0" " " < /proc/$p/cmdline '
                                     '&& echo && grep PPid /proc/$p/status', 'ud-pid')['stdout'].strip(),
            'server_log': sh('cat /var/log/mq/server.log 2>&1 | head -5', 'server-log')['stdout'].strip(),
            'os_release': sh('grep PRETTY_NAME /etc/os-release', 'os')['stdout'].strip(),
        }
        ev['user_data_sha_matches_input'] = ev['user_data_file_sha256'] == [self.user_data_sha]
        upd = self.inner('update', '--pids-limit', '256', cid, check=False, label='pids-after-launch')
        ev['pids_limit_applied_after_launch'] = 256 if upd['rc'] == 0 else upd['stderr'].strip()
        logs = self.run.aws(self.endpoint, 'logs', 'describe-log-streams', '--log-group-name', f'/aws/ec2/{iid}',
                            label='cw-streams')
        ev['cloudwatch_user_data_streams'] = logs['stdout'][:600] if logs['rc'] == 0 else logs['stderr'][-300:]
        if logs['rc'] == 0:
            streams = json.loads(logs['stdout']).get('logStreams', [])
            if streams:
                g = self.run.aws(self.endpoint, 'logs', 'get-log-events', '--log-group-name', f'/aws/ec2/{iid}',
                                 '--log-stream-name', streams[0]['logStreamName'], label='cw-events')
                ev['cloudwatch_user_data_lines'] = [e['message'] for e in json.loads(g['stdout'])['events']] \
                    if g['rc'] == 0 else g['stderr'][-300:]
        self.note(f'guest:{name}', ev)
        return ev

    def scenario(self):
        vpc = self.api('create-vpc', '--cidr-block', VPC_CIDR)['Vpc']['VpcId']
        sa = self.api('create-subnet', '--vpc-id', vpc, '--cidr-block', SUBNET_A)['Subnet']['SubnetId']
        imgs = self.api('describe-images', '--image-ids', AMI, label='catalog-ours')
        bundled = self.api('describe-images', '--image-ids', BUNDLED_AMI, label='catalog-bundled')
        # Floci answers any unknown AMI ID with a synthesized "fallback image" (backed by
        # defaultDockerImage), so replacement shows as the bundled AL2023 metadata being gone.
        b = (bundled.get('Images') or [{}])[0]
        self.case('custom_catalog_replaces_bundled',
                  imgs.get('Images') and imgs['Images'][0]['ImageId'] == AMI
                  and imgs['Images'][0]['Name'] == 'mq-java25-http-preflight'
                  and b.get('Description') != 'Amazon Linux 2023 AMI'
                  and not str(b.get('Name', '')).startswith('al2023-ami'),
                  {'ours': imgs, 'bundled_lookup': bundled})
        client = self.launch(sa, 'client', user_data=False)
        rec = {'vpc_id': vpc, 'subnet_a': sa, 'client_id': client['id'], 'ami': AMI, 'target_cidr': TARGET}
        self.run.save('owned-record', rec)
        ccid = self.guest_container(client['id'])['Id']
        self.note('client', client)

        r = self.check(rec)
        self.case('gate_initial_fails', r['verdict'] == 'fail', r)
        sb = self.api('create-subnet', '--vpc-id', vpc, '--cidr-block', TARGET, label='student-subnet-b')['Subnet']['SubnetId']

        wrong = self.launch(sa, 'server-wrong-subnet-A')
        # API `running` is recorded by launch(); HTTP readiness is polled separately afterwards.
        ready = self.wait_http(ccid, wrong)
        self.case('api_running_and_http_ready_measured_separately', ready,
                  {k: wrong.get(k) for k in ('api_running_after_s', 'http_ready_after_s', 'http_attempts', 'state_trace')}
                  | {'first_probe_after_running_failed': wrong['http_attempts'][0][1] != 0})
        self.note('server_wrong', wrong)
        r = self.check(rec)
        self.case('wrong_subnet_fails_even_though_http_answers',
                  r['verdict'] == 'fail' and 'server_in_wrong_subnet' in r['codes']
                  and wrong['http_ready_after_s'] is not None, r)

        right = self.launch(sb, 'server-target-subnet-B')
        right_ready = self.wait_http(ccid, right)
        self.note('server_right', right)
        r = self.check(rec)
        self.case('stray_server_in_A_still_fails', r['verdict'] == 'fail' and right_ready, r)

        self.api('terminate-instances', '--instance-ids', wrong['id'], label='terminate-wrong')
        wait_until(lambda: self.describe(wrong['id'])['State']['Name'] == 'terminated', 120, 1)
        try:
            gone = wait_until(lambda: self.guest_container(wrong['id']) is None, 60, 1)
        except TimeoutError:
            gone = False
        r = self.check(rec)
        self.case('corrected_placement_passes', r['verdict'] == 'pass', r)
        self.case('cross_subnet_http_via_api_private_ip',
                  r.get('observed', {}).get('http', {}).get('rc') == 0
                  and ipaddress.ip_address(client['private_ip']) in ipaddress.ip_network(SUBNET_A)
                  and ipaddress.ip_address(right['private_ip']) in ipaddress.ip_network(TARGET),
                  {'client_ip': client['private_ip'], 'server_ip': right['private_ip'],
                   'http': r.get('observed', {}).get('http'), 'wrong_container_gone': gone is True})

        ev = self.guest_evidence(right['id'], 'server')
        cev = self.guest_evidence(client['id'], 'client')
        self.case('guest_java_is_25', 'version "25' in ev['java_version'], ev['java_version'])
        self.case('guest_image_provenance',
                  ev['image_matches_guest_build'] and self.obs['guest_image']['base_layers_are_prefix']
                  and self.obs[f'image:{TEMURIN.split("@")[0]}']['pinned_digest_in_inner_repo_digests']
                  and self.obs['guest_image']['architecture'] == 'amd64',
                  {'guest_image': self.obs['guest_image'],
                   'base': self.obs[f'image:{TEMURIN.split("@")[0]}']})
        self.case('server_started_by_user_data',
                  ev['user_data_sha_matches_input'] and right['id'] in ev['user_data_marker']
                  and 'HelloServer.java' in ev['server_pid_cmdline'] and ev['cmd'] == ['tail', '-f', '/dev/null'],
                  {k: ev[k] for k in ('user_data_file_sha256', 'user_data_marker', 'server_pid_cmdline', 'cmd',
                                      'cloudwatch_user_data_streams')} | {'cw': ev.get('cloudwatch_user_data_lines')})
        neg = self.http_probe(ccid, client['private_ip'], label='negative-control')
        self.case('client_without_user_data_has_no_server',
                  'HelloServer' not in cev['server_pid_cmdline'] and neg['rc'] == 3,
                  {'client_marker': cev['user_data_marker'], 'probe_own_ip': neg})

    # -- audit + cleanup --------------------------------------------------------
    def audit(self):
        o = json.loads(self.run.docker('inspect', self.dind, label='audit-outer')['stdout'])[0]
        f = json.loads(self.inner('inspect', 'floci', label='audit-floci')['stdout'])[0]
        a = {'outer': {'privileged': o['HostConfig']['Privileged'], 'cgroupns': o['HostConfig'].get('CgroupnsMode'),
                       'live_ports': o['NetworkSettings']['Ports'], 'mounts': o['Mounts'],
                       'nano_cpus': o['HostConfig']['NanoCpus'], 'memory': o['HostConfig']['Memory'],
                       'pids_limit': o['HostConfig']['PidsLimit'], 'label': o['Config']['Labels'].get('mq.lab')},
             'floci': {'mounts': f['Mounts'], 'network_mode': f['HostConfig']['NetworkMode'],
                       'privileged': f['HostConfig']['Privileged'], 'nano_cpus': f['HostConfig']['NanoCpus'],
                       'memory': f['HostConfig']['Memory'], 'pids_limit': f['HostConfig']['PidsLimit'],
                       'env_keys': sorted(e.split('=', 1)[0] for e in f['Config']['Env'])}}
        ports = o['NetworkSettings']['Ports']
        only_api = bool(ports.get('4566/tcp')) and all(b['HostIp'] == '127.0.0.1' for b in ports['4566/tcp']) \
            and not [p for p, v in ports.items() if v and p != '4566/tcp']
        self.case('pinned_floci_and_temurin_digests_in_nested_engine',
                  all(self.obs[f'image:{r.split("@")[0]}']['pinned_digest_in_inner_repo_digests']
                      for r in (FLOCI, TEMURIN)) and f['Image'] == json.loads(self.inner(
                          'image', 'inspect', FLOCI, label='floci-image-id')['stdout'])[0]['Id'],
                  {r: self.obs[f'image:{r.split("@")[0]}'] for r in (FLOCI, TEMURIN)})
        socket_src = [m['Source'] for m in f['Mounts'] if 'docker.sock' in m['Destination']]
        self.run.save('isolation-audit', a)
        self.case('outer_only_loopback_api_port', only_api, ports)
        self.case('outer_mounts_only_owned_volume',
                  [m.get('Name') for m in o['Mounts']] == [self.volume], o['Mounts'])
        self.case('floci_uses_nested_socket_only', socket_src == ['/var/run/docker.sock'] and
                  all(m['Source'].startswith(('/var/run/docker.sock', '/mq-input/')) for m in f['Mounts']
                      if m['Type'] == 'bind'), f['Mounts'])

    def cleanup(self):
        if self.run.owned('container', self.dind):
            inv = {k: self.inner(*a, check=False, label='final-inventory')['stdout'].splitlines()
                   for k, a in (('containers', ('ps', '-a', '--no-trunc', '--format', '{{json .}}')),
                                ('images', ('images', '--digests', '--format', '{{json .}}')))}
            self.run.save('inner-final-inventory', inv)
            self.inner('logs', 'floci', check=False, label='floci-final-log')
        self.run.remove_owned('container', self.dind)
        self.run.remove_owned('volume', self.volume)
        self.run.remove_owned('network', self.network)


def main(run_id: str) -> dict:
    run = Run(run_id, 'java')
    print(f'java guest run dir: {run.dir}', flush=True)
    before = host_snapshot(run, 'host-before')
    lab, fatal = Lab(run), None
    try:
        lab.bootstrap()
        lab.build_guest_image()
        lab.start_floci()
        lab.audit()
        lab.scenario()
    except BaseException:
        fatal = traceback.format_exc()
        run.save('fatal', {'traceback': fatal})
        print(fatal, flush=True)
    finally:
        try:
            lab.cleanup()
        except Exception as e:
            run.save('cleanup-error', {'error': repr(e)})
        diff = compare_snapshots(before, host_snapshot(run, 'host-after'))
        run.save('host-diff', diff)
    summary = {'part': 'java-ec2-guest', 'run_dir': str(run.dir), 'fatal': fatal is not None,
               'floci_source_commit': FLOCI_SOURCE_COMMIT,
               'cases_total': len(lab.cases), 'cases_ok': sum(c['ok'] for c in lab.cases),
               'cases_bad': [c['name'] for c in lab.cases if not c['ok']],
               'host_inventory_clean': diff['clean'], 'host_diff': diff,
               'java_version': lab.obs.get('guest:server', {}).get('java_version'),
               'timing': {f'{k}.{f}': lab.obs.get(k, {}).get(f) for k in ('server_wrong', 'server_right')
                          for f in ('api_running_after_s', 'http_ready_after_s')}}
    run.save('summary', summary)
    return summary
