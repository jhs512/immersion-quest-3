"""Author and verify the JDK 25 course without touching the preserved KPC course.

Hand-written Korean lessons, commented answers and runnable narration stages are
kept together here. --verify executes every example, stage and answer on JDK 25.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from java_strengthening import strengthen

ROOT = Path(__file__).resolve().parents[1]


def program(body, extra=""):
    return "class Main {\n    public static void main(String[] args) {\n" + "\n".join("        " + line for line in body.splitlines()) + "\n    }\n" + extra + "}\n"


LESSONS = []


def lesson(title, body, example, example_output, check, accepted, goal, code, cases, hint, caution, quiz, options, explanation, extra="", stage=None):
    LESSONS.append(dict(title=title, body=body, example=example, example_output=example_output,
        check=check, accepted=accepted, goal=goal, solution=program(code, extra), cases=cases,
        hint=hint, caution=caution, quiz=quiz, options=options, explanation=explanation,
        stage=stage or program(example)))


lesson("처음 실행하고 출력하기",
"프로그램은 우리가 적은 순서대로 일을 해요.\nJDK는 자바 코드를 실행하는 개발 도구예요.\n이 과정에서는 JDK 25를 사용해요.\n\n먼저 터미널에서 `java --version`을 확인하세요.\n첫 줄의 버전이 25로 시작해야 해요.\n`javac --version`도 25인지 확인하세요.\n앱의 ‘환경 진단’에서도 실행을 확인할 수 있어요.\n\n코드는 `Main.java`에 적어요.\n`main`의 중괄호 안에 실행할 일을 넣어요.\n`System.out.println`은 출력 뒤에 줄을 바꿔요.\n문자열은 큰따옴표로 감싸요.\n문장 끝에는 세미콜론 `;`을 붙여요.\n\n앱 밖에서는 `java --source 25 Main.java`로 실행해요.\n이 과정은 preview 옵션을 사용하지 않아요.\n처음에는 준비 코드의 바깥 구조를 그대로 두세요.",
'// 큰따옴표 안의 글자를 한 줄로 출력해요.\nSystem.out.println("안녕");', "안녕\n",
"출력 후 줄을 바꾸는 메서드 이름은 무엇인가요?", ["println", "System.out.println"],
"첫 줄에 `안녕`, 둘째 줄에 `JDK 25`를 출력하세요.\n안내 문구나 빈 줄은 추가하지 마세요.",
'// 첫 인사는 첫 줄에 남겨요.\nSystem.out.println("안녕");\n// 다음 호출은 새 줄에 출력해요.\nSystem.out.println("JDK 25");',
[("", "안녕\nJDK 25\n")], "println을 두 번 호출하세요.", "작은따옴표는 문자열용이 아니에요. 큰따옴표를 쓰세요.",
"자바 문장의 끝에 붙이는 기호는 무엇인가요?", [";", ":", ",", "#"],
"정답은 세미콜론 ;예요.\n다른 보기는 왜 아닌가요?\n:는 문장 끝 표시가 아니에요.\n,는 값들을 구분할 때 써요.\n#는 자바의 주석 기호가 아니에요.")

lesson("변수와 자료형",
"변수는 값을 보관하는 이름이에요.\n`int`는 정수, `double`은 실수를 담아요.\n`String`은 문자열, `boolean`은 참과 거짓을 담죠.\n\n`int price = 1200;`을 살펴볼까요?\nprice라는 정수 변수에 1200을 넣어요.\n`=`는 오른쪽 값을 왼쪽에 저장해요.\n같은지 비교하는 기호는 `==`예요.\n\n숫자는 따옴표 없이 적어요.\n`1200`과 `\"1200\"`은 자료형이 달라요.\n`//` 뒤는 실행하지 않는 설명 주석이에요.",
"// 가격을 정수로 보관해요.\nint price = 1200;\nSystem.out.println(price);", "1200\n",
"정수를 담는 자료형은 무엇인가요?", ["int"],
"가격 1200과 수량 3을 각각 변수에 저장하세요.\n두 변수를 곱한 총액을 한 줄로 출력하세요.",
"// 가격과 수량은 계산할 숫자예요.\nint price = 1200;\nint quantity = 3;\n// 곱한 결과를 total에 보관해요.\nint total = price * quantity;\nSystem.out.println(total);",
[("", "3600\n")], "int total = price * quantity;를 사용해 보세요.", "숫자를 큰따옴표로 감싸면 문자열이 돼요. 곱셈에 쓰지 마세요.",
"참과 거짓을 담는 자료형은 무엇인가요?", ["boolean", "String", "double", "int"],
"boolean은 true와 false를 담아요.\n다른 보기는 왜 아닌가요?\nString은 글자, double은 실수예요.\nint는 정수를 담아요.")

lesson("몫과 나머지",
"정수끼리 나누면 정수 몫이 나와요.\n`7 / 2`는 3이에요. 소수 부분은 버려요.\n`7 % 2`는 나머지인 1이죠.\n\n괄호 안을 먼저 계산해요.\n곱셈과 나눗셈은 덧셈보다 먼저예요.\n소수 계산은 `7.0 / 2`처럼 실수를 써요.\n결과가 3.5로 달라져요.",
"// 정수 나눗셈은 정수 몫을 만들어요.\nSystem.out.println(7 / 2);", "3\n",
"7 % 2의 결과는 무엇인가요?", ["1"],
"빵 17개를 5개씩 포장해요.\n완성한 묶음 수와 남은 빵 수를 각각 출력하세요.",
"// 전체와 한 묶음의 크기를 보관해요.\nint breads = 17;\nint bundleSize = 5;\n// /는 몫, %는 남은 개수를 구해요.\nSystem.out.println(breads / bundleSize);\nSystem.out.println(breads % bundleSize);",
[("", "3\n2\n")], "/와 %를 각각 한 번 사용하세요.", "묶음 크기가 0이면 나눗셈을 할 수 없어요. 5를 사용하세요.",
"7.0 / 2의 결과는 무엇인가요?", ["3.5", "3", "1", "7.0"],
"실수가 하나 있으면 실수 나눗셈을 해요.\n다른 보기는 왜 아닌가요?\n3은 정수끼리 나눈 몫이에요.\n1은 7 % 2의 나머지예요.\n7.0은 나누기 전 값이에요.")

lesson("입력받아 계산하기",
"입력은 실행할 때 들어오는 값이에요.\n`Scanner`로 공백 사이의 값을 읽어요.\n`nextInt()`는 다음 정수를 읽어요.\n`next()`는 다음 문자열 한 토큰을 읽죠.\n\n아래 예제는 입력으로 `4 6`을 사용해요.\n각 실행은 새로운 입력에서 시작해요.\n앱의 ‘실행 입력’ 칸에 숫자를 적으세요.\n채점할 때는 여러 입력으로 다시 실행해요.\n한국어 입력도 읽도록 UTF-8을 지정해요.",
'// UTF-8 입력에서 정수 두 개를 읽어요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint a = scanner.nextInt();\nint b = scanner.nextInt();\n// 입력값은 실행마다 달라져요.\nSystem.out.println(a + b);', "10\n",
"Scanner에서 다음 정수를 읽는 메서드는 무엇인가요?", ["nextInt", "nextInt()"],
"정수 두 개를 입력받아 합을 출력하세요.\n입력은 -1000부터 1000까지의 정수예요.\n입력을 요청하는 안내 글은 출력하지 마세요.",
'// 공백과 줄바꿈으로 나뉜 입력을 읽어요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint first = scanner.nextInt();\nint second = scanner.nextInt();\n// 예제 숫자를 직접 적지 않고 입력으로 계산해요.\nSystem.out.println(first + second);',
[("4 6\n", "10\n"), ("-3 8\n", "5\n"), ("0 0\n", "0\n"), ("1000 -1000\n", "0\n")], "nextInt()를 두 번 호출하세요.", "안내 글을 출력하면 예상 출력과 달라져요. 합만 출력하세요.",
"nextInt()에 필요한 숫자가 입력에 없으면 어떻게 될까요?", ["실행 오류가 나요", "자동으로 0을 읽어요", "이전 값을 읽어요", "문자열을 반환해요"],
"읽을 값이 없으면 예외가 발생해요.\n다른 보기는 왜 아닌가요?\n0이나 이전 값을 자동으로 넣지 않아요.\nnextInt()의 결과는 문자열이 아니에요.")

lesson("조건에 따라 선택하기",
"`if`는 조건이 true일 때만 실행해요.\n`else`는 조건이 false일 때 실행하죠.\n`>=`는 크거나 같다는 뜻이에요.\n`==`는 같은 값을 비교해요.\n\n점수 60도 합격에 포함하려면 `>= 60`이에요.\n`> 60`은 60을 제외해요.\n경계값에서 직접 확인해 보세요.",
"// 경계 점수도 합격에 포함해요.\nint score = 60;\nSystem.out.println(score >= 60);", "true\n",
"60 이상을 비교할 때 쓰는 기호는 무엇인가요?", [">="],
"0부터 100까지의 점수를 입력받아요.\n60 이상이면 `합격`, 아니면 `재도전`을 출력하세요.",
'// 입력한 점수로 조건을 판단해요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint score = scanner.nextInt();\n// 60도 합격에 포함하므로 >=를 써요.\nif (score >= 60) {\n    System.out.println("합격");\n} else {\n    System.out.println("재도전");\n}',
[("60\n", "합격\n"), ("59\n", "재도전\n"), ("0\n", "재도전\n"), ("100\n", "합격\n")], "if (score >= 60) 다음에 중괄호를 여세요.", "> 60은 60점을 놓쳐요. 경계값을 포함하는지 확인하세요.",
"두 조건이 모두 참인지 확인하는 연산자는 무엇인가요?", ["&&", "||", "=", "!"],
"&&는 두 조건이 모두 true인지 확인해요.\n다른 보기는 왜 아닌가요?\n||는 하나만 참이어도 참이에요.\n=는 저장, !는 참과 거짓을 뒤집어요.")

lesson("for로 반복하고 누적하기",
"`for`는 같은 일을 여러 번 실행해요.\n괄호 안은 시작값, 조건, 다음 값 순서예요.\n`i++`는 i를 1 늘려요.\n조건이 false가 되면 반복을 끝내죠.\n\n합을 구할 때는 반복 밖에 변수를 만들어요.\n`sum += i`는 sum에 i를 더해 저장해요.\n반복 안에서 sum을 0으로 만들면 합이 사라져요.",
"// i가 1, 2, 3일 때 출력하고 멈춰요.\nfor (int i = 1; i <= 3; i++) {\n    System.out.println(i);\n}", "1\n2\n3\n",
"i를 1 늘리는 짧은 표현은 무엇인가요?", ["i++", "++i"],
"정수 n을 입력받아요. 범위는 1부터 100이에요.\n1부터 n까지의 합을 한 줄로 출력하세요.",
'// 몇까지 더할지 입력받아요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint n = scanner.nextInt();\nint sum = 0;\n// 누적 변수는 반복 밖에서 한 번만 만들어요.\nfor (int i = 1; i <= n; i++) {\n    sum += i;\n}\nSystem.out.println(sum);',
[("5\n", "15\n"), ("1\n", "1\n"), ("100\n", "5050\n")], "sum은 0에서 시작하고 i를 더해요.", "i < n이면 n을 더하지 않아요. 마지막 값도 포함하세요.",
"sum을 반복문 안에서 매번 0으로 만들면 어떤 문제가 생길까요?", ["이전까지 더한 값이 사라져요", "반복 횟수가 늘어요", "자료형이 String으로 바뀌어요", "항상 컴파일 오류예요"],
"sum을 다시 0으로 저장해 누적값을 잃어요.\n다른 보기는 왜 아닌가요?\n반복 횟수와 자료형은 바뀌지 않아요.\n문법은 맞아도 계산이 틀릴 수 있어요.")

lesson("while과 종료 조건",
"`while`은 조건이 참인 동안 반복해요.\n횟수보다 끝나는 조건이 중요할 때 써요.\n\n0이 나올 때까지 값을 더해 볼까요?\n먼저 값을 읽고 0인지 확인해요.\n반복 안에서도 다음 값을 읽어야 해요.\n그러지 않으면 같은 값으로 계속 반복해요.",
"// 조건을 바꿔야 반복이 끝나요.\nint count = 2;\nwhile (count > 0) {\n    System.out.println(count);\n    count--;\n}", "2\n1\n",
"조건이 참인 동안 반복하는 키워드는 무엇인가요?", ["while"],
"정수를 차례로 입력받아 0 전까지 더하세요.\n입력은 -100부터 100까지예요.\n마지막에는 반드시 0이 있어요.\n입력 개수는 100개 이하여요. 합만 출력하세요.",
'// 첫 값을 읽고 종료값인지 확인해요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint value = scanner.nextInt();\nint sum = 0;\n// 0은 더하지 않고 종료 신호로 사용해요.\nwhile (value != 0) {\n    sum += value;\n    // 다음 입력을 읽어 조건이 바뀌게 해요.\n    value = scanner.nextInt();\n}\nSystem.out.println(sum);',
[("3 4 0\n", "7\n"), ("0\n", "0\n"), ("-2 8 -1 0\n", "5\n")], "반복 안의 마지막 줄에서 다음 값을 읽으세요.", "다음 값을 읽지 않으면 끝나지 않아요. 실행 시간 제한이 있어요.",
"while의 조건이 처음부터 false이면 본문은 몇 번 실행될까요?", ["0번", "1번", "2번", "끝없이 반복해요"],
"while은 실행 전에 조건부터 확인해요.\n다른 보기는 왜 아닌가요?\n1번이나 2번 실행할 이유가 없어요.\nfalse 조건으로는 반복을 시작하지 않아요.")

lesson("배열과 인덱스",
"배열은 같은 자료형의 값을 묶어서 보관해요.\n`int[] scores = {70, 80, 90};`처럼 만들어요.\n인덱스는 배열 안의 자리 번호예요.\n첫 값은 `scores[0]`이에요.\n길이는 `scores.length`로 확인해요.\n\n길이가 3이면 마지막 인덱스는 2예요.\n`i < scores.length`까지만 접근하세요.\n범위를 벗어나면 실행 오류가 나요.",
"// 첫 자리는 0부터 시작해요.\nint[] scores = {70, 80, 90};\nSystem.out.println(scores[0]);", "70\n",
"배열의 첫 인덱스는 무엇인가요?", ["0"],
"첫 입력 n은 배열의 길이예요. 1부터 10이에요.\n이어서 n개의 정수를 입력받아요.\n각 값은 -100부터 100까지예요.\n배열에 담은 뒤 전체 합을 출력하세요.",
'// 길이를 읽고 그만큼의 배열을 만들어요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint n = scanner.nextInt();\nint[] values = new int[n];\n// 인덱스는 0부터 n-1까지예요.\nfor (int i = 0; i < values.length; i++) {\n    values[i] = scanner.nextInt();\n}\n// 배열에 저장한 값을 하나씩 더해요.\nint sum = 0;\nfor (int value : values) {\n    sum += value;\n}\nSystem.out.println(sum);',
[("3 70 80 90\n", "240\n"), ("1 -5\n", "-5\n"), ("4 -2 0 2 8\n", "8\n")], "new int[n]으로 배열을 만든 뒤 입력을 저장하세요.", "i <= values.length는 범위를 벗어나요. <를 사용하세요.",
"길이가 4인 배열의 마지막 인덱스는 무엇인가요?", ["3", "4", "1", "0"],
"0부터 세므로 마지막 자리는 3이에요.\n다른 보기는 왜 아닌가요?\n4는 길이이고 유효한 인덱스가 아니에요.\n1은 둘째, 0은 첫 자리예요.")

lesson("메서드로 계산 나누기",
"메서드는 이름을 붙여 묶은 동작이에요.\n입력값을 매개변수로 받아요.\n`return`으로 결과를 돌려주죠.\n\n`static int twice(int value)`를 볼까요?\n정수 하나를 받고 정수 결과를 돌려줘요.\nmain 밖, Main 클래스 안에 정의해요.\nmain에서 바로 부르도록 static을 붙여요.\nvoid 메서드는 결과값을 반환하지 않아요.",
"// 메서드 호출에 전달한 4가 value에 들어가요.\nSystem.out.println(twice(4));", "8\n",
"메서드에서 결과를 돌려주는 키워드는 무엇인가요?", ["return"],
"정수 하나를 입력받아 두 배를 출력하세요.\n입력 범위는 -1000부터 1000까지예요.\n계산은 static int twice(int value)에 적으세요.\nmain에서는 twice를 호출해 결과를 출력하세요.",
'// 입력을 메서드에 전달해요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint value = scanner.nextInt();\nSystem.out.println(twice(value));',
[("4\n", "8\n"), ("-3\n", "-6\n"), ("0\n", "0\n")], "main의 닫는 중괄호 뒤에 twice를 정의하세요.", "메서드를 main 안에 정의하면 컴파일 오류예요. Main 안의 다른 위치에 적으세요.",
"void의 뜻으로 맞는 것은 무엇인가요?", ["반환값이 없어요", "정수를 반환해요", "문자열을 반환해요", "호출할 수 없어요"],
"void는 결과값을 반환하지 않아요.\n다른 보기는 왜 아닌가요?\n정수 반환은 int, 문자열 반환은 String이에요.\nvoid 메서드도 호출할 수 있어요.",
extra="    // 같은 계산을 여러 곳에서 사용할 수 있어요.\n    static int twice(int value) {\n        return value * 2;\n    }\n",
stage=program("// 먼저 고정된 값으로 메서드를 확인해요.\nSystem.out.println(twice(4));", "    static int twice(int value) {\n        return value * 2;\n    }\n"))

lesson("문자열과 값 비교",
"문자열은 글자들의 묶음이에요.\n`length()`로 글자 수를 확인해요.\n`equals()`로 같은 내용인지 비교해요.\n\n문자열에 `==`를 쓰면 참조를 비교해요.\n내용을 비교하려면 equals를 사용하세요.\n`+`로 문자열을 이어 붙일 수도 있어요.\n숫자를 먼저 더하려면 괄호로 묶으세요.",
'// equals는 글자 내용이 같은지 비교해요.\nString word = "java";\nSystem.out.println(word.equals("java"));', "true\n",
"문자열 내용을 비교하는 메서드는 무엇인가요?", ["equals", "equals()"],
"공백 없는 단어 하나를 입력받아요.\n정확히 `java`면 `환영해요`를 출력하세요.\n다른 단어는 `다시 입력해요`를 출력하세요.\n영문 대문자와 소문자는 구분해요.",
'// 공백 없는 문자열 하나를 읽어요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nString word = scanner.next();\n// 문자열 내용은 equals로 비교해요.\nif (word.equals("java")) {\n    System.out.println("환영해요");\n} else {\n    System.out.println("다시 입력해요");\n}',
[("java\n", "환영해요\n"), ("Java\n", "다시 입력해요\n"), ("python\n", "다시 입력해요\n"), ("자바\n", "다시 입력해요\n")], 'word.equals("java")를 조건에 사용하세요.', "==로 문자열 내용을 비교하지 마세요. 우연히 맞아 보여도 입력에서는 달라질 수 있어요.",
'"합: " + (2 + 3)의 결과는 무엇인가요?', ["합: 5", "합: 23", "5", "컴파일 오류"],
"괄호 안에서 먼저 숫자 덧셈을 해요.\n다른 보기는 왜 아닌가요?\n합: 23은 괄호 없이 이어 붙인 결과예요.\n앞의 문자열도 남으므로 5만 나오지 않아요.\n유효한 문법이라 컴파일 오류는 아니에요.")

lesson("클래스와 객체",
"클래스는 데이터와 동작을 함께 정의해요.\n객체는 그 클래스로 만든 실제 값이에요.\n`new Counter()`로 새 객체를 만들어요.\n\n객체의 필드에는 각자의 값을 보관해요.\n메서드는 그 객체의 값을 바꿀 수 있죠.\n`counter.add()`처럼 점으로 호출해요.\n아래 Counter는 Main 안에 둔 중첩 클래스예요.\n그래서 Main.java 한 파일에서 연습할 수 있어요.",
"// new로 만든 객체의 필드를 읽어요.\nCounter counter = new Counter();\nSystem.out.println(counter.value);", "0\n",
"객체를 만드는 키워드는 무엇인가요?", ["new"],
"Counter 클래스에 int value 필드를 만들어요.\nadd() 메서드는 value를 1 늘려요.\n객체 하나를 만들고 add()를 세 번 호출하세요.\n마지막 value를 출력하세요.",
"// 이 객체가 자기 value를 보관해요.\nCounter counter = new Counter();\n// 호출할 때마다 같은 객체의 값이 늘어요.\ncounter.add();\ncounter.add();\ncounter.add();\nSystem.out.println(counter.value);",
[("", "3\n")], "Counter의 add() 안에 value++;를 적으세요.", "호출마다 새 객체를 만들면 값이 쌓이지 않아요. 같은 객체를 사용하세요.",
"Counter 객체를 두 개 만들면 일반 인스턴스 필드 value는 어떻게 될까요?", ["각 객체가 따로 보관해요", "항상 같은 값을 공유해요", "필드를 읽을 수 없어요", "자동으로 3이 돼요"],
"인스턴스 필드는 객체마다 따로 있어요.\n다른 보기는 왜 아닌가요?\nstatic 필드와는 다르게 공유하지 않아요.\n이 예제의 필드는 읽을 수 있어요.\n자동으로 메서드를 호출하지는 않아요.",
extra="    // static 중첩 클래스로 한 파일에서 연습해요.\n    static class Counter {\n        int value = 0;\n        // 이 객체의 필드만 바꿔요.\n        void add() {\n            value++;\n        }\n    }\n",
stage=program("// 처음 값은 0이에요.\nCounter counter = new Counter();\nSystem.out.println(counter.value);", "    static class Counter {\n        int value = 0;\n    }\n"))

lesson("도전: 점수 요약하기",
"지금까지 배운 입력과 반복을 함께 사용해요.\n필요한 값을 읽고 합과 개수를 구해요.\n조건문으로 합격인지 판단해 볼까요?\n\n예상 출력의 줄 순서도 답의 일부예요.\n값이 맞아도 안내 글을 추가하면 실패해요.\n한 명뿐인 입력과 경계 점수도 확인하세요.\n여러 입력이 모두 통과해야 미션을 클리어해요.",
"// 평균을 소수로 계산하려면 실수로 나눠요.\nint sum = 121;\nint count = 2;\nSystem.out.println((double) sum / count);", "60.5\n",
"int 값을 double로 바꾸는 형 변환 표현은 무엇인가요?", ["(double)"],
"첫 입력 n은 학생 수예요. 1부터 10이에요.\n이어서 0부터 100까지의 점수 n개가 와요.\n첫 줄은 점수 합, 둘째 줄은 60점 이상 인원이에요.\n셋째 줄은 정수 평균이에요. 소수 부분은 버려요.\n배열에 점수를 저장한 뒤 요약하세요.",
'// 학생 수만큼 배열을 준비해요.\nvar scanner = new java.util.Scanner(System.in, "UTF-8");\nint n = scanner.nextInt();\nint[] scores = new int[n];\nfor (int i = 0; i < n; i++) {\n    scores[i] = scanner.nextInt();\n}\n// 합과 합격 인원을 각각 누적해요.\nint sum = 0;\nint passed = 0;\nfor (int score : scores) {\n    sum += score;\n    if (score >= 60) {\n        passed++;\n    }\n}\n// 정수 나눗셈으로 소수 부분을 버려요.\nSystem.out.println(sum);\nSystem.out.println(passed);\nSystem.out.println(sum / n);',
[("3 50 60 100\n", "210\n2\n70\n"), ("1 0\n", "0\n0\n0\n"), ("2 60 61\n", "121\n2\n60\n"), ("4 0 59 60 100\n", "219\n2\n54\n")], "sum과 passed를 반복 전에 0으로 준비하세요.", "평균만 실수로 출력하면 이 문제의 조건과 달라져요. 정수 평균을 출력하세요.",
"합격 인원에 포함해야 하는 점수는 무엇인가요?", ["60", "59", "50", "0"],
"60 이상이므로 60도 포함해요.\n다른 보기는 왜 아닌가요?\n59, 50, 0은 모두 60보다 작아요.")


strengthen(LESSONS, program)


def question(qid, prompt, accepted, explanation):
    return dict(id=qid, type="short_answer", prompt=prompt, accepted=accepted, explanation=explanation)


def build():
    course = dict(id="immersion-quest-3-java25-v1", title="자바 기초 · JDK 25",
        description="출력부터 객체까지 직접 실행해요. 개념 확인 · 코딩 문제 · 복습 퀴즈로 자바의 첫걸음을 익혀요.", chapters=[])
    titles = ["1. 자바의 첫걸음", "2. 조건과 반복", "3. 값을 묶고 동작 나누기"]
    for c, title in enumerate(titles):
        course["chapters"].append(dict(id=f"java25-ch{c+1}", title=title, units=[]))
    sources = {}
    for i, item in enumerate(LESSONS):
        uid = f"java25-{i+1:02}"
        cid = uid + "-concept"
        pid = uid + "-code"
        qid = uid + "-quiz"
        example_code = item["stage"]
        body = item["body"] + "\n\n### 실행 예제\n\n```java\n" + example_code + "```\n\n예상 출력:\n\n```text\n" + item["example_output"] + "```"
        if i == 3:
            body += "\n\n이 예제의 입력은 `4 6`이에요."
        tests = [dict(input=a, expected=b) for a, b in item["cases"]]
        problem = dict(id=pid, title="직접 풀기 · " + item["title"], language="java", revision=2 if i in (8, 10, 11) else 1,
            content="### 목표\n\n" + item["goal"] + "\n\n### 힌트\n\n" + item["hint"],
            starter_code=program("// 이곳에 코드를 적으세요."), tests=tests, solution=item["solution"],
            prompt=f"JDK 25에서 Main.java 한 파일로 풀어줘. preview 기능 없이.\n{item['goal']}\n코드만 줘.")
        if item.get("checker"):
            problem["checker"] = item["checker"]
        # Two complete runnable states keep Java braces valid during the explanation.
        code_actions = [dict(action="say", target="problem", text=item["goal"]),
            dict(action="set_code", code=example_code, say="먼저 작은 예제를 실행해 볼게요."),
            dict(action="run"), dict(action="say", target="output", text="예제 출력은 " + item["example_output"].strip().replace("\n", ", ") + "예요."),
            dict(action="say", target="editor", text=item["caution"]),
            dict(action="set_code", code=item["solution"], say="이제 문제의 입력과 출력에 맞춰 확장해요."),
            dict(action="run"), dict(action="say", target="output", text="첫 예제의 결과는 " + tests[0]["expected"].strip().replace("\n", ", ") + "예요."),
            dict(action="submit", say="다른 입력도 통과하는지 제출해요.")]
        # The input lesson's example and the task both use the first test's input.
        concept_check = question("check", item["check"], item["accepted"], "정답은 " + item["accepted"][0] + "예요.\n본문의 예제에서 같은 표현을 찾아보세요.")
        shift = i % len(item["options"])
        options = item["options"][shift:] + item["options"][:shift]
        correct = (-shift) % len(options)
        review = item.get("review", (item["check"], item["accepted"], concept_check["explanation"]))
        quiz = [dict(id="choice", type="choice", prompt=item["quiz"], options=options, correct=correct, explanation=item["explanation"]),
            question("recall", *review)]
        if i in (8, 10, 11):
            code_actions = progressive(problem, item["caution"])
        activities = [dict(id=cid, title="개념 · " + item["title"], kind="concept", body=body, check=concept_check,
                narration=[dict(action="say", target="title", text=item["body"].split("\n\n")[0]),
                    dict(action="say", target="check", text=concept_check["explanation"]), dict(action="answer_quiz", answers={"1": item["accepted"][0]})]),
            dict(id=pid, title=problem["title"], kind="coding", problem=problem, narration=code_actions, challenge=i == 11),
            dict(id=qid, title="복습 · " + item["title"], kind="quiz", questions=quiz,
                narration=[dict(action="say", target="quiz", text=item["explanation"] + "\n" + review[2]), dict(action="answer_quiz", answers={"1": str(correct + 1), "2": review[1][0]})])]
        for practice in item.get("practices", []):
            practice_id = uid + "-code-" + practice["suffix"]
            p = dict(id=practice_id, title="직접 풀기 · " + practice["title"], language="java", revision=1,
                content=practice["body"] + "\n\n### 목표\n\n" + practice["goal"] + "\n\n### 힌트\n\n" + practice["hint"],
                starter_code=program("// 이곳에 코드를 적으세요."),
                solution=practice["solution"], checker=practice["checker"],
                tests=[dict(input=a, expected=b) for a,b in practice["cases"]])
            activities.insert(-1, dict(id=practice_id, title=p["title"], kind="coding", problem=p,
                narration=progressive(p, practice["caution"])))
        for activity in activities:
            activity["tour"] = [item["body"].splitlines()[0]]
        course["chapters"][i // 4]["units"].append(dict(id=uid, title=f"{i//4+1}-{i%4+1} {item['title']}", activities=activities))
        sources[uid] = hashlib.sha256(json.dumps(item, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    (ROOT / "courses/java-basics.json").write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "courses/java-basics.sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
    return course


def execute(code, input_text):
    java = os.environ.get("MOLIP_JAVA") or (str(Path(os.environ["JAVA_HOME"]) / "bin" / ("java.exe" if os.name == "nt" else "java")) if os.environ.get("JAVA_HOME") else "java")
    clean_env = {k: v for k, v in os.environ.items() if k not in ("JDK_JAVA_OPTIONS", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS")}
    with tempfile.TemporaryDirectory() as directory:
        Path(directory, "Main.java").write_text(code, encoding="utf-8")
        result = subprocess.run([java, "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "--source", "25", "Main.java"], input=input_text, text=True, encoding="utf-8", capture_output=True, cwd=directory, timeout=20, env=clean_env)
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout


def progressive(problem, caution):
    """Keep braces valid while adding a small completed statement to main."""
    cache_path = ROOT / "tools/java_course/narration_cache" / (problem["id"] + ".json")
    source_hash = hashlib.sha256(json.dumps([problem, caution], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached["hash"] == source_hash:
            return cached["actions"]
    source = problem["solution"]
    start = source.index("    public static void main(String[] args) {\n") + len("    public static void main(String[] args) {\n")
    end = source.index("\n    }", start)
    lines = source[start:end].splitlines(keepends=True)
    prefix, depth, stages = "", 0, []
    for line in lines:
        prefix += line
        if not line.strip().startswith("//"):
            depth += line.count("{") - line.count("}")
        if depth == 0 and line.strip() and not line.strip().startswith("//"):
            stages.append(source[:start] + prefix.rstrip("\n") + source[end:])
    actions = [dict(action="say", target="problem", text=problem["content"]),
        dict(action="set_code", code=source[:start] + source[end:], say="바깥 구조와 메서드를 먼저 준비해요.")]
    previous = source[:start] + source[end:]
    for stage in stages:
        # Use a stable whole-prefix anchor, retaining the rest of the file.
        common = 0
        while common < min(len(previous), len(stage)) and previous[common] == stage[common]:
            common += 1
        tail = 0
        while tail < min(len(previous)-common, len(stage)-common) and previous[-tail-1] == stage[-tail-1]:
            tail += 1
        left = previous[:common].rfind("\n") + 1
        right = len(previous)-tail
        right = previous.find("\n", right) + 1 if previous.find("\n", right) >= 0 else len(previous)
        new_right = len(stage) - (len(previous)-right)
        before, after = previous[left:right], stage[left:new_right]
        if previous.count(before) != 1:
            left = 0
            before, after = previous[:right], stage[:new_right]
        output = execute(stage, problem["tests"][0]["input"])
        actions += [dict(action="patch_code", before=before, after=after, say=after.strip().splitlines()[0].replace("//", "").strip()),
            dict(action="run"), dict(action="say", target="output", text=("출력은 " + output.strip().replace("\n", ", ") + "예요.") if output else "아직 출력은 없어요. 값을 준비한 단계예요.")]
        previous = stage
    assert previous == source
    actions += [dict(action="say", target="editor", text=caution + " 조심하세요."), dict(action="submit", say="다른 입력도 확인해요.")]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(dict(hash=source_hash, by="hand", actions=actions), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return actions


def verify():
    java = os.environ.get("MOLIP_JAVA") or (str(Path(os.environ["JAVA_HOME"]) / "bin" / ("java.exe" if os.name == "nt" else "java")) if os.environ.get("JAVA_HOME") else "java")
    version = subprocess.run([java, "--version"], text=True, encoding="utf-8", capture_output=True, timeout=10, check=True).stdout
    tokens = version.split()
    assert tokens[0] in ("openjdk", "java") and tokens[1].split(".")[0].split("-")[0] == "25", "JDK 25 is required"
    print(version.splitlines()[0])
    count = 0
    for i, item in enumerate(LESSONS):
        example_input = "4 6\n" if i == 3 else ""
        assert execute(item["stage"], example_input) == item["example_output"], item["title"]
        for input_text, expected in item["cases"]:
            assert execute(item["solution"], input_text) == expected, item["title"]
            count += 1
        for practice in item.get("practices", []):
            for input_text, expected in practice["cases"]:
                assert execute(practice["solution"], input_text) == expected, practice["title"]
                count += 1
    print(f"JDK 25 verified: {len(LESSONS)} runnable examples, {count} answer cases; no preview flags")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    build()
    if args.verify:
        verify()
    print("Built 3 chapters, 12 units, 39 missions, 15 coding practices, 24 quiz questions")
