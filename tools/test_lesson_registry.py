import copy,json,unittest
from pathlib import Path
from lesson_registry import load_registry

ROOT=Path(__file__).resolve().parents[1]
class RegistryTests(unittest.TestCase):
    def test_all_published_lessons_resolve_from_the_same_registry(self):
        catalog=json.loads((ROOT/'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
        rows=load_registry(catalog)
        self.assertEqual(len(rows),98)  # 80 retained lessons + 14 principle lessons + 3 shell environment lessons + GitLab CI/CD (2026-10-29).
        self.assertEqual(len({row['pilot'] for row in rows}),len(rows))
        for row in rows:
            published=json.loads((ROOT/'courses/redesigned'/f"{row['key']}.json").read_text(encoding='utf-8'))
            self.assertEqual(published['revision'],row['revision'])
            self.assertTrue((ROOT/'tools/redesigned_lessons'/row['folder']/'approved-prd.json').exists())
    def test_a_duplicate_validation_identity_is_rejected_before_generation(self):
        catalog=json.loads((ROOT/'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
        catalog['courses'][0]['lessons'][1]['validation']['pilot']=catalog['courses'][0]['lessons'][0]['validation']['pilot']
        with self.assertRaisesRegex(ValueError,'duplicate'):
            load_registry(catalog)
    def test_windows_case_insensitive_fixture_alias_cannot_replace_legacy_a(self):
        catalog=json.loads((ROOT/'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
        catalog['courses'][0]['lessons'][0]['validation']['pilot']='A'
        with self.assertRaisesRegex(ValueError,'Invalid'):
            load_registry(catalog)
    def test_existing_special_exercises_keep_their_distinct_drivers(self):
        rows={row['key']:row for row in load_registry()}
        self.assertEqual(rows['git-first']['driver'],'native')
        self.assertEqual(rows['git-remote']['driver'],'git-remote')
        self.assertEqual(rows['java-values']['config']['modifications']['1']['source_replace'],['println(2)','println(99)'])
        self.assertTrue(rows['java-react']['config']['requireHtml'])
if __name__=='__main__':unittest.main()
