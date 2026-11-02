use std::sync::LazyLock;

static DECLARATION: LazyLock<regex::Regex> = LazyLock::new(|| {
    regex::Regex::new(r"^let\s+(?:mut\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=;]+)?=").unwrap()
});

pub fn replace_initializer(source: &str, name: &str, value: &str) -> Option<String> {
    let bytes = source.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if let Some(end) = skip_literal(bytes, i) { i = end; continue; }
        if bytes[i] == b'l' && (i == 0 || !identifier(bytes[i - 1])) {
            if let Some(found) = DECLARATION.captures(&source[i..]) {
                if &found[1] == name {
                    let begin = i + found.get(0)?.end();
                    if bytes.get(begin) == Some(&b'=') { i = begin; continue; }
                    let mut end = begin;
                    let mut depth = 0i32;
                    while end < bytes.len() {
                        if let Some(next) = skip_literal(bytes, end) { end = next; continue; }
                        match bytes[end] {
                            b'(' | b'[' | b'{' => depth += 1,
                            b')' | b']' | b'}' => depth -= 1,
                            b';' if depth == 0 => return Some(format!("{} {}{}", &source[..begin], value.trim(), &source[end..])),
                            _ => {}
                        }
                        end += 1;
                    }
                    return None;
                }
            }
        }
        i += 1;
    }
    None
}

fn identifier(byte: u8) -> bool { byte.is_ascii_alphanumeric() || byte == b'_' || byte >= 128 }

fn skip_literal(bytes: &[u8], i: usize) -> Option<usize> {
    let rest = &bytes[i..];
    if rest.starts_with(b"//") {
        return Some(bytes[i..].iter().position(|&c| c == b'\n').map_or(bytes.len(), |n| i + n));
    }
    if rest.starts_with(b"/*") {
        let mut depth = 1;
        let mut end = i + 2;
        while end < bytes.len() && depth > 0 {
            if bytes[end..].starts_with(b"/*") { depth += 1; end += 2; }
            else if bytes[end..].starts_with(b"*/") { depth -= 1; end += 2; }
            else { end += 1; }
        }
        return Some(end);
    }
    let raw = if rest.starts_with(b"br") || rest.starts_with(b"cr") { Some(i + 2) }
        else if bytes[i] == b'r' { Some(i + 1) } else { None };
    if let Some(mut end) = raw {
        let hash_start = end;
        while bytes.get(end) == Some(&b'#') { end += 1; }
        let hashes = end - hash_start;
        if bytes.get(end) == Some(&b'"') {
            end += 1;
            while end < bytes.len() {
                if bytes[end] == b'"' && bytes.get(end + 1..end + 1 + hashes).is_some_and(|s| s.iter().all(|&c| c == b'#')) {
                    return Some(end + 1 + hashes);
                }
                end += 1;
            }
            return Some(bytes.len());
        }
    }
    if bytes[i] == b'"' {
        let mut end = i + 1;
        while end < bytes.len() {
            if bytes[end] == b'\\' { end = (end + 2).min(bytes.len()); }
            else if bytes[end] == b'"' { return Some(end + 1); }
            else { end += 1; }
        }
        return Some(end);
    }
    if bytes[i] == b'\'' {
        let mut end = i + 1;
        if bytes.get(end) == Some(&b'\\') {
            end += 1;
            while end < bytes.len() && bytes[end] != b'\'' && bytes[end] != b'\n' { end += 1; }
        } else {
            end += 1;
            while bytes.get(end).is_some_and(|c| c & 0xc0 == 0x80) { end += 1; }
        }
        if bytes.get(end) == Some(&b'\'') { return Some(end + 1); }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::replace_initializer;

    #[test]
    fn replaces_typed_mutable_and_nested_initializers() {
        let source = "fn main() { let mut stock: Vec<i32> = vec![1, 2]; println!(\"{:?}\", stock); }";
        assert_eq!(replace_initializer(source, "stock", "vec![8, 9]"), Some(source.replace("vec![1, 2]", "vec![8, 9]")));
        assert!(replace_initializer(source, "missing", "0").is_none());
    }

    #[test]
    fn ignores_comments_and_literals_and_replaces_only_the_first_binding() {
        let source = "/* /* nested */ let stock = 2; */ let text = r##\"let stock = 4;\"##; let symbol = ';'; let stock: i32 = 1; let stock = 3;";
        assert_eq!(replace_initializer(source, "stock", "8"), Some(source.replace("let stock: i32 = 1;", "let stock: i32 = 8;")));
        let source = "let text: &'static str = \"문자;열\";";
        assert_eq!(replace_initializer(source, "text", "\"새 값\""), Some("let text: &'static str = \"새 값\";".into()));
    }
}
