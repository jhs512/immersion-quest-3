from _engineer_final import fields

EXAMPLE = '''class Parent { int n = 1; int value() { return n; } }
class Child extends Parent { int n = 2; int value() { return n; } }
public class Main {
    static int result() {
        try { return 4; }
        finally { System.out.println("cleanup"); }
    }
    public static void main(String[] args) {
        Parent item = new Child();
        System.out.println(item.n);
        System.out.println(item.value());
        System.out.println(result());
    }
}
'''
SPEC = fields('engineer-java-polymorphism', '필드·재정의·finally의 결과를 나눠 적으세요',
    '선언형의 필드 선택과 실제 객체의 메서드 선택, 반환 전 finally 실행을 함께 추적해요.',
    '아래 Java 코드를 읽으세요. result()의 반환값을 출력하기 전에 finally의 cleanup이 먼저 출력돼요. 각 답안에는 해당 출력만 적으세요.',
    [('field', 'item.n의 출력', ['1']), ('method', 'item.value()의 출력', ['2']),
     ('return', 'result() 호출로 나오는 마지막 두 줄을 공백으로 이어 적으세요.', ['cleanup 4'])],
    ['필드는 item의 선언형 Parent를 따라 1을 읽어요.', '재정의한 메서드는 실제 객체 Child에서 실행돼 2를 반환해요.', 'return 값 4를 전달하기 전에 finally가 cleanup을 출력해요. 마지막 두 줄은 cleanup 다음 4예요.'])
SPEC['task']['language'] = 'java'
SPEC['task']['example_code'] = EXAMPLE
SPEC['task']['narration'].insert(1, dict(action='run', lines=[10,12]))
SPEC['cases']['expected_outputs'] = ['1\n2\ncleanup\n4']
