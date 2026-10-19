/// Render course Markdown while keeping executable HTML out of the WebView.
pub fn render(source: &str) -> String {
    let mut code_block = false;
    let parser = pulldown_cmark::Parser::new_ext(
        source,
        pulldown_cmark::Options::ENABLE_TABLES | pulldown_cmark::Options::ENABLE_STRIKETHROUGH,
    ).map(|event| match event {
        pulldown_cmark::Event::Start(pulldown_cmark::Tag::CodeBlock(_)) => {code_block=true;event},
        pulldown_cmark::Event::End(pulldown_cmark::TagEnd::CodeBlock) => {code_block=false;event},
        pulldown_cmark::Event::Text(text) if !code_block => pulldown_cmark::Event::Text(format_prices(&text).into()),
        _ => event,
    });
    let mut html = String::new();
    pulldown_cmark::html::push_html(&mut html, parser);
    ammonia::Builder::default()
        .add_tag_attributes("code", &["class"])
        .rm_tags(&["img"])
        .clean(&html)
        .to_string()
}

/// Group won amounts in prose; identifiers, decimals and executable code stay literal.
pub fn format_prices(text: &str) -> String {
    let mut result=String::with_capacity(text.len());
    let mut chars=text.char_indices().peekable();
    let mut previous=None;
    while let Some((start,ch))=chars.next() {
        if ch.is_ascii_digit() && !previous.is_some_and(|c:char|c.is_ascii_alphanumeric()||c=='_'||c=='.'||c==',') {
            let mut end=start+1;
            while let Some(&(index,next))=chars.peek() {
                if !next.is_ascii_digit() && next!=',' {break;}
                chars.next();end=index+1;
            }
            let amount=&text[start..end];
            if text[end..].trim_start().starts_with('원') && !amount.ends_with(',') {
                let digits=amount.replace(',',"");
                for (index,digit) in digits.chars().enumerate() {
                    if index>0 && (digits.len()-index)%3==0 {result.push(',');}
                    result.push(digit);
                }
            } else {result.push_str(amount);}
            previous=amount.chars().last();
        } else {result.push(ch);previous=Some(ch);}
    }
    result
}

#[cfg(test)]
mod tests {
    use super::render;

    #[test]
    fn groups_prices_in_prose_without_changing_code_or_other_numbers() {
        let html=render("19999원과 20000 원, **3000원**. 19,999원. 3.19999원. id19999원.\n\n`int amount = 19999;`\n\n```java\n// 19999원\nint amount = 19999;\n```");
        assert!(html.contains("19,999원과 20,000 원"));
        assert!(html.contains("<strong>3,000원</strong>"));
        assert!(html.contains("3.19999원. id19999원."));
        assert!(html.contains("int amount = 19999;"));
        assert!(html.contains("// 19999원"));
    }

    #[test]
    fn renders_course_headings_emphasis_tables_and_python_blocks() {
        let html = render("## 개념\n\n**중요**: `main.py`\n\n```python\nprint('안녕')\n```\n\n| A | B |\n|---|---|\n| 1 | 2 |");
        assert!(html.contains("<h2>개념</h2>"));
        assert!(html.contains("<strong>중요</strong>"));
        assert!(html.contains("<code>main.py</code>"));
        assert!(html.contains("class=\"language-python\""));
        assert!(html.contains("<table>"));
    }

    #[test]
    fn course_markup_cannot_execute_scripts_or_load_remote_images() {
        let html = render("<script>alert('x')</script>\n\n[bad](javascript:alert%281%29)\n\n![remote](https://example.com/image.png)");
        assert!(!html.contains("<script"));
        assert!(!html.contains("javascript:"));
        assert!(!html.contains("<img"));
    }
}
