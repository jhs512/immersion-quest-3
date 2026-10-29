"""Prepare both courses transactionally by phase: sources, lessons, then manifests.

No network calls. A lesson build failure stops before any course publication. Preparing all
lessons before the course bundle avoids a partially built lesson invalidating the whole registry.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    apply = load('apply_finals', 'tools/apply-final-challenges.py')
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    keys = [l['key'] for c in catalog['courses'] if c['key'] in ('aice', 'engineer') for l in c['lessons']]
    for key in keys:
        spec = apply.spec_for(key)
        _, prd, content = apply.apply(spec)
        apply.record_review(spec, prd, content)
    builder = load('build_lessons', 'tools/build-redesigned-git.py')
    for key in keys:
        builder.build(key)
    load('build_courses', 'tools/build-redesigned-course-bundle.py').build()
    print(f'Prepared {len(keys)} new final challenges; no publication performed')


if __name__ == '__main__':
    main()
