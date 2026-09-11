import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
import {mkdirSync} from 'node:fs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const shots=process.env.CHEM_SCREENSHOTS||resolve(root,'evidence/screenshots');mkdirSync(shots,{recursive:true});
const server=spawn(process.env.PYTHON||'python',['server.py','--port','8001'],{cwd:root,env:{...process.env,OPENAI_API_KEY:'',OPENAI_MODEL:''}});
await new Promise((resolve,reject)=>{server.stdout.once('data',resolve);server.once('error',reject);server.once('exit',code=>reject(Error('Server exited '+code)))});
try {
const {chromium}=await import('playwright');
const browser=await chromium.launch({headless:true,...(process.env.CHEM_CHROMIUM_EXECUTABLE?{executablePath:process.env.CHEM_CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHEM_CHROMIUM_ARGS||'[]')}: {})});
const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
await page.goto('http://127.0.0.1:8001');await page.getByRole('heading',{name:'Think it through.'}).waitFor();
await page.getByRole('button',{name:'Explore',exact:true}).click();await page.getByRole('img').waitFor();
await page.screenshot({path:resolve(shots,'desktop.png'),fullPage:true});
await page.getByRole('slider').fill('100');
if(!(await page.locator('output').innerText()).includes('x ='))throw Error('Missing coordinate output');
await page.getByRole('button',{name:'Show accessible data table'}).click();if(await page.locator('tbody tr').count()!==201)throw Error('Missing data rows');
await page.getByRole('button',{name:'New practice'}).click();await page.getByRole('button',{name:'Get a hint'}).waitFor();
await page.getByRole('button',{name:'Get a hint'}).click();await page.getByText('Which gas variables are supplied?').waitFor();
await page.getByRole('button',{name:'Get a hint'}).click();await page.getByText('Try a step before requesting another hint.').waitFor();
await page.getByLabel('Practice attempt').fill('0');await page.getByRole('button',{name:'Check attempt'}).click();await page.getByText('That result does not match.',{exact:false}).waitFor();
await page.screenshot({path:resolve(shots,'practice.png'),fullPage:true});
await page.getByRole('button',{name:'End practice'}).click();await page.getByLabel('Chemistry question or follow-up').fill('How does equilibrium work?');await page.getByRole('button',{name:'Send ↗'}).click();await page.getByText('Open-ended chat needs a model connection.',{exact:false}).waitFor();
await page.getByRole('button',{name:'Step checker',exact:true}).click();
await page.getByLabel('Expression',{exact:true}).fill('2*3');await page.getByLabel('Your result',{exact:true}).fill('6');await page.getByRole('button',{name:'Check step',exact:true}).click();await page.getByText('Your arithmetic matches.',{exact:false}).waitFor();
await page.getByLabel('Your balanced equation').fill('Fe^3+ + e^- -> Fe^2+');await page.getByRole('button',{name:'Check conservation'}).click();await page.getByText('Atoms and charge are conserved.',{exact:false}).waitFor();
await page.getByLabel('Chemistry question or follow-up').fill(String.raw`How do I use \(PV=nRT\) and \(\ce{H2O}\)?`);await page.getByRole('button',{name:'Send ↗'}).click();await page.locator('.katex').first().waitFor();
await page.getByRole('button',{name:'Coverage & proof',exact:true}).click();await page.getByRole('dialog').waitFor();await page.getByRole('button',{name:'Close ×'}).press('Escape');if(await page.getByRole('dialog').count())throw Error('Escape did not close modal');
await page.getByRole('button',{name:'Graph lab',exact:true}).click();
await page.setViewportSize({width:390,height:844});await page.screenshot({path:resolve(shots,'mobile.png'),fullPage:true});
const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
console.log(JSON.stringify({title:await page.title(),url:page.url(),errors,overflow,checks:['app loaded','graph rendered','coordinate slider','201-row table','practice start','hint gate','wrong attempt','end practice','honest model-unconfigured state','mobile viewport','step checking','ionic charge conservation','LaTeX and mhchem','coverage modal and Escape']},null,2));
await browser.close();if(errors.length||overflow)process.exitCode=1;

}finally{server.kill();}
