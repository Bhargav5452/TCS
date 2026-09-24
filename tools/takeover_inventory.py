"""Read-only inventory; run with BeautifulSoup and Jinja2 installed."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import jinja2

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html'] + [p.stem + '.html' for p in sorted((ROOT / 'data').glob('*.json'))]

def inspect(name):
    text = (ROOT / name).read_text(encoding='utf-8')
    soup = BeautifulSoup(text, 'html.parser')
    links = []
    for el in soup.find_all(True):
        for attr in ['href', 'src', 'srcset', 'imagesrcset', 'action', 'poster']:
            if el.get(attr):
                value = el[attr]
                if 'indiafilings' in value.lower() or any(x in value for x in ['ledgers', 'ifpayment', '_next', 'cdn-cgi']):
                    links.append({'tag': el.name, 'attr': attr, 'rel': el.get('rel'), 'url': value, 'text': el.get_text(' ', strip=True)[:80]})
    scripts = [{'src': s.get('src'), 'length': len(s.get_text()), 'start': s.get_text().strip()[:110]} for s in soup.find_all('script')]
    css = '\n'.join(s.get_text() for s in soup.find_all('style'))
    missing = []
    for el in soup.select('link[rel=stylesheet], img[src], script[src]'):
        url = el.get('href') or el.get('src')
        if url and not urlsplit(url).scheme and not (ROOT / url.lstrip('./')).exists():
            missing.append(url)
    return {'sha256': hashlib.sha256(text.encode()).hexdigest(), 'scripts': scripts, 'dependency_attributes': links,
            'missing_assets': sorted(set(missing)), 'faq_count': len(soup.select('.ifcFaqCard')),
            'tokens': dict(re.findall(r'(--color-[\w-]+)\s*:\s*([^;]+)', css)),
            'inline_color_literals': len(re.findall(r'#[\da-fA-F]{3,8}\b|rgba?\(', css)),
            'headings': [h.get_text(' ', strip=True) for h in soup.select('h1,h2')],
            'stylesheet_links': [x.get('href') for x in soup.select('link[rel=stylesheet]')]}

if __name__ == '__main__':
    result = {p: inspect(p) for p in PAGES + ['templates/service_page.html']}
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ROOT / 'templates'))
    import importlib.util
    spec = importlib.util.spec_from_file_location('generator', ROOT / 'generate_pages.py')
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    for path in sorted((ROOT / 'data').glob('*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        rendered = env.get_template('service_page.html').render(page=data, site=gen.site_data)
        existing = (ROOT / (path.stem + '.html')).read_text(encoding='utf-8')
        result[path.stem + '.html']['render_matches'] = rendered == existing
        result[path.stem + '.html']['data_fields'] = list(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
