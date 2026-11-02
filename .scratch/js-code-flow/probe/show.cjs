const d = require(process.argv[2]);
console.log('status', d.status, 'exit', d.exitCode, 'steps', d.trace.length, 'ms', d.timing?.runMs, 'notes', d.notes, 'problems', JSON.stringify(d.problems), d.message || '');
console.log('stdout', JSON.stringify(d.stdout), 'stderr', JSON.stringify(d.stderr.slice(0, 300)));
const max = Number(process.argv[3] || 60);
for (const s of d.trace.slice(0, max)) {
  console.log(`${s.event} L${s.line} [${s.stack_to_render.map(f => f.func_name + '#' + f.frame_id).join(' > ')}] ` +
    s.stack_to_render.map(f => f.ordered_varnames.map(n => n + '=' + JSON.stringify(f.encoded_locals[n])).join(' ')).join(' | ') +
    (s.exception_msg ? ' EXC ' + s.exception_msg : '') + ' HEAP ' + JSON.stringify(s.heap) + ' OUT ' + JSON.stringify(s.stdout));
}
