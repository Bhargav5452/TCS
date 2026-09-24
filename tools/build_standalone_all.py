import os
import re
import urllib.parse
import bs4

BASE = 'd:/user/TCS_website'

page_configs = [
    {
        'raw_file': 'publc_raw.html',
        'out_file': 'public-limited-company.html',
        'slug': 'public-limited-company',
        'title': 'Public Limited Company Registration in India | TCS'
    },
    {
        'raw_file': 'plc_raw.html',
        'out_file': 'private-limited-company.html',
        'slug': 'private-limited-company',
        'title': 'Private Limited Company Registration in India | TCS'
    },
    {
        'raw_file': 'llp_raw.html',
        'out_file': 'llp-registration.html',
        'slug': 'llp-registration',
        'title': 'LLP Registration in India | TCS'
    },
    {
        'raw_file': 'opc_raw.html',
        'out_file': 'one-person-company.html',
        'slug': 'one-person-company',
        'title': 'One Person Company Registration in India | TCS'
    },
    {
        'raw_file': 'proprietorship_raw.html',
        'out_file': 'proprietorship.html',
        'slug': 'proprietorship',
        'title': 'Solo Proprietorship Registration Online in India | TCS'
    }
]

copy_replacements = {
    "IndiaFilings": "Tirumala Consultancy Services",
    "indiafilings": "tirumalaconsultancy",
    "India's Largest AI-Powered Corporate Services & Compliance Platform": "Strategic Corporate Services & Compliance Platform",
    "Join millions who trust IndiaFilings": "Join thousands who trust TCS",
    "Lionel Charles": "TCS Team"
}

internal_links = {
    'proprietorship': './proprietorship.html',
    'private-limited-company': './private-limited-company.html',
    'public-limited-company': './public-limited-company.html',
    'llp-registration': './llp-registration.html',
    'one-person-company': './one-person-company.html'
}

import json
try:
    with open(os.path.join(BASE, 'menus_fixed.json'), 'r', encoding='utf-8') as f:
        scraped_menus = json.load(f)
except Exception:
    scraped_menus = {}

def build_standalone_page(cfg):
    raw_path = os.path.join(BASE, cfg['raw_file'])
    out_path = os.path.join(BASE, cfg['out_file'])
    slug = cfg['slug']
    
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found!")
        return

    with open(raw_path, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')

    # 1. Title & Meta
    if soup.title:
        soup.title.string = cfg['title']

    for meta in soup.find_all('meta'):
        prop = meta.get('property', '') or meta.get('name', '')
        content = meta.get('content', '')
        if prop == 'og:url':
            meta['content'] = f'./{slug}.html'
        elif prop in ['og:image', 'twitter:image']:
            meta['content'] = './images/tcs_logo.png'
        elif prop == 'og:site_name':
            meta['content'] = 'Tirumala Consultancy Services'
        elif 'indiafilings' in content.lower():
            for old, new in copy_replacements.items():
                content = content.replace(old, new)
            meta['content'] = content

    # 2. Clean head: remove Next.js preload scripts, preconnects to external domains
    for link in list(soup.find_all('link')):
        href = link.get('href', '')
        rel = link.get('rel', [])
        if isinstance(rel, str):
            rel = [rel]
        
        # Remove any link with image preloads or imagesrcset pointing to external cdns
        if link.has_attr('imagesrcset') or (link.get('as') == 'image' and 'indiafilings' in href):
            link.decompose()
            continue

        # Remove external preconnects / dns-prefetch
        if any(dom in href for dom in ['indiafilings.com', 'ledgersapi.com', 'ledgers.cloud', 'ifpayment', 'cognito-idp']):
            link.decompose()
            continue
            
        # Remove preload scripts for Next.js chunks
        if 'preload' in rel and link.get('as') == 'script':
            link.decompose()
            continue

        # Canonical tag -> local
        if 'canonical' in rel:
            link['href'] = f'./{slug}.html'

        # Localize stylesheets
        if 'stylesheet' in rel or link.get('as') == 'style':
            filename = href.split('/')[-1].split('?')[0]
            if filename:
                if not filename.endswith('.css'):
                    filename += '.css'
                link['href'] = f'./css/{filename}'
                if link.has_attr('crossorigin'):
                    del link['crossorigin']
                if link.has_attr('as'):
                    del link['as']

        # Favicon
        if any('icon' in r.lower() for r in rel):
            link['href'] = './images/tcs_favicon.png'

    # Ensure 2hybm2qaok1px.css is linked if not already present
    has_2hy = any('2hybm2qaok1px.css' in (l.get('href') or '') for l in soup.find_all('link', rel='stylesheet'))
    if not has_2hy and soup.head:
        new_link = soup.new_tag('link', rel='stylesheet', href='./css/2hybm2qaok1px.css')
        soup.head.append(new_link)

    # 3. Clean and Localize Images
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            if 'logo-110x52.png' in src:
                img['src'] = './images/tcs_logo.png'
                if img.has_attr('class'):
                    classes = ' '.join(img['class'])
                    classes = classes.replace('w-[100px]', 'w-auto')
                    classes = classes.replace('max-h-10', 'h-16')
                    classes = classes.replace('sm:h-10', 'sm:h-16')
                    img['class'] = classes.split(' ')
                if img.has_attr('width'):
                    del img['width']
                if img.has_attr('height'):
                    del img['height']
            elif src.startswith('/_next/image'):
                parsed = urllib.parse.urlparse(src)
                query = urllib.parse.parse_qs(parsed.query)
                if 'url' in query:
                    actual_url = query['url'][0]
                    filename = actual_url.split('/')[-1].split('?')[0]
                else:
                    filename = "gift.png"
                img['src'] = f'./images/{filename}'
            else:
                filename = src.split('/')[-1].split('?')[0]
                if filename:
                    img['src'] = f'./images/{filename}'

        if img.has_attr('srcset'):
            del img['srcset']
        if img.has_attr('srcSet'):
            del img['srcSet']

    # 4. Remove Next.js Scripts, Tracking, Analytics, Bot Challenges, Hydration
    for script in list(soup.find_all('script')):
        src = script.get('src', '')
        text = script.string or script.get_text() or ''
        
        # Keep tailwind config script if present
        if 'tailwind.config' in text:
            continue
            
        # Decompose ALL other scripts (Next.js SSR streams, JSON-LD, Cloudflare, GTM)
        script.decompose()

    # Remove noscript
    for noscript in list(soup.find_all('noscript')):
        noscript.decompose()

    # 5. Navbar Mega Menus (Enable hover dropdowns)
    nav = soup.find('nav')
    if nav and scraped_menus:
        for a in nav.find_all('a', href=True):
            href = a['href']
            if href in scraped_menus:
                a['href'] = 'javascript:void(0)'
                parent = a.find_parent('div')
                if parent:
                    p_classes = parent.get('class', [])
                    if 'group' not in p_classes:
                        p_classes.append('group')
                    if 'relative' not in p_classes:
                        p_classes.append('relative')
                    parent['class'] = p_classes

                    raw_menu = scraped_menus[href]
                    for old_text, new_text in copy_replacements.items():
                        raw_menu = raw_menu.replace(old_text, new_text)

                    dropdown_soup = bs4.BeautifulSoup(raw_menu, 'html.parser')
                    for div in dropdown_soup.find_all('div', class_=True):
                        div_classes = div.get('class', [])
                        if 'absolute' in div_classes and 'top-full' in div_classes:
                            if 'hidden' not in div_classes:
                                div_classes.append('hidden')
                            div_classes.append('group-hover:block')
                            div['class'] = div_classes

                    parent.clear()
                    for child in list(dropdown_soup.children):
                        parent.append(child)

    # Replace Login button with "Talk to experts"
    for btn in soup.find_all('button'):
        if btn.string and 'Login' in btn.string:
            btn.string = btn.string.replace('Login', 'Talk to experts')
            if btn.has_attr('class'):
                classes = ' '.join(btn['class'])
                classes = classes.replace('px-5', 'px-4').replace('py-2.5', 'py-2')
                btn['class'] = classes.split(' ')

    # 6. Replace External Links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/careers' in href or '/referral' in href:
            a.decompose()
            continue
        if any(s in href for s in ['facebook.com/IndiaFilings', 'twitter.com/IndiaFilings', 'youtube.com/@indiafilings']):
            a['href'] = '#'
            continue
        if 'indiafilings.com' in href:
            matched_slug = None
            for s_key in internal_links:
                if f'/{s_key}' in href:
                    matched_slug = internal_links[s_key]
                    break
            if matched_slug:
                a['href'] = matched_slug
            else:
                a['href'] = '#'

    # 7. Text Replacements in DOM
    for el in soup.find_all(string=True):
        if el.parent.name not in ['script', 'style']:
            orig = el.string
            changed = False
            for old_text, new_text in copy_replacements.items():
                if old_text in orig:
                    orig = orig.replace(old_text, new_text)
                    changed = True
            if changed:
                el.replace_with(orig)

    # 8. Add local interaction script before </body>
    if soup.body:
        has_tcs_js = any('tcs.js' in (s.get('src') or '') for s in soup.body.find_all('script'))
        if not has_tcs_js:
            tcs_script = soup.new_tag('script', src='./js/tcs.js', defer=True)
            soup.body.append(tcs_script)

    # 9. Write clean standalone HTML
    out_html = str(soup)
    out_html = out_html.replace('https://www.facebook.com/IndiaFilings', '#')
    out_html = out_html.replace('https://twitter.com/IndiaFilings', '#')
    out_html = out_html.replace('https://www.youtube.com/@indiafilings', '#')
    out_html = re.sub(r'href=[\'"]https?://(?:www\.)?indiafilings\.com[^\'"]*[\'"]', 'href="#"', out_html, flags=re.I)
    out_html = re.sub(r'https?://(?:www\.)?indiafilings\.com[^\s"\'<>]*', '#', out_html, flags=re.I)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out_html)

    print(f"Successfully built standalone {out_path} (length: {len(out_html)})")

for cfg in page_configs:
    build_standalone_page(cfg)
