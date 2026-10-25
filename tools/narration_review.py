"""Meaning review of redesigned narration, kept apart from the deterministic build checks.

The build (tools/build-redesigned-git.py) checks form: targets exist, commands are followed by a result,
no boilerplate, no copied caution. It cannot tell whether a sentence says something true and clear about
this step. That judgement is a reviewer's (docs/agents/narration.md 「해설 문장 검토」); this module makes it
traceable and keeps it fresh:

- context: everything a sentence must agree with (objectives, goal, start/demo/goal state, commands, code,
  all narration). Its sha256 ties a review to the exact source it looked at.
- prompts: sentences a reviewer must look at, found deterministically (every 「조심하세요」 sentence and
  concessive clauses). A prompt is not a verdict; the reviewer decides keep or fix with a reason.
- ledger tools/redesigned_lessons/narration-review.json, one entry per step:
  state "baseline" = published before this gate and NOT reviewed for meaning; accepted only while unchanged.
  state "reviewed" = a reviewer pass covered every prompt (kept with a note, or fixed with issue/reason).
  An "open" finding blocks the build. A changed context makes the entry stale, so an old review is never
  reused for new text.

CLI:
  python tools/narration_review.py status
  python tools/narration_review.py packet <lesson-key|all> [--prompts-only]
  python tools/narration_review.py baseline            # entries for steps that have none (never overwrites)
  python tools/narration_review.py record <decisions.json> [--dry-run]
"""
import argparse
import copy
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'tools/redesigned_lessons/narration-review.json'
CAUTION = '조심하세요'
# Concession sets up a contrast (A이어도 B): B must actually contrast with A. Bash9's
# 「이름이 같아도 지금 위치 notes 안에 만들어요」 sets one up and never delivers it.
CONCESSIVE = re.compile(r'[가-힣]+(?:아도|어도|해도|라도|여도|더라도)(?=[\s,.?!]|$)')


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def spoken(action):
    return (action.get('text') or action.get('say') or '').strip()


def context(step, task):
    """What every sentence of this step has to agree with, including the narration itself."""
    return {'objectives': step['objectives'], 'task': task}


def context_sha256(step, task):
    return digest(context(step, task))


def prompts(task):
    """Spoken items a reviewer must look at, with the deterministic reason. Not verdicts."""
    found = []
    for action in task.get('narration', []):
        text = spoken(action)
        reasons = []
        if CAUTION in text:
            reasons.append('caution: names a real, likely mistake of this step and its consequence?')
        for match in CONCESSIVE.finditer(text):
            reasons.append(f'concession 「{match.group(0)}」: does the following clause really contrast with it?')
        if reasons and text not in [item['text'] for item in found]:
            found.append({'text': text, 'reasons': reasons})
    return found


def load_ledger(path=LEDGER):
    if not path.exists():
        return {'schema': 1, 'procedure': 'docs/agents/narration.md 「해설 문장 검토」', 'steps': {}}
    return json.loads(path.read_text(encoding='utf-8'))


def save_ledger(ledger, path=LEDGER):
    ledger['steps'] = dict(sorted(ledger['steps'].items(), key=lambda item: (item[1]['lesson'], item[0])))
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')


def problems(lesson, step, task, entry):
    """Why this step's review record does not cover its current narration (empty = covered)."""
    label = f"{lesson} {step['id']} 「{task.get('title', '')}」"
    if entry is None:
        return [f'{label}: 해설 검토 기록이 없어요. tools/narration_review.py로 검토를 기록하세요.']
    if entry.get('lesson') != lesson:
        return [f'{label}: 검토 기록의 수업이 달라요.']
    if entry.get('context_sha256') != context_sha256(step, task):
        return [f'{label}: 해설이나 문제가 검토 뒤 바뀌었어요. 바뀐 스텝을 다시 검토하세요(이전 검토는 쓰지 않아요).']
    found = []
    for finding in entry.get('findings', []):
        if finding.get('status') not in ('fixed', 'kept', 'open'):
            found.append(f"{label}: 검토 결과 상태가 잘못됐어요: {finding.get('status')}")
        elif finding['status'] == 'open':
            found.append(f"{label}: 해결하지 않은 해설 문제가 있어요: 「{finding.get('sentence', '')[:40]}」 {finding.get('issue', '')}")
        for key in ('sentence', 'issue', 'reason'):
            if not str(finding.get(key, '')).strip():
                found.append(f'{label}: 검토 결과에 {key}가 없어요.')
    state = entry.get('state')
    if state == 'baseline':
        return found
    if state != 'reviewed':
        return found + [f'{label}: 검토 상태가 잘못됐어요: {state}']
    current = {spoken(action) for action in task.get('narration', [])}
    covered = set(entry.get('checked', {}))
    superseded = superseded_fixes(entry.get('findings', []))
    for finding in entry.get('findings', []):
        if finding.get('status') == 'fixed' and finding.get('fix') in superseded:
            continue  # a later review fixed this fix again; the later finding is checked instead
        if finding.get('status') == 'fixed' and finding.get('fix') == '':
            if finding.get('sentence') in current:
                found.append(f"{label}: 지운 문장이 아직 해설에 있어요: 「{str(finding.get('sentence', ''))[:40]}」")
        elif finding.get('status') == 'fixed':
            if finding.get('fix') not in current:
                found.append(f"{label}: 고친 문장이 현재 해설에 없어요: 「{str(finding.get('fix', ''))[:40]}」")
            covered.add(finding.get('fix'))
        elif finding.get('status') == 'kept':
            covered.add(finding.get('sentence'))
    for note in entry.get('checked', {}).values():
        if not str(note).strip():
            found.append(f'{label}: 문제없다고 본 문장에 이유가 없어요.')
    for prompt in prompts(task):
        if prompt['text'] not in covered:
            found.append(f"{label}: 검토하지 않은 문장이 있어요: 「{prompt['text'][:40]}」")
    return found


def superseded_fixes(findings):
    """Fix texts that a later fixed finding of the same step replaced or removed again (a fix chain)."""
    fixed = [f for f in findings if f.get('status') == 'fixed']
    return {f.get('fix') for i, f in enumerate(fixed) if f.get('fix')
            and any(later.get('sentence') == f.get('fix') for later in fixed[i + 1:])}


def check_lesson(lesson, steps, tasks, ledger=None):
    """Build gate. Raises with every uncovered step of the lesson."""
    ledger = load_ledger() if ledger is None else ledger
    found = []
    for step, task in zip(steps, tasks):
        found += problems(lesson, step, task, ledger['steps'].get(step['id']))
    if found:
        raise ValueError('해설 문장 검토가 현재 해설을 덮지 않아요:\n  ' + '\n  '.join(found[:20])
                         + (f'\n  … 외 {len(found) - 20}건' if len(found) > 20 else ''))


# ---- registry access ---------------------------------------------------------------------------

def lessons():
    sys.path.insert(0, str(ROOT / 'tools'))
    from lesson_registry import load_registry
    return {row['key']: row['folder'] for row in load_registry()}


def load(lesson):
    folder = ROOT / 'tools/redesigned_lessons' / lessons()[lesson]
    prd = json.loads((folder / 'approved-prd.json').read_text(encoding='utf-8'))
    authored = json.loads((folder / 'content.json').read_text(encoding='utf-8'))
    steps = [step for chapter in prd['chapters'] for unit in chapter['units'] for step in unit['steps']]
    return folder, prd, authored, steps


def terminal_summary(task):
    terminal = task.get('git_terminal') or {}
    shell = terminal.get('shell') or {}
    summary = {}
    for key in ('start', 'demo', 'goal'):
        if key in shell:
            summary[key] = shell[key]
    if shell.get('commands'):
        summary['commands'] = shell['commands']
    for key in ('files', 'setup', 'state_goal', 'commands', 'initial_history'):
        if terminal.get(key):
            summary[key] = terminal[key]
    return summary


def packet(lesson, prompts_only=False):
    """Plain-text review packet: per step the objective, goal, state, code and the whole narration."""
    _, prd, authored, steps = load(lesson)
    lines = [f'# {lesson} — {prd["title"]}']
    tasks = authored['tasks']
    for index, (step, task) in enumerate(zip(steps, tasks)):
        found = prompts(task)
        if prompts_only and not found:
            continue
        lines.append(f'\n## {index + 1}. {task["title"]}  ({step["id"]})')
        lines.append('objectives: ' + ' / '.join(step['objectives']))
        lines.append('goal: ' + task['goal'].replace('\n', ' ⏎ '))
        state = terminal_summary(task)
        if state:
            lines.append('terminal: ' + json.dumps(state, ensure_ascii=False))
        for key in ('question', 'starter_code', 'example_code', 'solution'):
            if task.get(key):
                lines.append(f'{key}: ' + str(task[key]).replace('\n', ' ⏎ ')[:900])
        if task.get('interaction'):
            lines.append('interaction: ' + json.dumps(task['interaction'], ensure_ascii=False)[:900])
        if index:
            previous = [spoken(a) for a in tasks[index - 1].get('narration', []) if spoken(a)]
            if previous:
                lines.append('previous step ends: ' + previous[-1])
        for action in task.get('narration', []):
            mark = '  >> ' if any(p['text'] == spoken(action) for p in found) else '     '
            detail = action.get('command') or action.get('keys') or ''
            lines.append(f"{mark}[{action['action']}{' ' + detail if detail else ''}] {spoken(action)}  <{action.get('target', '')}>")
        if index + 1 < len(tasks):
            following = [spoken(a) for a in tasks[index + 1].get('narration', []) if spoken(a)]
            if following:
                lines.append('next step starts: ' + following[0])
    return '\n'.join(lines)


def baseline(ledger):
    added = 0
    for lesson in lessons():
        _, _, authored, steps = load(lesson)
        for step, task in zip(steps, authored['tasks']):
            if step['id'] in ledger['steps']:
                continue
            ledger['steps'][step['id']] = {'lesson': lesson, 'state': 'baseline', 'context_sha256': context_sha256(step, task),
                                           'note': 'published before the meaning review gate; not reviewed for meaning'}
            added += 1
    return added


def record(decisions, ledger, dry_run=False):
    """Apply a reviewer pass. decisions: [{lesson, step, checked: {text: note}, findings: [{sentence, issue,
    reason, fix?, status}]}]. A fixed finding replaces exactly one spoken item of that step in content.json;
    commands, keys and code are never touched. The step entry is then written against the new context."""
    today = datetime.date.today().isoformat()
    by_lesson = {}
    for decision in decisions:
        by_lesson.setdefault(decision['lesson'], []).append(decision)
    changed = []
    for lesson, items in by_lesson.items():
        folder, _, authored, steps = load(lesson)
        tasks = {task['id']: task for task in authored['tasks']}
        step_of = {step['id']: step for step in steps}
        before = copy.deepcopy(authored)
        for decision in items:
            task = tasks[decision['step']]
            for finding in decision.get('findings', []):
                if finding['status'] != 'fixed':
                    continue
                matches = [action for action in task['narration'] if spoken(action) == finding['sentence']]
                earlier = ledger['steps'].get(decision['step'], {}).get('findings', [])
                if not matches and finding in earlier:
                    continue  # applied by an earlier review of this step: re-recording never applies it twice
                if len(matches) != 1:
                    raise ValueError(f"{lesson} {decision['step']}: 고칠 문장을 정확히 하나 찾지 못했어요: {finding['sentence'][:40]}")
                action = matches[0]
                if finding['fix'] == '':
                    # A sentence that only repeats its neighbour: removed. Only a plain say can go;
                    # a command or edit keeps its action and needs a replacement sentence instead.
                    if action['action'] != 'say':
                        raise ValueError(f"{lesson} {decision['step']}: 말만 하는 문장만 지울 수 있어요: {finding['sentence'][:40]}")
                    task['narration'].remove(action)
                    continue
                field = 'text' if action.get('text') else 'say'
                action[field] = finding['fix']
        for decision in items:
            task = tasks[decision['step']]
            step = step_of[decision['step']]
            entry = {'lesson': lesson, 'state': 'reviewed', 'context_sha256': context_sha256(step, task),
                     'reviewed': today, 'checked': decision.get('checked', {}), 'findings': decision.get('findings', [])}
            found = problems(lesson, step, task, entry)
            if found:
                raise ValueError('\n'.join(found))
            ledger['steps'][step['id']] = entry
        if authored != before:
            changed.append(lesson)
            if not dry_run:
                path = folder / 'content.json'
                # Same layout as the authored file (indent 2), keeping its line endings.
                newline = '\r\n' if b'\r\n' in path.read_bytes() else '\n'
                path.write_text(json.dumps(authored, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline=newline)
    return changed


def status(ledger):
    counts = {}
    for entry in ledger['steps'].values():
        counts[entry['state']] = counts.get(entry['state'], 0) + 1
    findings = [f for entry in ledger['steps'].values() for f in entry.get('findings', [])]
    stale = []
    for lesson in lessons():
        _, _, authored, steps = load(lesson)
        for step, task in zip(steps, authored['tasks']):
            stale += problems(lesson, step, task, ledger['steps'].get(step['id']))
    return {'entries': counts, 'findings': {s: sum(f['status'] == s for f in findings) for s in ('fixed', 'kept', 'open')},
            'uncovered': len(stale), 'first_uncovered': stale[:5]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    p = sub.add_parser('packet'); p.add_argument('lesson'); p.add_argument('--prompts-only', action='store_true')
    sub.add_parser('baseline')
    r = sub.add_parser('record'); r.add_argument('decisions'); r.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    ledger = load_ledger()
    if args.command == 'status':
        print(json.dumps(status(ledger), ensure_ascii=False, indent=1))
    elif args.command == 'packet':
        for lesson in (lessons() if args.lesson == 'all' else [args.lesson]):
            print(packet(lesson, args.prompts_only))
    elif args.command == 'baseline':
        added = baseline(ledger)
        save_ledger(ledger)
        print(f'baseline entries added: {added}')
    elif args.command == 'record':
        decisions = json.loads(Path(args.decisions).read_text(encoding='utf-8'))
        changed = record(decisions, ledger, args.dry_run)
        if not args.dry_run:
            save_ledger(ledger)
        print(json.dumps({'recorded_steps': len(decisions), 'changed_lessons': changed, 'dry_run': args.dry_run}, ensure_ascii=False))


if __name__ == '__main__':
    main()
