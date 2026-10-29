"""Small builders for conversion specs. Line numbers are computed from the code, never typed."""


def line_of(code, needle, nth=1):
    found = 0
    for number, text in enumerate(code.splitlines(), 1):
        if needle in text:
            found += 1
            if found == nth:
                return number
    raise ValueError(f'line not found: {needle!r}')


def say(text, target):
    return {'action': 'say', 'text': text, 'target': target}


def patch(before, after, spoken):
    return {'action': 'patch_code', 'before': before, 'after': after, 'say': spoken}


def run(code, first, last=None):
    """Run while highlighting the print lines that the next sentence reads (in `code` as it is then)."""
    a = line_of(code, first)
    b = line_of(code, last) if last else a
    return {'action': 'run', 'lines': [a, b]}


def run_error(code, first, error, last=None):
    action = run(code, first, last)
    action['expect_error'] = error
    return action


def set_input(value):
    return {'action': 'set_input', 'value': value}


def apply_patches(code, actions):
    """The code after the narration's patches, to compute later line numbers."""
    for action in actions:
        if action['action'] == 'patch_code':
            if code.count(action['before']) != 1:
                raise ValueError(f"patch not unique: {action['before']!r}")
            code = code.replace(action['before'], action['after'], 1)
    return code


def todo(*items):
    return '**할 일**\n\n' + '\n'.join(f'{i}. {item}' for i, item in enumerate(items, 1))


class Script:
    """A narration written in order: patches update the code that later highlights are computed on."""

    def __init__(self, code):
        self.code = code
        self.actions = []

    def say(self, text, target):
        self.actions.append(say(text, target))
        return self

    def patch(self, before, after, spoken):
        if self.code.count(before) != 1:
            raise ValueError(f'patch not unique: {before!r}')
        self.code = self.code.replace(before, after, 1)
        self.actions.append(patch(before, after, spoken))
        return self

    def run(self, first, last=None, error=None):
        action = run(self.code, first, last)
        if error:
            action['expect_error'] = error
        self.actions.append(action)
        return self

    def input(self, value):
        self.actions.append(set_input(value))
        return self
