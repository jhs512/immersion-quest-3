"""Publish reviewed cross-course categories and entry briefs independently of app binaries.

Requires every prepared lesson pin to be published already. Updates only category/track on the
same ordered lesson references, categories, lesson_previews and one history entry. Optimistic SHA
and exact readback protect concurrent course changes.
"""
import argparse
import base64
import copy
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('final_publisher', ROOT / 'tools/publish-final-challenges.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def prepare(course, remote, local):
    if [r['id'] for r in remote['lessons']] != [r['id'] for r in local['lessons']]:
        raise ValueError('Course order or lesson identity differs')
    stripped = lambda r: {k: v for k, v in r.items() if k not in ('category', 'track')}
    if [stripped(r) for r in remote['lessons']] != [stripped(r) for r in local['lessons']]:
        raise ValueError('Publish and verify lesson revisions/challenges first; metadata cannot change their pins')
    if set(local['lesson_previews']) != {r['id'] for r in local['lessons']}:
        raise ValueError('Every course lesson needs an entry brief')
    if not all(r.get('category') for r in local['lessons']):
        raise ValueError('Every lesson needs a reviewed category')
    merged = copy.deepcopy(remote)
    merged['lessons'] = copy.deepcopy(local['lessons'])
    merged['categories'] = copy.deepcopy(local['categories'])
    merged['lesson_previews'] = copy.deepcopy(local['lesson_previews'])
    summary = '주제별 묶음과 수업별 학습 예고를 적용했어요.'
    if not any(h.get('summary') == summary for h in merged.get('change_history', [])):
        merged.setdefault('change_history', []).insert(0, dict(
            at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
            summary=summary, reason='다른 두 과정에도 백엔드의 적절한 개선을 적용하라는 사용자 요청이에요.',
            details=['기본 카테고리 묶음과 전체 보기에서 같은 수업을 탐색해요.',
                     '각 수업의 목표·흐름·가정·마지막 도전을 시작 전에 확인해요.',
                     '수업 순서·리소스 ID·문제 ID·실제 문제 진도는 보존해요.']))
    for field in set(remote) - {'lessons', 'categories', 'lesson_previews', 'change_history'}:
        if merged[field] != remote[field]:
            raise ValueError('Unexpected metadata change: ' + field)
    return merged


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--course', choices=['aice', 'engineer'], required=True)
    p.add_argument('--publish', action='store_true')
    args = p.parse_args()
    original, remote = module.read_course(args.course)
    local = json.loads((ROOT / f'courses/redesigned-courses/{module.SLUG[args.course]}.json').read_text(encoding='utf-8'))
    merged = prepare(args.course, remote, local)
    print(f'{args.course}: {len(merged["categories"])} categories, {len(merged["lesson_previews"])} entry briefs')
    if not args.publish or merged == remote:
        print('Verified only' if not args.publish else 'Already published')
        return
    account = module.gh('user')
    if (account['login'], account['id']) != ('jhs512', 4741844):
        raise ValueError('Unexpected publishing account')
    current, latest = module.read_course(args.course)
    if current['sha'] != original['sha'] or latest != remote:
        raise ValueError('Remote changed; rerun to merge current metadata')
    raw = (json.dumps(merged, ensure_ascii=False, indent=2) + '\n').encode()
    result = module.gh(module.course_endpoint(args.course), 'PUT', dict(
        branch='main', sha=current['sha'], message='Publish reviewed categories and lesson entry briefs',
        content=base64.b64encode(raw).decode('ascii')))
    check = base64.b64decode(module.gh(module.course_endpoint(args.course) + '?ref=' + result['commit']['sha'])['content'])
    if check != raw:
        raise ValueError('Published metadata differs on readback')
    print('READBACK ' + result['commit']['sha'])


if __name__ == '__main__':
    main()
