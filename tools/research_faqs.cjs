// Read the current live FAQ accordion; no forms or account actions are used.
const fs=require('fs');const path=require('path');
const {chromium}=require(process.env.TCS_PLAYWRIGHT||'playwright');
const services=JSON.parse(fs.readFileSync('audit/navigation-services.json','utf8'));
const requested=process.argv.slice(2);
const selected=requested.length?services.filter(s=>requested.includes(s.id)):services;
fs.mkdirSync('.firecrawl/faqs',{recursive:true});
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 for(const service of selected){
  const output=path.join('.firecrawl/faqs',service.id+'.json');if(fs.existsSync(output))continue;
  const page=await browser.newPage();
  try{
   await page.goto(service.source_url,{waitUntil:'domcontentloaded',timeout:60000});
   await page.locator('.ifcFaqCardBtn').first().waitFor({timeout:20000});
   const more=page.locator('.ifcFaqBtnPrimary');
   for(let attempt=0;attempt<15;attempt++){
    if(!await more.count()||!await more.isVisible()||!/load more/i.test(await more.innerText()))break;
    const count=await page.locator('.ifcFaqCardBtn').count();
    await more.click();await page.waitForTimeout(350);
    if(await page.locator('.ifcFaqCardBtn').count()===count)break;
   }
   const buttons=page.locator('.ifcFaqCardBtn');const faqs=[];
   for(let i=0;i<await buttons.count();i++){
    const button=buttons.nth(i);await button.click();
    const answerId=await button.getAttribute('aria-controls');
    await page.waitForTimeout(70);
    const answer=await page.locator('[id="'+answerId+'"]').textContent();
    faqs.push({question:(await button.innerText()).trim(),answer:answer?.replace(/\s+/g,' ').trim()||''});
   }
   if(faqs.some(x=>!x.answer))throw new Error('One or more answers remained empty');
   fs.writeFileSync(output,JSON.stringify({source_url:page.url(),retrieved_at:new Date().toISOString(),faqs},null,2));
   console.log(service.id,faqs.length,'expanded FAQs');
  }catch(e){console.log(service.id,'FAQ_RESEARCH_FAILED',e.message.split('\n')[0]);}
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
