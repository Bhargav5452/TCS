const fs = require('fs');
const crypto = require('crypto');
const {chromium} = require(process.env.TCS_PLAYWRIGHT || 'playwright');
const pages = JSON.parse(fs.readFileSync('dist/build-manifest.json')).pages;
(async()=>{
  const browser = await chromium.launch({headless:true,channel:'msedge'});
  const results=[];
  for(const name of pages){
    const pairs=[];
    for(const prefix of ['', 'dist/']){
      const page=await browser.newPage({viewport:{width:1440,height:900}});
      const requests=[],errors=[];
      page.on('request',r=>requests.push(r.url()));
      page.on('pageerror',e=>errors.push(e.message));
      await page.route(/indiafilings|ledgers|ifpayment|helpcrunch/i,r=>r.abort());
      await page.goto('http://127.0.0.1:8765/'+prefix+name,{waitUntil:'networkidle'});
      await page.evaluate(()=>document.fonts.ready);
      await page.waitForTimeout(750);
      const screenshot=await page.screenshot({fullPage:true,animations:'disabled'});
      pairs.push({hash:crypto.createHash('sha256').update(screenshot).digest('hex'),errors,
        providerRequests:requests.filter(x=>/indiafilings|ledgers|ifpayment|helpcrunch/i.test(x)),
        externalHosts:[...new Set(requests.map(x=>new URL(x).hostname).filter(x=>x!=='127.0.0.1'))]});
      await page.close();
    }
    results.push({page:name,identical:pairs[0].hash===pairs[1].hash,baseline:pairs[0],production:pairs[1]});
  }
  await browser.close();
  fs.writeFileSync('audit/production-verification.json',JSON.stringify(results,null,2));
  console.log(JSON.stringify(results,null,2));
  if(results.some(x=>!x.identical||x.production.errors.length||x.production.providerRequests.length)) process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
