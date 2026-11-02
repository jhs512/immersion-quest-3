const { fork } = require('node:child_process');
if (process.argv[2] === 'child') { console.log('child'); process.exit(0); }
const c = fork(__filename, ['child']);
c.on('exit', (code) => console.log('done', code));
