/*! Comic Gen browser SDK v0.7.5
Bundled yaml license:
Copyright Eemeli Aro <eemeli@gmail.com>

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

*/
const pe = Object.freeze({
  skinColor: "#f0c8a6",
  hairStyle: "short",
  hairColor: "#47362f",
  outfit: "shirt",
  outfitColor: "#647bd6",
  glasses: !1
}), Et = (n) => {
  if (n.length !== 4 && n.length !== 7 || !/^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i.test(n))
    throw new Error("사람의 외형 색상은 #RGB 또는 #RRGGBB로 작성하세요.");
  return n;
};
function Cn(n = pe) {
  const e = Et(n.skinColor), t = Et(n.hairColor), s = Et(n.outfitColor), i = {
    short: "",
    bob: `<path d="M-37 -24Q-42 -56 0 -58Q42 -56 37 -24L41 17Q29 26 20 15H-20Q-29 26 -41 17Z" fill="${t}"/>`,
    long: `<path d="M-37 -24Q-43 -56 0 -58Q43 -56 37 -24L43 46Q30 53 23 40H-23Q-30 53 -43 46Z" fill="${t}"/>`,
    bald: ""
  }, r = {
    short: `<path d="M-36 -24Q-40 -52 -11 -57Q21 -63 36 -37L37 -23L29 -32L26 -43Q13 -43 3 -48Q-9 -42 -25 -43L-30 -31Z" fill="${t}"/>`,
    bob: `<path d="M-37 -23Q-42 -55 0 -58Q42 -55 37 -23L32 8L28 -13L27 -41Q7 -47 -8 -43Q-18 -46 -27 -41L-28 -13L-32 8Z" fill="${t}"/>`,
    long: `<path d="M-37 -24Q-41 -55 0 -58Q41 -55 37 -24L32 16L28 -9L27 -41Q12 -46 2 -50Q-9 -43 -27 -39L-28 -9L-32 16Z" fill="${t}"/>`,
    bald: ""
  }, o = {
    shirt: `<path d="M-16 21L-34 25Q-43 29 -45 38L-49 44L-37 49L-34 56H34L37 49L49 44L45 38Q43 29 34 25L16 21Z" fill="${s}"/><path d="M-15 23Q0 38 15 23M-45 39L-36 43M36 43L45 39" fill="none"/>`,
    jacket: `<path d="M-16 21L-34 25Q-43 29 -45 39L-49 47L-36 51L-33 56H33L36 51L49 47L45 39Q43 29 34 25L16 21Z" fill="${s}"/><path d="M-12 23L0 31L12 23L16 56H-16Z" fill="#f4f5f9"/><path d="M-16 22L-23 32L-12 36L-17 55M16 22L23 32L12 36L17 55M-31 41H-21M21 41H31" fill="none"/>`,
    hoodie: `<path d="M-17 21L-33 25Q-43 29 -45 39L-49 47L-36 52L-33 56H33L36 52L49 47L45 39Q43 29 33 25L17 21Z" fill="${s}"/><path d="M-21 20Q-29 23 -25 32Q0 45 25 32Q29 23 21 20L12 22Q0 32 -12 22Z" fill="${s}"/><path d="M-17 43H17L21 54H-21ZM-10 32V40M10 32V40" fill="none"/>`
  };
  if (!Object.hasOwn(r, n.hairStyle) || !Object.hasOwn(o, n.outfit))
    throw new Error("지원하는 머리 모양과 옷을 선택하세요.");
  const a = (d, m) => m ? `<g data-human-part="${d}">${m}</g>` : "", c = n.glasses ? '<g data-human-part="glasses" fill="none" stroke-width="2.2"><circle cx="-17" cy="-20" r="11"/><circle cx="17" cy="-20" r="11"/><path d="M-6 -20Q0 -24 6 -20M-28 -22L-34 -25M28 -22L34 -25"/></g>' : "", l = `<g data-human="true" data-hair-style="${n.hairStyle}" data-outfit="${n.outfit}">${a("hair-back", i[n.hairStyle])}${a("outfit", o[n.outfit])}${a("neck", `<path d="M-10 11V24Q0 33 10 24V11Z" fill="${e}"/>`)}${a("ears", `<ellipse cx="-36" cy="-17" rx="7" ry="9" fill="${e}"/><ellipse cx="36" cy="-17" rx="7" ry="9" fill="${e}"/><path d="M-37 -21Q-41 -17 -37 -13M37 -21Q41 -17 37 -13" fill="none" stroke-width="1.8"/>`)}${a("face", `<path d="M-34 -25Q-36 -54 0 -55Q36 -54 34 -25L32 -5Q29 18 0 21Q-29 18 -32 -5Z" fill="${e}"/><g stroke="none" fill="#df8e8b" fill-opacity=".28"><ellipse cx="-24" cy="-8" rx="5" ry="3"/><ellipse cx="24" cy="-8" rx="5" ry="3"/></g>`)}${a("hair-front", r[n.hairStyle])}${a("nose", '<path d="M0 -13V-7H3" fill="none" stroke-width="1.8"/>')}${c}</g>`, f = `<path d="M-49 43Q-54 46 -51 51L-48 55Q-44 59 -40 55L-36 50Q-34 46 -38 43L-40 42Z" fill="${e}"/><path d="M-46 48L-43 51M-42 46L-39 49" fill="none" stroke-width="1.5"/>`, u = `<g data-human-part="arm-left" fill="none" stroke-linecap="round"><path d="M-36 34L-63 25" stroke-width="15"/><path d="M-36 34L-63 25" stroke="${s}" stroke-width="9.4"/></g><g data-hand="point"><path d="M-70 20H-86a3 3 0 0 0 0 6H-70Z" fill="${e}" stroke-width="2.2"/><circle cx="-67" cy="24" r="9.5" fill="${e}"/><path d="M-64 19Q-61 24 -64 29" fill="none" stroke-width="1.8"/></g>`;
  return {
    body: l,
    faceY: -16,
    color: e,
    pointGesture: u,
    restingHands: {
      left: `<g data-human-part="resting-hand-left">${f}</g>`,
      right: `<g data-human-part="resting-hand-right" transform="scale(-1 1)">${f}</g>`
    }
  };
}
const Fs = "6", In = {
  client: {
    color: "#9fcdfa",
    faceY: 0,
    body: '<circle r="56" fill="#badcff"/><path d="M-24 -58h48" fill="none"/>'
  },
  server: {
    color: "#efb970",
    faceY: 0,
    body: '<rect x="-52" y="-54" width="104" height="108" rx="22" fill="#ffe0a8"/><path d="M-34 -36h42M-34 -27h26"/><circle cx="30" cy="-33" r="3" fill="#7bb79b"/>'
  },
  database: {
    color: "#b4a0ed",
    faceY: 5,
    body: '<path d="M-52 -39v79c0 23 104 23 104 0v-79" fill="#daccff"/><ellipse cy="-39" rx="52" ry="18" fill="#ece4ff"/><path d="M-52 24c0 23 104 23 104 0" fill="none"/>'
  },
  human: Cn()
};
function fn(n) {
  return n.asset === "human" ? Cn(n.appearance) : In[n.asset];
}
const jn = {
  neutral: '<circle cx="-17" cy="-4" r="3.5"/><circle cx="17" cy="-4" r="3.5"/><path d="M-10 17q10 7 20 0" fill="none"/>',
  happy: '<path d="M-25 -2q8 -12 16 0m18 0q8 -12 16 0M-13 16q13 18 26 0" fill="none"/>',
  confused: '<circle cx="-17" cy="-4" r="3.5"/><circle cx="17" cy="-4" r="3.5"/><path d="M-24 -17l13 -5m21 1 14 4M-8 18q8 -6 16 0" fill="none"/>',
  sad: '<circle cx="-17" cy="-4" r="3.5"/><circle cx="17" cy="-4" r="3.5"/><path d="M-12 23q12 -14 24 0" fill="none"/>',
  angry: '<path d="M-25 -16l15 6m20 0 15 -6M-10 20h20" fill="none"/><circle cx="-17" cy="-1" r="3"/><circle cx="17" cy="-1" r="3"/>'
}, Bn = {
  wave: '<g data-hand="wave"><circle cx="-65" cy="-22" r="12" fill="white"/><path d="M-77 -42l-4 -8m15 2v-10m13 17 5 -7" fill="none"/></g>',
  point: '<g data-hand="point"><circle cx="-65" cy="0" r="11" fill="white"/><path d="M-77 0h-13" fill="none"/></g>'
}, Lt = "M-65 -9Q-76 -9 -79 -18L-85 -22Q-89 -25 -86 -28Q-83 -31 -80 -28L-83.5 -31V-46Q-83.5 -50 -79.75 -50Q-76 -50 -76 -46V-31Q-76 -28 -71.5 -31V-47Q-71.5 -51 -67.75 -51Q-64 -51 -64 -47V-31Q-64 -28 -59.5 -31V-47Q-59.5 -51 -55.75 -51Q-52 -51 -52 -47V-31Q-52 -28 -47.5 -31V-46Q-47.5 -50 -43.75 -50Q-40 -50 -40 -46V-22Q-40 -11 -57 -9Z", Ks = {
  wave: `<g data-hand="wave" stroke-linejoin="round"><g data-wave-trail="left" transform="translate(-54 -9) rotate(-28) scale(.85) translate(65 9)" opacity=".3"><path d="${Lt}" fill="white"/></g><g data-wave-trail="center" transform="translate(-65 -9) scale(.93) translate(65 9)" opacity=".38"><path d="${Lt}" fill="white"/></g><path d="M-89 -38Q-86 -56 -72 -63M-83 -35Q-81 -50 -68 -56" fill="none" stroke="#586c8c" stroke-width="2.7"/><g data-wave-pose="current" transform="translate(-69 -9) rotate(35) translate(65 9)"><path d="${Lt}" fill="white"/></g></g>`,
  point: '<g data-hand="point" stroke-linejoin="round"><path d="M-72 -4H-85a4 4 0 0 0 0 8H-74l3 5q3 4 9 2l5 -3q4 -2 3 -7l-1 -6q-1 -5 -6 -6h-4q-5 -1 -7 3Z" fill="white"/><path d="M-68 -7q3 5 8 4" fill="none" stroke-width="2"/></g>'
}, ot = {
  request: '<rect x="-18" y="-13" width="36" height="26" rx="4" fill="#f9f0cd"/><path d="M-18 -13L0 1l18 -14" fill="none"/>',
  data: '<path d="M-16 -12v23c0 10 32 10 32 0v-23" fill="#daccff"/><ellipse cy="-12" rx="16" ry="6" fill="#ece4ff"/>',
  key: '<circle cx="-10" r="9" fill="#ffe0a8"/><path d="M0 0h21m-5 0v8m-8 -8v6" fill="none"/>'
};
function H(n) {
  return n.replace(
    /[&<>"']/g,
    (e) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&apos;"
    })[e]
  );
}
class qs {
  constructor(e = 2e6) {
    if (this.maxBytes = e, !Number.isFinite(e) || e < 0)
      throw new Error("캐시 크기는 0 이상의 숫자여야 합니다.");
  }
  maxBytes;
  entries = /* @__PURE__ */ new Map();
  size = 0;
  get bytes() {
    return this.size;
  }
  get(e) {
    const t = this.entries.get(e);
    return t && (this.entries.delete(e), this.entries.set(e, t)), t;
  }
  set(e, t) {
    const s = this.entries.get(e);
    s && (this.size -= s.bytes, this.entries.delete(e));
    const i = (e.length + t.markup.length) * 2;
    if (!(i > this.maxBytes)) {
      for (; this.size + i > this.maxBytes && this.entries.size; ) {
        const r = this.entries.keys().next().value;
        this.size -= this.entries.get(r).bytes, this.entries.delete(r);
      }
      this.entries.set(e, { ...t, bytes: i }), this.size += i;
    }
  }
  clear() {
    this.entries.clear(), this.size = 0;
  }
}
const Qt = /* @__PURE__ */ Symbol.for("yaml.alias"), Bt = /* @__PURE__ */ Symbol.for("yaml.document"), le = /* @__PURE__ */ Symbol.for("yaml.map"), _n = /* @__PURE__ */ Symbol.for("yaml.pair"), te = /* @__PURE__ */ Symbol.for("yaml.scalar"), Me = /* @__PURE__ */ Symbol.for("yaml.seq"), X = /* @__PURE__ */ Symbol.for("yaml.node.type"), Ce = (n) => !!n && typeof n == "object" && n[X] === Qt, ut = (n) => !!n && typeof n == "object" && n[X] === Bt, ze = (n) => !!n && typeof n == "object" && n[X] === le, V = (n) => !!n && typeof n == "object" && n[X] === _n, K = (n) => !!n && typeof n == "object" && n[X] === te, He = (n) => !!n && typeof n == "object" && n[X] === Me;
function q(n) {
  if (n && typeof n == "object")
    switch (n[X]) {
      case le:
      case Me:
        return !0;
    }
  return !1;
}
function R(n) {
  if (n && typeof n == "object")
    switch (n[X]) {
      case Qt:
      case le:
      case te:
      case Me:
        return !0;
    }
  return !1;
}
const Pn = (n) => (K(n) || q(n)) && !!n.anchor, me = /* @__PURE__ */ Symbol("break visit"), Rs = /* @__PURE__ */ Symbol("skip children"), Ke = /* @__PURE__ */ Symbol("remove node");
function Ie(n, e) {
  const t = Vs(e);
  ut(n) ? Ee(null, n.contents, t, Object.freeze([n])) === Ke && (n.contents = null) : Ee(null, n, t, Object.freeze([]));
}
Ie.BREAK = me;
Ie.SKIP = Rs;
Ie.REMOVE = Ke;
function Ee(n, e, t, s) {
  const i = Us(n, e, t, s);
  if (R(i) || V(i))
    return Qs(n, s, i), Ee(n, i, t, s);
  if (typeof i != "symbol") {
    if (q(e)) {
      s = Object.freeze(s.concat(e));
      for (let r = 0; r < e.items.length; ++r) {
        const o = Ee(r, e.items[r], t, s);
        if (typeof o == "number")
          r = o - 1;
        else {
          if (o === me)
            return me;
          o === Ke && (e.items.splice(r, 1), r -= 1);
        }
      }
    } else if (V(e)) {
      s = Object.freeze(s.concat(e));
      const r = Ee("key", e.key, t, s);
      if (r === me)
        return me;
      r === Ke && (e.key = null);
      const o = Ee("value", e.value, t, s);
      if (o === me)
        return me;
      o === Ke && (e.value = null);
    }
  }
  return i;
}
function Vs(n) {
  return typeof n == "object" && (n.Collection || n.Node || n.Value) ? Object.assign({
    Alias: n.Node,
    Map: n.Node,
    Scalar: n.Node,
    Seq: n.Node
  }, n.Value && {
    Map: n.Value,
    Scalar: n.Value,
    Seq: n.Value
  }, n.Collection && {
    Map: n.Collection,
    Seq: n.Collection
  }, n) : n;
}
function Us(n, e, t, s) {
  if (typeof t == "function")
    return t(n, e, s);
  if (ze(e))
    return t.Map?.(n, e, s);
  if (He(e))
    return t.Seq?.(n, e, s);
  if (V(e))
    return t.Pair?.(n, e, s);
  if (K(e))
    return t.Scalar?.(n, e, s);
  if (Ce(e))
    return t.Alias?.(n, e, s);
}
function Qs(n, e, t) {
  const s = e[e.length - 1];
  if (q(s))
    s.items[n] = t;
  else if (V(s))
    n === "key" ? s.key = t : s.value = t;
  else if (ut(s))
    s.contents = t;
  else {
    const i = Ce(s) ? "alias" : "scalar";
    throw new Error(`Cannot replace node with ${i} parent`);
  }
}
const Gs = {
  "!": "%21",
  ",": "%2C",
  "[": "%5B",
  "]": "%5D",
  "{": "%7B",
  "}": "%7D"
}, zs = (n) => n.replace(/[!,[\]{}]/g, (e) => Gs[e]);
class G {
  constructor(e, t) {
    this.docStart = null, this.docEnd = !1, this.yaml = Object.assign({}, G.defaultYaml, e), this.tags = Object.assign({}, G.defaultTags, t);
  }
  clone() {
    const e = new G(this.yaml, this.tags);
    return e.docStart = this.docStart, e;
  }
  /**
   * During parsing, get a Directives instance for the current document and
   * update the stream state according to the current version's spec.
   */
  atDocument() {
    const e = new G(this.yaml, this.tags);
    switch (this.yaml.version) {
      case "1.1":
        this.atNextDocument = !0;
        break;
      case "1.2":
        this.atNextDocument = !1, this.yaml = {
          explicit: G.defaultYaml.explicit,
          version: "1.2"
        }, this.tags = Object.assign({}, G.defaultTags);
        break;
    }
    return e;
  }
  /**
   * @param onError - May be called even if the action was successful
   * @returns `true` on success
   */
  add(e, t) {
    this.atNextDocument && (this.yaml = { explicit: G.defaultYaml.explicit, version: "1.1" }, this.tags = Object.assign({}, G.defaultTags), this.atNextDocument = !1);
    const s = e.trim().split(/[ \t]+/), i = s.shift();
    switch (i) {
      case "%TAG": {
        if (s.length !== 2 && (t(0, "%TAG directive should contain exactly two parts"), s.length < 2))
          return !1;
        const [r, o] = s;
        return this.tags[r] = o, !0;
      }
      case "%YAML": {
        if (this.yaml.explicit = !0, s.length !== 1)
          return t(0, "%YAML directive should contain exactly one part"), !1;
        const [r] = s;
        if (r === "1.1" || r === "1.2")
          return this.yaml.version = r, !0;
        {
          const o = /^\d+\.\d+$/.test(r);
          return t(6, `Unsupported YAML version ${r}`, o), !1;
        }
      }
      default:
        return t(0, `Unknown directive ${i}`, !0), !1;
    }
  }
  /**
   * Resolves a tag, matching handles to those defined in %TAG directives.
   *
   * @returns Resolved tag, which may also be the non-specific tag `'!'` or a
   *   `'!local'` tag, or `null` if unresolvable.
   */
  tagName(e, t) {
    if (e === "!")
      return "!";
    if (e[0] !== "!")
      return t(`Not a valid tag: ${e}`), null;
    if (e[1] === "<") {
      const o = e.slice(2, -1);
      return o === "!" || o === "!!" ? (t(`Verbatim tags aren't resolved, so ${e} is invalid.`), null) : (e[e.length - 1] !== ">" && t("Verbatim tags must end with a >"), o);
    }
    const [, s, i] = e.match(/^(.*!)([^!]*)$/s);
    i || t(`The ${e} tag has no suffix`);
    const r = this.tags[s];
    if (r)
      try {
        return r + decodeURIComponent(i);
      } catch (o) {
        return t(String(o)), null;
      }
    return s === "!" ? e : (t(`Could not resolve tag: ${e}`), null);
  }
  /**
   * Given a fully resolved tag, returns its printable string form,
   * taking into account current tag prefixes and defaults.
   */
  tagString(e) {
    for (const [t, s] of Object.entries(this.tags))
      if (e.startsWith(s))
        return t + zs(e.substring(s.length));
    return e[0] === "!" ? e : `!<${e}>`;
  }
  toString(e) {
    const t = this.yaml.explicit ? [`%YAML ${this.yaml.version || "1.2"}`] : [], s = Object.entries(this.tags);
    let i;
    if (e && s.length > 0 && R(e.contents)) {
      const r = {};
      Ie(e.contents, (o, a) => {
        R(a) && a.tag && (r[a.tag] = !0);
      }), i = Object.keys(r);
    } else
      i = [];
    for (const [r, o] of s)
      r === "!!" && o === "tag:yaml.org,2002:" || (!e || i.some((a) => a.startsWith(o))) && t.push(`%TAG ${r} ${o}`);
    return t.join(`
`);
  }
}
G.defaultYaml = { explicit: !1, version: "1.2" };
G.defaultTags = { "!!": "tag:yaml.org,2002:" };
function Dn(n) {
  if (/[\x00-\x19\s,[\]{}]/.test(n)) {
    const t = `Anchor must not contain whitespace or control characters: ${JSON.stringify(n)}`;
    throw new Error(t);
  }
  return !0;
}
function Fn(n) {
  const e = /* @__PURE__ */ new Set();
  return Ie(n, {
    Value(t, s) {
      s.anchor && e.add(s.anchor);
    }
  }), e;
}
function Kn(n, e) {
  for (let t = 1; ; ++t) {
    const s = `${n}${t}`;
    if (!e.has(s))
      return s;
  }
}
function Hs(n, e) {
  const t = [], s = /* @__PURE__ */ new Map();
  let i = null;
  return {
    onAnchor: (r) => {
      t.push(r), i ?? (i = Fn(n));
      const o = Kn(e, i);
      return i.add(o), o;
    },
    /**
     * With circular references, the source node is only resolved after all
     * of its child nodes are. This is why anchors are set only after all of
     * the nodes have been created.
     */
    setAnchors: () => {
      for (const r of t) {
        const o = s.get(r);
        if (typeof o == "object" && o.anchor && (K(o.node) || q(o.node)))
          o.node.anchor = o.anchor;
        else {
          const a = new Error("Failed to resolve repeated object (this should not happen)");
          throw a.source = r, a;
        }
      }
    },
    sourceObjects: s
  };
}
function Le(n, e, t, s) {
  if (s && typeof s == "object")
    if (Array.isArray(s))
      for (let i = 0, r = s.length; i < r; ++i) {
        const o = s[i], a = Le(n, s, String(i), o);
        a === void 0 ? delete s[i] : a !== o && (s[i] = a);
      }
    else if (s instanceof Map)
      for (const i of Array.from(s.keys())) {
        const r = s.get(i), o = Le(n, s, i, r);
        o === void 0 ? s.delete(i) : o !== r && s.set(i, o);
      }
    else if (s instanceof Set)
      for (const i of Array.from(s)) {
        const r = Le(n, s, i, i);
        r === void 0 ? s.delete(i) : r !== i && (s.delete(i), s.add(r));
      }
    else
      for (const [i, r] of Object.entries(s)) {
        const o = Le(n, s, i, r);
        o === void 0 ? delete s[i] : o !== r && (s[i] = o);
      }
  return n.call(e, t, s);
}
function J(n, e, t) {
  if (Array.isArray(n))
    return n.map((s, i) => J(s, String(i), t));
  if (n && typeof n.toJSON == "function") {
    if (!t || !Pn(n))
      return n.toJSON(e, t);
    const s = { aliasCount: 0, count: 1, res: void 0 };
    t.anchors.set(n, s), t.onCreate = (r) => {
      s.res = r, delete t.onCreate;
    };
    const i = n.toJSON(e, t);
    return t.onCreate && t.onCreate(i), i;
  }
  return typeof n == "bigint" && !t?.keep ? Number(n) : n;
}
class Gt {
  constructor(e) {
    Object.defineProperty(this, X, { value: e });
  }
  /** Create a copy of this node.  */
  clone() {
    const e = Object.create(Object.getPrototypeOf(this), Object.getOwnPropertyDescriptors(this));
    return this.range && (e.range = this.range.slice()), e;
  }
  /** A plain JavaScript representation of this node. */
  toJS(e, { mapAsMap: t, maxAliasCount: s, onAnchor: i, reviver: r } = {}) {
    if (!ut(e))
      throw new TypeError("A document argument is required");
    const o = {
      anchors: /* @__PURE__ */ new Map(),
      doc: e,
      keep: !0,
      mapAsMap: t === !0,
      mapKeyWarned: !1,
      maxAliasCount: typeof s == "number" ? s : 100
    }, a = J(this, "", o);
    if (typeof i == "function")
      for (const { count: c, res: l } of o.anchors.values())
        i(l, c);
    return typeof r == "function" ? Le(r, { "": a }, "", a) : a;
  }
}
class zt extends Gt {
  constructor(e) {
    super(Qt), this.source = e, Object.defineProperty(this, "tag", {
      set() {
        throw new Error("Alias nodes cannot have tags");
      }
    });
  }
  /**
   * Resolve the value of this alias within `doc`, finding the last
   * instance of the `source` anchor before this node.
   */
  resolve(e, t) {
    if (t?.maxAliasCount === 0)
      throw new ReferenceError("Alias resolution is disabled");
    let s;
    t?.aliasResolveCache ? s = t.aliasResolveCache : (s = [], Ie(e, {
      Node: (r, o) => {
        (Ce(o) || Pn(o)) && s.push(o);
      }
    }), t && (t.aliasResolveCache = s));
    let i;
    for (const r of s) {
      if (r === this)
        break;
      r.anchor === this.source && (i = r);
    }
    if (i && t) {
      const { anchors: r, doc: o, maxAliasCount: a } = t;
      let c = r.get(i);
      if (c || (J(i, null, t), c = r.get(i)), c?.res === void 0) {
        const l = "This should not happen: Alias anchor was not resolved?";
        throw new ReferenceError(l);
      }
      if (a >= 0 && (c.count += 1, c.aliasCount === 0 && (c.aliasCount = nt(o, i, r)), c.count * c.aliasCount > a)) {
        const l = "Excessive alias count indicates a resource exhaustion attack";
        throw new ReferenceError(l);
      }
    }
    return i;
  }
  toJSON(e, t) {
    if (!t)
      return { source: this.source };
    const s = this.resolve(t.doc, t);
    if (!s) {
      const i = `Unresolved alias (the anchor must be set before the alias): ${this.source}`;
      throw new ReferenceError(i);
    }
    return t.anchors.get(s).res;
  }
  toString(e, t, s) {
    const i = `*${this.source}`;
    if (e) {
      if (Dn(this.source), e.options.verifyAliasOrder && !e.anchors.has(this.source)) {
        const r = `Unresolved alias (the anchor must be set before the alias): ${this.source}`;
        throw new Error(r);
      }
      if (e.implicitKey)
        return `${i} `;
    }
    return i;
  }
}
function nt(n, e, t) {
  if (Ce(e)) {
    const s = e.resolve(n), i = t && s && t.get(s);
    return i ? i.count * i.aliasCount : 0;
  } else if (q(e)) {
    let s = 0;
    for (const i of e.items) {
      const r = nt(n, i, t);
      r > s && (s = r);
    }
    return s;
  } else if (V(e)) {
    const s = nt(n, e.key, t), i = nt(n, e.value, t);
    return Math.max(s, i);
  }
  return 1;
}
const qn = (n) => !n || typeof n != "function" && typeof n != "object";
class O extends Gt {
  constructor(e) {
    super(te), this.value = e;
  }
  toJSON(e, t) {
    return t?.keep ? this.value : J(this.value, e, t);
  }
  toString() {
    return String(this.value);
  }
}
O.BLOCK_FOLDED = "BLOCK_FOLDED";
O.BLOCK_LITERAL = "BLOCK_LITERAL";
O.PLAIN = "PLAIN";
O.QUOTE_DOUBLE = "QUOTE_DOUBLE";
O.QUOTE_SINGLE = "QUOTE_SINGLE";
const Ys = "tag:yaml.org,2002:";
function Ws(n, e, t) {
  if (e) {
    const s = t.filter((r) => r.tag === e), i = s.find((r) => !r.format) ?? s[0];
    if (!i)
      throw new Error(`Tag ${e} not found`);
    return i;
  }
  return t.find((s) => s.identify?.(n) && !s.format);
}
function Ve(n, e, t) {
  if (ut(n) && (n = n.contents), R(n))
    return n;
  if (V(n)) {
    const u = t.schema[le].createNode?.(t.schema, null, t);
    return u.items.push(n), u;
  }
  (n instanceof String || n instanceof Number || n instanceof Boolean || typeof BigInt < "u" && n instanceof BigInt) && (n = n.valueOf());
  const { aliasDuplicateObjects: s, onAnchor: i, onTagObj: r, schema: o, sourceObjects: a } = t;
  let c;
  if (s && n && typeof n == "object") {
    if (c = a.get(n), c)
      return c.anchor ?? (c.anchor = i(n)), new zt(c.anchor);
    c = { anchor: null, node: null }, a.set(n, c);
  }
  e?.startsWith("!!") && (e = Ys + e.slice(2));
  let l = Ws(n, e, o.tags);
  if (!l) {
    if (n && typeof n.toJSON == "function" && (n = n.toJSON()), !n || typeof n != "object") {
      const u = new O(n);
      return c && (c.node = u), u;
    }
    l = n instanceof Map ? o[le] : Symbol.iterator in Object(n) ? o[Me] : o[le];
  }
  r && (r(l), delete t.onTagObj);
  const f = l?.createNode ? l.createNode(t.schema, n, t) : typeof l?.nodeClass?.from == "function" ? l.nodeClass.from(t.schema, n, t) : new O(n);
  return e ? f.tag = e : l.default || (f.tag = l.tag), c && (c.node = f), f;
}
function at(n, e, t) {
  let s = t;
  for (let i = e.length - 1; i >= 0; --i) {
    const r = e[i];
    if (typeof r == "number" && Number.isInteger(r) && r >= 0) {
      const o = [];
      o[r] = s, s = o;
    } else
      s = /* @__PURE__ */ new Map([[r, s]]);
  }
  return Ve(s, void 0, {
    aliasDuplicateObjects: !1,
    keepUndefined: !1,
    onAnchor: () => {
      throw new Error("This should not happen, please report a bug.");
    },
    schema: n,
    sourceObjects: /* @__PURE__ */ new Map()
  });
}
const De = (n) => n == null || typeof n == "object" && !!n[Symbol.iterator]().next().done;
class Rn extends Gt {
  constructor(e, t) {
    super(e), Object.defineProperty(this, "schema", {
      value: t,
      configurable: !0,
      enumerable: !1,
      writable: !0
    });
  }
  /**
   * Create a copy of this collection.
   *
   * @param schema - If defined, overwrites the original's schema
   */
  clone(e) {
    const t = Object.create(Object.getPrototypeOf(this), Object.getOwnPropertyDescriptors(this));
    return e && (t.schema = e), t.items = t.items.map((s) => R(s) || V(s) ? s.clone(e) : s), this.range && (t.range = this.range.slice()), t;
  }
  /**
   * Adds a value to the collection. For `!!map` and `!!omap` the value must
   * be a Pair instance or a `{ key, value }` object, which may not have a key
   * that already exists in the map.
   */
  addIn(e, t) {
    if (De(e))
      this.add(t);
    else {
      const [s, ...i] = e, r = this.get(s, !0);
      if (q(r))
        r.addIn(i, t);
      else if (r === void 0 && this.schema)
        this.set(s, at(this.schema, i, t));
      else
        throw new Error(`Expected YAML collection at ${s}. Remaining path: ${i}`);
    }
  }
  /**
   * Removes a value from the collection.
   * @returns `true` if the item was found and removed.
   */
  deleteIn(e) {
    const [t, ...s] = e;
    if (s.length === 0)
      return this.delete(t);
    const i = this.get(t, !0);
    if (q(i))
      return i.deleteIn(s);
    throw new Error(`Expected YAML collection at ${t}. Remaining path: ${s}`);
  }
  /**
   * Returns item at `key`, or `undefined` if not found. By default unwraps
   * scalar values from their surrounding node; to disable set `keepScalar` to
   * `true` (collections are always returned intact).
   */
  getIn(e, t) {
    const [s, ...i] = e, r = this.get(s, !0);
    return i.length === 0 ? !t && K(r) ? r.value : r : q(r) ? r.getIn(i, t) : void 0;
  }
  hasAllNullValues(e) {
    return this.items.every((t) => {
      if (!V(t))
        return !1;
      const s = t.value;
      return s == null || e && K(s) && s.value == null && !s.commentBefore && !s.comment && !s.tag;
    });
  }
  /**
   * Checks if the collection includes a value with the key `key`.
   */
  hasIn(e) {
    const [t, ...s] = e;
    if (s.length === 0)
      return this.has(t);
    const i = this.get(t, !0);
    return q(i) ? i.hasIn(s) : !1;
  }
  /**
   * Sets a value in this collection. For `!!set`, `value` needs to be a
   * boolean to add/remove the item from the set.
   */
  setIn(e, t) {
    const [s, ...i] = e;
    if (i.length === 0)
      this.set(s, t);
    else {
      const r = this.get(s, !0);
      if (q(r))
        r.setIn(i, t);
      else if (r === void 0 && this.schema)
        this.set(s, at(this.schema, i, t));
      else
        throw new Error(`Expected YAML collection at ${s}. Remaining path: ${i}`);
    }
  }
}
const Js = (n) => n.replace(/^(?!$)(?: $)?/gm, "#");
function ne(n, e) {
  return /^\n+$/.test(n) ? n.substring(1) : e ? n.replace(/^(?! *$)/gm, e) : n;
}
const ge = (n, e, t) => n.endsWith(`
`) ? ne(t, e) : t.includes(`
`) ? `
` + ne(t, e) : (n.endsWith(" ") ? "" : " ") + t, Vn = "flow", _t = "block", st = "quoted";
function ht(n, e, t = "flow", { indentAtStart: s, lineWidth: i = 80, minContentWidth: r = 20, onFold: o, onOverflow: a } = {}) {
  if (!i || i < 0)
    return n;
  i < r && (r = 0);
  const c = Math.max(1 + r, 1 + i - e.length);
  if (n.length <= c)
    return n;
  const l = [], f = {};
  let u = i - e.length;
  typeof s == "number" && (s > i - Math.max(2, r) ? l.push(0) : u = i - s);
  let d, m, y = !1, h = -1, g = -1, w = -1;
  t === _t && (h = un(n, h, e.length), h !== -1 && (u = h + c));
  for (let k; k = n[h += 1]; ) {
    if (t === st && k === "\\") {
      switch (g = h, n[h + 1]) {
        case "x":
          h += 3;
          break;
        case "u":
          h += 5;
          break;
        case "U":
          h += 9;
          break;
        default:
          h += 1;
      }
      w = h;
    }
    if (k === `
`)
      t === _t && (h = un(n, h, e.length)), u = h + e.length + c, d = void 0;
    else {
      if (k === " " && m && m !== " " && m !== `
` && m !== "	") {
        const p = n[h + 1];
        p && p !== " " && p !== `
` && p !== "	" && (d = h);
      }
      if (h >= u)
        if (d)
          l.push(d), u = d + c, d = void 0;
        else if (t === st) {
          for (; m === " " || m === "	"; )
            m = k, k = n[h += 1], y = !0;
          const p = h > w + 1 ? h - 2 : g - 1;
          if (f[p])
            return n;
          l.push(p), f[p] = !0, u = p + c, d = void 0;
        } else
          y = !0;
    }
    m = k;
  }
  if (y && a && a(), l.length === 0)
    return n;
  o && o();
  let S = n.slice(0, l[0]);
  for (let k = 0; k < l.length; ++k) {
    const p = l[k], b = l[k + 1] || n.length;
    p === 0 ? S = `
${e}${n.slice(0, b)}` : (t === st && f[p] && (S += `${n[p]}\\`), S += `
${e}${n.slice(p + 1, b)}`);
  }
  return S;
}
function un(n, e, t) {
  let s = e, i = e + 1, r = n[i];
  for (; r === " " || r === "	"; )
    if (e < i + t)
      r = n[++e];
    else {
      do
        r = n[++e];
      while (r && r !== `
`);
      s = e, i = e + 1, r = n[i];
    }
  return s;
}
const dt = (n, e) => ({
  indentAtStart: e ? n.indent.length : n.indentAtStart,
  lineWidth: n.options.lineWidth,
  minContentWidth: n.options.minContentWidth
}), pt = (n) => /^(%|---|\.\.\.)/m.test(n);
function Xs(n, e, t) {
  if (!e || e < 0)
    return !1;
  const s = e - t, i = n.length;
  if (i <= s)
    return !1;
  for (let r = 0, o = 0; r < i; ++r)
    if (n[r] === `
`) {
      if (r - o > s)
        return !0;
      if (o = r + 1, i - o <= s)
        return !1;
    }
  return !0;
}
function qe(n, e) {
  const t = JSON.stringify(n);
  if (e.options.doubleQuotedAsJSON)
    return t;
  const { implicitKey: s } = e, i = e.options.doubleQuotedMinMultiLineLength, r = e.indent || (pt(n) ? "  " : "");
  let o = "", a = 0;
  for (let c = 0, l = t[c]; l; l = t[++c])
    if (l === " " && t[c + 1] === "\\" && t[c + 2] === "n" && (o += t.slice(a, c) + "\\ ", c += 1, a = c, l = "\\"), l === "\\")
      switch (t[c + 1]) {
        case "u":
          {
            o += t.slice(a, c);
            const f = t.substr(c + 2, 4);
            switch (f) {
              case "0000":
                o += "\\0";
                break;
              case "0007":
                o += "\\a";
                break;
              case "000b":
                o += "\\v";
                break;
              case "001b":
                o += "\\e";
                break;
              case "0085":
                o += "\\N";
                break;
              case "00a0":
                o += "\\_";
                break;
              case "2028":
                o += "\\L";
                break;
              case "2029":
                o += "\\P";
                break;
              default:
                f.substr(0, 2) === "00" ? o += "\\x" + f.substr(2) : o += t.substr(c, 6);
            }
            c += 5, a = c + 1;
          }
          break;
        case "n":
          if (s || t[c + 2] === '"' || t.length < i)
            c += 1;
          else {
            for (o += t.slice(a, c) + `

`; t[c + 2] === "\\" && t[c + 3] === "n" && t[c + 4] !== '"'; )
              o += `
`, c += 2;
            o += r, t[c + 2] === " " && (o += "\\"), c += 1, a = c + 1;
          }
          break;
        default:
          c += 1;
      }
  return o = a ? o + t.slice(a) : t, s ? o : ht(o, r, st, dt(e, !1));
}
function Pt(n, e) {
  if (e.options.singleQuote === !1 || e.implicitKey && n.includes(`
`) || /[ \t]\n|\n[ \t]/.test(n))
    return qe(n, e);
  const t = e.indent || (pt(n) ? "  " : ""), s = "'" + n.replace(/'/g, "''").replace(/\n+/g, `$&
${t}`) + "'";
  return e.implicitKey ? s : ht(s, t, Vn, dt(e, !1));
}
function xe(n, e) {
  const { singleQuote: t } = e.options;
  let s;
  if (t === !1)
    s = qe;
  else {
    const i = n.includes('"'), r = n.includes("'");
    i && !r ? s = Pt : r && !i ? s = qe : s = t ? Pt : qe;
  }
  return s(n, e);
}
let Dt;
try {
  Dt = new RegExp(`(^|(?<!
))
+(?!
|$)`, "g");
} catch {
  Dt = /\n+(?!\n|$)/g;
}
function it({ comment: n, type: e, value: t }, s, i, r) {
  const { blockQuote: o, commentString: a, lineWidth: c } = s.options;
  if (!o || /\n[\t ]+$/.test(t))
    return xe(t, s);
  const l = s.indent || (s.forceBlockIndent || pt(t) ? "  " : ""), f = o === "literal" ? !0 : o === "folded" || e === O.BLOCK_FOLDED ? !1 : e === O.BLOCK_LITERAL ? !0 : !Xs(t, c, l.length);
  if (!t)
    return f ? `|
` : `>
`;
  let u, d;
  for (d = t.length; d > 0; --d) {
    const b = t[d - 1];
    if (b !== `
` && b !== "	" && b !== " ")
      break;
  }
  let m = t.substring(d);
  const y = m.indexOf(`
`);
  y === -1 ? u = "-" : t === m || y !== m.length - 1 ? (u = "+", r && r()) : u = "", m && (t = t.slice(0, -m.length), m[m.length - 1] === `
` && (m = m.slice(0, -1)), m = m.replace(Dt, `$&${l}`));
  let h = !1, g, w = -1;
  for (g = 0; g < t.length; ++g) {
    const b = t[g];
    if (b === " ")
      h = !0;
    else if (b === `
`)
      w = g;
    else
      break;
  }
  let S = t.substring(0, w < g ? w + 1 : g);
  S && (t = t.substring(S.length), S = S.replace(/\n+/g, `$&${l}`));
  let p = (h ? l ? "2" : "1" : "") + u;
  if (n && (p += " " + a(n.replace(/ ?[\r\n]+/g, " ")), i && i()), !f) {
    const b = t.replace(/\n+/g, `
$&`).replace(/(?:^|\n)([\t ].*)(?:([\n\t ]*)\n(?![\n\t ]))?/g, "$1$2").replace(/\n+/g, `$&${l}`);
    let v = !1;
    const x = dt(s, !0);
    o !== "folded" && e !== O.BLOCK_FOLDED && (x.onOverflow = () => {
      v = !0;
    });
    const $ = ht(`${S}${b}${m}`, l, _t, x);
    if (!v)
      return `>${p}
${l}${$}`;
  }
  return t = t.replace(/\n+/g, `$&${l}`), `|${p}
${l}${S}${t}${m}`;
}
function Zs(n, e, t, s) {
  const { type: i, value: r } = n, { actualString: o, implicitKey: a, indent: c, indentStep: l, inFlow: f } = e;
  if (a && r.includes(`
`) || f && /[[\]{},]/.test(r))
    return xe(r, e);
  if (/^[\n\t ,[\]{}#&*!|>'"%@`]|^[?-]$|^[?-][ \t]|[\n:][ \t]|[ \t]\n|[\n\t ]#|[\n\t :]$/.test(r))
    return a || f || !r.includes(`
`) ? xe(r, e) : it(n, e, t, s);
  if (!a && !f && i !== O.PLAIN && r.includes(`
`))
    return it(n, e, t, s);
  if (pt(r)) {
    if (c === "")
      return e.forceBlockIndent = !0, it(n, e, t, s);
    if (a && c === l)
      return xe(r, e);
  }
  const u = r.replace(/\n+/g, `$&
${c}`);
  if (o) {
    const d = (h) => h.default && h.tag !== "tag:yaml.org,2002:str" && h.test?.test(u), { compat: m, tags: y } = e.doc.schema;
    if (y.some(d) || m?.some(d))
      return xe(r, e);
  }
  return a ? u : ht(u, c, Vn, dt(e, !1));
}
function Ht(n, e, t, s) {
  const { implicitKey: i, inFlow: r } = e, o = typeof n.value == "string" ? n : Object.assign({}, n, { value: String(n.value) });
  let { type: a } = n;
  a !== O.QUOTE_DOUBLE && /[\x00-\x08\x0b-\x1f\x7f-\x9f\u{D800}-\u{DFFF}]/u.test(o.value) && (a = O.QUOTE_DOUBLE);
  const c = (f) => {
    switch (f) {
      case O.BLOCK_FOLDED:
      case O.BLOCK_LITERAL:
        return i || r ? xe(o.value, e) : it(o, e, t, s);
      case O.QUOTE_DOUBLE:
        return qe(o.value, e);
      case O.QUOTE_SINGLE:
        return Pt(o.value, e);
      case O.PLAIN:
        return Zs(o, e, t, s);
      default:
        return null;
    }
  };
  let l = c(a);
  if (l === null) {
    const { defaultKeyType: f, defaultStringType: u } = e.options, d = i && f || u;
    if (l = c(d), l === null)
      throw new Error(`Unsupported default string type ${d}`);
  }
  return l;
}
function Un(n, e) {
  const t = Object.assign({
    blockQuote: !0,
    commentString: Js,
    defaultKeyType: null,
    defaultStringType: "PLAIN",
    directives: null,
    doubleQuotedAsJSON: !1,
    doubleQuotedMinMultiLineLength: 40,
    falseStr: "false",
    flowCollectionPadding: !0,
    indentSeq: !0,
    lineWidth: 80,
    minContentWidth: 20,
    nullStr: "null",
    simpleKeys: !1,
    singleQuote: null,
    trailingComma: !1,
    trueStr: "true",
    verifyAliasOrder: !0
  }, n.schema.toStringOptions, e);
  let s;
  switch (t.collectionStyle) {
    case "block":
      s = !1;
      break;
    case "flow":
      s = !0;
      break;
    default:
      s = null;
  }
  return {
    anchors: /* @__PURE__ */ new Set(),
    doc: n,
    flowCollectionPadding: t.flowCollectionPadding ? " " : "",
    indent: "",
    indentStep: typeof t.indent == "number" ? " ".repeat(t.indent) : "  ",
    inFlow: s,
    options: t
  };
}
function ei(n, e) {
  if (e.tag) {
    const i = n.filter((r) => r.tag === e.tag);
    if (i.length > 0)
      return i.find((r) => r.format === e.format) ?? i[0];
  }
  let t, s;
  if (K(e)) {
    s = e.value;
    let i = n.filter((r) => r.identify?.(s));
    if (i.length > 1) {
      const r = i.filter((o) => o.test);
      r.length > 0 && (i = r);
    }
    t = i.find((r) => r.format === e.format) ?? i.find((r) => !r.format);
  } else
    s = e, t = n.find((i) => i.nodeClass && s instanceof i.nodeClass);
  if (!t) {
    const i = s?.constructor?.name ?? (s === null ? "null" : typeof s);
    throw new Error(`Tag not resolved for ${i} value`);
  }
  return t;
}
function ti(n, e, { anchors: t, doc: s }) {
  if (!s.directives)
    return "";
  const i = [], r = (K(n) || q(n)) && n.anchor;
  r && Dn(r) && (t.add(r), i.push(`&${r}`));
  const o = n.tag ?? (e.default ? null : e.tag);
  return o && i.push(s.directives.tagString(o)), i.join(" ");
}
function Ae(n, e, t, s) {
  if (V(n))
    return n.toString(e, t, s);
  if (Ce(n)) {
    if (e.doc.directives)
      return n.toString(e);
    if (e.resolvedAliases?.has(n))
      throw new TypeError("Cannot stringify circular structure without alias nodes");
    e.resolvedAliases ? e.resolvedAliases.add(n) : e.resolvedAliases = /* @__PURE__ */ new Set([n]), n = n.resolve(e.doc);
  }
  let i;
  const r = R(n) ? n : e.doc.createNode(n, { onTagObj: (c) => i = c });
  i ?? (i = ei(e.doc.schema.tags, r));
  const o = ti(r, i, e);
  o.length > 0 && (e.indentAtStart = (e.indentAtStart ?? 0) + o.length + 1);
  const a = typeof i.stringify == "function" ? i.stringify(r, e, t, s) : K(r) ? Ht(r, e, t, s) : r.toString(e, t, s);
  return o ? K(r) || a[0] === "{" || a[0] === "[" ? `${o} ${a}` : `${o}
${e.indent}${a}` : a;
}
function ni({ key: n, value: e }, t, s, i) {
  const { allNullValues: r, doc: o, indent: a, indentStep: c, options: { commentString: l, indentSeq: f, simpleKeys: u } } = t;
  let d = R(n) && n.comment || null;
  if (u) {
    if (d)
      throw new Error("With simple keys, key nodes cannot have comments");
    if (q(n) || !R(n) && typeof n == "object") {
      const x = "With simple keys, collection cannot be used as a key value";
      throw new Error(x);
    }
  }
  let m = !u && (!n || d && e == null && !t.inFlow || q(n) || (K(n) ? n.type === O.BLOCK_FOLDED || n.type === O.BLOCK_LITERAL : typeof n == "object"));
  t = Object.assign({}, t, {
    allNullValues: !1,
    implicitKey: !m && (u || !r),
    indent: a + c
  });
  let y = !1, h = !1, g = Ae(n, t, () => y = !0, () => h = !0);
  if (!m && !t.inFlow && g.length > 1024) {
    if (u)
      throw new Error("With simple keys, single line scalar must not span more than 1024 characters");
    m = !0;
  }
  if (t.inFlow) {
    if (r || e == null)
      return y && s && s(), g === "" ? "?" : m ? `? ${g}` : g;
  } else if (r && !u || e == null && m)
    return g = `? ${g}`, d && !y ? g += ge(g, t.indent, l(d)) : h && i && i(), g;
  y && (d = null), m ? (d && (g += ge(g, t.indent, l(d))), g = `? ${g}
${a}:`) : (g = `${g}:`, d && (g += ge(g, t.indent, l(d))));
  let w, S, k;
  R(e) ? (w = !!e.spaceBefore, S = e.commentBefore, k = e.comment) : (w = !1, S = null, k = null, e && typeof e == "object" && (e = o.createNode(e))), t.implicitKey = !1, !m && !d && K(e) && (t.indentAtStart = g.length + 1), h = !1, !f && c.length >= 2 && !t.inFlow && !m && He(e) && !e.flow && !e.tag && !e.anchor && (t.indent = t.indent.substring(2));
  let p = !1;
  const b = Ae(e, t, () => p = !0, () => h = !0);
  let v = " ";
  if (d || w || S) {
    if (v = w ? `
` : "", S) {
      const x = l(S);
      v += `
${ne(x, t.indent)}`;
    }
    b === "" && !t.inFlow ? v === `
` && k && (v = `

`) : v += `
${t.indent}`;
  } else if (!m && q(e)) {
    const x = b[0], $ = b.indexOf(`
`), N = $ !== -1, C = t.inFlow ?? e.flow ?? e.items.length === 0;
    if (N || !C) {
      let P = !1;
      if (N && (x === "&" || x === "!")) {
        let A = b.indexOf(" ");
        x === "&" && A !== -1 && A < $ && b[A + 1] === "!" && (A = b.indexOf(" ", A + 1)), (A === -1 || $ < A) && (P = !0);
      }
      P || (v = `
${t.indent}`);
    }
  } else (b === "" || b[0] === `
`) && (v = "");
  return g += v + b, t.inFlow ? p && s && s() : k && !p ? g += ge(g, t.indent, l(k)) : h && i && i(), g;
}
function si(n, e) {
  (n === "debug" || n === "warn") && console.warn(e);
}
const Je = "<<", ie = {
  identify: (n) => n === Je || typeof n == "symbol" && n.description === Je,
  default: "key",
  tag: "tag:yaml.org,2002:merge",
  test: /^<<$/,
  resolve: () => Object.assign(new O(Symbol(Je)), {
    addToJSMap: Qn
  }),
  stringify: () => Je
}, ii = (n, e) => (ie.identify(e) || K(e) && (!e.type || e.type === O.PLAIN) && ie.identify(e.value)) && n?.doc.schema.tags.some((t) => t.tag === ie.tag && t.default);
function Qn(n, e, t) {
  const s = Gn(n, t);
  if (He(s))
    for (const i of s.items)
      xt(n, e, i);
  else if (Array.isArray(s))
    for (const i of s)
      xt(n, e, i);
  else
    xt(n, e, s);
}
function xt(n, e, t) {
  const s = Gn(n, t);
  if (!ze(s))
    throw new Error("Merge sources must be maps or map aliases");
  const i = s.toJSON(null, n, Map);
  for (const [r, o] of i)
    e instanceof Map ? e.has(r) || e.set(r, o) : e instanceof Set ? e.add(r) : Object.prototype.hasOwnProperty.call(e, r) || Object.defineProperty(e, r, {
      value: o,
      writable: !0,
      enumerable: !0,
      configurable: !0
    });
  return e;
}
function Gn(n, e) {
  return n && Ce(e) ? e.resolve(n.doc, n) : e;
}
function zn(n, e, { key: t, value: s }) {
  if (R(t) && t.addToJSMap)
    t.addToJSMap(n, e, s);
  else if (ii(n, t))
    Qn(n, e, s);
  else {
    const i = J(t, "", n);
    if (e instanceof Map)
      e.set(i, J(s, i, n));
    else if (e instanceof Set)
      e.add(i);
    else {
      const r = ri(t, i, n), o = J(s, r, n);
      r in e ? Object.defineProperty(e, r, {
        value: o,
        writable: !0,
        enumerable: !0,
        configurable: !0
      }) : e[r] = o;
    }
  }
  return e;
}
function ri(n, e, t) {
  if (e === null)
    return "";
  if (typeof e != "object")
    return String(e);
  if (R(n) && t?.doc) {
    const s = Un(t.doc, {});
    s.anchors = /* @__PURE__ */ new Set();
    for (const r of t.anchors.keys())
      s.anchors.add(r.anchor);
    s.inFlow = !0, s.inStringifyKey = !0;
    const i = n.toString(s);
    if (!t.mapKeyWarned) {
      let r = JSON.stringify(i);
      r.length > 40 && (r = r.substring(0, 36) + '..."'), si(t.doc.options.logLevel, `Keys with collection values will be stringified due to JS Object restrictions: ${r}. Set mapAsMap: true to use object keys.`), t.mapKeyWarned = !0;
    }
    return i;
  }
  return JSON.stringify(e);
}
function Yt(n, e, t) {
  const s = Ve(n, void 0, t), i = Ve(e, void 0, t);
  return new z(s, i);
}
class z {
  constructor(e, t = null) {
    Object.defineProperty(this, X, { value: _n }), this.key = e, this.value = t;
  }
  clone(e) {
    let { key: t, value: s } = this;
    return R(t) && (t = t.clone(e)), R(s) && (s = s.clone(e)), new z(t, s);
  }
  toJSON(e, t) {
    const s = t?.mapAsMap ? /* @__PURE__ */ new Map() : {};
    return zn(t, s, this);
  }
  toString(e, t, s) {
    return e?.doc ? ni(this, e, t, s) : JSON.stringify(this);
  }
}
function Hn(n, e, t) {
  return (e.inFlow ?? n.flow ? ai : oi)(n, e, t);
}
function oi({ comment: n, items: e }, t, { blockItemPrefix: s, flowChars: i, itemIndent: r, onChompKeep: o, onComment: a }) {
  const { indent: c, options: { commentString: l } } = t, f = Object.assign({}, t, { indent: r, type: null });
  let u = !1;
  const d = [];
  for (let y = 0; y < e.length; ++y) {
    const h = e[y];
    let g = null;
    if (R(h))
      !u && h.spaceBefore && d.push(""), lt(t, d, h.commentBefore, u), h.comment && (g = h.comment);
    else if (V(h)) {
      const S = R(h.key) ? h.key : null;
      S && (!u && S.spaceBefore && d.push(""), lt(t, d, S.commentBefore, u));
    }
    u = !1;
    let w = Ae(h, f, () => g = null, () => u = !0);
    g && (w += ge(w, r, l(g))), u && g && (u = !1), d.push(s + w);
  }
  let m;
  if (d.length === 0)
    m = i.start + i.end;
  else {
    m = d[0];
    for (let y = 1; y < d.length; ++y) {
      const h = d[y];
      m += h ? `
${c}${h}` : `
`;
    }
  }
  return n ? (m += `
` + ne(l(n), c), a && a()) : u && o && o(), m;
}
function ai({ items: n }, e, { flowChars: t, itemIndent: s }) {
  const { indent: i, indentStep: r, flowCollectionPadding: o, options: { commentString: a } } = e;
  s += r;
  const c = Object.assign({}, e, {
    indent: s,
    inFlow: !0,
    type: null
  });
  let l = !1, f = 0;
  const u = [];
  for (let y = 0; y < n.length; ++y) {
    const h = n[y];
    let g = null;
    if (R(h))
      h.spaceBefore && u.push(""), lt(e, u, h.commentBefore, !1), h.comment && (g = h.comment);
    else if (V(h)) {
      const S = R(h.key) ? h.key : null;
      S && (S.spaceBefore && u.push(""), lt(e, u, S.commentBefore, !1), S.comment && (l = !0));
      const k = R(h.value) ? h.value : null;
      k ? (k.comment && (g = k.comment), k.commentBefore && (l = !0)) : h.value == null && S?.comment && (g = S.comment);
    }
    g && (l = !0);
    let w = Ae(h, c, () => g = null);
    l || (l = u.length > f || w.includes(`
`)), y < n.length - 1 ? w += "," : e.options.trailingComma && (e.options.lineWidth > 0 && (l || (l = u.reduce((S, k) => S + k.length + 2, 2) + (w.length + 2) > e.options.lineWidth)), l && (w += ",")), g && (w += ge(w, s, a(g))), u.push(w), f = u.length;
  }
  const { start: d, end: m } = t;
  if (u.length === 0)
    return d + m;
  if (!l) {
    const y = u.reduce((h, g) => h + g.length + 2, 2);
    l = e.options.lineWidth > 0 && y > e.options.lineWidth;
  }
  if (l) {
    let y = d;
    for (const h of u)
      y += h ? `
${r}${i}${h}` : `
`;
    return `${y}
${i}${m}`;
  } else
    return `${d}${o}${u.join(" ")}${o}${m}`;
}
function lt({ indent: n, options: { commentString: e } }, t, s, i) {
  if (s && i && (s = s.replace(/^\n+/, "")), s) {
    const r = ne(e(s), n);
    t.push(r.trimStart());
  }
}
function ye(n, e) {
  const t = K(e) ? e.value : e;
  for (const s of n)
    if (V(s) && (s.key === e || s.key === t || K(s.key) && s.key.value === t))
      return s;
}
class W extends Rn {
  static get tagName() {
    return "tag:yaml.org,2002:map";
  }
  constructor(e) {
    super(le, e), this.items = [];
  }
  /**
   * A generic collection parsing method that can be extended
   * to other node classes that inherit from YAMLMap
   */
  static from(e, t, s) {
    const { keepUndefined: i, replacer: r } = s, o = new this(e), a = (c, l) => {
      if (typeof r == "function")
        l = r.call(t, c, l);
      else if (Array.isArray(r) && !r.includes(c))
        return;
      (l !== void 0 || i) && o.items.push(Yt(c, l, s));
    };
    if (t instanceof Map)
      for (const [c, l] of t)
        a(c, l);
    else if (t && typeof t == "object")
      for (const c of Object.keys(t))
        a(c, t[c]);
    return typeof e.sortMapEntries == "function" && o.items.sort(e.sortMapEntries), o;
  }
  /**
   * Adds a value to the collection.
   *
   * @param overwrite - If not set `true`, using a key that is already in the
   *   collection will throw. Otherwise, overwrites the previous value.
   */
  add(e, t) {
    let s;
    V(e) ? s = e : !e || typeof e != "object" || !("key" in e) ? s = new z(e, e?.value) : s = new z(e.key, e.value);
    const i = ye(this.items, s.key), r = this.schema?.sortMapEntries;
    if (i) {
      if (!t)
        throw new Error(`Key ${s.key} already set`);
      K(i.value) && qn(s.value) ? i.value.value = s.value : i.value = s.value;
    } else if (r) {
      const o = this.items.findIndex((a) => r(s, a) < 0);
      o === -1 ? this.items.push(s) : this.items.splice(o, 0, s);
    } else
      this.items.push(s);
  }
  delete(e) {
    const t = ye(this.items, e);
    return t ? this.items.splice(this.items.indexOf(t), 1).length > 0 : !1;
  }
  get(e, t) {
    const i = ye(this.items, e)?.value;
    return (!t && K(i) ? i.value : i) ?? void 0;
  }
  has(e) {
    return !!ye(this.items, e);
  }
  set(e, t) {
    this.add(new z(e, t), !0);
  }
  /**
   * @param ctx - Conversion context, originally set in Document#toJS()
   * @param {Class} Type - If set, forces the returned collection type
   * @returns Instance of Type, Map, or Object
   */
  toJSON(e, t, s) {
    const i = s ? new s() : t?.mapAsMap ? /* @__PURE__ */ new Map() : {};
    t?.onCreate && t.onCreate(i);
    for (const r of this.items)
      zn(t, i, r);
    return i;
  }
  toString(e, t, s) {
    if (!e)
      return JSON.stringify(this);
    for (const i of this.items)
      if (!V(i))
        throw new Error(`Map items must all be pairs; found ${JSON.stringify(i)} instead`);
    return !e.allNullValues && this.hasAllNullValues(!1) && (e = Object.assign({}, e, { allNullValues: !0 })), Hn(this, e, {
      blockItemPrefix: "",
      flowChars: { start: "{", end: "}" },
      itemIndent: e.indent || "",
      onChompKeep: s,
      onComment: t
    });
  }
}
const je = {
  collection: "map",
  default: !0,
  nodeClass: W,
  tag: "tag:yaml.org,2002:map",
  resolve(n, e) {
    return ze(n) || e("Expected a mapping for this tag"), n;
  },
  createNode: (n, e, t) => W.from(n, e, t)
};
class we extends Rn {
  static get tagName() {
    return "tag:yaml.org,2002:seq";
  }
  constructor(e) {
    super(Me, e), this.items = [];
  }
  add(e) {
    this.items.push(e);
  }
  /**
   * Removes a value from the collection.
   *
   * `key` must contain a representation of an integer for this to succeed.
   * It may be wrapped in a `Scalar`.
   *
   * @returns `true` if the item was found and removed.
   */
  delete(e) {
    const t = Xe(e);
    return typeof t != "number" ? !1 : this.items.splice(t, 1).length > 0;
  }
  get(e, t) {
    const s = Xe(e);
    if (typeof s != "number")
      return;
    const i = this.items[s];
    return !t && K(i) ? i.value : i;
  }
  /**
   * Checks if the collection includes a value with the key `key`.
   *
   * `key` must contain a representation of an integer for this to succeed.
   * It may be wrapped in a `Scalar`.
   */
  has(e) {
    const t = Xe(e);
    return typeof t == "number" && t < this.items.length;
  }
  /**
   * Sets a value in this collection. For `!!set`, `value` needs to be a
   * boolean to add/remove the item from the set.
   *
   * If `key` does not contain a representation of an integer, this will throw.
   * It may be wrapped in a `Scalar`.
   */
  set(e, t) {
    const s = Xe(e);
    if (typeof s != "number")
      throw new Error(`Expected a valid index, not ${e}.`);
    const i = this.items[s];
    K(i) && qn(t) ? i.value = t : this.items[s] = t;
  }
  toJSON(e, t) {
    const s = [];
    t?.onCreate && t.onCreate(s);
    let i = 0;
    for (const r of this.items)
      s.push(J(r, String(i++), t));
    return s;
  }
  toString(e, t, s) {
    return e ? Hn(this, e, {
      blockItemPrefix: "- ",
      flowChars: { start: "[", end: "]" },
      itemIndent: (e.indent || "") + "  ",
      onChompKeep: s,
      onComment: t
    }) : JSON.stringify(this);
  }
  static from(e, t, s) {
    const { replacer: i } = s, r = new this(e);
    if (t && Symbol.iterator in Object(t)) {
      let o = 0;
      for (let a of t) {
        if (typeof i == "function") {
          const c = t instanceof Set ? a : String(o++);
          a = i.call(t, c, a);
        }
        r.items.push(Ve(a, void 0, s));
      }
    }
    return r;
  }
}
function Xe(n) {
  let e = K(n) ? n.value : n;
  return e && typeof e == "string" && (e = Number(e)), typeof e == "number" && Number.isInteger(e) && e >= 0 ? e : null;
}
const Be = {
  collection: "seq",
  default: !0,
  nodeClass: we,
  tag: "tag:yaml.org,2002:seq",
  resolve(n, e) {
    return He(n) || e("Expected a sequence for this tag"), n;
  },
  createNode: (n, e, t) => we.from(n, e, t)
}, mt = {
  identify: (n) => typeof n == "string",
  default: !0,
  tag: "tag:yaml.org,2002:str",
  resolve: (n) => n,
  stringify(n, e, t, s) {
    return e = Object.assign({ actualString: !0 }, e), Ht(n, e, t, s);
  }
}, gt = {
  identify: (n) => n == null,
  createNode: () => new O(null),
  default: !0,
  tag: "tag:yaml.org,2002:null",
  test: /^(?:~|[Nn]ull|NULL)?$/,
  resolve: () => new O(null),
  stringify: ({ source: n }, e) => typeof n == "string" && gt.test.test(n) ? n : e.options.nullStr
}, Wt = {
  identify: (n) => typeof n == "boolean",
  default: !0,
  tag: "tag:yaml.org,2002:bool",
  test: /^(?:[Tt]rue|TRUE|[Ff]alse|FALSE)$/,
  resolve: (n) => new O(n[0] === "t" || n[0] === "T"),
  stringify({ source: n, value: e }, t) {
    if (n && Wt.test.test(n)) {
      const s = n[0] === "t" || n[0] === "T";
      if (e === s)
        return n;
    }
    return e ? t.options.trueStr : t.options.falseStr;
  }
};
function ee({ format: n, minFractionDigits: e, tag: t, value: s }) {
  if (typeof s == "bigint")
    return String(s);
  const i = typeof s == "number" ? s : Number(s);
  if (!isFinite(i))
    return isNaN(i) ? ".nan" : i < 0 ? "-.inf" : ".inf";
  let r = Object.is(s, -0) ? "-0" : JSON.stringify(s);
  if (!n && e && (!t || t === "tag:yaml.org,2002:float") && /^-?\d/.test(r) && !r.includes("e")) {
    let o = r.indexOf(".");
    o < 0 && (o = r.length, r += ".");
    let a = e - (r.length - o - 1);
    for (; a-- > 0; )
      r += "0";
  }
  return r;
}
const Yn = {
  identify: (n) => typeof n == "number",
  default: !0,
  tag: "tag:yaml.org,2002:float",
  test: /^(?:[-+]?\.(?:inf|Inf|INF)|\.nan|\.NaN|\.NAN)$/,
  resolve: (n) => n.slice(-3).toLowerCase() === "nan" ? NaN : n[0] === "-" ? Number.NEGATIVE_INFINITY : Number.POSITIVE_INFINITY,
  stringify: ee
}, Wn = {
  identify: (n) => typeof n == "number",
  default: !0,
  tag: "tag:yaml.org,2002:float",
  format: "EXP",
  test: /^[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)[eE][-+]?[0-9]+$/,
  resolve: (n) => parseFloat(n),
  stringify(n) {
    const e = Number(n.value);
    return isFinite(e) ? e.toExponential() : ee(n);
  }
}, Jn = {
  identify: (n) => typeof n == "number",
  default: !0,
  tag: "tag:yaml.org,2002:float",
  test: /^[-+]?(?:\.[0-9]+|[0-9]+\.[0-9]*)$/,
  resolve(n) {
    const e = new O(parseFloat(n)), t = n.indexOf(".");
    return t !== -1 && n[n.length - 1] === "0" && (e.minFractionDigits = n.length - t - 1), e;
  },
  stringify: ee
}, yt = (n) => typeof n == "bigint" || Number.isInteger(n), Jt = (n, e, t, { intAsBigInt: s }) => s ? BigInt(n) : parseInt(n.substring(e), t);
function Xn(n, e, t) {
  const { value: s } = n;
  return yt(s) && s >= 0 ? t + s.toString(e) : ee(n);
}
const Zn = {
  identify: (n) => yt(n) && n >= 0,
  default: !0,
  tag: "tag:yaml.org,2002:int",
  format: "OCT",
  test: /^0o[0-7]+$/,
  resolve: (n, e, t) => Jt(n, 2, 8, t),
  stringify: (n) => Xn(n, 8, "0o")
}, es = {
  identify: yt,
  default: !0,
  tag: "tag:yaml.org,2002:int",
  test: /^[-+]?[0-9]+$/,
  resolve: (n, e, t) => Jt(n, 0, 10, t),
  stringify: ee
}, ts = {
  identify: (n) => yt(n) && n >= 0,
  default: !0,
  tag: "tag:yaml.org,2002:int",
  format: "HEX",
  test: /^0x[0-9a-fA-F]+$/,
  resolve: (n, e, t) => Jt(n, 2, 16, t),
  stringify: (n) => Xn(n, 16, "0x")
}, li = [
  je,
  Be,
  mt,
  gt,
  Wt,
  Zn,
  es,
  ts,
  Yn,
  Wn,
  Jn
];
function hn(n) {
  return typeof n == "bigint" || Number.isInteger(n);
}
const Ze = ({ value: n }) => JSON.stringify(n), ci = [
  {
    identify: (n) => typeof n == "string",
    default: !0,
    tag: "tag:yaml.org,2002:str",
    resolve: (n) => n,
    stringify: Ze
  },
  {
    identify: (n) => n == null,
    createNode: () => new O(null),
    default: !0,
    tag: "tag:yaml.org,2002:null",
    test: /^null$/,
    resolve: () => null,
    stringify: Ze
  },
  {
    identify: (n) => typeof n == "boolean",
    default: !0,
    tag: "tag:yaml.org,2002:bool",
    test: /^true$|^false$/,
    resolve: (n) => n === "true",
    stringify: Ze
  },
  {
    identify: hn,
    default: !0,
    tag: "tag:yaml.org,2002:int",
    test: /^-?(?:0|[1-9][0-9]*)$/,
    resolve: (n, e, { intAsBigInt: t }) => t ? BigInt(n) : parseInt(n, 10),
    stringify: ({ value: n }) => hn(n) ? n.toString() : JSON.stringify(n)
  },
  {
    identify: (n) => typeof n == "number",
    default: !0,
    tag: "tag:yaml.org,2002:float",
    test: /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]*)?(?:[eE][-+]?[0-9]+)?$/,
    resolve: (n) => parseFloat(n),
    stringify: Ze
  }
], fi = {
  default: !0,
  tag: "",
  test: /^/,
  resolve(n, e) {
    return e(`Unresolved plain scalar ${JSON.stringify(n)}`), n;
  }
}, ui = [je, Be].concat(ci, fi), Xt = {
  identify: (n) => n instanceof Uint8Array,
  // Buffer inherits from Uint8Array
  default: !1,
  tag: "tag:yaml.org,2002:binary",
  /**
   * Returns a Buffer in node and an Uint8Array in browsers
   *
   * To use the resulting buffer as an image, you'll want to do something like:
   *
   *   const blob = new Blob([buffer], { type: 'image/jpeg' })
   *   document.querySelector('#photo').src = URL.createObjectURL(blob)
   */
  resolve(n, e) {
    if (typeof atob == "function") {
      const t = atob(n.replace(/[\n\r]/g, "")), s = new Uint8Array(t.length);
      for (let i = 0; i < t.length; ++i)
        s[i] = t.charCodeAt(i);
      return s;
    } else
      return e("This environment does not support reading binary tags; either Buffer or atob is required"), n;
  },
  stringify({ comment: n, type: e, value: t }, s, i, r) {
    if (!t)
      return "";
    const o = t;
    let a;
    if (typeof btoa == "function") {
      let c = "";
      for (let l = 0; l < o.length; ++l)
        c += String.fromCharCode(o[l]);
      a = btoa(c);
    } else
      throw new Error("This environment does not support writing binary tags; either Buffer or btoa is required");
    if (e ?? (e = O.BLOCK_LITERAL), e !== O.QUOTE_DOUBLE) {
      const c = Math.max(s.options.lineWidth - s.indent.length, s.options.minContentWidth), l = Math.ceil(a.length / c), f = new Array(l);
      for (let u = 0, d = 0; u < l; ++u, d += c)
        f[u] = a.substr(d, c);
      a = f.join(e === O.BLOCK_LITERAL ? `
` : " ");
    }
    return Ht({ comment: n, type: e, value: a }, s, i, r);
  }
};
function ns(n, e) {
  if (He(n))
    for (let t = 0; t < n.items.length; ++t) {
      let s = n.items[t];
      if (!V(s)) {
        if (ze(s)) {
          s.items.length > 1 && e("Each pair must have its own sequence indicator");
          const i = s.items[0] || new z(new O(null));
          if (s.commentBefore && (i.key.commentBefore = i.key.commentBefore ? `${s.commentBefore}
${i.key.commentBefore}` : s.commentBefore), s.comment) {
            const r = i.value ?? i.key;
            r.comment = r.comment ? `${s.comment}
${r.comment}` : s.comment;
          }
          s = i;
        }
        n.items[t] = V(s) ? s : new z(s);
      }
    }
  else
    e("Expected a sequence for this tag");
  return n;
}
function ss(n, e, t) {
  const { replacer: s } = t, i = new we(n);
  i.tag = "tag:yaml.org,2002:pairs";
  let r = 0;
  if (e && Symbol.iterator in Object(e))
    for (let o of e) {
      typeof s == "function" && (o = s.call(e, String(r++), o));
      let a, c;
      if (Array.isArray(o))
        if (o.length === 2)
          a = o[0], c = o[1];
        else
          throw new TypeError(`Expected [key, value] tuple: ${o}`);
      else if (o && o instanceof Object) {
        const l = Object.keys(o);
        if (l.length === 1)
          a = l[0], c = o[a];
        else
          throw new TypeError(`Expected tuple with one key, not ${l.length} keys`);
      } else
        a = o;
      i.items.push(Yt(a, c, t));
    }
  return i;
}
const Zt = {
  collection: "seq",
  default: !1,
  tag: "tag:yaml.org,2002:pairs",
  resolve: ns,
  createNode: ss
};
class Ne extends we {
  constructor() {
    super(), this.add = W.prototype.add.bind(this), this.delete = W.prototype.delete.bind(this), this.get = W.prototype.get.bind(this), this.has = W.prototype.has.bind(this), this.set = W.prototype.set.bind(this), this.tag = Ne.tag;
  }
  /**
   * If `ctx` is given, the return type is actually `Map<unknown, unknown>`,
   * but TypeScript won't allow widening the signature of a child method.
   */
  toJSON(e, t) {
    if (!t)
      return super.toJSON(e);
    const s = /* @__PURE__ */ new Map();
    t?.onCreate && t.onCreate(s);
    for (const i of this.items) {
      let r, o;
      if (V(i) ? (r = J(i.key, "", t), o = J(i.value, r, t)) : r = J(i, "", t), s.has(r))
        throw new Error("Ordered maps must not include duplicate keys");
      s.set(r, o);
    }
    return s;
  }
  static from(e, t, s) {
    const i = ss(e, t, s), r = new this();
    return r.items = i.items, r;
  }
}
Ne.tag = "tag:yaml.org,2002:omap";
const en = {
  collection: "seq",
  identify: (n) => n instanceof Map,
  nodeClass: Ne,
  default: !1,
  tag: "tag:yaml.org,2002:omap",
  resolve(n, e) {
    const t = ns(n, e), s = [];
    for (const { key: i } of t.items)
      K(i) && (s.includes(i.value) ? e(`Ordered maps must not include duplicate keys: ${i.value}`) : s.push(i.value));
    return Object.assign(new Ne(), t);
  },
  createNode: (n, e, t) => Ne.from(n, e, t)
};
function is({ value: n, source: e }, t) {
  return e && (n ? rs : os).test.test(e) ? e : n ? t.options.trueStr : t.options.falseStr;
}
const rs = {
  identify: (n) => n === !0,
  default: !0,
  tag: "tag:yaml.org,2002:bool",
  test: /^(?:Y|y|[Yy]es|YES|[Tt]rue|TRUE|[Oo]n|ON)$/,
  resolve: () => new O(!0),
  stringify: is
}, os = {
  identify: (n) => n === !1,
  default: !0,
  tag: "tag:yaml.org,2002:bool",
  test: /^(?:N|n|[Nn]o|NO|[Ff]alse|FALSE|[Oo]ff|OFF)$/,
  resolve: () => new O(!1),
  stringify: is
}, hi = {
  identify: (n) => typeof n == "number",
  default: !0,
  tag: "tag:yaml.org,2002:float",
  test: /^(?:[-+]?\.(?:inf|Inf|INF)|\.nan|\.NaN|\.NAN)$/,
  resolve: (n) => n.slice(-3).toLowerCase() === "nan" ? NaN : n[0] === "-" ? Number.NEGATIVE_INFINITY : Number.POSITIVE_INFINITY,
  stringify: ee
}, di = {
  identify: (n) => typeof n == "number",
  default: !0,
  tag: "tag:yaml.org,2002:float",
  format: "EXP",
  test: /^[-+]?(?:[0-9][0-9_]*)?(?:\.[0-9_]*)?[eE][-+]?[0-9]+$/,
  resolve: (n) => parseFloat(n.replace(/_/g, "")),
  stringify(n) {
    const e = Number(n.value);
    return isFinite(e) ? e.toExponential() : ee(n);
  }
}, pi = {
  identify: (n) => typeof n == "number",
  default: !0,
  tag: "tag:yaml.org,2002:float",
  test: /^[-+]?(?:[0-9][0-9_]*)?\.[0-9_]*$/,
  resolve(n) {
    const e = new O(parseFloat(n.replace(/_/g, ""))), t = n.indexOf(".");
    if (t !== -1) {
      const s = n.substring(t + 1).replace(/_/g, "");
      s[s.length - 1] === "0" && (e.minFractionDigits = s.length);
    }
    return e;
  },
  stringify: ee
}, Ye = (n) => typeof n == "bigint" || Number.isInteger(n);
function wt(n, e, t, { intAsBigInt: s }) {
  const i = n[0];
  if ((i === "-" || i === "+") && (e += 1), n = n.substring(e).replace(/_/g, ""), s) {
    switch (t) {
      case 2:
        n = `0b${n}`;
        break;
      case 8:
        n = `0o${n}`;
        break;
      case 16:
        n = `0x${n}`;
        break;
    }
    const o = BigInt(n);
    return i === "-" ? BigInt(-1) * o : o;
  }
  const r = parseInt(n, t);
  return i === "-" ? -1 * r : r;
}
function tn(n, e, t) {
  const { value: s } = n;
  if (Ye(s)) {
    const i = s.toString(e);
    return s < 0 ? "-" + t + i.substr(1) : t + i;
  }
  return ee(n);
}
const mi = {
  identify: Ye,
  default: !0,
  tag: "tag:yaml.org,2002:int",
  format: "BIN",
  test: /^[-+]?0b[0-1_]+$/,
  resolve: (n, e, t) => wt(n, 2, 2, t),
  stringify: (n) => tn(n, 2, "0b")
}, gi = {
  identify: Ye,
  default: !0,
  tag: "tag:yaml.org,2002:int",
  format: "OCT",
  test: /^[-+]?0[0-7_]+$/,
  resolve: (n, e, t) => wt(n, 1, 8, t),
  stringify: (n) => tn(n, 8, "0")
}, yi = {
  identify: Ye,
  default: !0,
  tag: "tag:yaml.org,2002:int",
  test: /^[-+]?[0-9][0-9_]*$/,
  resolve: (n, e, t) => wt(n, 0, 10, t),
  stringify: ee
}, wi = {
  identify: Ye,
  default: !0,
  tag: "tag:yaml.org,2002:int",
  format: "HEX",
  test: /^[-+]?0x[0-9a-fA-F_]+$/,
  resolve: (n, e, t) => wt(n, 2, 16, t),
  stringify: (n) => tn(n, 16, "0x")
};
class Oe extends W {
  constructor(e) {
    super(e), this.tag = Oe.tag;
  }
  add(e) {
    let t;
    V(e) ? t = e : e && typeof e == "object" && "key" in e && "value" in e && e.value === null ? t = new z(e.key, null) : t = new z(e, null), ye(this.items, t.key) || this.items.push(t);
  }
  /**
   * If `keepPair` is `true`, returns the Pair matching `key`.
   * Otherwise, returns the value of that Pair's key.
   */
  get(e, t) {
    const s = ye(this.items, e);
    return !t && V(s) ? K(s.key) ? s.key.value : s.key : s;
  }
  set(e, t) {
    if (typeof t != "boolean")
      throw new Error(`Expected boolean value for set(key, value) in a YAML set, not ${typeof t}`);
    const s = ye(this.items, e);
    s && !t ? this.items.splice(this.items.indexOf(s), 1) : !s && t && this.items.push(new z(e));
  }
  toJSON(e, t) {
    return super.toJSON(e, t, Set);
  }
  toString(e, t, s) {
    if (!e)
      return JSON.stringify(this);
    if (this.hasAllNullValues(!0))
      return super.toString(Object.assign({}, e, { allNullValues: !0 }), t, s);
    throw new Error("Set items must all have null values");
  }
  static from(e, t, s) {
    const { replacer: i } = s, r = new this(e);
    if (t && Symbol.iterator in Object(t))
      for (let o of t)
        typeof i == "function" && (o = i.call(t, o, o)), r.items.push(Yt(o, null, s));
    return r;
  }
}
Oe.tag = "tag:yaml.org,2002:set";
const nn = {
  collection: "map",
  identify: (n) => n instanceof Set,
  nodeClass: Oe,
  default: !1,
  tag: "tag:yaml.org,2002:set",
  createNode: (n, e, t) => Oe.from(n, e, t),
  resolve(n, e) {
    if (ze(n)) {
      if (n.hasAllNullValues(!0))
        return Object.assign(new Oe(), n);
      e("Set items must all have null values");
    } else
      e("Expected a mapping for this tag");
    return n;
  }
};
function sn(n, e) {
  const t = n[0], s = t === "-" || t === "+" ? n.substring(1) : n, i = (o) => e ? BigInt(o) : Number(o), r = s.replace(/_/g, "").split(":").reduce((o, a) => o * i(60) + i(a), i(0));
  return t === "-" ? i(-1) * r : r;
}
function as(n) {
  let { value: e } = n, t = (o) => o;
  if (typeof e == "bigint")
    t = (o) => BigInt(o);
  else if (isNaN(e) || !isFinite(e))
    return ee(n);
  let s = "";
  e < 0 && (s = "-", e *= t(-1));
  const i = t(60), r = [e % i];
  return e < 60 ? r.unshift(0) : (e = (e - r[0]) / i, r.unshift(e % i), e >= 60 && (e = (e - r[0]) / i, r.unshift(e))), s + r.map((o) => String(o).padStart(2, "0")).join(":").replace(/000000\d*$/, "");
}
const ls = {
  identify: (n) => typeof n == "bigint" || Number.isInteger(n),
  default: !0,
  tag: "tag:yaml.org,2002:int",
  format: "TIME",
  test: /^[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+$/,
  resolve: (n, e, { intAsBigInt: t }) => sn(n, t),
  stringify: as
}, cs = {
  identify: (n) => typeof n == "number",
  default: !0,
  tag: "tag:yaml.org,2002:float",
  format: "TIME",
  test: /^[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*$/,
  resolve: (n) => sn(n, !1),
  stringify: as
}, bt = {
  identify: (n) => n instanceof Date,
  default: !0,
  tag: "tag:yaml.org,2002:timestamp",
  // If the time zone is omitted, the timestamp is assumed to be specified in UTC. The time part
  // may be omitted altogether, resulting in a date format. In such a case, the time part is
  // assumed to be 00:00:00Z (start of day, UTC).
  test: RegExp("^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})(?:(?:t|T|[ \\t]+)([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}(\\.[0-9]+)?)(?:[ \\t]*(Z|[-+][012]?[0-9](?::[0-9]{2})?))?)?$"),
  resolve(n) {
    const e = n.match(bt.test);
    if (!e)
      throw new Error("!!timestamp expects a date, starting with yyyy-mm-dd");
    const [, t, s, i, r, o, a] = e.map(Number), c = e[7] ? Number((e[7] + "00").substr(1, 3)) : 0;
    let l = Date.UTC(t, s - 1, i, r || 0, o || 0, a || 0, c);
    const f = e[8];
    if (f && f !== "Z") {
      let u = sn(f, !1);
      Math.abs(u) < 30 && (u *= 60), l -= 6e4 * u;
    }
    return new Date(l);
  },
  stringify: ({ value: n }) => n?.toISOString().replace(/(T00:00:00)?\.000Z$/, "") ?? ""
}, dn = [
  je,
  Be,
  mt,
  gt,
  rs,
  os,
  mi,
  gi,
  yi,
  wi,
  hi,
  di,
  pi,
  Xt,
  ie,
  en,
  Zt,
  nn,
  ls,
  cs,
  bt
], pn = /* @__PURE__ */ new Map([
  ["core", li],
  ["failsafe", [je, Be, mt]],
  ["json", ui],
  ["yaml11", dn],
  ["yaml-1.1", dn]
]), mn = {
  binary: Xt,
  bool: Wt,
  float: Jn,
  floatExp: Wn,
  floatNaN: Yn,
  floatTime: cs,
  int: es,
  intHex: ts,
  intOct: Zn,
  intTime: ls,
  map: je,
  merge: ie,
  null: gt,
  omap: en,
  pairs: Zt,
  seq: Be,
  set: nn,
  timestamp: bt
}, bi = {
  "tag:yaml.org,2002:binary": Xt,
  "tag:yaml.org,2002:merge": ie,
  "tag:yaml.org,2002:omap": en,
  "tag:yaml.org,2002:pairs": Zt,
  "tag:yaml.org,2002:set": nn,
  "tag:yaml.org,2002:timestamp": bt
};
function Nt(n, e, t) {
  const s = pn.get(e);
  if (s && !n)
    return t && !s.includes(ie) ? s.concat(ie) : s.slice();
  let i = s;
  if (!i)
    if (Array.isArray(n))
      i = [];
    else {
      const r = Array.from(pn.keys()).filter((o) => o !== "yaml11").map((o) => JSON.stringify(o)).join(", ");
      throw new Error(`Unknown schema "${e}"; use one of ${r} or define customTags array`);
    }
  if (Array.isArray(n))
    for (const r of n)
      i = i.concat(r);
  else typeof n == "function" && (i = n(i.slice()));
  return t && (i = i.concat(ie)), i.reduce((r, o) => {
    const a = typeof o == "string" ? mn[o] : o;
    if (!a) {
      const c = JSON.stringify(o), l = Object.keys(mn).map((f) => JSON.stringify(f)).join(", ");
      throw new Error(`Unknown custom tag ${c}; use one of ${l}`);
    }
    return r.includes(a) || r.push(a), r;
  }, []);
}
const ki = (n, e) => n.key < e.key ? -1 : n.key > e.key ? 1 : 0;
class rn {
  constructor({ compat: e, customTags: t, merge: s, resolveKnownTags: i, schema: r, sortMapEntries: o, toStringDefaults: a }) {
    this.compat = Array.isArray(e) ? Nt(e, "compat") : e ? Nt(null, e) : null, this.name = typeof r == "string" && r || "core", this.knownTags = i ? bi : {}, this.tags = Nt(t, this.name, s), this.toStringOptions = a ?? null, Object.defineProperty(this, le, { value: je }), Object.defineProperty(this, te, { value: mt }), Object.defineProperty(this, Me, { value: Be }), this.sortMapEntries = typeof o == "function" ? o : o === !0 ? ki : null;
  }
  clone() {
    const e = Object.create(rn.prototype, Object.getOwnPropertyDescriptors(this));
    return e.tags = this.tags.slice(), e;
  }
}
function $i(n, e) {
  const t = [];
  let s = e.directives === !0;
  if (e.directives !== !1 && n.directives) {
    const c = n.directives.toString(n);
    c ? (t.push(c), s = !0) : n.directives.docStart && (s = !0);
  }
  s && t.push("---");
  const i = Un(n, e), { commentString: r } = i.options;
  if (n.commentBefore) {
    t.length !== 1 && t.unshift("");
    const c = r(n.commentBefore);
    t.unshift(ne(c, ""));
  }
  let o = !1, a = null;
  if (n.contents) {
    if (R(n.contents)) {
      if (n.contents.spaceBefore && s && t.push(""), n.contents.commentBefore) {
        const f = r(n.contents.commentBefore);
        t.push(ne(f, ""));
      }
      i.forceBlockIndent = !!n.comment, a = n.contents.comment;
    }
    const c = a ? void 0 : () => o = !0;
    let l = Ae(n.contents, i, () => a = null, c);
    a && (l += ge(l, "", r(a))), (l[0] === "|" || l[0] === ">") && t[t.length - 1] === "---" ? t[t.length - 1] = `--- ${l}` : t.push(l);
  } else
    t.push(Ae(n.contents, i));
  if (n.directives?.docEnd)
    if (n.comment) {
      const c = r(n.comment);
      c.includes(`
`) ? (t.push("..."), t.push(ne(c, ""))) : t.push(`... ${c}`);
    } else
      t.push("...");
  else {
    let c = n.comment;
    c && o && (c = c.replace(/^\n+/, "")), c && ((!o || a) && t[t.length - 1] !== "" && t.push(""), t.push(ne(r(c), "")));
  }
  return t.join(`
`) + `
`;
}
class kt {
  constructor(e, t, s) {
    this.commentBefore = null, this.comment = null, this.errors = [], this.warnings = [], Object.defineProperty(this, X, { value: Bt });
    let i = null;
    typeof t == "function" || Array.isArray(t) ? i = t : s === void 0 && t && (s = t, t = void 0);
    const r = Object.assign({
      intAsBigInt: !1,
      keepSourceTokens: !1,
      logLevel: "warn",
      prettyErrors: !0,
      strict: !0,
      stringKeys: !1,
      uniqueKeys: !0,
      version: "1.2"
    }, s);
    this.options = r;
    let { version: o } = r;
    s?._directives ? (this.directives = s._directives.atDocument(), this.directives.yaml.explicit && (o = this.directives.yaml.version)) : this.directives = new G({ version: o }), this.setSchema(o, s), this.contents = e === void 0 ? null : this.createNode(e, i, s);
  }
  /**
   * Create a deep copy of this Document and its contents.
   *
   * Custom Node values that inherit from `Object` still refer to their original instances.
   */
  clone() {
    const e = Object.create(kt.prototype, {
      [X]: { value: Bt }
    });
    return e.commentBefore = this.commentBefore, e.comment = this.comment, e.errors = this.errors.slice(), e.warnings = this.warnings.slice(), e.options = Object.assign({}, this.options), this.directives && (e.directives = this.directives.clone()), e.schema = this.schema.clone(), e.contents = R(this.contents) ? this.contents.clone(e.schema) : this.contents, this.range && (e.range = this.range.slice()), e;
  }
  /** Adds a value to the document. */
  add(e) {
    $e(this.contents) && this.contents.add(e);
  }
  /** Adds a value to the document. */
  addIn(e, t) {
    $e(this.contents) && this.contents.addIn(e, t);
  }
  /**
   * Create a new `Alias` node, ensuring that the target `node` has the required anchor.
   *
   * If `node` already has an anchor, `name` is ignored.
   * Otherwise, the `node.anchor` value will be set to `name`,
   * or if an anchor with that name is already present in the document,
   * `name` will be used as a prefix for a new unique anchor.
   * If `name` is undefined, the generated anchor will use 'a' as a prefix.
   */
  createAlias(e, t) {
    if (!e.anchor) {
      const s = Fn(this);
      e.anchor = // eslint-disable-next-line @typescript-eslint/prefer-nullish-coalescing
      !t || s.has(t) ? Kn(t || "a", s) : t;
    }
    return new zt(e.anchor);
  }
  createNode(e, t, s) {
    let i;
    if (typeof t == "function")
      e = t.call({ "": e }, "", e), i = t;
    else if (Array.isArray(t)) {
      const g = (S) => typeof S == "number" || S instanceof String || S instanceof Number, w = t.filter(g).map(String);
      w.length > 0 && (t = t.concat(w)), i = t;
    } else s === void 0 && t && (s = t, t = void 0);
    const { aliasDuplicateObjects: r, anchorPrefix: o, flow: a, keepUndefined: c, onTagObj: l, tag: f } = s ?? {}, { onAnchor: u, setAnchors: d, sourceObjects: m } = Hs(
      this,
      // eslint-disable-next-line @typescript-eslint/prefer-nullish-coalescing
      o || "a"
    ), y = {
      aliasDuplicateObjects: r ?? !0,
      keepUndefined: c ?? !1,
      onAnchor: u,
      onTagObj: l,
      replacer: i,
      schema: this.schema,
      sourceObjects: m
    }, h = Ve(e, f, y);
    return a && q(h) && (h.flow = !0), d(), h;
  }
  /**
   * Convert a key and a value into a `Pair` using the current schema,
   * recursively wrapping all values as `Scalar` or `Collection` nodes.
   */
  createPair(e, t, s = {}) {
    const i = this.createNode(e, null, s), r = this.createNode(t, null, s);
    return new z(i, r);
  }
  /**
   * Removes a value from the document.
   * @returns `true` if the item was found and removed.
   */
  delete(e) {
    return $e(this.contents) ? this.contents.delete(e) : !1;
  }
  /**
   * Removes a value from the document.
   * @returns `true` if the item was found and removed.
   */
  deleteIn(e) {
    return De(e) ? this.contents == null ? !1 : (this.contents = null, !0) : $e(this.contents) ? this.contents.deleteIn(e) : !1;
  }
  /**
   * Returns item at `key`, or `undefined` if not found. By default unwraps
   * scalar values from their surrounding node; to disable set `keepScalar` to
   * `true` (collections are always returned intact).
   */
  get(e, t) {
    return q(this.contents) ? this.contents.get(e, t) : void 0;
  }
  /**
   * Returns item at `path`, or `undefined` if not found. By default unwraps
   * scalar values from their surrounding node; to disable set `keepScalar` to
   * `true` (collections are always returned intact).
   */
  getIn(e, t) {
    return De(e) ? !t && K(this.contents) ? this.contents.value : this.contents : q(this.contents) ? this.contents.getIn(e, t) : void 0;
  }
  /**
   * Checks if the document includes a value with the key `key`.
   */
  has(e) {
    return q(this.contents) ? this.contents.has(e) : !1;
  }
  /**
   * Checks if the document includes a value at `path`.
   */
  hasIn(e) {
    return De(e) ? this.contents !== void 0 : q(this.contents) ? this.contents.hasIn(e) : !1;
  }
  /**
   * Sets a value in this document. For `!!set`, `value` needs to be a
   * boolean to add/remove the item from the set.
   */
  set(e, t) {
    this.contents == null ? this.contents = at(this.schema, [e], t) : $e(this.contents) && this.contents.set(e, t);
  }
  /**
   * Sets a value in this document. For `!!set`, `value` needs to be a
   * boolean to add/remove the item from the set.
   */
  setIn(e, t) {
    De(e) ? this.contents = t : this.contents == null ? this.contents = at(this.schema, Array.from(e), t) : $e(this.contents) && this.contents.setIn(e, t);
  }
  /**
   * Change the YAML version and schema used by the document.
   * A `null` version disables support for directives, explicit tags, anchors, and aliases.
   * It also requires the `schema` option to be given as a `Schema` instance value.
   *
   * Overrides all previously set schema options.
   */
  setSchema(e, t = {}) {
    typeof e == "number" && (e = String(e));
    let s;
    switch (e) {
      case "1.1":
        this.directives ? this.directives.yaml.version = "1.1" : this.directives = new G({ version: "1.1" }), s = { resolveKnownTags: !1, schema: "yaml-1.1" };
        break;
      case "1.2":
      case "next":
        this.directives ? this.directives.yaml.version = e : this.directives = new G({ version: e }), s = { resolveKnownTags: !0, schema: "core" };
        break;
      case null:
        this.directives && delete this.directives, s = null;
        break;
      default: {
        const i = JSON.stringify(e);
        throw new Error(`Expected '1.1', '1.2' or null as first argument, but found: ${i}`);
      }
    }
    if (t.schema instanceof Object)
      this.schema = t.schema;
    else if (s)
      this.schema = new rn(Object.assign(s, t));
    else
      throw new Error("With a null YAML version, the { schema: Schema } option is required");
  }
  // json & jsonArg are only used from toJSON()
  toJS({ json: e, jsonArg: t, mapAsMap: s, maxAliasCount: i, onAnchor: r, reviver: o } = {}) {
    const a = {
      anchors: /* @__PURE__ */ new Map(),
      doc: this,
      keep: !e,
      mapAsMap: s === !0,
      mapKeyWarned: !1,
      maxAliasCount: typeof i == "number" ? i : 100
    }, c = J(this.contents, t ?? "", a);
    if (typeof r == "function")
      for (const { count: l, res: f } of a.anchors.values())
        r(f, l);
    return typeof o == "function" ? Le(o, { "": c }, "", c) : c;
  }
  /**
   * A JSON representation of the document `contents`.
   *
   * @param jsonArg Used by `JSON.stringify` to indicate the array index or
   *   property name.
   */
  toJSON(e, t) {
    return this.toJS({ json: !0, jsonArg: e, mapAsMap: !1, onAnchor: t });
  }
  /** A YAML representation of the document. */
  toString(e = {}) {
    if (this.errors.length > 0)
      throw new Error("Document with errors cannot be stringified");
    if ("indent" in e && (!Number.isInteger(e.indent) || Number(e.indent) <= 0)) {
      const t = JSON.stringify(e.indent);
      throw new Error(`"indent" option must be a positive integer, not ${t}`);
    }
    return $i(this, e);
  }
}
function $e(n) {
  if (q(n))
    return !0;
  throw new Error("Expected a YAML collection as document contents");
}
class fs extends Error {
  constructor(e, t, s, i) {
    super(), this.name = e, this.code = s, this.message = i, this.pos = t;
  }
}
class Fe extends fs {
  constructor(e, t, s) {
    super("YAMLParseError", e, t, s);
  }
}
class Si extends fs {
  constructor(e, t, s) {
    super("YAMLWarning", e, t, s);
  }
}
const gn = (n, e) => (t) => {
  if (t.pos[0] === -1)
    return;
  t.linePos = t.pos.map((a) => e.linePos(a));
  const { line: s, col: i } = t.linePos[0];
  t.message += ` at line ${s}, column ${i}`;
  let r = i - 1, o = n.substring(e.lineStarts[s - 1], e.lineStarts[s]).replace(/[\n\r]+$/, "");
  if (r >= 60 && o.length > 80) {
    const a = Math.min(r - 39, o.length - 79);
    o = "…" + o.substring(a), r -= a - 1;
  }
  if (o.length > 80 && (o = o.substring(0, 79) + "…"), s > 1 && /^ *$/.test(o.substring(0, r))) {
    let a = n.substring(e.lineStarts[s - 2], e.lineStarts[s - 1]);
    a.length > 80 && (a = a.substring(0, 79) + `…
`), o = a + o;
  }
  if (/[^ ]/.test(o)) {
    let a = 1;
    const c = t.linePos[1];
    c?.line === s && c.col > i && (a = Math.max(1, Math.min(c.col - i, 80 - r)));
    const l = " ".repeat(r) + "^".repeat(a);
    t.message += `:

${o}
${l}
`;
  }
};
function Te(n, { flow: e, indicator: t, next: s, offset: i, onError: r, parentIndent: o, startOnNewline: a }) {
  let c = !1, l = a, f = a, u = "", d = "", m = !1, y = !1, h = null, g = null, w = null, S = null, k = null, p = null, b = null;
  for (const $ of n)
    switch (y && ($.type !== "space" && $.type !== "newline" && $.type !== "comma" && r($.offset, "MISSING_CHAR", "Tags and anchors must be separated from the next token by white space"), y = !1), h && (l && $.type !== "comment" && $.type !== "newline" && r(h, "TAB_AS_INDENT", "Tabs are not allowed as indentation"), h = null), $.type) {
      case "space":
        !e && (t !== "doc-start" || s?.type !== "flow-collection") && $.source.includes("	") && (h = $), f = !0;
        break;
      case "comment": {
        f || r($, "MISSING_CHAR", "Comments must be separated from other tokens by white space characters");
        const N = $.source.substring(1) || " ";
        u ? u += d + N : u = N, d = "", l = !1;
        break;
      }
      case "newline":
        l ? u ? u += $.source : (!p || t !== "seq-item-ind") && (c = !0) : d += $.source, l = !0, m = !0, (g || w) && (S = $), f = !0;
        break;
      case "anchor":
        g && r($, "MULTIPLE_ANCHORS", "A node can have at most one anchor"), $.source.endsWith(":") && r($.offset + $.source.length - 1, "BAD_ALIAS", "Anchor ending in : is ambiguous", !0), g = $, b ?? (b = $.offset), l = !1, f = !1, y = !0;
        break;
      case "tag": {
        w && r($, "MULTIPLE_TAGS", "A node can have at most one tag"), w = $, b ?? (b = $.offset), l = !1, f = !1, y = !0;
        break;
      }
      case t:
        (g || w) && r($, "BAD_PROP_ORDER", `Anchors and tags must be after the ${$.source} indicator`), p && r($, "UNEXPECTED_TOKEN", `Unexpected ${$.source} in ${e ?? "collection"}`), p = $, l = t === "seq-item-ind" || t === "explicit-key-ind", f = !1;
        break;
      case "comma":
        if (e) {
          k && r($, "UNEXPECTED_TOKEN", `Unexpected , in ${e}`), k = $, l = !1, f = !1;
          break;
        }
      // else fallthrough
      default:
        r($, "UNEXPECTED_TOKEN", `Unexpected ${$.type} token`), l = !1, f = !1;
    }
  const v = n[n.length - 1], x = v ? v.offset + v.source.length : i;
  return y && s && s.type !== "space" && s.type !== "newline" && s.type !== "comma" && (s.type !== "scalar" || s.source !== "") && r(s.offset, "MISSING_CHAR", "Tags and anchors must be separated from the next token by white space"), h && (l && h.indent <= o || s?.type === "block-map" || s?.type === "block-seq") && r(h, "TAB_AS_INDENT", "Tabs are not allowed as indentation"), {
    comma: k,
    found: p,
    spaceBefore: c,
    comment: u,
    hasNewline: m,
    anchor: g,
    tag: w,
    newlineAfterProp: S,
    end: x,
    start: b ?? x
  };
}
function Ue(n) {
  if (!n)
    return null;
  switch (n.type) {
    case "alias":
    case "scalar":
    case "double-quoted-scalar":
    case "single-quoted-scalar":
      if (n.source.includes(`
`))
        return !0;
      if (n.end) {
        for (const e of n.end)
          if (e.type === "newline")
            return !0;
      }
      return !1;
    case "flow-collection":
      for (const e of n.items) {
        for (const t of e.start)
          if (t.type === "newline")
            return !0;
        if (e.sep) {
          for (const t of e.sep)
            if (t.type === "newline")
              return !0;
        }
        if (Ue(e.key) || Ue(e.value))
          return !0;
      }
      return !1;
    default:
      return !0;
  }
}
function Ft(n, e, t) {
  if (e?.type === "flow-collection") {
    const s = e.end[0];
    s.indent === n && (s.source === "]" || s.source === "}") && Ue(e) && t(s, "BAD_INDENT", "Flow end indicator should be more indented than parent", !0);
  }
}
function us(n, e, t) {
  const { uniqueKeys: s } = n.options;
  if (s === !1)
    return !1;
  const i = typeof s == "function" ? s : (r, o) => r === o || K(r) && K(o) && r.value === o.value;
  return e.some((r) => i(r.key, t));
}
const yn = "All mapping items must start at the same column";
function vi({ composeNode: n, composeEmptyNode: e }, t, s, i, r) {
  const o = r?.nodeClass ?? W, a = new o(t.schema);
  t.atRoot && (t.atRoot = !1);
  let c = s.offset, l = null;
  for (const f of s.items) {
    const { start: u, key: d, sep: m, value: y } = f, h = Te(u, {
      indicator: "explicit-key-ind",
      next: d ?? m?.[0],
      offset: c,
      onError: i,
      parentIndent: s.indent,
      startOnNewline: !0
    }), g = !h.found;
    if (g) {
      if (d && (d.type === "block-seq" ? i(c, "BLOCK_AS_IMPLICIT_KEY", "A block sequence may not be used as an implicit map key") : "indent" in d && d.indent !== s.indent && i(c, "BAD_INDENT", yn)), !h.anchor && !h.tag && !m) {
        l = h.end, h.comment && (a.comment ? a.comment += `
` + h.comment : a.comment = h.comment);
        continue;
      }
      (h.newlineAfterProp || Ue(d)) && i(d ?? u[u.length - 1], "MULTILINE_IMPLICIT_KEY", "Implicit keys need to be on a single line");
    } else h.found?.indent !== s.indent && i(c, "BAD_INDENT", yn);
    t.atKey = !0;
    const w = h.end, S = d ? n(t, d, h, i) : e(t, w, u, null, h, i);
    t.schema.compat && Ft(s.indent, d, i), t.atKey = !1, us(t, a.items, S) && i(w, "DUPLICATE_KEY", "Map keys must be unique");
    const k = Te(m ?? [], {
      indicator: "map-value-ind",
      next: y,
      offset: S.range[2],
      onError: i,
      parentIndent: s.indent,
      startOnNewline: !d || d.type === "block-scalar"
    });
    if (c = k.end, k.found) {
      g && (y?.type === "block-map" && !k.hasNewline && i(c, "BLOCK_AS_IMPLICIT_KEY", "Nested mappings are not allowed in compact mappings"), t.options.strict && h.start < k.found.offset - 1024 && i(S.range, "KEY_OVER_1024_CHARS", "The : indicator must be at most 1024 chars after the start of an implicit block mapping key"));
      const p = y ? n(t, y, k, i) : e(t, c, m, null, k, i);
      t.schema.compat && Ft(s.indent, y, i), c = p.range[2];
      const b = new z(S, p);
      t.options.keepSourceTokens && (b.srcToken = f), a.items.push(b);
    } else {
      g && i(S.range, "MISSING_CHAR", "Implicit map keys need to be followed by map values"), k.comment && (S.comment ? S.comment += `
` + k.comment : S.comment = k.comment);
      const p = new z(S);
      t.options.keepSourceTokens && (p.srcToken = f), a.items.push(p);
    }
  }
  return l && l < c && i(l, "IMPOSSIBLE", "Map comment with trailing content"), a.range = [s.offset, c, l ?? c], a;
}
function Ei({ composeNode: n, composeEmptyNode: e }, t, s, i, r) {
  const o = r?.nodeClass ?? we, a = new o(t.schema);
  t.atRoot && (t.atRoot = !1), t.atKey && (t.atKey = !1);
  let c = s.offset, l = null;
  for (const { start: f, value: u } of s.items) {
    const d = Te(f, {
      indicator: "seq-item-ind",
      next: u,
      offset: c,
      onError: i,
      parentIndent: s.indent,
      startOnNewline: !0
    });
    if (!d.found)
      if (d.anchor || d.tag || u)
        u?.type === "block-seq" ? i(d.end, "BAD_INDENT", "All sequence items must start at the same column") : i(c, "MISSING_CHAR", "Sequence item without - indicator");
      else {
        l = d.end, d.comment && (a.comment = d.comment);
        continue;
      }
    const m = u ? n(t, u, d, i) : e(t, d.end, f, null, d, i);
    t.schema.compat && Ft(s.indent, u, i), c = m.range[2], a.items.push(m);
  }
  return a.range = [s.offset, c, l ?? c], a;
}
function We(n, e, t, s) {
  let i = "";
  if (n) {
    let r = !1, o = "";
    for (const a of n) {
      const { source: c, type: l } = a;
      switch (l) {
        case "space":
          r = !0;
          break;
        case "comment": {
          t && !r && s(a, "MISSING_CHAR", "Comments must be separated from other tokens by white space characters");
          const f = c.substring(1) || " ";
          i ? i += o + f : i = f, o = "";
          break;
        }
        case "newline":
          i && (o += c), r = !0;
          break;
        default:
          s(a, "UNEXPECTED_TOKEN", `Unexpected ${l} at node end`);
      }
      e += c.length;
    }
  }
  return { comment: i, offset: e };
}
const Ot = "Block collections are not allowed within flow collections", At = (n) => n && (n.type === "block-map" || n.type === "block-seq");
function Li({ composeNode: n, composeEmptyNode: e }, t, s, i, r) {
  const o = s.start.source === "{", a = o ? "flow map" : "flow sequence", c = r?.nodeClass ?? (o ? W : we), l = new c(t.schema);
  l.flow = !0;
  const f = t.atRoot;
  f && (t.atRoot = !1), t.atKey && (t.atKey = !1);
  let u = s.offset + s.start.source.length;
  for (let g = 0; g < s.items.length; ++g) {
    const w = s.items[g], { start: S, key: k, sep: p, value: b } = w, v = Te(S, {
      flow: a,
      indicator: "explicit-key-ind",
      next: k ?? p?.[0],
      offset: u,
      onError: i,
      parentIndent: s.indent,
      startOnNewline: !1
    });
    if (!v.found) {
      if (!v.anchor && !v.tag && !p && !b) {
        g === 0 && v.comma ? i(v.comma, "UNEXPECTED_TOKEN", `Unexpected , in ${a}`) : g < s.items.length - 1 && i(v.start, "UNEXPECTED_TOKEN", `Unexpected empty item in ${a}`), v.comment && (l.comment ? l.comment += `
` + v.comment : l.comment = v.comment), u = v.end;
        continue;
      }
      !o && t.options.strict && Ue(k) && i(
        k,
        // checked by containsNewline()
        "MULTILINE_IMPLICIT_KEY",
        "Implicit keys of flow sequence pairs need to be on a single line"
      );
    }
    if (g === 0)
      v.comma && i(v.comma, "UNEXPECTED_TOKEN", `Unexpected , in ${a}`);
    else if (v.comma || i(v.start, "MISSING_CHAR", `Missing , between ${a} items`), v.comment) {
      let x = "";
      e: for (const $ of S)
        switch ($.type) {
          case "comma":
          case "space":
            break;
          case "comment":
            x = $.source.substring(1);
            break e;
          default:
            break e;
        }
      if (x) {
        let $ = l.items[l.items.length - 1];
        V($) && ($ = $.value ?? $.key), $.comment ? $.comment += `
` + x : $.comment = x, v.comment = v.comment.substring(x.length + 1);
      }
    }
    if (!o && !p && !v.found) {
      const x = b ? n(t, b, v, i) : e(t, v.end, p, null, v, i);
      l.items.push(x), u = x.range[2], At(b) && i(x.range, "BLOCK_IN_FLOW", Ot);
    } else {
      t.atKey = !0;
      const x = v.end, $ = k ? n(t, k, v, i) : e(t, x, S, null, v, i);
      At(k) && i($.range, "BLOCK_IN_FLOW", Ot), t.atKey = !1;
      const N = Te(p ?? [], {
        flow: a,
        indicator: "map-value-ind",
        next: b,
        offset: $.range[2],
        onError: i,
        parentIndent: s.indent,
        startOnNewline: !1
      });
      if (N.found) {
        if (!o && !v.found && t.options.strict) {
          if (p)
            for (const A of p) {
              if (A === N.found)
                break;
              if (A.type === "newline") {
                i(A, "MULTILINE_IMPLICIT_KEY", "Implicit keys of flow sequence pairs need to be on a single line");
                break;
              }
            }
          v.start < N.found.offset - 1024 && i(N.found, "KEY_OVER_1024_CHARS", "The : indicator must be at most 1024 chars after the start of an implicit flow sequence key");
        }
      } else b && ("source" in b && b.source?.[0] === ":" ? i(b, "MISSING_CHAR", `Missing space after : in ${a}`) : i(N.start, "MISSING_CHAR", `Missing , or : between ${a} items`));
      const C = b ? n(t, b, N, i) : N.found ? e(t, N.end, p, null, N, i) : null;
      C ? At(b) && i(C.range, "BLOCK_IN_FLOW", Ot) : N.comment && ($.comment ? $.comment += `
` + N.comment : $.comment = N.comment);
      const P = new z($, C);
      if (t.options.keepSourceTokens && (P.srcToken = w), o) {
        const A = l;
        us(t, A.items, $) && i(x, "DUPLICATE_KEY", "Map keys must be unique"), A.items.push(P);
      } else {
        const A = new W(t.schema);
        A.flow = !0, A.items.push(P);
        const D = (C ?? $).range;
        A.range = [$.range[0], D[1], D[2]], l.items.push(A);
      }
      u = C ? C.range[2] : N.end;
    }
  }
  const d = o ? "}" : "]", [m, ...y] = s.end;
  let h = u;
  if (m?.source === d)
    h = m.offset + m.source.length;
  else {
    const g = a[0].toUpperCase() + a.substring(1), w = f ? `${g} must end with a ${d}` : `${g} in block collection must be sufficiently indented and end with a ${d}`;
    i(u, f ? "MISSING_CHAR" : "BAD_INDENT", w), m && m.source.length !== 1 && y.unshift(m);
  }
  if (y.length > 0) {
    const g = We(y, h, t.options.strict, i);
    g.comment && (l.comment ? l.comment += `
` + g.comment : l.comment = g.comment), l.range = [s.offset, h, g.offset];
  } else
    l.range = [s.offset, h, h];
  return l;
}
function Tt(n, e, t, s, i, r) {
  const o = t.type === "block-map" ? vi(n, e, t, s, r) : t.type === "block-seq" ? Ei(n, e, t, s, r) : Li(n, e, t, s, r), a = o.constructor;
  return i === "!" || i === a.tagName ? (o.tag = a.tagName, o) : (i && (o.tag = i), o);
}
function xi(n, e, t, s, i) {
  const r = s.tag, o = r ? e.directives.tagName(r.source, (d) => i(r, "TAG_RESOLVE_FAILED", d)) : null;
  if (t.type === "block-seq") {
    const { anchor: d, newlineAfterProp: m } = s, y = d && r ? d.offset > r.offset ? d : r : d ?? r;
    y && (!m || m.offset < y.offset) && i(y, "MISSING_CHAR", "Missing newline after block sequence props");
  }
  const a = t.type === "block-map" ? "map" : t.type === "block-seq" ? "seq" : t.start.source === "{" ? "map" : "seq";
  if (!r || !o || o === "!" || o === W.tagName && a === "map" || o === we.tagName && a === "seq")
    return Tt(n, e, t, i, o);
  let c = e.schema.tags.find((d) => d.tag === o && d.collection === a);
  if (!c) {
    const d = e.schema.knownTags[o];
    if (d?.collection === a)
      e.schema.tags.push(Object.assign({}, d, { default: !1 })), c = d;
    else
      return d ? i(r, "BAD_COLLECTION_TYPE", `${d.tag} used for ${a} collection, but expects ${d.collection ?? "scalar"}`, !0) : i(r, "TAG_RESOLVE_FAILED", `Unresolved tag: ${o}`, !0), Tt(n, e, t, i, o);
  }
  const l = Tt(n, e, t, i, o, c), f = c.resolve?.(l, (d) => i(r, "TAG_RESOLVE_FAILED", d), e.options) ?? l, u = R(f) ? f : new O(f);
  return u.range = l.range, u.tag = o, c?.format && (u.format = c.format), u;
}
function Ni(n, e, t) {
  const s = e.offset, i = Oi(e, n.options.strict, t);
  if (!i)
    return { value: "", type: null, comment: "", range: [s, s, s] };
  const r = i.mode === ">" ? O.BLOCK_FOLDED : O.BLOCK_LITERAL, o = e.source ? Ai(e.source) : [];
  let a = o.length;
  for (let h = o.length - 1; h >= 0; --h) {
    const g = o[h][1];
    if (g === "" || g === "\r")
      a = h;
    else
      break;
  }
  if (a === 0) {
    const h = i.chomp === "+" && o.length > 0 ? `
`.repeat(Math.max(1, o.length - 1)) : "";
    let g = s + i.length;
    return e.source && (g += e.source.length), { value: h, type: r, comment: i.comment, range: [s, g, g] };
  }
  let c = e.indent + i.indent, l = e.offset + i.length, f = 0;
  for (let h = 0; h < a; ++h) {
    const [g, w] = o[h];
    if (w === "" || w === "\r")
      i.indent === 0 && g.length > c && (c = g.length);
    else {
      g.length < c && t(l + g.length, "MISSING_CHAR", "Block scalars with more-indented leading empty lines must use an explicit indentation indicator"), i.indent === 0 && (c = g.length), f = h, c === 0 && !n.atRoot && t(l, "BAD_INDENT", "Block scalar values in collections must be indented");
      break;
    }
    l += g.length + w.length + 1;
  }
  for (let h = o.length - 1; h >= a; --h)
    o[h][0].length > c && (a = h + 1);
  let u = "", d = "", m = !1;
  for (let h = 0; h < f; ++h)
    u += o[h][0].slice(c) + `
`;
  for (let h = f; h < a; ++h) {
    let [g, w] = o[h];
    l += g.length + w.length + 1;
    const S = w[w.length - 1] === "\r";
    if (S && (w = w.slice(0, -1)), w && g.length < c) {
      const p = `Block scalar lines must not be less indented than their ${i.indent ? "explicit indentation indicator" : "first line"}`;
      t(l - w.length - (S ? 2 : 1), "BAD_INDENT", p), g = "";
    }
    r === O.BLOCK_LITERAL ? (u += d + g.slice(c) + w, d = `
`) : g.length > c || w[0] === "	" ? (d === " " ? d = `
` : !m && d === `
` && (d = `

`), u += d + g.slice(c) + w, d = `
`, m = !0) : w === "" ? d === `
` ? u += `
` : d = `
` : (u += d + w, d = " ", m = !1);
  }
  switch (i.chomp) {
    case "-":
      break;
    case "+":
      for (let h = a; h < o.length; ++h)
        u += `
` + o[h][0].slice(c);
      u[u.length - 1] !== `
` && (u += `
`);
      break;
    default:
      u += `
`;
  }
  const y = s + i.length + e.source.length;
  return { value: u, type: r, comment: i.comment, range: [s, y, y] };
}
function Oi({ offset: n, props: e }, t, s) {
  if (e[0].type !== "block-scalar-header")
    return s(e[0], "IMPOSSIBLE", "Block scalar header not found"), null;
  const { source: i } = e[0], r = i[0];
  let o = 0, a = "", c = -1;
  for (let d = 1; d < i.length; ++d) {
    const m = i[d];
    if (!a && (m === "-" || m === "+"))
      a = m;
    else {
      const y = Number(m);
      !o && y ? o = y : c === -1 && (c = n + d);
    }
  }
  c !== -1 && s(c, "UNEXPECTED_TOKEN", `Block scalar header includes extra characters: ${i}`);
  let l = !1, f = "", u = i.length;
  for (let d = 1; d < e.length; ++d) {
    const m = e[d];
    switch (m.type) {
      case "space":
        l = !0;
      // fallthrough
      case "newline":
        u += m.source.length;
        break;
      case "comment":
        t && !l && s(m, "MISSING_CHAR", "Comments must be separated from other tokens by white space characters"), u += m.source.length, f = m.source.substring(1);
        break;
      case "error":
        s(m, "UNEXPECTED_TOKEN", m.message), u += m.source.length;
        break;
      /* istanbul ignore next should not happen */
      default: {
        const y = `Unexpected token in block scalar header: ${m.type}`;
        s(m, "UNEXPECTED_TOKEN", y);
        const h = m.source;
        h && typeof h == "string" && (u += h.length);
      }
    }
  }
  return { mode: r, indent: o, chomp: a, comment: f, length: u };
}
function Ai(n) {
  const e = n.split(/\n( *)/), t = e[0], s = t.match(/^( *)/), r = [s?.[1] ? [s[1], t.slice(s[1].length)] : ["", t]];
  for (let o = 1; o < e.length; o += 2)
    r.push([e[o], e[o + 1]]);
  return r;
}
function Ti(n, e, t) {
  const { offset: s, type: i, source: r, end: o } = n;
  let a, c;
  const l = (d, m, y) => t(s + d, m, y);
  switch (i) {
    case "scalar":
      a = O.PLAIN, c = Mi(r, l);
      break;
    case "single-quoted-scalar":
      a = O.QUOTE_SINGLE, c = Ci(r, l);
      break;
    case "double-quoted-scalar":
      a = O.QUOTE_DOUBLE, c = Ii(r, l);
      break;
    /* istanbul ignore next should not happen */
    default:
      return t(n, "UNEXPECTED_TOKEN", `Expected a flow scalar value, but found: ${i}`), {
        value: "",
        type: null,
        comment: "",
        range: [s, s + r.length, s + r.length]
      };
  }
  const f = s + r.length, u = We(o, f, e, t);
  return {
    value: c,
    type: a,
    comment: u.comment,
    range: [s, f, u.offset]
  };
}
function Mi(n, e) {
  let t = "";
  switch (n[0]) {
    /* istanbul ignore next should not happen */
    case "	":
      t = "a tab character";
      break;
    case ",":
      t = "flow indicator character ,";
      break;
    case "%":
      t = "directive indicator character %";
      break;
    case "|":
    case ">": {
      t = `block scalar indicator ${n[0]}`;
      break;
    }
    case "@":
    case "`": {
      t = `reserved character ${n[0]}`;
      break;
    }
  }
  return t && e(0, "BAD_SCALAR_START", `Plain value cannot start with ${t}`), hs(n);
}
function Ci(n, e) {
  return (n[n.length - 1] !== "'" || n.length === 1) && e(n.length, "MISSING_CHAR", "Missing closing 'quote"), hs(n.slice(1, -1)).replace(/''/g, "'");
}
function hs(n) {
  const e = /(.*?)\r?\n/sy;
  let t = e.exec(n);
  if (!t)
    return n;
  let s, i;
  try {
    s = new RegExp("(?<![ 	])[ 	]+$"), i = new RegExp("^[ 	]+|(?<![ 	])[ 	]+$", "g");
  } catch {
    s = /[ \t]+$/, i = /^[ \t]+|[ \t]+$/g;
  }
  let r = t[1].replace(s, ""), o = " ", a = e.lastIndex;
  for (; t = e.exec(n); ) {
    const l = t[1].replace(i, "");
    l === "" ? o === `
` ? r += o : o = `
` : (r += o + l, o = " "), a = e.lastIndex;
  }
  const c = /[ \t]*(.*)/sy;
  return c.lastIndex = a, t = c.exec(n), r + o + (t?.[1] ?? "");
}
function Ii(n, e) {
  let t = "";
  for (let s = 1; s < n.length - 1; ++s) {
    const i = n[s];
    if (!(i === "\r" && n[s + 1] === `
`))
      if (i === `
`) {
        const { fold: r, offset: o } = ji(n, s);
        t += r, s = o;
      } else if (i === "\\") {
        let r = n[++s];
        const o = Bi[r];
        if (o)
          t += o;
        else if (r === `
`)
          for (r = n[s + 1]; r === " " || r === "	"; )
            r = n[++s + 1];
        else if (r === "\r" && n[s + 1] === `
`)
          for (r = n[++s + 1]; r === " " || r === "	"; )
            r = n[++s + 1];
        else if (r === "x" || r === "u" || r === "U") {
          const a = r === "x" ? 2 : r === "u" ? 4 : 8;
          t += _i(n, s + 1, a, e), s += a;
        } else {
          const a = n.substr(s - 1, 2);
          e(s - 1, "BAD_DQ_ESCAPE", `Invalid escape sequence ${a}`), t += a;
        }
      } else if (i === " " || i === "	") {
        const r = s;
        let o = n[s + 1];
        for (; o === " " || o === "	"; )
          o = n[++s + 1];
        o !== `
` && !(o === "\r" && n[s + 2] === `
`) && (t += s > r ? n.slice(r, s + 1) : i);
      } else
        t += i;
  }
  return (n[n.length - 1] !== '"' || n.length === 1) && e(n.length, "MISSING_CHAR", 'Missing closing "quote'), t;
}
function ji(n, e) {
  let t = "", s = n[e + 1];
  for (; (s === " " || s === "	" || s === `
` || s === "\r") && !(s === "\r" && n[e + 2] !== `
`); )
    s === `
` && (t += `
`), e += 1, s = n[e + 1];
  return t || (t = " "), { fold: t, offset: e };
}
const Bi = {
  0: "\0",
  // null character
  a: "\x07",
  // bell character
  b: "\b",
  // backspace
  e: "\x1B",
  // escape character
  f: "\f",
  // form feed
  n: `
`,
  // line feed
  r: "\r",
  // carriage return
  t: "	",
  // horizontal tab
  v: "\v",
  // vertical tab
  N: "",
  // Unicode next line
  _: " ",
  // Unicode non-breaking space
  L: "\u2028",
  // Unicode line separator
  P: "\u2029",
  // Unicode paragraph separator
  " ": " ",
  '"': '"',
  "/": "/",
  "\\": "\\",
  "	": "	"
};
function _i(n, e, t, s) {
  const i = n.substr(e, t), o = i.length === t && /^[0-9a-fA-F]+$/.test(i) ? parseInt(i, 16) : NaN;
  try {
    return String.fromCodePoint(o);
  } catch {
    const a = n.substr(e - 2, t + 2);
    return s(e - 2, "BAD_DQ_ESCAPE", `Invalid escape sequence ${a}`), a;
  }
}
function ds(n, e, t, s) {
  const { value: i, type: r, comment: o, range: a } = e.type === "block-scalar" ? Ni(n, e, s) : Ti(e, n.options.strict, s), c = t ? n.directives.tagName(t.source, (u) => s(t, "TAG_RESOLVE_FAILED", u)) : null;
  let l;
  n.options.stringKeys && n.atKey ? l = n.schema[te] : c ? l = Pi(n.schema, i, c, t, s) : e.type === "scalar" ? l = Di(n, i, e, s) : l = n.schema[te];
  let f;
  try {
    const u = l.resolve(i, (d) => s(t ?? e, "TAG_RESOLVE_FAILED", d), n.options);
    f = K(u) ? u : new O(u);
  } catch (u) {
    const d = u instanceof Error ? u.message : String(u);
    s(t ?? e, "TAG_RESOLVE_FAILED", d), f = new O(i);
  }
  return f.range = a, f.source = i, r && (f.type = r), c && (f.tag = c), l.format && (f.format = l.format), o && (f.comment = o), f;
}
function Pi(n, e, t, s, i) {
  if (t === "!")
    return n[te];
  const r = [];
  for (const a of n.tags)
    if (!a.collection && a.tag === t)
      if (a.default && a.test)
        r.push(a);
      else
        return a;
  for (const a of r)
    if (a.test?.test(e))
      return a;
  const o = n.knownTags[t];
  return o && !o.collection ? (n.tags.push(Object.assign({}, o, { default: !1, test: void 0 })), o) : (i(s, "TAG_RESOLVE_FAILED", `Unresolved tag: ${t}`, t !== "tag:yaml.org,2002:str"), n[te]);
}
function Di({ atKey: n, directives: e, schema: t }, s, i, r) {
  const o = t.tags.find((a) => (a.default === !0 || n && a.default === "key") && a.test?.test(s)) || t[te];
  if (t.compat) {
    const a = t.compat.find((c) => c.default && c.test?.test(s)) ?? t[te];
    if (o.tag !== a.tag) {
      const c = e.tagString(o.tag), l = e.tagString(a.tag), f = `Value may be parsed as either ${c} or ${l}`;
      r(i, "TAG_RESOLVE_FAILED", f, !0);
    }
  }
  return o;
}
function Fi(n, e, t) {
  if (e) {
    t ?? (t = e.length);
    for (let s = t - 1; s >= 0; --s) {
      let i = e[s];
      switch (i.type) {
        case "space":
        case "comment":
        case "newline":
          n -= i.source.length;
          continue;
      }
      for (i = e[++s]; i?.type === "space"; )
        n += i.source.length, i = e[++s];
      break;
    }
  }
  return n;
}
const Ki = { composeNode: ps, composeEmptyNode: on };
function ps(n, e, t, s) {
  const i = n.atKey, { spaceBefore: r, comment: o, anchor: a, tag: c } = t;
  let l, f = !0;
  switch (e.type) {
    case "alias":
      l = qi(n, e, s), (a || c) && s(e, "ALIAS_PROPS", "An alias node must not specify any properties");
      break;
    case "scalar":
    case "single-quoted-scalar":
    case "double-quoted-scalar":
    case "block-scalar":
      l = ds(n, e, c, s), a && (l.anchor = a.source.substring(1));
      break;
    case "block-map":
    case "block-seq":
    case "flow-collection":
      try {
        l = xi(Ki, n, e, t, s), a && (l.anchor = a.source.substring(1));
      } catch (u) {
        const d = u instanceof Error ? u.message : String(u);
        s(e, "RESOURCE_EXHAUSTION", d);
      }
      break;
    default: {
      const u = e.type === "error" ? e.message : `Unsupported token (type: ${e.type})`;
      s(e, "UNEXPECTED_TOKEN", u), f = !1;
    }
  }
  return l ?? (l = on(n, e.offset, void 0, null, t, s)), a && l.anchor === "" && s(a, "BAD_ALIAS", "Anchor cannot be an empty string"), i && n.options.stringKeys && (!K(l) || typeof l.value != "string" || l.tag && l.tag !== "tag:yaml.org,2002:str") && s(c ?? e, "NON_STRING_KEY", "With stringKeys, all keys must be strings"), r && (l.spaceBefore = !0), o && (e.type === "scalar" && e.source === "" ? l.comment = o : l.commentBefore = o), n.options.keepSourceTokens && f && (l.srcToken = e), l;
}
function on(n, e, t, s, { spaceBefore: i, comment: r, anchor: o, tag: a, end: c }, l) {
  const f = {
    type: "scalar",
    offset: Fi(e, t, s),
    indent: -1,
    source: ""
  }, u = ds(n, f, a, l);
  return o && (u.anchor = o.source.substring(1), u.anchor === "" && l(o, "BAD_ALIAS", "Anchor cannot be an empty string")), i && (u.spaceBefore = !0), r && (u.comment = r, u.range[2] = c), u;
}
function qi({ options: n }, { offset: e, source: t, end: s }, i) {
  const r = new zt(t.substring(1));
  r.source === "" && i(e, "BAD_ALIAS", "Alias cannot be an empty string"), r.source.endsWith(":") && i(e + t.length - 1, "BAD_ALIAS", "Alias ending in : is ambiguous", !0);
  const o = e + t.length, a = We(s, o, n.strict, i);
  return r.range = [e, o, a.offset], a.comment && (r.comment = a.comment), r;
}
function Ri(n, e, { offset: t, start: s, value: i, end: r }, o) {
  const a = Object.assign({ _directives: e }, n), c = new kt(void 0, a), l = {
    atKey: !1,
    atRoot: !0,
    directives: c.directives,
    options: c.options,
    schema: c.schema
  }, f = Te(s, {
    indicator: "doc-start",
    next: i ?? r?.[0],
    offset: t,
    onError: o,
    parentIndent: 0,
    startOnNewline: !0
  });
  f.found && (c.directives.docStart = !0, i && (i.type === "block-map" || i.type === "block-seq") && !f.hasNewline && o(f.end, "MISSING_CHAR", "Block collection cannot start on same line with directives-end marker")), c.contents = i ? ps(l, i, f, o) : on(l, f.end, s, null, f, o);
  const u = c.contents.range[2], d = We(r, u, !1, o);
  return d.comment && (c.comment = d.comment), c.range = [t, u, d.offset], c;
}
function _e(n) {
  if (typeof n == "number")
    return [n, n + 1];
  if (Array.isArray(n))
    return n.length === 2 ? n : [n[0], n[1]];
  const { offset: e, source: t } = n;
  return [e, e + (typeof t == "string" ? t.length : 1)];
}
function wn(n) {
  let e = "", t = !1, s = !1;
  for (let i = 0; i < n.length; ++i) {
    const r = n[i];
    switch (r[0]) {
      case "#":
        e += (e === "" ? "" : s ? `

` : `
`) + (r.substring(1) || " "), t = !0, s = !1;
        break;
      case "%":
        n[i + 1]?.[0] !== "#" && (i += 1), t = !1;
        break;
      default:
        t || (s = !0), t = !1;
    }
  }
  return { comment: e, afterEmptyLine: s };
}
class Vi {
  constructor(e = {}) {
    this.doc = null, this.atDirectives = !1, this.prelude = [], this.errors = [], this.warnings = [], this.onError = (t, s, i, r) => {
      const o = _e(t);
      r ? this.warnings.push(new Si(o, s, i)) : this.errors.push(new Fe(o, s, i));
    }, this.directives = new G({ version: e.version || "1.2" }), this.options = e;
  }
  decorate(e, t) {
    const { comment: s, afterEmptyLine: i } = wn(this.prelude);
    if (s) {
      const r = e.contents;
      if (t)
        e.comment = e.comment ? `${e.comment}
${s}` : s;
      else if (i || e.directives.docStart || !r)
        e.commentBefore = s;
      else if (q(r) && !r.flow && r.items.length > 0) {
        let o = r.items[0];
        V(o) && (o = o.key);
        const a = o.commentBefore;
        o.commentBefore = a ? `${s}
${a}` : s;
      } else {
        const o = r.commentBefore;
        r.commentBefore = o ? `${s}
${o}` : s;
      }
    }
    if (t) {
      for (let r = 0; r < this.errors.length; ++r)
        e.errors.push(this.errors[r]);
      for (let r = 0; r < this.warnings.length; ++r)
        e.warnings.push(this.warnings[r]);
    } else
      e.errors = this.errors, e.warnings = this.warnings;
    this.prelude = [], this.errors = [], this.warnings = [];
  }
  /**
   * Current stream status information.
   *
   * Mostly useful at the end of input for an empty stream.
   */
  streamInfo() {
    return {
      comment: wn(this.prelude).comment,
      directives: this.directives,
      errors: this.errors,
      warnings: this.warnings
    };
  }
  /**
   * Compose tokens into documents.
   *
   * @param forceDoc - If the stream contains no document, still emit a final document including any comments and directives that would be applied to a subsequent document.
   * @param endOffset - Should be set if `forceDoc` is also set, to set the document range end and to indicate errors correctly.
   */
  *compose(e, t = !1, s = -1) {
    for (const i of e)
      yield* this.next(i);
    yield* this.end(t, s);
  }
  /** Advance the composer by one CST token. */
  *next(e) {
    switch (e.type) {
      case "directive":
        this.directives.add(e.source, (t, s, i) => {
          const r = _e(e);
          r[0] += t, this.onError(r, "BAD_DIRECTIVE", s, i);
        }), this.prelude.push(e.source), this.atDirectives = !0;
        break;
      case "document": {
        const t = Ri(this.options, this.directives, e, this.onError);
        this.atDirectives && !t.directives.docStart && this.onError(e, "MISSING_CHAR", "Missing directives-end/doc-start indicator line"), this.decorate(t, !1), this.doc && (yield this.doc), this.doc = t, this.atDirectives = !1;
        break;
      }
      case "byte-order-mark":
      case "space":
        break;
      case "comment":
      case "newline":
        this.prelude.push(e.source);
        break;
      case "error": {
        const t = e.source ? `${e.message}: ${JSON.stringify(e.source)}` : e.message, s = new Fe(_e(e), "UNEXPECTED_TOKEN", t);
        this.atDirectives || !this.doc ? this.errors.push(s) : this.doc.errors.push(s);
        break;
      }
      case "doc-end": {
        if (!this.doc) {
          const s = "Unexpected doc-end without preceding document";
          this.errors.push(new Fe(_e(e), "UNEXPECTED_TOKEN", s));
          break;
        }
        this.doc.directives.docEnd = !0;
        const t = We(e.end, e.offset + e.source.length, this.doc.options.strict, this.onError);
        if (this.decorate(this.doc, !0), t.comment) {
          const s = this.doc.comment;
          this.doc.comment = s ? `${s}
${t.comment}` : t.comment;
        }
        this.doc.range[2] = t.offset;
        break;
      }
      default:
        this.errors.push(new Fe(_e(e), "UNEXPECTED_TOKEN", `Unsupported token ${e.type}`));
    }
  }
  /**
   * Call at end of input to yield any remaining document.
   *
   * @param forceDoc - If the stream contains no document, still emit a final document including any comments and directives that would be applied to a subsequent document.
   * @param endOffset - Should be set if `forceDoc` is also set, to set the document range end and to indicate errors correctly.
   */
  *end(e = !1, t = -1) {
    if (this.doc)
      this.decorate(this.doc, !0), yield this.doc, this.doc = null;
    else if (e) {
      const s = Object.assign({ _directives: this.directives }, this.options), i = new kt(void 0, s);
      this.atDirectives && this.onError(t, "MISSING_CHAR", "Missing directives-end indicator line"), i.range = [0, t, t], this.decorate(i, !1), yield i;
    }
  }
}
const ms = "\uFEFF", gs = "", ys = "", Kt = "";
function Ui(n) {
  switch (n) {
    case ms:
      return "byte-order-mark";
    case gs:
      return "doc-mode";
    case ys:
      return "flow-error-end";
    case Kt:
      return "scalar";
    case "---":
      return "doc-start";
    case "...":
      return "doc-end";
    case "":
    case `
`:
    case `\r
`:
      return "newline";
    case "-":
      return "seq-item-ind";
    case "?":
      return "explicit-key-ind";
    case ":":
      return "map-value-ind";
    case "{":
      return "flow-map-start";
    case "}":
      return "flow-map-end";
    case "[":
      return "flow-seq-start";
    case "]":
      return "flow-seq-end";
    case ",":
      return "comma";
  }
  switch (n[0]) {
    case " ":
    case "	":
      return "space";
    case "#":
      return "comment";
    case "%":
      return "directive-line";
    case "*":
      return "alias";
    case "&":
      return "anchor";
    case "!":
      return "tag";
    case "'":
      return "single-quoted-scalar";
    case '"':
      return "double-quoted-scalar";
    case "|":
    case ">":
      return "block-scalar-header";
  }
  return null;
}
function Z(n) {
  switch (n) {
    case void 0:
    case " ":
    case `
`:
    case "\r":
    case "	":
      return !0;
    default:
      return !1;
  }
}
const bn = new Set("0123456789ABCDEFabcdef"), Qi = new Set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-#;/?:@&=+$_.!~*'()"), et = new Set(",[]{}"), Gi = new Set(` ,[]{}
\r	`), Mt = (n) => !n || Gi.has(n);
class zi {
  constructor() {
    this.atEnd = !1, this.blockScalarIndent = -1, this.blockScalarKeep = !1, this.buffer = "", this.flowKey = !1, this.flowLevel = 0, this.indentNext = 0, this.indentValue = 0, this.lineEndPos = null, this.next = null, this.pos = 0;
  }
  /**
   * Generate YAML tokens from the `source` string. If `incomplete`,
   * a part of the last line may be left as a buffer for the next call.
   *
   * @returns A generator of lexical tokens
   */
  *lex(e, t = !1) {
    if (e) {
      if (typeof e != "string")
        throw TypeError("source is not a string");
      this.buffer = this.buffer ? this.buffer + e : e, this.lineEndPos = null;
    }
    this.atEnd = !t;
    let s = this.next ?? "stream";
    for (; s && (t || this.hasChars(1)); )
      s = yield* this.parseNext(s);
  }
  atLineEnd() {
    let e = this.pos, t = this.buffer[e];
    for (; t === " " || t === "	"; )
      t = this.buffer[++e];
    return !t || t === "#" || t === `
` ? !0 : t === "\r" ? this.buffer[e + 1] === `
` : !1;
  }
  charAt(e) {
    return this.buffer[this.pos + e];
  }
  continueScalar(e) {
    let t = this.buffer[e];
    if (this.indentNext > 0) {
      let s = 0;
      for (; t === " "; )
        t = this.buffer[++s + e];
      if (t === "\r") {
        const i = this.buffer[s + e + 1];
        if (i === `
` || !i && !this.atEnd)
          return e + s + 1;
      }
      return t === `
` || s >= this.indentNext || !t && !this.atEnd ? e + s : -1;
    }
    if (t === "-" || t === ".") {
      const s = this.buffer.substr(e, 3);
      if ((s === "---" || s === "...") && Z(this.buffer[e + 3]))
        return -1;
    }
    return e;
  }
  getLine() {
    let e = this.lineEndPos;
    return (typeof e != "number" || e !== -1 && e < this.pos) && (e = this.buffer.indexOf(`
`, this.pos), this.lineEndPos = e), e === -1 ? this.atEnd ? this.buffer.substring(this.pos) : null : (this.buffer[e - 1] === "\r" && (e -= 1), this.buffer.substring(this.pos, e));
  }
  hasChars(e) {
    return this.pos + e <= this.buffer.length;
  }
  setNext(e) {
    return this.buffer = this.buffer.substring(this.pos), this.pos = 0, this.lineEndPos = null, this.next = e, null;
  }
  peek(e) {
    return this.buffer.substr(this.pos, e);
  }
  *parseNext(e) {
    switch (e) {
      case "stream":
        return yield* this.parseStream();
      case "line-start":
        return yield* this.parseLineStart();
      case "block-start":
        return yield* this.parseBlockStart();
      case "doc":
        return yield* this.parseDocument();
      case "flow":
        return yield* this.parseFlowCollection();
      case "quoted-scalar":
        return yield* this.parseQuotedScalar();
      case "block-scalar":
        return yield* this.parseBlockScalar();
      case "plain-scalar":
        return yield* this.parsePlainScalar();
    }
  }
  *parseStream() {
    let e = this.getLine();
    if (e === null)
      return this.setNext("stream");
    if (e[0] === ms && (yield* this.pushCount(1), e = e.substring(1)), e[0] === "%") {
      let t = e.length, s = e.indexOf("#");
      for (; s !== -1; ) {
        const r = e[s - 1];
        if (r === " " || r === "	") {
          t = s - 1;
          break;
        } else
          s = e.indexOf("#", s + 1);
      }
      for (; ; ) {
        const r = e[t - 1];
        if (r === " " || r === "	")
          t -= 1;
        else
          break;
      }
      const i = (yield* this.pushCount(t)) + (yield* this.pushSpaces(!0));
      return yield* this.pushCount(e.length - i), this.pushNewline(), "stream";
    }
    if (this.atLineEnd()) {
      const t = yield* this.pushSpaces(!0);
      return yield* this.pushCount(e.length - t), yield* this.pushNewline(), "stream";
    }
    return yield gs, yield* this.parseLineStart();
  }
  *parseLineStart() {
    const e = this.charAt(0);
    if (!e && !this.atEnd)
      return this.setNext("line-start");
    if (e === "-" || e === ".") {
      if (!this.atEnd && !this.hasChars(4))
        return this.setNext("line-start");
      const t = this.peek(3);
      if ((t === "---" || t === "...") && Z(this.charAt(3)))
        return yield* this.pushCount(3), this.indentValue = 0, this.indentNext = 0, t === "---" ? "doc" : "stream";
    }
    return this.indentValue = yield* this.pushSpaces(!1), this.indentNext > this.indentValue && !Z(this.charAt(1)) && (this.indentNext = this.indentValue), yield* this.parseBlockStart();
  }
  *parseBlockStart() {
    const [e, t] = this.peek(2);
    if (!t && !this.atEnd)
      return this.setNext("block-start");
    if ((e === "-" || e === "?" || e === ":") && Z(t)) {
      const s = (yield* this.pushCount(1)) + (yield* this.pushSpaces(!0));
      return this.indentNext = this.indentValue + 1, this.indentValue += s, "block-start";
    }
    return "doc";
  }
  *parseDocument() {
    yield* this.pushSpaces(!0);
    const e = this.getLine();
    if (e === null)
      return this.setNext("doc");
    let t = yield* this.pushIndicators();
    switch (e[t]) {
      case "#":
        yield* this.pushCount(e.length - t);
      // fallthrough
      case void 0:
        return yield* this.pushNewline(), yield* this.parseLineStart();
      case "{":
      case "[":
        return yield* this.pushCount(1), this.flowKey = !1, this.flowLevel = 1, "flow";
      case "}":
      case "]":
        return yield* this.pushCount(1), "doc";
      case "*":
        return yield* this.pushUntil(Mt), "doc";
      case '"':
      case "'":
        return yield* this.parseQuotedScalar();
      case "|":
      case ">":
        return t += yield* this.parseBlockScalarHeader(), t += yield* this.pushSpaces(!0), yield* this.pushCount(e.length - t), yield* this.pushNewline(), yield* this.parseBlockScalar();
      default:
        return yield* this.parsePlainScalar();
    }
  }
  *parseFlowCollection() {
    let e, t, s = -1;
    do
      e = yield* this.pushNewline(), e > 0 ? (t = yield* this.pushSpaces(!1), this.indentValue = s = t) : t = 0, t += yield* this.pushSpaces(!0);
    while (e + t > 0);
    const i = this.getLine();
    if (i === null)
      return this.setNext("flow");
    if ((s !== -1 && s < this.indentNext && i[0] !== "#" || s === 0 && (i.startsWith("---") || i.startsWith("...")) && Z(i[3])) && !(s === this.indentNext - 1 && this.flowLevel === 1 && (i[0] === "]" || i[0] === "}")))
      return this.flowLevel = 0, yield ys, yield* this.parseLineStart();
    let r = 0;
    for (; i[r] === ","; )
      r += yield* this.pushCount(1), r += yield* this.pushSpaces(!0), this.flowKey = !1;
    switch (r += yield* this.pushIndicators(), i[r]) {
      case void 0:
        return "flow";
      case "#":
        return yield* this.pushCount(i.length - r), "flow";
      case "{":
      case "[":
        return yield* this.pushCount(1), this.flowKey = !1, this.flowLevel += 1, "flow";
      case "}":
      case "]":
        return yield* this.pushCount(1), this.flowKey = !0, this.flowLevel -= 1, this.flowLevel ? "flow" : "doc";
      case "*":
        return yield* this.pushUntil(Mt), "flow";
      case '"':
      case "'":
        return this.flowKey = !0, yield* this.parseQuotedScalar();
      case ":": {
        const o = this.charAt(1);
        if (this.flowKey || Z(o) || o === ",")
          return this.flowKey = !1, yield* this.pushCount(1), yield* this.pushSpaces(!0), "flow";
      }
      // fallthrough
      default:
        return this.flowKey = !1, yield* this.parsePlainScalar();
    }
  }
  *parseQuotedScalar() {
    const e = this.charAt(0);
    let t = this.buffer.indexOf(e, this.pos + 1);
    if (e === "'")
      for (; t !== -1 && this.buffer[t + 1] === "'"; )
        t = this.buffer.indexOf("'", t + 2);
    else
      for (; t !== -1; ) {
        let r = 0;
        for (; this.buffer[t - 1 - r] === "\\"; )
          r += 1;
        if (r % 2 === 0)
          break;
        t = this.buffer.indexOf('"', t + 1);
      }
    const s = this.buffer.substring(0, t);
    let i = s.indexOf(`
`, this.pos);
    if (i !== -1) {
      for (; i !== -1; ) {
        const r = this.continueScalar(i + 1);
        if (r === -1)
          break;
        i = s.indexOf(`
`, r);
      }
      i !== -1 && (t = i - (s[i - 1] === "\r" ? 2 : 1));
    }
    if (t === -1) {
      if (!this.atEnd)
        return this.setNext("quoted-scalar");
      t = this.buffer.length;
    }
    return yield* this.pushToIndex(t + 1, !1), this.flowLevel ? "flow" : "doc";
  }
  *parseBlockScalarHeader() {
    this.blockScalarIndent = -1, this.blockScalarKeep = !1;
    let e = this.pos;
    for (; ; ) {
      const t = this.buffer[++e];
      if (t === "+")
        this.blockScalarKeep = !0;
      else if (t > "0" && t <= "9")
        this.blockScalarIndent = Number(t) - 1;
      else if (t !== "-")
        break;
    }
    return yield* this.pushUntil((t) => Z(t) || t === "#");
  }
  *parseBlockScalar() {
    let e = this.pos - 1, t = 0, s;
    e: for (let r = this.pos; s = this.buffer[r]; ++r)
      switch (s) {
        case " ":
          t += 1;
          break;
        case `
`:
          e = r, t = 0;
          break;
        case "\r": {
          const o = this.buffer[r + 1];
          if (!o && !this.atEnd)
            return this.setNext("block-scalar");
          if (o === `
`)
            break;
        }
        // fallthrough
        default:
          break e;
      }
    if (!s && !this.atEnd)
      return this.setNext("block-scalar");
    if (t >= this.indentNext) {
      this.blockScalarIndent === -1 ? this.indentNext = t : this.indentNext = this.blockScalarIndent + (this.indentNext === 0 ? 1 : this.indentNext);
      do {
        const r = this.continueScalar(e + 1);
        if (r === -1)
          break;
        e = this.buffer.indexOf(`
`, r);
      } while (e !== -1);
      if (e === -1) {
        if (!this.atEnd)
          return this.setNext("block-scalar");
        e = this.buffer.length;
      }
    }
    let i = e + 1;
    for (s = this.buffer[i]; s === " "; )
      s = this.buffer[++i];
    if (s === "	") {
      for (; s === "	" || s === " " || s === "\r" || s === `
`; )
        s = this.buffer[++i];
      e = i - 1;
    } else if (!this.blockScalarKeep)
      do {
        let r = e - 1, o = this.buffer[r];
        o === "\r" && (o = this.buffer[--r]);
        const a = r;
        for (; o === " "; )
          o = this.buffer[--r];
        if (o === `
` && r >= this.pos && r + 1 + t > a)
          e = r;
        else
          break;
      } while (!0);
    return yield Kt, yield* this.pushToIndex(e + 1, !0), yield* this.parseLineStart();
  }
  *parsePlainScalar() {
    const e = this.flowLevel > 0;
    let t = this.pos - 1, s = this.pos - 1, i;
    for (; i = this.buffer[++s]; )
      if (i === ":") {
        const r = this.buffer[s + 1];
        if (Z(r) || e && et.has(r))
          break;
        t = s;
      } else if (Z(i)) {
        let r = this.buffer[s + 1];
        if (i === "\r" && (r === `
` ? (s += 1, i = `
`, r = this.buffer[s + 1]) : t = s), r === "#" || e && et.has(r))
          break;
        if (i === `
`) {
          const o = this.continueScalar(s + 1);
          if (o === -1)
            break;
          s = Math.max(s, o - 2);
        }
      } else {
        if (e && et.has(i))
          break;
        t = s;
      }
    return !i && !this.atEnd ? this.setNext("plain-scalar") : (yield Kt, yield* this.pushToIndex(t + 1, !0), e ? "flow" : "doc");
  }
  *pushCount(e) {
    return e > 0 ? (yield this.buffer.substr(this.pos, e), this.pos += e, e) : 0;
  }
  *pushToIndex(e, t) {
    const s = this.buffer.slice(this.pos, e);
    return s ? (yield s, this.pos += s.length, s.length) : (t && (yield ""), 0);
  }
  *pushIndicators() {
    let e = 0;
    e: for (; ; ) {
      switch (this.charAt(0)) {
        case "!":
          e += yield* this.pushTag(), e += yield* this.pushSpaces(!0);
          continue e;
        case "&":
          e += yield* this.pushUntil(Mt), e += yield* this.pushSpaces(!0);
          continue e;
        case "-":
        // this is an error
        case "?":
        // this is an error outside flow collections
        case ":": {
          const t = this.flowLevel > 0, s = this.charAt(1);
          if (Z(s) || t && et.has(s)) {
            t ? this.flowKey && (this.flowKey = !1) : this.indentNext = this.indentValue + 1, e += yield* this.pushCount(1), e += yield* this.pushSpaces(!0);
            continue e;
          }
        }
      }
      break e;
    }
    return e;
  }
  *pushTag() {
    if (this.charAt(1) === "<") {
      let e = this.pos + 2, t = this.buffer[e];
      for (; !Z(t) && t !== ">"; )
        t = this.buffer[++e];
      return yield* this.pushToIndex(t === ">" ? e + 1 : e, !1);
    } else {
      let e = this.pos + 1, t = this.buffer[e];
      for (; t; )
        if (Qi.has(t))
          t = this.buffer[++e];
        else if (t === "%" && bn.has(this.buffer[e + 1]) && bn.has(this.buffer[e + 2]))
          t = this.buffer[e += 3];
        else
          break;
      return yield* this.pushToIndex(e, !1);
    }
  }
  *pushNewline() {
    const e = this.buffer[this.pos];
    return e === `
` ? yield* this.pushCount(1) : e === "\r" && this.charAt(1) === `
` ? yield* this.pushCount(2) : 0;
  }
  *pushSpaces(e) {
    let t = this.pos - 1, s;
    do
      s = this.buffer[++t];
    while (s === " " || e && s === "	");
    const i = t - this.pos;
    return i > 0 && (yield this.buffer.substr(this.pos, i), this.pos = t), i;
  }
  *pushUntil(e) {
    let t = this.pos, s = this.buffer[t];
    for (; !e(s); )
      s = this.buffer[++t];
    return yield* this.pushToIndex(t, !1);
  }
}
class Hi {
  constructor() {
    this.lineStarts = [], this.addNewLine = (e) => this.lineStarts.push(e), this.linePos = (e) => {
      let t = 0, s = this.lineStarts.length;
      for (; t < s; ) {
        const r = t + s >> 1;
        this.lineStarts[r] < e ? t = r + 1 : s = r;
      }
      if (this.lineStarts[t] === e)
        return { line: t + 1, col: 1 };
      if (t === 0)
        return { line: 0, col: e };
      const i = this.lineStarts[t - 1];
      return { line: t, col: e - i + 1 };
    };
  }
}
function oe(n, e) {
  for (let t = 0; t < n.length; ++t)
    if (n[t].type === e)
      return !0;
  return !1;
}
function kn(n) {
  for (let e = 0; e < n.length; ++e)
    switch (n[e].type) {
      case "space":
      case "comment":
      case "newline":
        break;
      default:
        return e;
    }
  return -1;
}
function ws(n) {
  switch (n?.type) {
    case "alias":
    case "scalar":
    case "single-quoted-scalar":
    case "double-quoted-scalar":
    case "flow-collection":
      return !0;
    default:
      return !1;
  }
}
function tt(n) {
  switch (n.type) {
    case "document":
      return n.start;
    case "block-map": {
      const e = n.items[n.items.length - 1];
      return e.sep ?? e.start;
    }
    case "block-seq":
      return n.items[n.items.length - 1].start;
    /* istanbul ignore next should not happen */
    default:
      return [];
  }
}
function Se(n) {
  if (n.length === 0)
    return [];
  let e = n.length;
  e: for (; --e >= 0; )
    switch (n[e].type) {
      case "doc-start":
      case "explicit-key-ind":
      case "map-value-ind":
      case "seq-item-ind":
      case "newline":
        break e;
    }
  for (; n[++e]?.type === "space"; )
    ;
  return n.splice(e, n.length);
}
function ct(n, e) {
  if (e.length < 1e5)
    Array.prototype.push.apply(n, e);
  else
    for (let t = 0; t < e.length; ++t)
      n.push(e[t]);
}
function $n(n) {
  if (n.start.type === "flow-seq-start")
    for (const e of n.items)
      e.sep && !e.value && !oe(e.start, "explicit-key-ind") && !oe(e.sep, "map-value-ind") && (e.key && (e.value = e.key), delete e.key, ws(e.value) ? e.value.end ? ct(e.value.end, e.sep) : e.value.end = e.sep : ct(e.start, e.sep), delete e.sep);
}
class Yi {
  /**
   * @param onNewLine - If defined, called separately with the start position of
   *   each new line (in `parse()`, including the start of input).
   */
  constructor(e) {
    this.atNewLine = !0, this.atScalar = !1, this.indent = 0, this.offset = 0, this.onKeyLine = !1, this.stack = [], this.source = "", this.type = "", this.lexer = new zi(), this.onNewLine = e;
  }
  /**
   * Parse `source` as a YAML stream.
   * If `incomplete`, a part of the last line may be left as a buffer for the next call.
   *
   * Errors are not thrown, but yielded as `{ type: 'error', message }` tokens.
   *
   * @returns A generator of tokens representing each directive, document, and other structure.
   */
  *parse(e, t = !1) {
    this.onNewLine && this.offset === 0 && this.onNewLine(0);
    for (const s of this.lexer.lex(e, t))
      yield* this.next(s);
    t || (yield* this.end());
  }
  /**
   * Advance the parser by the `source` of one lexical token.
   */
  *next(e) {
    if (this.source = e, this.atScalar) {
      this.atScalar = !1, yield* this.step(), this.offset += e.length;
      return;
    }
    const t = Ui(e);
    if (t)
      if (t === "scalar")
        this.atNewLine = !1, this.atScalar = !0, this.type = "scalar";
      else {
        switch (this.type = t, yield* this.step(), t) {
          case "newline":
            this.atNewLine = !0, this.indent = 0, this.onNewLine && this.onNewLine(this.offset + e.length);
            break;
          case "space":
            this.atNewLine && e[0] === " " && (this.indent += e.length);
            break;
          case "explicit-key-ind":
          case "map-value-ind":
          case "seq-item-ind":
            this.atNewLine && (this.indent += e.length);
            break;
          case "doc-mode":
          case "flow-error-end":
            return;
          default:
            this.atNewLine = !1;
        }
        this.offset += e.length;
      }
    else {
      const s = `Not a YAML token: ${e}`;
      yield* this.pop({ type: "error", offset: this.offset, message: s, source: e }), this.offset += e.length;
    }
  }
  /** Call at end of input to push out any remaining constructions */
  *end() {
    for (; this.stack.length > 0; )
      yield* this.pop();
  }
  get sourceToken() {
    return {
      type: this.type,
      offset: this.offset,
      indent: this.indent,
      source: this.source
    };
  }
  *step() {
    const e = this.peek(1);
    if (this.type === "doc-end" && e?.type !== "doc-end") {
      for (; this.stack.length > 0; )
        yield* this.pop();
      this.stack.push({
        type: "doc-end",
        offset: this.offset,
        source: this.source
      });
      return;
    }
    if (!e)
      return yield* this.stream();
    switch (e.type) {
      case "document":
        return yield* this.document(e);
      case "alias":
      case "scalar":
      case "single-quoted-scalar":
      case "double-quoted-scalar":
        return yield* this.scalar(e);
      case "block-scalar":
        return yield* this.blockScalar(e);
      case "block-map":
        return yield* this.blockMap(e);
      case "block-seq":
        return yield* this.blockSequence(e);
      case "flow-collection":
        return yield* this.flowCollection(e);
      case "doc-end":
        return yield* this.documentEnd(e);
    }
    yield* this.pop();
  }
  peek(e) {
    return this.stack[this.stack.length - e];
  }
  *pop(e) {
    const t = e ?? this.stack.pop();
    if (!t)
      yield { type: "error", offset: this.offset, source: "", message: "Tried to pop an empty stack" };
    else if (this.stack.length === 0)
      yield t;
    else {
      const s = this.peek(1);
      switch (t.type === "block-scalar" ? t.indent = "indent" in s ? s.indent : 0 : t.type === "flow-collection" && s.type === "document" && (t.indent = 0), t.type === "flow-collection" && $n(t), s.type) {
        case "document":
          s.value = t;
          break;
        case "block-scalar":
          s.props.push(t);
          break;
        case "block-map": {
          const i = s.items[s.items.length - 1];
          if (i.value) {
            s.items.push({ start: [], key: t, sep: [] }), this.onKeyLine = !0;
            return;
          } else if (i.sep)
            i.value = t;
          else {
            Object.assign(i, { key: t, sep: [] }), this.onKeyLine = !i.explicitKey;
            return;
          }
          break;
        }
        case "block-seq": {
          const i = s.items[s.items.length - 1];
          i.value ? s.items.push({ start: [], value: t }) : i.value = t;
          break;
        }
        case "flow-collection": {
          const i = s.items[s.items.length - 1];
          !i || i.value ? s.items.push({ start: [], key: t, sep: [] }) : i.sep ? i.value = t : Object.assign(i, { key: t, sep: [] });
          return;
        }
        /* istanbul ignore next should not happen */
        default:
          yield* this.pop(), yield* this.pop(t);
      }
      if ((s.type === "document" || s.type === "block-map" || s.type === "block-seq") && (t.type === "block-map" || t.type === "block-seq")) {
        const i = t.items[t.items.length - 1];
        i && !i.sep && !i.value && i.start.length > 0 && kn(i.start) === -1 && (t.indent === 0 || i.start.every((r) => r.type !== "comment" || r.indent < t.indent)) && (s.type === "document" ? s.end = i.start : s.items.push({ start: i.start }), t.items.splice(-1, 1));
      }
    }
  }
  *stream() {
    switch (this.type) {
      case "directive-line":
        yield { type: "directive", offset: this.offset, source: this.source };
        return;
      case "byte-order-mark":
      case "space":
      case "comment":
      case "newline":
        yield this.sourceToken;
        return;
      case "doc-mode":
      case "doc-start": {
        const e = {
          type: "document",
          offset: this.offset,
          start: []
        };
        this.type === "doc-start" && e.start.push(this.sourceToken), this.stack.push(e);
        return;
      }
    }
    yield {
      type: "error",
      offset: this.offset,
      message: `Unexpected ${this.type} token in YAML stream`,
      source: this.source
    };
  }
  *document(e) {
    if (e.value)
      return yield* this.lineEnd(e);
    switch (this.type) {
      case "doc-start": {
        kn(e.start) !== -1 ? (yield* this.pop(), yield* this.step()) : e.start.push(this.sourceToken);
        return;
      }
      case "anchor":
      case "tag":
      case "space":
      case "comment":
      case "newline":
        e.start.push(this.sourceToken);
        return;
    }
    const t = this.startBlockValue(e);
    t ? this.stack.push(t) : yield {
      type: "error",
      offset: this.offset,
      message: `Unexpected ${this.type} token in YAML document`,
      source: this.source
    };
  }
  *scalar(e) {
    if (this.type === "map-value-ind") {
      const t = tt(this.peek(2)), s = Se(t);
      let i;
      e.end ? (i = e.end, i.push(this.sourceToken), delete e.end) : i = [this.sourceToken];
      const r = {
        type: "block-map",
        offset: e.offset,
        indent: e.indent,
        items: [{ start: s, key: e, sep: i }]
      };
      this.onKeyLine = !0, this.stack[this.stack.length - 1] = r;
    } else
      yield* this.lineEnd(e);
  }
  *blockScalar(e) {
    switch (this.type) {
      case "space":
      case "comment":
      case "newline":
        e.props.push(this.sourceToken);
        return;
      case "scalar":
        if (e.source = this.source, this.atNewLine = !0, this.indent = 0, this.onNewLine) {
          let t = this.source.indexOf(`
`) + 1;
          for (; t !== 0; )
            this.onNewLine(this.offset + t), t = this.source.indexOf(`
`, t) + 1;
        }
        yield* this.pop();
        break;
      /* istanbul ignore next should not happen */
      default:
        yield* this.pop(), yield* this.step();
    }
  }
  *blockMap(e) {
    const t = e.items[e.items.length - 1];
    switch (this.type) {
      case "newline":
        if (this.onKeyLine = !1, t.value) {
          const s = "end" in t.value ? t.value.end : void 0;
          (Array.isArray(s) ? s[s.length - 1] : void 0)?.type === "comment" ? s?.push(this.sourceToken) : e.items.push({ start: [this.sourceToken] });
        } else t.sep ? t.sep.push(this.sourceToken) : t.start.push(this.sourceToken);
        return;
      case "space":
      case "comment":
        if (t.value)
          e.items.push({ start: [this.sourceToken] });
        else if (t.sep)
          t.sep.push(this.sourceToken);
        else {
          if (this.atIndentedComment(t.start, e.indent)) {
            const i = e.items[e.items.length - 2]?.value?.end;
            if (Array.isArray(i)) {
              ct(i, t.start), i.push(this.sourceToken), e.items.pop();
              return;
            }
          }
          t.start.push(this.sourceToken);
        }
        return;
    }
    if (this.indent >= e.indent) {
      const s = !this.onKeyLine && this.indent === e.indent, i = s && (t.sep || t.explicitKey) && this.type !== "seq-item-ind";
      let r = [];
      if (i && t.sep && !t.value) {
        const o = [];
        for (let a = 0; a < t.sep.length; ++a) {
          const c = t.sep[a];
          switch (c.type) {
            case "newline":
              o.push(a);
              break;
            case "space":
              break;
            case "comment":
              c.indent > e.indent && (o.length = 0);
              break;
            default:
              o.length = 0;
          }
        }
        o.length >= 2 && (r = t.sep.splice(o[1]));
      }
      switch (this.type) {
        case "anchor":
        case "tag":
          i || t.value ? (r.push(this.sourceToken), e.items.push({ start: r }), this.onKeyLine = !0) : t.sep ? t.sep.push(this.sourceToken) : t.start.push(this.sourceToken);
          return;
        case "explicit-key-ind":
          !t.sep && !t.explicitKey ? (t.start.push(this.sourceToken), t.explicitKey = !0) : i || t.value ? (r.push(this.sourceToken), e.items.push({ start: r, explicitKey: !0 })) : this.stack.push({
            type: "block-map",
            offset: this.offset,
            indent: this.indent,
            items: [{ start: [this.sourceToken], explicitKey: !0 }]
          }), this.onKeyLine = !0;
          return;
        case "map-value-ind":
          if (t.explicitKey)
            if (t.sep)
              if (t.value)
                e.items.push({ start: [], key: null, sep: [this.sourceToken] });
              else if (oe(t.sep, "map-value-ind"))
                this.stack.push({
                  type: "block-map",
                  offset: this.offset,
                  indent: this.indent,
                  items: [{ start: r, key: null, sep: [this.sourceToken] }]
                });
              else if (ws(t.key) && !oe(t.sep, "newline")) {
                const o = Se(t.start), a = t.key, c = t.sep;
                c.push(this.sourceToken), delete t.key, delete t.sep, this.stack.push({
                  type: "block-map",
                  offset: this.offset,
                  indent: this.indent,
                  items: [{ start: o, key: a, sep: c }]
                });
              } else r.length > 0 ? t.sep = t.sep.concat(r, this.sourceToken) : t.sep.push(this.sourceToken);
            else if (oe(t.start, "newline"))
              Object.assign(t, { key: null, sep: [this.sourceToken] });
            else {
              const o = Se(t.start);
              this.stack.push({
                type: "block-map",
                offset: this.offset,
                indent: this.indent,
                items: [{ start: o, key: null, sep: [this.sourceToken] }]
              });
            }
          else
            t.sep ? t.value || i ? e.items.push({ start: r, key: null, sep: [this.sourceToken] }) : oe(t.sep, "map-value-ind") ? this.stack.push({
              type: "block-map",
              offset: this.offset,
              indent: this.indent,
              items: [{ start: [], key: null, sep: [this.sourceToken] }]
            }) : t.sep.push(this.sourceToken) : Object.assign(t, { key: null, sep: [this.sourceToken] });
          this.onKeyLine = !0;
          return;
        case "alias":
        case "scalar":
        case "single-quoted-scalar":
        case "double-quoted-scalar": {
          const o = this.flowScalar(this.type);
          i || t.value ? (e.items.push({ start: r, key: o, sep: [] }), this.onKeyLine = !0) : t.sep ? this.stack.push(o) : (Object.assign(t, { key: o, sep: [] }), this.onKeyLine = !0);
          return;
        }
        default: {
          const o = this.startBlockValue(e);
          if (o) {
            if (o.type === "block-seq") {
              if (!t.explicitKey && t.sep && !oe(t.sep, "newline")) {
                yield* this.pop({
                  type: "error",
                  offset: this.offset,
                  message: "Unexpected block-seq-ind on same line with key",
                  source: this.source
                });
                return;
              }
            } else s && e.items.push({ start: r });
            this.stack.push(o);
            return;
          }
        }
      }
    }
    yield* this.pop(), yield* this.step();
  }
  *blockSequence(e) {
    const t = e.items[e.items.length - 1];
    switch (this.type) {
      case "newline":
        if (t.value) {
          const s = "end" in t.value ? t.value.end : void 0;
          (Array.isArray(s) ? s[s.length - 1] : void 0)?.type === "comment" ? s?.push(this.sourceToken) : e.items.push({ start: [this.sourceToken] });
        } else
          t.start.push(this.sourceToken);
        return;
      case "space":
      case "comment":
        if (t.value)
          e.items.push({ start: [this.sourceToken] });
        else {
          if (this.atIndentedComment(t.start, e.indent)) {
            const i = e.items[e.items.length - 2]?.value?.end;
            if (Array.isArray(i)) {
              ct(i, t.start), i.push(this.sourceToken), e.items.pop();
              return;
            }
          }
          t.start.push(this.sourceToken);
        }
        return;
      case "anchor":
      case "tag":
        if (t.value || this.indent <= e.indent)
          break;
        t.start.push(this.sourceToken);
        return;
      case "seq-item-ind":
        if (this.indent !== e.indent)
          break;
        t.value || oe(t.start, "seq-item-ind") ? e.items.push({ start: [this.sourceToken] }) : t.start.push(this.sourceToken);
        return;
    }
    if (this.indent > e.indent) {
      const s = this.startBlockValue(e);
      if (s) {
        this.stack.push(s);
        return;
      }
    }
    yield* this.pop(), yield* this.step();
  }
  *flowCollection(e) {
    const t = e.items[e.items.length - 1];
    if (this.type === "flow-error-end") {
      let s;
      do
        yield* this.pop(), s = this.peek(1);
      while (s?.type === "flow-collection");
    } else if (e.end.length === 0) {
      switch (this.type) {
        case "comma":
        case "explicit-key-ind":
          !t || t.sep ? e.items.push({ start: [this.sourceToken] }) : t.start.push(this.sourceToken);
          return;
        case "map-value-ind":
          !t || t.value ? e.items.push({ start: [], key: null, sep: [this.sourceToken] }) : t.sep ? t.sep.push(this.sourceToken) : Object.assign(t, { key: null, sep: [this.sourceToken] });
          return;
        case "space":
        case "comment":
        case "newline":
        case "anchor":
        case "tag":
          !t || t.value ? e.items.push({ start: [this.sourceToken] }) : t.sep ? t.sep.push(this.sourceToken) : t.start.push(this.sourceToken);
          return;
        case "alias":
        case "scalar":
        case "single-quoted-scalar":
        case "double-quoted-scalar": {
          const i = this.flowScalar(this.type);
          !t || t.value ? e.items.push({ start: [], key: i, sep: [] }) : t.sep ? this.stack.push(i) : Object.assign(t, { key: i, sep: [] });
          return;
        }
        case "flow-map-end":
        case "flow-seq-end":
          e.end.push(this.sourceToken);
          return;
      }
      const s = this.startBlockValue(e);
      s ? this.stack.push(s) : (yield* this.pop(), yield* this.step());
    } else {
      const s = this.peek(2);
      if (s.type === "block-map" && (this.type === "map-value-ind" && s.indent === e.indent || this.type === "newline" && !s.items[s.items.length - 1].sep))
        yield* this.pop(), yield* this.step();
      else if (this.type === "map-value-ind" && s.type !== "flow-collection") {
        const i = tt(s), r = Se(i);
        $n(e);
        const o = e.end.splice(1, e.end.length);
        o.push(this.sourceToken);
        const a = {
          type: "block-map",
          offset: e.offset,
          indent: e.indent,
          items: [{ start: r, key: e, sep: o }]
        };
        this.onKeyLine = !0, this.stack[this.stack.length - 1] = a;
      } else
        yield* this.lineEnd(e);
    }
  }
  flowScalar(e) {
    if (this.onNewLine) {
      let t = this.source.indexOf(`
`) + 1;
      for (; t !== 0; )
        this.onNewLine(this.offset + t), t = this.source.indexOf(`
`, t) + 1;
    }
    return {
      type: e,
      offset: this.offset,
      indent: this.indent,
      source: this.source
    };
  }
  startBlockValue(e) {
    switch (this.type) {
      case "alias":
      case "scalar":
      case "single-quoted-scalar":
      case "double-quoted-scalar":
        return this.flowScalar(this.type);
      case "block-scalar-header":
        return {
          type: "block-scalar",
          offset: this.offset,
          indent: this.indent,
          props: [this.sourceToken],
          source: ""
        };
      case "flow-map-start":
      case "flow-seq-start":
        return {
          type: "flow-collection",
          offset: this.offset,
          indent: this.indent,
          start: this.sourceToken,
          items: [],
          end: []
        };
      case "seq-item-ind":
        return {
          type: "block-seq",
          offset: this.offset,
          indent: this.indent,
          items: [{ start: [this.sourceToken] }]
        };
      case "explicit-key-ind": {
        this.onKeyLine = !0;
        const t = tt(e), s = Se(t);
        return s.push(this.sourceToken), {
          type: "block-map",
          offset: this.offset,
          indent: this.indent,
          items: [{ start: s, explicitKey: !0 }]
        };
      }
      case "map-value-ind": {
        this.onKeyLine = !0;
        const t = tt(e), s = Se(t);
        return {
          type: "block-map",
          offset: this.offset,
          indent: this.indent,
          items: [{ start: s, key: null, sep: [this.sourceToken] }]
        };
      }
    }
    return null;
  }
  atIndentedComment(e, t) {
    return this.type !== "comment" || this.indent <= t ? !1 : e.every((s) => s.type === "newline" || s.type === "space");
  }
  *documentEnd(e) {
    this.type !== "doc-mode" && (e.end ? e.end.push(this.sourceToken) : e.end = [this.sourceToken], this.type === "newline" && (yield* this.pop()));
  }
  *lineEnd(e) {
    switch (this.type) {
      case "comma":
      case "doc-start":
      case "doc-end":
      case "flow-seq-end":
      case "flow-map-end":
      case "map-value-ind":
        yield* this.pop(), yield* this.step();
        break;
      case "newline":
        this.onKeyLine = !1;
      default:
        e.end ? e.end.push(this.sourceToken) : e.end = [this.sourceToken], this.type === "newline" && (yield* this.pop());
    }
  }
}
function Wi(n) {
  const e = n.prettyErrors !== !1;
  return { lineCounter: n.lineCounter || e && new Hi() || null, prettyErrors: e };
}
function Ji(n, e = {}) {
  const { lineCounter: t, prettyErrors: s } = Wi(e), i = new Yi(t?.addNewLine), r = new Vi(e);
  let o = null;
  for (const a of r.compose(i.parse(n), !0, n.length))
    if (!o)
      o = a;
    else if (o.options.logLevel !== "silent") {
      o.errors.push(new Fe(a.range.slice(0, 2), "MULTIPLE_DOCS", "Source contains multiple documents; please use YAML.parseAllDocuments()"));
      break;
    }
  return s && t && (o.errors.forEach(gn(n, t)), o.warnings.forEach(gn(n, t))), o;
}
const Y = {
  comic: {
    title: "제목",
    cast: "등장인물",
    panels: "컷",
    personas: "페르소나"
  },
  cast: {
    asset: "그림",
    label: "이름표",
    appearance: "외형",
    persona: "페르소나"
  },
  persona: { role: "직무", personality: "성격", speechStyle: "말투" },
  appearance: {
    skinColor: "피부색",
    hairStyle: "머리모양",
    hairColor: "머리색",
    outfit: "옷",
    outfitColor: "옷색",
    glasses: "안경"
  },
  panel: {
    mode: "구성",
    actors: "인물",
    dialogue: "대사",
    transfer: "전달",
    removeActors: "제외인물",
    diagram: "다이어그램"
  },
  actor: {
    id: "식별자",
    expression: "표정",
    gesture: "손모양",
    holding: "든소품",
    x: "가로위치",
    y: "세로위치",
    scale: "배율"
  },
  dialogue: {
    from: "화자",
    to: "상대",
    text: "내용",
    x: "가로위치",
    y: "세로위치",
    fontSize: "글자크기"
  },
  transfer: { from: "주는인물", to: "받는인물", prop: "소품" },
  diagram: {
    type: "종류",
    source: "원문",
    title: "제목",
    height: "높이"
  },
  options: {
    width: "너비",
    font: "글꼴",
    fontVersion: "글꼴버전",
    panelFormat: "컷비율"
  }
}, qt = {
  asset: {
    client: "클라이언트",
    server: "서버",
    database: "데이터베이스",
    human: "사람"
  },
  hairStyle: { short: "짧은머리", bob: "단발", long: "긴머리", bald: "민머리" },
  outfit: { shirt: "셔츠", jacket: "재킷", hoodie: "후드" },
  expression: {
    neutral: "보통",
    happy: "기쁨",
    confused: "어리둥절",
    sad: "슬픔",
    angry: "화남"
  },
  gesture: { wave: "인사손", point: "가리키는손" },
  prop: { request: "요청", data: "데이터", key: "열쇠" },
  mode: { full: "전체", before: "이전" },
  panelFormat: { compact: "기본", phone: "모바일" },
  diagramType: { mermaid: "머메이드" }
}, Xi = {
  cast: { asset: "asset" },
  appearance: { hairStyle: "hairStyle", outfit: "outfit" },
  actor: { expression: "expression", gesture: "gesture", holding: "prop" },
  panel: { mode: "mode" },
  transfer: { prop: "prop" },
  diagram: { type: "diagramType" },
  options: { panelFormat: "panelFormat" }
};
function rt(n) {
  return !!n && typeof n == "object" && !Array.isArray(n);
}
function ae(n, e, t, s) {
  if (!rt(n)) return n;
  const i = Y[e], r = /* @__PURE__ */ Object.create(null);
  for (const [o, a] of Object.entries(n)) {
    const c = Object.keys(i).find(
      (m) => o === m || o === i[m]
    ) ?? o;
    Object.hasOwn(i, c) && i[c];
    const l = c;
    if (Object.hasOwn(r, l))
      throw new Error(
        `${s}: '${i[c]}'와 '${c}'은 같은 항목입니다. 하나만 작성하세요.`
      );
    let f = a;
    const u = Xi[e], d = u && Object.hasOwn(u, c) ? u[c] : void 0;
    if (d && typeof a == "string") {
      const m = qt[d], y = Object.keys(m).find(
        (h) => a === h || a === m[h]
      );
      y && (f = y);
    }
    if (e === "comic" && c === "cast" && rt(a)) {
      const m = /* @__PURE__ */ Object.create(null);
      for (const [y, h] of Object.entries(a))
        m[y] = ae(h, "cast", t, `${s}.등장인물.${y}`);
      f = m;
    } else if (e === "comic" && c === "personas" && rt(a)) {
      const m = /* @__PURE__ */ Object.create(null);
      for (const [y, h] of Object.entries(a))
        m[y] = ae(
          h,
          "persona",
          t,
          `${s}.페르소나.${y}`
        );
      f = m;
    } else if (e === "cast" && c === "persona")
      f = ae(a, "persona", t, `${s}.페르소나`);
    else if (e === "cast" && c === "appearance")
      f = ae(a, "appearance", t, `${s}.외형`);
    else if (e === "panel" && c === "diagram")
      f = ae(a, "diagram", t, `${s}.다이어그램`);
    else if (Array.isArray(a)) {
      const m = e === "comic" && c === "panels" ? "panel" : e === "panel" && c === "actors" ? "actor" : e === "panel" && c === "dialogue" ? "dialogue" : e === "panel" && c === "transfer" ? "transfer" : void 0;
      m && (f = a.map(
        (y, h) => ae(
          y,
          m,
          t,
          `${s}.${i[c]}[${h + 1}]`
        )
      ));
    }
    r[l] = f;
  }
  return r;
}
const Zi = (n) => ae(n, "comic", !1, "만화");
function er(n) {
  const e = ae(n, "options", !1, "표시 설정");
  if (!rt(e)) throw new Error("표시 설정: 객체가 필요합니다.");
  for (const t of Object.keys(e))
    if (!Object.hasOwn(Y.options, t))
      throw new Error(`표시 설정: 알 수 없는 항목 '${t}'.`);
  return e;
}
function Re(n, e) {
  if (!n || typeof n != "object" || Array.isArray(n))
    throw new Error(`${e}: 객체가 필요합니다.`);
  return n;
}
function se(n, e, t = 1e4) {
  if (typeof n != "string" || !n.trim())
    throw new Error(`${e}: 비어 있지 않은 문자열이 필요합니다.`);
  if (n.length > t)
    throw new Error(
      `${e}: 텍스트가 너무 깁니다. ${t}자 이내로 작성하세요.`
    );
  return n;
}
function an(n, e, t) {
  for (const s of Object.keys(n))
    if (!Object.hasOwn(e, s))
      throw new Error(`${t}: 알 수 없는 항목 '${s}'.`);
}
function Sn(n, e) {
  const t = Re(n, e);
  an(t, Y.persona, e);
  const s = {};
  if (t.role !== void 0 && (s.role = se(t.role, `${e}.직무`, 100)), t.personality !== void 0 && (s.personality = se(t.personality, `${e}.성격`, 300)), t.speechStyle !== void 0 && (s.speechStyle = se(t.speechStyle, `${e}.말투`, 300)), !Object.keys(s).length)
    throw new Error(`${e}: 직무·성격·말투 중 하나 이상 작성하세요.`);
  return s;
}
function Ct(n, e, t) {
  if (n === void 0) return e;
  const s = se(n, t, 7);
  if (s.length !== 4 && s.length !== 7 || !/^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i.test(s))
    throw new Error(`${t}: #RGB 또는 #RRGGBB 색상을 작성하세요.`);
  return s;
}
function vn(n, e, t, s) {
  if (n === void 0) return t;
  const i = se(n, s);
  if (!Object.hasOwn(e, i))
    throw new Error(
      `${s}: ${Object.values(e).join(", ")} 중 하나를 선택하세요.`
    );
  return i;
}
function tr(n, e) {
  const t = n === void 0 ? {} : Re(n, e);
  if (an(t, Y.appearance, e), t.glasses !== void 0 && typeof t.glasses != "boolean")
    throw new Error(`${e}.안경: true 또는 false가 필요합니다.`);
  return {
    skinColor: Ct(
      t.skinColor,
      pe.skinColor,
      `${e}.피부색`
    ),
    hairStyle: vn(
      t.hairStyle,
      qt.hairStyle,
      pe.hairStyle,
      `${e}.머리모양`
    ),
    hairColor: Ct(
      t.hairColor,
      pe.hairColor,
      `${e}.머리색`
    ),
    outfit: vn(
      t.outfit,
      qt.outfit,
      pe.outfit,
      `${e}.옷`
    ),
    outfitColor: Ct(
      t.outfitColor,
      pe.outfitColor,
      `${e}.옷색`
    ),
    glasses: t.glasses === void 0 ? pe.glasses : t.glasses
  };
}
function nr(n, e) {
  const t = /* @__PURE__ */ Object.create(null);
  if (e !== void 0)
    for (const [i, r] of Object.entries(
      Re(e, "페르소나")
    ))
      se(i, "페르소나 식별자"), t[i] = Sn(r, `페르소나.${i}`);
  const s = /* @__PURE__ */ Object.create(null);
  for (const [i, r] of Object.entries(Re(n, "등장인물"))) {
    const o = `등장인물.${i}`, a = Re(r, o);
    an(a, Y.cast, o);
    const c = se(a.asset, `${o}.그림`);
    if (!Object.hasOwn(In, c))
      throw new Error(`${o}: 없는 에셋 '${c}'.`);
    let l;
    if (a.persona !== void 0)
      if (typeof a.persona == "string") {
        const f = se(a.persona, `${o}.페르소나`);
        if (!Object.hasOwn(t, f))
          throw new Error(`${o}.페르소나: 없는 페르소나 '${f}'.`);
        l = { ...t[f] };
      } else l = Sn(a.persona, `${o}.페르소나`);
    if (c !== "human" && a.appearance !== void 0)
      throw new Error(`${o}.외형: 사람 그림에서만 사용할 수 있습니다.`);
    s[i] = {
      asset: c,
      label: a.label === void 0 ? i : se(a.label, `${o}.이름표`),
      ...c === "human" ? { appearance: tr(a.appearance, `${o}.외형`) } : {},
      ...l ? { persona: l } : {}
    };
  }
  return { cast: s, ...e !== void 0 ? { personas: t } : {} };
}
function ue(n, e) {
  if (!n || typeof n != "object" || Array.isArray(n))
    throw new Error(`${e}: 객체가 필요합니다.`);
  return n;
}
function Q(n, e, t = 1e4) {
  if (typeof n != "string" || !n.trim())
    throw new Error(`${e}: 비어 있지 않은 문자열이 필요합니다.`);
  if (n.length > t)
    throw new Error(
      `${e}: 텍스트가 너무 깁니다. ${t}자 이내로 작성하세요.`
    );
  return n;
}
function ve(n, e) {
  if (!Array.isArray(n)) throw new Error(`${e}: 목록이 필요합니다.`);
  return n;
}
function he(n, e, t) {
  for (const s of Object.keys(n))
    if (!e.includes(s))
      throw new Error(`${t}: 알 수 없는 항목 '${s}'.`);
}
function de(n, e, t, s) {
  if (n !== void 0) {
    if (typeof n != "number" || !Number.isFinite(n) || n < e || n > t)
      throw new Error(`${s}: ${e}~${t} 사이 숫자가 필요합니다.`);
    return n;
  }
}
function sr(n) {
  if (n.length > 1e5)
    throw new Error("코드가 너무 깁니다. 100KB 이내로 작성하세요.");
  const e = Ji(n, { uniqueKeys: !0 });
  if (e.errors.length) throw new Error(e.errors[0].message);
  const t = ue(Zi(e.toJS({ maxAliasCount: 20 })), "만화");
  he(t, Object.keys(Y.comic), "만화");
  const { cast: s, personas: i } = nr(t.cast, t.personas);
  let r;
  const o = ve(t.panels, "컷").map((a, c) => {
    const l = `컷 ${c + 1}`, f = { ...ue(a, l) };
    if (he(f, Object.keys(Y.panel), l), f.mode !== void 0 && f.mode !== "before" && f.mode !== "full")
      throw new Error(`${l}: 구성은 전체 또는 이전이어야 합니다.`);
    if (f.mode === "before") {
      if (!r)
        throw new Error(`${l}: 첫 컷에서는 이전 구성을 사용할 수 없습니다.`);
      const h = r.actors.map(
        (p) => ({ ...p })
      ), g = ve(f.removeActors ?? [], `${l}.제외인물`).map(
        (p) => Q(p, `${l}.제외인물`)
      );
      for (const p of g)
        if (!h.some((b) => b.id === p))
          throw new Error(`${l}: 제거할 인물 '${p}'가 이전 컷에 없습니다.`);
      const w = h.filter(
        (p) => !g.some((b) => b === p.id)
      ), S = ve(f.actors ?? [], `${l}.인물`), k = /* @__PURE__ */ new Set();
      for (const p of S) {
        const b = typeof p == "string" ? { id: p } : ue(p, `${l}.인물`);
        he(b, Object.keys(Y.actor), `${l}.인물`);
        const v = Q(b.id, `${l}.인물.식별자`);
        if (k.has(v))
          throw new Error(`${l}: 캐릭터 식별자가 중복됩니다.`);
        k.add(v);
        const x = w.findIndex((N) => N.id === v), $ = {
          ...x < 0 ? {} : w[x],
          ...b
        };
        for (const [N, C] of Object.entries(b))
          N !== "id" && C === null && delete $[N];
        x < 0 ? w.push($) : w[x] = $;
      }
      f.actors = f.actors !== void 0 && S.length === 0 ? [] : w;
    } else if (f.removeActors !== void 0)
      throw new Error(`${l}: 제외인물은 이전 구성에서만 사용할 수 있습니다.`);
    const u = ve(f.actors, `${l}.인물`).map((h) => {
      const g = typeof h == "string" ? { id: h } : ue(h, `${l}.인물`);
      he(g, Object.keys(Y.actor), `${l}.인물`);
      const w = Q(g.id, `${l}.인물.식별자`), S = g.expression === void 0 ? "neutral" : Q(g.expression, `${l}.${w}.표정`);
      if (!Object.hasOwn(s, w))
        throw new Error(`${l}: 없는 캐릭터 '${w}'.`);
      if (!Object.hasOwn(jn, S))
        throw new Error(`${l}.${w}: 없는 표정 '${S}'.`);
      const k = g.gesture === void 0 ? void 0 : Q(g.gesture, `${l}.${w}.손모양`), p = g.holding === void 0 ? void 0 : Q(g.holding, `${l}.${w}.든소품`);
      if (k && !Object.hasOwn(Bn, k))
        throw new Error(`${l}.${w}: 없는 손 제스처 '${k}'.`);
      if (p && !Object.hasOwn(ot, p))
        throw new Error(`${l}.${w}: 없는 소품 '${p}'.`);
      return {
        id: w,
        expression: S,
        gesture: k,
        holding: p,
        x: de(g.x, 0, 1, `${l}.${w}.가로위치`),
        y: de(g.y, 0, 1, `${l}.${w}.세로위치`),
        scale: de(g.scale, 0.5, 1.25, `${l}.${w}.배율`) ?? 1
      };
    });
    if (u.length < 1 || u.length > 3)
      throw new Error(`${l}: 캐릭터는 1~3명이어야 합니다.`);
    if (new Set(u.map((h) => h.id)).size !== u.length)
      throw new Error(`${l}: 캐릭터 식별자가 중복됩니다.`);
    const d = ve(f.dialogue ?? [], `${l}.대사`).map(
      (h) => {
        const g = ue(h, `${l}.대사`);
        he(g, Object.keys(Y.dialogue), `${l}.대사`);
        const w = Q(g.from, `${l}.대사.화자`), S = g.to === void 0 ? void 0 : Q(g.to, `${l}.대사.상대`);
        if (!u.some((k) => k.id === w))
          throw new Error(`${l}: 화자 '${w}'가 컷에 없습니다.`);
        if (S && !u.some((k) => k.id === S))
          throw new Error(`${l}: 대화 상대 '${S}'가 컷에 없습니다.`);
        return {
          from: w,
          to: S,
          text: Q(g.text, `${l}.대사.내용`),
          x: de(g.x, 0, 1, `${l}.대사.가로위치`),
          y: de(g.y, 0, 1, `${l}.대사.세로위치`),
          fontSize: de(g.fontSize, 12, 32, `${l}.대사.글자크기`) ?? 18
        };
      }
    );
    if (d.length > 20)
      throw new Error(`${l}: 대사는 20개 이내로 작성하세요.`);
    const m = ve(f.transfer ?? [], `${l}.전달`).map(
      (h) => {
        const g = ue(h, `${l}.전달`);
        he(g, Object.keys(Y.transfer), `${l}.전달`);
        const w = Q(g.from, `${l}.전달.주는인물`), S = Q(g.to, `${l}.전달.받는인물`), k = Q(g.prop, `${l}.전달.소품`);
        if (!u.some((p) => p.id === w))
          throw new Error(`${l}: 전달 주체 '${w}'가 컷에 없습니다.`);
        if (!u.some((p) => p.id === S))
          throw new Error(`${l}: 전달 대상 '${S}'가 컷에 없습니다.`);
        if (w === S)
          throw new Error(`${l}: 전달 주체와 대상은 달라야 합니다.`);
        if (!Object.hasOwn(ot, k))
          throw new Error(`${l}: 없는 소품 '${k}'.`);
        return { from: w, to: S, prop: k };
      }
    );
    if (m.length > 6)
      throw new Error(`${l}: 소품 전달은 6개 이내로 작성하세요.`);
    let y;
    if (f.diagram !== void 0 && f.diagram !== null) {
      const h = `${l}.다이어그램`, g = ue(f.diagram, h);
      if (he(g, Object.keys(Y.diagram), h), g.type !== "mermaid")
        throw new Error(`${h}.종류: 머메이드여야 합니다.`);
      y = {
        type: "mermaid",
        source: Q(g.source, `${h}.원문`, 2e4),
        title: g.title === void 0 ? "다이어그램" : Q(g.title, `${h}.제목`, 100),
        height: de(g.height, 160, 1200, `${h}.높이`)
      };
    }
    return r = { actors: u, dialogue: d, transfer: m, ...y ? { diagram: y } : {} }, r;
  });
  if (o.length < 1 || o.length > 30)
    throw new Error("컷은 1~30개여야 합니다.");
  return {
    title: t.title === void 0 ? "Comic Gen" : Q(t.title, "제목"),
    cast: s,
    panels: o,
    ...i ? { personas: i } : {}
  };
}
const Pe = (n, e, t) => Math.max(e, Math.min(t, n));
function It(n, e, t, s) {
  const i = document.createElement("canvas").getContext("2d");
  i.font = `${t}px ${s}`;
  const r = [];
  for (const o of n.split(`
`)) {
    let a = "";
    for (const c of Array.from(o))
      a && i.measureText(a + c).width > e && (r.push(a), a = ""), a += c;
    r.push(a);
  }
  return r;
}
function bs(n, e, t, s, i = "compact", r) {
  const o = Math.min(t - 80, 390), a = n.dialogue.map((p) => ({
    line: p,
    lines: It(p.text, o - 36, p.fontSize, s),
    lineHeight: Math.ceil(p.fontSize * 1.45)
  })), c = a.reduce(
    (p, b) => p + 60 + b.lines.length * b.lineHeight,
    20
  ), l = c + 254, f = Math.max(
    ...n.actors.map((p) => p.holding || p.gesture ? 92 : 60)
  ), u = (t - 72) / n.actors.length, d = Math.min(
    1,
    (u - 12) / (2 * f * Math.max(...n.actors.map((p) => p.scale)))
  ), m = n.actors.map((p) => p.scale * d), y = n.actors.map(
    (p, b) => Pe(
      36 + (t - 72) * (p.x ?? (b + 0.5) / n.actors.length),
      26 + f * m[b],
      t - 26 - f * m[b]
    )
  ), h = n.actors.map(
    (p, b) => Pe(
      p.y === void 0 ? l - 126 : p.y * l,
      c + 70 * m[b],
      l - 126 * m[b]
    )
  );
  for (let p = 0; p < n.actors.length; p++)
    for (let b = p + 1; b < n.actors.length; b++)
      if (Math.abs(y[p] - y[b]) < f * (m[p] + m[b]) && Math.abs(h[p] - h[b]) < 120 * Math.max(m[p], m[b]))
        throw new Error(
          `캐릭터 '${n.actors[p].id}'와 '${n.actors[b].id}'가 겹칩니다. 가로위치·세로위치 또는 배율을 조정하세요.`
        );
  const g = [
    `<rect x="20" y="0" width="${t - 40}" height="${l}" rx="18" fill="white" stroke="#303341" stroke-width="2.5"/>`
  ];
  let w = 20;
  a.forEach(({ line: p, lines: b, lineHeight: v }) => {
    const x = y[n.actors.findIndex((j) => j.id === p.from)], $ = Pe(
      (p.x === void 0 ? x : p.x * t) - o / 2,
      40,
      t - o - 40
    ), N = 28 + b.length * v, C = p.y === void 0 ? w : Pe(p.y * l, 20, c - N), P = Math.max($ + 24, Math.min($ + o - 24, x)), A = $ + o, D = C + N, E = n.actors.findIndex(
      (j) => j.id === p.from
    ), T = h[E] - 65 * m[E], _ = `M${$ + 14} ${C}H${A - 14}Q${A} ${C} ${A} ${C + 14}V${D - 14}Q${A} ${D} ${A - 14} ${D}H${P + 9}L${x} ${T}L${P - 9} ${D}H${$ + 14}Q${$} ${D} ${$} ${D - 14}V${C + 14}Q${$} ${C} ${$ + 14} ${C}Z`;
    g.push(
      `<g data-dialogue="${H(p.from)}" data-to="${H(p.to ?? "")}"><path d="${_}" fill="#fffaf0" stroke="#303341" stroke-width="2" stroke-linejoin="round"/><text x="${$ + 18}" y="${C + 18 + p.fontSize}" font-size="${p.fontSize}">${b.map((j, M) => `<tspan x="${$ + 18}" dy="${M ? v : 0}">${H(j)}</tspan>`).join("")}</text></g>`
    ), w += N + 32;
  }), n.actors.forEach((p, b) => {
    const v = e[p.id], x = fn(v), $ = v.asset === "human", N = $ ? x.color : "white", C = new Set(
      n.transfer.flatMap((M) => {
        const F = M.from === p.id ? M.to : M.to === p.id ? M.from : void 0;
        if (!F) return [];
        const be = n.actors.findIndex(
          (re) => re.id === F
        );
        return [y[be] < y[b] ? "left" : "right"];
      })
    ), P = x.restingHands ? (p.gesture || C.has("left") ? "" : x.restingHands.left) + (p.holding || C.has("right") ? "" : x.restingHands.right) : "", A = n.dialogue.find(
      (M) => M.from === p.id && M.to
    )?.to, D = n.actors.findIndex((M) => M.id === A), E = D < 0 ? 0 : Math.sign(y[D] - y[b]) * 4, T = It(
      v.label,
      (t - 72) / n.actors.length - 12,
      16,
      s
    );
    if (T.length > 2)
      throw new Error(`캐릭터 '${p.id}'의 이름표가 너무 깁니다.`);
    const _ = p.gesture ? `<g data-gesture="${p.gesture}">${p.gesture === "point" && x.pointGesture ? x.pointGesture : $ ? Bn[p.gesture].replace('fill="white"', `fill="${N}"`) : Ks[p.gesture]}</g>` : "", j = p.holding ? `<g data-holding="${p.holding}"><circle data-hand="holding" cx="58" cy="20" r="11" fill="${N}"/><g data-prop="${p.holding}" transform="translate(73 6)">${ot[p.holding]}</g></g>` : "";
    g.push(
      `<g data-character="${H(p.id)}" transform="translate(${y[b]} ${h[b]}) scale(${m[b]})" stroke="#303341" stroke-width="2.8" stroke-linecap="round"><ellipse cy="69" rx="51" ry="7" fill="#e8edf3" stroke="none"/>${x.body}<g transform="translate(${E} ${x.faceY})" fill="#303341">${jn[p.expression]}</g>${P}${_}${j}<text y="94" text-anchor="middle" stroke="none" fill="#303341" font-size="16">${T.map((M, F) => `<tspan x="0" dy="${F ? 18 : 0}">${H(M)}</tspan>`).join("")}</text></g>`
    );
  }), n.transfer.forEach((p, b) => {
    const v = n.actors.findIndex(
      (M) => M.id === p.from
    ), x = n.actors.findIndex((M) => M.id === p.to), $ = y[v], N = y[x], C = Math.sign(N - $), P = $ + 62 * m[v] * C, A = N - 62 * m[x] * C, D = 20 + (b - (n.transfer.length - 1) / 2) * 12, E = h[v] + D * m[v], T = h[x] + D * m[x], _ = Math.atan2(T - E, A - P) * 180 / Math.PI, j = (M) => {
      const F = e[n.actors[M].id];
      return F.asset === "human" ? fn(F).color : "white";
    };
    g.push(
      `<g data-transfer="${H(p.from)}" data-to="${H(p.to)}" stroke="#586c8c" stroke-width="2.5"><path d="M${P} ${E}L${A} ${T}" fill="none"/><circle data-hand="transfer" cx="${P}" cy="${E}" r="${9 * m[v]}" fill="${j(v)}"/><circle data-hand="receive" cx="${A}" cy="${T}" r="${9 * m[x]}" fill="${j(x)}"/><path transform="translate(${A} ${T}) rotate(${_})" d="M-12 -5L-4 0L-12 5" fill="none"/><g data-prop="${p.prop}" transform="translate(${(P + A) / 2} ${(E + T) / 2 - 16})">${ot[p.prop]}</g></g>`
    );
  });
  let S = g.slice(1).join(""), k = l;
  if (r && n.diagram) {
    const p = t - 80, b = p - 32, v = n.diagram.height ?? Pe(b * r.height / r.width + 58, 180, 1200), x = v - 58, $ = Math.min(
      b / r.width,
      x / r.height
    ), N = 56 + (b - r.width * $) / 2, C = 66 + (x - r.height * $) / 2;
    if (It(n.diagram.title, b, 16, s).length > 1)
      throw new Error(
        "다이어그램 제목이 너무 깁니다. 제목이나 너비를 조정하세요."
      );
    S = `<g data-diagram="mermaid"><rect x="40" y="20" width="${p}" height="${v}" rx="10" fill="#f3f7fc" stroke="#8093ab" stroke-width="2"/><text x="56" y="48" font-size="16" font-weight="700">${H(n.diagram.title)}</text><g data-diagram-content="mermaid" transform="translate(${N} ${C}) scale(${$})">${r.svg}</g></g><g data-scene="true" transform="translate(0 ${v + 40})">${S}</g>`, k += v + 40;
  }
  if (i === "phone") {
    const p = k * 2 + 92;
    return {
      markup: `<rect x="20" y="0" width="${t - 40}" height="${p}" rx="18" fill="white" stroke="#303341" stroke-width="2.5"/><g transform="translate(0 ${(p - k) / 2})">${S}</g>`,
      height: p
    };
  }
  return r ? {
    markup: `<rect x="20" y="0" width="${t - 40}" height="${k}" rx="18" fill="white" stroke="#303341" stroke-width="2.5"/>${S}`,
    height: k
  } : { markup: g.join(""), height: l };
}
const ir = "https://cdn.jsdelivr.net/gh/jhs512/comic-gen@v0.6.0/cdn/comic-gen.mermaid.js", Rt = 2e4, rr = "http://www.w3.org/2000/svg", or = Math.random().toString(36).slice(2);
let ar = 0, En = Promise.resolve();
const $t = [
  "fill",
  "fill-opacity",
  "fill-rule",
  "stroke",
  "stroke-width",
  "stroke-opacity",
  "stroke-dasharray",
  "stroke-dashoffset",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-miterlimit",
  "color",
  "opacity",
  "font-family",
  "font-size",
  "font-style",
  "font-weight",
  "font-variant",
  "text-anchor",
  "dominant-baseline",
  "alignment-baseline",
  "baseline-shift",
  "letter-spacing",
  "word-spacing",
  "text-decoration",
  "visibility",
  "marker-start",
  "marker-mid",
  "marker-end",
  "clip-path",
  "mask",
  "filter",
  "paint-order"
], lr = new Set($t), cr = /* @__PURE__ */ new Set([
  "svg",
  "g",
  "defs",
  "marker",
  "clippath",
  "mask",
  "pattern",
  "lineargradient",
  "radialgradient",
  "stop",
  "path",
  "rect",
  "circle",
  "ellipse",
  "line",
  "polyline",
  "polygon",
  "text",
  "tspan",
  "textpath",
  "title",
  "desc",
  "use",
  "filter",
  "fegaussianblur",
  "feoffset",
  "feblend",
  "fecolormatrix",
  "fecomponenttransfer",
  "fefunca",
  "fefuncb",
  "fefuncg",
  "fefuncr",
  "femerge",
  "femergenode",
  "feflood",
  "fecomposite"
]), fr = /* @__PURE__ */ new Set([
  "id",
  "class",
  "style",
  "xmlns",
  "xmlns:xlink",
  "xml:space",
  "role",
  "viewbox",
  "preserveaspectratio",
  "width",
  "height",
  "x",
  "y",
  "x1",
  "y1",
  "x2",
  "y2",
  "dx",
  "dy",
  "cx",
  "cy",
  "r",
  "rx",
  "ry",
  "d",
  "points",
  "transform",
  "pathlength",
  "refx",
  "refy",
  "markerwidth",
  "markerheight",
  "markerunits",
  "orient",
  "clippathunits",
  "maskunits",
  "maskcontentunits",
  "patternunits",
  "patterncontentunits",
  "patterntransform",
  "gradientunits",
  "gradienttransform",
  "offset",
  "stop-color",
  "stop-opacity",
  "spreadmethod",
  "href",
  "xlink:href",
  "textlength",
  "lengthadjust",
  "vector-effect",
  "filterunits",
  "primitiveunits",
  "in",
  "in2",
  "result",
  "stddeviation",
  "mode",
  "type",
  "values",
  "operator",
  "k1",
  "k2",
  "k3",
  "k4",
  "slope",
  "intercept",
  "amplitude",
  "exponent",
  "tablevalues",
  ...$t
]);
function ur(n) {
  if (!n.trim() || n.length > Rt)
    throw new Error(`Mermaid 원문은 1~${Rt}자여야 합니다.`);
  const e = document.createElement("textarea");
  e.innerHTML = n.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const t = e.value;
  if (/%%\s*\{|^\s*---\s*(?:\r?\n|$)/m.test(t))
    throw new Error(
      "Mermaid 원문 안의 설정 지시문과 frontmatter는 지원하지 않습니다."
    );
  if (/<(?:\s*\/?\s*(?:script|style|img|image|svg|foreignobject|iframe|object|embed|link|a|html|body|div|span|p|br|b|i|em|strong|input|video|audio|canvas|math)\b|[!?])/i.test(
    t
  ) || /<[a-z][^>]*\s+[a-z_:][\w:.-]*\s*=/i.test(t))
    throw new Error(
      "Mermaid 원문에는 HTML 대신 일반 텍스트 라벨을 사용해 주세요."
    );
  if (/@\s*\{/.test(t) || /(?:^|[;\r\n])\s*(?:click|links?|style|classDef|linkStyle|cssClass)\s/i.test(
    t
  ) || /(?:\b(?:img|image|icon)\s*:|url\s*\(|@import|javascript\s*:|vbscript\s*:|data\s*:\s*[a-z]+\/)/i.test(
    t
  ))
    throw new Error(
      "Mermaid 노드 메타데이터(@{}), 이미지·링크·CSS 선언과 외부 리소스는 지원하지 않습니다."
    );
}
function hr(n) {
  if (typeof n != "string" || !n.trim() || n.length > 300 || /[^\p{L}\p{N}\s,'"_\-]/u.test(n))
    throw new Error("다이어그램에 사용할 올바른 글꼴 이름이 필요합니다.");
  return n;
}
async function dr(n) {
  const e = document.createElement("iframe");
  e.title = "Mermaid 렌더링", e.tabIndex = -1, e.setAttribute("aria-hidden", "true"), e.style.cssText = "all:initial!important;display:block!important;width:20000px!important;height:20000px!important;border:0!important;", n.append(e);
  const t = e.contentDocument, s = e.contentWindow;
  if (!t?.body || !s)
    throw e.remove(), new Error("Mermaid 격리 문서를 만들지 못했습니다.");
  const i = t.createElement("script");
  i.type = "module", i.src = ir;
  try {
    return { api: await new Promise((o, a) => {
      const c = window.setTimeout(() => {
        l(), a(new Error("Mermaid 모듈을 불러오는 시간이 초과되었습니다."));
      }, 3e4), l = () => {
        window.clearTimeout(c), i.onload = null, i.onerror = null, s.removeEventListener("comic-gen-mermaid-ready", f), s.removeEventListener("comic-gen-mermaid-error", u);
      }, f = () => {
        l();
        const d = s.__comicGenMermaid;
        typeof d?.initialize != "function" || typeof d?.render != "function" ? a(new Error("Mermaid 모듈을 불러오지 못했습니다.")) : o(d);
      }, u = () => {
        l(), a(new Error("Mermaid 모듈을 불러오지 못했습니다."));
      };
      s.addEventListener("comic-gen-mermaid-ready", f), s.addEventListener("comic-gen-mermaid-error", u), i.onload = () => {
        s.__comicGenMermaid && f();
      }, i.onerror = u, t.head.append(i);
    }), document: t, dispose: () => e.remove() };
  } catch (r) {
    throw e.remove(), r;
  }
}
function ks(n) {
  const e = new DOMParser().parseFromString(n, "image/svg+xml");
  if (e.querySelector("parsererror") || e.documentElement.localName !== "svg")
    throw new Error("Mermaid가 올바른 SVG를 만들지 못했습니다.");
  return e.documentElement;
}
function ft(n, e, t = !1) {
  let s = !0;
  const i = n.replace(
    /url\(\s*(["']?)(.*?)\1\s*\)/gi,
    (r, o, a) => {
      let c = a.trim();
      if (t && !c.startsWith("#")) {
        const l = c.lastIndexOf("#");
        c = l >= 0 ? c.slice(l) : "";
      }
      return !c.startsWith("#") || !e.has(c.slice(1)) ? (s = !1, "") : `url(${c})`;
    }
  );
  return /url\s*\(/i.test(i.replace(/url\(#[^)]*\)/g, "")) && (s = !1), s ? i : void 0;
}
function $s(n, e) {
  const t = document.createElement("span").style;
  for (const s of $t) {
    const i = ft(n.getPropertyValue(s), e);
    i && t.setProperty(s, i, n.getPropertyPriority(s));
  }
  return n.getPropertyValue("display") === "none" && (t.display = "none"), t.cssText;
}
function pr(n) {
  const e = [];
  let t = 0, s = 0, i = "";
  for (let r = 0; r < n.length; r++) {
    const o = n[r];
    i ? o === i && n[r - 1] !== "\\" && (i = "") : o === "'" || o === '"' ? i = o : o === "(" || o === "[" ? s++ : o === ")" || o === "]" ? s-- : o === "," && s === 0 && (e.push(n.slice(t, r).trim()), t = r + 1);
  }
  return e.push(n.slice(t).trim()), e;
}
function mr(n, e, t) {
  const s = new CSSStyleSheet();
  s.replaceSync(n);
  const i = [], r = `#${e}`;
  for (const o of s.cssRules) {
    if (!(o instanceof CSSStyleRule)) continue;
    if (!pr(o.selectorText).every(
      (l) => l === r || l.startsWith(r + " ") || l.startsWith(r + ">") || l.startsWith(r + ":")
    )) throw new Error("Mermaid SVG에 범위 밖 스타일이 있습니다.");
    const c = $s(o.style, t);
    c && i.push(`${o.selectorText}{${c}}`);
  }
  return i.join(`
`);
}
function gr(n) {
  if (n.length > 2e6)
    throw new Error("Mermaid SVG가 너무 큽니다. 다이어그램을 나누어 주세요.");
  const e = ks(n), t = [e, ...e.querySelectorAll("*")];
  if (t.length > 1e4)
    throw new Error(
      "Mermaid SVG 요소가 너무 많습니다. 다이어그램을 나누어 주세요."
    );
  const s = new Set(t.map((r) => r.id).filter(Boolean)), i = e.id;
  for (const r of t)
    for (const o of [...r.attributes])
      if (/url\s*\(/i.test(o.value)) {
        const a = ft(o.value, s, !0);
        a === void 0 ? r.removeAttributeNode(o) : r.setAttribute(o.name, a);
      }
  for (const r of t) {
    const o = r.localName.toLowerCase();
    if (r.namespaceURI !== rr || !cr.has(o) && o !== "style") {
      o === "a" ? r.replaceWith(...r.childNodes) : r.remove();
      continue;
    }
    if (o === "style") {
      r.textContent = mr(r.textContent ?? "", i, s);
      continue;
    }
    for (const a of [...r.attributes]) {
      const c = a.name.toLowerCase(), l = a.value;
      if (!fr.has(c) && !c.startsWith("aria-") && !c.startsWith("data-"))
        r.removeAttributeNode(a);
      else if (c === "href" || c === "xlink:href")
        (!l.startsWith("#") || !s.has(l.slice(1))) && r.removeAttributeNode(a);
      else if (c === "style") {
        const f = document.createElement("span").style;
        f.cssText = l, r.setAttribute("style", $s(f, s));
      } else if (lr.has(c)) {
        const f = ft(l, s);
        f === void 0 ? r.removeAttributeNode(a) : r.setAttribute(a.name, f);
      }
    }
  }
  return e;
}
function yr(n) {
  if (n.length > 3e6)
    throw new Error("Mermaid SVG가 너무 큽니다. 다이어그램을 나누어 주세요.");
  const e = n.match(
    /\bsrc="data:text\/html;charset=UTF-8;base64,([^"]+)"/i
  )?.[1];
  if (!e) throw new Error("Mermaid 격리 문서에서 SVG를 읽지 못했습니다.");
  const t = Uint8Array.from(
    atob(e),
    (o) => o.charCodeAt(0)
  ), s = new TextDecoder().decode(t), r = new DOMParser().parseFromString(s, "text/html").querySelector("svg");
  if (!r) throw new Error("Mermaid 격리 문서에서 SVG를 읽지 못했습니다.");
  return r.outerHTML;
}
function wr(n) {
  const e = (n.getAttribute("viewBox") ?? "").trim().split(/[\s,]+/).map(Number), t = e.length === 4 ? e[2] : Number.parseFloat(n.getAttribute("width") ?? ""), s = e.length === 4 ? e[3] : Number.parseFloat(n.getAttribute("height") ?? "");
  if (!Number.isFinite(t) || !Number.isFinite(s) || t <= 0 || s <= 0 || t > 2e4 || s > 2e4 || t * s > 16e7)
    throw new Error(
      "Mermaid 다이어그램 크기가 너무 큽니다. 다이어그램을 나누어 주세요."
    );
  return (e.length !== 4 || e.some((i) => !Number.isFinite(i))) && n.setAttribute("viewBox", `0 0 ${t} ${s}`), n.setAttribute("width", String(t)), n.setAttribute("height", String(s)), n.setAttribute("preserveAspectRatio", "xMidYMid meet"), { width: t, height: s };
}
async function br(n, e) {
  if (typeof document > "u" || !document.body)
    throw new Error("Mermaid 렌더링에는 브라우저 문서가 필요합니다.");
  ur(n), e = hr(e);
  const t = En.then(async () => {
    await Promise.all([
      document.fonts.load(`18px ${e}`, n),
      document.fonts.load(`bold 18px ${e}`, n),
      document.fonts.load(`italic 18px ${e}`, n)
    ]), await document.fonts.ready;
    const s = `comic-gen-mermaid-${or}-${++ar}`, i = document.createElement("div");
    i.dataset.comicDiagramTemporary = "", i.style.cssText = "all:initial!important;display:block!important;position:fixed!important;left:-100000px!important;top:0!important;width:20000px!important;pointer-events:none!important;opacity:0!important;";
    const r = [...document.fonts].filter(
      (l) => l.status === "loaded"
    );
    let o, a;
    const c = new MutationObserver(() => {
      const l = a?.querySelector("iframe"), f = l?.contentDocument;
      if (!(!l || !f)) {
        l.style.cssText = "all:initial!important;display:block!important;width:20000px!important;height:20000px!important;border:0!important;";
        for (const u of r) f.fonts.add(u);
      }
    });
    document.body.append(i);
    try {
      o = await dr(i);
      for (const k of r) o.document.fonts.add(k);
      a = o.document.createElement("div"), a.style.cssText = "width:20000px;", o.document.body.append(a), c.observe(a, { childList: !0, subtree: !0 });
      const l = o.api;
      l.initialize({
        startOnLoad: !1,
        securityLevel: "sandbox",
        suppressErrorRendering: !0,
        maxTextSize: Rt,
        maxEdges: 500,
        htmlLabels: !1,
        fontFamily: e,
        theme: "neutral",
        themeVariables: { fontFamily: e, fontSize: "18px" },
        flowchart: { htmlLabels: !1, useMaxWidth: !1 },
        class: { htmlLabels: !1, useMaxWidth: !1 },
        sequence: {
          useMaxWidth: !1,
          actorFontFamily: e,
          noteFontFamily: e,
          messageFontFamily: e
        },
        secure: [
          "secure",
          "securityLevel",
          "startOnLoad",
          "maxTextSize",
          "maxEdges",
          "suppressErrorRendering",
          "htmlLabels",
          "theme",
          "themeCSS",
          "themeVariables",
          "fontFamily",
          "altFontFamily"
        ]
      });
      const f = await l.render(s, n, a);
      c.disconnect();
      const u = gr(yr(f.svg)), d = wr(u), m = i.attachShadow({ mode: "closed" });
      m.append(document.importNode(u, !0));
      const y = m.firstElementChild, h = [y, ...y.querySelectorAll("*")], g = new Set(
        h.map((k) => k.id).filter(Boolean)
      ), w = h.map((k) => {
        if (k.localName === "style") return "";
        const p = getComputedStyle(k), b = document.createElement("span").style;
        for (const v of $t) {
          const x = ft(
            p.getPropertyValue(v),
            g,
            !0
          );
          x && b.setProperty(v, x, "important");
        }
        return p.display === "none" && b.setProperty("display", "none", "important"), b.cssText;
      });
      h.forEach((k, p) => {
        k.localName === "style" ? k.remove() : (k.setAttribute("style", w[p]), k.removeAttribute("class"));
      }), y.style.removeProperty("visibility"), y.style.setProperty("width", `${d.width}px`, "important"), y.style.setProperty("height", `${d.height}px`, "important"), y.style.setProperty("max-width", "none", "important"), y.style.setProperty("max-height", "none", "important");
      const S = new XMLSerializer().serializeToString(y);
      if (S.length > 2e6)
        throw new Error(
          "Mermaid SVG가 너무 큽니다. 다이어그램을 나누어 주세요."
        );
      return { svg: S, ...d };
    } finally {
      c.disconnect(), o?.document.getElementById(s)?.remove(), o?.document.getElementById(`d${s}`)?.remove(), o?.document.getElementById(`i${s}`)?.remove(), o?.dispose(), i.remove();
    }
  });
  return En = t.catch(() => {
  }), t;
}
function kr(n, e) {
  if (!/^[A-Za-z][A-Za-z0-9_-]{0,120}$/.test(e))
    throw new Error("다이어그램 SVG 식별자 접두사가 올바르지 않습니다.");
  const t = ks(n.svg), s = [t, ...t.querySelectorAll("*")], i = /* @__PURE__ */ new Map();
  let r = 0;
  const o = (a) => {
    const c = a.localName === "svg" ? a : a.closest("svg");
    let l = i.get(c);
    return l || (l = /* @__PURE__ */ new Map(), i.set(c, l)), l;
  };
  for (const a of s) {
    if (!a.id) continue;
    const c = o(a);
    if (c.has(a.id))
      throw new Error("다이어그램 SVG 식별자가 중복됩니다.");
    c.set(a.id, `${e}-${r++}`);
  }
  for (const a of s) {
    const c = o(a);
    for (const l of [...a.attributes])
      if (l.name === "id")
        a.setAttribute("id", c.get(l.value));
      else if (l.localName === "href" && l.value.startsWith("#")) {
        const f = c.get(l.value.slice(1));
        f && a.setAttribute(l.name, `#${f}`);
      } else l.name === "aria-labelledby" || l.name === "aria-describedby" ? a.setAttribute(
        l.name,
        l.value.split(/\s+/).map((f) => c.get(f) ?? f).join(" ")
      ) : /url\(/i.test(l.value) && a.setAttribute(
        l.name,
        l.value.replace(
          /url\(\s*(["']?)#([^"')\s]+)\1\s*\)/gi,
          (f, u, d) => c.has(d) ? `url(#${c.get(d)})` : f
        )
      );
  }
  return new XMLSerializer().serializeToString(t);
}
let Ss = 0, $r = 0;
document.fonts.addEventListener("loadingdone", (n) => {
  n.fontfaces.length && Ss++;
});
function vs(n, e, t) {
  e = er(e);
  const s = sr(n), i = e.width ?? 720, r = e.panelFormat ?? t;
  if (r !== "compact" && r !== "phone")
    throw new Error("컷비율은 기본 또는 모바일이어야 합니다.");
  if (!Number.isFinite(i) || i < 480 || i > 2400)
    throw new Error("너비는 480~2400 사이여야 합니다.");
  const o = e.font ?? "Malgun Gothic, Apple SD Gothic Neo, sans-serif";
  if (typeof o != "string" || o.length > 300 || /[<>]/.test(o))
    throw new Error("올바른 글꼴 이름이 필요합니다.");
  return { comic: s, options: e, width: i, font: o, format: r };
}
function Es(n, e) {
  const { comic: t, width: s, font: i, options: r, format: o } = e;
  return JSON.stringify({
    panel: n,
    members: n.actors.map((a) => {
      const { asset: c, label: l, appearance: f } = t.cast[a.id];
      return [
        a.id,
        { asset: c, label: l, ...f ? { appearance: f } : {} }
      ];
    }),
    width: s,
    font: i,
    fontEpoch: Ss,
    fontVersion: r.fontVersion,
    assetVersion: Fs,
    layoutVersion: n.diagram ? 3 : 2,
    format: o
  });
}
function Ls(n) {
  return {
    svg: "",
    width: 0,
    height: 0,
    diagnostics: [n instanceof Error ? n.message : "렌더링 실패"],
    panels: []
  };
}
function xs(n, e, t) {
  const { comic: s, width: i, font: r } = n, o = [], a = [], c = `cg-${Date.now().toString(36)}-${++$r}-${Math.random().toString(36).slice(2, 9)}`, l = (u, d, m) => `<svg xmlns="http://www.w3.org/2000/svg" width="${i}" height="${d}" viewBox="0 0 ${i} ${d}" role="img" aria-label="${H(m)}"><title>${H(m)}</title><rect width="100%" height="100%" fill="#f5f7fb"/><g font-family="${H(r)}" fill="#303341"><text x="24" y="42" font-size="24" font-weight="700">${H(m)}</text>${u}</g></svg>`;
  let f = 68;
  for (const [u, d] of e.entries()) {
    const { markup: m, height: y, hit: h } = d, g = (w) => s.panels[u].diagram ? kr(
      {
        svg: `<svg xmlns="http://www.w3.org/2000/svg" width="${i}" height="${y}" viewBox="0 0 ${i} ${y}" style="width:${i}px!important;height:${y}px!important;max-width:none!important;max-height:none!important">${m}</svg>`
      },
      `${c}-${w}-${u}`
    ) : m;
    o.push(
      `<g data-panel="${u}" transform="translate(0 ${f})">${g("whole")}</g>`
    ), a.push({
      index: u,
      svg: l(
        `<g data-panel="${u}" transform="translate(0 68)">${g("panel")}</g>`,
        y + 92,
        `${s.title} · ${u + 1}/${s.panels.length}`
      ),
      width: i,
      height: y + 92,
      diagnostics: [],
      cache: { hits: h ? 1 : 0, misses: h ? 0 : 1, bytes: t.bytes }
    }), f += y + 24;
  }
  return {
    svg: l(o.join(""), f, s.title),
    width: i,
    height: f,
    diagnostics: [],
    panels: a,
    cache: {
      hits: e.filter((u) => u.hit).length,
      misses: e.filter((u) => !u.hit).length,
      bytes: t.bytes
    }
  };
}
function Ln(n, e, t, s = "compact") {
  try {
    const i = vs(n, e, s), r = i.comic.panels.findIndex(
      (a) => a.diagram
    );
    if (r >= 0)
      throw new Error(
        `컷 ${r + 1}.다이어그램: 만화그리기비동기(renderComicAsync) 또는 컷그리기비동기(renderPanelsAsync)를 await로 호출하세요.`
      );
    const o = i.comic.panels.map((a) => {
      const c = Es(a, i), l = t.get(c), f = l ?? bs(
        a,
        i.comic.cast,
        i.width,
        i.font,
        i.format
      );
      return l || t.set(c, f), { ...f, hit: !!l };
    });
    return xs(i, o, t);
  } catch (i) {
    return Ls(i);
  }
}
async function xn(n, e, t, s = "compact") {
  try {
    const i = vs(n, e, s);
    i.comic.panels.some((o) => o.diagram) && await document.fonts.ready;
    const r = [];
    for (const [o, a] of i.comic.panels.entries()) {
      const c = Es(a, i), l = t.get(c);
      if (l) {
        r.push({ ...l, hit: !0 });
        continue;
      }
      let f;
      if (a.diagram)
        try {
          f = await br(a.diagram.source, i.font);
        } catch (d) {
          throw new Error(
            `컷 ${o + 1}.다이어그램: ${d instanceof Error ? d.message : "Mermaid 렌더링 실패"}`
          );
        }
      const u = bs(
        a,
        i.comic.cast,
        i.width,
        i.font,
        i.format,
        f
      );
      t.set(c, u), r.push({ ...u, hit: !1 });
    }
    return xs(i, r, t);
  } catch (i) {
    return Ls(i);
  }
}
function Ns(n = 2e6) {
  const e = new qs(n);
  return {
    render: (t, s = {}) => Ln(t, s, e),
    renderPanels: (t, s = {}) => Ln(t, s, e, "phone"),
    renderAsync: (t, s = {}) => xn(t, s, e),
    renderPanelsAsync: (t, s = {}) => xn(t, s, e, "phone"),
    clearCache: () => e.clear()
  };
}
const St = Ns(), Or = St.render, Ar = St.renderPanels, Tr = St.renderAsync, Mr = St.renderPanelsAsync;
function Cr(n, e) {
  const t = URL.createObjectURL(n), s = document.createElement("a");
  s.href = t, s.download = e, s.click(), setTimeout(() => URL.revokeObjectURL(t), 1e3);
}
async function Ir(n, e = 1) {
  if (!n.svg || !Number.isFinite(e) || e < 0.5 || e > 4)
    throw new Error("올바른 만화와 0.5~4 배율이 필요합니다.");
  const t = Math.round(n.width * e), s = Math.round(n.height * e);
  if (t > 16384 || s > 16384 || t * s > 32e6)
    throw new Error("PNG 크기가 너무 큽니다. 배율이나 컷 수를 줄이세요.");
  await document.fonts.ready;
  const i = URL.createObjectURL(
    new Blob([n.svg], { type: "image/svg+xml;charset=utf-8" })
  );
  try {
    const r = new Image();
    r.src = i, await r.decode();
    const o = document.createElement("canvas");
    o.width = t, o.height = s;
    const a = o.getContext("2d");
    if (!a) throw new Error("이 브라우저에서는 PNG를 만들 수 없습니다.");
    return a.drawImage(r, 0, 0, t, s), await new Promise(
      (c, l) => o.toBlob(
        (f) => f ? c(f) : l(new Error("PNG 생성에 실패했습니다.")),
        "image/png"
      )
    );
  } finally {
    URL.revokeObjectURL(i);
  }
}
const Sr = `
.comic-figure { margin:20px 0; }
.comic-figure [role="alert"] { color:#b53b45; white-space:pre-wrap; }
.comic-card { box-sizing:border-box; display:flex; align-items:center; gap:18px; width:100%; max-width:540px; padding:16px; border:1px solid #dbe3ee; border-radius:16px; background:white; color:#233044; text-align:left; font:14px/1.6 system-ui,sans-serif; cursor:pointer; }
.comic-card:hover { background:#f8faff; border-color:#4c64e8; }
.comic-card:focus-visible { outline:3px solid #8096ff; outline-offset:3px; }
.comic-card-thumbnail { display:block; flex:0 0 112px; width:112px; height:96px; overflow:hidden; border-radius:10px; background:#f5f7fb; }
.comic-card-thumbnail svg { display:block; width:100%; height:auto; }
.comic-card-copy { display:grid; gap:6px; min-width:0; overflow-wrap:anywhere; }
.comic-card-copy strong { font-size:17px; }
.comic-card-copy span { color:#526fea; font-size:13px; }
@media(max-width:600px) {
  .comic-card { gap:12px; padding:12px; }
  .comic-card-thumbnail { flex-basis:88px; width:88px; height:80px; }
}
`;
function Nn(n, e = 0) {
  return [...n.querySelectorAll("g[data-panel]")].map((t, s) => {
    if (t.getAttribute("data-panel") !== String(s + e))
      throw new TypeError("만화의 컷 순서가 올바르지 않습니다.");
    const i = t.querySelector("rect");
    if (!i) throw new TypeError("만화에 컷 프레임이 없습니다.");
    let r = new DOMMatrix();
    for (let m = i; m && m !== n.documentElement; m = m.parentElement) {
      let y = new DOMMatrix();
      const h = m.getAttribute("transform") ?? "", g = /(matrix|translate|scale|rotate|skewX|skewY)\(([^)]*)\)/g;
      let w = h;
      for (const S of h.matchAll(g)) {
        const k = S[2].trim().split(/[\s,]+/).map(Number);
        if (!k.length || k.some((x) => !Number.isFinite(x)))
          throw new TypeError("만화의 컷 변환이 올바르지 않습니다.");
        const [p, b = 0, v = 0] = k;
        switch (S[1]) {
          case "matrix":
            if (k.length !== 6)
              throw new TypeError("올바른 컷 행렬이 필요합니다.");
            y = y.multiply(new DOMMatrix(k));
            break;
          case "translate":
            y = y.translate(p, b);
            break;
          case "scale":
            y = y.scale(p, k[1] ?? p);
            break;
          case "rotate":
            y = y.translate(b, v).rotate(p).translate(-b, -v);
            break;
          case "skewX":
            y = y.skewX(p);
            break;
          case "skewY":
            y = y.skewY(p);
            break;
        }
        w = w.replace(S[0], "");
      }
      if (w.trim()) throw new TypeError("지원하지 않는 컷 변환입니다.");
      r = y.multiply(r);
    }
    const o = Number(i.getAttribute("x") ?? 0), a = Number(i.getAttribute("y") ?? 0), c = Number(i.getAttribute("width")), l = Number(i.getAttribute("height"));
    if (![o, a, c, l].every(Number.isFinite) || c <= 0 || l <= 0)
      throw new TypeError("만화의 컷 크기가 올바르지 않습니다.");
    const f = [
      [o, a],
      [o + c, a],
      [o, a + l],
      [o + c, a + l]
    ].map(([m, y]) => r.transformPoint(new DOMPoint(m, y))), u = Math.min(...f.map((m) => m.x)), d = Math.min(...f.map((m) => m.y));
    return {
      x: u,
      y: d,
      width: Math.max(...f.map((m) => m.x)) - u,
      height: Math.max(...f.map((m) => m.y)) - d
    };
  });
}
function vr(n, e, t, s, i, r, o, a) {
  let c = 0, l = !1, f = 0;
  const u = () => {
    const E = n.getBoundingClientRect(), T = getComputedStyle(n);
    return {
      x: E.x + n.clientLeft + (parseFloat(T.paddingLeft) || 0),
      y: E.y + n.clientTop + (parseFloat(T.paddingTop) || 0)
    };
  }, d = () => {
    const E = e.getBoundingClientRect(), T = E.width / s;
    return t.map((_) => ({
      x: E.x + _.x * T,
      y: E.y + _.y * T,
      width: _.width * T,
      height: _.height * T
    }));
  };
  let m = 0;
  const y = () => {
    i.disabled = c === 0, r.disabled = c === t.length - 1, (document.activeElement === i && i.disabled || document.activeElement === r && r.disabled) && n.focus();
    const E = `${c + 1} / ${t.length}컷`;
    o.textContent !== E && (o.textContent = E), m !== c && (m = c, a?.());
  }, h = () => {
    if (l) return;
    if (n.scrollLeft === 0 && n.scrollTop === 0) {
      c = 0, y();
      return;
    }
    const E = u(), T = n.clientWidth - (parseFloat(getComputedStyle(n).paddingLeft) || 0) - (parseFloat(getComputedStyle(n).paddingRight) || 0), _ = n.clientHeight - (parseFloat(getComputedStyle(n).paddingTop) || 0) - (parseFloat(getComputedStyle(n).paddingBottom) || 0);
    let j = -1, M = 1 / 0;
    d().forEach((F, be) => {
      const re = Math.max(
        0,
        Math.min(F.x + F.width, E.x + T) - Math.max(F.x, E.x)
      ) * Math.max(
        0,
        Math.min(F.y + F.height, E.y + _) - Math.max(F.y, E.y)
      ), ce = Math.hypot(
        Math.max(F.x - E.x, 0, E.x - F.x - F.width),
        Math.max(F.y - E.y, 0, E.y - F.y - F.height)
      );
      (re > j || re === j && ce < M) && (j = re, M = ce, c = be);
    }), y();
  }, g = () => {
    cancelAnimationFrame(f), l = !0;
    const E = n.scrollLeft, T = n.scrollTop;
    f = requestAnimationFrame(() => {
      f = requestAnimationFrame(() => {
        l = !1, (n.scrollLeft !== E || n.scrollTop !== T) && h();
      });
    });
  }, w = (E, T = c) => {
    if (c = Math.max(0, Math.min(t.length - 1, T + E)), c === T) {
      y();
      return;
    }
    const _ = d()[c], j = u();
    n.scrollTo({
      left: n.scrollLeft + _.x - j.x,
      top: n.scrollTop + _.y - j.y,
      behavior: "instant"
    }), g(), y();
  }, S = () => w(-1), k = () => w(1), p = (E) => {
    E.target !== n || E.altKey || E.ctrlKey || E.metaKey || E.shiftKey || (E.key === "ArrowLeft" || E.key === "ArrowRight") && (E.preventDefault(), w(E.key === "ArrowLeft" ? -1 : 1));
  }, b = /* @__PURE__ */ new Set();
  let v, x = !1;
  const $ = (E) => {
    if (b.add(E.pointerId), x = !1, b.size !== 1 || !E.isPrimary || E.button !== 0) {
      v = void 0;
      return;
    }
    v = {
      id: E.pointerId,
      x: E.clientX,
      y: E.clientY,
      moved: !1
    };
  }, N = (E) => {
    v?.id === E.pointerId && Math.hypot(E.clientX - v.x, E.clientY - v.y) > 8 && (v.moved = !0);
  }, C = (E) => {
    x = b.size === 1 && v?.id === E.pointerId && !v.moved, b.delete(E.pointerId), v = void 0;
  }, P = (E) => {
    E ? b.delete(E.pointerId) : b.clear(), v = void 0, x = !1;
  }, A = (E) => {
    const T = x;
    if (x = !1, !T || E.detail > 1 || E.ctrlKey || E.metaKey || E.altKey || E.shiftKey || E.target !== e)
      return;
    const _ = d(), j = _.findIndex(
      (M) => E.clientX >= M.x && E.clientX <= M.x + M.width && E.clientY >= M.y && E.clientY <= M.y + M.height
    );
    j >= 0 && (n.focus({ preventScroll: !0 }), w(
      E.clientX < _[j].x + _[j].width / 2 ? -1 : 1,
      j
    ));
  }, D = (E) => {
    n.contains(E.target) || P(E);
  };
  return e.draggable = !1, i.addEventListener("click", S), r.addEventListener("click", k), n.addEventListener("scroll", h), n.addEventListener("keydown", p), n.addEventListener("pointerdown", $), n.addEventListener("pointermove", N), n.addEventListener("pointerup", C), n.addEventListener("pointercancel", P), n.addEventListener("click", A), document.addEventListener("pointerup", D), document.addEventListener("pointercancel", D), y(), {
    get currentIndex() {
      return c;
    },
    goTo: (E) => w(E - c),
    capturePosition: () => {
      const E = u(), T = e.getBoundingClientRect(), _ = T.width / s;
      return { x: (E.x - T.x) / _, y: (E.y - T.y) / _ };
    },
    restorePosition: (E) => {
      const T = n.scrollLeft, _ = n.scrollTop, j = e.getBoundingClientRect(), M = u(), F = j.width / s;
      n.scrollTo({
        left: n.scrollLeft + j.x + E.x * F - M.x,
        top: n.scrollTop + j.y + E.y * F - M.y,
        behavior: "instant"
      }), (n.scrollLeft !== T || n.scrollTop !== _) && g(), y();
    },
    reset: () => {
      cancelAnimationFrame(f), l = !1, c = 0, P(), y();
    },
    dispose: () => {
      cancelAnimationFrame(f), i.removeEventListener("click", S), r.removeEventListener("click", k), n.removeEventListener("scroll", h), n.removeEventListener("keydown", p), n.removeEventListener("pointerdown", $), n.removeEventListener("pointermove", N), n.removeEventListener("pointerup", C), n.removeEventListener("pointercancel", P), n.removeEventListener("click", A), document.removeEventListener("pointerup", D), document.removeEventListener("pointercancel", D), P();
    }
  };
}
const Er = `
.comic-card[data-comic-gen-card] { box-sizing:border-box; display:flex; align-items:center; gap:18px; width:100%; max-width:540px; padding:16px; border:1px solid #dbe3ee; border-radius:16px; background:white; color:#233044; text-align:left; font:14px/1.6 system-ui,sans-serif; cursor:pointer; }
.comic-card[data-comic-gen-card]:hover { background:#f8faff; border-color:#4c64e8; }
.comic-card[data-comic-gen-card]:focus-visible, .comic-viewer[data-comic-gen-viewer] :is(button,input,select,.comic-viewer-viewport):focus-visible { outline:3px solid #8096ff; outline-offset:3px; }
[data-comic-gen-card] .comic-card-thumbnail { display:block; flex:0 0 112px; width:112px; height:96px; overflow:hidden; border-radius:10px; background:#f5f7fb; }
[data-comic-gen-card] .comic-card-thumbnail img { display:block; width:100%; max-width:none; height:auto; margin:0; }
[data-comic-gen-card] .comic-card-copy { display:grid; gap:6px; min-width:0; overflow-wrap:anywhere; }
[data-comic-gen-card] .comic-card-copy strong { font-size:17px; }
[data-comic-gen-card] .comic-card-copy span { color:#526fea; font-size:13px; }
.comic-viewer[data-comic-gen-viewer] { box-sizing:border-box; margin:auto; width:calc(100vw - 48px); max-width:1800px; height:calc(100dvh - 48px); max-height:none; padding:0; border:1px solid #dbe3ee; border-radius:16px; background:#f5f7fb; color:#233044; font:14px/1.6 system-ui,sans-serif; overflow:hidden; }
.comic-viewer[data-comic-gen-viewer][open] { display:flex; flex-direction:column; }
.comic-viewer[data-comic-gen-viewer]::backdrop { background:#162339b3; }
[data-comic-gen-viewer] .comic-viewer-toolbar { flex:none; display:flex; align-items:center; flex-wrap:wrap; gap:12px; padding:16px 20px; background:white; border-bottom:1px solid #dbe3ee; }
[data-comic-gen-viewer] .comic-viewer-title { margin:0 auto 0 0; min-width:0; font-size:18px; color:inherit; letter-spacing:0; overflow-wrap:anywhere; }
[data-comic-gen-viewer] .comic-viewer-controls { display:flex; align-items:center; flex-wrap:wrap; gap:12px; max-width:100%; }
[data-comic-gen-viewer] .comic-viewer-navigation { display:flex; align-items:center; gap:12px; }
[data-comic-gen-viewer] .comic-viewer-controls label { display:flex; align-items:center; gap:8px; margin:0; color:inherit; font-size:13px; white-space:nowrap; }
[data-comic-gen-viewer] .comic-viewer-checkbox input { flex:none; width:16px; height:16px; margin:0; padding:0; accent-color:#526fea; cursor:pointer; }
[data-comic-gen-viewer] :is(button,select) { border:1px solid #dbe3ee; border-radius:8px; background:white; color:#344055; padding:8px 12px; font:inherit; cursor:pointer; }
[data-comic-gen-viewer] button:disabled { opacity:.4; cursor:default; }
[data-comic-gen-viewer] .comic-position { min-width:5rem; text-align:center; font-variant-numeric:tabular-nums; }
[data-comic-gen-viewer] .comic-viewer-help { flex:none; margin:0; padding:8px 20px; font-size:12px; color:#69778b; }
[data-comic-gen-viewer] .comic-viewer-viewport { box-sizing:border-box; flex:1; min-width:0; min-height:0; overflow:auto; overscroll-behavior:contain; padding:16px; }
[data-comic-gen-viewer] .comic-viewer-viewport[data-prevent-overflow="true"] { overflow-x:hidden; overflow-y:auto; }
[data-comic-gen-viewer] .comic-viewer-artwork { margin:0 auto; }
[data-comic-gen-viewer] .comic-viewer-artwork img { display:block; width:100%; max-width:none; height:auto; margin:0; user-select:none; }
@media (max-width:600px) {
  .comic-viewer[data-comic-gen-viewer] { width:100vw; max-width:none; height:100dvh; margin:0; border:0; border-radius:0; }
  [data-comic-gen-viewer] .comic-viewer-toolbar { padding:12px; gap:10px; }
  [data-comic-gen-viewer] .comic-viewer-title { flex-basis:calc(100% - 80px); font-size:16px; }
  [data-comic-gen-viewer] .comic-viewer-controls { width:100%; }
  [data-comic-gen-viewer] .comic-viewer-navigation { flex-basis:100%; justify-content:center; }
  [data-comic-gen-viewer] .comic-viewer-help { padding:8px 12px; }
  [data-comic-gen-viewer] .comic-viewer-viewport { padding:8px; }
  .comic-card[data-comic-gen-card] { gap:12px; padding:12px; }
  [data-comic-gen-card] .comic-card-thumbnail { flex-basis:88px; width:88px; height:80px; }
}
`, On = "http://www.w3.org/2000/svg", An = /^#[\p{L}_][\p{L}\p{N}_:.-]*$/u, Lr = /* @__PURE__ */ new Set([
  "fill",
  "stroke",
  "filter",
  "mask",
  "clip-path",
  "marker-start",
  "marker-mid",
  "marker-end",
  "cursor"
]), xr = /* @__PURE__ */ new Set([
  "svg",
  "g",
  "defs",
  "title",
  "desc",
  "path",
  "rect",
  "circle",
  "ellipse",
  "line",
  "polyline",
  "polygon",
  "text",
  "tspan",
  "textPath",
  "use",
  "symbol",
  "marker",
  "clipPath",
  "mask",
  "pattern",
  "linearGradient",
  "radialGradient",
  "stop",
  "filter",
  "feGaussianBlur",
  "feOffset",
  "feBlend",
  "feColorMatrix",
  "feComposite",
  "feFlood",
  "feMerge",
  "feMergeNode",
  "feDropShadow",
  "feComponentTransfer",
  "feFuncA",
  "feFuncR",
  "feFuncG",
  "feFuncB",
  "feMorphology",
  "feConvolveMatrix",
  "feDisplacementMap",
  "feTurbulence",
  "feDiffuseLighting",
  "feSpecularLighting",
  "feDistantLight",
  "fePointLight",
  "feSpotLight",
  "feTile"
]);
function Tn(n) {
  if (!n || typeof n.svg != "string" || !n.svg || n.svg.length > 64e6 || !Number.isFinite(n.width) || n.width <= 0 || n.width > 1e6 || !Number.isFinite(n.height) || n.height <= 0 || n.height > 1e6 || n.diagnostics !== void 0 && (!Array.isArray(n.diagnostics) || n.diagnostics.length))
    throw new TypeError("완성된 코믹젠 렌더 결과가 필요합니다.");
  if (/<!DOCTYPE|<!ENTITY|<\?/i.test(n.svg))
    throw new TypeError("정적 코믹젠 SVG만 뷰어에 전달하세요.");
  const e = new DOMParser().parseFromString(n.svg, "image/svg+xml"), t = e.documentElement, s = (t.getAttribute("viewBox") ?? `0 0 ${n.width} ${n.height}`).trim().split(/[\s,]+/).map(Number);
  if (t.localName !== "svg" || t.namespaceURI !== On || e.querySelector("parsererror") || s.length !== 4 || s[0] !== 0 || s[1] !== 0 || s[2] !== n.width || s[3] !== n.height || Number(t.getAttribute("width")) !== n.width || Number(t.getAttribute("height")) !== n.height)
    throw new TypeError("만화 SVG와 렌더 결과의 크기가 일치해야 합니다.");
  for (const i of [t, ...t.querySelectorAll("*")]) {
    if (i.namespaceURI !== On || !xr.has(i.localName))
      throw new TypeError("외부 리소스나 실행 가능한 SVG는 지원하지 않습니다.");
    for (const r of i.attributes) {
      const o = r.localName.toLowerCase(), a = r.value;
      if (o.startsWith("on") || o === "base" && r.namespaceURI === "http://www.w3.org/XML/1998/namespace" || o === "href" && !An.test(a))
        throw new TypeError(
          "외부 링크나 이벤트가 포함된 SVG는 지원하지 않습니다."
        );
      if (o === "style" && /@|javascript\s*:|vbscript\s*:|expression\s*\(|[\\<>]/i.test(a))
        throw new TypeError("정적 코믹젠 SVG 스타일만 지원합니다.");
      if (Lr.has(o) && /[\\<>@]/.test(a))
        throw new TypeError("정적 코믹젠 SVG 색상과 참조만 지원합니다.");
      for (const c of a.matchAll(/url\s*\(([^)]*)\)/gi)) {
        const l = c[1].trim().replace(/^(['"])(.*)\1$/, "$2");
        if (!An.test(l))
          throw new TypeError("SVG의 외부 리소스는 지원하지 않습니다.");
      }
    }
  }
  return e;
}
function Os(n) {
  const e = Tn(n);
  if (!Array.isArray(n.panels) || n.panels.length < 1 || n.panels.length > 30)
    throw new TypeError("만화에는 실제 렌더된 1~30개의 컷이 필요합니다.");
  const t = [], s = n.panels.map((a, c) => {
    if (a.index !== c)
      throw new TypeError("만화의 개별 컷 순서가 일치해야 합니다.");
    const l = Nn(Tn(a), c);
    if (l.length !== 1 || ![l[0].x, l[0].y, l[0].width, l[0].height].every(
      Number.isFinite
    ) || l[0].width <= 0 || l[0].height <= 0 || l[0].x < 0 || l[0].y < 0 || l[0].x + l[0].width > a.width + 1 || l[0].y + l[0].height > a.height + 1)
      throw new TypeError("개별 컷 SVG에는 한 개의 컷 프레임이 필요합니다.");
    return t.push(l[0]), { ...a };
  }), i = Nn(e);
  if (i.length !== s.length || i.some(
    (a) => ![a.x, a.y, a.width, a.height].every(Number.isFinite) || a.width <= 0 || a.height <= 0 || a.x < 0 || a.y < 0 || a.x + a.width > n.width + 1 || a.y + a.height > n.height + 1
  ))
    throw new TypeError("만화의 컷 프레임과 렌더 결과가 일치해야 합니다.");
  const r = e.documentElement.getAttribute("aria-label") ?? e.documentElement.querySelector("title")?.textContent ?? "만화", o = s.map((a, c) => {
    const l = i[c], f = t[c], u = Math.max(
      l.width / f.width,
      l.height / f.height
    );
    return { width: a.width * u, height: a.height * u };
  });
  return {
    result: { ...n, panels: s },
    title: r,
    bounds: i,
    panelWidth: Math.max(...o.map((a) => a.width)),
    panelHeight: Math.max(...o.map((a) => a.height))
  };
}
const jt = /* @__PURE__ */ Symbol.for("comic-gen.viewer.document-state.v1");
function ln() {
  const n = document;
  return n[jt] || Object.defineProperty(n, jt, {
    value: { bodyLocks: /* @__PURE__ */ new WeakMap(), nextId: 0 }
  }), n[jt];
}
function As() {
  const n = ln();
  let e = n.styles;
  if (e)
    e.element.isConnected || document.head.append(e.element);
  else {
    const s = document.createElement("style");
    s.dataset.comicGenViewerStyles = "", s.textContent = Er, document.head.append(s), e = { element: s, count: 0 }, n.styles = e;
  }
  e.count++;
  let t = !1;
  return () => {
    t || (t = !0, --e.count === 0 && (e.element.remove(), n.styles = void 0));
  };
}
function Nr() {
  const n = ln().bodyLocks, e = document.body;
  let t = n.get(e);
  t || (t = {
    count: 0,
    value: e.style.getPropertyValue("overflow"),
    priority: e.style.getPropertyPriority("overflow")
  }, n.set(e, t), e.style.setProperty("overflow", "hidden", "important")), t.count++;
  let s = !1;
  return () => {
    s || (s = !0, --t.count === 0 && (t.value ? e.style.setProperty("overflow", t.value, t.priority) : e.style.removeProperty("overflow"), n.delete(e)));
  };
}
function Ts(n, e, t, s) {
  const i = document.createElement("img"), r = URL.createObjectURL(new Blob([n], { type: "image/svg+xml" }));
  Object.assign(i, {
    src: r,
    width: e,
    height: t,
    alt: s,
    decoding: "async",
    draggable: !1
  });
  let o = !1;
  return {
    image: i,
    revoke: () => {
      o || (o = !0, URL.revokeObjectURL(r));
    }
  };
}
function Ms(n = {}) {
  n = { ...n };
  let e = {}, t;
  const s = (L, I) => {
    if (L.zoom !== void 0 && (!Number.isFinite(L.zoom) || L.zoom <= 0 || L.zoom > 10))
      throw new RangeError("zoom must be greater than 0 and at most 10.");
    if (L.panelIndex !== void 0 && (!Number.isInteger(L.panelIndex) || L.panelIndex < 0 || I !== void 0 && L.panelIndex >= I))
      throw new RangeError("panelIndex must identify an existing panel.");
    if (L.preventOverflow !== void 0 && typeof L.preventOverflow != "boolean")
      throw new TypeError("preventOverflow must be a boolean.");
  }, i = (L, I) => {
    s(L, I);
    for (const B of [
      "closeOnBackdrop",
      "closeOnEmptyArea",
      "closeOnEscape",
      "showCloseButton"
    ])
      if (L[B] !== void 0 && typeof L[B] != "boolean")
        throw new TypeError(`${B} must be a boolean.`);
    if (L.onChange !== void 0 && typeof L.onChange != "function")
      throw new TypeError("onChange must be a function.");
  };
  i(n);
  const r = () => f?.open && k ? Object.freeze({
    zoom: Number(y.value),
    preventOverflow: h.checked,
    panelIndex: p?.currentIndex ?? 0
  }) : null;
  let o, a = !1;
  const c = () => {
    if (a) return;
    const L = r(), I = JSON.stringify(L);
    I !== o && (o = I, e.onChange?.(L));
  }, l = (L) => {
    const I = String(L);
    if (![...y.options].some((B) => B.value === I)) {
      const B = document.createElement("option");
      B.value = I, B.textContent = `${Math.round(L * 100)}%`, B.dataset.customZoom = "", y.append(B);
    }
    y.value = I;
  };
  let f, u, d, m, y, h, g, w, S, k, p, b, v, x, $, N, C = !1;
  const P = () => {
    if (!f?.open || !k) return;
    const L = p?.capturePosition();
    u.dataset.preventOverflow = String(h.checked);
    const I = k.result;
    let B = I.width * Number(y.value);
    if (h.checked) {
      const U = getComputedStyle(u), ke = Math.max(
        0,
        u.clientWidth - (parseFloat(U.paddingLeft) || 0) - (parseFloat(U.paddingRight) || 0)
      ), fe = Math.max(
        0,
        u.clientHeight - (parseFloat(U.paddingTop) || 0) - (parseFloat(U.paddingBottom) || 0)
      );
      B = Math.min(
        B,
        ke * I.width / k.panelWidth,
        fe * I.width / k.panelHeight
      );
    }
    d.style.width = `${Math.max(0, B)}px`, L && Number.isFinite(L.x) && Number.isFinite(L.y) && p?.restorePosition(L);
  }, A = () => {
    p?.dispose(), p = void 0, v?.(), v = void 0, d?.replaceChildren(), k = void 0, x?.(), x = void 0;
    const L = o !== void 0 && o !== "null", I = N;
    N = void 0;
    const B = [
      ...document.querySelectorAll("dialog[open]")
    ].find((U) => U !== f);
    I?.isConnected && (!B || B.contains(I)) && I.focus({ preventScroll: !0 }), L && c();
  }, D = () => {
    f?.open && f.close(), A();
  }, E = (L) => {
    L.preventDefault(), e.closeOnEscape !== !1 && D();
  }, T = () => {
    f?.open || A();
  };
  let _ = !1, j;
  const M = (L) => {
    if (L.target !== f) return !1;
    const I = f.getBoundingClientRect();
    return L.clientX < I.left || L.clientX > I.right || L.clientY < I.top || L.clientY > I.bottom;
  }, F = (L) => {
    if (L.target !== u) return !1;
    const I = u.getBoundingClientRect();
    return L.clientX >= I.left + u.clientLeft && L.clientX < I.left + u.clientLeft + u.clientWidth && L.clientY >= I.top + u.clientTop && L.clientY < I.top + u.clientTop + u.clientHeight;
  }, be = (L) => {
    j = L.button === 0 && L.isPrimary && F(L) ? { x: L.clientX, y: L.clientY } : void 0, _ = L.button === 0 && M(L);
  }, re = (L) => {
    const I = _ && M(L) && e.closeOnBackdrop === !0 || !!(j && F(L) && e.closeOnEmptyArea === !0 && Math.hypot(L.clientX - j.x, L.clientY - j.y) <= 8);
    j = void 0, _ = !1, I && D();
  }, ce = () => {
    P(), c();
  }, cn = (L) => {
    if (L.key !== "Tab" || !f?.open) return;
    const B = [
      ...f.querySelectorAll(
        "button:not(:disabled), input, select, [tabindex='0']"
      )
    ].filter((fe) => !fe.hidden), U = B[0], ke = B[B.length - 1];
    (!L.shiftKey && document.activeElement === ke || L.shiftKey && document.activeElement === U) && (L.preventDefault(), (L.shiftKey ? ke : U).focus());
  }, Ds = () => {
    if (f) return;
    $ = As();
    const L = `comic-gen-viewer-${++ln().nextId}`;
    f = document.createElement("dialog"), f.className = "comic-viewer", f.dataset.comicGenViewer = "", f.setAttribute("aria-labelledby", `${L}-title`), f.setAttribute("aria-describedby", `${L}-help`), f.innerHTML = `<div class="comic-viewer-toolbar"><h2 class="comic-viewer-title" id="${L}-title"></h2><button type="button" autofocus>닫기</button><div class="comic-viewer-controls"><label class="comic-viewer-checkbox"><input type="checkbox" checked>화면 넘침 방지</label><label>보기 크기 <select><option value="1">100%</option><option value="1.5">150%</option><option value="2">200%</option></select></label><div class="comic-viewer-navigation"><button type="button" class="comic-previous" aria-label="이전 컷">←</button><span class="comic-position" role="status" aria-live="polite"></span><button type="button" class="comic-next" aria-label="다음 컷">→</button></div></div></div><p class="comic-viewer-help" id="${L}-help">화면 넘침 방지는 한 컷의 너비·높이를 화면에 맞춥니다. 다음 컷은 아래로 스크롤해 읽습니다. 컷 왼쪽은 이전, 오른쪽은 다음 컷입니다. 읽기 영역에서 ←/→ 키로도 이동합니다.</p><div class="comic-viewer-viewport" tabindex="0" role="region" aria-label="만화 읽기 영역"><div class="comic-viewer-artwork"></div></div>`, m = f.querySelector("h2"), u = f.querySelector(".comic-viewer-viewport"), d = f.querySelector(".comic-viewer-artwork"), y = f.querySelector("select"), h = f.querySelector('input[type="checkbox"]'), g = f.querySelector(".comic-previous"), w = f.querySelector(".comic-next"), S = f.querySelector(".comic-position"), t = f.querySelector("button"), y.addEventListener("change", ce), h.addEventListener("change", ce), f.querySelector("button").addEventListener("click", D), f.addEventListener("pointerdown", be), f.addEventListener("click", re), f.addEventListener("cancel", E), f.addEventListener("close", T), f.addEventListener("keydown", cn), document.body.append(f), b = new ResizeObserver(P), b.observe(u);
  };
  return {
    get isOpen() {
      return !!f?.open;
    },
    get state() {
      return r();
    },
    setView: (L) => {
      if (!f?.open || !k)
        throw new Error("Open the viewer before setting its view.");
      s(L, k.result.panels.length), a = !0, L.zoom !== void 0 && l(L.zoom), L.preventOverflow !== void 0 && (h.checked = L.preventOverflow), P(), L.panelIndex !== void 0 && p?.goTo(L.panelIndex), a = !1, c();
    },
    open: (L, I = {}) => {
      if (C) throw new Error("폐기한 만화 뷰어는 다시 열 수 없습니다.");
      const B = Os(L), U = { ...n, ...I };
      i(U, B.result.panels.length);
      const ke = U.trigger ?? (f?.open ? N : document.activeElement instanceof HTMLElement ? document.activeElement : void 0);
      Ds(), p?.dispose(), v?.(), a = !0, e = U, o = void 0, _ = !1, j = void 0, k = B, N = ke, m.textContent = B.title, y.querySelectorAll("[data-custom-zoom]").forEach((vt) => vt.remove()), l(U.zoom ?? 1), h.checked = U.preventOverflow ?? !0, t.hidden = U.showCloseButton === !1;
      const fe = Ts(
        B.result.svg,
        B.result.width,
        B.result.height,
        B.title
      );
      if (v = fe.revoke, d.replaceChildren(fe.image), p = vr(
        u,
        fe.image,
        B.bounds,
        B.result.width,
        g,
        w,
        S,
        c
      ), !f.open) {
        x = Nr();
        try {
          f.showModal();
        } catch (vt) {
          throw a = !1, A(), vt;
        }
      }
      P(), u.scrollTo(0, 0), p.reset(), p.goTo(U.panelIndex ?? 0), (t.hidden ? u : t).focus({
        preventScroll: !0
      }), a = !1, c();
    },
    close: D,
    destroy: () => {
      C || (C = !0, D(), b?.disconnect(), f && (y.removeEventListener("change", ce), h.removeEventListener("change", ce), f.querySelector("button").removeEventListener("click", D), f.removeEventListener("pointerdown", be), f.removeEventListener("click", re), f.removeEventListener("cancel", E), f.removeEventListener("close", T), f.removeEventListener("keydown", cn), f.remove()), $?.(), $ = void 0);
    }
  };
}
function jr(n, e, t = {}) {
  const s = Os(e), i = As(), r = Ms(t), o = document.createElement("button");
  o.type = "button", o.className = "comic-card", o.dataset.comicGenCard = "", o.setAttribute("aria-haspopup", "dialog"), o.setAttribute("aria-label", `${s.title} · 만화 읽기`);
  const a = document.createElement("span");
  a.className = "comic-card-thumbnail", a.setAttribute("aria-hidden", "true");
  const c = s.result.panels[0], l = Ts(
    c.svg,
    c.width,
    c.height,
    `${s.title} · 1/${s.result.panels.length}`
  );
  a.append(l.image);
  const f = document.createElement("span");
  f.className = "comic-card-copy";
  const u = document.createElement("strong");
  u.textContent = s.title;
  const d = document.createElement("span");
  d.textContent = `${s.result.panels.length}컷 · 만화 읽기 ↗`, f.append(u, d), o.append(a, f);
  const m = () => r.open(s.result, { trigger: o });
  o.addEventListener("click", m), n.replaceChildren(o);
  let y = !1;
  return () => {
    y || (y = !0, o.removeEventListener("click", m), r.destroy(), l.revoke(), o.remove(), i());
  };
}
const Mn = /* @__PURE__ */ new WeakMap(), Cs = Ns(), Vt = /* @__PURE__ */ new WeakMap(), Qe = Ms();
let Ge;
function Is(n) {
  n.result?.svg && (Ge = n, Qe.open(n.result, { trigger: n.button }));
}
function js(n) {
  if (!document.getElementById("comic-gen-embed-styles")) {
    const s = document.createElement("style");
    s.id = "comic-gen-embed-styles", s.textContent = Sr, document.head.append(s);
  }
  const e = 'pre[language="comic-gen"], pre[data-comic], pre:has(code.language-comic), pre:has(code.language-comic-gen)', t = [...n.querySelectorAll(e)];
  return n instanceof HTMLElement && n.matches(e) && t.unshift(n), t;
}
function Ut(n) {
  return (n.querySelector("code") ?? n).textContent ?? "";
}
function Bs(n) {
  let e = Mn.get(n);
  if (!e) {
    const t = document.createElement("figure");
    t.className = "comic-figure";
    const s = document.createElement("button");
    s.type = "button", s.className = "comic-card", s.setAttribute("aria-haspopup", "dialog");
    const i = document.createElement("span");
    i.className = "comic-card-thumbnail", i.setAttribute("aria-hidden", "true");
    const r = document.createElement("span");
    r.className = "comic-card-copy";
    const o = document.createElement("strong"), a = document.createElement("span");
    r.append(o, a), s.append(i, r), e = { figure: t, button: s, thumbnail: i, title: o, caption: a };
    const c = e;
    s.addEventListener("click", () => Is(c)), Mn.set(n, e);
  }
  return n.after(e.figure), n.hidden = !0, e;
}
function _s(n, e) {
  if (n.result = e, n.figure.removeAttribute("aria-busy"), n.button.disabled = !1, e.svg) {
    const t = new DOMParser().parseFromString(e.svg, "image/svg+xml");
    n.title.textContent = t.documentElement.getAttribute("aria-label"), n.caption.textContent = `${e.panels.length}컷 · 만화 읽기 ↗`, n.button.setAttribute(
      "aria-label",
      `${n.title.textContent} · 만화 읽기`
    ), n.thumbnail.innerHTML = e.panels[0].svg, n.figure.replaceChildren(n.button), Ge === n && Qe.isOpen && Is(n);
  } else {
    Ge === n && Qe.close();
    const t = document.createElement("p");
    t.setAttribute("role", "alert"), t.textContent = e.diagnostics.join(`
`), n.figure.replaceChildren(t);
  }
}
function Ps(n) {
  const e = (Vt.get(n) ?? 0) + 1;
  return Vt.set(n, e), e;
}
function Br(n = document, e = {}) {
  return js(n).map((t) => {
    Ps(t);
    const s = Cs.render(Ut(t), e);
    return _s(Bs(t), s), s;
  });
}
async function _r(n = document, e = {}) {
  return Promise.all(
    js(n).map(async (t) => {
      const s = Ut(t), i = Ps(t), r = t.isConnected, o = Bs(t);
      if (o.figure.setAttribute("aria-busy", "true"), o.button.disabled = !0, !o.result) {
        const c = document.createElement("p");
        c.setAttribute("role", "status"), c.textContent = "만화를 그리는 중…", o.figure.replaceChildren(c);
      }
      const a = await Cs.renderAsync(s, e);
      if (Vt.get(t) !== i) return a;
      if (r && !t.isConnected)
        return o.figure.remove(), Ge === o && Qe.close(), a;
      if (Ut(t) !== s) {
        o.figure.removeAttribute("aria-busy"), o.result = void 0, Ge === o && Qe.close();
        const c = document.createElement("p");
        return c.setAttribute("role", "status"), c.textContent = "코드가 바뀌었어요. 다시 그리기를 호출하세요.", o.figure.replaceChildren(c), a;
      }
      return _s(o, a), a;
    })
  );
}
export {
  Fs as assetVersion,
  Ms as createComicViewer,
  Ns as createRenderer,
  Cr as downloadBlob,
  Ir as exportPng,
  jr as mountComicCard,
  Br as renderCodeBlocks,
  _r as renderCodeBlocksAsync,
  Or as renderComic,
  Tr as renderComicAsync,
  Ar as renderPanels,
  Mr as renderPanelsAsync,
  Ns as 렌더러만들기,
  Or as 만화그리기,
  Tr as 만화그리기비동기,
  Ms as 만화뷰어만들기,
  jr as 만화카드붙이기,
  qt as 문법값,
  Y as 문법항목,
  Ar as 컷그리기,
  Mr as 컷그리기비동기,
  Br as 코드블록그리기,
  _r as 코드블록그리기비동기
};
