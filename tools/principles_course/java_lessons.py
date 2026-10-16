from .common import java,task,lesson,code
S=['https://slog.gg/p/14146']

def build():
    lesson('principles-java-values','자바 · 값과 이름의 관계','변수·자료형·대입·계산을 작은 변경으로 확인해요.',S,[
      java('use-values','숫자를 바꿔도 계산되게 해요','변수에는 이번 입력의 값이 들어가요.\n정답 숫자를 적으면 입력이 바뀔 때 틀려요.',
       'return 뒤를 `price * count`로 바꾸세요.','static int run(int price, int count)','// 입력을 이용해 계산할 자리에요.\nreturn 600;', 'return 600;','return price * count;','Exercise.run(in.nextInt(),in.nextInt())',[('200 3','600'),('150 4','600'),('70 5','350')]),
      java('assignment','오른쪽 계산 뒤에 왼쪽을 바꿔요','대입은 양쪽이 같다는 뜻이 아니에요.\n오른쪽 값을 계산해 왼쪽에 저장해요.',
       '`amount = 1`을 `amount = amount + 1`로 바꿔요.','static int run(int amount)','// 지금 값에 하나를 더해야 해요.\namount = 1;\nreturn amount;', 'amount = 1;','amount = amount + 1;','Exercise.run(in.nextInt())',[('5','6'),('0','1'),('-2','-1')]),
      java('decimal-before','나눈 뒤 소수로 바꾸면 늦어요','정수 나눗셈은 소수 부분을 먼저 버려요.\n나누기 전에 한쪽을 소수로 바꿔야 해요.',
       '`total / count`를 `(double) total / count`로 바꿔요.','static double run(int total,int count)','// 나누기 전에 자료형을 정해요.\nreturn total / count;', 'total / count','(double) total / count','Exercise.run(in.nextInt(),in.nextInt())',[('7 2','3.5'),('10 4','2.5'),('0 3','0.0')]),
      java('remainder','남는 묶음을 세어 보세요','나머지는 같은 크기로 묶고 남은 양이에요.\n몫과 나머지를 구분해요.',
       '`/` 한 곳을 `%`로 바꿔요.','static int run(int count,int size)','// 묶지 못한 양을 반환해요.\nreturn count / size;','count / size','count % size','Exercise.run(in.nextInt(),in.nextInt())',[('17 5','2'),('20 4','0'),('3 7','3')]),
      java('pack-boxes','빈칸이 있어도 상자는 필요해요','나머지가 있으면 상자가 하나 더 필요해요.\n앞의 몫과 나머지를 조합해 보세요.',
       '물건 개수와 상자 크기를 받아 필요한 상자 수를 구해요.\n물건은 0개 이상, 상자 크기는 1 이상이에요.',
       'static int run(int count,int size)','// 남는 물건도 상자에 담아야 해요.\nreturn count / size;',
       'return count / size;','return (count + size - 1) / size;','Exercise.run(in.nextInt(),in.nextInt())',[('10 4','3'),('8 4','2'),('0 4','0'),('1 8','1')],challenge=True,hints=['정확히 나누어떨어질 때는 상자를 더하면 안 돼요.','나누기 전에 size - 1을 더하는 방법도 있어요.']),
    ])
    lesson('principles-java-control','자바 · 조건과 반복을 추적해요','경계값·반복 범위·누적·종료를 확인하고 작은 규칙을 조합해요.',S,[
      java('boundary','경계값 한 개를 놓쳤어요','크다와 크거나 같다는 경계에서 달라요.\n조건의 양쪽을 확인해요.',
       '18세도 true가 되도록 비교 한 곳을 바꿔요.','static boolean run(int age)','// 경계값도 검사해야 해요.\nreturn age > 18;', 'age > 18','age >= 18','Exercise.run(in.nextInt())',[('17','false'),('18','true'),('19','true')]),
      java('both-conditions','두 조건이 모두 필요해요','또는은 하나만 맞아도 통과해요.\n둘 다 필요하면 그리고를 써야 해요.',
       '점수 60 이상이고 출석 80 이상이어야 해요.\n`||`를 `&&`로 바꿔요.','static boolean run(int score,int attendance)',
       '// 두 조건을 함께 확인해요.\nreturn score >= 60 || attendance >= 80;','||','&&','Exercise.run(in.nextInt(),in.nextInt())',[('60 80','true'),('59 99','false'),('99 79','false')]),
      java('loop-end','마지막 숫자도 더해요','반복 조건은 매번 실행 전에 검사해요.\n마지막 값을 포함할지 직접 정해요.',
       '1부터 n까지 더하도록 `<`를 `<=`로 바꿔요.','static int run(int n)',
       '// 합계는 반복 밖에서 유지해요.\nint sum=0;\nfor(int i=1;i<n;i++) sum+=i;\n// 반복이 끝나면 누적값을 반환해요.\nreturn sum;',
       'i<n','i<=n','Exercise.run(in.nextInt())',[('1','1'),('5','15'),('0','0')]),
      java('sum-not-replace','누적은 이전 값을 기억해요','대입만 하면 앞에서 계산한 값을 잃어요.\n누적은 이전 합계에 값을 더해요.',
       '`sum=i`를 `sum+=i`로 바꿔요.','static int run(int n)',
       '// sum은 반복할 때마다 이어져요.\nint sum=0;\nfor(int i=1;i<=n;i++) sum=i;\n// 마지막 숫자와 합계는 달라요.\nreturn sum;',
       'sum=i','sum+=i','Exercise.run(in.nextInt())',[('4','10'),('2','3'),('0','0')]),
      java('even-sum','짝수만 골라 더해 보세요','반복 안에 조건을 넣어 대상을 고를 수 있어요.',
       '1부터 n까지 짝수의 합을 구해요.\n조건과 나머지 연산을 조합하세요.',
       'static int run(int n)','// 합계는 처음에 한 번만 준비해요.\nint sum=0;\nfor(int i=1;i<=n;i++) sum+=i;\n// 고른 값의 합계를 반환해요.\nreturn sum;',
       'sum+=i','if(i%2==0) sum+=i','Exercise.run(in.nextInt())',[('6','12'),('5','6'),('1','0')],challenge=True,hints=['짝수는 2로 나눈 나머지가 0이에요.','더하는 줄 앞에 if 조건을 붙일 수 있어요.']),
    ])
    array_call='Arrays.stream(in.nextLine().split(",")).mapToInt(Integer::parseInt).toArray()'
    lesson('principles-java-arrays','자바 · 배열과 메서드로 나눠요','인덱스·참조·복사·반환을 배열 실험으로 구분해요.',S,[
      java('last-index','마지막 자리는 길이와 달라요','배열의 첫 인덱스는 0이에요.\n마지막 인덱스는 길이보다 하나 작아요.',
       '마지막 값을 읽도록 인덱스 한 곳을 고쳐요.','static int run(int[] values)','// 길이는 개수, 인덱스는 자리예요.\nreturn values[values.length];',
       'values[values.length]','values[values.length-1]',f'Exercise.run({array_call})',[('2,4,9','9'),('7','7'),('-1,0','0')]),
      java('method-return','화면 출력과 반환은 달라요','반환값은 호출한 곳에서 다시 쓸 수 있어요.\n출력했다고 값이 반환되지는 않아요.',
       '두 수의 큰 값을 반환하도록 return을 고쳐요.','static int run(int a,int b)','// 호출한 쪽에서 결과를 사용해요.\nreturn a;',
       'return a;','return a>b?a:b;','Exercise.run(in.nextInt(),in.nextInt())',[('2 7','7'),('9 3','9'),('-4 -2','-2')]),
      java('copy-array','이름만 새로 만들면 같은 배열이에요','배열을 대입하면 같은 배열을 가리켜요.\n따로 바꾸려면 배열 자체를 복사해요.',
       '`copy=values`를 `copy=values.clone()`으로 바꿔요.\n원본 첫 값이 보존되는지 확인해요.','static int run(int[] values)',
       '// 바꿀 배열은 따로 준비해야 해요.\nint[] copy=values;\ncopy[0]=999;\n// 원본 값을 꺼내 두 배열을 비교해요.\nreturn values[0];',
       'copy=values','copy=values.clone()',f'Exercise.run({array_call})',[('3,5','3'),('-1,4','-1'),('8','8')]),
      java('max-array','가장 큰 값을 찾아보세요','초기값도 입력의 일부여야 해요.\n양수에서만 맞는 답을 피하세요.',
       '빈 배열은 오지 않아요. 모든 원소의 최댓값을 구해요.\n음수만 있는 입력도 확인하세요.','static int run(int[] values)',
       '// 처음 후보를 고르고 하나씩 비교해요.\nint best=0;\nfor(int value:values) if(value>best) best=value;\n// 가장 큰 후보를 반환해요.\nreturn best;',
       'int best=0;','int best=values[0];',f'Exercise.run({array_call})',[('-8,-3,-9','-3'),('1,5,2','5'),('-7','-7')],challenge=True,hints=['0은 배열 안에 없을 수도 있어요.','첫 원소를 최초 후보로 삼아 보세요.']),
    ])
    lesson('principles-java-objects','자바 · 객체마다 다른 상태','인스턴스·캡슐화·동적 호출을 작은 객체로 비교해요.',S,[
      task('instance-state','두 객체가 값을 나눠 쓰고 있어요','static 필드는 클래스가 함께 써요.\n객체별 상태는 인스턴스 필드에 둬요.',
       'Counter의 static 한 곳을 지우세요.\n새 객체의 시작값은 0이어야 해요.',
       '''
       class Counter {
           // 이 값은 객체마다 따로 있어야 해요.
           static int value;
           void add(int n) { value+=n; }
       }
       class Exercise {
           // 첫 객체만 바꾼 뒤 새 객체를 확인해요.
           static int run(int n) {
               Counter first=new Counter(); first.add(n);
               return new Counter().value;
           }
       }
       ''','static int value;','int value;',files={'Main.java':'class Main {public static void main(String[] a){System.out.println(Exercise.run(new java.util.Scanner(System.in).nextInt()));}}'},tests=[('7','0'),('3','0')]),
      task('protect-state','잔액이 음수가 되지 않게 해요','상태를 바꾸는 메서드가 규칙을 지켜요.\n호출한 쪽에서 매번 확인하지 않아도 돼요.',
       '잔액이 부족하거나 amount가 음수이면 거절해요.\n조건 한 줄을 고쳐 보세요.',
       '''
       class Exercise {
           // 외부에서 잔액을 직접 바꾸지 못하게 해요.
           private int balance=100;
           boolean withdraw(int amount) {
               // 이 조건이 상태의 규칙을 지켜요.
               if(amount<0) return false;
               balance-=amount;
               return true;
           }
           // 검사에서 현재 상태를 확인해요.
           int balance(){return balance;}
       }
       ''','if(amount<0)','if(amount<0 || amount>balance)',files={'Main.java':'class Main {public static void main(String[] a){Exercise e=new Exercise();boolean ok=e.withdraw(new java.util.Scanner(System.in).nextInt());System.out.println(ok+":"+e.balance());}}'},tests=[('30','true:70'),('120','false:100'),('-5','false:100')]),
      task('dispatch','같은 호출인데 동작이 달라요','실행할 메서드는 실제 객체에 따라 달라져요.\n부모 타입으로도 자식의 동작을 쓸 수 있어요.',
       'Animal 대신 Dog 객체를 만들어 보세요.\n호출 코드는 그대로 두세요.',
       '''
       class Animal { String sound(){return "quiet";} }
       class Dog extends Animal {
           // 부모와 같은 메서드를 새 동작으로 정의해요.
           @Override String sound(){return "bark";}
       }
       class Exercise {
           static String run() {
               // 변수 타입과 실제 객체 타입을 비교해요.
               Animal animal=new Animal();
               return animal.sound();
           }
       }
       ''','new Animal()','new Dog()',files={'Main.java':'class Main {public static void main(String[] a){System.out.println(Exercise.run());}}'},tests=[('','bark')]),
      java('recursive-step','종료 조건과 작은 문제','재귀는 같은 일을 더 작은 입력으로 불러요.\n끝나는 조건과 입력 감소가 둘 다 필요해요.',
       '0부터 n까지의 합을 재귀로 구해요.\nn은 0 이상 100 이하예요.','static int run(int n)',
       '// 0에서는 더 부르지 않아요.\nif(n==0)return 0;\n// 현재 값과 더 작은 문제의 답을 합쳐요.\nreturn n;',
       'return n;','return n+run(n-1);','Exercise.run(in.nextInt())',[('0','0'),('1','1'),('6','21')],challenge=True,hints=['n을 더한 뒤 0부터 n-1의 합이 남아요.','같은 메서드를 n-1로 불러 보세요.']),
    ])
    lesson('principles-java-streams','자바 · 모음에서 필요한 값을 찾아요','List·Map·Stream의 변화와 평가 순서를 관찰해요.',S+['https://slog.gg/p/14147'],[
      java('list-remove','인덱스를 지울까요, 값을 지울까요?','정수 List에는 remove가 두 종류예요.\n인수 타입에 따라 지울 대상이 달라져요.',
       '값 2를 지우도록 `remove(2)`를 바꿔요.','static String run()',
       '// 같은 숫자도 인덱스와 값은 달라요.\nvar values=new java.util.ArrayList<>(java.util.List.of(2,4,6));\nvalues.remove(2);\n// 남은 순서를 확인해요.\nreturn values.toString();',
       'values.remove(2)','values.remove(Integer.valueOf(2))','Exercise.run()',[('','[4, 6]')]),
      java('map-count','같은 키의 이전 값을 이어 받아요','Map은 키마다 값을 하나씩 가져요.\n개수를 세려면 이전 값에 더해야 해요.',
       '`count.put(word,1)`을 누적하도록 고쳐요.','static int run(String text)',
       '// 단어마다 누적 횟수를 저장해요.\nvar count=new java.util.HashMap<String,Integer>();\nfor(String word:text.split(",")) count.put(word,1);\n// 처음 단어가 몇 번 나왔는지 확인해요.\nreturn count.get(text.split(",")[0]);',
       'count.put(word,1)','count.put(word,count.getOrDefault(word,0)+1)','Exercise.run(in.nextLine())',[('a,b,a','2'),('x,x,x','3'),('a,b','1')]),
      java('stream-filter','중간 연산은 새 흐름을 만들어요','filter는 조건을 통과한 값만 다음에 보내요.\n원본 배열을 지우는 작업은 아니에요.',
       '양수만 세도록 조건을 `n>0`으로 바꿔요.','static long run(int[] values)',
       '// 조건을 통과한 값의 개수를 세어요.\nreturn java.util.Arrays.stream(values).filter(n->true).count();',
       'n->true','n->n>0',f'Exercise.run({array_call})',[('-2,0,3,4','2'),('-1,-3','0'),('7','1')]),
      java('stream-transform','고른 다음 변환하고 합쳐요','filter와 map은 맡은 일이 달라요.\n최종 연산이 흐름을 실행해요.',
       '짝수만 골라 각각 제곱한 합을 구해요.\n원본 값은 바꾸지 마세요.','static int run(int[] values)',
       '// 고르기, 변환, 합계의 순서를 정해요.\nreturn java.util.Arrays.stream(values).sum();',
       '.sum();','.filter(n->n%2==0).map(n->n*n).sum();',f'Exercise.run({array_call})',[('1,2,3,4','20'),('-2,0,3','4'),('1,5','0')],challenge=True,hints=['filter에서는 나머지를 검사해요.','map에서 n*n으로 바꾼 뒤 sum으로 모아요.']),
    ])
