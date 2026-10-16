import assert from 'node:assert/strict';
await import('@marp-team/marp-core');
globalThis.document = { body: {}, querySelectorAll: () => [] };
globalThis.Element = class {};
globalThis.MutationObserver = class { observe() {} };
const { renderDeck } = await import('./slides.js');
const source = `---
theme: molip
---
## 만화와 ** 강조 **
가격이 **높으면** 선택합니다.
**\`amount\`**를 계산합니다.

\`\`\`comic-gen
제목: 두 컷
등장인물:
  강사: {그림: 사람}
컷:
  - 인물: [강사]
    대사: [{화자: 강사, 내용: 첫 번째}]
  - 구성: 이전
    대사: [{화자: 강사, 내용: 두 번째}]
\`\`\`

---
## 코드
\`\`\`python
print('** 원문 **')
\`\`\`
`;
const { html } = renderDeck(source);
assert.equal((html.match(/<section\b/g) || []).length, 3, 'two comic panels must occupy separate slides');
assert.ok(html.includes('<strong>강조</strong>'), 'spaced emphasis must render as bold');
assert.ok(html.includes('<strong>높으면</strong>'), 'Korean emphasis must render as bold');
assert.ok(html.includes('<strong><code>amount</code></strong>'), 'emphasis must preserve inline code formatting');
assert.ok(html.includes('** 원문 **'), 'code fences must preserve literal stars');
assert.ok(html.includes('# molip-panel:0') && html.includes('# molip-panel:1'), 'both panels must remain available');
// Presenter notes: a slide's comment becomes its note, every panel slide of a comic inherits it,
// and directive comments never count as notes.
const noted = renderDeck(`---
theme: molop
---
## 첫 장
<!-- _class: lead -->
본문
<!-- 자, 첫 장에서는 이것만 말합니다. -->

---
## 만화 장
<!-- 만화는 두 컷, 같은 말을 합니다. -->

\`\`\`comic-gen
제목: 두 컷
등장인물:
  강사: {그림: 사람}
컷:
  - 인물: [강사]
    대사: [{화자: 강사, 내용: 첫 번째}]
  - 구성: 이전
    대사: [{화자: 강사, 내용: 두 번째}]
\`\`\`

---
## 셋째 장
`);
assert.deepEqual(noted.notes, ['자, 첫 장에서는 이것만 말합니다.', '만화는 두 컷, 같은 말을 합니다.', '만화는 두 컷, 같은 말을 합니다.', ''], JSON.stringify(noted.notes));
console.log('PASS: one panel per slide, emphasis, code literals, presenter notes');
