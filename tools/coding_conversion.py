"""Replace answer-picking steps of a lesson with real coding steps (2026-10-29 user decision).

A converted step changes the problem's essence (pick a value -> write the code), so it gets a new
stable step code; `issue_progress::learned_tasks` carries stable codes across revisions, and the old
choice pass must not count as the new coding skill. Old completions stay with the old step and the old
revision. Specs live in tools/coding_conversions/<lesson-key>.py (SPECS, optional OPENING).

  python tools/coding_conversion.py apply <key>     # write content, PRD, review, cases, revision
  python tools/coding_conversion.py record <key>    # build + validator in record mode -> outputs into cases
  python tools/coding_conversion.py verify <key>    # build + normal validator -> target/mcq/<key>.json
  python tools/coding_conversion.py all <key>       # apply, record, apply outputs, verify
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/coding_conversions'))
from lesson_prd import approve  # noqa: E402
from lesson_registry import load_registry  # noqa: E402
import narration_review  # noqa: E402

CATALOG = ROOT / 'tools/redesigned_courses/catalog.json'
EVIDENCE = ('2026-10-29 사용자(Codex 경유): 「정처기 에서도 코딩문제에서는 객관식 다 지우자 에이쓰에서도」 「지우는게 아니라 바꾸자 '
            '객관식에서 순수 코딩 문제로」. 코드의 값·식·설정을 고르던 스텝을 직접 코드를 쓰고 실행해 채점하는 스텝으로 바꾸고 새 스텝 코드를 '
            '부여했어요(Claude Code, Codex 경유). 순수 이론 문항과 수업·챕터·단원 목표는 그대로예요. 분류: '
            '.scratch/coding-conversion-trace-reset/classification.json. 사용자가 이 PRD 파일 자체를 열람했다고 주장하지 않아요.')


def new_step_id(old):
    # Reproducible, version-4 formatted (the PRD validator accepts only UUIDv4 resource codes).
    seed = hashlib.sha256(f'mq3:coding-conversion:2026-10-29:{old}'.encode()).digest()[:16]
    return 'stp_' + str(uuid.UUID(bytes=seed, version=4))


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dump(path, value, indent=2):
    text = json.dumps(value, ensure_ascii=False, indent=indent) + '\n'
    newline = '\r\n' if path.exists() and b'\r\n' in path.read_bytes() else '\n'
    if not path.exists() or path.read_text(encoding='utf-8') != text:
        path.write_text(text, encoding='utf-8', newline=newline)


def specs_for(key):
    path = ROOT / 'tools/coding_conversions' / (key.replace('-', '_') + '.py')
    module = importlib.util.spec_from_file_location('conversion_' + key.replace('-', '_'), path)
    loaded = importlib.util.module_from_spec(module)
    module.loader.exec_module(loaded)
    return loaded


def row(key):
    return next(r for r in load_registry() if r['key'] == key)


TASK_FIELDS = ('title', 'goal', 'question', 'language', 'starter_code', 'solution', 'entry_file', 'files', 'tests', 'variations',
               'checker', 'hints', 'code_flow', 'narration')


def build_task(old, spec):
    task = {'id': spec['new']}
    for field in TASK_FIELDS:
        if field in spec:
            task[field] = copy.deepcopy(spec[field])
    task.setdefault('language', old['language'])
    task.setdefault('tests', [])
    task['required'] = old.get('required', True)
    if old.get('supporting_materials'):
        task['supporting_materials'] = old['supporting_materials']
    # Field order as the other authored tasks: identity, text, code, grading, narration.
    order = ['id', 'title', 'goal', 'question', 'language', 'starter_code', 'solution', 'entry_file', 'files', 'tests',
             'variations', 'checker', 'hints', 'required', 'code_flow', 'supporting_materials', 'narration']
    return {k: task[k] for k in order if k in task}


def apply(key):
    module = specs_for(key)
    specs = module.SPECS
    folder = ROOT / 'tools/redesigned_lessons' / row(key)['folder']
    content_path, prd_path = folder / 'content.json', folder / 'approved-prd.json'
    content, prd = load_json(content_path), load_json(prd_path)
    cases_path = ROOT / 'tests/lesson-cases' / f'{key}.json'
    cases = load_json(cases_path)
    if cases.pop('only_last', False):
        # A converted lesson is validated step by step: every starter fails, every solution passes and
        # every narration's real outputs are pinned. Empty entries are filled by `record`.
        cases['expected_outputs'] = [[] for _ in content['tasks'][:-1]] + cases['expected_outputs']
    ledger = narration_review.load_ledger()
    exceptions_path = ROOT / 'tools/redesigned_lessons/narration-target-exceptions.json'
    exceptions = load_json(exceptions_path)
    steps = [s for c in prd['chapters'] for u in c['units'] for s in u['steps']]
    decisions = []
    for spec in specs:
        spec['new'] = new_step_id(spec['old'])
        index = next(i for i, t in enumerate(content['tasks']) if t['id'] in (spec['old'], spec['new']))
        old_task = content['tasks'][index]
        # Choice steps, and (2026-10-30 user decision) code-reading answer fields: typing what given code prints.
        if old_task['id'] == spec['old'] and (old_task.get('interaction') or {}).get('kind') not in ('choice', 'fill', 'fill_fields'):
            raise ValueError(f"{key}: {spec['old']} is not an answer-picking or answer-typing step")
        content['tasks'][index] = build_task(old_task, spec)
        if 'prepared_cases' in spec:
            content.setdefault('prepared_cases', {}).pop(spec['old'], None)
            content['prepared_cases'][spec['new']] = spec['prepared_cases']
        for field in ('prepared_probes', 'prepared_task_timeout_seconds'):
            if field in spec:
                content.setdefault(field, {}).pop(spec['old'], None)
                content[field][spec['new']] = spec[field]
        step = next(s for s in steps if s['id'] in (spec['old'], spec['new']))
        step.update(id=spec['new'], title=spec['title'], objectives=spec['objectives'], core_flow=spec['core_flow'])
        if 'complexity' in spec:
            step['complexity'] = spec['complexity']
        if prd['representative'].get('step_id') == spec['old']:
            prd['representative']['step_id'] = spec['new']
        stale = folder / 'narration_cache' / f"{spec['old']}.json"
        if stale.exists():
            stale.unlink()
        ledger['steps'].pop(spec['old'], None)
        exceptions = [e for e in exceptions if e['step_id'] != spec['old']]
        for text, reason in spec.get('caption_only', {}).items():
            if not any(e['step_id'] == spec['new'] and e['text'] == text for e in exceptions):
                exceptions.append(dict(lesson=key, step_id=spec['new'], text=text, reason=reason))
        decisions.append(dict(lesson=key, step=spec['new'], checked=spec.get('review', {}), findings=[]))
        number = index + 1
        if 'outputs' in spec:
            cases['expected_outputs'][index] = spec['outputs']
        for field in ('reject', 'accept'):
            cases[field] = [c for c in cases.get(field, []) if c['step'] != number]
            cases[field] += [dict(step=number, replacements=r[0], reason=r[1]) for r in spec.get(field, [])]
            cases[field].sort(key=lambda c: c['step'])
    # Keep the PRD's own record of grading: a chapter-free note for converted steps.
    if EVIDENCE not in prd['approval']['evidence']:
        evidence = prd['approval']['evidence'] + ' ' + EVIDENCE
    else:
        evidence = prd['approval']['evidence']
    for field in ('scope', 'grading', 'narration'):
        extra = getattr(module, 'PRD_' + field.upper(), None)
        if extra:
            prd[field] = extra
    prd = approve({k: v for k, v in prd.items() if k != 'approval'} | {'approval': {'status': 'draft'}}, prd['approval']['by'], evidence)
    # A converted final challenge stays the lesson's challenge under its new step code.
    for course_dir in (ROOT / 'tools/redesigned_courses').iterdir():
        challenges_path = course_dir / 'lesson-challenges.json'
        if challenges_path.exists():
            challenges = load_json(challenges_path)
            item = challenges['lessons'].get(key)
            moved = {s['old']: s['new'] for s in specs}
            if item and item['task_id'] in moved:
                item['task_id'] = moved[item['task_id']]
                dump(challenges_path, challenges)
    dump(content_path, content)
    dump(prd_path, prd)
    dump(cases_path, cases)
    dump(exceptions_path, exceptions)
    narration_review.save_ledger(ledger)
    if getattr(module, 'OPENING', None):
        openings_path = ROOT / 'tools/redesigned_lessons/narration-openings.json'
        openings = load_json(openings_path)
        openings[key] = module.OPENING
        dump(openings_path, openings)
    # Revision: one step up from what is published (origin/main), once, however often this lesson is re-applied.
    catalog = load_json(CATALOG)
    committed = json.loads(subprocess.check_output(['git', 'show', 'origin/main:tools/redesigned_courses/catalog.json'], cwd=ROOT))
    for course, base in zip(catalog['courses'], committed['courses']):
        for item, was in zip(course['lessons'], base['lessons']):
            if item['key'] == key and item['revision'] == was['revision']:
                prefix, number = was['revision'].rsplit('-', 1)
                item['revision'] = f'{prefix}-{int(number) + 1}'
    dump(CATALOG, catalog)
    ledger = narration_review.load_ledger()
    narration_review.record(decisions, ledger)
    narration_review.save_ledger(ledger)
    print(f'{key}: {len(specs)} steps converted')


def build(key):
    subprocess.run([sys.executable, 'tools/build-redesigned-git.py', '--lesson', key], cwd=ROOT, check=True)


def validate(key, record=False):
    env = dict(os.environ)
    if record:
        env['MQ3_VALIDATE_RECORD'] = '1'
    out = ROOT / 'target/mcq' / (f'{key}.record.json' if record else f'{key}.json')
    run = subprocess.run(['cargo', 'run', '--quiet', '--example', 'validate_redesigned_lesson', '--',
                          f'tests/lesson-cases/{key}.json', str(out)], cwd=ROOT, env=env)
    evidence = load_json(out)
    if run.returncode != 0:
        raise SystemExit(f"{key}: {evidence.get('error')}")
    return evidence


def take_outputs(key):
    """Copy recorded narration outputs of the converted steps into the lesson cases."""
    evidence = load_json(ROOT / 'target/mcq' / f'{key}.record.json')
    cases_path = ROOT / 'tests/lesson-cases' / f'{key}.json'
    cases = load_json(cases_path)
    converted = {new_step_id(s['old']) for s in specs_for(key).SPECS}
    for index, step in enumerate(evidence['steps']):
        if step['id'] in converted or cases['expected_outputs'][index] == []:
            cases['expected_outputs'][index] = step['teacher_outputs']
            # A lesson that pins figures pins them per narrated run too; the converted narration runs twice.
            if 'expected_images' in cases:
                cases['expected_images'][index] = step['teacher_images']
            print(f"  step {index + 1}: {step['teacher_outputs']}")
    dump(cases_path, cases)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['apply', 'record', 'verify', 'all', 'prompts'])
    parser.add_argument('key')
    args = parser.parse_args()
    if args.command == 'prompts':
        # Sentences the meaning review must cover, and those the spec has not yet noted.
        for spec in specs_for(args.key).SPECS:
            for prompt in narration_review.prompts({'narration': spec['narration']}):
                mark = 'ok ' if prompt['text'] in spec.get('review', {}) else 'TODO'
                print(f"{mark} {spec['title']}: {prompt['text']}")
            for kind in ('reject', 'accept'):
                for replacements, reason in spec.get(kind, []):
                    code = spec['solution']
                    for before, after in replacements:
                        if code.count(before) != 1:
                            print(f"TODO {kind} patch not unique ({code.count(before)}): {spec['title']}: {reason}: {before!r}")
                            break
                        code = code.replace(before, after, 1)
            import narration_openings
            try:
                narration_openings.overview_text({'id': 'new', 'title': spec['title'], 'narration': spec['narration']})
            except ValueError as error:
                print(f"TODO overview: {error}")
        raise SystemExit
    if args.command in ('apply', 'all'):
        apply(args.key)
    if args.command in ('record', 'all'):
        build(args.key)
        validate(args.key, record=True)
        take_outputs(args.key)
    if args.command in ('verify', 'all'):
        build(args.key)
        evidence = validate(args.key)
        print(f"{args.key}: verified {len(evidence['steps'])} steps, rejected {evidence['rejected_answers']}, accepted {evidence['accepted_answers']}")
