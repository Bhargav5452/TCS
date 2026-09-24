"""Prepare a source-specific editorial import schema, never a generic outline."""
import json
import re
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
slug=sys.argv[1]
raw=json.loads((ROOT/'.firecrawl'/f'{slug}.json').read_text(encoding='utf-8'))
markdown=raw['markdown']
start=re.search(r'^# (.+)$',markdown,re.M)
if not start: raise ValueError('No main article heading; inspect this source manually')
end=re.search(r'^### Related Guides|^## Frequently asked questions',markdown[start.end():],re.M)
article=markdown[start.end():start.end()+end.start()] if end else markdown[start.end():]
sections=[]
positions=list(re.finditer(r'^## (.+)$',article,re.M))
intro=article[:positions[0].start()] if positions else article
for i,m in enumerate(positions):
    body=article[m.end():positions[i+1].start() if i+1<len(positions) else len(article)].strip()
    # The consultant illustration is branding, not factual article content.
    body=re.split(r'\[!\[Expert ',body)[0].strip()
    sections.append({'key':f's{i+1:03}', 'source_heading':m.group(1), 'source_body':body,
                     'subheadings':re.findall(r'^#{3,6} (.+)$',body,re.M),
                     'list_items':len(re.findall(r'^(?:- |\d+\. )',body,re.M)),
                     'table_rows':len(re.findall(r'^\|',body,re.M))})
policy=('Write original, publishable editorial copy for Tirumala Consultancy Services (TCS), '
        'based on the factual information in this exact source section. Do not summarize or compress '
        'away topics. Preserve every subheading topic in its order, each list item, each process step '
        'and every meaningful table cell. Use fresh sentence structures and your own explanations, '
        'not synonym substitution. Do not copy source branding, testimonials, proprietary assets, '
        'claims about provider scale, guaranteed turnaround or provider prices. Use a neutral TCS '
        'service explanation for promotional sections; no invented credentials, promises or prices. '
        'Retain legal references and essential figures, but qualify conditional requirements and '
        'flag questionable assertions in editorial_notes. Markdown only, no HTML, scripts, images '
        'or external links. Links to services may use a local /service-slug path. Never invent an '
        'extra section or substitute a standard outline. Each requested field corresponds to an '
        'actual section of the current page.')
properties={
 'hero_title':{'type':'string','description':'Original concise service title, no pricing or provider name.'},
 'hero_description':{'type':'string','description':'Original TCS service introduction, 45–65 words, grounded in the page.'},
 'introduction':{'type':'string','description':policy+' Rewrite this introduction independently: '+intro},
 'editorial_notes':{'type':'array','items':{'type':'string'},'description':'Flag factual conflicts, state-specific conditions, unsupported guarantees and unavailable source answers. Do not invent facts.'},
 'sections':{'type':'object','properties':{},'required':[],'additionalProperties':False}}
for section in sections:
    key=section['key']
    properties['sections']['properties'][key]={'type':'object','properties':{
      'heading':{'type':'string','description':'Original heading for this exact topic: '+section['source_heading']},
      'body_markdown':{'type':'string','description':policy+' Preserve these subtopics: '+json.dumps(section['subheadings'])+' Source section for factual research: '+section['source_body']}},
      'required':['heading','body_markdown'],'additionalProperties':False}
    properties['sections']['required'].append(key)
schema={'type':'object','description':policy,'properties':properties,'required':list(properties),'additionalProperties':False}
dest=ROOT/'.firecrawl'/'schemas';dest.mkdir(exist_ok=True)
(dest/f'{slug}.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2),encoding='utf-8')
outlines=ROOT/'.firecrawl'/'outlines';outlines.mkdir(exist_ok=True)
(outlines/f'{slug}.json').write_text(json.dumps({'title':start.group(1),'sections':sections},ensure_ascii=False,indent=2),encoding='utf-8')
print(slug, len(sections), 'source-specific sections',sum(s['list_items'] for s in sections),'list items',sum(s['table_rows'] for s in sections),'table rows')
