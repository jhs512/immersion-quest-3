"""Write the 2026-10-26 principle lessons (Docker · DB · OOP) into the standard lesson pipeline.

Each lesson is a module next to this file (LESSON = dict(...)). This script is the only writer of:
  tools/redesigned_lessons/<folder>/{approved-prd.json, content.json}
  tests/lesson-cases/<key>.json, tests/fixtures/player-pilot/<pilot>/course.json
and it adds (never rewrites) the lesson's entries in catalog.json, lesson-classification.json and the
course preview table. Running it again on a newer checkout (another worker's commits) re-applies only
these lessons, so the shared files merge by regeneration instead of by hand.

Then: python tools/build-redesigned-git.py --lesson <key>  (form gates, narration cache, lesson file)
      python tools/principles_lessons/make.py --review    (meaning-review records for the new steps)
      cargo run --example validate_redesigned_lesson tests/lesson-cases/<key>.json <evidence.json>

Approval truth: PRD approval mode delegated_scope. The user ordered these lessons to be built and
published without a per-problem review on 2026-10-26; nobody reviewed each PRD or problem individually.
"""
import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(HERE))
from lesson_prd import content_hash, policy_revision, validate  # noqa: E402

MODULES = ['o1_class_objects', 'o2_inheritance', 'o3_patterns',
           'd1_image_container', 'd2_network_ports',
           's0_sql_first', 's1_constraints', 's2_join_group', 's3_index_plan',
           't1_transactions', 'h1_h2_memory_file', 'j1_jdbc_basics',
           'd3_compose_db', 't2_concurrency']
NEW_ORDER = ['java-class-objects', 'java-inheritance-composition', 'java-oop-patterns',
             'docker-image-container', 'docker-network-ports', 'sql-first',
             'sql-tables-constraints', 'sql-join-group', 'sql-index-plan',
             'sql-transactions', 'h2-memory-file', 'java-jdbc',
             'docker-compose-db', 'sql-isolation-locks']

ADDED_ON = '2026-10-26'
APPROVAL = dict(
    status='approved', mode='delegated_scope', by='사용자의 제작·배포 위임 지시(2026-10-26)',
    evidence='2026-10-26 사용자(Codex 경유): 「도커랑 DB 수업도 클로드가 마저 만들어. 사용법만 알려주지 말고 원리를 이해하게 하고, '
             '나한테 물어보지 말고 끝까지 만들어서 배포해. 클래스, 상속, 객체지향 패턴 몇개 수업도 만들고, 알지 중요한건 원리 이해야. 길어도 돼.」 '
             '이 범위에서는 이전의 「최종 문제부터 검수」 절차가 면제됐어요. 이 PRD와 문제 내용을 사람이 개별 검토했다고 주장하지 않아요.')
DECIDED_BY = '사용자 위임: 2026-10-26 Docker·DB·객체지향 원리 수업 제작·배포 지시(분류는 작성자 판단)'


def uid(prefix, key, part):
    h = list(hashlib.sha256(f'mq3-principles:{key}:{part}'.encode()).hexdigest()[:32])
    h[12] = '4'
    h[16] = '89ab'[int(h[16], 16) % 4]
    h = ''.join(h)
    return f'{prefix}_{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text(encoding='utf-8') != text:
        path.write_text(text, encoding='utf-8', newline='\n')


def goal(step):
    parts = [step['start']] + list(step['intro'])
    if step.get('know'):
        parts.append('**알아두세요**\n\n' + step['know'])
    parts.append('**할 일**\n\n' + '\n'.join(f'{i}. {t}' for i, t in enumerate(step['todo'], 1)))
    return '\n\n'.join(parts)


def print_line(source):
    """The last output statement, so a run highlights the line whose output is read next."""
    found = [i for i, line in enumerate(source.splitlines(), 1) if 'System.out.print' in line]
    return [found[-1], found[-1]] if found else None


def narration(step):
    out = []
    source = step['starter']
    for item in step['narration']:
        kind = item[0]
        if kind == 'say':
            out.append(dict(action='say', text=item[1], target=item[2]))
        elif kind == 'run':
            action = dict(action='run')
            lines = item[1] if len(item) > 1 and item[1] else (print_line(source) if step['language'] in ('java', 'java_libraries') else None)
            if lines:
                action['lines'] = list(lines)
            if len(item) > 2 and item[2]:
                action['expect_error'] = item[2]
            out.append(action)
        elif kind == 'patch':
            if source.count(item[1]) != 1:
                raise ValueError(f"{step['slug']}: patch target must be unique: {item[1][:60]}")
            source = source.replace(item[1], item[2], 1)
            out.append(dict(action='patch_code', before=item[1], after=item[2], say=item[3]))
        elif kind == 'set':
            source = item[1]
            out.append(dict(action='set_code', code=item[1], say=item[2]))
        elif kind == 'submit':
            out.append(dict(action='submit'))
        else:
            raise ValueError(f'unknown narration item {kind}')
    return out


def task_of(step, sid):
    final = step['starter']
    for item in step['narration']:
        if item[0] == 'patch':
            final = final.replace(item[1], item[2], 1)
        elif item[0] == 'set':
            final = item[1]
    if final != step['solution']:
        raise ValueError(f"{step['slug']}: the narration's edits must end at the solution")
    task = dict(id=sid, title=step['title'], goal=goal(step), language=step['language'],
                starter_code=step['starter'], solution=step['solution'],
                tests=[dict(input=i, expected=e) for i, e in step['tests']], required=True,
                narration=narration(step))
    if step.get('question'):
        task['question'] = step['question']
    for field in ('entry_file', 'files', 'expected_files', 'variations', 'libraries', 'docker_images'):
        if step.get(field):
            task[field] = step[field]
    return task


def load(name):
    module = importlib.import_module(name)
    return module.LESSON


def policy():
    reference = json.loads((ROOT / 'tools/redesigned_lessons/java_calculator/approved-prd.json').read_text(encoding='utf-8'))
    artifacts = [dict(path=p, text=(ROOT / p).read_text(encoding='utf-8').replace('\r\n', '\n')) for p in ('docs/content-rules.md', 'docs/voice.md')]
    rules = reference['policy_snapshot']['rules'] + [
        '정상 동작 → 조건 하나를 바꾼 실제 실패 → 원인 → 1~3줄 수정 → 바뀐 입력·자료로 다시 검증하는 순서로 원리를 발견해요.',
        '객관식·보기 선택 없이 직접 코딩·명령 작성으로만 통과해요. 실제 실행 결과(출력·파일·DB·Docker 상태)로 채점해요.',
        '실제 엔진(JDK·H2·MySQL·PostgreSQL·Docker)의 결과만 그 엔진의 결과라고 말해요.']
    return dict(revision=policy_revision(artifacts), artifacts=artifacts, rules=rules)


def build_lesson(lesson, pol):
    key = lesson['key']
    lid = uid('lsn', key, 'lesson')
    tasks, chapters, pres_ch, pres_units = [], [], {}, {}
    for ci, chapter in enumerate(lesson['chapters']):
        cid = uid('chp', key, f'c{ci}')
        pres_ch[cid] = chapter['objectives']
        units = []
        for ui, unit in enumerate(chapter['units']):
            unid = uid('unt', key, f'c{ci}u{ui}')
            pres_units[unid] = dict(objectives=unit['objectives'], premise=unit['premise'])
            steps = []
            for step in unit['steps']:
                sid = uid('stp', key, step['slug'])
                c = step['complexity']
                steps.append(dict(id=sid, title=step['title'], objectives=step['objectives'],
                                  core_flow=step['core_flow'] if step.get('core_flow') else
                                  f"시작 상태: {step['start']}\n관찰: {c['evidence']}\n바꾸는 것: {c['changed']}\n"
                                  f"성공 조건: {step['success']}\n해설: 수정 전 실행 → 결과 읽기 → 고칠 곳 수정 → 재실행 비교.",
                                  complexity=dict(prerequisite_experience=c['prior'], new_concepts=[c['new']] if c.get('new') else [],
                                                  changed_condition=c['changed'], observable_evidence=c['evidence'],
                                                  learner_edited_lines=c['lines'], new_external_services=c.get('services', 0))))
                tasks.append(task_of(step, sid))
            units.append(dict(id=unid, title=unit['title'], objectives=unit['objectives'], premise=unit['premise'], steps=steps))
        chapters.append(dict(id=cid, title=chapter['title'], objectives=chapter['objectives'], units=units))
    rep = lesson['representative']
    rep_step = next(t for t in tasks if t['id'] == uid('stp', key, rep['slug']))
    prd = dict(schema_version=1, id=lid, title=lesson['title'], course='자바 백엔드 과정', audience=lesson['audience'],
               objectives=lesson['objectives'], prerequisites=lesson['prerequisites'], scope=lesson['scope'],
               out_of_scope=lesson['out_of_scope'], policy_snapshot=pol,
               sources=[dict(url=u, checked_at=ADDED_ON, finding=f, certainty=c) for u, f, c in lesson['sources']],
               chapters=chapters, grading=lesson['grading'], reset=lesson['reset'], narration=lesson['narration_policy'],
               verification=lesson['verification'],
               representative=dict(step_id=rep_step['id'], prompt=rep_step['title'], starter_state=rep_step['goal'],
                                   expected_action=rep['expected_action'], acceptance=rep['acceptance'],
                                   reset=rep['reset'], narration=rep['narration']))
    prd['approval'] = dict(status='draft')
    validate(prd)
    prd['approval'] = dict(APPROVAL, content_sha256=content_hash(prd))
    validate(prd, require_approval=True)
    content = dict(description=lesson['description'], tasks=tasks,
                   presentation=dict(objectives=lesson['objectives'], chapters=pres_ch, units=pres_units,
                                     learning_strategy=lesson['learning_strategy']))
    return lid, prd, content


def cases(lesson):
    key = lesson['key']
    path = HERE / 'recorded' / f'{key}.json'
    recorded = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
    steps = [s for c in lesson['chapters'] for u in c['units'] for s in u['steps']]
    reject, accept, expected = [], [], []
    for index, step in enumerate(steps, 1):
        for replacements, reason in step.get('rejects', []):
            reject.append(dict(step=index, replacements=[list(r) for r in replacements], reason=reason))
        for replacements, reason in step.get('accepts', []):
            accept.append(dict(step=index, replacements=[list(r) for r in replacements], reason=reason))
        expected.append(recorded[index - 1] if recorded else [])
    return dict(course=f"tests/fixtures/player-pilot/{lesson['pilot']}/course.json", lesson=f'courses/redesigned/{key}.json',
                expected_outputs=expected, reject=reject, accept=accept)


def register(lesson, lid):
    key = lesson['key']
    folder = lesson['folder']
    catalog_path = ROOT / 'tools/redesigned_courses/catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    java = next(c for c in catalog['courses'] if c['key'] == 'java')
    entry = dict(key=key, id=lid, title=lesson['title'], objectives=lesson['objectives'],
                 authoring_prd=f'tools/redesigned_lessons/{folder}/approved-prd.json',
                 continuing_situation=lesson['description'], revision=f"{key}-{lesson.get('revision', 1)}", required=False,
                 added_on=ADDED_ON,
                 origin='2026-10-26 사용자의 Docker·DB·객체지향 원리 수업 제작·배포 위임 지시로 새로 만든 선택 수업.',
                 validation=dict(pilot=lesson['pilot'], driver='code', label=key,
                                 modifications={str(lesson.get('pilot_step', 1)): {'correct': True}}))
    existing = [i for i, item in enumerate(java['lessons']) if item['key'] == key]
    if existing:
        java['lessons'][existing[0]] = entry
    else:
        java['lessons'].append(entry)
    # Preserve every pre-existing lesson and its order. Only the new lessons
    # move into the prerequisite sequence; withdrawn CS lessons are not added.
    registered = {item['key']: item for item in java['lessons'] if item['key'] in NEW_ORDER}
    java['lessons'] = [item for item in java['lessons'] if item['key'] not in NEW_ORDER] + [
        registered[name] for name in NEW_ORDER if name in registered]
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

    cls_path = ROOT / 'tools/redesigned_courses/lesson-classification.json'
    cls = json.loads(cls_path.read_text(encoding='utf-8'))
    course = cls['courses']['java']
    if lesson['category'] not in [c['id'] for c in course['categories']]:
        course['categories'].append(dict(id=lesson['category'], title=lesson['category_title']))
    course['lessons'][key] = dict(category=lesson['category'], track=lesson['track'], status='approved',
                                  decided_by=DECIDED_BY, decided_on=ADDED_ON,
                                  evidence=dict(category=lesson['category_evidence'], track=lesson['track_evidence']),
                                  title=lesson['title'])
    used_categories={value.get('category') for name,value in course['lessons'].items()
                     if any(item['key']==name for item in java['lessons'])}
    course['categories']=[item for item in course['categories']
                          if item['id']!='container' or item['id'] in used_categories]
    cls_path.write_text(json.dumps(cls, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

    fixture = json.loads((ROOT / 'tests/fixtures/player-pilot/저/course.json').read_text(encoding='utf-8'))
    fixture['lessons'][0].update(id=lid, title=lesson['title'], revision=entry['revision'])
    path = ROOT / 'tests/fixtures/player-pilot' / lesson['pilot'] / 'course.json'
    if not path.exists():
        fixture['lessons'][0]['sha256'] = '0' * 64
        write(path, fixture)


def previews(lessons):
    """Append learner-facing briefs (learn, challenge, scenario, assumptions, question) to the preview table."""
    path = ROOT / 'tools/redesigned_courses/backend_previews.py'
    text = path.read_text(encoding='utf-8')
    marker = '\n}\n\n\ndef for_course'
    head, tail = text.split(marker, 1)
    lines = [line for line in head.split('\n') if not any(line.startswith(f" '{l['key']}':") for l in lessons)]
    for lesson in lessons:
        lines.append(f" {lesson['key']!r}: {tuple(lesson['brief'])!r},")
    path.write_text('\n'.join(lines) + marker + tail, encoding='utf-8', newline='\n')


def review(lessons, reviewer='작성자 문맥 검토'):
    """Meaning-review records for the new steps (Claude 문맥 검토, 사람 검토 아님). Every flagged sentence needs a note."""
    from narration_review import load_ledger, save_ledger, context_sha256, prompts, problems
    ledger = load_ledger()
    missing = []
    for lesson in lessons:
        folder = ROOT / 'tools/redesigned_lessons' / lesson['folder']
        prd = json.loads((folder / 'approved-prd.json').read_text(encoding='utf-8'))
        content = json.loads((folder / 'content.json').read_text(encoding='utf-8'))
        steps = [s for c in prd['chapters'] for u in c['units'] for s in u['steps']]
        authored = [s for c in lesson['chapters'] for u in c['units'] for s in u['steps']]
        for step, task, source in zip(steps, content['tasks'], authored):
            notes = source.get('review', {})
            checked = {}
            for prompt in prompts(task):
                note = notes.get(prompt['text'])
                if not note:
                    missing.append(f"{lesson['key']} {source['slug']}: {prompt['text']}")
                    continue
                checked[prompt['text']] = note + f' ({reviewer}, 사람 검토 아님)'
            if missing:
                continue
            entry = dict(lesson=lesson['key'], state='reviewed', context_sha256=context_sha256(step, task),
                         reviewed=ADDED_ON, checked=checked, findings=[])
            found = problems(lesson['key'], step, task, entry)
            if found:
                raise ValueError('\n'.join(found))
            ledger['steps'][step['id']] = entry
    if missing:
        raise ValueError('검토 메모가 없는 문장:\n  ' + '\n  '.join(missing))
    save_ledger(ledger)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--only', nargs='*')
    parser.add_argument('--review', action='store_true', help='write meaning-review records (after the build)')
    parser.add_argument('--reviewer', default='작성자 문맥 검토')
    args = parser.parse_args()
    names = [m for m in MODULES if (HERE / f'{m}.py').exists()]
    lessons = [load(m) for m in names]
    if args.only:
        lessons = [l for l in lessons if l['key'] in args.only]
    if args.review:
        review(lessons, args.reviewer)
        print('reviewed', [l['key'] for l in lessons])
        return
    pol = policy()
    for lesson in lessons:
        lid, prd, content = build_lesson(lesson, pol)
        folder = ROOT / 'tools/redesigned_lessons' / lesson['folder']
        write(folder / 'approved-prd.json', prd)
        write(folder / 'content.json', content)
        write(ROOT / 'tests/lesson-cases' / f"{lesson['key']}.json", cases(lesson))
        register(lesson, lid)
        print('prepared', lesson['key'], lid, sum(len(u['steps']) for c in lesson['chapters'] for u in c['units']), 'steps')
    previews(lessons)


if __name__ == '__main__':
    main()
