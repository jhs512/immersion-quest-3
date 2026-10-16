# Python editor

CodeMirror 6 is bundled locally so the desktop editor works without a CDN.
The same local Python parser highlights Markdown code blocks via Lezer.
The hidden textarea bridges edits to Dioxus. Normal edits are owned by
CodeMirror; delayed `data-editor-value` echoes never replace its document.
Explicit code reset updates increment `data-editor-reset` and supply the new
`data-editor-value`, so resetting still works without interrupting IME input.

To rebuild after changing `editor.js`, run from the repository root:

```powershell
npm.cmd ci --prefix assets/editor
node -e "require('./assets/editor/node_modules/esbuild').buildSync({entryPoints:['assets/editor/editor.js'],bundle:true,minify:true,format:'iife',outfile:'assets/editor/editor.bundle.js',nodePaths:['assets/editor/node_modules']})"
cargo build --bin molip-quest
```

The committed bundle is embedded in the desktop binary. License notices are
included in `THIRD-PARTY-LICENSES.txt`.
