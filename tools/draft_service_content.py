"""Research-only editorial drafting; drafts require coverage and human/agent review.

Uses Firecrawl query against the freshly captured page. Never runs in production.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.firecrawl'
services=json.loads((ROOT/'audit/navigation-services.json').read_text(encoding='utf-8'))
output=CACHE/'drafts';output.mkdir(exist_ok=True)
log=ROOT/'audit/editorial-progress.json'
progress={}
if log.exists(): progress=json.loads(log.read_text(encoding='utf-8'))
cli=Path(shutil.which('firecrawl.cmd')).parent/'node_modules/firecrawl-cli/dist/index.js'
for service in services:
    slug=service['id']
    if slug=='proprietorship': continue
    source=CACHE/f'{slug}.json'
    # Research collector is independent; do not substitute an assumed outline.
    if not source.exists():
        progress[slug]={'status':'awaiting_source'}
        continue
    capture=json.loads(source.read_text(encoding='utf-8'))
    text=capture.get('markdown','')
    if capture.get('metadata',{}).get('statusCode')!=200:
        progress[slug]={'status':'source_unavailable'};continue
    article_start=re.search(r'^# (.+)$',text,re.M)
    if not article_start:
        progress[slug]={'status':'requires_manual_source_outline'};continue
    tail=text[article_start.start():]
    article=re.split(r'^### Related Guides|^## Frequently asked questions',tail,flags=re.M)[0]
    headings=re.findall(r'^#{2,6} (.+)$',article,re.M)
    sections=re.findall(r'^## (.+)$',article,re.M)
    list_count=len(re.findall(r'^\s*(?:[-*] |\d+\. )',article,re.M))
    table_rows=len(re.findall(r'^\|',article,re.M))
    facts_words=len(re.sub(r'https?://[^\s)]+','',article).split())
    target=output/f'{slug}.md'
    if target.exists(): continue
    prompt=(f'Write a complete original service article for Tirumala Consultancy Services (TCS), '
            f'using this exact current live page as factual research. This is a full editorial draft, '
            f'NOT a summary. Retain the article information architecture: {len(sections)} main '
            f'sections, {len(headings)} total subsection/main topics, {list_count} list items and '
            f'{table_rows} table rows. Retain every meaningful table, comparison, requirement, '
            f'process step, exception and document. Aim for at least {max(700,int(facts_words*.95))} '
            f'words so nothing is compressed away. Use new original explanations, not copied '
            f'sentences or synonym substitutions. Start with one H1 and a service introduction, '
            f'then cover these exact topics in this exact hierarchy/order: {json.dumps(headings)}. '
            f'Main H2 sections in order: {json.dumps(sections)}. Rewrite headings naturally; '
            f'preserve topic meaning. Use source-appropriate paragraphs, lists and tables. '
            f'No HTML, images, source code, copied branding or external visitor links. '
            f'Never adopt provider prices, service promises, turnaround guarantees, testimonials, '
            f'customer counts, certifications, platform features or credentials as TCS claims. '
            f'TCS prices and contact details have not been supplied. Present promotional topics '
            f'as proposed assistance with scope to be confirmed, not invented promises. '
            f'Keep essential factual figures, forms and legal references; state conditional and '
            f'jurisdiction-specific rules accurately rather than absolute guarantees. Do not '
            f'claim business registration limits ordinary partners liability or guarantees loans. '
            f'Do not include site navigation, footer, popular searches, testimonials, related '
            f'article link directories, FAQs or related-service lists: these are researched '
            f'and implemented separately. End immediately after the final article section.')
    try:
        result=subprocess.run([shutil.which('node'),str(cli),'scrape',service['source_url'],'--query',prompt,'--max-age','3600000',
                               '-o',str(target)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=300)
        status='draft_requires_review' if result.returncode==0 and target.exists() else 'draft_failed'
        progress[slug]={'status':status,'at':datetime.now(timezone.utc).isoformat(),
                        'source_h2':sections,'source_headings':headings,'source_list_items':list_count,
                        'source_table_rows':table_rows,'source_article_words':facts_words,
                        'error':result.stderr[-300:] if result.returncode else None}
    except Exception as e: progress[slug]={'status':'draft_failed','error':str(e)}
    log.write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
    print(slug,progress[slug]['status'],flush=True)
log.write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
