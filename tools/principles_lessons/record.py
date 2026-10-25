"""Replay a built lesson through the real grader and keep each demo run's actual output.

The outputs become tests/lesson-cases/<key>.json expected_outputs (via make.py). A recorded output is
evidence of what the engine printed, not a target: read the summary and check every narration claim
against it before keeping it. Usage: python tools/principles_lessons/record.py <key> [<key> ...]
"""
import json
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys', nargs='+')
    parser.add_argument('--runner', type=Path, help='already-built real replay executable')
    args = parser.parse_args()
    failed = False
    for key in args.keys:
        lesson = ROOT / 'courses/redesigned' / f'{key}.json'
        cases = ROOT / 'tests/lesson-cases' / f'{key}.json'
        command = [str(args.runner.resolve()), str(lesson), str(cases)] if args.runner else ['cargo', 'run', '-q', '--example', 'replay_lesson_outputs', '--', str(lesson), str(cases)]
        run = subprocess.run(command,
                             cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        if run.returncode:
            raise SystemExit(run.stderr[-3000:])
        report = json.loads(run.stdout)
        problems = []
        recorded = []
        for step in report['steps']:
            recorded.append([o.get('stdout', '') for o in step['outputs']])
            if step['starter_passes'] != {'Ok': False}:
                problems.append(f"step {step['step']}: starter result {step['starter_passes']}")
            if not step['solution'].get('passed'):
                problems.append(f"step {step['step']}: solution fails {json.dumps(step['solution'], ensure_ascii=False)[:800]}")
            if any('error' in o for o in step['outputs']):
                problems.append(f"step {step['step']}: a demo run could not start {step['outputs']}")
        for answer in report['answers']:
            passed = answer['verdict'].get('passed')
            if (answer['kind'] == 'accept') != bool(passed):
                problems.append(f"{answer['kind']} step {answer['step']} ({answer['reason']}): {json.dumps(answer['verdict'], ensure_ascii=False)[:800]}")
        out = HERE / 'recorded' / f'{key}.json'
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(recorded, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
        (ROOT / '.scratch/pe').mkdir(parents=True, exist_ok=True)
        (ROOT / '.scratch/pe' / f'{key}.replay.json').write_text(run.stdout, encoding='utf-8')
        print(f'{key}: {len(recorded)} steps recorded, {len(report["answers"])} answers checked')
        for problem in problems:
            print('  PROBLEM', problem)
        failed = failed or bool(problems)
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
