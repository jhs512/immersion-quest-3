from _engineer_final import code

START = '''#include <stdio.h>
int main(void) {
    int stock = 8;
    int shipped = 3;
    int before = stock;
    // 출고 수량을 반영한 뒤 남은 수량을 저장하세요.
    int after = stock;
    stock = stock - shipped;
    printf("%d %d %d", before, after, stock);
    return 0;
}
'''
SPEC = code('engineer-c-start', '출고 전후의 값을 서로 다른 변수에 기록하세요',
    '값 복사와 대입 순서를 함께 적용해 출고 전후 기록을 남겨요.',
    'before는 출고 전 수량, after와 stock은 출고 후 수량이어야 해요. 지금 출력은 8 5 5여야 해요. stock과 shipped 준비값은 바꾸지 마세요.', 'c', START,
    [('int after = stock;\n    stock = stock - shipped;', 'stock = stock - shipped;\n    int after = stock;', '출고 계산이 끝난 다음 after를 선언해 현재 stock을 저장하세요.')],
    '8 5 5', ['8 8 5', '8 5 5'],
    [dict(values=dict(stock='12', shipped='2'), expected='12 10 10'), dict(values=dict(stock='3', shipped='3'), expected='3 0 0')],
    [([['int after = stock;', 'int after = before;']], '출고 전 복사본을 읽으면 안 돼요.')],
    [([['stock = stock - shipped;', 'stock -= shipped;']], '복합 대입도 같은 출고 계산이에요.')],
    'after를 너무 일찍 복사해 8 8 5가 나와요.', '출고 전 8은 before에 남고 출고 후 5는 after와 stock에 있어요.',
    '조심하세요. stock이 바뀌어도 이미 복사한 before 값은 함께 바뀌지 않아요.')
