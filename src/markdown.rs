/// Render course Markdown while keeping executable HTML out of the WebView.
pub fn render(source: &str) -> String {
    let parser = pulldown_cmark::Parser::new_ext(
        source,
        pulldown_cmark::Options::ENABLE_TABLES | pulldown_cmark::Options::ENABLE_STRIKETHROUGH,
    );
    let mut html = String::new();
    pulldown_cmark::html::push_html(&mut html, parser);
    ammonia::Builder::default()
        .add_tag_attributes("code", &["class"])
        .rm_tags(&["img"])
        .clean(&html)
        .to_string()
}

#[cfg(test)]
mod tests {
    use super::render;

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
