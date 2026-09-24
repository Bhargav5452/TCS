"""One-time extraction of the protected service shell into shared partials."""
import json
from pathlib import Path
import re
import sys
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_production import clean_page

ROOT=Path(__file__).resolve().parents[1]
reference=ROOT/'audit/reference-backup/templates/service_page.html'
raw=reference.read_text(encoding='utf-8')
# HTML parsers cannot parse Jinja control-flow as standalone tag attributes.
raw=raw.replace('{% if service.id == page.id %}aria-current="page"{% endif %}',
                'aria-current="{{ \'page\' if service.id == page.id else \'false\' }}"')
html=clean_page(raw,'service-template')
soup=BeautifulSoup(html,'html.parser')
partials=ROOT/'templates/partials';partials.mkdir(exist_ok=True)

# Match the currently rendered colors exactly; tokenize without introducing the
# missing semantic utility rules, which would change the protected appearance.
root_style=next(el for el in soup.find_all('style') if '--color-brand:' in el.get_text())
tokens=root_style.get_text()
palette=dict(re.findall(r'(--color-[\w-]+)\s*:\s*([^;]+);',tokens))
reverse={value.strip():name for name,value in reversed(list(palette.items()))}
for style in soup.find_all('style'):
    if style is root_style: continue
    content=style.get_text()
    for value,name in sorted(reverse.items(),key=lambda x:-len(x[0])):
        content=re.sub(re.escape(value)+r'(?![\da-fA-F])',f'var({name})',content)
    style.string=content
(ROOT/'css/tcs-tokens.css').write_text(tokens.strip()+'\n',encoding='utf-8')
root_style.replace_with(soup.new_tag('link',rel='stylesheet',href='./css/tcs-tokens.css'))

# Service metadata and breadcrumbs are data; geometry and classes stay intact.
for meta in soup.select('meta[property="og:title"],meta[name="twitter:title"],meta[property="og:image:alt"]'):
    meta['content']='{{ page.meta_title }}'
for meta in soup.select('meta[property="og:description"],meta[name="twitter:description"]'):
    meta['content']='{{ page.meta_description }}'
for meta in soup.select('meta[property="og:url"],meta[name="keywords"]'): meta.decompose()
crumb=soup.find(id='custom-breadcrumb')
crumb.find_all('a')[1].string="{{ page.category | default('Business Registration') }}"
crumb.find_all('span')[-1].string="{{ page.nav_label | default('Proprietorship') }}"
for button in soup.select('.ifcFaqCardBtn'):
    button['id']='faq-heading-{{ loop.index }}'
related=soup.find(id='related-services')
related.find('h3').string="{{ page.related_heading | default('Related Services - Business Registration') }}"

# Retain the existing local animation/FAQ code; add shared navigation separately.
scripts=[sc for sc in soup.find_all('script') if 'IntersectionObserver' in sc.get_text()]
assert len(scripts)==1
(ROOT/'js/tcs-service.js').write_text(scripts[0].get_text().strip()+'\n',encoding='utf-8')
scripts[0].replace_with(soup.new_tag('script',src='./js/tcs-service.js',defer=''))
soup.body.append(soup.new_tag('script',src='./js/tcs-navigation.js',defer=''))
soup.head.append(soup.new_tag('link',rel='stylesheet',href='./css/tcs-interactions.css'))

replacements=[]
for name,element in [('navbar',soup.select_one('header.ifLayoutHeader')),
                     ('hero',soup.find(id='hero-title-proprietor').find_parent('section')),
                     ('breadcrumb',crumb),('faq',soup.find(id='custom-faq-container')),
                     ('related-services',related),('footer',soup.find('footer'))]:
    assert element is not None,name
    text=str(element)
    if name=='related-services':
        text=text.replace('site.related_services','page.related_services | default(site.related_services)')
    (partials/f'{name}.html').write_text(text,encoding='utf-8')
    marker='TCS_INCLUDE_'+name.upper().replace('-','_')
    element.replace_with(marker)
    replacements.append((marker,"{% include 'partials/"+name+".html' %}"))
out=str(soup)
for marker,include in replacements: out=out.replace(marker,include)
(ROOT/'templates/service_page.html').write_text(out,encoding='utf-8')
print('Extracted six shared partials; no layout or palette redesign.')
