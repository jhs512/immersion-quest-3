from .common import *

git_tasks=[]
for id,title,goal,script,minimum,message,files,pushed in [
    ('first-commit','작업 폴더와 첫 커밋','`work` 폴더에 main 브랜치 저장소를 만드세요.\nREADME.md에 `Java backend`와 줄바꿈을 저장하세요.\n`start course`라는 메시지로 커밋하세요.',
     '''
     # 명령 하나가 실패하면 다음 작업을 멈춰요.
     set -e
     # 매 실습은 빈 폴더에서 시작해요.
     git init -b main work
     cd work
     # 파일 저장과 커밋은 서로 다른 일이에요.
     printf 'Java backend\\n' > README.md
     git add README.md
     # 스테이징한 파일을 이력으로 남겨요.
     git commit -m 'start course'
     ''',1,'start course',{'README.md':'Java backend\n'},False),
    ('remote-history','수정 이력을 원격으로 보내기','첫 실습과 같은 저장소를 새로 만드세요.\n첫 커밋 뒤 README.md에 `Learning Git`을 추가하세요.\n둘째 커밋 메시지는 `add learning plan`이에요.\n제공한 `../remote.git`을 origin으로 연결하세요.\nmain 브랜치를 push하세요.',
     '''
     set -e
     # 앞 문제의 작업 폴더를 재사용하지 않아요.
     git init -b main work
     cd work
     printf 'Java backend\\n' > README.md
     git add README.md
     git commit -m 'start course'
     # 수정한 내용도 다시 스테이징해야 해요.
     printf 'Learning Git\\n' >> README.md
     git add README.md
     git commit -m 'add learning plan'
     # 이 원격은 실습용 로컬 저장소예요.
     git remote add origin ../remote.git
     git push -u origin main
     ''',2,'add learning plan',{'README.md':'Java backend\nLearning Git\n'},True),
]:
    t=task(id,title,goal,script,language='git',entry='practice.sh',starter='set -e\n# 여기에 Git 명령을 작성하세요.')
    t['git_checks']=dict(minimum_commits=minimum,head_message=message,tracked_files=files,branch='main',pushed=pushed)
    git_tasks.append(t)
lesson('git-environment','개발환경과 Git의 첫 흐름','파일을 실행하고 변경 이력을 원격에 남겨요.',[14148],[
('실행 도구와 작업 폴더','''
    JDK 25, Git, Node.js를 설치하세요.
    웹 실습에는 Microsoft Edge도 사용해요.
    터미널에서 버전을 먼저 확인하세요.

    ```shell
    java --version
    javac --version
    git --version
    node --version
    ```

    자바와 javac의 주 버전은 25여야 해요.
    명령을 못 찾으면 설치 경로를 확인하세요.
    실습 실행은 새 임시 폴더에서 이뤄져요.
    각 문제는 앞 문제의 파일에 의존하지 않아요.

    개인 연습에서는 빈 프로젝트 폴더를 만드세요.
    그 폴더를 편집기로 열고 Main.java를 저장해요.
    터미널의 현재 위치도 같은 폴더여야 하죠.
'''),
('저장·스테이징·커밋·push','''
    Git은 파일의 변경 이력을 관리해요.
    저장만 하면 Git 이력에는 아직 남지 않아요.
    먼저 파일 하나를 만들고 상태를 확인할게요.

    ```shell
    git init -b main work
    cd work
    printf 'Java backend\\n' > README.md
    git status --short
    ```

    새 파일은 아직 추적하지 않는 상태예요.
    이제 커밋할 파일을 고르고 이력을 남겨요.

    ```shell
    git add README.md
    git commit -m 'start course'
    git log --oneline
    ```

    커밋 뒤에는 메시지와 커밋 ID가 보여요.
    ID는 실행할 때마다 달라질 수 있어요.
    조심하세요. 커밋은 원격 전송이 아니에요.
    origin을 연결하고 push해야 원격에도 남아요.
    이 실습의 remote.git은 로컬 원격이에요.
    실제 GitHub 연습은 빈 공개 리포에서 해보세요.
    비밀번호나 접근 토큰은 커밋하지 마세요.
''')],git_tasks)

old=json.loads((ROOT/'courses/java-basics.json').read_text(encoding='utf-8'))
units={u['id']:u for c in old['chapters'] for u in c['units']}
groups=[
('java-values','자바의 값과 입력·출력','값의 종류를 구분하고 입력을 계산해요.',[1,2,3,4],['git-environment']),
('java-control','조건·반복·디버깅','경계값과 반복의 종료 조건을 확인해요.',[5,6,7],['java-values']),
('java-methods-arrays','메서드와 배열','계산을 나누고 여러 값을 함께 다뤄요.',[8,9,10,12],['java-control']),
('java-objects','객체·생성자·참조·static','서로 다른 객체와 공유 상태를 구분해요.',[11],['java-methods-arrays'])]
for id,title,description,numbers,prereq in groups:
    sections=[];tasks=[]
    for n in numbers:
        u=units[f'java25-{n:02}']
        for a in u['activities']:
            if a['kind']=='concept': sections.append((a['title'],a['body']))
            if a['kind']=='coding':
                p=a['problem']
                t=task(p['id'],a['title'],p['content'],p['solution'],language='java',entry='Main.java',tests=p['tests'],starter=p['starter_code'])
                if p.get('checker'):t['checker']=p['checker']
                t['narration']=a['narration']
                tasks.append(t)
    lesson(id,title,description,[14146],sections,tasks,prereq)

lesson('java-collections','컬렉션·제네릭·예외','크기가 변하는 자료와 잘못된 입력을 다뤄요.',[14146],[
('List와 Map을 고르는 기준','''
    배열은 만들 때 길이를 정해요.
    등록과 삭제가 많으면 목록(List)을 사용해요.
    `List<String>`은 문자열 목록이라는 뜻이에요.
    제네릭은 자료형의 실수를 일찍 찾아줘요.

    ```java
    var names = new java.util.ArrayList<String>();
    names.add("민수");
    System.out.println(names.size());
    ```

    실행하면 등록한 원소 수가 보여요.
    이제 한 명을 더 넣고 첫 원소를 지워봐요.

    ```java
    names.add("영희");
    names.remove(0);
    System.out.println(names.get(0));
    ```

    남은 원소는 영희예요.
    조심하세요. 삭제하면 뒤 원소의 위치가 바뀌어요.
    업무상의 ID와 목록 인덱스는 구분해야 해요.
    키로 찾을 때는 사전(Map)을 사용해요.
    같은 키에 put하면 기존 값이 교체돼요.
'''),
('예외를 경계에서 다루기','''
    숫자가 아닌 입력은 parseInt로 읽을 수 없어요.
    이때 NumberFormatException이 발생해요.
    입력을 받는 경계에서 그 예외를 처리하세요.
    모든 예외를 숨기면 버그도 못 찾게 돼요.
    정상 결과와 실패 결과를 구분해 돌려주세요.
    빈 목록, 중복 키, 잘못된 숫자를 검사해요.
''')],[
jt('unique-names','등장 순서대로 중복 제거','`unique(List<String>)`을 구현하세요.\n처음 등장한 순서를 유지하세요.\n원본 목록은 변경하지 마세요.', '''
import java.util.*;
class Exercise {
    static List<String> unique(List<String> names) {
        // 새 목록을 만들어 원본을 보호해요.
        var result = new ArrayList<String>();
        for (String name : names) {
            // 처음 만난 이름만 추가해요.
            if (!result.contains(name)) result.add(name);
        }
        return result;
    }
}
''','''
@Test void preservesOrderAndInput() {
    var input = new java.util.ArrayList<>(java.util.List.of("나", "가", "나", "다"));
    assertThat(Exercise.unique(input)).containsExactly("나", "가", "다");
    assertThat(input).containsExactly("나", "가", "나", "다");
    assertThat(Exercise.unique(java.util.List.of())).isEmpty();
}
'''),
jt('safe-count','숫자 입력을 안전하게 읽기','`count(String)`을 구현하세요.\n공백을 제거한 뒤 0 이상인 정수만 인정해요.\nnull, 빈 문자열, 음수, 숫자가 아닌 값은 -1이에요.', '''
class Exercise {
    static int count(String text) {
        // null은 문자열 메서드를 호출하기 전에 확인해요.
        if (text == null) return -1;
        try {
            int value = Integer.parseInt(text.trim());
            // 범위를 벗어난 입력도 실패로 구분해요.
            return value >= 0 ? value : -1;
        } catch (NumberFormatException e) {
            // 숫자 변환 실패만 여기에서 처리해요.
            return -1;
        }
    }
}
''','''
@Test void inputBoundaries() {
    assertThat(Exercise.count(" 12 ")).isEqualTo(12);
    assertThat(Exercise.count("0")).isZero();
    for (String s : new String[]{null,"","-1","abc","999999999999"}) assertThat(Exercise.count(s)).isEqualTo(-1);
}
''')],['wise-array'])

lesson('java-design','캡슐화·인터페이스·조합','변경할 부분을 객체의 역할로 나눠요.',[14146],[
('외부에서 바꾸면 안 되는 상태','''
    객체는 값과 그 값을 바꾸는 규칙을 묶어요.
    잔액을 public으로 열면 음수를 넣을 수 있죠.
    private 필드와 검증하는 메서드로 막아요.
    생성자에서도 같은 규칙을 지켜야 해요.
    입력이 잘못되면 조용히 보정하지 마세요.
    IllegalArgumentException으로 알려주세요.
'''),
('역할을 받아서 사용하기','''
    알림을 보내는 역할을 인터페이스로 정해요.
    사용하는 객체는 실제 전송 방법을 몰라도 돼요.
    생성자로 필요한 역할을 받으면 바꾸기 쉬워요.
    이것이 이 실습에서 사용하는 의존성 주입이에요.
    상속은 부모의 모든 구현을 물려받아요.
    단지 기능이 필요하면 조합을 먼저 검토해요.
    조심하세요. static도 객체를 전달받을 수 있어요.
    static의 제한은 암묵적인 this가 없다는 점이에요.
    참조의 실제 크기와 GC 시점은 JVM에 달려요.
    참조가 사라졌다고 즉시 수거되지는 않아요.
''')],[
jt('wallet','잔액의 규칙을 보호하기','`Wallet(int)`과 `balance()`, `deposit(int)`을 구현하세요.\n초기 잔액은 0 이상이에요. 입금액은 양수예요.\n잘못된 값에는 IllegalArgumentException을 던지세요.\n서로 다른 지갑의 잔액은 독립이에요.', '''
class Wallet {
    // 객체마다 독립된 잔액을 보관해요.
    private int balance;
    Wallet(int balance) {
        if (balance < 0) throw new IllegalArgumentException("잔액");
        this.balance = balance;
    }
    int balance() { return balance; }
    void deposit(int amount) {
        // 잘못된 입력이 상태를 바꾸기 전에 거부해요.
        if (amount <= 0) throw new IllegalArgumentException("입금액");
        balance = Math.addExact(balance, amount);
    }
}
''','''
@Test void balancesAreIndependent() {
    var a = new Wallet(10); var b = new Wallet(20);
    a.deposit(5);
    assertThat(a.balance()).isEqualTo(15); assertThat(b.balance()).isEqualTo(20);
    assertThatThrownBy(() -> a.deposit(0)).isInstanceOf(IllegalArgumentException.class);
    assertThatThrownBy(() -> new Wallet(-1)).isInstanceOf(IllegalArgumentException.class);
}
''',starter='class Wallet {\n    // 상태와 메서드를 작성하세요.\n}'),
jt('notification','교체 가능한 알림 역할','`Notifier`에 `void send(String)`을 선언하세요.\n`Registration(Notifier)`은 전달받은 알림을 보관해요.\n`welcome(String)`은 `환영해요, 이름`을 보내요.', '''
interface Notifier { void send(String message); }
class Registration {
    // 구체적인 전송 방법 대신 역할에 의존해요.
    private final Notifier notifier;
    Registration(Notifier notifier) { this.notifier = notifier; }
    void welcome(String name) {
        // 전송은 주입받은 객체에 맡겨요.
        notifier.send("환영해요, " + name);
    }
}
''','''
@Test void injectedRoleReceivesMessage() {
    var messages = new java.util.ArrayList<String>();
    var service = new Registration(messages::add);
    service.welcome("민수"); service.welcome("영희");
    assertThat(messages).containsExactly("환영해요, 민수", "환영해요, 영희");
}
''',starter='interface Notifier {\n}\nclass Registration {\n}')],['java-collections'])

lesson('java-streams','람다·스트림·집계','선별·변환·집계를 자료의 흐름으로 표현해요.',[14147],[
('반복문을 자료 흐름으로 읽기','''
    람다는 함수의 동작을 값처럼 전달하는 문법이에요.
    `n -> n * 2`는 숫자를 두 배로 바꿔요.
    스트림은 저장소가 아니라 처리의 흐름이에요.

    ```java
    var values = java.util.List.of(1, 2, 3, 4);
    System.out.println(values.stream().filter(n -> n % 2 == 0).toList());
    ```

    실행하면 짝수만 모은 목록이 보여요.
    그 뒤 map을 연결하면 값을 바꿀 수 있어요.

    ```java
    System.out.println(values.stream().filter(n -> n % 2 == 0).map(n -> n * 2).toList());
    ```

    선별한 뒤 두 배로 바뀐 목록이 나와요.
    조심하세요. 스트림은 최종 연산 뒤 재사용하지 못해요.
    filter는 원본 목록을 수정하지 않아요.
    부수 효과가 필요 없는 변환부터 연습하세요.
'''),
('빈 결과와 집계','''
    개수를 세면 count, 합을 내면 sum을 사용해요.
    최댓값은 자료가 비어 있으면 없을 수 있어요.
    Optional은 값이 없을 가능성을 드러내요.
    get을 바로 호출하면 빈 값에서 예외가 나요.
    기본값을 정하거나 없는 경우를 따로 처리하세요.
    병렬 스트림을 쓰면 늘 빨라지는 것은 아니에요.
''')],[
jt('even-square','짝수의 제곱만 모으기','`evenSquares(List<Integer>)`를 구현하세요.\n짝수만 제곱하고 원래 순서를 유지하세요.\n원본 목록을 수정하지 마세요.', '''
import java.util.*;
class Exercise {
    static List<Integer> evenSquares(List<Integer> values) {
        // 선별과 변환을 분리해서 읽어요.
        return values.stream().filter(n -> n % 2 == 0)
            .map(n -> n * n).toList();
    }
}
''','''
@Test void negativeZeroAndEmpty() {
    assertThat(Exercise.evenSquares(java.util.List.of(-2,3,0,4))).containsExactly(4,0,16);
    assertThat(Exercise.evenSquares(java.util.List.of())).isEmpty();
}
'''),
jt('word-count','이름별 개수와 빈 최댓값','`counts(List<String>)`는 문자열별 개수 Map을 반환해요.\n`max(List<Integer>)`는 Optional<Integer>를 반환해요.\n빈 목록에는 Optional.empty()를 반환하세요.', '''
import java.util.*;
import java.util.stream.Collectors;
class Exercise {
    static Map<String, Long> counts(List<String> names) {
        // 같은 이름을 묶은 뒤 각 묶음의 수를 세요.
        return names.stream().collect(Collectors.groupingBy(n -> n, Collectors.counting()));
    }
    static Optional<Integer> max(List<Integer> values) {
        // 빈 목록은 값이 없는 Optional로 남겨요.
        return values.stream().max(Integer::compareTo);
    }
}
''','''
@Test void aggregationAndAbsence() {
    assertThat(Exercise.counts(java.util.List.of("가","나","가"))).containsEntry("가",2L).containsEntry("나",1L);
    assertThat(Exercise.counts(java.util.List.of())).isEmpty();
    assertThat(Exercise.max(java.util.List.of(-3,-1))).contains(-1);
    assertThat(Exercise.max(java.util.List.of())).isEmpty();
}
''')],['wise-list'])
