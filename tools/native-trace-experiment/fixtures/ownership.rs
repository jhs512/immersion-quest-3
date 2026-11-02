#[derive(Debug, Clone)]
struct Item {
    name: String,
    stock: u32,
}

fn describe(item: &Item) -> usize {
    item.name.len()
}

fn take(item: Item) -> u32 {
    item.stock
}

fn main() {
    let first = String::from("pen");
    let moved = first;
    let copy = moved.clone();
    let mut items: Vec<Item> = Vec::new();
    items.push(Item { name: copy, stock: 3 });
    let found: bool = items.iter().find(|i| i.stock > 1).is_some();
    let width = describe(&items[0]);
    let parsed: Result<i32, std::num::ParseIntError> = "42".parse::<i32>();
    let bad: Result<i32, std::num::ParseIntError> = "x".parse::<i32>();
    let owned = items.pop().unwrap();
    let stock = take(owned);
    let big: u64 = 18446744073709551615;
    let nan = f64::NAN;
    println!("{} {:?} {} {:?} {:?} {} {} {}", moved, found, width, parsed, bad.is_err(), stock, big, nan);
}
