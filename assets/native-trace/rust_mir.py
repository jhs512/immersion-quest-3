"""Ownership events of user bindings, read from the MIR of the same rustc and the same source.

Stable rustc emits only the final, optimized MIR, where a last use can turn `move` into `copy`. Moves as the borrow
checker sees them are in the `built` MIR, which the same rustc dumps (with source positions) when -Z options are
allowed (RUSTC_BOOTSTRAP=1). That compile's binary is not used: `same_mir` checks that its final MIR equals the
final MIR of the build that made the executed binary, once position comments are removed.
"""
import re

BODY = re.compile(r'^fn (.+?)\(.*\{\s*$')
RETURN = re.compile(r'^\s*let mut _0: .*// return place in scope \d+ at (.+?):(\d+):')
BLOCK = re.compile(r'^\s*bb\d+( \(cleanup\))?: \{')
DEBUG = re.compile(r'^\s*debug ([A-Za-z_][A-Za-z0-9_]*) => (_\d+);\s*// in scope \d+ at (.+?):(\d+):(\d+):')
STATEMENT = re.compile(r'^\s*(.+?);?\s*// scope \d+ at (.+?):(\d+):(\d+): ')
CALL = re.compile(r'= (?:<[^>]*>::)?((?:[A-Za-z_][A-Za-z0-9_]*::)*[A-Za-z_][A-Za-z0-9_]*)(?:::<.*?>)?\(')


def normalized(text):
    lines = []
    for line in text.splitlines():
        line = re.sub(r'\s*//.*$', '', line).rstrip()
        if line:
            lines.append(line)
    return lines


def same_mir(stable, spans):
    return normalized(stable) == normalized(spans)


def events(text, source_name, source):
    """Ownership facts of every body in `text`.

    events: {line: [event, ...]} in MIR order; event is [kind, binding, field] or ['call', name], where binding is
    'name@declared_line' and kind is init, move, move_field or init_field.
    entries: {signature line: line of the body's first statement}.
    hidden: bindings the compiler made (a `for` loop's `iter`), whose name is not written at their position.
    """
    found, entries, hidden = {}, {}, set()
    lines = source.splitlines()
    bindings, body, signature = {}, [], None

    def finish():
        if signature is not None and body:
            entries.setdefault(str(signature), body[0][0])
        for line, code in body:
            out = []
            for local, field in re.findall(r'move \((_\d+)\.(\d+): ', code):
                if local in bindings:
                    out.append(['move_field', bindings[local], int(field)])
            for local in re.findall(r'move (_\d+)\b(?!\.)', code):
                if local in bindings:
                    out.append(['move', bindings[local], None])
            assigned = re.match(r'(_\d+) = ', code)
            field_assigned = re.match(r'\((_\d+)\.(\d+): [^)]*\) = ', code)
            call = CALL.search(code)
            if call:
                out.append(['call', call.group(1).split('::')[-1]])
            # The assignment happens after its right-hand side (and any call in it) is evaluated.
            if assigned and assigned.group(1) in bindings:
                out.append(['init', bindings[assigned.group(1)], None])
            if field_assigned and field_assigned.group(1) in bindings:
                out.append(['init_field', bindings[field_assigned.group(1)], int(field_assigned.group(2))])
            if out:
                found.setdefault(line, []).extend(out)

    cleanup = False
    for raw in text.splitlines():
        header = BODY.match(raw)
        if header:
            finish()
            bindings, body, cleanup, signature = {}, [], False, None
            continue
        returned = RETURN.match(raw)
        if returned and returned.group(1) == source_name:
            signature = int(returned.group(2))
            continue
        block = BLOCK.match(raw)
        if block:
            cleanup = bool(block.group(1))
            continue
        if cleanup:
            continue
        debug = DEBUG.match(raw)
        if debug:
            name, local, file, line = debug.group(1), debug.group(2), debug.group(3), int(debug.group(4))
            if file == source_name:
                bindings[local] = f'{name}@{line}'
                column = int(debug.group(5))
                written = re.sub(r'^(?:ref\s+)?(?:mut\s+)?', '', lines[line - 1][column - 1:]) if line <= len(lines) else ''
                if not re.match(re.escape(name) + r'\b', written):
                    hidden.add(bindings[local])
            continue
        statement = STATEMENT.match(raw)
        if statement and statement.group(2) == source_name:
            body.append((int(statement.group(3)), statement.group(1)))
    finish()
    return {'events': {str(line): items for line, items in found.items()}, 'entries': entries, 'hidden': sorted(hidden)}
