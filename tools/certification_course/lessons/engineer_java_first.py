"""engineer-java-first: Java value and operator rules that written-exam output questions rely on.

Each exercise is one rule (integer division, %, string joining, +=, ++, casts, char) shown by a
tiny program. Learners write the expected output by hand first, run it, then change one place.
The contract rewrites the prepared values, so a memorized output does not pass.
"""
from certification_course.kit import java_task, main_class
from principles_course.common import lesson

SOURCES = ['https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=991',
           'https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=1453']


def build():
    return lesson('engineer-java-first', '자바의 값과 연산 규칙',
        '실기 코드 문제에서 자주 틀리는 계산 규칙을 익혀요. '
        '출력을 먼저 손으로 적고 실행해서 맞춰 봐요. 필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        java_task('int-division', '정수끼리 나누면 몫만 남아요',
            'int는 정수, double은 소수점이 있는 실수를 담아요.\n'
            'int끼리 나누면 소수 부분을 버리고 몫만 남아요. 한쪽만 double이어도 소수까지 나눠요.\n'
            '실행하기 전에 출력을 먼저 손으로 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            'people 앞의 int를 double로 바꾸세요. double에 담은 2는 2.0이 돼요.\n'
            '다시 실행해서 두 출력을 비교해요.',
            main_class('''
                // 쿠키 수와 나눌 사람 수예요.
                int cookies = 7;
                int people = 2;
                // 한 사람 몫을 출력해요. int인지 double인지에 따라 결과가 달라요.
                System.out.println(cookies / people);
            '''),
            'int people = 2;', 'double people = 2;',
            caution='나누는 수를 2.0처럼 직접 적으면 사람 수가 바뀔 때 틀려요.',
            hints=['int people = 2;를 double people = 2;로 바꿔요.'],
            scenarios=[{'cookies': '9', 'people': '4'}, {'cookies': '8', 'people': '2'}],
            wrong=[('cookies / people', 'cookies / 2.0'),
                   ('System.out.println(cookies / people);', 'System.out.println(3.5);')]),
        java_task('remainder', '나머지는 %로 구해요',
            '/는 나눈 몫을, %는 나눈 나머지를 구해요.\n'
            '예를 들어 7을 2로 나누면 몫은 3, 나머지는 1이에요.\n'
            '실행하기 전에 두 출력을 먼저 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            'left를 구하는 줄의 /를 %로 바꾸세요.\n'
            '남은 쿠키 수가 맞게 나오는지 확인해요.',
            main_class('''
                // 쿠키 수와 한 상자에 담는 개수예요.
                int cookies = 17;
                int size = 5;
                // 꽉 채운 상자 수는 몫으로 구해요.
                int boxes = cookies / size;
                System.out.println(boxes);
                // 상자에 못 담고 남은 쿠키 수를 구할 자리예요.
                int left = cookies / size;
                System.out.println(left);
            '''),
            'int left = cookies / size;', 'int left = cookies % size;',
            caution='size % cookies처럼 순서를 바꾸면 전혀 다른 나머지가 나와요.',
            hints=['int left = cookies % size;로 바꿔요.'],
            # 11, 4 makes boxes differ from size, so cookies % boxes cannot pass by luck.
            scenarios=[{'cookies': '23', 'size': '4'}, {'cookies': '20', 'size': '5'},
                       {'cookies': '9', 'size': '2'}, {'cookies': '11', 'size': '4'}],
            wrong=[('int left = cookies / size;', 'int left = size % cookies;'),
                   ('int left = cookies / size;', 'int left = 2;'),
                   ('int left = cookies / size;', 'int left = cookies % boxes;')]),
        java_task('string-join', '글자 뒤의 +는 이어 붙여요',
            'a + b + c는 a + b를 먼저 구하고, 그 결과에 c를 더해요.\n'
            '+의 한쪽이 따옴표 글자인 문자열(String)이면 이어 붙여요.\n'
            '실행하기 전에 두 줄의 출력을 먼저 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            '둘째 줄도 두 수의 합이 나오게 고치세요.\n'
            'morning + afternoon을 괄호로 묶으면 먼저 더해요.',
            main_class('''
                // 오전과 오후의 판매 수예요.
                int morning = 3;
                int afternoon = 4;
                // 숫자 두 개 뒤에 단위 글자를 붙여요.
                System.out.println(morning + afternoon + "개");
                // 합계 글자 뒤에 숫자 두 개를 붙여요.
                System.out.println("합계: " + morning + afternoon);
            '''),
            '"합계: " + morning + afternoon', '"합계: " + (morning + afternoon)',
            caution='숫자를 하나씩 괄호로 감싸면 여전히 이어 붙여요.',
            hints=['"합계: " + (morning + afternoon)처럼 묶어요.'],
            scenarios=[{'morning': '12', 'afternoon': '5'}, {'morning': '20', 'afternoon': '30'}],
            wrong=[('"합계: " + morning + afternoon', '"합계: " + (morning) + (afternoon)'),
                   ('"합계: " + morning + afternoon', '"합계: 7"')]),
        java_task('compound-assign', '+=는 더한 값을 다시 담아요',
            'total += save는 total = total + save와 같아요.\n'
            '-=, *=, /=도 같은 방식으로 계산해서 다시 담아요.\n'
            '실행하기 전에 마지막 출력을 먼저 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            '둘째 날 줄의 =+는 +=와 기호 순서가 달라요.\n'
            '=+는 total = +save로 읽혀서 save 값만 담아요.\n'
            '그 줄을 +=로 고쳐 저금이 쌓이게 하세요.',
            main_class('''
                // 통장의 처음 금액이에요.
                int total = 1000;
                // 하루에 저금하는 금액이에요.
                int save = 300;
                // 첫날 저금한 금액을 더해 다시 담아요.
                total = total + save;
                // 둘째 날도 더하려고 기호로 줄여 쓴 줄이에요.
                total =+ save;
                System.out.println(total);
            '''),
            'total =+ save;', 'total += save;',
            caution='=+는 =와 부호 +로 읽혀 더하지 않고 덮어써요.',
            hints=['둘째 날 줄을 total += save;로 바꿔요.'],
            scenarios=[{'total': '5000', 'save': '700'}, {'total': '0', 'save': '250'}],
            wrong=[('total =+ save;', 'total = save;'),
                   ('total =+ save;', 'total = total + 300;')]),
        java_task('increment', '++가 앞인지 뒤인지 봐요',
            '++는 변수에 1을 더해요.\n'
            'number++는 지금 값을 mine에 먼저 담고 나서 1을 더해요. ++number는 1을 먼저 더하고 담아요.\n'
            '실행하기 전에 두 출력을 먼저 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            'mine이 1 늘어난 번호를 받게 하세요.\n'
            '++를 number 앞으로 옮기고 다시 실행해요.',
            main_class('''
                // 지금 대기 번호예요.
                int number = 7;
                // 번호를 1 늘리면서 mine에도 담아요.
                int mine = number++;
                // 받은 번호와 늘어난 번호를 차례로 출력해요.
                System.out.println(mine);
                System.out.println(number);
            '''),
            'int mine = number++;', 'int mine = ++number;',
            caution='number + 1로 쓰면 number 자체는 늘어나지 않아요.',
            hints=['int mine = ++number;로 바꿔요.'],
            scenarios=[{'number': '12'}, {'number': '0'}],
            wrong=[('int mine = number++;', 'int mine = number + 1;')]),
        java_task('cast-int', '(int)는 소수 부분을 버려요',
            '값 앞에 (int)를 쓰면 정수로 바꿔요. 이걸 형 변환(cast)이라고 해요.\n'
            '(int)는 반올림하지 않고 소수 부분을 그냥 버려요. 바로 뒤 값 하나에만 붙어요.\n'
            '실행하기 전에 출력을 먼저 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            '무게를 반올림한 정수가 나오게 하세요.\n'
            '0.5를 더하면 소수가 0.5 이상일 때만 다음 정수로 넘어가요.\n'
            '0.5를 더한 값을 괄호로 묶고 (int)로 바꿔요.',
            main_class('''
                // 저울에 찍힌 무게예요.
                double weight = 3.9;
                // 무게를 정수로 바꿔 kg에 담아요.
                int kg = (int) weight;
                System.out.println(kg);
            '''),
            '(int) weight', '(int) (weight + 0.5)',
            caution='괄호 없이 쓰면 합이 실수라 int에 못 담는 오류가 나요.',
            hints=['int kg = (int) (weight + 0.5);처럼 써요.'],
            scenarios=[{'weight': '2.2'}, {'weight': '7.5'}, {'weight': '0.4'}],
            wrong=[('int kg = (int) weight;', 'int kg = (int) weight + 0.5;'),
                   ('(int) weight', '(int) weight + 1')]),
        java_task('cast-before-divide', '나누기 전에 바꿔야 해요',
            '=는 오른쪽 계산을 먼저 끝내고 왼쪽에 담아요.\n'
            '그래서 double 변수에 담아도 int끼리 나눈 몫은 그대로예요. double은 3도 3.0처럼 출력해요.\n'
            '실행하기 전에 출력을 먼저 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            '나누기 전에 sum을 double로 바꾸세요.\n'
            'sum 앞에 (double)을 붙이면 돼요. 괄호가 없으니 sum에만 붙어요.\n'
            '(double)이 /보다 먼저라 한쪽이 double인 나누기가 돼요.',
            main_class('''
                // 점수 합계와 시험 횟수예요.
                int sum = 17;
                int count = 4;
                // 평균을 double 변수에 담아요.
                double avg = sum / count;
                System.out.println(avg);
            '''),
            'sum / count', '(double) sum / count',
            caution='나눈 뒤에 (double)로 바꾸면 버린 소수는 돌아오지 않아요.',
            hints=['double avg = (double) sum / count;처럼 써요.'],
            scenarios=[{'sum': '10', 'count': '4'}, {'sum': '9', 'count': '3'}],
            wrong=[('sum / count', '(double) (sum / count)'),
                   ('sum / count', 'sum / 4.0')]),
        java_task('char-code', '글자 하나에도 번호가 있어요',
            'char는 글자 하나를 담고 작은따옴표로 써요. 글자마다 번호가 있어요.\n'
            "'A'는 65번, 'a'는 97번이에요. + 1은 번호로 계산하고, (char)는 번호를 글자로 바꿔요.\n"
            '실행하기 전에 출력을 먼저 적어 보세요.',
            '준비 코드를 실행해 적은 답과 비교하세요.\n'
            '다음 글자가 나오게 바꾸세요.\n'
            'grade + 1 전체를 괄호로 묶고 (char)로 바꿔요.',
            main_class('''
                // 작은따옴표 안 글자 하나를 char에 담아요.
                char grade = 'A';
                // 다음 등급을 출력하려고 1을 더해요.
                System.out.println(grade + 1);
            '''),
            'grade + 1', '(char) (grade + 1)',
            caution='(char) grade + 1은 글자로 바꾼 뒤 다시 번호로 계산해요.',
            hints=['System.out.println((char) (grade + 1));로 바꿔요.'],
            scenarios=[{'grade': "'C'"}, {'grade': "'x'"}],
            wrong=[('grade + 1', '(char) grade + 1'),
                   ('grade + 1', "'B'")]),
        java_task('average-sentence', '도전 · 평균을 문장에 넣어요',
            '*, /, %는 +보다 먼저 계산해요. 그다음 +를 왼쪽부터 계산해요.\n'
            '앞에서 배운 나누기·형 변환·이어 붙이기를 섞어 봐요.\n'
            '실행하기 전에 출력을 먼저 적어 보세요.',
            '평균이 소수까지 문장에 나오게 하세요.\n'
            '출력 줄 안의 한 곳만 고치면 돼요.',
            main_class('''
                // 점수 합계와 과목 수예요.
                int sum = 15;
                int count = 6;
                // 평균을 문장 가운데에 넣어 출력해요.
                System.out.println("평균 " + sum / count + "점");
            '''),
            'sum / count', '(double) sum / count',
            caution='나눈 뒤에 1.0을 곱해도 버린 소수는 돌아오지 않아요.',
            hints=['나누기는 이미 먼저 계산돼요. 괄호로 묶어도 int끼리면 몫이에요.',
                   '나누기 전에 sum을 double로 바꿔요.'],
            scenarios=[{'sum': '17', 'count': '4'}, {'sum': '12', 'count': '4'}],
            wrong=[('sum / count', '(double) (sum / count)'),
                   ('sum / count', 'sum / count * 1.0')],
            challenge=True),
        java_task('letter-cycle', '도전 · 번호를 알파벳으로 돌려요',
            '0번은 A, 1번은 B처럼 번호로 글자를 골라요.\n'
            '알파벳은 26개라서 26번은 다시 A여야 해요. Z 바로 뒤 번호들은 알파벳이 아닌 기호예요.\n'
            '실행하기 전에 알파벳이 나올지 기호가 나올지 먼저 적어 보세요.',
            'seat가 26 이상이어도 알파벳이 나오게 하세요.\n'
            '앞에서 배운 기호 하나와 숫자 26을 넣으면 돼요.',
            main_class('''
                // 0번부터 세는 자리 번호예요.
                int seat = 27;
                // A에서 번호만큼 뒤에 있는 글자를 골라요.
                System.out.println((char) ('A' + seat));
            '''),
            "'A' + seat", "'A' + seat % 26",
            caution='%를 /로 쓰면 나머지 대신 몫으로 글자를 골라요.',
            hints=['26으로 나눈 나머지는 0부터 25까지예요.', '%는 +보다 먼저 계산돼요.'],
            scenarios=[{'seat': '30'}, {'seat': '52'}, {'seat': '3'}],
            wrong=[("'A' + seat", "'A' + seat / 26"),
                   ("(char) ('A' + seat)", "(char) ('A' + seat) % 26")],
            challenge=True),
    ])
