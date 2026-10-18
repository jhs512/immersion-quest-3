"""Build optional-aid fixtures on the fixed validation course, never a real lesson."""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    folder = ROOT / 'tests/fixtures/player-pilot/j'
    folder.mkdir(exist_ok=True)
    course = json.loads((folder.parent / 'a/course.json').read_text(encoding='utf-8'))
    lesson = json.loads((folder.parent / 'a/lesson.json').read_text(encoding='utf-8'))
    lesson['revision'] = 'pilot-j'
    png = base64.b64encode((folder.parent / 'support-pixel.png').read_bytes()).decode()
    image = {'alt': '검증용 한 픽셀 그림이에요.', 'png_base64': png,
             'sha256': hashlib.sha256(base64.b64decode(png)).hexdigest()}
    lesson['tasks'][0]['supporting_materials'] = [
        {'id': 'flow', 'title': '값과 출력 그림', 'kind': 'mermaid',
         'source': 'flowchart LR\n A[값] --> B[출력]'},
        {'id': 'state', 'title': '값 변화', 'kind': 'interactive', 'variants': [
            {'label': '처음 값', 'frames': [
                {'caption': '값을 준비해요.', 'facts': {'value': '1'}},
                {'caption': '하나를 더했어요.', 'facts': {'value': '2'}}]},
            {'label': '다른 값', 'frames': [
                {'caption': '값을 준비해요.', 'facts': {'value': '3'}},
                {'caption': '하나를 더했어요.', 'facts': {'value': '4'}}]}]},
        {'id': 'image', 'title': '그림 보기', 'kind': 'image', 'image': image},
        {'id': 'comic', 'title': '만화 보기', 'kind': 'comic', 'image': image},
    ]
    raw = json.dumps(lesson, ensure_ascii=False, indent=2) + '\n'
    course['lessons'][0].update(revision='pilot-j', sha256=hashlib.sha256(raw.encode()).hexdigest())
    (folder / 'lesson.json').write_bytes(raw.encode())
    (folder / 'course.json').write_bytes((json.dumps(course, ensure_ascii=False, indent=2)+'\n').encode())


if __name__ == '__main__':
    build()
