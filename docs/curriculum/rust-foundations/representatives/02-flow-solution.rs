fn shipping(total: i32) -> i32 {
    // 30,000원부터 배송비가 없어요.
    if total >= 30_000 { 0 } else { 3000 }
}

fn main() {
    println!("{}", shipping(30_000));
}
