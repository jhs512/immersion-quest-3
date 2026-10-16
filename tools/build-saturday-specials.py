"""Build and prove the independent Saturday workshops, without changing full courses."""
import concurrent.futures
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from certification_course import kit
from principles_course.common import ROOT, code, compile_narration, execute
from saturday_specials import aice, java, c, narration

OUT = ROOT / 'target/saturday-specials'
TCC = Path(os.environ.get('MQ3_SATURDAY_TCC', str(ROOT / 'target/saturday-specials-tools/tcc/tcc.exe')))
COURSES = [
    ('aice-saturday-practice', '에이스 · 데이터 분리와 모의문제 특강',
     '토요일 09~12시 G강의장이에요. 데이터 분리부터 분석·전처리 문제를 풀어요.',
     ['sat-aice-split', 'sat-aice-options', 'sat-aice-mock-inspect', 'sat-aice-mock-clean']),
    ('engineer-saturday-final', '정처기 실기 · C 포인터와 Java static 특강',
     '토요일 15~18시 A강의장이에요. C 다중 포인터와 Java static을 마무리해요.',
     ['sat-engineer-c-pointers', 'sat-engineer-c-multiple', 'sat-engineer-c-memory-strings', 'sat-engineer-static', 'sat-engineer-java-challenge']),
]


def run_c(t, source, input):
    with tempfile.TemporaryDirectory(prefix='mq3-sat-c-') as folder:
        home = Path(folder)
        (home / 'main.c').write_text(source, encoding='utf8')
        built = subprocess.run([str(TCC), '-o', 'main.exe', 'main.c'], cwd=home,
            capture_output=True, text=True, encoding='utf8', errors='replace', timeout=15)
        if built.returncode:
            return built
        return subprocess.run([str(home / 'main.exe')], cwd=home, input=input,
            capture_output=True, text=True, encoding='utf8', errors='replace', timeout=5)


def narration_c(item, t):
    initial = run_c(t, t['starter_code'], t['tests'][0]['input'])
    final = run_c(t, t['solution'], t['tests'][0]['input'])
    def reading(r):
        if r.returncode:
            return '실행 오류가 나요. 바꿀 줄을 확인해요.'
        return '실행 결과를 비교해요. ' + r.stdout.strip().replace('\n', ' / ')
    t['narration'] = [
        dict(action='set_code', code=t['starter_code'], say='먼저 값을 예상하고 실행해 볼게요.'),
        dict(action='run', expected_failure=initial.returncode != 0),
        dict(action='say', target='output', text=reading(initial)),
        dict(action='say', target='editor', text='조심하세요. ' + t['_caution']),
        dict(action='patch_code', **t['_edit'], say='대상 칸을 확인하고 작은 부분만 바꿔요.'),
        dict(action='run'),
        dict(action='say', target='output', text=reading(final)),
        dict(action='submit'),
    ]
    cache = OUT / 'narration-cache'
    cache.mkdir(parents=True, exist_ok=True)
    fingerprint = hashlib.sha256(json.dumps(t, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    (cache / (item['id'] + '--' + t['id'] + '.json')).write_text(
        json.dumps(dict(hash=fingerprint, actions=t['narration']), ensure_ascii=False, indent=2), encoding='utf8')
    t.pop('_edit')
    t.pop('_caution')


def build_one(item):
    item = copy.deepcopy(item)
    is_c = item['tasks'][0]['language'] == 'c'
    for t in item['tasks']:
        if is_c:
            starter_passes = []
            for case in t['tests']:
                reference = run_c(t, t['solution'], case['input'])
                assert reference.returncode == 0, (item['id'], t['id'], reference.stderr)
                case['expected'] = reference.stdout.rstrip('\n')
                starter = run_c(t, t['starter_code'], case['input'])
                starter_passes.append(starter.returncode == 0 and starter.stdout.rstrip('\n') == case['expected'])
            assert not all(starter_passes), (t['id'], 'starter passed every case')
            narration_c(item, t)
        else:
            reference = execute(t, t['solution'])
            assert reference.returncode == 0, (item['id'], t['id'], reference.stderr[-1200:])
            # The shared narration compiler compares a trimmed display sample.
            # Python's checker compares the original full output on every changed dataset.
            t['tests'][0]['expected'] = reference.stdout.strip()
    if not is_c:
        print('\n'.join(kit.verify(item)), flush=True)
        mistakes = kit.finish(item)
        for t in item['tasks']:
            compile_narration(item, t)
        kit.settle_narration(item)
    else:
        assert not kit.voice_problems(item), kit.voice_problems(item)
        mistakes = {}
    narration.rewrite(item, OUT)
    assert not kit.voice_problems(item), kit.voice_problems(item)
    item['sections'] = [
        dict(id='how', title='예상하고, 실행하고, 한 줄만 바꿔요',
             body='실행하기 전에 결과를 먼저 예상해요.\n틀린 이유는 변수 칸이나 자료의 행에서 찾아요.\n준비 코드를 조금 바꾸고 결과를 비교해요.\n마지막 선택 도전은 힌트 없이 먼저 풀어봐요.'),
    ]
    if is_c:
        item['sections'].append(dict(id='memory', title='화살표를 그리는 순서',
            body='a와 b의 값 칸을 먼저 그려요.\np는 어느 값 칸의 주소인지 연결해요.\npp는 p 칸의 주소를 연결해요.\n별 하나마다 화살표를 한 번 따라가요.\n대입 왼쪽이 어떤 칸인지 표시한 뒤 계산해요.'))
    folder = OUT / item['id']
    folder.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(item, ensure_ascii=False, indent=2) + '\n'
    (folder / 'lesson.json').write_text(raw, encoding='utf8', newline='\n')
    (folder / 'mistakes.json').write_text(json.dumps(mistakes, ensure_ascii=False, indent=2), encoding='utf8')
    print(f"BUILT {item['id']}: {len(item['tasks'])} actual exercises", flush=True)
    return item


def main():
    import argparse
    args = argparse.ArgumentParser()
    args.add_argument('--group', choices=['aice', 'java', 'c'])
    args.add_argument('--ids', nargs='*')
    args.add_argument('--narration-only', action='store_true', help='Refresh authored speech on already verified lessons')
    options = args.parse_args()
    chosen = options.group
    groups = {'aice': aice, 'java': java, 'c': c}
    items = []
    for name, module in groups.items():
        if chosen is None or chosen == name:
            items.extend(module.build())
    if options.ids:
        items = [item for item in items if item['id'] in options.ids]
    OUT.mkdir(parents=True, exist_ok=True)
    if options.narration_only:
        for original in items:
            path = OUT / original['id'] / 'lesson.json'
            item = json.loads(path.read_text(encoding='utf8'))
            narration.rewrite(item, OUT)
            path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(build_one, items))
    for id, title, description, ids in COURSES:
        if not all((OUT / name / 'lesson.json').exists() for name in ids):
            continue
        references = []
        for name in ids:
            raw = (OUT / name / 'lesson.json').read_bytes()
            item = json.loads(raw)
            references.append(dict(id=name, title=item['title'], repository='jhs512/mq3-lesson-' + name,
                revision=item['revision'], sha256=hashlib.sha256(raw).hexdigest(),
                prerequisites=ids[max(0, ids.index(name)-1):ids.index(name)], required=True, review_enabled=False))
        manifest = dict(schema_version=1, id=id, title=title, description=description,
            repository='jhs512/mq3-course-' + id, lessons=references)
        folder = OUT / id
        folder.mkdir(exist_ok=True)
        (folder / 'course.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
        print(f'COURSE {id}: {len(ids)} lessons', flush=True)


if __name__ == '__main__':
    main()
