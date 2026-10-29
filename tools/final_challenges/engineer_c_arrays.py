from _engineer_final import code

START = '''#include <stdio.h>
int main(void) {
    int bins[] = {4, 9, 9, 2};
    int count = 4;
    int total = 0, best = 0;
    // 모든 칸을 더하고 최댓값이 처음 나온 위치를 기록하세요.
    for (int i = 0; i < count - 1; i++) {
        total = bins[i];
        if (bins[i] >= bins[best]) best = i;
    }
    printf("%d %d", total, best);
    return 0;
}
'''
SPEC = code('engineer-c-arrays', '모든 재고의 합과 첫 최대 위치를 구하세요',
    '배열 순회·누적·동점 조건을 하나의 반복에 적용해요.',
    'count는 배열의 칸 수이고 1 이상이에요. 모든 재고 합과 최대 재고가 처음 나타나는 위치를 0부터 세어 출력하세요. 지금 답은 24 1이에요.', 'c', START,
    [('i < count - 1;', 'i < count;', '마지막 칸까지 순회하세요.'), ('total = bins[i];', 'total += bins[i];', '읽은 재고를 total에 누적하세요.'), ('bins[i] >= bins[best]', 'bins[i] > bins[best]', '동점이면 앞 위치를 유지하세요.')],
    '24 1', ['9 2', '24 1'],
    [dict(values=dict(bins='{7}', count='1'), expected='7 0'), dict(values=dict(bins='{1, 2, 8}', count='3'), expected='11 2'), dict(values=dict(bins='{5, 5}', count='2'), expected='10 0')],
    [([['bins[i] > bins[best]', 'bins[i] >= bins[best]']], '최댓값의 마지막 위치는 요구와 달라요.')],
    [([['total += bins[i];', 'total = total + bins[i];']], '일반 대입 누적도 정답이에요.')],
    '합을 덮어쓰고 마지막 칸도 빠져 9 2가 나와요.', '모든 재고의 합은 24이고 최대 9의 첫 위치는 1이에요.',
    '조심하세요. 동점에서도 위치를 바꾸면 첫 번째 최대 위치가 사라져요.')
