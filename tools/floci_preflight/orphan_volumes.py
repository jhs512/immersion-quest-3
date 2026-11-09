"""Remove anonymous volumes a past run created implicitly (image VOLUME), and nothing else.

Ownership proof: the volume name appears as a Type=volume mount in a recorded inspect of a
container whose Config.Labels mq.lab equals that run id (events.json). Before removal the
volume must still exist, be labelled anonymous, be absent from host-before, and be referenced
by no container. The result is written to <run>/ownership-cleanup.json, separate from the
run's raw host diff.

    python tools/floci_preflight/orphan_volumes.py <run-id> [--apply]
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys

from common import TARGET


def docker(*args):
    r = subprocess.run(['docker', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, r.stdout, r.stderr


def proven_volumes(run_id: str) -> dict[str, dict]:
    proven = {}
    for events in (TARGET / run_id).glob('*/events.json'):
        for e in json.loads(events.read_text(encoding='utf-8')):
            argv = e.get('argv') or []
            if e.get('rc') != 0 or argv[:1] != ['docker'] or 'inspect' not in argv[1:3]:
                continue
            try:
                objs = json.loads(e['stdout'])
            except (json.JSONDecodeError, KeyError):
                continue
            for o in objs:
                if (o.get('Config') or {}).get('Labels', {}).get('mq.lab') != run_id:
                    continue
                for m in o.get('Mounts', []):
                    if m.get('Type') == 'volume':
                        proven[m['Name']] = {'container': o['Name'], 'destination': m['Destination'],
                                             'evidence': str(events.relative_to(TARGET))}
    return proven


def main(run_id: str, apply: bool) -> dict:
    before_names = set()
    for snap in (TARGET / run_id).glob('*/host-before.json'):
        before_names |= {v['Name'] for v in json.loads(snap.read_text(encoding='utf-8'))['volumes']}
    actions = []
    for name, proof in sorted(proven_volumes(run_id).items()):
        rc, out, _ = docker('volume', 'inspect', name)
        if rc != 0:
            actions.append({'volume': name, 'proof': proof, 'action': 'already_absent'})
            continue
        labels = json.loads(out)[0].get('Labels') or {}
        _, refs, _ = docker('ps', '-a', '--no-trunc', '--filter', f'volume={name}', '--format', '{{.ID}}')
        refs = refs.split()
        checks = {'anonymous_label': 'com.docker.volume.anonymous' in labels,
                  'absent_from_host_before': name not in before_names,
                  'unreferenced': not refs}
        entry = {'volume': name, 'proof': proof, 'checks': checks, 'referenced_by': refs}
        if all(checks.values()) and apply:
            rc, _, err = docker('volume', 'rm', name)
            entry['action'] = 'removed' if rc == 0 else f'remove_failed: {err.strip()}'
        else:
            entry['action'] = 'kept' if not all(checks.values()) else 'would_remove'
        actions.append(entry)
    record = {'run_id': run_id, 'at': datetime.datetime.now().isoformat(timespec='seconds'),
              'applied': apply, 'actions': actions}
    if apply:
        (TARGET / run_id / 'ownership-cleanup.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    return record


if __name__ == '__main__':
    print(json.dumps(main(sys.argv[1], '--apply' in sys.argv), indent=1))
