"""Build and prove one lesson module in isolation: python tools/certification_course/check_lesson.py <module>

Writes only target/certification-drafts/<lesson id>/ and that lesson's narration cache files, so
several lessons can be checked at the same time without touching shared outputs.
"""
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from certification_course import kit
from principles_course.common import ROOT, compile_narration, execute


def prove(item):
    for t in item['tasks']:
        initial = execute(t, t['starter_code'])
        final = execute(t, t['solution'])
        assert final.returncode == 0, (t['id'], final.stderr[-1500:])
        assert initial.returncode != 0 or initial.stdout != final.stdout, (t['id'], 'starter equals solution')
        t['tests'][0]['expected'] = final.stdout.rstrip('\n')
    report = kit.verify(item)
    mistakes = kit.finish(item)
    for t in item['tasks']:
        compile_narration(item, t)
    kit.settle_narration(item)
    return report, mistakes


if __name__ == '__main__':
    name = sys.argv[1].removesuffix('.py')
    module = importlib.import_module('certification_course.lessons.' + name)
    item = module.build()
    report, mistakes = prove(item)
    folder = ROOT / 'target/certification-drafts' / item['id']
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'lesson.json').write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
    (folder / 'mistakes.json').write_text(json.dumps(mistakes, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
    print('\n'.join(report))
    required = sum(t['required'] for t in item['tasks'])
    print(f"CHECKED {item['id']}: {required} required + {len(item['tasks']) - required} challenge; draft at {folder}")
