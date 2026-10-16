"""Act as the player for a drafted lesson: run or grade a learner's code for one exercise.

python tools/certification_course/try_answer.py <lesson id> <task id> <code file> [--run]

--run prints what the 코드 실행 button would show; without it the exercise is graded like 제출.
Reads target/certification-drafts/<lesson id>/lesson.json, written by check_lesson.py.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from certification_course import kit
from principles_course.common import ROOT, execute

if __name__ == '__main__':
    lesson_id, task_id, path = sys.argv[1:4]
    lesson = json.loads((ROOT / 'target/certification-drafts' / lesson_id / 'lesson.json').read_text(encoding='utf8'))
    t = next(x for x in lesson['tasks'] if x['id'] == task_id)
    source = Path(path).read_text(encoding='utf8')
    if '--run' in sys.argv:
        result = execute(t, source)
        print(result.stdout, end='')
        if result.stderr:
            print(result.stderr[-3000:], file=sys.stderr, end='')
        print(f'\n[exit {result.returncode}]')
    else:
        passed, detail = kit.grade(t, source)
        print('PASS' if passed else 'FAIL')
        if not passed:
            print(detail)
