"""Shared helpers for final-challenge specs: hand-written narration with exact line targets."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location('java_contract', Path(__file__).resolve().parents[1] / 'java-contract.py')
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
contract = _module.contract


class Script:
    """Narration for a code step. Tracks the editor source so every run highlights real lines."""

    def __init__(self, starter):
        self.source = starter
        self.actions = []
        self.snapshots = []

    def say(self, text, target):
        self.actions.append(dict(action='say', text=text, target=target))
        return self

    def patch(self, before, after, say):
        if self.source.count(before) != 1:
            raise ValueError(f'patch must select one region: {before!r}')
        self.source = self.source.replace(before, after, 1)
        self.actions.append(dict(action='patch_code', before=before, after=after, say=say))
        return self

    def run(self, first=None, last=None, expect_error=None):
        lines = self.source.splitlines()
        if first is None:
            marked = [i + 1 for i, line in enumerate(lines) if 'print' in line]
            if not marked:
                marked = [i + 1 for i, line in enumerate(lines) if line.strip() not in ('', '{', '}', '};')][:1]
            span = [marked[0], marked[-1]]
        else:
            start = next(i + 1 for i, line in enumerate(lines) if first in line)
            end = next(i + 1 for i, line in enumerate(lines) if (last or first) in line and i + 1 >= start)
            span = [start, end]
        action = dict(action='run', lines=span)
        if expect_error:
            action['expect_error'] = expect_error
        self.actions.append(action)
        self.snapshots.append(self.source)
        return self

    def input(self, value):
        self.actions.append(dict(action='set_input', value=value))
        return self


def todo(*items):
    return '**할 일**\n\n' + '\n'.join(f'{i}. {item}' for i, item in enumerate(items, 1))
