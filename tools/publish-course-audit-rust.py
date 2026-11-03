"""Publish reviewed course-audit revisions and four Rust lessons without replacing remote courses."""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUST = ['rust-values', 'rust-flow-functions', 'rust-ownership-borrowing', 'rust-data-results']
RUNTIME = 'jhs512/immersion-quest-3'
BASELINE = 'b9fb3a998a216953e05476224ed63a87fc99664f'
REVIEWED_RUNTIME = '3262af8c0075e3c0b1c2c8dcccb885456f77e972'
PUBLICATION_AT = '2026-11-03T04:00:00Z'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load('audit_revision_publisher', 'publish-coding-conversions.py')
initial = load('audit_initial_publisher', 'publish-redesigned-courses.py')
gh = publisher.gh


def pin(row):
    return tuple(row.get(field) for field in ('id', 'repository', 'revision', 'sha256'))


def merge_course(remote, prepared, rows):
    value = copy.deepcopy(remote)
    desired_rust = []
    for old, new, _ in rows:
        current = next((row for row in value['lessons'] if row['repository'] == new['repository']), None)
        if current is not None and pin(current) not in (pin(old or {}), pin(new)):
            raise ValueError('Concurrent course revision changed: ' + new['repository'])
        if old is not None and current is None:
            raise ValueError('An existing lesson was removed concurrently: ' + new['repository'])
        if old is None:
            if new['repository'].removeprefix('jhs512/mq3-lesson-redesigned-') not in RUST:
                raise ValueError('Unexpected new lesson')
            desired_rust.append(new)
        else:
            current.update({field: new[field] for field in ('revision', 'sha256')})
        if new['id'] in prepared.get('lesson_previews', {}):
            value.setdefault('lesson_previews', {})[new['id']] = prepared['lesson_previews'][new['id']]
    if desired_rust:
        repositories = {'jhs512/mq3-lesson-redesigned-' + key for key in RUST}
        current_rust = {row['repository']: row for row in value['lessons'] if row['repository'] in repositories}
        additions = {row['repository']: current_rust.get(row['repository'], row)
                     for row in prepared['lessons'] if row['repository'] in repositories}
        if set(additions) != repositories:
            raise ValueError('The four Rust lessons must be published together')
        value['lessons'] = [row for row in value['lessons'] if row['repository'] not in repositories]
        position = next(i for i, row in enumerate(value['lessons'])
                        if row['repository'] == 'jhs512/mq3-lesson-redesigned-java-launch') + 1
        value['lessons'][position:position] = [copy.deepcopy(additions['jhs512/mq3-lesson-redesigned-' + key]) for key in RUST]
        category = next(row for row in prepared['categories'] if row['id'] == 'rust')
        existing = next((row for row in value.get('categories', []) if row['id'] == 'rust'), None)
        if existing is not None and existing != category:
            raise ValueError('A different Rust category is already published')
        if existing is None:
            value.setdefault('categories', []).append(copy.deepcopy(category))
    ids = [row['id'] for row in value['lessons']]
    repositories = [row['repository'] for row in value['lessons']]
    if len(set(ids)) != len(ids) or len(set(repositories)) != len(repositories):
        raise ValueError('Duplicate course lesson identity')
    if rows:
        summary = ('해설과 코드 흐름 보기를 보완하고 Rust 기초 네 수업을 더했어요.' if desired_rust
                   else '수업 감사에서 찾은 설명과 해설을 보완했어요.')
        entry = {'at': PUBLICATION_AT, 'summary': summary,
                 'reason': '수업 목표·정답·실행 결과와 해설을 대조한 감사 결과를 반영해요.',
                 'details': ['기존 수업의 고유 코드와 학습 기록을 유지하고 검증한 새 버전을 참조해요.',
                             '다른 작업에서 추가한 수업과 현재 과정 설정은 그대로 유지해요.']}
        if desired_rust:
            entry['details'].append('자바 실행 수업 바로 뒤에 값·흐름·소유권·자료와 결과를 다루는 Rust 선택 수업 네 개를 놓았어요.')
        history = value.setdefault('change_history', [])
        if not any(item.get('at') == PUBLICATION_AT and item.get('summary') == summary for item in history):
            history.insert(0, entry)
    return value


def prepare():
    plans = []
    for path in sorted((ROOT / 'courses/redesigned-courses').glob('*.json')):
        prepared = json.loads(path.read_text(encoding='utf-8'))
        baseline = json.loads(subprocess.check_output(
            ['git', 'show', BASELINE + ':courses/redesigned-courses/' + path.name], cwd=ROOT, text=True, encoding='utf-8'))
        baseline_by_repo = {row['repository']: row for row in baseline['lessons']}
        endpoint = f'repos/{prepared["repository"]}/contents/course.json'
        current = gh(endpoint)
        remote = json.loads(base64.b64decode(current['content']))
        rows = []
        by_repo = {row['repository']: row for row in remote['lessons']}
        for new in prepared['lessons']:
            old = by_repo.get(new['repository'])
            if old is not None and pin(old) == pin(new):
                continue
            key = new['repository'].removeprefix('jhs512/mq3-lesson-redesigned-')
            raw = (ROOT / 'courses/redesigned' / (key + '.json')).read_bytes()
            if hashlib.sha256(raw).hexdigest() != new['sha256']:
                raise ValueError('Prepared lesson hash differs: ' + key)
            if old is not None:
                if pin(old) != pin(baseline_by_repo.get(new['repository'], {})):
                    raise ValueError('The reviewed baseline is no longer published: ' + key)
                publisher.check_transition(key, old, new)
                prior = base64.b64decode(gh(f'repos/{old["repository"]}/contents/lesson.json?ref={old["revision"]}')['content'])
                if hashlib.sha256(prior).hexdigest() != old['sha256']:
                    raise ValueError('Published baseline pin differs: ' + key)
            elif key not in RUST:
                raise ValueError('Unexpected course addition: ' + key)
            tag = gh(f'repos/{new["repository"]}/git/ref/tags/{new["revision"]}', optional=True)
            if tag is not None:
                tagged = base64.b64decode(gh(f'repos/{new["repository"]}/contents/lesson.json?ref={new["revision"]}')['content'])
                if tagged != raw:
                    raise ValueError('Immutable revision differs: ' + key)
            rows.append((old, new, raw))
        merged = merge_course(remote, prepared, rows)
        plans.append((endpoint, prepared, remote, rows, merged))
    return plans


def require_runtime(tag, commit):
    release = gh(f'repos/{RUNTIME}/releases/tags/{tag}')
    names = [asset['name'].lower() for asset in release.get('assets', [])]
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('The runtime release must be public and stable')
    required = {'molip-quest-3-windows-x64-setup.exe', 'molip-quest-3-macos-arm64.dmg'}
    if not required.issubset(names):
        raise ValueError('Windows and ARM Mac runtime installers must be public first')
    comparison = gh(f'repos/{RUNTIME}/compare/{commit}...{tag}')
    if comparison['status'] not in ('identical', 'ahead'):
        raise ValueError('The runtime release does not include the reviewed commit')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--runtime-release')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    plans = prepare()
    report = [{'repository': prepared['repository'], 'before': len(remote['lessons']), 'after': len(merged['lessons']),
               'preserved_remote_only': [row['repository'] for row in remote['lessons']
                                         if not any(item['repository'] == row['repository'] for item in prepared['lessons'])],
               'lessons': [{'repository': new['repository'], 'before': old['revision'] if old else None,
                            'after': new['revision'], 'sha256': new['sha256']} for old, new, _ in rows]}
              for _, prepared, remote, rows, merged in plans]
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.publish:
        return
    if not args.runtime_release:
        raise ValueError('--runtime-release is required before publishing')
    require_runtime(args.runtime_release, REVIEWED_RUNTIME)
    user = gh('user')
    if (user['login'], user['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publishing account')
    for endpoint, prepared, _, rows, _ in plans:
        if not rows:
            continue
        for old, new, raw in rows:
            if old is None:
                initial.publish_file(new['repository'], 'lesson.json', raw, new['revision'])
            else:
                publisher.publish_lesson(old, new, raw, 'Publish reviewed course narration and visualizer audit')
        fresh = gh(endpoint)
        remote = json.loads(base64.b64decode(fresh['content']))
        merged = merge_course(remote, prepared, rows)
        body = (json.dumps(merged, ensure_ascii=False, indent=2) + '\n').encode()
        if body != base64.b64decode(fresh['content']):
            result = gh(endpoint, 'PUT', dict(message='Publish course audit fixes and Rust foundations',
                        branch='main', sha=fresh['sha'], content=base64.b64encode(body).decode('ascii')))
            readback = gh(endpoint + '?ref=' + result['commit']['sha'])
            if base64.b64decode(readback['content']) != body:
                raise ValueError('Published course readback differs')
        print('VERIFIED ' + prepared['repository'])


if __name__ == '__main__':
    main()
