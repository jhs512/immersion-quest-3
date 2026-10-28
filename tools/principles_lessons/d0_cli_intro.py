"""Real Nginx CLI before Compose, typed by the learner in a real terminal.

Each step is a Docker terminal step (git_terminal.docker): the learner types the docker command
at a real Bash prompt and presses Enter. The real Docker CLI prints its own output. Grading reads
the commands the learner's shell completed and the actual engine state of the lesson's container
(src/docker_practice.rs). The steps form one chain: the lesson session keeps the container while
the learner moves between steps, and prepares only a missing start state (src/docker_lab/terminal.rs).
"""

NGINX = 'nginx:1.28-alpine'
NGINX_PIN = NGINX + '@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236'
TERMINAL = '#git-demo-terminal'
TODO_SUBMIT = '확인한 뒤 제출 버튼을 누르세요.'
ISOLATION = ('BOX에는 이번 수업만의 고유한 컨테이너 이름이 들어 있어요. 다른 컨테이너 이름과 겹치지 않아요. '
             '문제를 옮겨 다녀도 컨테이너는 그대로 남아요. 이 문제의 시작 상태로 돌아가려면 초기화를 누르세요. '
             '수업을 나가면 이 수업이 만든 것만 정리해요.')


def todo_command(command, observe):
    return f'터미널에 `{command}` 명령을 입력하고 Enter를 누르세요. {observe}'


def cli_step(*, slug, title, concept, start, intro, know, docker_start, goal, commands, narration, success, evidence, review, wait=None, opening=None):
    """commands: [(command, what to read in its output)]; narration: authored items after the intro.

    opening: the spoken first line. It frames the start state instead of re-reading the highlighted intro
    (2026-10-28 narration audit: do not read the body text aloud again)."""
    shell = dict(goal=dict(files={}, directories=[], cwd=''), demo=dict(files={}, directories=[], cwd=''),
                 commands=[command for command, _ in commands], requires_vim=False)
    terminal = dict(initial_history='uninitialized', workspace_group='docker-cli', workspace_revision='docker-cli-1',
                    shell=shell, docker=dict(image=NGINX_PIN, container='nginx', port=80, start=docker_start, goal=goal))
    return dict(slug=slug, title=title, language='docker', docker_images=[NGINX_PIN], git_terminal=terminal,
        start=start, objectives=[concept], intro=[intro], know=know,
        todo=[todo_command(command, observe) for command, observe in commands] + [TODO_SUBMIT],
        starter='', solution='\n'.join(command for command, _ in commands), tests=[], success=success,
        complexity=dict(prior='터미널에서 명령을 실행해 봤어요.', new=concept, changed=title,
                        evidence=evidence, lines=len(commands), services=1 if slug == 'cli-run' else 0),
        narration=[('say', opening or intro, 'text:' + intro)] + narration, review=review)


def bash(command, say, wait=None, fails=False):
    extra = {key: value for key, value in (('wait_seconds', wait), ('fails', fails)) if value}
    return ('bash', command, say, TERMINAL) + ((extra,) if extra else ())


def chapter(_image):
    run = 'docker run -d --name "$BOX" -p 127.0.0.1::80 nginx:1.28-alpine'
    steps = [
        cli_step(slug='cli-pull', opening='직접 설치하면 컴퓨터마다 버전과 과정이 달라져요. 같은 태그의 이미지를 받으면 모두 같은 재료로 시작해요.',
            title='실행하기 전에 이미지를 내려받으세요',
            concept='이미지는 프로그램과 실행에 필요한 파일을 묶은 재료예요.',
            start='오른쪽은 이 컴퓨터의 실제 Bash 터미널이에요. 입력한 docker 명령은 실제 Docker가 실행해요. 이번 수업의 컨테이너는 아직 없어요.',
            intro='Nginx는 웹 페이지를 보내 주는 서버예요. 직접 설치하면 컴퓨터마다 설치 과정이 달라져요. 같은 버전의 이미지로 실행 재료를 맞춰 보세요.',
            know='nginx:1.28-alpine에서 콜론 뒤는 이미지의 태그예요. pull은 이미지를 받아요. 서버를 실행하지는 않아요. 이미 받아 둔 이미지라면 최신 상태라는 안내가 나와요. ' + ISOLATION,
            docker_start='absent', goal=dict(image_present=True),
            commands=[('docker pull nginx:1.28-alpine', '출력의 Status 줄에서 받은 이미지 이름을 읽으세요.')],
            narration=[bash('docker pull nginx:1.28-alpine', '이미지는 프로그램과 실행에 필요한 파일을 묶은 재료예요.', wait=900),
                       ('say', '레이어를 받는 줄과 Status 줄이 보여요. 이미 받아 뒀다면 최신 상태라고 나와요.', TERMINAL),
                       ('say', '조심하세요. 이미지가 있어도 웹 서버가 켜진 것은 아니에요. 아직 컨테이너는 없어요.', 'text:pull은 이미지를 받아요. 서버를 실행하지는 않아요.')],
            success='터미널에서 pull이 성공했고 이 컴퓨터에 nginx:1.28-alpine 이미지가 있어요.',
            evidence='터미널의 실제 pull 출력과 이미지 존재',
            review={'조심하세요. 이미지가 있어도 웹 서버가 켜진 것은 아니에요. 아직 컨테이너는 없어요.': 'pull과 실행을 같은 일로 오해하기 쉬워요. 다음 문제의 run과 구별해요.'}),
        cli_step(slug='cli-run', opening='이미지는 이미 받아 둔 상태예요. 이번에는 그 이미지로 서버를 켜요.',
            title='이미지로 컨테이너 하나를 실행하세요',
            concept='run은 이미지에서 새 컨테이너를 만들고 서버를 시작해요.',
            start='앞 문제에서 받은 Nginx 이미지로 시작해요. 이번 수업의 컨테이너는 아직 없어요.',
            intro='Nginx 이미지는 준비됐어요. 이제 그 이미지로 웹 서버를 실행하세요.',
            know='-d는 서버를 뒤에서 실행해요. --name은 이름을 붙여요. "$BOX"는 터미널에 미리 들어 있는 이번 수업의 이름이에요. -p 127.0.0.1::80은 컨테이너의 80번 포트를 연결해요. 가운데가 비어 있어 호스트의 빈 포트를 Docker가 골라요. ' + ISOLATION,
            docker_start='absent', goal=dict(container='running', created_from_image=True),
            commands=[(run, '출력된 긴 컨테이너 ID를 확인하세요.')],
            narration=[bash(run, 'run은 이미지에서 새 컨테이너를 만들고 서버를 시작해요.', wait=900),
                       ('say', '긴 컨테이너 ID가 출력됐어요. Nginx가 뒤에서 실행되고 있어요.', TERMINAL),
                       bash(run, '같은 명령을 한 번 더 입력해 볼게요.', fails=True),
                       ('say', '조심하세요. 같은 이름의 컨테이너가 이미 있어서 Conflict 오류가 나요. run은 매번 새 컨테이너를 만들거든요.', TERMINAL)],
            success='터미널에서 run이 성공했고 BOX 컨테이너가 nginx:1.28-alpine으로 실행 중이에요.',
            evidence='터미널의 실제 컨테이너 ID와 실행 상태',
            review={'조심하세요. 같은 이름의 컨테이너가 이미 있어서 Conflict 오류가 나요. run은 매번 새 컨테이너를 만들거든요.': '실제로 다시 실행해 이름 충돌 오류를 보여 줘요. 다시 켜는 start는 뒤에서 배워요.'}),
        cli_step(slug='cli-ps', opening='앞에서 켠 Nginx 컨테이너가 실행 중이에요. 이 서버의 이름과 포트를 표에서 찾아요.',
            title='이미지 목록 대신 실행 중인 컨테이너를 조회하세요',
            concept='ps는 실행 중인 컨테이너를 표로 보여 줘요.',
            start='앞 문제에서 실행한 Nginx 컨테이너가 켜져 있어요. 컨테이너가 없으면 앱이 같은 이름으로 하나 만들어 실행해 둬요.',
            intro='실행 중인 컨테이너의 이름과 포트를 찾아보세요.',
            know='docker images는 이미지를 보여 줘요. docker ps는 실행 중인 컨테이너를 보여 줘요. IMAGE·STATUS·PORTS·NAMES 열을 읽으세요. 원래 켜 두었던 컨테이너도 나올 수 있어요. mq3lab-으로 시작하는 이름이 이번 수업의 컨테이너예요. 조회만으로 다른 컨테이너가 바뀌지는 않아요.',
            docker_start='running', goal=dict(container='running'),
            commands=[('docker images', '목록에서 nginx와 1.28-alpine을 찾으세요.'),
                      ('docker ps', '표의 NAMES와 PORTS 열에서 이번 수업의 컨테이너를 찾으세요.')],
            narration=[bash('docker images', '먼저 images로 이 컴퓨터에 있는 이미지 목록을 볼게요.'),
                       ('say', '이미지 목록에 nginx 1.28-alpine이 보여요. 실행 중인지는 이 목록으로 알 수 없어요.', TERMINAL),
                       bash('docker ps', 'ps는 실행 중인 컨테이너를 표로 보여 줘요.'),
                       ('say', 'NAMES 열에서 mq3lab-으로 시작하는 이름을 찾으세요. PORTS의 화살표 왼쪽이 이 컴퓨터의 포트예요.', TERMINAL),
                       ('say', '조심하세요. 이미지를 받기만 했다면 ps 목록에는 새 컨테이너가 없어요.', 'text:docker ps는 실행 중인 컨테이너를 보여 줘요.')],
            success='터미널에서 images와 ps가 성공했고 BOX 컨테이너가 실행 중이에요.',
            evidence='터미널의 실제 images·ps 표',
            review={'조심하세요. 이미지를 받기만 했다면 ps 목록에는 새 컨테이너가 없어요.': '이미지 표와 컨테이너 표를 혼동하는 실수를 짚어요.'}),
        cli_step(slug='cli-logs', opening='Nginx는 이미 실행 중이에요. 시작하며 남긴 기록을 읽어요.',
            title='컨테이너가 시작할 때 남긴 로그를 읽으세요',
            concept='logs는 컨테이너의 주 프로세스가 남긴 출력을 읽어요.',
            start='앞 문제의 Nginx 컨테이너가 실행 중이에요. 컨테이너가 없으면 앱이 같은 이름으로 하나 만들어 실행해 둬요.',
            intro='서버가 시작하며 남긴 로그를 직접 읽으세요.',
            know='ps는 상태를 보여 줘요. logs는 실행 중에 기록한 출력을 보여 줘요. Nginx는 시작할 때 설정 확인과 작업 프로세스 시작을 기록해요.',
            docker_start='running', goal=dict(container='running', logs=True),
            commands=[('docker logs "$BOX"', 'Configuration complete로 끝나는 줄을 찾으세요.')],
            narration=[bash('docker logs "$BOX"', 'logs는 컨테이너의 주 프로세스가 남긴 출력을 읽어요.'),
                       ('say', 'Nginx의 시작 안내가 보여요. 시각과 프로세스 번호는 실행마다 달라요.', TERMINAL),
                       ('say', '조심하세요. logs가 비었다고 멈춘 것은 아니에요. 출력하지 않는 프로그램도 있어요.', 'text:logs는 실행 중에 기록한 출력을 보여 줘요.')],
            success='터미널에서 logs가 성공했고 실행 중인 BOX 컨테이너에 실제 로그가 있어요.',
            evidence='터미널의 실제 Nginx 로그',
            review={'조심하세요. logs가 비었다고 멈춘 것은 아니에요. 출력하지 않는 프로그램도 있어요.': '로그 유무와 실행 상태를 같은 것으로 보는 오해를 짚어요.'}),
        cli_step(slug='cli-exec', opening='Nginx가 실행 중이에요. 새 컨테이너 없이 그 안에서 메모를 쓰고 읽어요.',
            title='실행 중인 컨테이너 안에 메모를 쓰세요',
            concept='exec는 실행 중인 컨테이너 안에서 명령을 더 실행해요.',
            start='앞 문제의 Nginx 컨테이너가 실행 중이에요. 컨테이너가 없으면 앱이 같은 이름으로 하나 만들어 실행해 둬요.',
            intro='같은 컨테이너 안에 메모를 쓰고 읽으세요.',
            know='run은 새 컨테이너를 만들어요. exec는 기존 컨테이너에 명령을 보내요. sh -c 뒤의 명령은 컨테이너 안에서 실행돼요. echo로 쓰고 cat으로 읽어요.',
            docker_start='running', goal=dict(container='running', file=dict(path='/memo.txt', content='hello')),
            commands=[("docker exec \"$BOX\" sh -c 'echo hello > /memo.txt; cat /memo.txt'", '출력된 hello를 확인하세요.')],
            narration=[bash("docker exec \"$BOX\" sh -c 'echo hello > /memo.txt; cat /memo.txt'", 'exec는 실행 중인 컨테이너 안에서 명령을 더 실행해요.'),
                       ('say', 'cat이 읽은 hello가 그대로 출력됐어요. 같은 컨테이너 안에서 실행했어요.', TERMINAL),
                       bash('ls /memo.txt', '이번에는 docker 없이 내 컴퓨터에서 같은 경로를 찾아볼게요.', fails=True),
                       ('say', '조심하세요. 내 컴퓨터에는 /memo.txt가 없어요. 메모는 컨테이너 안에만 있어요.', TERMINAL)],
            success='터미널에서 exec가 성공했고 BOX 컨테이너 안 /memo.txt의 내용이 hello예요.',
            evidence='터미널의 실제 exec 출력과 컨테이너 안 파일',
            review={'조심하세요. 내 컴퓨터에는 /memo.txt가 없어요. 메모는 컨테이너 안에만 있어요.': '호스트에서 실제로 찾아 없다는 오류를 보여 줘요. 컨테이너 파일 시스템을 구별해요.'}),
        cli_step(slug='cli-stop', opening='지금 Nginx가 실행 중이에요. 컨테이너는 남기고 실행만 멈춰야 해요.',
            title='컨테이너를 삭제하지 않고 멈추세요',
            concept='stop은 서버를 멈추고 컨테이너는 남겨요.',
            start='앞 문제의 Nginx 컨테이너가 실행 중이에요. 컨테이너가 없으면 앱이 같은 이름으로 하나 만들어 실행해 둬요.',
            intro='컨테이너를 지우지 말고 서버만 멈추세요.',
            know='stop은 대상 컨테이너 이름을 출력해요. 멈춘 컨테이너는 docker ps -a로 확인할 수 있어요. rm은 삭제하는 다른 명령이에요.',
            docker_start='running', goal=dict(container='exited', same_container=True),
            commands=[('docker stop "$BOX"', '출력된 컨테이너 이름을 확인하세요.'),
                      ('docker ps -a', 'STATUS 열에서 Exited를 확인하세요.')],
            narration=[bash('docker stop "$BOX"', 'stop은 서버를 멈추고 컨테이너는 남겨요.'),
                       ('say', '멈춘 컨테이너의 이름이 출력됐어요.', TERMINAL),
                       bash('docker ps -a', '-a를 붙이면 멈춘 컨테이너도 표에 나와요.'),
                       ('say', 'STATUS가 Exited예요. 컨테이너는 지워지지 않고 남아 있어요.', TERMINAL),
                       ('say', '조심하세요. 멈추기와 삭제는 달라요. rm으로 지우면 다시 시작할 컨테이너도 없어져요.', 'text:rm은 삭제하는 다른 명령이에요.')],
            success='터미널에서 stop과 ps -a가 성공했고 같은 BOX 컨테이너가 exited 상태로 남아 있어요.',
            evidence='터미널의 실제 stop 출력과 ps -a 표, 같은 컨테이너 식별자',
            review={'조심하세요. 멈추기와 삭제는 달라요. rm으로 지우면 다시 시작할 컨테이너도 없어져요.': 'stop과 rm을 혼동하는 실수와 결과를 짚어요.'}),
        cli_step(slug='cli-start', opening='컨테이너는 만들어진 뒤 멈춰 있어요. 새로 만들지 않고 이 컨테이너를 켜요.',
            title='새로 만들지 말고 멈춘 컨테이너를 다시 켜세요',
            concept='start는 남아 있는 같은 컨테이너를 다시 시작해요.',
            start='앞 문제에서 멈춘 Nginx 컨테이너로 시작해요. 컨테이너가 없거나 실행 중이면 앱이 같은 이름으로 만들어 멈춰 둬요.',
            intro='멈춘 컨테이너를 새로 만들지 말고 다시 켜세요.',
            know='run은 새 컨테이너를 만들어요. start는 기존 컨테이너를 켜요. 채점은 실행 상태와 컨테이너 식별자를 함께 비교해요.',
            docker_start='stopped', goal=dict(container='running', same_container=True),
            commands=[('docker start "$BOX"', '출력된 컨테이너 이름을 확인하세요.'),
                      ('docker ps', 'STATUS 열에서 Up을 확인하세요.')],
            narration=[bash('docker start "$BOX"', 'start는 남아 있는 같은 컨테이너를 다시 시작해요.'),
                       ('say', '다시 시작한 컨테이너 이름이 출력됐어요.', TERMINAL),
                       bash('docker ps', 'ps로 다시 실행 중인지 볼게요.'),
                       ('say', 'STATUS가 Up으로 바뀌었어요. CONTAINER ID는 앞에서 본 것과 같아요.', TERMINAL),
                       ('say', '조심하세요. run은 같은 이미지를 써도 새 컨테이너를 만드는 명령이에요.', 'text:run은 새 컨테이너를 만들어요. start는 기존 컨테이너를 켜요.')],
            success='터미널에서 start와 ps가 성공했고 시작할 때와 같은 BOX 컨테이너가 실행 중이에요.',
            evidence='터미널의 실제 start 출력과 ps 표, 같은 컨테이너 식별자',
            review={'조심하세요. run은 같은 이미지를 써도 새 컨테이너를 만드는 명령이에요.': 'start 대신 run을 쓰면 다른 객체가 생긴다는 점을 짚어요.'}),
        cli_step(slug='cli-rm', opening='Nginx 컨테이너가 실행 중이에요. 이미지는 두고 이 컨테이너만 지워요.',
            title='컨테이너를 멈춘 뒤 삭제하고 이미지는 남기세요',
            concept='rm은 컨테이너를 지워요. 이미지는 따로 남아요.',
            start='앞 문제에서 다시 켠 Nginx 컨테이너가 실행 중이에요. 컨테이너가 없으면 앱이 같은 이름으로 하나 만들어 실행해 둬요.',
            intro='이 컨테이너만 지우고 이미지는 남기세요.',
            know='실행 중인 컨테이너는 rm으로 바로 지울 수 없어요. 먼저 멈춰요. rm은 삭제한 컨테이너 이름을 출력해요. 이미지까지 지우지는 않아요.',
            docker_start='running', goal=dict(container='absent', image_present=True),
            commands=[('docker stop "$BOX"', '출력된 컨테이너 이름을 확인하세요.'),
                      ('docker rm "$BOX"', '삭제한 컨테이너 이름을 확인하세요.'),
                      ('docker images', 'nginx 이미지가 남아 있는지 확인하세요.')],
            narration=[bash('docker rm "$BOX"', '실행 중인 컨테이너에 바로 rm을 입력해 볼게요.', fails=True),
                       ('say', '조심하세요. 실행 중이라서 지울 수 없다는 오류가 나요. 먼저 멈춰야 해요.', TERMINAL),
                       bash('docker stop "$BOX"', 'stop으로 먼저 멈춰요.'),
                       ('say', '멈춘 컨테이너 이름이 출력됐어요. 이제 지울 수 있어요.', TERMINAL),
                       bash('docker rm "$BOX"', 'rm은 컨테이너를 지워요. 이미지는 따로 남아요.'),
                       ('say', '삭제한 이름이 출력됐어요. 컨테이너 안에 쓴 메모도 함께 사라졌어요.', TERMINAL),
                       bash('docker images', 'images로 이미지가 남았는지 볼게요.'),
                       ('say', 'nginx 1.28-alpine 이미지는 그대로예요. 같은 이미지로 새 컨테이너를 만들 수 있어요.', 'text:이미지까지 지우지는 않아요.')],
            success='터미널에서 stop·rm·images가 성공했고 BOX 컨테이너는 없고 nginx:1.28-alpine 이미지는 남아 있어요.',
            evidence='터미널의 실제 rm 거절·삭제 출력과 images 표',
            review={'조심하세요. 실행 중이라서 지울 수 없다는 오류가 나요. 먼저 멈춰야 해요.': '실제로 rm이 거절되는 오류를 보여 준 뒤 stop으로 이어가요.'}),
    ]
    return dict(identity='cli-introduction', title='왜 Docker를 쓰고 어떻게 직접 실행할까요?',
        objectives=['컴퓨터마다 다른 설치·버전 문제와 이미지의 역할을 설명해요.',
            'Compose 전에 터미널에서 pull·run·ps·logs·exec·stop·start·rm을 직접 실행해요.'],
        units=[dict(title='이미지를 받고 컨테이너를 직접 다뤄요',
            objectives=['이미지·실행 상태·출력·컨테이너 수명을 명령별로 구별해요.'],
            premise='Nginx 이미지 하나로 시작해요. 터미널에 명령을 직접 입력하고 원래 출력을 읽어요. ' + ISOLATION, steps=steps)])
