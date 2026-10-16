# Comic strips

Course concepts embed short comics as ```` ```comic-gen ```` fences written in the
Korean YAML syntax of [Comic Gen](https://github.com/jhs512/comic-gen)
(authoring reference: https://jhs512.github.io/comic-gen/llm-guide.md).
The Markdown renderer keeps the fence as `pre > code.language-comic-gen`;
`comics.js` replaces each one with a `<figure class="comic-strip">` holding the
SVG of every panel, so the strip reads inline with the surrounding paragraphs.
Inside a slide deck, each panel gets its own slide. The complete comic script is
rendered once so character and previous-panel inheritance are preserved, and each
slide displays its corresponding resolved panel within the available height. Panels keep a
fixed height and only widen, so slide comics are rendered a second time at the width that makes
the tallest panel fill the slide box; diagrams on a panel then stay readable.

`comic-gen.js` is the vendored browser SDK (v0.7.5, an ES module from
`https://cdn.jsdelivr.net/gh/jhs512/comic-gen@v0.7.5/cdn/comic-gen.js`). The app
embeds it as a string and the loader imports it from a Blob URL, so comics work
offline on desktop and Android. Panels may hold Mermaid diagrams: `mermaid.min.js`
(Mermaid 11.17.2, MIT, https://github.com/mermaid-js/mermaid) is vendored too and served
to the SDK's isolated frame from a Blob URL by `comics.js`, so diagrams also render offline.

Editorial rules for new comics live with the course source in `tools/kpc_course/`:
a comic is one Markdown paragraph (no blank lines inside the fence), every
dialogue line fits in two short rows, and the shared cast (강사, 민지, 준호,
파이썬, 빵 공장장, 콜센터 팀장) keeps the same appearance across units.
