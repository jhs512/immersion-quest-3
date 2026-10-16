# Fonts

Bundled so the app looks the same offline on every platform.

- `PretendardVariable.woff2`: Pretendard (variable), SIL Open Font License 1.1, https://github.com/orioncactus/pretendard. Body text.
- `JetBrainsMono-Regular.woff2`, `JetBrainsMono-Bold.woff2`: JetBrains Mono, SIL Open Font License 1.1, https://github.com/JetBrains/JetBrainsMono. Code editor, code blocks and inline code; Korean inside code falls back to Pretendard.

`fonts.css` embeds them as base64 `@font-face` rules and is inlined into the page by `src/main.rs`. Regenerate it with `python tools/build-fonts.py` after replacing a file.
