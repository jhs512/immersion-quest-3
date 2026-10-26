"""Real Nginx CLI before Compose. Native output and grading are separate lanes."""
from common import START_NEW, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT

NGINX = 'nginx:1.28-alpine'
NGINX_PIN = NGINX + '@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236'

LAB = r'''set -eu
REAL_DOCKER=$(command -v docker)
IMAGE=nginx:1.28-alpine
BOX="${MQ3_PROJECT}-nginx"
OWNER="$MQ3_OWNER_LABEL"
MODE=__MODE__
TRACE="$PWD/.docker-calls"
: > "$TRACE"
state() {
  local value
  if value=$("$REAL_DOCKER" inspect -f '{{.State.Status}}' "$BOX" 2>/dev/null); then
    printf '%s' "$value"
  else
    printf '없음'
  fi
}
called() { grep -qx "$1" "$TRACE"; }
image_ready() { "$REAL_DOCKER" image inspect "$IMAGE" >/dev/null 2>&1; }
owned() {
  [ "$("$REAL_DOCKER" inspect -f '{{index .Config.Labels "io.mq3.project"}}' "$BOX" 2>/dev/null)" = "$MQ3_PROJECT" ]
}
docker() {
  local sub="$1" result=0
  shift
  case "$sub" in
    pull)
      [ "$#" = 1 ] && [ "$1" = "$IMAGE" ] || return 2
      "$REAL_DOCKER" pull "$@" || result=$? ;;
    run)
      # Learner-visible name and port; only the ownership label is added here.
      local args=("$@") name='' port='' image='' detached=0
      while [ "$#" -gt 0 ]; do
        case "$1" in
          -d|--detach) detached=1; shift ;;
          --name) [ "$#" -ge 2 ] && [ -z "$name" ] || return 2; name="$2"; shift 2 ;;
          --name=*) [ -z "$name" ] || return 2; name="${1#--name=}"; shift ;;
          -p|--publish) [ "$#" -ge 2 ] && [ -z "$port" ] || return 2; port="$2"; shift 2 ;;
          --publish=*) [ -z "$port" ] || return 2; port="${1#--publish=}"; shift ;;
          nginx:1.28-alpine) image="$1"; shift; [ "$#" = 0 ] || return 2 ;;
          *) return 2 ;;
        esac
      done
      [ "$detached" = 1 ] && [ "$name" = "$BOX" ] && [ "$port" = '127.0.0.1::80' ] && [ "$image" = "$IMAGE" ] || {
        echo '실습 이름과 127.0.0.1::80을 사용하세요. 호스트 포트는 Docker가 골라요.' >&2; return 2;
      }
      "$REAL_DOCKER" run --label "$OWNER" "${args[@]}" || result=$? ;;
    ps|images)
      # Read-only: show Docker's actual table, including unrelated containers.
      "$REAL_DOCKER" "$sub" "$@" || result=$? ;;
    port|logs|exec|stop|start|rm)
      if [ "$sub" != exec ]; then [ "$#" = 1 ] || return 2; fi
      [ "$#" -gt 0 ] && [ "$1" = "$BOX" ] && owned || {
        echo '이 실습에서 만든 컨테이너 이름을 사용하세요.' >&2; return 2;
      }
      "$REAL_DOCKER" "$sub" "$@" || result=$? ;;
    *) echo '이 단계에서는 안내한 Docker 명령을 사용하세요.' >&2; return 2 ;;
  esac
  if [ "$result" = 0 ]; then printf '%s\n' "$sub" >> "$TRACE"; fi
  return "$result"
}
# Prepare once per problem workspace. Checks/demonstrations use a separate workspace.
if [ ! -f .initialized ]; then
  if [ "$MODE" != pull ] && [ "$MODE" != run ]; then
    "$REAL_DOCKER" run -d --name "$BOX" --label "$OWNER" -p 127.0.0.1::80 "$IMAGE" >/dev/null
    ready=0
    for attempt in $(seq 1 50); do
      if "$REAL_DOCKER" exec "$BOX" wget -q -O /dev/null http://127.0.0.1 2>/dev/null; then ready=1; break; fi
      sleep 0.1
    done
    [ "$ready" = 1 ] || { echo 'Nginx 시작을 확인하지 못했어요.' >&2; exit 1; }
    if [ "$MODE" = start ] || [ "$MODE" = rm ]; then "$REAL_DOCKER" stop "$BOX" >/dev/null; fi
  fi
  touch .initialized
fi
BEFORE_ID=$("$REAL_DOCKER" inspect -f '{{.Id}}' "$BOX" 2>/dev/null || true)
export BOX
set +e
( source "$MQ3_ENTRY" ) > .learner.stdout 2> .learner.stderr
RESULT=$?
set -e
if [ "${MQ3_OUTPUT:-raw}" != grading ]; then
  cat .learner.stdout
  cat .learner.stderr >&2
  exit "$RESULT"
fi
cat .learner.stderr >&2
[ "$RESULT" = 0 ] || exit "$RESULT"
case "$MODE" in
  pull)
    if called pull && image_ready; then echo '이미지: 내려받기 확인'; else echo '이미지: pull 명령이 아직 없어요'; fi
    echo "컨테이너: $(state)" ;;
  run)
    echo "컨테이너: $(state)"
    current=$("$REAL_DOCKER" inspect -f '{{.Config.Image}}' "$BOX" 2>/dev/null || true)
    if called run && [ "$current" = "$IMAGE" ]; then echo '실행 환경: 지정한 이미지'; else echo '실행 환경: 확인 안 됨'; fi ;;
  ps)
    if called ps; then
      count=$("$REAL_DOCKER" ps -q --filter "label=$OWNER" | awk 'NF{n++} END{print n+0}')
      echo "실행 중인 실습 컨테이너: $count"
    else echo '실행 목록: ps 명령이 아직 없어요'; fi ;;
  logs)
    if called logs && [ -s .learner.stdout ]; then echo '시작 로그: 확인'; else echo '시작 로그: logs 명령이 아직 없어요'; fi ;;
  exec)
    text=$("$REAL_DOCKER" exec "$BOX" sh -c 'cat /memo.txt 2>/dev/null' || true)
    echo "컨테이너 안 메모: ${text:-(없음)}" ;;
  stop|start)
    echo "컨테이너: $(state)"
    current=$("$REAL_DOCKER" inspect -f '{{.Id}}' "$BOX" 2>/dev/null || true)
    if [ "$MODE" = stop ]; then
      if [ -n "$current" ] && [ "$current" = "$BEFORE_ID" ]; then echo '컨테이너 객체: 그대로'; else echo '컨테이너 객체: 없음'; fi
    else
      if [ -n "$current" ] && [ "$current" = "$BEFORE_ID" ]; then echo '식별자: 같은 컨테이너'; else echo '식별자: 달라짐'; fi
    fi ;;
  rm)
    echo "컨테이너: $(state)"
    if image_ready; then echo '이미지: 남아 있어요'; else echo '이미지: 없음'; fi ;;
esac
'''


def cli_step(*, mode, title, concept, intro, know, command, expected, result, caution):
    starter = '# BOX에는 이번 실습만의 고유한 컨테이너 이름을 담아요.\nBOX="${MQ3_PROJECT}-nginx"\n'
    solution = starter + '# 아래 명령을 실행하고 실제 Docker 출력을 읽어요.\n' + command + '\n'
    first = dict(pull='아직 내려받는 명령을 쓰지 않아서 진행 출력도 없어요.',
        run='이름만 정해 둔 상태예요. 서버를 실행할 명령을 더해 볼게요.',
        ps='서버는 준비돼 있지만 목록을 조회하지 않아서 표가 없어요.',
        logs='로그를 요청하기 전이라 실행 결과는 비어 있어요.',
        exec='이름 변수만으로는 파일이 생기지 않아요. 컨테이너에 명령을 보내 볼게요.',
        stop='아직 멈추라는 명령을 보내지 않았어요. 서버는 실행 중이에요.',
        start='준비된 컨테이너는 멈춰 있어요. 이름을 정하는 것만으로 켜지지는 않아요.',
        rm='삭제 명령이 없어서 컨테이너는 아직 남아 있어요.')[mode]
    return dict(slug=f'cli-{mode}', title=title, language='docker', docker_images=[NGINX_PIN],
        entry_file='commands.sh', files={'lab.sh': LAB.replace('__MODE__', mode)},
        start=START_NEW, objectives=[concept], intro=[intro], know=know,
        todo=[TODO_RUN_BEFORE, f'commands.sh에 다음 명령을 쓰세요. `{command}`', TODO_RUN_AFTER, TODO_SUBMIT],
        starter=starter, solution=solution, tests=[('', expected)], success=expected,
        complexity=dict(prior='터미널에서 명령을 실행해 봤어요.', new=concept,
            changed=title, evidence='Docker 원본 출력과 실제 엔진 상태', lines=1, services=1 if mode=='run' else 0),
        narration=[('say', intro, 'text:'+intro), ('run',),
            ('say', first, 'output'),
            ('patch', starter, solution, title), ('say', concept, 'code:'+command), ('run',),
            ('say', result, 'output'), ('say', caution, 'text:'+know), ('submit',)],
        review={intro:'문제별로 준비된 상태를 먼저 설명해요.',
            first:'이름 변수만 설정한 시작 코드의 출력과 준비된 서버 상태를 구별해요.',
            concept:'실행할 명령의 역할을 설명해요.', title:'직접 실행할 명령을 추가해요.',
            result:'컨테이너 ID·시각·포트는 고정하지 않고 실제 출력의 열을 읽어요.',
            caution:'현재 명령에서 생길 수 있는 오해를 짚어요.'},
        rejects=[([(command, 'true')], '명령을 생략하면 실제 엔진 상태·호출 검사를 통과하지 못해요.')])


def chapter(_image):
    isolation = 'BOX는 이번 실습의 고유한 이름이에요. 다른 컨테이너 이름과 겹치지 않아요. 처음 제공한 상태는 코드 실행을 반복해도 유지돼요. 다시 시작하려면 초기화를 누르세요. 수업을 나가면 MQ가 만든 자원만 정리해요.'
    steps = [
        cli_step(mode='pull', title='실행하기 전에 이미지를 내려받으세요',
            concept='이미지는 프로그램과 실행에 필요한 파일을 묶은 재료예요.',
            intro='Nginx는 웹 페이지를 보내 주는 서버예요. 직접 설치하면 컴퓨터마다 설치 과정이 달라져요. 같은 버전의 이미지로 실행 재료를 맞춰 보세요.',
            know='nginx:1.28-alpine에서 콜론 뒤는 이미지의 태그예요. pull은 이미지를 받아요. 서버를 실행하지는 않아요. 앱이 이미지를 미리 받아 두었어도 pull 결과를 확인할 수 있어요. '+isolation,
            command='docker pull nginx:1.28-alpine', expected='이미지: 내려받기 확인\n컨테이너: 없음',
            result='내려받은 레이어와 이미지 상태가 표시돼요. 이미 받아 뒀다면 최신 상태라는 안내가 나와요.',
            caution='조심하세요. 이미지가 있어도 웹 서버가 켜진 것은 아니에요.'),
        cli_step(mode='run', title='이미지로 컨테이너 하나를 실행하세요',
            concept='run은 이미지에서 새 컨테이너를 만들고 서버를 시작해요.',
            intro='Nginx 이미지는 준비됐어요. 이제 그 이미지로 웹 서버를 실행하세요.',
            know='-d는 서버를 뒤에서 실행해요. --name은 이름을 붙여요. -p 127.0.0.1::80은 컨테이너의 80번 포트를 연결해요. 가운데가 비어 있어 호스트의 빈 포트를 Docker가 골라요. docker ps의 PORTS에서 배정된 포트를 읽을 수 있어요. '+isolation,
            command='docker run -d --name "$BOX" -p 127.0.0.1::80 nginx:1.28-alpine',
            expected='컨테이너: running\n실행 환경: 지정한 이미지',
            result='긴 컨테이너 ID가 출력됐어요. Nginx의 기본 실행 명령으로 서버가 시작돼요.',
            caution='조심하세요. run을 또 실행하면 같은 이름이 있어 실패해요. 기존 컨테이너를 다시 켜는 명령은 뒤에서 배워요.'),
        cli_step(mode='ps', title='이미지 목록 대신 실행 중인 컨테이너를 조회하세요',
            concept='ps는 실행 중인 컨테이너를 표로 보여 줘요.',
            intro='이번 문제는 준비된 Nginx 서버 하나에서 시작해요. 실행 중인 컨테이너의 이름과 포트를 찾아보세요.',
            know='docker images는 이미지를 보여 줘요. docker ps는 실행 중인 컨테이너를 보여 줘요. IMAGE·STATUS·PORTS·NAMES 열을 읽으세요. 원래 켜 두었던 컨테이너도 나올 수 있어요. BOX의 이름으로 이번 실습을 구별하세요. 조회만으로 다른 컨테이너가 바뀌지는 않아요.',
            command='docker ps', expected='실행 중인 실습 컨테이너: 1',
            result='표의 NAMES에서 실습 이름을 찾으세요. PORTS의 화살표 왼쪽은 이 컴퓨터의 포트예요. 오른쪽 80은 컨테이너의 포트예요.',
            caution='조심하세요. 이미지를 받기만 했다면 ps 목록에는 새 컨테이너가 없어요.'),
        cli_step(mode='logs', title='컨테이너가 시작할 때 남긴 로그를 읽으세요',
            concept='logs는 컨테이너의 주 프로세스가 남긴 출력을 읽어요.',
            intro='이번 문제는 Nginx가 실행된 상태예요. 서버가 시작하며 남긴 로그를 직접 읽으세요.',
            know='ps는 상태를 보여 줘요. logs는 실행 중에 기록한 출력을 보여 줘요. 준비 과정에서 웹 요청 하나도 보냈어요. 시작 안내와 요청 기록을 비교해 보세요.',
            command='docker logs "$BOX"', expected='시작 로그: 확인',
            result='Nginx의 시작 안내와 요청 기록이 보여요. 시각과 프로세스 번호는 실행마다 달라질 수 있어요.',
            caution='조심하세요. logs가 비었다고 멈춘 것은 아니에요. 출력하지 않는 프로그램도 있어요.'),
        cli_step(mode='exec', title='실행 중인 컨테이너 안에 메모를 쓰세요',
            concept='exec는 실행 중인 컨테이너 안에서 명령을 더 실행해요.',
            intro='Nginx가 실행 중이고 /memo.txt는 없어요. 같은 컨테이너 안에 메모를 쓰고 읽으세요.',
            know='run은 새 컨테이너를 만들어요. exec는 기존 컨테이너에 명령을 보내요. sh -c 뒤의 명령은 컨테이너 안에서 실행돼요. echo로 쓰고 cat으로 읽어요.',
            command='docker exec "$BOX" sh -c \'echo hello > /memo.txt; cat /memo.txt\'',
            expected='컨테이너 안 메모: hello', result='cat이 읽은 hello가 그대로 출력돼요. 같은 컨테이너 안에서 명령을 실행했어요.',
            caution='조심하세요. 이 파일은 내 컴퓨터의 /memo.txt가 아니에요. 컨테이너 안에 있어요.'),
        cli_step(mode='stop', title='컨테이너를 삭제하지 않고 멈추세요',
            concept='stop은 서버를 멈추고 컨테이너는 남겨요.',
            intro='이번 문제는 Nginx가 실행 중이에요. 컨테이너를 지우지 말고 서버만 멈추세요.',
            know='stop은 대상 컨테이너 이름을 출력해요. 멈춘 컨테이너는 docker ps -a로 확인할 수 있어요. rm은 삭제하는 다른 명령이에요.',
            command='docker stop "$BOX"', expected='컨테이너: exited\n컨테이너 객체: 그대로',
            result='멈춘 컨테이너의 이름이 출력됐어요. 객체는 남아 있어서 다시 시작할 수 있어요.',
            caution='조심하세요. 멈추기와 삭제는 달라요. rm으로 지우면 다시 시작할 객체도 없어져요.'),
        cli_step(mode='start', title='새로 만들지 말고 멈춘 컨테이너를 다시 켜세요',
            concept='start는 남아 있는 같은 컨테이너를 다시 시작해요.',
            intro='이번 문제는 Nginx 컨테이너를 만든 뒤 멈춘 상태예요. 같은 컨테이너를 다시 켜세요.',
            know='run은 새 컨테이너를 만들어요. start는 기존 컨테이너를 켜요. 채점은 실행 상태와 식별자를 함께 비교해요.',
            command='docker start "$BOX"', expected='컨테이너: running\n식별자: 같은 컨테이너',
            result='다시 시작한 컨테이너 이름이 출력됐어요. 새 객체를 만들지 않았어요.',
            caution='조심하세요. run은 같은 이미지를 써도 새 컨테이너를 만드는 명령이에요.'),
        cli_step(mode='rm', title='멈춘 컨테이너만 삭제하고 이미지는 남기세요',
            concept='rm은 컨테이너를 지워요. 이미지는 따로 남아요.',
            intro='이번 문제는 Nginx 컨테이너를 멈춘 상태예요. 이 컨테이너만 삭제하세요.',
            know='rm은 삭제한 컨테이너 이름을 출력해요. 이미지까지 지우지는 않아요. 같은 이미지로 새 컨테이너를 만들 수 있어요.',
            command='docker rm "$BOX"', expected='컨테이너: 없음\n이미지: 남아 있어요',
            result='삭제한 이름이 출력됐어요. Nginx 이미지는 그대로 남아 있어요.',
            caution='조심하세요. 컨테이너 안에 새로 쓴 파일도 함께 사라져요. 다음에는 데이터를 남기는 방법을 배워요.'),
    ]
    return dict(identity='cli-introduction', title='왜 Docker를 쓰고 어떻게 직접 실행할까요?',
        objectives=['컴퓨터마다 다른 설치·버전 문제와 이미지의 역할을 설명해요.',
            'Compose 전에 pull·run·ps·logs·exec·stop·start·rm을 실제로 실행해요.'],
        units=[dict(title='이미지를 받고 컨테이너를 직접 다뤄요',
            objectives=['이미지·실행 상태·출력·컨테이너 수명을 명령별로 구별해요.'],
            premise='Nginx 이미지 하나로 시작해요. 명령의 원래 출력을 읽어요. '+isolation, steps=steps)])
