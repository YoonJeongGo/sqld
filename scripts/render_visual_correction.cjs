// Render the reviewed SVG correction only. No original files or network sources are modified.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
(async()=>{
  const root=path.resolve(__dirname,'..');
  const svg=fs.readFileSync(path.join(root,'evidence/visuals-corrections/20-corrected.svg'),'utf8');
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  try{
    const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1.5});
    await page.route('**/*',route=>route.abort());
    await page.setContent('<!doctype html><html lang="ko"><meta charset="utf-8"><style>html,body{margin:0;width:1600px;height:1000px;overflow:hidden}svg{display:block}</style>'+svg+'</html>');
    await page.evaluate(()=>document.fonts.ready);
    await page.locator('svg').screenshot({path:path.join(root,'evidence/visuals-corrections/20-corrected.png')});
    fs.writeFileSync(path.join(root,'evidence/visuals-corrections/render-evidence.json'),JSON.stringify({engine:'Chromium '+browser.version(),source:'20-corrected.svg',output:'20-corrected.png',width:2400,height:1500,deviceScaleFactor:1.5,font:'SVG font fallback uses installed system Korean fonts; no font bundled',network:'blocked'},null,2));
    console.log('Rendered corrected CUBE SVG at 2400x1500');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
