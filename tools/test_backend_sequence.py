import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('course_bundle', ROOT / 'tools/build-redesigned-course-bundle.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BackendSequence(unittest.TestCase):
    def test_every_lesson_is_preserved_and_prerequisites_precede_it(self):
        course = next(c for c in json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))['courses'] if c['key'] == 'java')
        before = copy.deepcopy(course)
        ordered, dependencies = builder.learning_sequence(course)
        self.assertEqual(course, before)
        self.assertEqual({i['id'] for i in ordered}, {i['id'] for i in course['lessons']})
        ranks = {i['key']: n for n, i in enumerate(ordered)}
        for key, required in dependencies.items():
            for prerequisite in required:
                self.assertLess(ranks[prerequisite], ranks[key])
        self.assertLess(ranks['java-collections'], ranks['java-class-objects'])
        self.assertLess(ranks['java-jdbc'], ranks['sql-isolation-locks'])
        self.assertLess(ranks['java-testing'], ranks['java-crud'])

    def test_other_courses_keep_their_original_order(self):
        value = dict(key='aice', lessons=[dict(key='b'), dict(key='a')])
        self.assertEqual(builder.learning_sequence(value), (value['lessons'], {}))


if __name__ == '__main__':
    unittest.main()
