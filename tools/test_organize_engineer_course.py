import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('organization', Path(__file__).with_name('organize-engineer-course.py'))
organization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(organization)


class OrganizationTests(unittest.TestCase):
    def setUp(self):
        self.course = {'repository': organization.REPOSITORY, 'future_metadata': {'keep': True},
                       'change_history': [{'at': '2026-11-03T01:00:00Z', 'summary': 'existing'}],
                       'lessons': [dict(id=key, repository=organization.PREFIX + key,
                                        revision='immutable-1', sha256=key * 64, required=key != 'c',
                                        track='basic' if key == 'a' else '', challenge_task='final-' + key,
                                        prerequisites=[], category='old', custom={'keep': key})
                                   for key in ('c', 'a', 'b')]}
        self.plan = {'order': ['a', 'b', 'c'],
                     'categories': [{'id': 'language', 'title': '언어', 'keys': ['a', 'b']},
                                    {'id': 'application', 'title': '응용', 'keys': ['c']}],
                     'prerequisites': {'a': [], 'b': ['a'], 'c': ['b']}}

    def test_reorders_and_classifies_without_changing_pins_completion_tracks_or_other_metadata(self):
        before = copy.deepcopy(self.course)
        result = organization.organize(self.course, self.plan)
        self.assertEqual([item['id'] for item in result['lessons']], ['a', 'b', 'c'])
        self.assertEqual(result['lessons'][2]['prerequisites'], ['b'])
        self.assertEqual(result['future_metadata'], before['future_metadata'])
        for reference in result['lessons']:
            old = next(item for item in before['lessons'] if item['id'] == reference['id'])
            self.assertEqual({k: v for k, v in reference.items() if k not in ('category', 'prerequisites')},
                             {k: v for k, v in old.items() if k not in ('category', 'prerequisites')})
        self.assertEqual(self.course, before)

    def test_unknown_concurrent_lesson_is_not_dropped(self):
        self.course['lessons'].append(dict(self.course['lessons'][0], id='extra', repository=organization.PREFIX + 'extra'))
        with self.assertRaisesRegex(ValueError, 'lesson set changed'):
            organization.organize(self.course, self.plan)

    def test_cycles_missing_categories_and_duplicate_lessons_are_rejected(self):
        for mutate in [lambda p: p['order'].append('a'),
                       lambda p: p['categories'][0]['keys'].remove('b'),
                       lambda p: p['categories'][1]['keys'].append('b'),
                       lambda p: p['prerequisites'].update(a=['c']),
                       lambda p: p['prerequisites'].pop('b')]:
            plan = copy.deepcopy(self.plan)
            mutate(plan)
            with self.assertRaises(ValueError):
                organization.organize(self.course, plan)

    def test_history_uses_one_canonical_time_and_reruns_are_idempotent(self):
        first = organization.publication(self.course, self.plan, '2026-11-03T02:00:00Z')
        self.assertEqual(first['change_history'][0]['at'], '2026-11-03T02:00:00Z')
        self.assertEqual(first['change_history'][1:], self.course['change_history'])
        self.assertEqual(organization.publication(first, self.plan, '2026-11-03T03:00:00Z'), first)


if __name__ == '__main__':
    unittest.main()
