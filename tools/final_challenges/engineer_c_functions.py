from _engineer_final import code

START = '''#include <stdio.h>
int sum(int n) {
    static int calls = 0;
    calls++;
    if (n == 0) return 0;
    return sum(n - 1);
}
int main(void) {
    int n = 4;
    printf("%d %d", sum(n), sum(2));
    return 0;
}
'''
# Static call counts are not printed here: C argument evaluation order is unspecified.
SPEC = code('engineer-c-functions', '재귀가 돌려준 부분 합에 현재 수를 더하세요',
    '재귀의 종료 조건과 반환값 누적을 연결해요.',
    'sum(n)은 0부터 n까지의 합을 반환해야 해요. n은 0 이상이에요. 두 번 호출해도 각 합이 독립적으로 계산되게 하세요. 지금 출력은 10 3이에요.', 'c', START,
    [('return sum(n - 1);', 'return n + sum(n - 1);', '재귀가 돌려준 작은 합에 현재 n을 더해 반환하세요.')],
    '10 3', ['0 0', '10 3'],
    [dict(values=dict(n='0'), expected='0 3'), dict(values=dict(n='6'), expected='21 3')],
    [([['return n + sum(n - 1);', 'return calls + sum(n - 1);']], '호출 횟수는 현재 더할 값이 아니에요.')],
    [([['return n + sum(n - 1);', 'return sum(n - 1) + n;']], '정수 합의 순서를 바꿔도 돼요.')],
    '끝 조건까지 내려가지만 어느 호출도 자기 수를 더하지 않아 0 0이 나와요.', '4의 합 10과 2의 합 3을 각자 반환해요. static calls는 호출 간에 남는 별도 기록이에요.',
    '조심하세요. static 호출 횟수를 합에 더하면 이전 호출의 기록이 다음 계산에 섞여요.')
