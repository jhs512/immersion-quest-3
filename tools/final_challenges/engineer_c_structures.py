from _engineer_final import code

START = '''#include <stdio.h>
typedef struct { int price; int qty; } Item;
int normal(Item item) { return item.price * item.qty; }
int half(Item item) { return item.price * item.qty / 2; }
int main(void) {
    Item items[] = {{100, 2}, {80, 3}};
    int count = 2;
    int sale = 1;
    int (*rule)(Item) = normal;
    int total = 0;
    for (int i = 0; i < count; i++) {
        total = rule(items[i]);
    }
    printf("%d", total);
    return 0;
}
'''
SPEC = code('engineer-c-structures', '구조체 배열에 선택한 가격 규칙을 적용하세요',
    '구조체 값과 함수 포인터를 연결해 각 항목의 계산을 합쳐요.',
    'sale이 1이면 half, 0이면 normal 규칙으로 모든 상품의 금액을 합하세요. 수량과 가격은 양수이고 할인 전 금액은 짝수예요. 지금 출력은 220이에요.', 'c', START,
    [('int (*rule)(Item) = normal;', 'int (*rule)(Item) = sale ? half : normal;', 'sale 값에 맞춰 계산 함수의 주소를 고르세요.'),
     ('total = rule(items[i]);', 'total += rule(items[i]);', '각 구조체를 규칙 함수에 전달하고 반환 금액을 누적하세요.')],
    '220', ['240', '220'],
    [dict(values=dict(sale='0'), expected='440'), dict(values=dict(items='{{20, 4}, {10, 2}}'), expected='50')],
    [([['sale ? half : normal', 'half']], '할인 없는 경우도 처리해야 해요.')],
    [([['total += rule(items[i]);', 'total = total + rule(items[i]);']], '일반 누적 대입도 같아요.')],
    '정상 가격의 마지막 상품 240만 남아요.', '할인 가격 100과 120을 더해 220이에요.',
    '조심하세요. 함수 포인터를 선언해도 선택한 함수를 항목마다 호출하지 않으면 계산되지 않아요.')
