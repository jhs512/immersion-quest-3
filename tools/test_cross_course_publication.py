"""Protect course identities and publication boundaries while adding reviewed metadata."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('metadata_publisher', Path(__file__).with_name('publish-course-improvements.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicationBoundaries(unittest.TestCase):
    def setUp(self):
        self.remote = dict(id='course', lessons=[dict(id='one', revision='v1', sha256='abc', challenge_task='step', title='lesson')], description='keep', change_history=[])
        self.local = copy.deepcopy(self.remote)
        self.local['lessons'][0]['category'] = 'python'
        self.local['categories'] = [dict(id='python', title='Python')]
        self.local['lesson_previews'] = {'one': dict(learn=['values'], challenge='final', scenario=['read', 'change'], constraints=['local'], question='why?')}

    def test_only_authorized_metadata_changes(self):
        result = module.prepare('aice', self.remote, self.local)
        self.assertEqual(result['description'], 'keep')
        self.assertEqual(result['lessons'][0]['revision'], 'v1')
        self.assertEqual(result['lessons'][0]['category'], 'python')
        self.assertNotIn('category', self.remote['lessons'][0])

    def test_unpublished_pin_cannot_sneak_into_metadata_update(self):
        self.local['lessons'][0]['revision'] = 'v2'
        with self.assertRaises(ValueError):
            module.prepare('aice', self.remote, self.local)

    def test_identity_and_missing_briefs_are_refused(self):
        for mutate in [lambda x: x['lessons'][0].update(id='other'), lambda x: x['lesson_previews'].clear()]:
            local = copy.deepcopy(self.local)
            mutate(local)
            with self.assertRaises(ValueError):
                module.prepare('aice', self.remote, local)


if __name__ == '__main__':
    unittest.main()
