"""Reproduce adjacent authoring in disposable files for the fixed native pilot.

The model and approval below are synthetic validation inputs, never real approval.
No GitHub requests, real lessons, installation, or learner records are modified.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

from content_review import Artifact, ContentTree
from lesson_prd import approve, policy_revision
from review_pilot_candidate import materialize

ROOT = Path(__file__).resolve().parents[1]


def synthetic_prd(lesson):
    chapters = copy.deepcopy(lesson['chapters'])
    tasks = {task['id']: task for task in lesson['tasks']}
    for chapter in chapters:
        for unit in chapter['units']:
            for step in unit['steps']:
                step.update(title=tasks[step['id']]['title'], core_flow='격리된 개발 fixture에서 출력과 제출을 검증한다.')
    artifacts = [dict(path=path, text=(ROOT / path).read_text(encoding='utf-8'))
                 for path in ['docs/content-rules.md', 'docs/voice.md']]
    document = dict(schema_version=1, id=lesson['id'], title='격리된 개발 검증용 PRD',
        course='플레이어 검증 코스', audience='자동 검사 전용 fixture', objectives=lesson['objectives'],
        chapters=chapters,
        policy_snapshot=dict(artifacts=artifacts, revision=policy_revision(artifacts),
                             rules=['실제 수업 제작·사용자 승인으로 취급하지 않는다.']),
        sources=[dict(url='https://example.invalid/mq3-validation', checked_at='synthetic-fixture',
                      finding='외부 교육 사실을 주장하지 않는 자동 검사 입력이다.', certainty='검증용 가짜 자료')],
        representative=dict(step_id=lesson['tasks'][0]['id'], **{key: '자동 검사 전용 fixture'
            for key in ['prompt', 'starter_state', 'expected_action', 'acceptance', 'reset', 'narration']}),
        approval={'status': 'draft'})
    for key in ['prerequisites', 'scope', 'out_of_scope', 'grading', 'reset', 'narration', 'verification']:
        document[key] = ['실제 학습 콘텐츠가 아닌 격리된 자동 검사 입력이다.']
    return approve(document, 'synthetic-fixture-only', 'Not a human approval; disposable validation fixture only')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / 'tests/fixtures/player-pilot/a'
    lesson_bytes = (fixture / 'lesson.json').read_bytes()
    lesson = json.loads(lesson_bytes)
    course = json.loads((fixture / 'course.json').read_text(encoding='utf-8'))
    task = lesson['tasks'][0]
    step = lesson['chapters'][0]['units'][0]['steps'][0]
    goal = Artifact(task['id'] + '/goal', 'goal', '\n'.join(step['objectives']))
    flow = Artifact(task['id'] + '/core_flow', 'core_flow', '준비된 숫자 3을 출력한다.')
    content = Artifact(task['id'] + '/content', 'content', task['goal'])
    state, ledger = output / 'tree.json', output / 'review.sqlite3'
    ContentTree([goal, flow, content], {flow.key: goal.key, content.key: flow.key}).save(state)
    (output / 'prd.json').write_text(json.dumps(synthetic_prd(lesson), ensure_ascii=False), encoding='utf-8')
    worker = output / 'synthetic-model.py'
    worker.write_text('''import json, sys
request = json.load(sys.stdin)
source = request['input']['source_after']['text']
if '실패 검증' in source:
    sys.exit(7)
if request['operation'] == 'assess':
    result = {'change_required': '제출 순서' in source, 'reason': 'Synthetic fixture decision only'}
else:
    result = {'text': '숫자 3을 출력한 뒤 제출하세요.'}
print(json.dumps(result, ensure_ascii=False))
''', encoding='utf-8')
    config = output / 'model.json'
    config.write_text(json.dumps(dict(command=[sys.executable, '-X', 'utf8', str(worker)],
        model_revision='synthetic-review-pilot-v1', prd='prd.json',
        target_steps={artifact.key: task['id'] for artifact in [goal, flow, content]})), encoding='utf-8')
    def command(name, *extra):
        return subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'tools/content_review_command.py'),
            name, '--ledger', str(ledger), *map(str, extra)], capture_output=True, text=True, encoding='utf-8', timeout=20)
    def apply(text):
        replacement = output / 'replacement.json'
        replacement.write_text(json.dumps(dict(key=flow.key, layer=flow.layer, text=text)), encoding='utf-8')
        return command('apply', '--state', state, '--model-config', config, '--replacement', replacement)
    def export(directory):
        candidate, raw = materialize(ContentTree.load(state), lesson, course, {content.key: task['id']}, revision='pilot-i')
        directory.mkdir()
        (directory / 'lesson.json').write_bytes(raw.encode('utf-8'))
        (directory / 'course.json').write_bytes((json.dumps(candidate, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    unchanged = apply('준비된 숫자 3을 출력해 직접 결과를 확인한다.')
    if unchanged.returncode:
        raise RuntimeError(unchanged.stderr)
    export(output / 'no-impact')
    changed = apply('준비된 숫자 3을 출력한 뒤 제출 순서를 명확히 한다.')
    if changed.returncode:
        raise RuntimeError(changed.stderr)
    export(output / 'candidate')
    candidate_bytes = (output / 'candidate/lesson.json').read_bytes()
    failed = apply('실패 검증: 모델 호출을 완료할 수 없다.')
    if failed.returncode != 1:
        raise AssertionError('Synthetic failure was not rejected')
    try:
        export(output / 'failed-candidate')
    except ValueError:
        blocked = True
    else:
        raise AssertionError('Incomplete work became a candidate')
    if (output / 'candidate/lesson.json').read_bytes() != candidate_bytes or (fixture / 'lesson.json').read_bytes() != lesson_bytes:
        raise AssertionError('Failed review changed previous candidate or baseline')
    history = command('history', '--target', content.key)
    if history.returncode:
        raise RuntimeError(history.stderr)
    records = json.loads(history.stdout)
    result = dict(failure_export_blocked=blocked,
        successful_generations=sum(item['status'] == 'succeeded' for item in records['generations']),
        review_statuses=[item['status'] for item in records['reviews']],
        scope='Synthetic CLI authoring only; player validation remains required')
    (output / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
