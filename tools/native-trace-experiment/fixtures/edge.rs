#[derive(Debug)]
struct Order {
    label: String,
    counts: Vec<i32>,
}

#[derive(Debug, Clone, Copy, PartialEq)]
enum Size {
    Small,
    Large(u8),
}

fn depth(n: u32) -> u32 {
    if n == 0 { return 0; }
    depth(n - 1) + 1
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let order = Order { label: String::from("box"), counts: vec![1, 2] };
    let label = order.label;
    let counts = &order.counts;
    let total: i32 = counts.iter().sum();
    let x = 5;
    let x = x * 2;
    let mut name = String::from("a");
    for i in 0..2 {
        let taken = name;
        name = format!("{}{}", taken, i);
    }
    let boxed: Box<i64> = Box::new(-7);
    let maybe: Option<&String> = Some(&label);
    let none: Option<i32> = None;
    let slice: &str = &label[1..];
    let letter = 'R';
    let huge: i128 = -170141183460469231731687303715884105728;
    let size = Size::Large(3);
    let small = Size::Small;
    let mut level = 0;
    level = add(add(level, 1), add(2, 3));
    let deep = depth(2);
    let note = String::from("note");
    let consume = move || note.len();
    let used = consume();
    println!("{} {} {} {} {:?} {:?} {} {} {} {:?} {:?} {} {} {}", total, x, name, boxed, maybe, none, slice, letter, huge, size, small, level, deep, used);
}
