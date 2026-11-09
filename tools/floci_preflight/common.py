"""Shared safety plumbing for the Floci first-lesson preflight.

Every Docker mutation targets a resource labelled mq.lab=<run>; every AWS CLI call
carries an explicit loopback --endpoint-url and runs with dummy credentials and an
empty owned config file. The original environment is never printed or recorded.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import subprocess
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
TARGET = REPO / 'target' / 'floci-preflight'

FLOCI = 'floci/floci@sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c'
FLOCI_SOURCE_COMMIT = '9be236e2890c2042a6bb819f1a9228be996acd90'
DIND = 'docker@sha256:ecac43e78380d9b9d3bd24f0ab42b370f6391a1a06a66065c10a00b9d6d57a3e'
TEMURIN = ('public.ecr.aws/docker/library/eclipse-temurin@sha256:'
           'c7c3d0bdf7f2bbc5a05a6712ed334d198360105634ea9adf76fca94f381b1e3f')
AWS = r'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
GIT_BASH = r'C:\Program Files\Git\bin\bash.exe'
REGION = 'us-east-1'


def new_run_id(prefix: str = 'mq-floci-pf') -> str:
    return f"{prefix}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


class Run:
    """One owned run: its directory, event log and child-process environment."""

    def __init__(self, run_id: str, part: str):
        self.id = run_id
        self.label = f'mq.lab={run_id}'
        self.dir = TARGET / run_id / part
        self.dir.mkdir(parents=True, exist_ok=False)
        self.events: list[dict] = []
        self.removed_mounts: list[dict] = []
        self.empty_aws = self.dir / 'empty-aws-config'
        self.empty_aws.write_text('')
        self.env = self._child_env()

    def _child_env(self) -> dict:
        env = {k: v for k, v in os.environ.items() if not k.startswith('AWS_')}
        env.update(
            AWS_ACCESS_KEY_ID='test', AWS_SECRET_ACCESS_KEY='test', AWS_DEFAULT_REGION=REGION,
            AWS_REGION=REGION, AWS_CONFIG_FILE=str(self.empty_aws),
            AWS_SHARED_CREDENTIALS_FILE=str(self.empty_aws), AWS_EC2_METADATA_DISABLED='true',
            AWS_PAGER='', AWS_CLI_AUTO_PROMPT='off')
        env['PATH'] = str(pathlib.Path(AWS).parent) + os.pathsep + env.get('PATH', '')
        return env

    # -- process helpers -------------------------------------------------
    def cmd(self, argv, *, timeout=120, check=True, label=None, env=None, input=None, cwd=None):
        start = time.time()
        try:
            r = subprocess.run(argv, env=env or self.env, capture_output=True, text=True,
                               encoding='utf-8', errors='replace', timeout=timeout,
                               input=input, cwd=cwd)
            rc, out, err = r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired as e:
            rc, out, err = 'timeout', str(e.stdout or ''), str(e.stderr or '')
        event = dict(t=datetime.datetime.now().isoformat(timespec='milliseconds'), label=label,
                     argv=[str(a) for a in argv], rc=rc, seconds=round(time.time() - start, 3),
                     stdout=out, stderr=err)
        self.events.append(event)
        self.save('events', self.events)
        if check and rc != 0:
            raise RuntimeError(f'{label or argv[:3]} rc={rc}: {err[-1200:]}')
        return event

    def docker(self, *args, **kw):
        return self.cmd(['docker', *args], **kw)

    def aws(self, endpoint: str, service: str, action: str, *args, check=False, label=None,
            timeout=60):
        assert endpoint.startswith('http://127.0.0.1:'), endpoint
        argv = [AWS, '--endpoint-url', endpoint, '--region', REGION, '--output', 'json',
                '--cli-connect-timeout', '5', '--cli-read-timeout', '30',
                service, action, *args]
        return self.cmd(argv, check=check, label=label or f'{service}:{action}', timeout=timeout)

    def save(self, name, obj):
        (self.dir / f'{name}.json').write_text(
            json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

    # -- owned-resource helpers -----------------------------------------
    def owned(self, kind: str, name: str) -> bool:
        """True when <kind> <name> exists and carries exactly this run's label."""
        r = self.docker(kind, 'inspect', name, check=False, label=f'owned?{kind}')
        if r['rc'] != 0:
            return False
        obj = json.loads(r['stdout'])[0]
        labels = (obj.get('Config') or {}).get('Labels') if kind == 'container' else obj.get('Labels')
        if (labels or {}).get('mq.lab') != self.id:
            raise RuntimeError(f'refusing to touch {kind} {name}: label mismatch')
        return True

    def remove_owned(self, kind: str, name: str):
        if not self.owned(kind, name):
            return
        if kind != 'container':
            self.docker(kind, 'rm', name, label='cleanup')
            return
        # Record the container's mounts first; `-v` removes only its anonymous volumes.
        obj = json.loads(self.docker('container', 'inspect', name, label='cleanup-mounts')['stdout'])[0]
        anon = []
        for m in obj['Mounts']:
            if m.get('Type') != 'volume':
                continue
            v = self.docker('volume', 'inspect', m['Name'], check=False, label='cleanup-mount-kind')
            if v['rc'] == 0 and 'com.docker.volume.anonymous' in (json.loads(v['stdout'])[0].get('Labels') or {}):
                anon.append(m['Name'])  # named owned volumes are removed separately by label
        self.docker('rm', '-f', '-v', name, label='cleanup')
        left = [v for v in anon if self.docker('volume', 'inspect', v, check=False,
                                               label='cleanup-verify')['rc'] == 0]
        self.removed_mounts.append({'container': name, 'mounts': obj['Mounts'], 'volumes_left': left})
        self.save('removed-container-mounts', self.removed_mounts)
        if left:
            raise RuntimeError(f'anonymous volumes of {name} survived rm -v: {left}')

    def published_port(self, container: str, inner_port: str = '4566/tcp') -> int:
        r = self.docker('port', container, inner_port, label='port')
        lines = [ln.strip() for ln in r['stdout'].splitlines() if ln.strip()]
        if len(lines) != 1 or not lines[0].startswith('127.0.0.1:'):
            raise RuntimeError(f'unexpected port publication for {container}: {lines}')
        return int(lines[0].rsplit(':', 1)[1])


def wait_until(fn, seconds=90, interval=1.0):
    end = time.time() + seconds
    last = None
    while time.time() < end:
        try:
            value = fn()
            if value:
                return value
        except Exception as e:  # recorded by the caller's event log
            last = e
        time.sleep(interval)
    raise TimeoutError(f'readiness timeout after {seconds}s (last={last!r})')


# -- host inventory -----------------------------------------------------
def host_snapshot(run: Run, name: str) -> dict:
    def lines(r):
        return [json.loads(x) for x in r['stdout'].splitlines() if x.strip()]
    net_ids = run.docker('network', 'ls', '-q', '--no-trunc', label='snap')['stdout'].split()
    networks = json.loads(run.docker('network', 'inspect', *net_ids, label='snap')['stdout']) if net_ids else []
    info = json.loads(run.docker('info', '--format', '{{json .}}', label='snap')['stdout'])
    snap = {
        'taken_at': datetime.datetime.now().isoformat(timespec='milliseconds'),
        'daemon': {k: info.get(k) for k in ('ID', 'Name', 'ServerVersion', 'SystemTime',
                                             'Containers', 'ContainersRunning', 'Images')},
        'context': run.docker('context', 'show', label='snap')['stdout'].strip(),
        'contexts': lines(run.docker('context', 'ls', '--format', '{{json .}}', label='snap')),
        'containers': lines(run.docker('ps', '-a', '--no-trunc', '--format', '{{json .}}', label='snap')),
        'networks': networks,
        'volumes': lines(run.docker('volume', 'ls', '--format', '{{json .}}', label='snap')),
    }
    run.save(name, snap)
    return snap


def compare_snapshots(before: dict, after: dict) -> dict:
    # `docker ps` Status/RunningFor are relative-time strings ("8 hours ago") that drift on
    # their own; the State field still records any real start/stop.
    volatile = {'Status', 'RunningFor'}

    def norm(f, v):
        # `docker ps` lists a container's networks in no stable order (seen after a daemon restart).
        return ','.join(sorted(v.split(','))) if f == 'Networks' and isinstance(v, str) else v

    def by(items, key):
        return {i[key]: {f: norm(f, v) for f, v in i.items() if f not in volatile} for i in items}
    diff = {}
    for kind, key in [('containers', 'ID'), ('networks', 'Id'), ('volumes', 'Name')]:
        b, a = by(before[kind], key), by(after[kind], key)
        changed = sorted(k for k in set(b) & set(a)
                         if json.dumps(b[k], sort_keys=True) != json.dumps(a[k], sort_keys=True))
        diff[kind] = {'added': sorted(set(a) - set(b)), 'removed': sorted(set(b) - set(a)),
                      'changed': changed}
        if kind == 'containers':
            diff[kind]['changed_detail'] = {k: {f: [b[k].get(f), a[k].get(f)] for f in b[k]
                                                if b[k].get(f) != a[k].get(f)} for k in changed}
    # The built-in bridge gets a new id only when the daemon starts; flag it so an external
    # Docker Desktop restart is not mistaken for (or hidden behind) this run's own changes.
    bridges = [[n['Id'], n['Created']] for s in (before, after) for n in s['networks'] if n['Name'] == 'bridge']
    diff['daemon_restart_suspected'] = len({b[0] for b in bridges}) > 1
    diff['bridge_before_after'] = bridges
    diff['context'] = {'before': before['context'], 'after': after['context'],
                       'contexts_equal': before['contexts'] == after['contexts']}
    clean = all(not diff[k]['added'] and not diff[k]['removed'] and not diff[k]['changed']
                for k in ('containers', 'networks', 'volumes')) and before['context'] == after['context'] \
        and diff['context']['contexts_equal']
    diff['clean'] = clean
    return diff
