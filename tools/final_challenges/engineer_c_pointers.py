from _engineer_final import code

START = '''#include <stdio.h>
void swap(int *a, int *b) {
    int temp = *a;
    a = b;
    *b = temp;
}
int main(void) {
    int left = 3, right = 8;
    swap(&left, &right);
    printf("%d %d", left, right);
    return 0;
}
'''
SPEC = code('engineer-c-pointers', '두 원래 재고를 포인터로 교환하세요',
    '주소 복사와 역참조 쓰기를 구별해 호출자의 두 값을 바꿔요.',
    'swap이 받은 두 주소의 정수를 교환해야 해요. main의 출력문이나 준비값은 바꾸지 마세요. 지금 결과는 8 3이에요.', 'c', START,
    [('a = b;', '*a = *b;', '지역 포인터 a를 옮기지 말고 a가 가리킨 정수에 b의 값을 쓰세요.')],
    '8 3', ['3 3', '8 3'], [dict(values=dict(left='-2', right='7'), expected='7 -2'), dict(values=dict(left='5', right='5'), expected='5 5')],
    [([['int temp = *a;', 'int temp = *b;']], '교환 전에 a의 원래 값을 보관해야 해요.')],
    [([['*a = *b;', '(*a) = (*b);']], '괄호로 역참조를 묶어도 같은 쓰기예요.')],
    '주소 복사만 한 뒤 right를 덮어써 두 값이 3 3이 됐어요.', '호출자의 left와 right에 각각 8과 3을 썼어요.',
    '조심하세요. 임시 저장 없이 첫 값을 덮어쓰면 두 번째에 돌려줄 값이 사라져요.')
