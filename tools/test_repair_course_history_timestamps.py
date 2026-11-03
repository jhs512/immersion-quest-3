import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('repair', Path(__file__).with_name('repair-course-history-timestamps.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RepairTests(unittest.TestCase):
    def test_published_history_becomes_compatible_without_changing_any_other_field(self):
        original = {'lessons': [{'id': 'remote-only', 'revision': 'immutable-1', 'sha256': 'keep'}],
                    'unknown_future_field': {'keep': True},
                    'change_history': [{'at': '2026-11-03T04:57:18.008383+00:00',
                                        'summary': 'keep', 'reason': 'keep', 'details': ['keep']}]}
        fixed, changes = module.repair(original)
        self.assertEqual(fixed['change_history'][0]['at'], '2026-11-03T04:57:18Z')
        self.assertEqual(original['change_history'][0]['at'], '2026-11-03T04:57:18.008383+00:00')
        self.assertEqual(fixed['lessons'], original['lessons'])
        self.assertEqual(fixed['unknown_future_field'], original['unknown_future_field'])
        self.assertEqual(len(changes), 1)
        self.assertEqual(module.repair(fixed), (fixed, []))

    def test_invalid_dates_and_non_utc_times_are_rejected(self):
        for stamp in ['2026-02-29T00:00:00Z', '2026-11-03T00:00:00', '2026-11-03T09:00:00+09:00']:
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                module.repair({'change_history': [{'at': stamp}]})


if __name__ == '__main__':
    unittest.main()
