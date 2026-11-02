fn main() {
    let prices = vec![1200, 1800];
    let index: usize = 2;
    // 가격이 0원인 것과 상품이 없는 것은 달라요.
    match prices.get(index) {
        Some(price) => println!("가격: {price}"),
        None => println!("상품 없음"),
    }
}
