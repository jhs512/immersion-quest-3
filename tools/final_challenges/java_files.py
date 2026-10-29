"""java-files final challenge: append without losing history, read back as UTF-8, skip bad lines and keep counting."""
from _common import Script, todo

STEP = 'stp_7a5d3e18-6f92-4c4b-a0d7-2b8e1c96f43d'
APPEND_TODO = '        // 여기에 기존 기록을 남긴 채 today를 한 줄로 덧붙이세요.'
READ_TODO = '        // 여기에 파일의 모든 줄을 읽어 숫자인 줄은 total에 더하고, 숫자가 아닌 줄은 invalid로 세세요.'
STARTER = f'''import java.nio.file.*;
import java.nio.charset.StandardCharsets;

public class Main {{
    public static void main(String[] args) throws Exception {{
        Path path = Path.of("visits.txt");
        // 오늘의 방문 수예요. 기록 파일에 한 줄로 남겨야 해요.
        String today = "120";
        int total = 0;
        int invalid = 0;
{APPEND_TODO}
{READ_TODO}
        System.out.println("합계: " + total);
        System.out.println("잘못된 줄: " + invalid);
    }}
}}
'''
APPEND = '''        // APPEND는 기존 내용 뒤에 이어 써요. 없으면 파일 전체를 바꿔요.
        Files.writeString(path, today + "\\n", StandardCharsets.UTF_8, StandardOpenOption.APPEND);'''
READ = '''        for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {
            // 한 줄의 실패가 다음 줄의 계산을 막지 않도록 줄마다 처리해요.
            try {
                total += Integer.parseInt(line.strip());
            } catch (NumberFormatException error) {
                invalid++;
            }
        }'''
SOLUTION = STARTER.replace(APPEND_TODO, APPEND).replace(READ_TODO, READ)
OVERWRITE = APPEND.replace(', StandardOpenOption.APPEND', '')

s = Script(STARTER)
s.say('마지막 도전이에요. 방문 기록 파일에 오늘 줄을 덧붙이고, 파일 전체로 합계를 내요.', 'text:지난 기록은 그대로 남아야 해요.')
s.say('준비된 visits.txt에는 100, 오류, 30 세 줄이 있어요. 오류 줄은 숫자가 아니에요.', 'text:100, 오류, 30')
s.patch(READ_TODO, READ, '먼저 읽는 부분이에요. 줄마다 try를 두어 잘못된 줄을 세고 다음 줄로 가요.')
s.run()
s.say('합계: 130, 잘못된 줄: 1이에요. 아직 오늘 줄을 쓰지 않았어요.', 'output')
s.patch(APPEND_TODO, OVERWRITE, '오늘 줄을 써 볼게요. 먼저 옵션 없이 써 봐요.')
s.run()
s.say('합계: 120, 잘못된 줄: 0이에요. 지난 기록이 지워지고 오늘 줄만 남았어요.', 'output')
s.patch(OVERWRITE, APPEND, '기존 내용 뒤에 이어 쓰도록 APPEND 옵션을 더해요.')
s.run()
s.say('합계: 250, 잘못된 줄: 1이에요. 100, 30, 120을 더했고 오류 줄만 셌어요.', 'output')
s.say('조심하세요. try를 반복 바깥에 두면 오류 줄에서 반복이 끝나 뒤의 30과 120을 더하지 못해요.', 'code:total += Integer.parseInt(line.strip());')

GOAL = ('자, 마지막 도전이에요. 방문 기록 파일 visits.txt에 오늘의 방문 수 today를 한 줄로 덧붙여요. 지난 기록은 그대로 남아야 해요.\n\n'
        '그다음 파일의 모든 줄을 읽어 숫자인 줄은 더하고, 숫자가 아닌 줄은 세요. 준비 파일에는 100, 오류, 30 세 줄이 있어요. '
        '그래서 `합계: 250`과 `잘못된 줄: 1`이 나와야 하고, 실행 뒤 파일 끝에는 120 줄이 더해져 있어야 해요. '
        '채점은 다른 기록 파일과 다른 today로도 실행하고, 실행 뒤 파일 내용도 확인해요.\n\n'
        + todo('visits.txt를 UTF-8로 모든 줄 읽어 숫자인 줄은 total에 더하고 아닌 줄은 invalid로 세는 코드를 쓰세요.',
               '코드 실행 버튼을 눌러 지금 파일의 합계를 확인하세요.',
               '지난 기록을 남긴 채 today를 한 줄로 덧붙이는 코드를 읽기 코드 앞에 쓰세요.',
               '코드 실행 버튼을 눌러 두 줄이 요구와 같은지 확인하세요.',
               '수정한 코드를 제출하세요.'))

SPEC = dict(
    key='java-files', course='java', revision='java-files-8',
    reason='덧붙여 저장하기·같은 인코딩으로 읽기·줄 단위 실패 처리를 한 프로그램에서 직접 조합하고, 출력과 실행 뒤 실제 파일 내용을 함께 채점하는 마지막 도전이에요.',
    grading='실제 JDK 출력과 실행 뒤 visits.txt 내용을 채점하고, 다른 기록 파일·today로 다시 실행해요. 덮어쓰기, 오류 줄에서 중단, 줄바꿈 없는 덧붙임은 실패해요.',
    unit=dict(id='unt_2c9f4b85-7d16-4e3a-9f50-1b8a6d27e3c9', title='마지막 도전',
              objectives=['저장·읽기·실패 처리를 한 프로그램에서 함께 써요.'],
              premise='방문 기록 파일이 준비돼 있어요. 출력 두 줄은 준비돼 있어요.'),
    step=dict(id=STEP, title='방문 기록을 덧붙이고 잘못된 줄을 건너뛰며 합계를 내세요',
              objectives=['기존 파일을 보존하며 저장하고, 잘못된 줄이 있어도 나머지를 계속 처리해요.'],
              core_flow='준비 파일은 100·오류·30이다. 학생은 APPEND로 today를 덧붙이고 줄마다 try로 합계와 잘못된 줄 수를 구한다. '
                        '채점: 출력, 실행 뒤 파일 내용, 다른 파일·today 변형. 덮어쓰기는 지난 기록을 잃어 실패한다.'),
    task=dict(id=STEP, title='방문 기록을 덧붙이고 잘못된 줄을 건너뛰며 합계를 내세요', language='java', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected='합계: 250\n잘못된 줄: 1')],
              files={'visits.txt': '100\n오류\n30\n'},
              expected_files={'visits.txt': '100\n오류\n30\n120\n'},
              variations=[dict(values=dict(today='"5"'), expected='합계: 135\n잘못된 줄: 1', expected_files={'visits.txt': '100\n오류\n30\n5\n'}),
                          dict(files={'visits.txt': ''}, expected='합계: 120\n잘못된 줄: 0', expected_files={'visits.txt': '120\n'}),
                          dict(files={'visits.txt': 'x\n7\ny\n'}, expected='합계: 127\n잘못된 줄: 2', expected_files={'visits.txt': 'x\n7\ny\n120\n'}),
                          dict(values=dict(today='"없음"'), expected='합계: 130\n잘못된 줄: 2', expected_files={'visits.txt': '100\n오류\n30\n없음\n'})],
              narration=s.actions),
    cases=dict(expected_outputs=['합계: 130\n잘못된 줄: 1', '합계: 120\n잘못된 줄: 0', '합계: 250\n잘못된 줄: 1'],
               reject=[([[', StandardOpenOption.APPEND', '']], 'Overwriting loses the earlier visits'),
                       ([['today + "\\n"', 'today']], 'Without a line break the next visit joins this line'),
                       ([['        for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {\n            // 한 줄의 실패가 다음 줄의 계산을 막지 않도록 줄마다 처리해요.\n            try {\n                total += Integer.parseInt(line.strip());\n            } catch (NumberFormatException error) {\n                invalid++;\n            }\n        }',
                          '        try {\n            for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {\n                total += Integer.parseInt(line.strip());\n            }\n        } catch (NumberFormatException error) {\n            invalid++;\n        }']], 'One try around the loop stops at the first bad line')],
               accept=[([['Files.writeString(path, today + "\\n", StandardCharsets.UTF_8, StandardOpenOption.APPEND);',
                          'try (var writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8, StandardOpenOption.APPEND)) {\n            writer.write(today + "\\n");\n        }']], 'A writer with APPEND keeps the same file')]),
    review={'조심하세요. try를 반복 바깥에 두면 오류 줄에서 반복이 끝나 뒤의 30과 120을 더하지 못해요.':
            '이 수업 9번의 실제 실수(try 범위)를 이 파일의 줄 순서로 결과까지 말해요. 반례 채점이 같은 결과를 확인해요.'},
)
