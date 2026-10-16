from .common import lesson,java,task,code,ROOT
import json

def build():
    src=['https://slog.gg/p/14145','https://slog.gg/p/14156']
    lesson('principles-wise-app','명언 앱 · 상태와 요청을 연결해요','목록·식별자·수정·삭제·요청 해석을 준비된 작은 앱에서 익혀요.',src,[
      java('stable-id','목록 위치와 ID는 달라요','삭제하면 목록의 위치가 바뀔 수 있어요.\nID는 항목을 계속 구분하는 이름이에요.',
       'ID로 찾도록 조건의 `i`를 `ids[i]`로 바꿔요.','static String run(int id)',
       '// 첫 명언이 삭제된 뒤의 목록이에요.\nint[] ids={2,4}; String[] texts={"keep","try"};\nfor(int i=0;i<ids.length;i++) if(i==id)return texts[i];\n// 없는 ID는 실패로 알려줘요.\nreturn "missing";',
       'if(i==id)','if(ids[i]==id)','Exercise.run(in.nextInt())',[('2','keep'),('4','try'),('0','missing')]),
      java('append','등록할 때 이전 항목을 지우면 안 돼요','등록은 기존 목록 뒤에 항목을 더해요.\n초기화와 추가는 다른 일이에요.',
       '`quotes.clear()` 한 곳을 `quotes.add(text)`로 바꿔요.','static String run(String text)',
       '// 이미 등록한 명언이 있어요.\nvar quotes=new java.util.ArrayList<>(java.util.List.of("start"));\nquotes.clear();\n// 등록 뒤 전체 상태를 확인해요.\nreturn quotes.toString();',
       'quotes.clear()','quotes.add(text)','Exercise.run(in.nextLine())',[('next','[start, next]'),('again','[start, again]')]),
      java('update','수정은 기존 위치를 유지해요','수정은 같은 항목의 내용만 바꾸는 작업이에요.\n추가하면 항목 수가 늘어요.',
       '`add` 한 곳을 `set`으로 바꿔요.','static String run(String text)',
       '// 두 번째 항목만 수정할 거예요.\nvar quotes=new java.util.ArrayList<>(java.util.List.of("a","b"));\nquotes.add(1,text);\n// 위치와 개수를 함께 확인해요.\nreturn quotes.toString();',
       'quotes.add(1,text)','quotes.set(1,text)','Exercise.run(in.nextLine())',[('new','[a, new]'),('keep','[a, keep]')]),
      java('delete-id','삭제 대상만 골라요','삭제할 항목의 조건이 반대면 나머지를 지워요.\n지운 뒤의 목록을 꼭 확인해요.',
       '지정한 ID만 삭제하도록 조건을 고쳐요.','static String run(int id)',
       '// ID는 목록 위치와 다르게 유지해요.\nvar ids=new java.util.ArrayList<>(java.util.List.of(1,3,5));\nids.removeIf(value->value!=id);\n// 나머지 항목은 그대로 남아야 해요.\nreturn ids.toString();',
       'value!=id','value==id','Exercise.run(in.nextInt())',[('3','[1, 5]'),('9','[1, 3, 5]'),('1','[3, 5]')]),
      java('query-value','구분자를 전부 나누면 값이 깨져요','요청의 첫 등호만 이름과 값을 구분해요.\n값 안에도 등호가 있을 수 있어요.',
       '`split`에 최대 조각 수 2를 지정해요.','static String run(String query)',
       '// 앞은 이름이고 나머지는 값이에요.\nString[] pair=query.split("=");\nreturn pair.length<2?"":pair[1];',
       'query.split("=")','query.split("=",2)','Exercise.run(in.nextLine())',[('text=a=b','a=b'),('id=3','3'),('id=','')]),
      java('persist','메모리와 파일의 값은 달라요','저장은 다음 실행에서도 읽기 위해 해요.\n읽을 때는 파일에 남은 값을 가져와요.',
       '파일을 다시 읽도록 return 한 줄을 고쳐요.','static String run(String text) throws Exception',
       '// 파일에 저장한 뒤 메모리의 값을 바꿔요.\nvar path=java.nio.file.Path.of("quote.txt");\njava.nio.file.Files.writeString(path,text);\n// 메모리의 새 값과 파일은 독립이에요.\ntext="changed";\nreturn text;',
       'return text;','return java.nio.file.Files.readString(path);','Exercise.run(in.nextLine())',[('remember','remember'),('persist','persist')]),
      java('latest-first','최신 명언만 골라 보세요','조회는 저장 순서와 다른 순서로 보여줄 수 있어요.',
       '입력 ID들 중 3 이상만 내림차순으로 보여줘요.\n중복 ID도 결과에는 한 번만 나와야 해요.',
       'static String run(String text)',
       '// 조회할 때 필요한 규칙을 조합해요.\nvar ids=java.util.Arrays.stream(text.split(",")).map(Integer::valueOf);\nreturn ids.toList().toString();',
       'ids.toList()','ids.filter(id->id>=3).distinct().sorted(java.util.Comparator.reverseOrder()).toList()',
       'Exercise.run(in.nextLine())',[('2,5,3,5,1','[5, 3]'),('1,2','[]'),('4,3,9','[9, 4, 3]')],challenge=True,hints=['filter, distinct, sorted의 역할을 나눠 생각해요.','내림차순 정렬에는 reverseOrder를 쓸 수 있어요.']),
    ])
    lesson('principles-tdd','TDD · 실패를 만드는 테스트','틀린 기대값, 놓친 경계값, 결함 탐지를 실제 JUnit으로 확인해요.',src,[
      task('red-green','실패한 이유를 먼저 읽어요','테스트는 기대값과 실제값을 비교해요.\n실패했다고 구현이 항상 틀린 건 아니에요.',
       '실행해 실패 이유를 보세요.\n2+3의 기대값 한 곳을 올바르게 고쳐요.',
       '''
       import org.junit.jupiter.api.Test;
       import static org.junit.jupiter.api.Assertions.*;
       class ExerciseTest {
           // 작은 입력으로 기대한 계산을 확인해요.
           @Test void sum() { assertEquals(6,Calc.add(2,3)); }
       }
       ''','assertEquals(6,','assertEquals(5,',language='junit',files={'Calc.java':'class Calc {static int add(int a,int b){return a+b;}}'}),
      task('kill-mutant','초록색인데 결함을 놓쳤어요','0+0만 검사하면 빼기로 구현해도 통과해요.\n다른 구현을 구분하는 입력이 필요해요.',
       '0+0 대신 2+3을 검사하세요.\n덧셈을 뺄셈으로 바꾼 결함도 잡아야 해요.',
       '''
       import org.junit.jupiter.api.Test;
       import static org.junit.jupiter.api.Assertions.*;
       class ExerciseTest {
           // 서로 다른 동작을 구분할 입력이 필요해요.
           @Test void sum() { assertEquals(0,Calc.add(0,0)); }
       }
       ''','assertEquals(0,Calc.add(0,0))','assertEquals(5,Calc.add(2,3))',language='junit',files={'Calc.java':'class Calc {static int add(int a,int b){return a+b;}}'}),
      task('boundary-test','경계값을 테스트로 남겨요','규칙이 바뀌는 경계에서 오류가 자주 드러나요.\n규칙을 테스트로 기록해 두세요.',
       '18세가 성인인지 검사하세요.\n20세만 검사하는 테스트를 고쳐요.',
       '''
       import org.junit.jupiter.api.Test;
       import static org.junit.jupiter.api.Assertions.*;
       class ExerciseTest {
           // 성인이 시작되는 경계도 확인해야 해요.
           @Test void adult() { assertTrue(Rule.adult(20)); }
       }
       ''','Rule.adult(20)','Rule.adult(18)',language='junit',files={'Rule.java':'class Rule {static boolean adult(int age){return age>=18;}}'}),
      task('two-boundaries','통과와 거절을 함께 증명해요','통과 사례만으로는 항상 true인 구현을 못 잡아요.',
       '18세는 통과, 17세는 거절하는 테스트를 만드세요.\n항상 true인 구현과 경계가 틀린 구현을 구분해요.',
       '''
       import org.junit.jupiter.api.Test;
       import static org.junit.jupiter.api.Assertions.*;
       class ExerciseTest {
           // 규칙의 양쪽을 검사할 자리에요.
           @Test void boundary() { assertTrue(Rule.adult(20)); }
       }
       ''','assertTrue(Rule.adult(20));','assertTrue(Rule.adult(18)); assertFalse(Rule.adult(17));',language='junit',files={'Rule.java':'class Rule {static boolean adult(int age){return age>=18;}}'},challenge=True,
       hints=['경계에 포함되는 값과 바로 아래 값을 함께 골라요.','참이어야 할 때와 거짓이어야 할 때를 별도로 검사해요.']),
    ])
    # Mutations are assessed by the player's real JUnit runner after normal tests pass.
    for t in __import__('principles_course.common',fromlist=['LESSONS']).LESSONS[-1]['tasks']:
        if t['id']=='kill-mutant':t['mutations']=[{'Calc.java':'class Calc {static int add(int a,int b){return a-b;}}'}]
        if t['id']=='boundary-test':t['mutations']=[{'Rule.java':'class Rule {static boolean adult(int age){return age>18;}}'}]
        if t['id']=='two-boundaries':t['mutations']=[{'Rule.java':'class Rule {static boolean adult(int age){return true;}}'},{'Rule.java':'class Rule {static boolean adult(int age){return age>18;}}'}]
    calculator()

PARSER=code('''
class Parser {
    // 바깥 괄호만 벗겨요. 안쪽 괄호의 구조는 유지해요.
    static int parse(String source) {
        String s=source.replace(" ","");
        while(s.startsWith("(")&&matchingOuter(s)) s=s.substring(1,s.length()-1);
        // 우선순위가 낮은 연산을 먼저 분할해 재귀로 내려가요.
        int at=find(s,"+-");
        if(at<0)at=find(s,"*");
        if(at>=0)return Exercise.apply(s.charAt(at),parse(s.substring(0,at)),parse(s.substring(at+1)));
        // 단항 음수는 왼쪽 피연산자가 없어요.
        if(s.startsWith("-"))return -parse(s.substring(1));
        return Integer.parseInt(s);
    }
    static boolean matchingOuter(String s) {
        int depth=0;
        for(int i=0;i<s.length();i++) {
            if(s.charAt(i)=='(')depth++; if(s.charAt(i)==')')depth--;
            if(depth==0&&i<s.length()-1)return false;
        }
        return depth==0;
    }
    static int find(String s,String operators) {
        int depth=0;
        // 오른쪽부터 나눠야 연속 뺄셈이 왼쪽부터 계산돼요.
        for(int i=s.length()-1;i>=0;i--) {
            char c=s.charAt(i);
            if(c==')')depth++; if(c=='(')depth--;
            boolean binary=i>0&&"+-*(".indexOf(s.charAt(i-1))<0;
            if(depth==0&&binary&&operators.indexOf(c)>=0)return i;
        }
        return -1;
    }
}
''')

def calculator():
    source=['https://slog.gg/p/14151']
    main='class Main {public static void main(String[] a){System.out.println(Parser.parse(new java.util.Scanner(System.in).nextLine()));}}'
    def calc(id,title,principle,goal,body,before,after,cases,**kw):
        return task(id,title,principle,goal,'class Exercise {\n    // 연산자는 파서가 분리해서 전달해요.\n    static int apply(char op,int left,int right) {\n'+body+'\n    }\n}\n',before,after,files={'Parser.java':PARSER,'Main.java':main},tests=cases,**kw)
    lesson('principles-calculator','계산기 · 분해와 재귀의 원리','준비된 파서의 작은 연산 규칙을 완성해요. 마지막 도전은 원문 28사례를 모두 검사해요.',source,[
      calc('plus','분해한 두 값의 결과를 돌려줘요','파서는 식을 작은 부분으로 나눠요.\n연산 메서드는 두 결과를 합쳐요.',
           '덧셈이 되도록 반환값을 고쳐요.','        // 지금 받은 두 값만 계산해요.\n        return left;',
           'return left;','return left+right;',[('2 + 3','5'),('10 + 7','17'),('1 + 2 + 4','7')]),
      calc('minus','뺄셈은 왼쪽과 오른쪽이 달라요','덧셈과 달리 피연산자 순서가 중요해요.',
           '빼기의 방향을 고쳐요.','        // 연산 기호에 따라 규칙을 고르게 해요.\n        if(op==\'-\')return right-left;\n        return left+right;',
           'return right-left;','return left-right;',[('10 - 3','7'),('3 - 8','-5'),('10 - 3 - 2','5')]),
      calc('multiply','우선순위는 분해 순서에서 나와요','곱셈을 포함한 작은 식부터 계산한 뒤 더해요.',
           '곱셈 분기의 반환값을 고쳐요.','        // 덧셈보다 안쪽에서 곱셈이 계산돼요.\n        if(op==\'*\')return left+right;\n        if(op==\'-\')return left-right;\n        // 나머지 기호는 더하기예요.\n        return left+right;',
           "if(op=='*')return left+right;","if(op=='*')return left*right;",[('2 + 3 * 4','14'),('(2 + 3) * 4','20'),('2 * -3','-6')]),
      calc('all-rules','중첩된 식 28개에 도전해요','괄호와 단항 음수도 재귀로 작은 식이 돼요.',
           '덧셈·뺄셈·곱셈의 규칙을 모두 완성하세요.\n원문 28사례와 추가 입력을 검사해요.\n파서의 find와 parse도 함께 읽어 보세요.',
           '        // 분해된 두 값을 어떤 규칙으로 합칠까요?\n        return left;',
           'return left;',"if(op=='*')return left*right;\n        if(op=='-')return left-right;\n        return left+right;",
           [(c['input'],str(c['expected'])) for c in json.loads((ROOT/'.scratch/repo-curriculum/sources/arithmetic-cases.json').read_text(encoding='utf8'))]+[('-(-(2 + 3)) * 4','20'),('7 - 2 * (3 - 8)','17')],challenge=True,
           hints=['분해 순서와 실제 연산의 규칙은 역할이 달라요.','각 op가 들어올 때 돌려줄 결과를 따로 생각해요.']),
    ])
