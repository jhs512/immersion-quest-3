// Run the learner's page in a separate browser process, outside the player origin.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { prepareBrowser, launchBrowser } = require('./web-browser.cjs');
const request = JSON.parse(fs.readFileSync('request.json', 'utf8'));
(async () => {
  const modules=path.dirname(process.env.MQ3_PLAYWRIGHT);
  let html=fs.readFileSync('index.html','utf8');
  if (request.entry.endsWith('.jsx')) {
    const esbuild=require(path.join(modules,'esbuild'));
    const result=esbuild.buildSync({entryPoints:[request.entry],bundle:true,write:false,jsx:'automatic',format:'iife',minify:true,nodePaths:[modules],define:{'process.env.NODE_ENV':'"production"'}});
    const script=result.outputFiles[0].text;
    fs.writeFileSync('app.js',script);
    html=html.replace(/<script src="app.js"><\/script>/,()=>`<script>${script.replaceAll('</script','<\\/script')}</script>`);
  }
  if (html.includes('<!-- tailwind -->')) {
    const tailwind=fs.readFileSync(path.join(modules,'@tailwindcss/browser/dist/index.global.js'),'utf8');
    html=html.replace('<!-- tailwind -->',()=>`<script>${tailwind.replaceAll('</script','<\\/script')}</script>`);
  }
  fs.writeFileSync('preview.html',html);
  const options=fs.existsSync('.mq3-browser.json')?JSON.parse(fs.readFileSync('.mq3-browser.json','utf8')):await prepareBrowser();
  const browser = await launchBrowser(options);
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(5000);
    page.setDefaultNavigationTimeout(10000);
    const errors=[];
    page.on('pageerror', error=>errors.push(error.message));
    await page.goto('file:///' + path.resolve('preview.html').replaceAll('\\','/'));
    for (const [index, check] of request.checks.entries()) {
      const target=page.locator(check.selector || 'body');
      switch (check.kind) {
        case 'text': {
          // Keep patterns in Node; serializing quoted regexes into locator selectors is fragile.
          await target.waitFor();
          const matcher=new RegExp(check.pattern,'s'),deadline=Date.now()+5000;
          let actual;
          do {
            actual=await target.innerText();
            if(matcher.test(actual))break;
            await new Promise(resolve=>setTimeout(resolve,25));
          } while(Date.now()<deadline);
          assert.match(actual,matcher);
          break;
        }
        case 'count': assert.equal(await target.count(), check.value); break;
        case 'fill': await target.fill(check.value); break;
        case 'click': await target.click(); break;
        case 'press': await target.press(check.key); break;
        case 'css': await page.waitForFunction(c=>{const n=document.querySelector(c.selector);return n && getComputedStyle(n)[c.property]===c.value},check); break;
        case 'attribute': assert.equal(await target.getAttribute(check.name),check.value); break;
        case 'reload': await page.reload(); break;
        case 'viewport': await page.setViewportSize({width:check.width,height:check.height}); break;
        case 'focused': assert.equal(await target.evaluate(node=>node===document.activeElement),true); break;
        default: throw new Error('Unknown browser check: ' + check.kind);
      }
      console.log(`브라우저 검사 ${index+1} 통과`);
    }
    assert.deepEqual(errors,[], '브라우저 실행 오류');
    if (!request.checks.length) console.log((await page.locator('body').innerText()).slice(0,12000));
  } finally { await browser.close(); }
})().catch(error=>{console.error(error.message);process.exitCode=1;});
