from _engineer_final import fields

SPEC = fields('engineer-db-storage', '주문 표의 종속·조회·변경 사건을 판단하세요',
    '정규화의 함수 종속과 인덱스·트리거의 서로 다른 역할을 구별해요.',
    '주문상세의 키는 (order_id, product_id)예요. product_id만으로 product_name이 정해져요. 검색은 WHERE product_id = ?가 많고, 수량 변경 때마다 감사 행을 자동으로 남겨야 해요. 아래 세 설계 판단을 적으세요.',
    [('normal', '키 일부에만 의존하는 product_name 때문에 위반하는 정규형은?', ['제2정규형', '2NF', '2정규형']),
     ('index', '상품별 검색을 위해 인덱스의 선두에 둘 열 이름은?', ['product_id']),
     ('event', '행 변경 사건에 자동 반응해 감사 기록을 남기는 DB 기능은?', ['트리거', 'trigger', 'TRIGGER'])],
    ['상품명은 복합 키 전체가 아니라 product_id에만 의존하므로 부분 함수 종속이에요. 제2정규형을 위반해요.',
     '검색 조건에 쓰는 product_id를 인덱스의 선두 열로 검토해요. 인덱스는 정규화 자체를 대신하지 않아요.',
     '수량 변경 사건에 자동 실행하는 기능은 트리거예요. 단순 조회용 인덱스와 역할이 달라요.'])
