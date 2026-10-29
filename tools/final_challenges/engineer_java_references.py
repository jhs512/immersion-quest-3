from _engineer_final import code

START = '''public class Main {
    static class Order {
        int[] quantities;
        Order(int[] source) { quantities = source; }
        void add(int value) { quantities[0] += value; }
    }
    public static void main(String[] args) {
        int[] source = {2, 4};
        int added = 3;
        Order first = new Order(source);
        Order second = new Order(source);
        first.add(added);
        System.out.print(source[0] + " " + first.quantities[0] + " " + second.quantities[0]);
    }
}
'''
SPEC = code('engineer-java-references', '주문별 수량 배열을 독립적으로 보관하세요',
    '참조 대입과 배열 복사를 구별해 한 객체의 변경이 다른 객체로 번지지 않게 해요.',
    '두 Order는 source의 초기 내용을 받아요. first에만 added를 더했을 때 source와 second는 그대로여야 해요. 지금 출력은 2 5 2예요. add와 출력문은 바꾸지 마세요.', 'java', START,
    [('quantities = source;', 'quantities = source.clone();', '생성자에서 받은 배열의 복사본을 필드에 저장하세요.')],
    '2 5 2', ['5 5 5', '2 5 2'],
    [dict(values=dict(source='{7, 9}', added='2'), expected='7 9 7'), dict(values=dict(source='{0}', added='5'), expected='0 5 0')],
    [([['quantities = source.clone();', 'quantities = source;']], '같은 배열 참조는 서로 영향을 줘요.')],
    [([['source.clone()', 'java.util.Arrays.copyOf(source, source.length)']], 'Arrays.copyOf도 새 배열을 만들어요.')],
    '세 이름이 같은 배열을 가리켜 모두 5가 됐어요.', 'first만 5가 되고 원본과 second의 첫 수량은 2예요.',
    '조심하세요. 객체를 두 번 만들었다고 생성자에 넘긴 배열까지 자동으로 복사되지는 않아요.')
