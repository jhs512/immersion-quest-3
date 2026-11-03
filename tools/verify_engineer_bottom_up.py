"""Verify the class 1/2 capability map against the actual installed-course bundle.

The map contains identifiers and independently written principles, never source
exam questions. Default verification requires fresh real-grader reports. Use
--execute to regenerate them with the application's public lesson validator.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'tools/redesigned_courses/engineer/bottom-up-coverage.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify(execute=False, structural_only=False, validator=None):
    mapping = read(MAP)
    course = read(ROOT / 'courses/redesigned-courses/engineer-practical.json')
    catalog = next(c for c in read(ROOT / 'tools/redesigned_courses/catalog.json')['courses'] if c['key'] == 'engineer')
    references = {row['id']: row for row in course['lessons']}
    rows = {row['key']: row for row in catalog['lessons']}
    assert len(rows) == len(references) == 62
    assert len(mapping['items']) == len({row['id'] for row in mapping['items']}) == 385
    assert [sum(row['label'] == label for row in mapping['items']) for label in (1, 2)] == [222, 163]
    assert len(mapping['capabilities']) == 183 and mapping['source_text_included'] is False
    order = [row['key'] for row in catalog['lessons']]
    assert [row['id'] for row in catalog['lessons']] == [row['id'] for row in course['lessons']]
    lessons = {}
    for key, row in rows.items():
        raw = (ROOT / 'courses/redesigned' / f'{key}.json').read_bytes()
        lesson = json.loads(raw)
        ref = references[row['id']]
        assert ref['sha256'] == hashlib.sha256(raw).hexdigest(), key
        assert ref['revision'] == lesson['revision'] == row['revision'], key
        lessons[key] = lesson
    count, rejected, accepted, runs = 0, 0, 0, 0
    for addition in mapping['lesson_order']:
        key, after = addition['key'], addition['after']
        assert order.index(key) > order.index(after), key
        # No old lesson may be inserted between a foundation and its extension.
        assert not any(other not in {a['key'] for a in mapping['lesson_order']}
                       for other in order[order.index(after) + 1:order.index(key)]), key
        build = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'tools/build-redesigned-git.py'), '--lesson', key, '--check'],
                               cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        if build.returncode:
            raise ValueError(f'{key}: authored content and built lesson differ: {build.stderr[-2000:]}')
        lesson = lessons[key]
        tasks = lesson['tasks']
        assert all(not task.get('interaction') and task['starter_code'] != task['solution'] for task in tasks), key
        spec_path = ROOT / 'tests/lesson-cases' / f'{key}.json'
        spec = read(spec_path)
        assert len(spec['expected_outputs']) == len(tasks), key
        assert {r['step'] for r in spec['reject']} == set(range(1, len(tasks) + 1)), key
        assert spec['accept'], key
        proof_path = ROOT / 'target/ebu' / f'{key}.json'
        if execute:
            result = subprocess.run([str(validator), str(spec_path), str(proof_path)], cwd=ROOT,
                                    capture_output=True, text=True, encoding='utf-8')
            if result.returncode:
                raise ValueError(f'{key}: {result.stderr[-2500:]}')
        if not structural_only:
            proof = read(proof_path)
            assert proof['passed'] and proof['lesson_sha256'] == references[lesson['id']]['sha256'], key
            assert [s['id'] for s in proof['steps']] == [t['id'] for t in tasks], key
            assert proof['rejected_answers'] == len(spec['reject']), key
            assert proof['accepted_answers'] == len(spec['accept']), key
            authored = read(ROOT / 'tools/redesigned_lessons' / key.replace('-', '_') / 'content.json')
            # Python's one public checker executes every prepared data variant
            # internally. Its public report has one case, not one per variant.
            prepared = authored.get('prepared_cases', {})
            assert all(s['grading_cases'] >= 2 or len(prepared.get(s['id'], [])) >= 2
                       for s in proof['steps']), key
        count += len(tasks)
        rejected += len(spec['reject'])
        accepted += len(spec['accept'])
        runs += sum(len(outputs) for outputs in spec['expected_outputs'])
    assert len(mapping['lesson_order']) == 32 and count == 329
    for cap, definition in mapping['capabilities'].items():
        assert definition.get('name') and definition.get('principle') and definition.get('steps'), cap
        for target in definition['steps']:
            assert target['lesson'] in lessons, (cap, target)
            assert target['step'] in {t['id'] for t in lessons[target['lesson']]['tasks']}, (cap, target)
    for item in mapping['items']:
        assert item['caps'] and all(cap in mapping['capabilities'] for cap in item['caps']), item['id']
    result = dict(passed=True, lessons=32, added_steps=count, course_lessons=62,
                  course_steps=sum(len(l['tasks']) for l in lessons.values()), items=385, capabilities=183,
                  rejected_answers=rejected, accepted_answers=accepted, teacher_runs=runs,
                  real_grader_verified=not structural_only)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--structural-only', action='store_true')
    executable = 'validate_redesigned_lesson' + ('.exe' if sys.platform == 'win32' else '')
    parser.add_argument('--validator', type=Path, default=ROOT / 'target/cert-test/debug/examples' / executable)
    args = parser.parse_args()
    verify(args.execute, args.structural_only, args.validator)
