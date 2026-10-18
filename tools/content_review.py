"""Persist adjacent-layer review evidence separately from generated artifacts."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import uuid

ADJACENT = {
    'policy': {'prd'},
    'prd': {'goal'},
    'goal': {'core_flow'},
    'core_flow': {'content'},
    'content': {'support_spec', 'narration'},
    'support_spec': {'asset'},
    'narration': {'audio'},
    'asset': set(),
    'audio': set(),
}
CONTRACT_VERSION = 'adjacent-review-v1'


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class Artifact:
    key: str
    layer: str
    text: str

    def __post_init__(self):
        if not isinstance(self.key, str) or not self.key.strip() or self.layer not in ADJACENT:
            raise ValueError('자료의 고유 코드와 레이어를 확인하세요.')
        if not isinstance(self.text, str) or not self.text.strip() or len(self.text) > 1_000_000:
            raise ValueError('검토할 원문을 확인하세요.')
        object.__setattr__(self, 'text', self.text.replace('\r\n', '\n').replace('\r', '\n'))

    @property
    def revision(self):
        return _hash(self.text)

    def snapshot(self):
        return dict(asdict(self), revision=self.revision)


@dataclass(frozen=True)
class Decision:
    review_id: str
    change_required: bool
    reason: str


class ReviewLedger:
    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path)
        self.connection.execute("""CREATE TABLE IF NOT EXISTS adjacent_reviews (
            id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, target_key TEXT NOT NULL,
            created_at TEXT NOT NULL, payload TEXT NOT NULL
        )""")
        self.connection.execute('CREATE INDEX IF NOT EXISTS review_inputs ON adjacent_reviews(fingerprint)')
        self.connection.execute("""CREATE TABLE IF NOT EXISTS artifact_generations (
            id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, target_key TEXT NOT NULL,
            created_at TEXT NOT NULL, payload TEXT NOT NULL
        )""")
        self.connection.execute('CREATE INDEX IF NOT EXISTS generation_inputs ON artifact_generations(fingerprint)')
        self.connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self.connection.close()

    def history(self, target_key):
        return [json.loads(row[0]) for row in self.connection.execute(
            'SELECT payload FROM adjacent_reviews WHERE target_key=? ORDER BY rowid DESC', (target_key,))]

    def assess(self, before, after, target, assessor, *, assessor_key):
        if before.key != after.key or before.layer != after.layer:
            raise ValueError('변경 전후는 같은 리소스여야 해요.')
        if target.layer not in ADJACENT[after.layer]:
            raise ValueError('바로 인접한 레이어만 검토할 수 있어요.')
        if not isinstance(assessor_key, str) or not assessor_key.strip():
            raise ValueError('검토 모델과 지침의 버전을 지정하세요.')
        request = dict(contract=CONTRACT_VERSION, assessor_key=assessor_key,
                       source_before=before.snapshot(), source_after=after.snapshot(), target=target.snapshot())
        fingerprint = _hash(_json(request))
        for (payload,) in self.connection.execute(
                'SELECT payload FROM adjacent_reviews WHERE fingerprint=? ORDER BY rowid DESC', (fingerprint,)):
            cached = json.loads(payload)
            if cached['status'] == 'reviewed':
                return Decision(cached['id'], cached['change_required'], cached['reason'])
        record = dict(request, id=uuid.uuid4().hex, status='pending',
                      created_at=datetime.now(timezone.utc).isoformat())
        try:
            result = assessor(json.loads(_json(request)))
            if (not isinstance(result, dict) or set(result) != {'change_required', 'reason'}
                    or type(result['change_required']) is not bool
                    or not isinstance(result['reason'], str) or not result['reason'].strip()):
                raise ValueError('검토 결과의 변경 여부와 이유를 확인하세요.')
            record.update(result, status='reviewed')
        except Exception as error:
            record.update(status='failed', error=str(error))
            self._save(fingerprint, target.key, record)
            raise
        self._save(fingerprint, target.key, record)
        return Decision(record['id'], record['change_required'], record['reason'])

    def generation_history(self, target_key):
        return [json.loads(row[0]) for row in self.connection.execute(
            'SELECT payload FROM artifact_generations WHERE target_key=? ORDER BY rowid DESC', (target_key,))]

    def generate(self, before, after, target, decision, generator, *, generator_key):
        if not isinstance(generator_key, str) or not generator_key.strip():
            raise ValueError('생성 모델과 지침의 버전을 지정하세요.')
        row = self.connection.execute('SELECT payload FROM adjacent_reviews WHERE id=?', (decision.review_id,)).fetchone()
        review = json.loads(row[0]) if row else None
        if (not review or review['status'] != 'reviewed' or not review['change_required']
                or review['source_before'] != before.snapshot() or review['source_after'] != after.snapshot()
                or review['target'] != target.snapshot()):
            raise ValueError('이 변경을 승인한 인접 검토 근거가 없어요.')
        request = dict(contract=CONTRACT_VERSION, generator_key=generator_key, review_id=decision.review_id,
                       source_before=before.snapshot(), source_after=after.snapshot(),
                       target=target.snapshot(), reason=review['reason'])
        fingerprint = _hash(_json(request))
        for (payload,) in self.connection.execute(
                'SELECT payload FROM artifact_generations WHERE fingerprint=? ORDER BY rowid DESC', (fingerprint,)):
            cached = json.loads(payload)
            if cached['status'] == 'succeeded':
                output = cached['output']
                artifact = Artifact(output['key'], output['layer'], output['text'])
                if artifact.key != target.key or artifact.layer != target.layer or artifact.revision != output['revision']:
                    raise ValueError('보관된 생성 결과의 해시가 달라요.')
                return artifact
        record = dict(request, id=uuid.uuid4().hex, status='pending',
                      created_at=datetime.now(timezone.utc).isoformat())
        try:
            generated = Artifact(target.key, target.layer, generator(json.loads(_json(request))))
            if generated.revision == target.revision:
                raise ValueError('변경이 필요하지만 생성된 내용이 같아요. 다시 검토하세요.')
            record.update(status='succeeded', output=generated.snapshot())
        except Exception as error:
            record.update(status='failed', error=str(error))
            self._save_generation(fingerprint, target.key, record)
            raise
        self._save_generation(fingerprint, target.key, record)
        return generated

    def _save_generation(self, fingerprint, target_key, record):
        with self.connection:
            self.connection.execute('INSERT INTO artifact_generations VALUES (?,?,?,?,?)',
                                    (record['id'], fingerprint, target_key, record['created_at'], _json(record)))

    def _save(self, fingerprint, target_key, record):
        with self.connection:
            self.connection.execute('INSERT INTO adjacent_reviews VALUES (?,?,?,?,?)',
                                    (record['id'], fingerprint, target_key, record['created_at'], _json(record)))


class ContentTree:
    """Review immediate dependents; propagate only an actual artifact change.

    This in-memory tree does not publish lessons or grant PRD approvals.
    Failed review/generation leaves its edge pending for explicit resume.
    """
    def __init__(self, artifacts, parents):
        from collections import deque
        self._artifacts = {}
        for artifact in artifacts:
            if artifact.key in self._artifacts:
                raise ValueError('자료 코드가 중복돼요.')
            self._artifacts[artifact.key] = artifact
        self._parents = dict(parents)
        self._children = {key: [] for key in self._artifacts}
        self._generated = {}
        self._reviewed = {}
        self._pending = deque()
        for child, parent in self._parents.items():
            if child not in self._artifacts or parent not in self._artifacts:
                raise ValueError('연결된 자료가 없어요.')
            source, target = self.artifact(parent), self.artifact(child)
            if target.layer not in ADJACENT[source.layer]:
                raise ValueError('바로 인접한 레이어만 연결할 수 있어요.')
            self._children[parent].append(child)
            # Importing existing text does not prove which source produced it.
            self._generated[child] = None
            self._reviewed[child] = None

    def artifact(self, key):
        return self._artifacts[key]

    def generated_from(self, key):
        return self._generated[key]

    def reviewed_from(self, key):
        return self._reviewed[key]

    def apply(self, replacement, ledger, assessor, generator, *, assessor_key, generator_key=None):
        if self._pending:
            raise ValueError('이전 변경의 미완료 검토를 먼저 이어가세요.')
        before = self.artifact(replacement.key)
        if before.layer != replacement.layer:
            raise ValueError('자료의 레이어는 바꿀 수 없어요.')
        if before.revision == replacement.revision:
            return
        self._artifacts[replacement.key] = replacement
        if replacement.key in self._parents:
            self._generated[replacement.key] = None
            self._reviewed[replacement.key] = None
        self._pending.extend((before, replacement, child) for child in self._children[replacement.key])
        self.resume(ledger, assessor, generator, assessor_key=assessor_key, generator_key=generator_key)

    def resume(self, ledger, assessor, generator, *, assessor_key, generator_key=None):
        while self._pending:
            before, after, key = self._pending[0]
            target = self.artifact(key)
            if self.artifact(after.key).revision != after.revision:
                raise ValueError('검토 중 원본이 바뀌었어요.')
            decision = ledger.assess(before, after, target, assessor, assessor_key=assessor_key)
            if not decision.change_required:
                # Evidence of reviewing new input is not the provenance of old output.
                self._reviewed[key] = after.revision
                self._pending.popleft()
                continue
            generated = ledger.generate(before, after, target, decision, generator, generator_key=generator_key)
            self._artifacts[key] = generated
            self._generated[key] = after.revision
            self._reviewed[key] = after.revision
            self._pending.popleft()
            self._pending.extend((target, generated, child) for child in self._children[key])
