// Reuse an installed browser, or prepare Playwright's private headless browser.
// Installing Chromium here never replaces the user's Chrome or Edge installation.
const path=require('node:path');
const {execFile}=require('node:child_process');
const {promisify}=require('node:util');
const runFile=promisify(execFile);
function runtime(){
 const location=process.env.MQ3_PLAYWRIGHT;
 if(!location)throw Error('수업 브라우저 도구의 경로를 확인하세요.');
 return {location,chromium:require(location).chromium};
}
async function launchBrowser(options){
 return runtime().chromium.launch({...options,headless:true,timeout:10000});
}
async function prepareBrowser(){
 const override=process.env.MQ3_WEB_BROWSER_CHANNEL;
 if(override&&!['chromium','chrome','msedge'].includes(override))throw Error('수업 브라우저 설정을 확인하세요.');
 const channels=override?[override==='chromium'?null:override]:process.platform==='win32'?['msedge','chrome',null]:['chrome',null];
 for(const channel of channels){
  const options=channel?{channel,headless:true}:{headless:true};
  try{const browser=await launchBrowser(options);await browser.close();return options;}catch{}
 }
 if(override&&override!=='chromium')throw Error('선택한 수업 브라우저를 실행하지 못했어요.');
 const {location}=runtime();
 // The bounded preparation phase runs before the shorter learner-code timeout.
 await runFile(process.execPath,[path.join(location,'cli.js'),'install','chromium','--only-shell'],{timeout:180000,maxBuffer:65536,windowsHide:true});
 const options={headless:true};const browser=await launchBrowser(options);await browser.close();return options;
}
module.exports={prepareBrowser,launchBrowser};
if(require.main===module){
 prepareBrowser().then(options=>process.stdout.write(JSON.stringify(options))).catch(error=>{console.error(`수업 브라우저를 준비하지 못했어요. ${error.message}`);process.exitCode=1;});
}
