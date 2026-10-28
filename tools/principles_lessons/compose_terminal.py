"""Compose·Dockerfile steps in the learner's real terminal (git_terminal.docker.compose).

The learner edits compose.yaml, a Dockerfile, app files or migration.sql in the editor above the
terminal. The editor saves into the terminal's own folder, which is the Compose project directory.
The learner types `docker compose …` at the real Bash prompt and reads Docker's own output. The app
only checks the files before compose runs (src/docker_lab/terminal.rs) and grades by reading: the
commands the shell completed with the current files, the files, and the real engine state of the
step's own project (src/docker_practice.rs, ComposeCheck). Nothing here runs a lab script.
"""

TERMINAL = '#git-demo-terminal'
TODO_SUBMIT = '결과를 확인한 뒤 제출 버튼을 누르세요.'


def type_command(command, observe=''):
    """A todo item: one command, typed and entered by the learner."""
    return f'터미널에 `{command}` 명령을 입력하고 Enter를 누르세요.' + (f' {observe}' if observe else '')


def bash(command, say, fails=False, wait=None):
    """A narration item: the narration types this command in its own terminal; the next item reads it."""
    extra = {key: value for key, value in (('fails', fails), ('wait_seconds', wait)) if value}
    return ('bash', command, say, TERMINAL) + ((extra,) if extra else ())


def patch(file, before, after, say):
    """A narration item: the narration edits this file in its own editor (saved in its own folder)."""
    return ('patch', before, after, say, file)


def snapshot(files):
    return dict(files=dict(files), directories=sorted({path.rsplit('/', 1)[0] for path in files if '/' in path}), cwd='')


def compose_step(*, slug, title, objectives, start, intro, know, images, editable, files, solution_files,
                 commands, todo, checks, narration, success, complexity, review, same_files=None,
                 setup=(), accepts=(), rejects=()):
    """files: the step's start files (editable ones included); solution_files: the editable files after
    the fix. commands: the graded commands, typed with the fixed files. accepts/rejects replace text
    in the solution files; the validator types the same commands and expects a pass or a failure.
    setup: commands typed from the step's start before the graded ones. They belong to the full
    solution and the narration; their result is graded as engine state, not as typed commands."""
    goal = {**files, **solution_files}
    for name in editable:
        if name not in files or name not in goal:
            raise ValueError(f'{slug}: editable file {name} needs start and solution content')
    shell = dict(start=snapshot(files), demo=snapshot(files), goal=snapshot(goal), commands=list(commands), requires_vim=False)
    terminal = dict(initial_history='uninitialized', shell=shell,
                    docker=dict(compose=dict(images=list(images), editable=list(editable),
                                             same_files=list(editable if same_files is None else same_files),
                                             checks=list(checks))))
    return dict(slug=slug, title=title, objectives=list(objectives), language='docker', docker_images=list(images),
                git_terminal=terminal, start=start, intro=list(intro), know=know, todo=list(todo) + [TODO_SUBMIT],
                starter='', solution='\n'.join([*setup, *commands]), tests=[], success=success, complexity=complexity,
                narration=list(narration), review=dict(review), accepts=list(accepts), rejects=list(rejects))


# Read-only checks (src/docker_practice.rs ComposeCheck).
def running(service):
    return dict(kind='running', service=service)


def mount(service, target, volume=None):
    return dict(kind='mount', service=service, target=target, **({'volume': volume} if volume else {}))


def logs(service, *has):
    return dict(kind='logs', service=service, has=list(has))


def read(what, service, command, has=(), lacks=()):
    return dict(kind='exec', what=what, service=service, command=list(command), has=list(has), lacks=list(lacks))


def file_text(path, has=(), lacks=()):
    return dict(kind='file', path=path, has=list(has), lacks=list(lacks))


def config(what, expect):
    return dict(kind='config', what=what, expect=expect)


def history(service, *order):
    return dict(kind='history', service=service, order=list(order))


def http(service, port, has):
    return dict(kind='http', service=service, port=port, has=has)
