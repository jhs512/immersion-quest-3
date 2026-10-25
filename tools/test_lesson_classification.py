"""Lesson classification source → manifest metadata (tools/build-redesigned-course-bundle.py)."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bundle', ROOT / 'tools/build-redesigned-course-bundle.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)

CATALOG = {'courses': [{'key': 'java', 'lessons': [{'key': 'bash-basics'}, {'key': 'vim-basics'}, {'key': 'java-values'}]}]}
APPROVED = {'status': 'approved', 'decided_by': 'user', 'decided_on': '2026-10-25'}


def source(lessons, categories=None):
    return {'schema_version': 1, 'courses': {'java': {
        'categories': categories if categories is not None else [{'id': 'terminal', 'title': '터미널 기초'}, {'id': 'java-basics', 'title': '자바 기초'}],
        'lessons': lessons}}}


def run(data):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'classification.json'
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return bundle.classification(CATALOG, path)


class Classification(unittest.TestCase):
    def test_missing_source_changes_nothing(self):
        self.assertEqual(bundle.classification(CATALOG, Path('does-not-exist.json')), {})

    def test_proposals_never_reach_the_manifest(self):
        result = run(source({'bash-basics': {'category': 'terminal', 'track': 'essential', 'status': 'proposed', 'evidence': {}}}))
        self.assertEqual(result['java'], {'categories': [], 'lessons': {}})

    def test_only_approved_entries_and_used_categories_propagate(self):
        result = run(source({
            'bash-basics': dict(APPROVED, category='terminal', track='essential'),
            'vim-basics': dict(APPROVED, category='terminal', track=None),
            'java-values': {'category': 'java-basics', 'track': 'essential', 'status': 'proposed'}}))
        self.assertEqual(result['java']['categories'], [{'id': 'terminal', 'title': '터미널 기초'}])
        self.assertEqual(result['java']['lessons'], {'bash-basics': {'category': 'terminal', 'track': 'essential'},
                                                     'vim-basics': {'category': 'terminal'}})

    def test_bad_sources_are_rejected_at_authoring_time(self):
        good = dict(APPROVED, category='terminal', track='essential')
        cases = {
            'unknown category': source({'bash-basics': dict(good, category='nope')}),
            'bad track': source({'bash-basics': dict(good, track='expert')}),
            'approval without decider': source({'bash-basics': {'category': 'terminal', 'track': None, 'status': 'approved'}}),
            'empty approval': source({'bash-basics': dict(APPROVED, category=None, track=None)}),
            'unregistered lesson': source({'java-missing': good}),
            'bad status': source({'bash-basics': dict(good, status='maybe')}),
            'duplicate category': source({}, [{'id': 'a', 'title': 'A'}, {'id': 'a', 'title': 'B'}]),
            'untitled category': source({}, [{'id': 'a', 'title': ' '}]),
        }
        for name, data in cases.items():
            with self.subTest(name), self.assertRaises(ValueError):
                run(data)
        with self.assertRaises(ValueError):
            run({'courses': {'other': {'categories': [], 'lessons': {}}}})

    def test_repository_source_applies_backend_topics_and_preserves_the_basic_decision(self):
        catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
        data = json.loads(bundle.CLASSIFICATION.read_text(encoding='utf-8'))
        result = bundle.classification(catalog)
        keys = {c['key']: {l['key'] for l in c['lessons']} for c in catalog['courses']}
        for course, entry in data['courses'].items():
            self.assertEqual(set(entry['lessons']), keys[course], f'{course}: every lesson has an entry to review')
            for lesson, item in entry['lessons'].items():
                self.assertTrue(item['evidence']['category'] and item['evidence']['track'], f'{course}/{lesson}: evidence')
                if item['status'] == 'proposed':
                    # A proposal never reaches a manifest; only an approved user decision can add a track.
                    self.assertNotIn('category', result[course]['lessons'].get(lesson, {}))
        # 2026-10-25 user decision: exactly the lessons that existed then are 기본; lessons added later get no track.
        decision = next(d for d in data['track_decisions'] if d['track'] == 'basic')
        self.assertEqual(decision['status'], 'approved')
        self.assertEqual(sum(len(v) for v in decision['lessons'].values()), 80)
        for course in keys:
            basic = set(decision['lessons'].get(course, []))
            self.assertEqual({k for k, v in result[course]['lessons'].items() if v.get('track') == 'basic'}, basic)
            if course == 'java':
                self.assertEqual(set(result[course]['lessons']), keys[course])
                self.assertTrue(all('category' in v for v in result[course]['lessons'].values()))
                self.assertEqual(result[course]['lessons']['bash-basics']['category'], 'terminal')
                self.assertEqual(result[course]['lessons']['vim-basics']['category'], 'terminal')
                # 2026-10-26: lessons 27-34 were withdrawn; their classification stays only as a record.
                self.assertEqual(set(data['courses'][course]['withdrawn_lessons']).intersection(keys[course]), set())
                self.assertNotIn('sys-buffer-pool', result[course]['lessons'])
                self.assertEqual([c['id'] for c in result[course]['categories']], ['java', 'git', 'terminal', 'frontend'])
            else:
                self.assertTrue(all(set(v) == {'track'} for v in result[course]['lessons'].values()), 'other course proposals remain unpublished')
            for added in [l['key'] for c in catalog['courses'] if c['key'] == course for l in c['lessons'] if l.get('added_on')]:
                self.assertNotIn('track', result[course]['lessons'].get(added, {}), f'{added}: added later, no approved track')


if __name__ == '__main__':
    unittest.main()
