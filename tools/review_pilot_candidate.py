"""Narrow authoring-to-player bridge for the fixed validation course only."""
import copy
import hashlib
import json


def materialize(tree, lesson, course, task_goals, *, revision):
    """Map reviewed text to task instructions, preserving identity and grading.

    The real player must still validate the complete lesson and its pinned hash.
    This function has no publishing, installation, or learner-state side effects.
    """
    if tree.has_pending:
        raise ValueError('미완료 검토가 있어 후보를 만들 수 없어요.')
    if (course.get('repository') != 'mq3-validation/course' or len(course.get('lessons', [])) != 1
            or course['lessons'][0].get('repository') != 'mq3-validation/lesson'
            or course['lessons'][0].get('id') != lesson.get('id')):
        raise ValueError('고정된 개발 검증 코스에서만 후보를 만들어요.')
    if not isinstance(revision, str) or len(revision) != 7 or not revision.startswith('pilot-') or revision[-1] not in 'abcdefghijklmnopqrstuvwxyz':
        raise ValueError('검증 후보 버전을 확인하세요.')
    if not isinstance(task_goals, dict) or not task_goals or len(set(task_goals.values())) != len(task_goals):
        raise ValueError('자료와 문제 안내의 연결을 확인하세요.')
    output = copy.deepcopy(lesson)
    tasks = {task['id']: task for task in output['tasks']}
    for key, task_id in task_goals.items():
        artifact = tree.artifact(key)
        if artifact.layer != 'content' or task_id not in tasks or len(artifact.text) > 4000:
            raise ValueError('검토된 문제 안내 원문을 확인하세요.')
        lineage = tree.lineage(key)
        if len(lineage) < 2 or lineage[1].layer != 'core_flow' or tree.reviewed_from(key) != lineage[1].revision:
            raise ValueError('현재 핵심 흐름에 대한 검토 근거가 필요해요.')
        tasks[task_id]['goal'] = artifact.text
    output['revision'] = revision
    raw = json.dumps(output, ensure_ascii=False, indent=2) + '\n'
    candidate = copy.deepcopy(course)
    candidate['lessons'][0]['revision'] = revision
    candidate['lessons'][0]['sha256'] = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return candidate, raw
