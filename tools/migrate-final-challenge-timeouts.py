"""One-time source migration: restore old checker timeouts and scope new limits to new steps.

The base is the public app build 152 source commit. Existing legacy limits come from its Git blob,
never from an inferred default. Only lessons with one of this plan's new reserved challenge IDs
are touched. Re-running is harmless.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('apply_finals', ROOT / 'tools/apply-final-challenges.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    for source in sorted((ROOT / 'tools/final_challenges').glob('*.py')):
        if not source.stem.startswith(('aice_', 'engineer_')):
            continue
        definition = module.spec_for(source.stem.replace('_', '-'))
        if not definition.get('prepared_timeout_seconds'):
            continue
        path = ROOT / 'tools/redesigned_lessons' / definition['key'].replace('-', '_') / 'content.json'
        current = module.load(path)
        step = definition['step']['id']
        if not any(t['id'] == step for t in current['tasks']):
            continue
        old = json.loads(subprocess.check_output(['git', 'show', '73c7e7d:' + path.relative_to(ROOT).as_posix()], cwd=ROOT))
        if 'prepared_timeout_seconds' in old:
            current['prepared_timeout_seconds'] = old['prepared_timeout_seconds']
        else:
            current.pop('prepared_timeout_seconds', None)
        current.setdefault('prepared_task_timeout_seconds', {})[step] = definition['prepared_timeout_seconds']
        module.dump(path, current)
        print(definition['key'] + ': legacy timeout restored; final has its own limit')


if __name__ == '__main__':
    main()
