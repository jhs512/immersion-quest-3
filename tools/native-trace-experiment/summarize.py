"""Print a native_flow.json compactly: one line per step, only values that changed since the previous step."""
import json
import sys

doc = json.load(open(sys.argv[1], encoding='utf-8'))
print('status', doc['status'], doc.get('message', ''), 'steps', len(doc['trace']), 'stdout', repr(doc.get('stdout')))
print('verification', doc.get('verification'))


def show(value, heap, depth=0):
    if isinstance(value, list) and value and value[0] == 'REF':
        obj = heap.get(str(value[1]))
        if obj is None:
            return f'#{value[1]}?'
        if depth > 3:
            return f'#{value[1]}'
        if obj[0] == 'STRING':
            return f'#{value[1]}STRING{obj[1]!r}'
        if obj[0] == 'ARRAY':
            return f'#{value[1]}{obj[1]}[' + ', '.join(show(v, heap, depth + 1) for v in obj[2:]) + ']'
        return f'#{value[1]}{obj[1]}{{' + ', '.join(f'{k}={show(v, heap, depth + 1)}' for k, v in obj[2:]) + '}'
    return json.dumps(value, ensure_ascii=False)


seen = {}
for step in doc['trace']:
    parts = []
    for frame in step['stack_to_render']:
        changed = []
        for name, value in frame['encoded_locals'].items():
            text = show(value, step['heap'])
            key = (frame['frame_id'], name)
            if seen.get(key) != text:
                changed.append(f'{name}={text}')
                seen[key] = text
        parts.append(f"{frame['func_name']}#{frame['frame_id']}:{frame['line']} " + ' '.join(changed))
    print(f"{step['event'][:4]} L{step['line']:<3} " + ' | '.join(parts)[:500])
