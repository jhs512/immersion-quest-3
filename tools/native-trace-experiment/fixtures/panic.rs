fn main() {
    let items: Vec<i32> = vec![1, 2];
    let index = items.len() + 1;
    println!("before");
    let value = items[index];
    println!("{}", value);
}
