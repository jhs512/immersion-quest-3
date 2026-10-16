"""Independent, exercise-first Java lessons. Never rewrites the original course."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'target/principles-course'
SOURCE = ROOT / 'tools/principles_course'


def activity(id, title, explanation, instruction, lines, before, after, expected, caution):
    starter = 'void main() {\n' + ''.join('    ' + line + '\n' for line in lines) + '}\n'
    assert starter.count(before) == 1, id
    solution = starter.replace(before, after, 1)
    return dict(id=id, title=title, language='java', entry_file='Main.java',
                goal=f'{explanation}\n\n**먼저 실행해 보세요.**\n\n{instruction}\n\n통과할 출력이에요.\n```text\n{expected}\n```',
                starter_code=starter, solution=solution, tests=[dict(input='', expected=expected)],
                required=True, narration=[], edit=dict(before=before, after=after), caution=caution)


def build():
    tasks = [
        activity('change-text', '따옴표 안의 글자',
                 '`println`은 괄호 안의 값을 화면에 보여 줘요.\n따옴표는 글자의 시작과 끝을 알려 줘요.',
                 '`"처음"`만 `"시작!"`으로 바꿔 보세요.\n바깥의 준비 코드는 그대로 둬도 돼요.',
                 ['// 따옴표 안의 글자만 바꿔 보세요.', 'System.out.println("처음");'],
                 '"처음"', '"시작!"', '시작!', '조심하세요. 따옴표까지 지우면 글자로 읽지 못해요.'),
        activity('line-break', '줄은 언제 바뀔까요?',
                 '`print`는 값을 보여 줘요.\n`println`은 보여 준 뒤 줄도 바꿔요.',
                 '첫 줄의 `print`를 `println`으로 바꾸세요.\n두 번째 글자가 어디에 나타나는지 비교해요.',
                 ['// 첫 출력 뒤에 줄을 바꿔 보세요.', 'System.out.print("위");',
                  '// 이 줄의 글자는 그대로 둬요.', 'System.out.println("아래");'],
                 'print("위")', 'println("위")', '위\n아래', '조심하세요. print와 println은 줄을 바꾸는 때가 달라요.'),
        activity('execution-order', '코드는 위에서 아래로',
                 '화면에 나오는 순서는 코드의 순서를 따라요.',
                 '두 출력 줄의 순서를 바꾸세요.\n글자는 바꾸지 말고 줄만 옮겨 보세요.',
                 ['// 두 줄의 순서만 바꿔 보세요.', 'System.out.println("완료");', 'System.out.println("준비");'],
                 'System.out.println("완료");\n    System.out.println("준비");',
                 'System.out.println("준비");\n    System.out.println("완료");',
                 '준비\n완료', '조심하세요. 화면의 위치보다 코드의 실행 순서가 먼저예요.'),
        activity('text-or-sum', '글자와 계산의 차이',
                 '따옴표 안은 글자 그대로 보여 줘요.\n따옴표 밖의 숫자는 계산할 수 있어요.',
                 '`"6 + 4"`의 따옴표 두 개만 지우세요.\n계산식이었던 글자가 어떻게 달라질까요?',
                 ['// 같은 기호도 따옴표에 따라 다르게 읽어요.', 'System.out.println("6 + 4");'],
                 '"6 + 4"', '6 + 4', '10', '조심하세요. 따옴표 안의 더하기는 계산하지 않아요.'),
        activity('join-text', '숫자를 글자로 붙이면',
                 '글자에 `+`를 쓰면 옆에 이어 붙여요.\n숫자의 더하기와 결과를 비교해요.',
                 '두 숫자에 따옴표를 붙여 보세요.\n`6 + 4`를 `"6" + "4"`로 바꾸면 돼요.',
                 ['// 숫자 두 개를 글자 두 개로 바꿔요.', 'System.out.println(6 + 4);'],
                 '6 + 4', '"6" + "4"', '64', '조심하세요. 글자를 붙이는 것과 숫자를 더하는 것은 달라요.'),
        activity('left-to-right', '더하기는 왼쪽부터',
                 '`+`가 이어지면 왼쪽부터 처리해요.\n먼저 글자가 나오면 뒤의 숫자도 붙어요.',
                 '`1 + 2 + "점"`을 `"점" + 1 + 2`로 바꾸세요.\n숫자 둘이 더해지는지 관찰해요.',
                 ['// 글자를 앞에 두고 결과를 비교해요.', 'System.out.println(1 + 2 + "점");'],
                 '1 + 2 + "점"', '"점" + 1 + 2', '점12', '조심하세요. 글자에 붙기 시작하면 뒤의 숫자도 이어져요.'),
        activity('group-sum', '괄호로 계산을 먼저',
                 '괄호 안의 식을 먼저 계산해요.\n글자에 붙이기 전에 숫자를 더할 수 있어요.',
                 '`1 + 2`를 괄호로 묶어 보세요.\n다른 글자는 그대로 두세요.',
                 ['// 숫자를 먼저 더하도록 괄호를 넣어요.', 'System.out.println("합: " + 1 + 2);'],
                 '"합: " + 1 + 2', '"합: " + (1 + 2)', '합: 3', '조심하세요. 화면에 붙일 괄호는 따옴표 안에 넣지 않아요.'),
        activity('precedence', '곱하기와 괄호',
                 '곱하기는 더하기보다 먼저 계산해요.\n괄호를 쓰면 더하기를 먼저 할 수 있어요.',
                 '`2 + 3`에만 괄호를 붙여 보세요.\n계산 순서를 바꾸면 값도 바뀌죠?',
                 ['// 더하기를 먼저 하도록 묶어요.', 'System.out.println(2 + 3 * 4);'],
                 '2 + 3 * 4', '(2 + 3) * 4', '20', '조심하세요. 숫자를 그대로 둬도 괄호가 결과를 바꿔요.'),
        activity('division', '나누었는데 소수가 없어요',
                 '정수끼리 나누면 몫의 정수 부분만 남아요.\n한쪽을 소수로 쓰면 소수로 계산해요.',
                 '`7`을 `7.0`으로만 바꿔 보세요.\n실행 전과 후의 출력을 비교해요.',
                 ['// 나누기 전부터 소수로 계산하게 해요.', 'System.out.println(7 / 2);'],
                 '7 / 2', '7.0 / 2', '3.5', '조심하세요. 정수 나눗셈은 반올림하는 계산이 아니에요.'),
        activity('transfer', '글자와 계산을 함께',
                 '글자는 그대로 두고 식의 순서를 바꿔 봐요.\n앞에서 확인한 괄호의 역할을 써먹어요.',
                 '`"결과: " + 8 - 3`을 실행해 보세요.\n`8 - 3`만 괄호로 묶어 오류를 고치세요.',
                 ['// 글자에서 숫자를 뺄 수는 없어요.', 'System.out.println("결과: " + 8 - 3);'],
                 '"결과: " + 8 - 3', '"결과: " + (8 - 3)', '결과: 5', '조심하세요. 글자를 만든 뒤에는 숫자를 뺄 수 없어요.'),
    ]
    SOURCE.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    java = str(Path(os.environ['JAVA_HOME']) / 'bin/java.exe') if os.environ.get('JAVA_HOME') else 'java'
    cache_dir = SOURCE / 'narration_cache'
    cache_dir.mkdir(exist_ok=True)
    for task in tasks:
        fingerprint = hashlib.sha256(('compiler-2\n'+json.dumps(task, ensure_ascii=False, sort_keys=True)).encode()).hexdigest()
        cached = cache_dir / (task['id'] + '.json')
        if cached.exists() and json.loads(cached.read_text(encoding='utf8'))['hash'] == fingerprint:
            task['narration'] = json.loads(cached.read_text(encoding='utf8'))['actions']
        else:
            outputs = []
            for code in (task['starter_code'], task['solution']):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / 'Main.java'
                    path.write_text(code, encoding='utf8')
                    result = subprocess.run([java, '-Dfile.encoding=UTF-8', '-Dstdout.encoding=UTF-8', '-Dstderr.encoding=UTF-8', '--source', '25', str(path)],
                                            capture_output=True, text=True, encoding='utf8', errors='replace', timeout=25)
                    outputs.append(result)
            initial, final = outputs
            assert final.returncode == 0 and final.stdout.strip() == task['tests'][0]['expected'], task['id']
            assert initial.returncode != 0 or initial.stdout.strip() != final.stdout.strip(), task['id']
            initial_read = ('글자에서 숫자를 빼려고 해서 오류가 나요.' if initial.returncode
                            else f"처음 출력은 {initial.stdout.strip().replace(chr(10), ' / ')}예요.")
            actions = [dict(action='set_code', code=task['starter_code'], say='준비 코드를 먼저 실행해 볼게요.'),
                       dict(action='run', expected_failure=initial.returncode != 0),
                       dict(action='say', target='output', text=initial_read),
                       dict(action='say', target='editor', text=task['caution']),
                       dict(action='patch_code', **task['edit'], say='바꿀 부분만 고쳐서 다시 실행해요.'),
                       dict(action='run'),
                       dict(action='say', target='output', text=f"바꾼 뒤 출력은 {final.stdout.strip().replace(chr(10), ' / ')}예요."),
                       dict(action='submit')]
            cached.write_text(json.dumps(dict(hash=fingerprint, by='hand-executed', actions=actions), ensure_ascii=False, indent=2)+'\n', encoding='utf8')
            task['narration'] = actions
        del task['edit'], task['caution']
    lesson = dict(schema_version=1, id='java-principles-output', revision='v1.0.0',
                  title='직접 바꾸며 이해하는 출력과 계산',
                  description='준비 코드 한두 곳을 바꾸는 문제 10개예요. 실행 결과를 비교하며 원리를 찾아요.',
                  review_enabled=False, sources=['https://school.programmers.co.kr/learn/courses/5'], sections=[], tasks=tasks)
    raw = json.dumps(lesson, ensure_ascii=False, indent=2)+'\n'
    (OUT / 'lesson.json').write_text(raw, encoding='utf8', newline='\n')
    course = dict(schema_version=1, id='java-principles', title='자바 · 작은 실험으로 이해하기',
                  description='새 수업의 첫 묶음이에요. 긴 코드를 쓰기 전에 원리를 실험해요.',
                  repository='jhs512/mq3-course-java-principles', lessons=[dict(
                      id=lesson['id'], title=lesson['title'], repository='jhs512/mq3-lesson-java-principles-output',
                      revision='v1.0.0', sha256=hashlib.sha256(raw.encode()).hexdigest(),
                      prerequisites=[], required=True, review_enabled=False)])
    (OUT / 'course.json').write_text(json.dumps(course, ensure_ascii=False, indent=2)+'\n', encoding='utf8', newline='\n')
    print('Built 1 independent lesson / 10 small experiments; original courses preserved.')


if __name__ == '__main__':
    build()
