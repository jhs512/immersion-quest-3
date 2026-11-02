const { spawn } = require('node:child_process');
const c = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000); require("fs").writeFileSync("child.pid", String(process.pid))'], { stdio: 'ignore' });
console.log('spawned');
while (true) {}
