import os
import re
import urllib.parse
import bs4
import json
import concurrent.futures
import time

BASE = 'd:/user/TCS_website'

# 1. Load services from menus_fixed.json
with open(os.path.join(BASE, 'menus_fixed.json'), 'r', encoding='utf-8') as f:
    scraped_menus = json.load(f)

# Alternate raw file names for services that were downloaded with specific names
alt_raw = {
    'company-registration': 'plc_raw.html',
    'private-limited-company': 'plc_raw.html',
    'public-limited-company': 'publc_raw.html',
    'llp-registration': 'llp_raw.html',
    'one-person-company': 'opc_raw.html',
    'section-8-company-registration': 'section_8_raw.html',
    'indian-subsidiary': 'indian_subsidiary_raw.html',
    'producer-company-registration': 'producer_company_raw.html',
    'trust-registration': 'trust_raw.html',
    'gst-registration': 'gst_raw.html',
    'udyam-registration': 'udyam_raw.html',
    'trademark-registration': 'trademark_raw.html',
    'income-tax-filing': 'income_tax_filing_raw.html',
    'proprietorship': 'proprietorship_raw.html',
    'partnership': 'partnership_raw.html'
}

all_services = []
for cat, html in scraped_menus.items():
    s = bs4.BeautifulSoup(html, 'html.parser')
    for a in s.find_all('a')[1:]:
        href = a.get('href', '')
        text = a.get_text().strip()
        slug = href.lstrip('/')
        if slug:
            all_services.append({'title': text, 'slug': slug})

seen = set()
unique_services = []
for s in all_services:
    if s['slug'] not in seen:
        seen.add(s['slug'])
        unique_services.append(s)

# Build configuration for all 116 services
all_service_configs = []
for s in unique_services:
    slug = s['slug']
    title_clean = s['title']
    
    # Check which raw file exists
    raw_file = alt_raw.get(slug, f"{slug}_raw.html")
    if not os.path.exists(os.path.join(BASE, raw_file)):
        if os.path.exists(os.path.join(BASE, f"{slug}_raw.html")):
            raw_file = f"{slug}_raw.html"
        else:
            print(f"Warning: no raw file for {slug}")
            continue

    out_file = 'private-limited-company.html' if slug == 'company-registration' else f"{slug}.html"
    
    all_service_configs.append({
        'slug': slug,
        'raw_file': raw_file,
        'out_file': out_file,
        'title': f"{title_clean} Online in India | TCS"
    })

copy_replacements = {
    "IndiaFilings": "Tirumala Consultancy Services",
    "indiafilings": "tirumalaconsultancy",
    "India's Largest AI-Powered Corporate Services & Compliance Platform": "Strategic Corporate Services & Compliance Platform",
    "Join millions who trust IndiaFilings": "Join thousands who trust TCS",
    "Lionel Charles": "TCS Team"
}

# Every single service slug maps to its own standalone .html page
internal_links = {}
for s in unique_services:
    slug = s['slug']
    if slug == 'company-registration':
        internal_links[slug] = './private-limited-company.html'
    else:
        internal_links[slug] = f"./{slug}.html"

category_links = [
    '/startup', '/registrations', '/trademark', '/gst', '/income-tax',
    '/mca-services', '/hr-services', '/consultation', '/uae'
]

def build_single_page(cfg):
    raw_path = os.path.join(BASE, cfg['raw_file'])
    out_path = os.path.join(BASE, cfg['out_file'])
    slug = cfg['slug']
    
    if not os.path.exists(raw_path):
        return slug, False, f"Raw file {raw_path} not found"

    with open(raw_path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')

    # 1. Meta & Title
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

    # 2. Clean head
    for link in list(soup.find_all('link')):
        href = link.get('href', '')
        rel = link.get('rel', [])
        if isinstance(rel, str):
            rel = [rel]
        
        # Remove external preconnects / preloads / imagesrcset
        if link.has_attr('imagesrcset') or (link.get('as') == 'image' and 'indiafilings' in href):
            link.decompose()
            continue
        if any(dom in href for dom in ['indiafilings.com', 'ledgersapi.com', 'ledgers.cloud', 'ifpayment', 'cognito-idp']):
            link.decompose()
            continue
        if 'preload' in rel and link.get('as') == 'script':
            link.decompose()
            continue
        if 'canonical' in rel:
            link['href'] = f'./{slug}.html'
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
        if any('icon' in r.lower() for r in rel):
            link['href'] = './images/tcs_favicon.png'

    # Ensure 2hybm2qaok1px.css is linked
    has_2hy = any('2hybm2qaok1px.css' in (l.get('href') or '') for l in soup.find_all('link', rel='stylesheet'))
    if not has_2hy and soup.head:
        new_link = soup.new_tag('link', rel='stylesheet', href='./css/2hybm2qaok1px.css')
        soup.head.append(new_link)

    # Ensure tcs-interactions.css is linked
    has_interactions = any('tcs-interactions.css' in (l.get('href') or '') for l in soup.find_all('link', rel='stylesheet'))
    if not has_interactions and soup.head:
        new_link = soup.new_tag('link', rel='stylesheet', href='./css/tcs-interactions.css')
        soup.head.append(new_link)

    # 3. Clean Images
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            if 'logo-110x52.png' in src or 'tcs_logo' in src:
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
                
                # Link logo to home page
                parent_a = img.find_parent('a')
                if parent_a:
                    parent_a['href'] = './index.html'
                    parent_a['title'] = 'Tirumala Consultancy Services'
                    parent_a['aria-label'] = 'Tirumala Consultancy Services Home'
                else:
                    new_a = soup.new_tag('a', href='./index.html', title='Tirumala Consultancy Services', style='display: inline-block;')
                    new_a['aria-label'] = 'Tirumala Consultancy Services Home'
                    img.wrap(new_a)
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

    # 4. Decompose Next.js scripts, GTM, JSON-LD, Cloudflare
    for script in list(soup.find_all('script')):
        text = script.string or script.get_text() or ''
        if 'tailwind.config' in text:
            continue
        script.decompose()

    for noscript in list(soup.find_all('noscript')):
        noscript.decompose()

    # 5. Navbar Mega Menus & Sub Lists
    nav = soup.find('nav')
    if nav and scraped_menus:
        for a in nav.find_all('a', href=True):
            href = a['href']
            if href in scraped_menus:
                # Disable main category hyperlink so it does NOT redirect
                a['href'] = 'javascript:void(0)'
                a['role'] = 'button'
                a['aria-haspopup'] = 'true'
                a['aria-expanded'] = 'false'
                a['style'] = 'cursor: pointer;'
                
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
                    
                    # Ensure first link in dropdown menu also doesn't redirect
                    first_dropdown_a = dropdown_soup.find('a')
                    if first_dropdown_a:
                        first_dropdown_a['href'] = 'javascript:void(0)'
                        first_dropdown_a['role'] = 'button'
                        first_dropdown_a['style'] = 'cursor: pointer;'

                    # Fix internal sub-links in dropdown
                    for sub_a in dropdown_soup.find_all('a', href=True):
                        sub_href = sub_a['href']
                        if sub_href == 'javascript:void(0)':
                            continue
                        clean_sub = sub_href.lstrip('/')
                        if clean_sub in internal_links:
                            sub_a['href'] = internal_links[clean_sub]
                        elif any(c == sub_href for c in category_links):
                            sub_a['href'] = 'javascript:void(0)'
                        else:
                            sub_a['href'] = f"./{clean_sub}.html"

                    # Configure hover classes
                    for div in dropdown_soup.find_all('div', class_=True):
                        div_classes = div.get('class', [])
                        if 'absolute' in div_classes and 'top-full' in div_classes:
                            if 'hidden' not in div_classes:
                                div_classes.append('hidden')
                            if 'group-hover:block' not in div_classes:
                                div_classes.append('group-hover:block')
                            div['class'] = div_classes

                    parent.clear()
                    for child in list(dropdown_soup.children):
                        parent.append(child)

    # Ensure ALL category links in the nav are non-redirectable buttons
    if nav:
        for a in nav.find_all('a', href=True):
            href = a['href']
            if any(c == href for c in category_links):
                a['href'] = 'javascript:void(0)'
                a['role'] = 'button'
                a['aria-haspopup'] = 'true'
                a['aria-expanded'] = 'false'
                a['style'] = 'cursor: pointer;'

    # Replace Login button with "Talk to experts"
    for btn in soup.find_all('button'):
        if btn.string and 'Login' in btn.string:
            btn.string = btn.string.replace('Login', 'Talk to experts')
            if btn.has_attr('class'):
                classes = ' '.join(btn['class'])
                classes = classes.replace('px-5', 'px-4').replace('py-2.5', 'py-2')
                btn['class'] = classes.split(' ')

    # 5.5 Remove Unwanted Promotional & Form Cards from Hero Banner
    banner = soup.find('section', role='banner')
    if banner:
        title = banner.find(class_=lambda c: c and 'journey_first_section_title' in c)
        if title:
            title_box = title.find_parent('div', class_=lambda c: c and 'text-center' in c)
            if title_box:
                # Remove all siblings after title_box (Card 1: promo/pricing banner, Card 2: form section)
                for sib in list(title_box.next_siblings):
                    if hasattr(sib, 'decompose'):
                        sib.decompose()
                    elif hasattr(sib, 'extract'):
                        sib.extract()

                # Provide natural bottom breathing room so background curves cleanly below subtitle
                if title_box.parent:
                    title_box.parent['style'] = 'padding-bottom: 40px;'

                # Adjust background gradient div to 100% height and remove min-height: 500px
                bg_div = banner.find('div', style=lambda s: s and 'radial-gradient' in s)
                if bg_div:
                    s = bg_div['style']
                    s = re.sub(r'min-height:\s*500px;?', '', s)
                    s = re.sub(r'height:\s*calc\([^)]+\);?', 'height:100%;', s)
                    bg_div['style'] = s

        # Failsafe cleanup of any remaining pricing button wrappers, form sections, or templates in banner
        for btn in banner.find_all('button', attrs={'aria-label': lambda x: x and 'pricing' in x.lower()}):
            wrapper = btn.find_parent('div', class_=lambda c: c and 'items-center' in c)
            if wrapper:
                wrapper.decompose()
            else:
                btn.decompose()
        for form_sec in banner.find_all('section', attrs={'data-journey-form-section': True}):
            form_sec.decompose()
        for form_sec in banner.find_all('section', id=lambda x: x and 'form-section' in x):
            form_sec.decompose()
        for tmpl in banner.find_all('template'):
            tmpl.decompose()

    # 6. Replace External Links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href == '/' or href == './':
            a['href'] = './index.html'
            continue
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
                a['href'] = './proprietorship.html'

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

    # 8. Add local interaction script
    if soup.body:
        has_tcs_js = any('tcs.js' in (s.get('src') or '') for s in soup.body.find_all('script'))
        if not has_tcs_js:
            tcs_script = soup.new_tag('script', src='./js/tcs.js', defer=True)
            soup.body.append(tcs_script)

    out_html = str(soup)
    out_html = out_html.replace('https://www.facebook.com/IndiaFilings', '#')
    out_html = out_html.replace('https://twitter.com/IndiaFilings', '#')
    out_html = out_html.replace('https://www.youtube.com/@indiafilings', '#')
    out_html = re.sub(r'href=[\'"]https?://(?:www\.)?indiafilings\.com[^\'"]*[\'"]', 'href="./proprietorship.html"', out_html, flags=re.I)
    out_html = re.sub(r'https?://(?:www\.)?indiafilings\.com[^\s"\'<>]*', '#', out_html, flags=re.I)
    out_html = re.sub(r'https?://(?:img\.)?indiafilings\.com[^\s"\'<>]*', '#', out_html, flags=re.I)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out_html)

    return slug, True, len(out_html)

if __name__ == '__main__':
    print(f"Total service configs to build: {len(all_service_configs)}")
    t0 = time.time()
    built = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(build_single_page, cfg): cfg for cfg in all_service_configs}
        for fut in concurrent.futures.as_completed(futures):
            slug, success, msg = fut.result()
            if success:
                built += 1
            else:
                print(f"FAILED {slug}: {msg}")

    print(f"\nSuccessfully built {built}/{len(all_service_configs)} service pages in {time.time()-t0:.2f}s!")

    # Also update index.html with the new header and ensure all logos in index.html are linked
    try:
        sample_soup = bs4.BeautifulSoup(open(os.path.join(BASE, 'proprietorship.html'), encoding='utf-8'), 'html.parser')
        header = sample_soup.find('header')
        index_soup = bs4.BeautifulSoup(open(os.path.join(BASE, 'index.html'), encoding='utf-8'), 'html.parser')
        old_header = index_soup.find('header')
        if old_header and header:
            old_header.replace_with(header)
        for img in index_soup.find_all('img'):
            src = img.get('src', '')
            if 'logo' in src.lower():
                parent_a = img.find_parent('a')
                if parent_a:
                    parent_a['href'] = './index.html'
                else:
                    new_a = index_soup.new_tag('a', href='./index.html', title='Tirumala Consultancy Services', style='display: inline-block;')
                    new_a['aria-label'] = 'Tirumala Consultancy Services Home'
                    img.wrap(new_a)
        with open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(str(index_soup))
        print("index.html header and logos linked to ./index.html successfully.")
    except Exception as e:
        print(f"Error updating index.html: {e}")
