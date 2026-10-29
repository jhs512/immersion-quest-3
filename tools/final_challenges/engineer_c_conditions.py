from _engineer_final import code

START = '''#include <stdio.h>
int main(void) {
    int stock = 11;
    int size = 4;
    // 완성한 상자 수와 다음 상자에 부족한 낱개 수를 계산하세요.
    int boxes = stock % size;
    int missing = size - stock % size;
    printf("%d %d", boxes, missing);
    return 0;
}
'''
SPEC = code('engineer-c-conditions', '완성 상자와 추가로 필요한 낱개를 계산하세요',
    '몫·나머지·조건식으로 포장 수와 정확한 경계를 처리해요.',
    '재고는 0 이상, 상자 크기는 1 이상이에요. 완성 상자 수와 다음 상자에 모자란 수량을 출력하세요. 남은 낱개가 0이면 모자란 수도 0으로 정해요. 지금 답은 2 1이에요.', 'c', START,
    [('int boxes = stock % size;', 'int boxes = stock / size;', 'boxes에는 나눗셈의 몫을 저장하세요.'),
     ('int missing = size - stock % size;', 'int missing = stock % size == 0 ? 0 : size - stock % size;', '나머지가 0이면 missing도 0, 아니면 상자 크기에서 나머지를 빼세요.')],
    '2 1', ['3 1', '2 1'],
    [dict(values=dict(stock='8', size='4'), expected='2 0'), dict(values=dict(stock='0', size='3'), expected='0 0'), dict(values=dict(stock='2', size='5'), expected='0 3')],
    [([['stock % size == 0 ? 0 : size - stock % size', 'size - stock % size']], '딱 맞는 포장에는 부족한 수가 없어요.')],
    [([['stock % size == 0 ? 0 : size - stock % size', '(size - stock % size) % size']], '나머지로 경계를 처리해도 돼요.')],
    '완성 상자 대신 나머지 3을 출력해요.', '11개로 상자 2개를 만들고 낱개 3개가 남아 다음 상자에는 1개가 모자라요.',
    '조심하세요. 나머지가 0일 때 상자 크기만큼 부족하다고 계산하면 틀려요.')
