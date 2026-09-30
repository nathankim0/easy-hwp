import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:net';

const [input, destination] = process.argv.slice(2);
if (!input || !destination) throw new Error('usage: node render-pdf.mjs input.hwp output.pdf');
if ([input,destination].some(p => /[\r\n\0]/.test(p))) throw new Error('paths must not contain CR, LF, or NUL');
if (typeof WebSocket !== 'function') throw new Error('PDF export requires Node 22+ (built-in WebSocket)');
const source = realpathSync(input), output = resolve(destination);
if (!['.hwp','.hwpx'].includes(extname(source).toLowerCase()) || extname(output).toLowerCase() !== '.pdf' || source === output) throw new Error('expected an HWP/HWPX input and a separate PDF output');
const candidates = [process.env.HWP_BROWSER, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', process.env.PROGRAMFILES && join(process.env.PROGRAMFILES,'Google/Chrome/Application/chrome.exe')].filter(Boolean);
const browser = candidates.find(existsSync);
if (!browser) throw new Error('Chrome/Chromium missing; set HWP_BROWSER to its executable path');
const reserve = createServer();
await new Promise(resolve => reserve.listen(0,'127.0.0.1',resolve));
const previewPort = reserve.address().port;
await new Promise(resolve => reserve.close(resolve));
const server = spawn(process.execPath, [join(dirname(fileURLToPath(import.meta.url)),'preview-server.js')], {env:{...process.env, CLAW_HWP_PREVIEW_PORT:String(previewPort)}, stdio:['ignore','ignore','pipe']});
let serverError; server.on('error',error => {serverError=error;});
server.stderr.on('data',()=>{});
const profile = mkdtempSync(join(tmpdir(), 'hwp-print-'));
const chrome = spawn(browser, [
  '--headless=new', '--no-first-run', '--no-default-browser-check', '--disable-gpu',
  '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });
let chromeError; chrome.on('error',error => {chromeError=error;});
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws;
try {
  for (let i=0;i<100;i++) {
    if (serverError) throw serverError;
    try { if ((await fetch(`http://127.0.0.1:${previewPort}/`)).ok) break; } catch {}
    await sleep(100);
  }
  const portFile = join(profile, 'DevToolsActivePort');
  for (let i = 0; i < 100 && !existsSync(portFile); i++) {
    if (chromeError) throw chromeError;
    await sleep(100);
  }
  if (!existsSync(portFile)) throw new Error('Chrome debugging port did not open');
  const port = Number(readFileSync(portFile, 'utf8').split('\n')[0]);
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const target = targets.find(x => x.type === 'page');
  if (!target) throw new Error('Chrome page target missing');
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
  let nextId = 0;
  const pending = new Map();
  ws.onmessage = ({ data }) => {
    const msg = JSON.parse(data);
    if (!msg.id) return;
    const p = pending.get(msg.id);
    if (!p) return;
    pending.delete(msg.id);
    clearTimeout(p.timer);
    msg.error ? p.reject(new Error(msg.error.message)) : p.resolve(msg.result);
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`${method} timed out`)); }, 30000);
    pending.set(id, { resolve, reject, timer });
    ws.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => {
    const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
    return result.result.value;
  };
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Page.navigate', { url: `http://127.0.0.1:${previewPort}/?path=${encodeURIComponent(source)}` });
  let state;
  for (let i = 0; i < 120; i++) {
    state = await evaluate(`({pages:document.querySelectorAll('.hwp-page canvas').length,total:Number(document.querySelector('#page-total')?.textContent),error:document.querySelector('.status.error')?.textContent})`);
    if (state.error) throw new Error(state.error);
    if (state.total > 0 && state.pages === state.total) break;
    await sleep(500);
  }
  if (!state || state.total < 1 || state.pages !== state.total) throw new Error(`HWP render timed out: ${JSON.stringify(state)}`);
  const size = await evaluate(`(() => {
    const pages = [...document.querySelectorAll('.hwp-page canvas')];
    const w = Number(pages[0].dataset.pageWidth), h = Number(pages[0].dataset.pageHeight);
    const root = document.createElement('div'); root.id = 'print-root';
    for (const canvas of pages) {
      const page = document.createElement('div'); page.className = 'print-page';
      page.append(canvas); root.append(page);
    }
    document.body.replaceChildren(root);
    const style = document.createElement('style');
    style.textContent = '@page { size: '+w+'px '+h+'px; margin: 0 } html,body { display:block!important; width:'+w+'px!important; height:auto!important; margin:0!important; padding:0!important; overflow:visible!important; background:white!important } #print-root { display:block!important; width:'+w+'px!important } .print-page { display:block!important; width:'+w+'px!important; height:'+h+'px!important; margin:0!important; padding:0!important; overflow:hidden!important; break-after:page!important; page-break-after:always!important } .print-page:last-child { break-after:auto!important; page-break-after:auto!important } .print-page canvas { position:static!important; display:block!important; width:'+w+'px!important; height:'+h+'px!important; margin:0!important; padding:0!important; box-shadow:none!important }';
    document.head.append(style);
    return {width:w,height:h,pages:pages.length};
  })()`);
  if (size.width <= 0 || size.height <= 0) throw new Error('Invalid page geometry');
  await sleep(300);
  const result = await send('Page.printToPDF', {
    printBackground: true, preferCSSPageSize: true, displayHeaderFooter: false,
    marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0,
  });
  writeFileSync(output, Buffer.from(result.data, 'base64'));
  console.log(JSON.stringify({pages:size.pages,width:size.width,height:size.height,output,renderer:'rhwp-preview',searchable:false}));
} finally {
  ws?.close();
  chrome.kill();
  server.kill();
  rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 100 });
}
