"""Beginner Docker CLI experiments, before the existing Compose exercises.

The supplied shell adapter adds only the run's name/ownership label and scopes ps.
Every Docker operation delegates to the real binary; observations inspect that engine.
"""
from common import START_NEW, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT


LAB = r'''# 준비 스크립트: 실제 Docker 명령에 이 실습의 이름·소유 라벨만 더해요.
set -eu
REAL_DOCKER=$(command -v docker)
IMAGE=__IMAGE__
BOX="${MQ3_PROJECT}-intro"
OWNER="$MQ3_OWNER_LABEL"
MESSAGE=$(cat message.txt)
TRACE="$PWD/.docker-calls"
: > "$TRACE"
# 이 문제의 컨테이너 하나만 되돌려요. 다른 수업·사용자의 컨테이너는 건드리지 않아요.
"$REAL_DOCKER" rm -f "$BOX" >/dev/null 2>&1 || true
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
docker() {
  local sub="$1" result=0
  shift
  case "$sub" in
    pull)
      [ "$#" = 1 ] && [ "$1" = "$IMAGE" ] || return 2
      "$REAL_DOCKER" pull "$@" || result=$? ;;
    run)
      # 이름과 소유 라벨은 준비 스크립트가 더해요. 실행할 이미지·명령은 학습자가 써요.
      "$REAL_DOCKER" run --name "$BOX" --label "$OWNER" "$@" || result=$? ;;
    ps)
      "$REAL_DOCKER" ps --filter "label=$OWNER" "$@" || result=$? ;;
    images)
      "$REAL_DOCKER" images "$IMAGE" "$@" || result=$? ;;
    logs|exec|stop|start|rm)
      [ "$#" -gt 0 ] && [ "$1" = "$BOX" ] || return 2
      if [ "$sub" = stop ]; then
        "$REAL_DOCKER" stop -t 1 "$@" || result=$?
      else
        "$REAL_DOCKER" "$sub" "$@" || result=$?
      fi ;;
    *) return 2 ;;
  esac
  if [ "$result" = 0 ]; then printf '%s\n' "$sub" >> "$TRACE"; fi
  return "$result"
}
MODE=__MODE__
if [ "$MODE" != pull ] && [ "$MODE" != run ]; then
  "$REAL_DOCKER" run -d --name "$BOX" --label "$OWNER" "$IMAGE" sh -c 'echo "$1"; exec sleep 600' sh "$MESSAGE" >/dev/null
  # 로그를 쓰기 전후의 경합을 성공 조건으로 삼지 않아요.
  for attempt in 1 2 3 4 5 6 7 8 9 10; do
    [ -n "$("$REAL_DOCKER" logs "$BOX" 2>/dev/null)" ] && break
    sleep 0.1
  done
fi
BEFORE_ID=$("$REAL_DOCKER" inspect -f '{{.Id}}' "$BOX" 2>/dev/null || true)
if [ "$MODE" = start ]; then "$REAL_DOCKER" stop -t 0 "$BOX" >/dev/null; fi
if [ "$MODE" = rm ]; then "$REAL_DOCKER" stop -t 0 "$BOX" >/dev/null; fi
export IMAGE BOX OWNER MESSAGE
# 편집한 명령의 stdout은 관찰 자료예요. 채점은 출력 흉내가 아닌 실제 엔진 상태를 읽어요.
set +e
source "$MQ3_ENTRY" > .learner.stdout 2> .learner.stderr
RESULT=$?
set -e
case "$MODE" in
  pull)
    if called pull && image_ready; then echo '이미지: 내려받기 확인'; else echo '이미지: pull 명령이 아직 없어요'; fi
    echo "컨테이너: $(state)" ;;
  run)
    echo "컨테이너: $(state)"
    current=$("$REAL_DOCKER" inspect -f '{{.Config.Image}}' "$BOX" 2>/dev/null || true)
    if [ "$current" = "$IMAGE" ]; then echo '실행 환경: 지정한 이미지'; else echo '실행 환경: 확인 안 됨'; fi ;;
  ps)
    if called ps; then
      count=$("$REAL_DOCKER" ps -q --filter "label=$OWNER" | awk 'NF{n++} END{print n+0}')
      echo "실행 중인 실습 컨테이너: $count"
    else echo '실행 목록: ps 명령이 아직 없어요'; fi ;;
  logs)
    if called logs; then
      echo "시작 로그: $("$REAL_DOCKER" logs "$BOX" 2>/dev/null)"
    else echo '시작 로그: logs 명령이 아직 없어요'; fi ;;
  exec)
    text=$("$REAL_DOCKER" exec "$BOX" sh -c 'cat /memo.txt 2>/dev/null' || true)
    echo "컨테이너 안 메모: ${text:-(없음)}" ;;
  stop)
    echo "컨테이너: $(state)"
    current=$("$REAL_DOCKER" inspect -f '{{.Id}}' "$BOX" 2>/dev/null || true)
    if [ -n "$current" ] && [ "$current" = "$BEFORE_ID" ]; then echo '컨테이너 객체: 그대로'; else echo '컨테이너 객체: 없음'; fi ;;
  start)
    echo "컨테이너: $(state)"
    current=$("$REAL_DOCKER" inspect -f '{{.Id}}' "$BOX" 2>/dev/null || true)
    if [ -n "$current" ] && [ "$current" = "$BEFORE_ID" ]; then echo '식별자: 같은 컨테이너'; else echo '식별자: 달라짐'; fi ;;
  rm)
    echo "컨테이너: $(state)"
    if image_ready; then echo '이미지: 남아 있어요'; else echo '이미지: 없음'; fi ;;
esac
'''


def cli_step(image, *, mode, title, concept, intro, know, command, expected,
             first, result, caution, starter_command='', variations=None):
    starter = '# 제공된 IMAGE·BOX는 이 문제의 이미지와 컨테이너예요.\n' + starter_command
    solution = starter + '# 이번 목표에 맞는 Docker 명령을 실행해요.\n' + command + '\n'
    script = LAB.replace('__IMAGE__', image).replace('__MODE__', mode)
    # 상황에 필요한 상태는 준비 스크립트가 만들었다고 본문에 먼저 명시해요.
    return dict(slug=f'cli-{mode}', title=title, language='docker', docker_images=[image],
        entry_file='commands.sh', files={'lab.sh': script, 'message.txt': '메모 서버 시작'},
        start=START_NEW, objectives=[concept], intro=[intro], know=know,
        todo=[TODO_RUN_BEFORE, f'commands.sh에 다음 명령을 쓰세요. `{command}`', TODO_RUN_AFTER, TODO_SUBMIT],
        starter=starter, solution=solution, tests=[('', expected)], success=expected,
        variations=variations or [],
        complexity=dict(prior='앞에서 본 명령의 결과를 읽을 수 있어요.' if mode != 'pull' else '터미널에서 명령을 실행해 봤어요.',
            new=concept, changed=title, evidence='실제 Docker 명령 호출과 엔진에서 읽은 상태', lines=1, services=1 if mode=='run' else 0),
        narration=[('say', intro, 'text:'+intro), ('run',), ('say', first, 'output'),
            ('patch', starter, solution, title), ('say', concept, 'code:'+command), ('run',),
            ('say', result, 'output'), ('say', caution, 'text:'+know), ('submit',)],
        review={intro:'시작 상태와 준비한 범위를 먼저 밝혀요.', first:'명령을 쓰기 전 엔진 관찰 결과예요.',
            concept:'실제로 고를 명령과 새 개념을 연결해요.', title:'한 명령을 추가해 상태를 바꾸는 목표예요.',
            result:'실제 호출 기록과 엔진 상태를 함께 읽어요.', caution:'이 명령에서 생길 수 있는 구체적인 오해를 짚어요.'},
        rejects=[([(command, 'true')], '출력만 흉내 내거나 명령을 생략하면 엔진 상태·호출 검사를 만족하지 못해요.')])


def chapter(image):
    isolation = '이 실습은 이름과 소유 라벨을 준비 스크립트가 더해요. IMAGE는 실행 환경, BOX는 이 문제의 컨테이너예요. 표시한 Docker 명령은 실제 엔진에서 실행해요. 다른 컨테이너는 건드리지 않아요. 이 챕터는 명령 하나의 차이를 비교하는 독립 실험이에요. 실행 버튼을 다시 누르면 이 문제의 컨테이너만 준비 상태로 되돌려요. 앞 실행에서 쓴 메모를 이어 쓰는 수업은 아니에요. 뒤의 DB 수업이 실행마다 초기화된다는 뜻도 아니에요.'
    steps = [
        cli_step(image, mode='pull', title='실행하기 전에 이미지를 내려받으세요',
            concept='이미지는 프로그램과 필요한 사용자 공간 파일을 묶은 실행 재료예요.',
            intro='내 컴퓨터에는 도구가 있는데 동료 컴퓨터에는 없을 수 있어요. 버전도 다를 수 있죠. 설치 순서를 말로만 전달하면 빠뜨리기 쉬워요. 같은 이미지에서 시작하면 그 이미지에 담긴 도구와 파일을 함께 가져올 수 있어요.',
            know='Docker를 쓰지 않아도 설치·버전을 맞춰 실행할 수 있어요. 하지만 컴퓨터마다 반복해서 맞춰야 하죠. 이미지는 그 실행 재료를 묶어요. pull은 레지스트리에서 이미지를 받아요. 아직 프로그램을 실행하지는 않아요. '+isolation+' 이 앱이 실행 준비로 이미지를 미리 받아 두었을 수 있어요. 그래도 여러분의 pull 명령을 실제 실행해 확인해요.',
            command='docker pull "$IMAGE"', expected='이미지: 내려받기 확인\n컨테이너: 없음',
            first='아직 pull 명령을 쓰지 않았어요. 컨테이너도 없어요.',
            result='실제 pull이 끝났어요. 이미지는 있지만 컨테이너는 없어요.',
            caution='조심하세요. 이미지를 받았다고 서버가 켜진 것은 아니에요. 실행은 다음 run에서 해요.'),
        cli_step(image, mode='run', title='이미지로 컨테이너 하나를 실행하세요',
            concept='run은 이미지에서 새 컨테이너를 만들고 그 안의 프로세스를 시작해요.',
            intro='이미지는 준비됐지만 실행 중인 프로그램은 없어요. 같은 도구가 담긴 이미지로 작은 프로세스를 시작해 보세요.',
            know='컨테이너는 이미지에서 만든 실행 단위예요. run 뒤에는 이미지와 실행할 명령을 써요. -d는 화면을 붙잡지 않고 실행해요. sleep은 잠시 기다리는 작은 프로그램이에요. '+isolation+' 이미지가 같아도 CPU 구조·커널·외부 서비스까지 모두 같아지는 것은 아니에요.',
            command='docker run -d "$IMAGE" sleep 600', expected='컨테이너: running\n실행 환경: 지정한 이미지',
            first='아직 컨테이너가 없어서 실행 환경도 확인되지 않아요.',
            result='지정한 이미지에서 컨테이너가 생겼어요. 그 안의 sleep이 실행 중이에요.',
            caution='조심하세요. 컨테이너는 별도의 운영체제를 통째로 부팅하는 가상머신과 달라요. 여기서는 프로세스 하나를 실행했어요.'),
        cli_step(image, mode='ps', title='이미지 목록 대신 실행 중인 컨테이너를 조회하세요',
            concept='이미지 목록과 실행 중인 컨테이너 목록은 다른 대상을 보여 줘요.',
            intro='준비 스크립트가 컨테이너 하나를 켜 두었어요. 이미지가 있다는 사실과 실행 중이라는 사실을 구별해 보세요.',
            know='docker images는 실행 재료를 보여 줘요. docker ps는 실행 중인 컨테이너를 보여 줘요. ps -a는 멈춘 컨테이너도 보여 줘요. 이 실습의 ps에는 소유 라벨 필터가 자동으로 붙어요.',
            command='docker ps', expected='실행 중인 실습 컨테이너: 1',
            first='아직 ps로 컨테이너 목록을 요청하지 않았어요.',
            result='실습 소유 컨테이너 한 개가 실행 중이에요. 이미지를 받기만 한 상태와 달라요.',
            caution='조심하세요. images에 이미지가 보여도 ps에 실행 중인 컨테이너가 있다는 뜻은 아니에요.'),
        cli_step(image, mode='logs', title='컨테이너가 시작할 때 남긴 로그를 읽으세요',
            concept='logs는 컨테이너의 주 프로세스가 남긴 표준 출력을 읽어요.',
            intro='준비 스크립트가 시작 메시지를 찍는 컨테이너를 켰어요. 실행 중이라는 것만으로 그 메시지까지 읽은 것은 아니에요.',
            know='ps는 상태를 보여 줘요. logs는 주 프로세스의 출력 기록을 보여 줘요. BOX에는 이 문제의 컨테이너 이름이 있어요. 메시지는 message.txt에서 준비했어요.',
            command='docker logs "$BOX"', expected='시작 로그: 메모 서버 시작',
            first='아직 logs로 시작 메시지를 읽지 않았어요.', result='컨테이너가 시작하면서 남긴 메모 서버 시작 메시지를 읽었어요.',
            caution='조심하세요. logs가 비어 있다고 프로세스가 멈춘 것은 아니에요. 출력하지 않는 프로그램도 있어요.',
            variations=[dict(files={'message.txt':'다른 시작 메시지'}, expected='시작 로그: 다른 시작 메시지')]),
        cli_step(image, mode='exec', title='실행 중인 컨테이너 안에 메모를 쓰세요',
            concept='exec는 이미 실행 중인 컨테이너 안에서 명령을 하나 더 실행해요.',
            intro='준비 스크립트가 컨테이너 하나를 켰어요. 그 안에는 아직 /memo.txt가 없어요. 새 컨테이너를 만들지 않고 파일을 써 보세요.',
            know='run은 새 컨테이너를 만들어요. exec는 기존 컨테이너를 대상으로 해요. sh -c 뒤의 글자는 컨테이너 안 셸이 실행해요. MESSAGE의 글자는 sh의 첫 인수로 전달해요.',
            command='docker exec "$BOX" sh -c \'echo "$1" > /memo.txt\' sh "$MESSAGE"',
            expected='컨테이너 안 메모: 메모 서버 시작', first='컨테이너는 있지만 그 안의 메모 파일은 아직 없어요.',
            result='실행 중인 같은 컨테이너 안에 메모 파일이 생겼어요.',
            caution='조심하세요. 이 파일은 컨테이너 안에 있어요. 컨테이너를 지워도 남을지는 뒤에서 따로 확인해요.',
            variations=[dict(files={'message.txt':'새 메모'}, expected='컨테이너 안 메모: 새 메모')]),
        cli_step(image, mode='stop', title='컨테이너를 삭제하지 않고 멈추세요',
            concept='stop은 프로세스를 멈추고 컨테이너 객체는 남겨요.',
            intro='준비 스크립트가 컨테이너를 켰어요. 이번에는 새것으로 바꾸지 않고 멈추기만 해야 해요.',
            know='stop 뒤에는 멈출 컨테이너를 써요. 멈춘 상태는 exited예요. rm은 객체를 지우는 다른 명령이에요. 여기서는 이 실습의 BOX만 다뤄요.',
            command='docker stop "$BOX"', expected='컨테이너: exited\n컨테이너 객체: 그대로',
            first='아직 컨테이너가 running이에요. 같은 객체가 남아 있어요.', result='프로세스는 멈췄지만 같은 컨테이너 객체가 남았어요.',
            caution='조심하세요. 멈추기와 삭제는 달라요. rm으로 지우면 start할 그 객체도 없어져요.'),
        cli_step(image, mode='start', title='새로 만들지 말고 멈춘 컨테이너를 다시 켜세요',
            concept='start는 남아 있는 같은 컨테이너의 주 프로세스를 다시 시작해요.',
            intro='준비 스크립트가 컨테이너를 만든 뒤 멈춰 두었어요. 이번에는 그 컨테이너를 다시 켜야 해요.',
            know='run은 새 컨테이너를 만들어요. start는 기존 컨테이너를 다시 켜요. 실습 스크립트가 전후의 식별자도 비교해요. 상태만 running인 새 객체로 바꾸면 통과하지 못해요.',
            command='docker start "$BOX"', expected='컨테이너: running\n식별자: 같은 컨테이너',
            first='컨테이너는 exited예요. 객체는 그대로 남아 있어요.', result='다시 running이고 식별자도 같아요. 새로 만들지 않았어요.',
            caution='조심하세요. run과 start는 바꿔 쓸 수 없어요. run은 같은 이미지여도 새 객체를 만들어요.'),
        cli_step(image, mode='rm', title='멈춘 컨테이너만 삭제하고 이미지는 남기세요',
            concept='rm은 컨테이너를 지워요. 그 컨테이너의 이미지는 따로 남아요.',
            intro='준비 스크립트가 컨테이너를 만든 뒤 멈췄어요. 이제 그 객체를 지우고 실행 재료는 남겨 보세요.',
            know='stop으로 멈춘 객체는 ps -a나 inspect로 찾을 수 있어요. rm으로 지우면 그 객체는 없어져요. 이미지는 컨테이너와 별개예요. 새 run은 그 이미지로 다시 시작할 수 있어요.',
            command='docker rm "$BOX"', expected='컨테이너: 없음\n이미지: 남아 있어요',
            first='컨테이너는 멈췄지만 아직 있어요. 이미지도 남아 있어요.', result='컨테이너 객체는 없어졌어요. 이미지는 남아 있어요.',
            caution='조심하세요. rm은 그 컨테이너 안에서 새로 만든 파일도 없애요. 데이터 보존은 다음 챕터에서 다뤄요.'),
    ]
    return dict(identity='cli-introduction', title='왜 Docker를 쓰고 어떻게 직접 실행할까요?',
        objectives=['컴퓨터마다 다른 설치·버전 문제와 이미지의 역할을 설명해요.',
            'Compose 전에 pull·run·ps·logs·exec·stop·start·rm을 실제로 실행해요.'],
        units=[dict(title='이미지를 받고 컨테이너를 직접 다뤄요',
            objectives=['실행 재료·실행 상태·출력·컨테이너 수명을 명령별로 구별해요.'],
            premise='별도 서버나 DB 없이 이미지 하나로 시작해요. 이 챕터의 명령 비교 실험은 실행할 때마다 이 문제 컨테이너만 준비 상태로 되돌려요. 실행 전후를 같은 조건에서 비교하기 위해서예요. DB 수업의 데이터나 다른 컨테이너는 초기화하지 않아요. 이름·소유 라벨·정지 대기 시간만 준비 스크립트가 관리해요. Docker 명령 자체는 실제 엔진에서 실행해요.', steps=steps)])
