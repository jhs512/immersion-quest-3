"""Exercise image meaning review and asset reuse through the authoring boundary."""
import json
from pathlib import Path
import tempfile
import unittest

from content_review import Artifact, ContentTree, ReviewLedger


class SupportingAssetReviewTest(unittest.TestCase):
    def test_meaning_unchanged_reuses_image_then_changed_required_element_regenerates_only_it(self):
        # Synthetic evidence, not a claim about an actual model or educational artwork.
        meaning = {'educational_meaning': '두 이름이 같은 목록을 가리켜요.',
                   'required_elements': ['이름 두 개', '목록 한 개', '같은 목록으로 향하는 화살표']}
        recipe = {'prompt': '같은 목록을 가리키는 두 이름을 그려요.',
                  'settings': {'renderer': 'synthetic-test-v1'}}
        old_asset = json.dumps({'sha256': 'a'*64, 'file': 'shared-list.png'})
        spec = Artifact('step/picture-meaning', 'support_spec', json.dumps(meaning, ensure_ascii=False))
        image = Artifact('step/picture', 'asset', old_asset)
        unrelated = Artifact('other/picture', 'asset', '{"file":"other.png"}')
        tree = ContentTree([spec, image, unrelated], {image.key: spec.key})
        with tempfile.TemporaryDirectory() as directory, ReviewLedger(Path(directory)/'review.db') as ledger:
            def must_not_generate(_):
                raise AssertionError('A wording-only edit must retain the actual image')

            wording = dict(meaning, educational_meaning='두 이름은 같은 목록을 가리켜요.')
            tree.apply(Artifact(spec.key, spec.layer, json.dumps(wording, ensure_ascii=False)), ledger,
                       lambda _: {'change_required': False, 'reason': '같은 관계와 시각 요소를 표현해요.'},
                       must_not_generate, assessor_key='synthetic-image-review-v1', generator_key='synthetic-image-v1')
            self.assertEqual(tree.artifact(image.key).text, old_asset)
            self.assertEqual(ledger.generation_history(image.key), [])
            self.assertNotIn('prompt', tree.artifact(spec.key).text)
            self.assertEqual(recipe['settings']['renderer'], 'synthetic-test-v1')

            changed = dict(meaning, educational_meaning='각 이름이 서로 다른 목록을 가리켜요.',
                           required_elements=['이름 두 개', '목록 두 개', '각 목록으로 향하는 화살표'])
            generated = []

            def generate(request):
                generated.append(request)
                return '{"sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","file":"copied-list.png"}'

            tree.apply(Artifact(spec.key, spec.layer, json.dumps(changed, ensure_ascii=False)), ledger,
                       lambda _: {'change_required': True, 'reason': '목록 개수와 화살표의 목적지가 달라요.'},
                       generate, assessor_key='synthetic-image-review-v1', generator_key='synthetic-image-v1')
            self.assertEqual(len(generated), 1)
            self.assertEqual(tree.artifact(unrelated.key), unrelated)
            self.assertIn('copied-list.png', tree.artifact(image.key).text)
            self.assertEqual(len(ledger.history(image.key)), 2)
            self.assertEqual(len(ledger.generation_history(image.key)), 1)


if __name__ == '__main__':
    unittest.main()
