"""Validate and render a self-contained lesson PRD before producing lesson content."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import uuid


def content_hash(document):
    value = {key: data for key, data in document.items() if key != 'approval'}
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def policy_revision(artifacts):
    """Hash an ordered JSON snapshot after normalizing all line endings to LF."""
    normalized = [dict(path=item['path'], text=item['text'].replace('\r\n', '\n').replace('\r', '\n')) for item in artifacts]
    payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return 'sha256:' + hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} 내용을 확인하세요.')


def _items(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError(f'{label} 항목이 필요해요.')
    for item in value:
        _text(item, label)


def _records(value, label):
    if not isinstance(value, list) or not value or any(not isinstance(item, dict) for item in value):
        raise ValueError(f'{label} 구성을 확인하세요.')
    return value


def _code(value, prefix, used):
    if not isinstance(value, str) or not value.startswith(prefix + '_'):
        raise ValueError('리소스 코드 종류를 확인하세요.')
    try:
        parsed = uuid.UUID(value[len(prefix) + 1:])
    except ValueError as error:
        raise ValueError('UUID 형식을 확인하세요.') from error
    if parsed.version != 4 or str(parsed) != value[len(prefix) + 1:] or value in used:
        raise ValueError('UUID 버전·표기·중복을 확인하세요.')
    used.add(value)


def validate(document, require_approval=False):
    if not isinstance(document, dict):
        raise ValueError('PRD 객체가 필요해요.')
    if document.get('schema_version') != 1:
        raise ValueError('PRD 스키마 버전을 확인하세요.')
    used = set()
    _code(document.get('id'), 'lsn', used)
    for key in ['title', 'course', 'audience']:
        _text(document.get(key), key)
    for key in ['objectives', 'prerequisites', 'scope', 'out_of_scope', 'grading', 'reset', 'narration', 'verification']:
        _items(document.get(key), key)
    policy = document.get('policy_snapshot', {})
    if not isinstance(policy, dict):
        raise ValueError('적용 정책을 확인하세요.')
    _text(policy.get('revision'), '적용 정책 버전')
    artifacts = _records(policy.get('artifacts'), '정책 원본 스냅샷')
    paths = set()
    for artifact in artifacts:
        _text(artifact.get('path'), '정책 원본 경로')
        _text(artifact.get('text'), '정책 원본 내용')
        if artifact['path'] in paths:
            raise ValueError('정책 원본 경로가 중복돼요.')
        paths.add(artifact['path'])
    if policy['revision'] != policy_revision(artifacts):
        raise ValueError('정책 스냅샷과 적용 버전이 달라요.')
    _items(policy.get('rules'), '적용 정책')
    for source in _records(document.get('sources'), '조사 근거'):
        for key in ['url', 'checked_at', 'finding', 'certainty']:
            _text(source.get(key), '근거 ' + key)
        if not source['url'].startswith('https://'):
            raise ValueError('출처 주소를 확인하세요.')
    steps = []
    for chapter in _records(document.get('chapters'), '챕터'):
        _code(chapter.get('id'), 'chp', used)
        _text(chapter.get('title'), '챕터 제목')
        _items(chapter.get('objectives'), '챕터 교육 목표')
        for unit in _records(chapter.get('units'), '단원'):
            _code(unit.get('id'), 'unt', used)
            _text(unit.get('title'), '단원 제목')
            _items(unit.get('objectives'), '단원 교육 목표')
            _text(unit.get('premise'), '단원 기본 전제')
            for step in _records(unit.get('steps'), '스텝'):
                _code(step.get('id'), 'stp', used)
                _text(step.get('title'), '스텝 제목')
                _items(step.get('objectives'), '스텝 교육 목표')
                _text(step.get('core_flow'), '핵심 흐름')
                steps.append(step['id'])
    representative = document.get('representative', {})
    if not isinstance(representative, dict):
        raise ValueError('대표 문제를 확인하세요.')
    if representative.get('step_id') not in steps:
        raise ValueError('대표 문제의 스텝 연결을 확인하세요.')
    for key in ['prompt', 'starter_state', 'expected_action', 'acceptance', 'reset', 'narration']:
        _text(representative.get(key), '대표 문제 ' + key)
    approval = document.get('approval', {})
    if not isinstance(approval, dict):
        raise ValueError('승인 정보를 확인하세요.')
    if approval.get('status') not in ['draft', 'approved']:
        raise ValueError('승인 상태를 확인하세요.')
    if require_approval and approval.get('status') != 'approved':
        raise ValueError('사용자가 승인한 PRD로만 정식 제작하세요.')
    if approval.get('status') == 'approved':
        _text(approval.get('by'), '승인자')
        _text(approval.get('evidence'), '승인 근거')
        if approval.get('content_sha256') != content_hash(document):
            raise ValueError('승인 후 바뀐 PRD예요. 변경 범위를 검토하세요.')
    return document


def approve(document, by, evidence):
    """Call only after a trusted human approval; this function does not grant permission."""
    value = copy.deepcopy(validate(document))
    _text(by, '승인자')
    _text(evidence, '승인 근거')
    value['approval'] = dict(status='approved', by=by, evidence=evidence, content_sha256=content_hash(value))
    return validate(value, require_approval=True)


def render(document):
    validate(document)
    lines = [f"# {document['title']}", '', f"상태: {document['approval']['status']}", f"수업 코드: {document['id']}", f"코스: {document['course']}", '', '이 문서는 제작자용 PRD예요. 학생에게 핵심 흐름이나 정답을 직접 노출하지 않아요.', '']
    def section(title, items):
        lines.extend(['## ' + title, ''])
        lines.extend('- ' + item for item in items)
        lines.append('')
    section('수업 교육 목표', document['objectives'])
    section('대상과 선수 지식', [document['audience']] + document['prerequisites'])
    section('제작 범위', document['scope'])
    section('제외 범위', document['out_of_scope'])
    section('근거와 확인 한계', [f"{s['finding']} — {s['certainty']}; 확인 {s['checked_at']}. [원문]({s['url']})" for s in document['sources']])
    section('적용 교육 철학', [f"적용 버전: {document['policy_snapshot']['revision']}"] + document['policy_snapshot']['rules'])
    if document.get('strategy'):
        section('선택 교육 전략', [document['strategy']])
    lines.extend(['## 챕터·단원·스텝과 핵심 흐름', ''])
    for chapter in document['chapters']:
        lines.extend([f"### {chapter['title']}", '', '교육 목표: ' + ' / '.join(chapter['objectives']), ''])
        for unit in chapter['units']:
            lines.extend([f"#### {unit['title']}", '', '교육 목표: ' + ' / '.join(unit['objectives']), '', '공통 전제: ' + unit['premise'], ''])
            for step in unit['steps']:
                lines.extend([f"**{step['title']}**", '', f"스텝 코드: {step['id']}", '', '교육 목표: ' + ' / '.join(step['objectives']), '', step['core_flow'], ''])
    section('채점', document['grading'])
    section('초기화', document['reset'])
    section('해설', document['narration'])
    section('검증과 완료', document['verification'])
    section('대표 문제 초안', [f"{key}: {value}" for key, value in document['representative'].items() if key != 'execution_spec'])
    if 'execution_spec' in document['representative']:
        lines.extend(['### 대표 문제 검증 입력', '', '```json', json.dumps(document['representative']['execution_spec'], ensure_ascii=False, indent=2), '```', ''])
    section('제작 승인', ['PRD와 대표 문제의 승인을 함께 확인해요.', '승인된 범위 안의 수정은 가능해요. 목표나 교육 기법 변경은 다시 승인받아요.', f"내용 식별 해시: {content_hash(document)}"])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'render'])
    parser.add_argument('source', type=Path)
    parser.add_argument('--require-approval', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.source.read_text(encoding='utf-8'))
        validate(document, args.require_approval)
        if args.command == 'render':
            text = render(document)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(text, encoding='utf-8')
            else:
                print(text)
        else:
            print('PRD 검사를 통과했어요.')
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
