"""engineer-control-first: 조건 경계, AND/OR, 반복, 누적, 인자·반환, 호출 순서를 자바로 따라가요.

정보처리기사 실기는 필답형이라 문제마다 실행 전에 출력이나 상태표를 먼저 적게 해요.
원리 하나마다 준비 코드를 실행하고, 한 곳만 바꿔 다시 실행해 비교해요.
"""
from certification_course.kit import java_task, main_class
from principles_course.common import lesson

SOURCES = ['https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=991']

# main 안 코드는 8칸, 메서드 본문은 8칸, 그 안 블록은 4칸씩 더 들여 써요.
B8, B12, B16 = ' ' * 8, ' ' * 12, ' ' * 16


def solution_mistakes(t, *mistakes):
    """Add mistakes made on top of the solution. Each mistake is a list of (before, after) edits."""
    for edits in mistakes:
        source = t['solution']
        for before, after in edits:
            assert source.count(before) == 1, (t['id'], 'mistake edit must match once', before)
            source = source.replace(before, after, 1)
        assert source not in (t['solution'], t['starter_code']), (t['id'], 'mistake equals starter or solution')
        t['_wrong'].append(source)
    return t


def build():
    tasks = []

    # 1. 조건 경계: 초과와 이상은 기준값에서 갈려요.
    tasks.append(java_task('pass-boundary', '60점은 합격일까요?',
        '`if (조건) { ... }`는 조건이 참일 때만 중괄호 안을 실행해요.\n'
        '조건이 거짓이면 `else { ... }` 안을 실행해요.\n'
        '`>`는 초과, `>=`는 이상이에요. 기준값에서 결과가 갈려요.',
        '실행 전에 출력을 먼저 예상해 적어 보세요.\n'
        '60점도 합격이 되게 비교 기호 하나를 고치세요.\n'
        '다시 실행해서 예상과 비교하세요.',
        main_class('''
            // 합격 기준과 같은 경계값이에요.
            int score = 60;
            // 60점 이상이면 합격이에요.
            if (score > 60) {
                System.out.println(score + "점: 합격");
            } else {
                // 조건이 거짓일 때만 이쪽을 실행해요.
                System.out.println(score + "점: 불합격");
            }
        '''),
        'score > 60', 'score >= 60',
        caution='`>`로 두면 기준과 같은 60점이 불합격이 돼요.',
        hints=['60을 포함하려면 `>=`를 써요.'],
        scenarios=[{'score': '59'}, {'score': '0'}, {'score': '100'}],
        wrong=[('score > 60', 'score => 60'), ('score > 60', 'score == 60'),
               ('int score = 60;', 'int score = 61;')]))

    # 2. else if 순서: 처음 참인 블록 하나만 실행해요.
    swapped = (f'if (score >= 90) {{  // 90점 이상이면 우수예요.\n{B12}System.out.println(score + "점: 우수");\n'
               f'{B8}}} else if (score >= 60) {{  // 60점 이상이면 합격이에요.\n{B12}System.out.println(score + "점: 합격");')
    original = (f'if (score >= 60) {{  // 60점 이상이면 합격이에요.\n{B12}System.out.println(score + "점: 합격");\n'
                f'{B8}}} else if (score >= 90) {{  // 90점 이상이면 우수예요.\n{B12}System.out.println(score + "점: 우수");')
    t = java_task('else-if-order', '넓은 조건이 먼저 오면',
        '`else if`는 앞 조건이 거짓일 때만 다음 조건을 검사해요.\n'
        '위에서부터 처음 참이 된 블록 하나만 실행해요.\n'
        '그래서 더 좁은 조건을 먼저 검사해야 해요.',
        '95점이 어느 블록에 걸릴지 먼저 적어 보세요.\n'
        '90점 이상이면 우수가 나오게 고치세요.\n'
        '`if`와 `else if` 글자는 제자리에 두세요.\n'
        '괄호 안 조건과 그 아래 출력 줄만 맞바꾸면 돼요.',
        main_class('''
            // 90점 이상은 우수, 60점 이상은 합격이에요.
            int score = 95;
            // 위에서부터 차례로 검사해요.
            if (score >= 60) {  // 60점 이상이면 합격이에요.
                System.out.println(score + "점: 합격");
            } else if (score >= 90) {  // 90점 이상이면 우수예요.
                System.out.println(score + "점: 우수");
            } else {
                // 위 조건이 모두 거짓일 때만 와요.
                System.out.println(score + "점: 불합격");
            }
        '''),
        original, swapped,
        caution='60점 이상을 먼저 검사하면 95점도 합격에서 멈춰요.',
        hints=['맨 위 `if` 괄호에 `score >= 90`을 넣고 우수 출력을 그 아래로 옮겨요.'],
        scenarios=[{'score': '90'}, {'score': '60'}, {'score': '59'}],
        # 조건만 바꾸고 출력 글자는 그대로 둔 실수예요.
        wrong=[(original, original.replace('score >= 60', 'score >= 9X').replace('score >= 90', 'score >= 60')
                .replace('score >= 9X', 'score >= 90'))])
    # 순서는 맞게 바꿨지만 90점을 초과로 검사한 실수예요.
    tasks.append(solution_mistakes(t, [('if (score >= 90)', 'if (score > 90)')]))

    # 3. AND/OR: 둘 다인지, 하나라도인지.
    tasks.append(java_task('and-or', '둘 다일까요, 하나라도일까요?',
        '`&&`는 AND예요. 두 조건이 모두 참이어야 참이에요.\n'
        '`||`는 OR예요. 하나만 참이어도 참이에요.\n\n'
        '| 점수 조건 | 출석 조건 | AND | OR |\n'
        '|---|---|---|---|\n'
        '| 참 | 참 | 참 | 참 |\n'
        '| 참 | 거짓 | 거짓 | 참 |\n'
        '| 거짓 | 참 | 거짓 | 참 |\n'
        '| 거짓 | 거짓 | 거짓 | 거짓 |',
        '실행 전에 수료인지 미수료인지 먼저 적어 보세요.\n'
        '두 조건을 모두 채울 때만 수료가 되게 고치세요.\n'
        '기호 하나만 바꾸면 돼요.',
        main_class('''
            // 점수와 출석 횟수를 준비해요.
            int score = 70;
            int attend = 5;
            // 60점 이상이고 출석 8회 이상이면 수료예요.
            if (score >= 60 || attend >= 8) {
                System.out.println(score + "점 " + attend + "회: 수료");
            } else {
                // 두 조건 중 하나라도 못 채우면 와요.
                System.out.println(score + "점 " + attend + "회: 미수료");
            }
        '''),
        '||', '&&',
        caution='`||`로 두면 출석이 모자라도 수료가 나와요.',
        hints=['둘 다 참이어야 할 때는 `&&`를 써요.'],
        scenarios=[{'score': '60', 'attend': '8'}, {'score': '90', 'attend': '7'},
                   {'score': '59', 'attend': '12'}],
        wrong=[('score >= 60 || attend >= 8', 'score >= 60 && attend > 8'),
               ('score >= 60 || attend >= 8', 'score > 60 && attend >= 8')]))

    # 4. for의 증가량과 마지막 값 포함 여부.
    t = java_task('odd-step', '2씩 커지는 반복',
        '`for (시작; 조건; 증가)`는 세 칸으로 반복을 정해요.\n'
        '조건이 참이면 본문을 실행하고, 증가식을 거쳐 다시 검사해요.\n'
        '반복마다 값을 적은 표를 상태표라고 해요.\n'
        '아래 표는 n이 5일 때 i가 2씩 커지는 예예요.\n\n'
        '| i | `i <= n` | 출력 |\n'
        '|---|---|---|\n'
        '| 1 | 참 | 1 |\n'
        '| 3 | 참 | 3 |\n'
        '| 5 | ? | ? |\n'
        '| 7 | ? | ? |',
        '상태표의 ?를 채우세요. 출력이 없으면 -로 적어요.\n'
        '`i++`는 1씩 키워요. `+=`를 써서 2씩 키우게 고치세요.\n'
        '준비 코드의 n은 9 그대로 두세요.\n'
        '마지막 값 9도 출력되는지 확인하세요.',
        main_class('''
            // 출력할 범위의 끝이에요.
            int n = 9;
            // i는 1에서 시작해 n 이하인 동안 반복해요.
            for (int i = 1; i <= n; i++) {
                // 이번 반복의 i를 출력해요.
                System.out.println(i);
            }
        '''),
        'i++)', 'i += 2)',
        caution='`i + 2`는 i에 저장하지 않아서 실행 전에 오류가 나요.',
        hints=['`i += 2`는 `i = i + 2`와 같아요.'],
        scenarios=[{'n': '12'}, {'n': '1'}, {'n': '0'}],
        wrong=[('i++)', 'i + 2)')])
    # 2씩 늘렸지만 마지막 n을 빼거나 0에서 시작한 실수예요.
    tasks.append(solution_mistakes(t, [('i <= n; i += 2', 'i < n; i += 2')],
                                   [('int i = 1; i <= n; i += 2', 'int i = 0; i <= n; i += 2')]))

    # 5. 누적 변수의 위치: 반복 밖에서 한 번만 0으로 시작해요.
    t = java_task('sum-outside', '합계를 매번 0으로 지우면',
        '중괄호 안에서 만든 변수는 그 중괄호 안에서만 써요.\n'
        '반복 안의 `int sum = 0;`은 돌 때마다 새로 0이 돼요.\n'
        '쌓을 변수는 반복 밖에서 한 번만 만들어요.\n\n'
        '| i | 밖에서 만든 sum |\n'
        '|---|---|\n'
        '| 1 | 1 |\n'
        '| 2 | ? |\n'
        '| 3 | ? |',
        '준비 코드의 sum이 쌓이지 않는 걸 확인하세요.\n'
        '표의 ?를 채운 뒤 `int sum = 0;`을 for 위로 옮기세요.\n'
        '다시 실행해서 표와 비교하세요.',
        main_class('''
            // 1부터 n까지 차례로 더해요.
            int n = 4;
            for (int i = 1; i <= n; i++) {
                // 합계를 0에서 시작해요.
                int sum = 0;
                // 지금 i를 합계에 더해요.
                sum += i;
                // 반복마다 i와 sum을 상태표처럼 출력해요.
                System.out.println("i=" + i + ", sum=" + sum);
            }
        '''),
        f'for (int i = 1; i <= n; i++) {{\n{B12}// 합계를 0에서 시작해요.\n{B12}int sum = 0;',
        f'// 합계를 0에서 시작해요.\n{B8}int sum = 0;\n{B8}for (int i = 1; i <= n; i++) {{',
        caution='반복 안에서 `sum = 0`을 하면 앞에서 더한 값이 지워져요.',
        hints=['합계를 만드는 줄과 그 주석을 for 바로 위로 옮겨요.'],
        scenarios=[{'n': '1'}, {'n': '0'}, {'n': '6'}])
    # 밖에서 만들고도 안에서 다시 0으로 만들거나, 더하지 않고 덮어쓴 실수예요.
    tasks.append(solution_mistakes(t,
        [('i++) {\n' + B12 + '// 지금 i', 'i++) {\n' + B12 + 'sum = 0;\n' + B12 + '// 지금 i')],
        [('sum += i;', 'sum = i;')]))

    # 6. while: 0이 될 때까지 나누며 자릿수를 세요.
    tasks.append(java_task('digit-count', '0이 될 때까지 나눠요',
        '`while (조건)`은 조건이 참인 동안 본문을 반복해요.\n'
        '`n /= 10`은 `n = n / 10`이라 끝자리가 사라져요.\n\n'
        '| n | count |\n'
        '|---|---|\n'
        '| 35 | 0 |\n'
        '| 3 | 1 |\n'
        '| 0 | 2 |\n\n'
        '35는 두 번 나눠야 0이 되니 두 자리예요.',
        '4096의 상태표를 먼저 적어 보세요.\n'
        '자릿수가 맞게 while의 조건만 고치세요.\n'
        'n이 0이 될 때까지 나눠야 해요.',
        main_class('''
            // 자릿수를 셀 양의 정수예요.
            int n = 4096;
            // 나눈 횟수를 세요.
            int count = 0;
            // 조건이 참인 동안 반복해요.
            while (n > 10) {
                // 끝자리를 하나 지우고 횟수를 더해요.
                n /= 10;
                count++;
            }
            System.out.println("자릿수: " + count);
        '''),
        'n > 10', 'n > 0',
        caution='`n >= 10`으로 쓰면 마지막 한 자리를 세지 않아요.',
        hints=['n이 0보다 큰 동안 반복해요.'],
        scenarios=[{'n': '10'}, {'n': '1'}, {'n': '100000'}],
        wrong=[('n > 10', 'n >= 10'), ('n > 10', 'n > 1')]))

    # 7. 인자와 반환: 매개변수는 값의 복사본이고, 반환값은 받아야 남아요.
    tasks.append(java_task('return-value', '메서드가 돌려준 값을 받아요',
        '메서드는 이름 붙인 코드 묶음이에요. 부르면 실행하고 돌아와요.\n'
        '매개변수(parameter)는 메서드가 받는 변수예요. 값만 복사돼 들어와요.\n'
        '그래서 안에서 바꾼 값은 `return`으로 돌려받아 대입해야 남아요.',
        '두 줄의 출력을 먼저 예상해 적으세요.\n'
        '이름이 같아도 두 score는 서로 다른 변수예요.\n'
        'main의 score도 바뀐 값이 되게 호출 줄을 고치세요.',
        main_class('''
            // main의 점수예요.
            int score = 70;
            // score의 값만 복사해서 메서드에 넘겨요.
            addBonus(score);
            // main의 score를 확인해요.
            System.out.println("main: " + score);
        ''', '''
            // static을 붙여야 main에서 바로 부를 수 있어요.
            // 이름 앞 int는 돌려줄 값의 자료형, 괄호 안은 받을 값이에요.
            static int addBonus(int score) {
                // 더해 줄 보너스 점수예요.
                int bonus = 10;
                // 메서드 안의 score만 바뀌어요.
                score = score + bonus;
                System.out.println("메서드 안: " + score);
                // 바뀐 값을 호출한 자리로 돌려줘요.
                return score;
            }
        '''),
        'addBonus(score);', 'score = addBonus(score);',
        caution='`addBonus(score);`만 쓰면 돌려준 값이 버려져요.',
        hints=['`score = addBonus(score);`처럼 받아요.'],
        # 보너스도 바꿔서, 돌려준 값을 쓰지 않고 main에서 10을 직접 더한 답을 걸러요.
        scenarios=[{'score': '0'}, {'score': '95', 'bonus': '5'}, {'score': '1', 'bonus': '20'}],
        wrong=[('addBonus(score);', 'int score = addBonus(score);'),
               ('addBonus(score);', 'score = score + 10;'),
               ('addBonus(score);', 'addBonus(score);\n' + B8 + 'score = score + 10;')]))

    # 8. 호출 순서: 안쪽 호출이 먼저 끝나야 바깥 출력이 찍혀요.
    tasks.append(java_task('call-order', '안쪽 호출이 먼저 끝나요',
        '`twice(twice(n))`은 안쪽 `twice(n)`부터 실행해요.\n'
        '그 결과가 바깥 `twice`에 값으로 들어가요.\n'
        '바깥 println은 괄호 안 계산이 모두 끝난 뒤에 찍혀요.',
        '준비 코드의 출력 세 줄을 먼저 적어 보세요.\n'
        '`twice`를 두 번 거쳐 네 배가 나오게 고치세요.\n'
        '메서드 안 출력의 횟수와 순서를 비교하세요.',
        main_class('''
            // 처음 넘길 값이에요.
            int n = 3;
            System.out.println("시작");
            // 괄호 안 호출이 끝나야 이 줄을 출력할 수 있어요.
            System.out.println("결과: " + twice(n));
        ''', '''
            // 받은 int의 두 배를 돌려줘요.
            static int twice(int x) {
                // 불릴 때마다 받은 값을 먼저 출력해요.
                System.out.println("twice(" + x + ") 실행");
                return x * 2;
            }
        '''),
        'twice(n)', 'twice(twice(n))',
        caution='`twice(n) * 2`도 네 배지만 메서드는 한 번만 불려요.',
        hints=['`twice(n)`을 다시 `twice(...)`로 감싸요.'],
        scenarios=[{'n': '0'}, {'n': '1'}, {'n': '5'}],
        wrong=[('twice(n)', 'twice(n) * 2'), ('twice(n)', 'twice(n) + twice(n)')]))

    # 9. 도전: 반복 + 조건 + 누적 + 나머지.
    t = java_task('divisor-count', '도전 · 약수의 개수 세기',
        '앞에서 배운 반복·조건·누적을 함께 써요.\n'
        '`a % b`는 a를 b로 나눈 나머지예요. 0이면 나누어떨어져요.\n'
        'n을 나누어떨어지게 하는 수가 약수예요. `==`는 같은지 비교해요.',
        '12의 약수가 몇 개인지 먼저 손으로 세 보세요.\n'
        '준비 코드가 다르게 세는 곳을 찾아 고치세요.\n'
        '1과 n 자신도 약수에 넣어요.',
        main_class('''
            // 약수를 셀 정수예요.
            int n = 12;
            // 찾은 약수의 개수예요.
            int count = 0;
            // 1부터 n까지 하나씩 확인해요.
            for (int i = 1; i <= n; i++) {
                // i가 n의 약수인지 확인해요.
                if (i % n == 0) {
                    count++;
                }
            }
            System.out.println(n + "의 약수: " + count + "개");
        '''),
        'i % n == 0', 'n % i == 0',
        caution='`i % n`과 `n % i`는 나누는 쪽이 달라요.',
        hints=['n을 i로 나눈 나머지가 0이면 i는 약수예요.', '`%` 양쪽의 순서를 확인해 보세요.'],
        scenarios=[{'n': '1'}, {'n': '7'}, {'n': '16'}],
        challenge=True)
    # 조건은 고쳤지만 n 자신을 빼거나, 개수 대신 약수를 더한 실수예요.
    tasks.append(solution_mistakes(t, [('i <= n; i++', 'i < n; i++')], [('count++;', 'count += i;')]))

    # 10. 도전: while + 조건 + 메서드 인자·반환.
    t = java_task('max-digit', '도전 · 가장 큰 숫자 찾기',
        'while, 조건, 메서드를 함께 써요.\n'
        '최댓값은 더 큰 값을 만났을 때만 바꿔요.\n'
        '메서드 안에서 n이 줄어도 main의 num은 그대로예요.',
        '준비 코드대로 5283을 끝자리부터 따라가 보세요.\n'
        'digit과 max를 상태표로 적고 출력과 비교하세요.\n'
        '`maxDigit`이 가장 큰 숫자를 돌려주게 고치세요.',
        main_class('''
            // 가장 큰 숫자를 찾을 정수예요.
            int num = 5283;
            // 메서드에는 num의 값만 복사돼 넘어가요.
            System.out.println(num + "의 가장 큰 숫자: " + maxDigit(num));
        ''', '''
            // 각 자리 숫자 중 가장 큰 숫자를 돌려줘요.
            static int maxDigit(int n) {
                // 지금까지 본 숫자 중 가장 큰 값이에요.
                int max = 0;
                while (n > 0) {
                    // 맨 끝자리 숫자를 꺼내요.
                    int digit = n % 10;
                    // max를 고르는 자리예요.
                    max = digit;
                    // 끝자리를 지워요.
                    n /= 10;
                }
                return max;
            }
        '''),
        'max = digit;', f'if (digit > max) {{\n{B16}max = digit;\n{B12}}}',
        caution='조건 없이 대입하면 마지막에 본 숫자가 남아요.',
        hints=['더 큰 숫자를 만났을 때만 max를 바꿔요.', '`max = digit;`을 if로 감싸 보세요.'],
        scenarios=[{'num': '19'}, {'num': '1000'}, {'num': '0'}],
        wrong=[('max = digit;', 'max += digit;')],
        challenge=True)
    # if는 넣었지만 비교 방향을 거꾸로 쓴 실수예요.
    tasks.append(solution_mistakes(t, [('digit > max', 'digit < max')]))

    required = sum(item['required'] for item in tasks)
    challenges = len(tasks) - required
    return lesson('engineer-control-first', '조건·반복·함수의 공통 원리',
        '실기 코드 문제처럼 조건·반복·메서드를 따라가요. 상태표를 손으로 적는 습관을 만들어요. '
        f'필수 문제 {required}개와 선택 도전 {challenges}개예요.',
        SOURCES, tasks)
