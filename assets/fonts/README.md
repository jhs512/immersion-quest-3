# Fonts

Bundled so the app looks the same offline on every platform.

- `PretendardVariable.woff2`: Pretendard (variable), SIL Open Font License 1.1, https://github.com/orioncactus/pretendard. Body text.
- `D2Coding-Regular.woff2`: NAVER D2 Coding 1.4.0, SIL Open Font License 1.1, https://github.com/naver/d2-coding-font/releases/tag/VER1.4.0. Code text, including Korean. See `D2Coding-OFL.txt`.

`fonts.css` embeds them as base64 `@font-face` rules and is inlined into the page by `src/main.rs`. Regenerate it with `python tools/build-fonts.py` after replacing a file.
