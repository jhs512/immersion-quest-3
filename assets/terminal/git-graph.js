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
    const refs = snapshot.references.filter(ref => ref.id === commit.id).map(ref => ref.remote ? `원격 기록: ${ref.name}` : ref.name);
    const current = snapshot.head === commit.id;
    const names = [current ? 'HEAD' : '', ...refs].filter(Boolean).join(' · ');
    return {data: {id: commit.id, label: `${names ? names + '\n' : ''}${commit.id.slice(0,7)} ${commit.subject.slice(0,60)}`,
      detail: `${commit.id.slice(0,7)} · ${commit.subject}${names ? ' · ' + names : ''}`},
      position: {x: 24 + lane * 70, y: 24 + row * 64}, classes: current ? 'current' : ''};
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
      this.dispose(owner);
      const canvas = root.querySelector('.git-graph-canvas');
      const cy = cytoscape({container: canvas, elements: [], layout: {name: 'preset'}, minZoom: 0.15, maxZoom: 2,
        wheelSensitivity: 0.2, boxSelectionEnabled: false,
        style: [
          {selector: 'node', style: {'background-color': '#82b9ee', width: 15, height: 15, label: 'data(label)',
            color: '#dce9f5', 'font-size': 12, 'font-family': 'sans-serif', 'text-valign': 'center',
            'text-halign': 'right', 'text-margin-x': 10, 'text-wrap': 'wrap', 'text-max-width': 190}},
          {selector: 'node.current', style: {'background-color': '#66d7ab', 'border-width': 3, 'border-color': '#d2ffef'}},
          {selector: 'node:selected', style: {'border-width': 3, 'border-color': '#ffd98e'}},
          {selector: 'edge', style: {width: 2, 'line-color': '#6586a8', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'target-arrow-color': '#6586a8'}}
        ]});
      view = {root, cy, snapshot: null}; views.set(owner, view);
      cy.on('tap', 'node', event => { root.querySelector('.git-graph-detail').textContent = event.target.data('detail'); });
      const fit = () => { cy.resize(); if (cy.nodes().length && canvas.clientWidth && canvas.clientHeight) cy.fit(undefined, 18); };
      view.observer = new ResizeObserver(fit); view.observer.observe(canvas);
      view.toggle = () => requestAnimationFrame(fit); root.addEventListener('toggle', view.toggle, true);
    }
    view.snapshot = snapshot;
    const status = root.querySelector('.git-graph-status');
    const detail = root.querySelector('.git-graph-detail');
    status.textContent = error || (!snapshot.initialized ? 'git init으로 저장소를 만들면 보여요.' :
      !snapshot.head ? '아직 첫 커밋이 없어요.' : `${snapshot.branch || '브랜치 밖의 HEAD'} · ${snapshot.merging ? '병합 진행 중' : snapshot.changes.length ? '커밋하지 않은 변경이 있어요' : '작업 폴더가 깨끗해요'}${snapshot.truncated ? ' · 최근 200개 표시' : ''}`);
    detail.textContent = snapshot.references.some(ref => ref.remote) ? '원격 기록은 마지막 fetch·push 때 확인한 상태예요. PR 상태를 직접 조회한 것은 아니에요.' : '점을 누르면 커밋 설명을 볼 수 있어요.';
    view.cy.batch(() => { view.cy.elements().remove(); if (!error) view.cy.add(elements(snapshot)); });
    view.cy.resize(); if (view.cy.nodes().length) view.cy.fit(undefined, 18);
    root.dataset.graphReady = 'true';
    root.dataset.graphCount = String(view.cy.nodes().length);
  },
  snapshot(owner) { return views.get(owner)?.snapshot; },
  dispose(owner) {
    const view = views.get(owner); if (!view) return;
    view.observer.disconnect(); view.root.removeEventListener('toggle', view.toggle, true); view.cy.destroy(); views.delete(owner);
  }
};
