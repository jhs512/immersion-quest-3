"""Authoring contract: course intent -> lesson preview -> PRD -> executable work.

Canonical previews bind only the network series, the cloud lessons and the Git worktree lesson. Existing courses'
other preview sources remain unchanged. Structural checks do not replace review.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


# Lessons whose learner-facing preview is a canonical, reviewed file bound to the course intent.
CANONICAL_PREVIEW_PREFIXES = ('network-', 'cloud-', 'git-worktree')


def course_intent(course):
    sequence=json.loads((ROOT/'tools/redesigned_courses/backend-sequence.json').read_text(encoding='utf-8'))
    return dict(objectives=course['objectives'], flow=sequence,
                presentation=course.get('presentation'), scope_boundary=course.get('scope_boundary'))


def preview_for(item, course):
    ordered = course_intent(course)['flow']['order']
    registered=[entry['key'] for entry in course['lessons']]
    if len(ordered)!=len(set(ordered)) or len(ordered)!=len(registered) or set(ordered)!=set(registered):
        raise ValueError(f"{course['key']}: flow must cover every lesson exactly once in recommended order")
    path = ROOT / Path(item['authoring_prd']).parent / 'lesson-preview.json'
    preview = json.loads(path.read_text(encoding='utf-8'))
    if preview['lesson_id'] != item['id']:
        raise ValueError(f"{item['key']}: preview identity differs")
    if preview['course_intent_sha256'] != digest(course_intent(course)):
        raise ValueError(f"{item['key']}: review changed course objectives/flow first")
    if preview['lesson_key'] not in ordered:
        raise ValueError(f"{item['key']}: lesson is not in the course flow")
    for field in ('learn', 'scenario', 'constraints'):
        if not preview.get(field) or any(not str(v).strip() for v in preview[field]):
            raise ValueError(f"{item['key']}: empty preview {field}")
    for field in ('challenge', 'question'):
        if not str(preview.get(field, '')).strip():
            raise ValueError(f"{item['key']}: empty preview {field}")
    return preview


def validate_alignment(item, course, prd, authored):
    preview = preview_for(item, course)
    if prd.get('lesson_preview') and public_preview(prd['lesson_preview']) != public_preview(preview):
        raise ValueError(f"{item['key']}: PRD snapshot disagrees with the canonical preview")
    binding = json.loads((ROOT / Path(item['authoring_prd']).parent / 'preview-alignment.json').read_text(encoding='utf-8'))
    actual = alignment_source(preview, prd, authored)
    if binding['source_sha256'] != digest(actual):
        raise ValueError(f"{item['key']}: preview/PRD/content alignment needs review")
    if binding['status'] not in ('migration_needs_semantic_review', 'reviewed'):
        raise ValueError(f"{item['key']}: unknown alignment review status")
    return preview


def alignment_source(preview, prd, authored):
    return dict(preview_sha256=digest(preview),
                # Include hierarchy, premises, grading and reset rules, not just leaf objectives.
                prd_contract={key: value for key, value in prd.items()
                              if key not in ('approval', 'policy_snapshot')},
                content_metadata={key: value for key, value in authored.items() if key != 'tasks'},
                # Files and custom checkers can change a problem as much as its visible code.
                # Narration/supporting materials are the next layer and have their own freshness gate.
                tasks=[{key: value for key, value in task.items()
                        if key not in ('narration', 'supporting_materials')} for task in authored['tasks']])


def public_preview(preview):
    return {key: preview[key] for key in ('learn', 'challenge', 'scenario', 'constraints', 'question')}
