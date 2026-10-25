"""Publication must preserve other work and wait for the compatible runtime."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('expansion_publish',Path(__file__).with_name('publish-principles-expansion.py'))
publish=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.prepared,self.rows=publish.additions()
        self.remote=copy.deepcopy(self.prepared)
        new={row['id'] for row,_ in self.rows}
        self.remote['lessons']=[row for row in self.remote['lessons'] if row['id'] not in new]
        self.remote['lesson_previews']={key:value for key,value in self.remote['lesson_previews'].items() if key not in new}
        self.remote['change_history']=[row for row in self.remote['change_history'] if '14개' not in row['summary']]

    def test_a_parallel_coding_revision_and_all_old_fields_survive(self):
        self.remote['lessons'][0]['revision']='parallel-coding-99'
        self.remote['lessons'][0]['sha256']='a'*64
        self.remote['description']='A concurrent course description'
        old=copy.deepcopy(self.remote)
        merged=publish.merge_course(self.remote,self.prepared,self.rows)
        self.assertEqual(merged['lessons'][:26],old['lessons'])
        self.assertEqual(merged['description'],old['description'])
        self.assertEqual(self.remote,old)
        self.assertEqual(len(merged['lessons']),40)
        self.assertEqual(publish.merge_course(merged,self.prepared,self.rows),merged)

    def test_a_different_public_revision_is_not_silently_downgraded(self):
        reference=copy.deepcopy(self.rows[0][0])
        reference['revision']='future-version-2'
        self.remote['lessons'].append(reference)
        with self.assertRaisesRegex(ValueError,'different revision'):
            publish.merge_course(self.remote,self.prepared,self.rows)

    def test_an_older_runtime_release_is_rejected(self):
        release={'draft':False,'prerelease':False,'assets':[{'name':'windows.exe'},{'name':'mac.dmg'}]}
        with patch.object(publish,'gh',side_effect=[release,{'status':'behind'}]), patch.object(publish.subprocess,'check_output',return_value='current\n'):
            with self.assertRaisesRegex(ValueError,'does not contain'):
                publish.require_runtime_release('old')

    def test_both_platform_installers_must_exist(self):
        release={'draft':False,'prerelease':False,'assets':[{'name':'windows.exe'}]}
        with patch.object(publish,'gh',return_value=release):
            with self.assertRaisesRegex(ValueError,'both be public'):
                publish.require_runtime_release('incomplete')


if __name__=='__main__':unittest.main()
