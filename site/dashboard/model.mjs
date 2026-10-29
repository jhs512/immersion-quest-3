// Read the same append-only records as the player. Never trust identity in a body alone.
export function markers(body, name) {
  return [...String(body ?? '').matchAll(new RegExp(`<!-- mq3-${name}:([\\s\\S]*?) -->`, 'g'))].flatMap(match => {
    try { const value=JSON.parse(match[1]); return value && typeof value==='object' && !Array.isArray(value) ? [value] : []; } catch { return []; }
  });
}
export function repository(value) {
  const repo = String(value).trim().replace(/^https:\/\/github\.com\//, '').replace(/\/$/, '');
  if (!/^[\w.-]+\/[\w.-]+$/.test(repo) || repo.split('/').some(p => p === '.' || p === '..')) throw new Error('코스 저장소를 owner/repo 형태로 입력하세요.');
  return repo;
}
export function repositoryFromUrl(value) {
  const url = new URL(value);
  const match = url.pathname.match(/\/dashboard\/(.+?)\/?$/);
  if (match) return repository(decodeURIComponent(match[1]));
  const legacy = url.searchParams.get('repo');
  return legacy ? repository(legacy) : null;
}
export function dashboardPath(repo, pathname) {
  const start = pathname.indexOf('/dashboard');
  const prefix = start < 0 ? '' : pathname.slice(0, start);
  return `${prefix}/dashboard/${repository(repo)}/`;
}
export function progressKey(issue, course) {
  if (issue.pull_request) return null;
  return markers(issue.body, 'progress').find(key => key.user_id === issue.user?.id && key.course_id === course.id && course.lessons.some(l => l.id === key.lesson_id)) ?? null;
}
export function verifiedEvents(comments, key) {
  const seen = new Set();
  return comments.filter(c => c.user?.id === key.user_id).flatMap(c => markers(c.body, 'event')).filter(e => {
    if (e.key?.user_id !== key.user_id || e.key?.course_id !== key.course_id || e.key?.lesson_id !== key.lesson_id || typeof e.id !== 'string' || !Number.isFinite(e.at) || seen.has(e.id)) return false;
    seen.add(e.id); return true;
  }).sort((a,b) => a.at - b.at || a.id.localeCompare(b.id));
}
// A lesson reset (kind "reset") voids that lesson's earlier events and the ones it lists in `voids`.
// The original comments stay; the player and this page simply stop counting them.
export function effective(events) {
  const resets = events.filter(e => e.kind === 'reset');
  if (!resets.length) return events;
  return events.filter(e => e.kind !== 'reset' && !resets.some(r => r.key?.lesson_id === e.key?.lesson_id
    && (e.at < r.at || (Array.isArray(r.voids) && r.voids.includes(e.id)))));
}
export function enrollments(issues,course){
  const names=new Map();
  for(const issue of [...issues].sort((a,b)=>a.number-b.number)){
    if(issue.pull_request)continue;
    const p=markers(issue.body,'enrollment').find(p=>p.user_id===issue.user?.id&&p.course_id===course.id&&typeof p.name==='string'&&p.name.length>0&&p.name.length<=160&&!/[\s<>\x00-\x1f]/u.test(p.name));
    if(p&&!names.has(p.user_id))names.set(p.user_id,{name:p.name,login:issue.user.login,url:issue.html_url});
  }
  return names;
}
export function summarize(course, lessons, records, registrations=[]) {
  const students = new Map();
  const names=enrollments(registrations,course);
  for(const [id,p] of names)students.set(id,{id,login:p.login,name:p.name,events:new Map(),issues:[p.url]});
  for (const {issue, events} of records) {
    const key = progressKey(issue, course);
    if (!key) continue;
    if (!students.has(key.user_id)) students.set(key.user_id, {id:key.user_id, login:issue.user.login, name:issue.user.login, events:new Map(), issues:[]});
    const student = students.get(key.user_id);
    for (const e of events) if (e.key?.user_id === key.user_id && e.key?.course_id === course.id && e.key?.lesson_id === key.lesson_id) student.events.set(e.id, e);
    student.issues.push(issue.html_url);
  }
  return [...students.values()].map(student => {
    const all = [...student.events.values()].sort((a,b) => a.at-b.at || a.id.localeCompare(b.id));
    let total=0, solved=0, unavailable=0;
    const details = course.lessons.map(ref => {
      const lesson = lessons.get(ref.id);
      if (!lesson) { unavailable++; return {title:ref.title, unavailable:true}; }
      const required = (lesson.tasks ?? []).filter(t => t.required);
      const events = effective(all.filter(e => e.key.lesson_id === ref.id));
      const passed = new Set(events.filter(e => e.kind === 'attempt' && e.passed === true && (e.revision === ref.revision || /^stp_[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/.test(e.task_id))).map(e => e.task_id));
      const count = required.filter(t => passed.has(t.id)).length;
      total += required.length; solved += count;
      const tasks = (lesson.tasks ?? []).map(task => {
        const history = events.filter(e => e.task_id === task.id
          && (e.revision === ref.revision || /^stp_[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/.test(task.id)));
        const finished = history.find(e => e.kind === 'attempt' && e.passed === true)?.at;
        // Reopening a legacy completed problem must not invent a start after its
        // first completion. Its original, uncollected start remains unknown.
        const started = history.find(e => e.kind === 'started' && (finished === undefined || e.at <= finished))?.at;
        const attempts = history.filter(e => e.kind === 'attempt').length;
        return {id:task.id, title:task.title, required:task.required, started, finished, attempts,
          status:finished !== undefined ? '완료' : history.length ? '학습 중' : '시작 전'};
      });
      // The course's designated final challenge, passed in real grading, also clears the lesson.
      const challenge = typeof ref.challenge_task === 'string' && required.some(t => t.id === ref.challenge_task) && passed.has(ref.challenge_task);
      return {title:ref.title, tasks, solved:count, total:required.length, complete:required.length>0 && count===required.length, challenge};
    });
    const counted = course.lessons.flatMap(ref => effective(all.filter(e => e.key.lesson_id === ref.id))).sort((a,b) => a.at-b.at || a.id.localeCompare(b.id));
    const last = [...counted].reverse().find(e => e.kind==='attempt' && e.passed === true && course.lessons.some(l => l.id===e.key.lesson_id));
    const ref = course.lessons.find(l => l.id === last?.key.lesson_id);
    const task = lessons.get(ref?.id)?.tasks?.find(t => t.id===last.task_id);
    return {...student, details, total, solved, unavailable, percent:unavailable || !total ? null : Math.floor(100*solved/total), latest:all.at(-1)?.at, last: last ? `${ref.title} · ${task?.title ?? last.task_id}` : '아직 통과 기록이 없어요'};
  }).sort((a,b) => (b.latest ?? 0)-(a.latest ?? 0));
}
