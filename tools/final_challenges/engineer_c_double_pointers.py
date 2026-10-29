from _engineer_final import code

START = '''#include <stdio.h>
void select_min(int **selected, int *bins, int count) {
    int *best = bins;
    for (int i = 1; i < count; i++) {
        if (bins[i] < *best) best = &bins[i];
    }
    // 호출자가 가진 포인터를 최소 재고 칸으로 옮기세요.
    **selected = *best;
}
int main(void) {
    int bins[] = {8, 2, 5};
    int count = 3;
    int *chosen = &bins[0];
    select_min(&chosen, bins, count);
    printf("%d %d %d", (int)(chosen - bins), *chosen, bins[0]);
    return 0;
}
'''
SPEC = code('engineer-c-double-pointers', '최소 재고를 가리키도록 호출자의 포인터를 바꾸세요',
    '이중 포인터의 어느 층에 써야 주소가 바뀌는지 판단해요.',
    '배열은 바꾸지 말고 chosen이 가장 작은 재고의 첫 칸을 가리키게 하세요. count는 1 이상이에요. 출력은 선택 위치·선택 값·첫 칸 원래 값 순서로 지금 1 2 8이에요.', 'c', START,
    [('**selected = *best;', '*selected = best;', '두 번 따라가 정수를 고치지 말고 한 번 따라가 포인터에 best 주소를 쓰세요.')],
    '1 2 8', ['0 2 2', '1 2 8'],
    [dict(values=dict(bins='{1, 4, 1}', count='3'), expected='0 1 1'), dict(values=dict(bins='{7, 5, -1}', count='3'), expected='2 -1 7')],
    [([['*selected = best;', '**selected = *best;']], '값을 복사하면 배열이 훼손되고 선택 주소는 그대로예요.')],
    [([['*selected = best;', '(*selected) = best;']], '역참조 괄호도 같은 주소 쓰기예요.')],
    '첫 칸이 2로 훼손됐고 선택 위치는 여전히 0이에요.', '위치 1의 값 2를 가리키며 원래 첫 칸 8은 그대로예요.',
    '조심하세요. 별 하나는 포인터를, 별 둘은 그 포인터가 가리킨 정수를 바꿔요.')
