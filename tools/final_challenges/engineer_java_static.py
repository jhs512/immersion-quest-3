from _engineer_final import code

START = '''public class Main {
    static class Ticket {
        static int issued = 0;
        int number;
        Ticket() { number = issued; }
    }
    public static void main(String[] args) {
        Ticket a = new Ticket();
        Ticket alias = a;
        Ticket b = new Ticket();
        System.out.print(a.number + " " + alias.number + " " + b.number + " " + Ticket.issued);
    }
}
'''
SPEC = code('engineer-java-static', '생성된 객체에만 다음 발급 번호를 부여하세요',
    '클래스 공유 카운터와 객체별 번호를 나누고 참조 대입을 새 생성과 구별해요.',
    '새 Ticket을 만들 때 issued를 하나 늘린 뒤 그 값을 number에 저장하세요. alias는 a와 같은 객체예요. 지금 출력은 1 1 2 2예요.', 'java', START,
    [('Ticket() { number = issued; }', 'Ticket() { issued++; number = issued; }', '생성자에서 공유 카운터를 먼저 늘리고 객체 번호에 복사하세요.')],
    '1 1 2 2', ['0 0 0 0', '1 1 2 2'],
    [dict(values=dict(issued='10'), expected='11 11 12 12')],
    [([['issued++; number = issued;', 'number = issued; issued++;']], '증가 전 번호를 복사하면 발급 기준과 달라요.')],
    [([['issued++; number = issued;', 'number = ++issued;']], '전위 증가 값을 저장해도 같은 발급 순서예요.')],
    '발급 수를 늘리지 않아 모든 번호가 0이에요.', 'a와 alias는 번호 1 하나를 공유하고 새 b는 번호 2예요. 실제 발급 수는 2예요.',
    '조심하세요. alias = a는 새 객체 생성이 아니므로 발급 수를 늘리지 않아요.')
