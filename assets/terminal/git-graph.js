import cytoscape from 'cytoscape';

// Each teacher/student terminal owns a separate graph and lifecycle.
const views = new Map();
function elements(snapshot) {
  const lanes = new Map(); let nextLane = 0;
  const ids = new Set(snapshot.commits.map(commit => commit.id));
  const nodes = snapshot.commits.map((commit, row) => {
    if (!lanes.has(commit.id)) lanes.set(commit.id, nextLane++);
    const lane = lanes.get(commit.id);
    commit.parents.forEach((parent, index) => {
      if (!lanes.has(parent)) lanes.set(parent, index === 0 ? lane : nextLane++);
    });
    const current = snapshot.head === commit.id;
    const refs = snapshot.references.filter(ref => ref.id === commit.id && !(current && !ref.remote && ref.name === snapshot.branch)).map(ref => ref.remote ? `원격 기록: ${ref.name}` : ref.name);
    const names = [current ? (snapshot.branch ? `HEAD → ${snapshot.branch}` : 'HEAD · 브랜치 밖') : '', refs.length ? `브랜치: ${refs.join(' · ')}` : ''].filter(Boolean).join('\n');
    return {data: {id: commit.id, label: `${names ? names + '\n' : ''}${commit.id.slice(0,7)} ${commit.subject.slice(0,60)}`,
      detail: `${commit.id.slice(0,7)} · ${commit.subject}${names ? ' · ' + names : ''}`},
      position: {x: 24 + lane * 100, y: 24 + row * 96}, classes: current ? 'current' : ''};
  });
  const edges = snapshot.commits.flatMap(commit => commit.parents.filter(parent => ids.has(parent)).map(parent => ({
    data: {id: `${commit.id}:${parent}`, source: commit.id, target: parent}
  })));
  return [...nodes, ...edges];
}
function panel(owner) {
  return [...document.querySelectorAll('[data-git-graph-owner]')].find(node => node.dataset.gitGraphOwner === owner);
}
export const gitGraphs = {
  update(owner, snapshot, error = '') {
    const root = panel(owner); if (!root) return;
    let view = views.get(owner);
    if (!view || view.root !== root) {
      // A keyed component may reuse its DOM. Retire the previous canvas owner
      // before Cytoscape replaces the renderer registered on that container.
      for (const [prior, candidate] of views) if (candidate.root === root) this.dispose(prior);
      this.dispose(owner);
      const canvas = root.querySelector('.git-graph-canvas');
      const cy = cytoscape({container: canvas, elements: [], layout: {name: 'preset'}, minZoom: 0.8, maxZoom: 2,
        wheelSensitivity: 0.2, boxSelectionEnabled: false,
        style: [
          {selector: 'node', style: {'background-color': '#82b9ee', width: 15, height: 15, label: 'data(label)',
            color: '#dce9f5', 'font-size': 14, 'font-family': 'sans-serif', 'text-valign': 'center',
            'text-halign': 'right', 'text-margin-x': 10, 'text-wrap': 'wrap', 'text-max-width': 190}},
          {selector: 'node.current', style: {'background-color': '#66d7ab', 'border-width': 3, 'border-color': '#d2ffef'}},
          {selector: 'node:selected', style: {'border-width': 3, 'border-color': '#ffd98e'}},
          {selector: 'edge', style: {width: 2, 'line-color': '#6586a8', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'target-arrow-color': '#6586a8'}}
        ]});
      view = {root, cy, snapshot: null}; views.set(owner, view);
      cy.on('tap', 'node', event => { root.querySelector('.git-graph-detail').textContent = event.target.data('detail'); });
      view.focus = (announce = false) => {
        cy.resize(); cy.zoom(1);
        const node = cy.getElementById(view.snapshot?.head || '');
        const position = node.length ? node.position() : {x:24,y:24};
        cy.pan({x:Math.max(30,canvas.clientWidth/2-80)-position.x,y:canvas.clientHeight/2-position.y});
        if (announce && node.length) {
          cy.nodes().unselect();node.select();
          root.querySelector('.git-graph-detail').textContent = `현재 위치: ${view.snapshot.branch ? `HEAD → ${view.snapshot.branch}` : '브랜치 밖의 HEAD'} · ${node.id().slice(0,7)}`;
        }
      };
      view.observer = new ResizeObserver(() => cy.resize()); view.observer.observe(canvas);
      view.toggle = () => {if (!root.open) expand(false);requestAnimationFrame(() => cy.resize());}; root.addEventListener('toggle', view.toggle, true);
      const expand = expanded => {
        root.classList.toggle('is-expanded', expanded);
        const button = root.querySelector('[data-graph-action="expand"]');
        if (button) {button.textContent = expanded ? '작게 보기' : '크게 보기';button.setAttribute('aria-pressed',String(expanded));}
        requestAnimationFrame(() => cy.resize());
      };
      view.click = event => {
        const action = event.target.closest('[data-graph-action]')?.dataset.graphAction;
        if (action === 'expand') expand(!root.classList.contains('is-expanded'));
        if (action === 'focus') view.focus(true);
      };
      view.key = event => {if(event.key === 'Escape' && root.classList.contains('is-expanded')) {event.preventDefault();event.stopImmediatePropagation();expand(false);root.querySelector('[data-graph-action="expand"]')?.focus();}};
      root.addEventListener('click',view.click);window.addEventListener('keydown',view.key,true);
    }
    const moved = !view.snapshot || view.snapshot.head !== snapshot.head || view.snapshot.branch !== snapshot.branch;
    view.snapshot = snapshot;
    const status = root.querySelector('.git-graph-status');
    const detail = root.querySelector('.git-graph-detail');
    status.textContent = error || (!snapshot.initialized ? 'git init으로 저장소를 만들면 보여요.' :
      !snapshot.head ? '아직 첫 커밋이 없어요.' : `${snapshot.branch ? `현재 브랜치: ${snapshot.branch}` : '현재 위치: 브랜치 밖의 HEAD'} · ${snapshot.merging ? '병합 진행 중' : snapshot.changes.length ? '커밋하지 않은 변경이 있어요' : '작업 폴더가 깨끗해요'}${snapshot.truncated ? ' · 최근 200개 표시' : ''}`);
    const focusButton = root.querySelector('[data-graph-action="focus"]');
    if (focusButton) focusButton.disabled = !snapshot.head || !!error;
    detail.textContent = snapshot.references.some(ref => ref.remote) ? '원격 기록은 마지막 fetch·push 때 확인한 상태예요. PR 상태를 직접 조회한 것은 아니에요.' : '점을 누르면 커밋 설명을 볼 수 있어요.';
    view.cy.batch(() => { view.cy.elements().remove(); if (!error) view.cy.add(elements(snapshot)); });
    view.cy.resize(); if (moved) view.focus();
    root.dataset.graphReady = 'true';
    root.dataset.graphCount = String(view.cy.nodes().length);
  },
  snapshot(owner) { return views.get(owner)?.snapshot; },
  reset(owner) {
    const root = panel(owner); this.dispose(owner);
    if (!root) return;
    // Pending snapshots from the retired process cannot match this panel again.
    root.dataset.gitGraphOwner = '';
    root.dataset.graphCount = '0';root.dataset.graphReady = 'false';
    root.classList.remove('is-expanded');
    root.querySelector('.git-graph-status').textContent = '실습을 초기화하고 있어요…';
    root.querySelector('.git-graph-detail').textContent = '';
  },
  dispose(owner) {
    const view = views.get(owner); if (!view) return;
    view.observer.disconnect(); view.root.removeEventListener('toggle', view.toggle, true);
    view.root.removeEventListener('click',view.click);window.removeEventListener('keydown',view.key,true);
    view.cy.destroy(); views.delete(owner);
  }
};
