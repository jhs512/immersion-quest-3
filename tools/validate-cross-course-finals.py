"""Run only new finals through the real public grader; preserve exact-byte passing checkpoints.

Existing problems are separately protected by publish-final-challenges.only_appended. No source
or bundle is modified here. Full lesson-case files stay unchanged; narrowed replay cases live in
target. A failed problem does not stop independent lessons from being validated.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'target/codex-final-challenges'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lessons', nargs='+')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    keys = args.lessons or [l['key'] for c in catalog['courses'] if c['key'] in ('aice', 'engineer') for l in c['lessons']]
    OUT.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    if not env.get('MOLIP_TCC'):
        candidates = (Path(env.get('LOCALAPPDATA', '')) / 'Temp').glob('mq3-player-pilot-installed-*/course-tools/tcc-0.9.27/tcc/tcc.exe')
        for candidate in candidates:
            if candidate.is_file():
                env['MOLIP_TCC'] = str(candidate)
                break
    results = []
    for key in keys:
        raw = (ROOT / f'courses/redesigned/{key}.json').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        evidence_path = ROOT / f'target/final-challenges/{key}.json'
        evidence = json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else {}
        if not args.force and evidence.get('passed') is True and evidence.get('lesson_sha256') == digest:
            row = dict(key=key, passed=True, reused_exact_hash=True)
        else:
            lesson = json.loads(raw)
            cases = json.loads((ROOT / f'tests/lesson-cases/{key}.json').read_text(encoding='utf-8'))
            cases['only_last'] = True
            cases['expected_outputs'] = cases['expected_outputs'][-1:]
            if 'expected_images' in cases:
                cases['expected_images'] = cases['expected_images'][-1:]
            for field in ('accept', 'reject'):
                cases[field] = [r for r in cases.get(field, []) if r['step'] == len(lesson['tasks'])]
            narrowed = OUT / f'{key}-last.json'
            narrowed.write_text(json.dumps(cases, ensure_ascii=False), encoding='utf-8')
            started = time.monotonic()
            with (OUT / f'{key}.log').open('w', encoding='utf-8') as log:
                try:
                    result = subprocess.run(['cargo', 'run', '--quiet', '--locked', '--example', 'validate_redesigned_lesson', '--',
                        str(narrowed), str(evidence_path)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=1200)
                    row = dict(key=key, passed=result.returncode == 0, seconds=round(time.monotonic()-started, 1))
                except subprocess.TimeoutExpired:
                    row = dict(key=key, passed=False, timeout=True)
        results.append(row)
        (OUT / 'cross-course-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(json.dumps(row), flush=True)
    raise SystemExit(any(not r['passed'] for r in results))


if __name__ == '__main__':
    main()
