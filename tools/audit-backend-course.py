"""Produce an exhaustive backend review packet and a deterministic issue inventory.

The packet is for semantic review. A clean inventory alone never means that a
person listened to the audio or that real-engine replay has passed.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.scratch/course-quality-20261026'


def main():
    course = json.loads((ROOT / 'courses/redesigned-courses/java-backend.json').read_text(encoding='utf-8'))
    rows, findings = [], []
    for ref in course['lessons']:
        key = ref['repository'].split('redesigned-', 1)[1]
        raw = (ROOT / 'courses/redesigned' / (key + '.json')).read_bytes()
        lesson = json.loads(raw)
        packet = ['# ' + lesson['title'], lesson['description'], *lesson['objectives']]
        row = dict(key=key, id=ref['id'], sha256=hashlib.sha256(raw).hexdigest(), steps=len(lesson['tasks']), sentences=0)
        for index, task in enumerate(lesson['tasks'], 1):
            location = dict(lesson=key, step=index, id=task['id'])
            if task.get('interaction'):
                findings.append(dict(**location, kind='selection', text='선택/입력형이 남아 있어요.'))
            if '할 일' not in task['goal']:
                findings.append(dict(**location, kind='instructions', text='할 일이 없어요.'))
            if not re.search(r'^1\. ', task['goal'], re.M):
                findings.append(dict(**location, kind='instructions', text='번호 목록이 없어요.'))
            packet.extend(['', f'## {index}. {task["title"]} ({task["id"]})', task['goal'], '', '### 해설'])
            for action in task['narration']:
                spoken = action.get('text') or action.get('say') or ''
                if spoken:
                    row['sentences'] += 1
                    packet.append(f'- {spoken}')
                # A changed answer must not leave a detached old selection narration behind.
                if re.search(r'정답 보기를|번째 보기를|선택지를 고르|선택한 보기', spoken):
                    findings.append(dict(**location, kind='stale-selection-copy', text=spoken))
                if re.search(r'[\u3040-\u30ff]', spoken):
                    findings.append(dict(**location, kind='language', text=spoken))
            packet.extend(['', '### 시작 코드', '```', task['starter_code'], '```', '### 정답', '```', task['solution'], '```'])
        rows.append(row)
        (OUT / (key + '-review.md')).write_text('\n'.join(packet) + '\n', encoding='utf-8')
    evidence = dict(lessons=rows, total_steps=sum(r['steps'] for r in rows),
                    total_sentences=sum(r['sentences'] for r in rows), findings=findings,
                    semantic_review_complete=False, audio_listened=False)
    (OUT / 'inventory.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(rows)} lessons / {evidence["total_steps"]} steps / {evidence["total_sentences"]} spoken actions; {len(findings)} deterministic findings')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    main()
