from _engineer_final import code

START = '''public class Main {
    public static void main(String[] args) {
        int[] amounts = {0, 5, 8, -1, 20};
        int total = 0;
        for (int amount : amounts) {
            if (amount == -1) continue;
            if (amount == 0) break;
            total += amount / 2;
        }
        System.out.print(total);
    }
}
'''
SPEC = code('engineer-java-flow', '건너뛸 값과 종료 표시를 구별해 합산하세요',
    'continue·break·정수 나눗셈의 순서를 함께 판단해요.',
    '0은 건너뛰고 -1을 만나면 입력 처리를 끝내세요. 그전 양수 금액 각각을 정수로 2로 나눈 몫만 더하세요. 준비 배열에는 0 이상 금액과 -1만 있어요. 지금 답은 6이에요.', 'java', START,
    [('if (amount == -1) continue;', 'if (amount == -1) break;', '-1에서 반복을 끝내세요.'),
     ('if (amount == 0) break;', 'if (amount == 0) continue;', '0이면 다음 금액으로 건너뛰세요.')],
    '6', ['0', '6'],
    [dict(values=dict(amounts='{3, 3, -1, 8}'), expected='2'), dict(values=dict(amounts='{-1, 10}'), expected='0'), dict(values=dict(amounts='{0, 2, 0, 6}'), expected='4')],
    [([['if (amount == -1) break;', 'if (amount == -1) continue;']], '종료 표시 뒤 금액은 처리하지 않아요.')],
    [([['total += amount / 2;', 'total = total + amount / 2;']], '몫을 누적하는 일반 대입도 정답이에요.')],
    '첫 값 0에서 종료해 뒤 금액을 전혀 읽지 못해요.', '5의 몫 2와 8의 몫 4만 합해 6이에요. -1 뒤 20은 제외해요.',
    '조심하세요. 각 금액의 정수 몫을 합하는 것과 금액을 모두 합한 뒤 나누는 것은 다를 수 있어요.')
