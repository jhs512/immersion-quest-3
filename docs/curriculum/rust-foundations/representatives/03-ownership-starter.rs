fn show(title: String) {
    // 전달받은 제목을 보여줘요.
    println!("{title}");
}

fn main() {
    let title = String::from("MQ");
    show(title);
    // 함수를 부른 뒤에도 원래 제목이 필요해요.
    println!("{title}");
}
