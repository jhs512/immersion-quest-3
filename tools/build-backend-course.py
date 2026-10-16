"""Compile independent repository lessons. Execution checks live in repository_lessons.rs."""
import json
import hashlib
from backend_course.common import *
from backend_course import foundations, projects, frontend, supplemental
from backend_course.narration import cache_task

ORDER='git-environment java-values java-control java-methods-arrays java-objects wise-array java-collections java-design wise-list java-streams tdd-basics tdd-rq wise-layers wise-files java-recursion calculator-sequences calculator-parser html-css tailwind-layout javascript-browser react-components react-state react-effects-context frontend-project'.split()
LESSONS.sort(key=lambda pair:ORDER.index(pair[0]['id']))
assert [l['id'] for l,_ in LESSONS]==ORDER
for content,_ in LESSONS:
    for t in content['tasks']:
        assert t['tests'] or t['files'] or t.get('git_checks') or t['web_checks'] or t.get('checker'),t['id']
        t['source_hash']=cache_task(content['id'],t)
out=publish_files()
(out/'source-map.json').write_text(json.dumps({l['id']:dict(sources=l['sources'],tasks={t['id']:t['source_hash'] for t in l['tasks']}) for l,_ in LESSONS},ensure_ascii=False,indent=2),encoding='utf-8')
