import os
import glob
import re
from collections import Counter, defaultdict
from urllib.parse import urlparse

PAGES_DIR = 'd:/user/TCS_website'

# All production HTML files
all_html_files = [os.path.basename(f) for f in glob.glob(os.path.join(PAGES_DIR, '*.html')) if not f.endswith('_raw.html')]
valid_pages = set(all_html_files)
valid_slugs = set(os.path.splitext(p)[0] for p in all_html_files)

print(f"Total HTML files in website: {len(all_html_files)}")
print(f"Index.html present: {'index.html' in valid_pages}")
print(f"Total service pages: {len(all_html_files) - 1}")

def is_external_or_special(href):
    h = href.strip().lower()
    if not h or h.startswith('#') or h.startswith('javascript:') or h.startswith('tel:') or h.startswith('mailto:'):
        return True
    if h.startswith('http://') or h.startswith('https://') or h.startswith('//'):
        return True
    return False

def resolve_internal_target(href, current_page):
    """
    Resolves an internal href to a normalized page name like 'proprietorship.html',
    or None if it cannot be resolved / does not exist.
    Also returns whether it is considered an internal link.
    """
    clean_h = href.split('#')[0].split('?')[0].strip()
    if not clean_h:
        # Just an anchor or query on current page
        return current_page, True
    
    # Remove leading slash or ./
    path = clean_h
    if path.startswith('/'):
        path = path[1:]
    elif path.startswith('./'):
        path = path[2:]
    
    # Check if empty (e.g. '/' -> index.html)
    if not path or path == '':
        return 'index.html', True
        
    # Check if path ends with .html
    if path.endswith('.html'):
        candidate = path
    else:
        # maybe 'proprietorship' or 'gst-registration/'
        candidate_stem = path.rstrip('/')
        candidate = candidate_stem + '.html'
        
    # Is candidate in valid_pages?
    if candidate in valid_pages:
        return candidate, True
        
    # Check if stem is in valid_slugs
    stem = os.path.splitext(candidate)[0]
    # Sometimes paths have folders e.g. /services/proprietorship or /startup/proprietorship
    basename = os.path.basename(candidate)
    if basename in valid_pages:
        return basename, True
        
    return candidate, False

# Scan all pages
all_internal_links = Counter()
broken_internal_links = Counter()
valid_internal_links = Counter()
external_or_special_links = Counter()

# Section breakdowns for broken links
broken_in_related_services = Counter()
broken_in_faq = Counter()
broken_in_nav_or_footer = Counter()
broken_in_body = Counter()

broken_details = []

for page in all_html_files:
    fpath = os.path.join(PAGES_DIR, page)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Find sections
    # related services section: <section id="related-services-section"> ... </section>
    related_sec_match = re.search(r'(<section\b[^>]*id=[\"\']related-services-section[\"\'][^>]*>.*?</section>)', content, re.DOTALL | re.IGNORECASE)
    related_sec = related_sec_match.group(1) if related_sec_match else ""

    # faq section: <section id="faq-section"> ... </section>
    faq_sec_match = re.search(r'(<section\b[^>]*id=[\"\']faq-section[\"\'][^>]*>.*?</section>)', content, re.DOTALL | re.IGNORECASE)
    faq_sec = faq_sec_match.group(1) if faq_sec_match else ""

    # Find all <a> tags
    # regex to extract the full <a>...</a> tag and its href
    a_pattern = re.compile(r'(<a\b([^>]*)>(.*?)</a>)', re.DOTALL | re.IGNORECASE)
    for match in a_pattern.finditer(content):
        full_tag, attrs, inner_text = match.groups()
        href_match = re.search(r'\bhref\s*=\s*[\"\']([^\"\']*)[\"\']', attrs, re.IGNORECASE)
        if not href_match:
            continue
        href = href_match.group(1)
        
        if is_external_or_special(href):
            external_or_special_links[href] += 1
            continue
            
        target, exists = resolve_internal_target(href, page)
        all_internal_links[href] += 1
        
        if exists:
            valid_internal_links[href] += 1
        else:
            broken_internal_links[href] += 1
            
            # Check which section it is in
            in_rel = full_tag in related_sec
            in_faq = full_tag in faq_sec
            
            loc = "body"
            if in_rel:
                loc = "related-services"
                broken_in_related_services[href] += 1
            elif in_faq:
                loc = "faq"
                broken_in_faq[href] += 1
            else:
                broken_in_body[href] += 1
                
            broken_details.append({
                'page': page,
                'href': href,
                'target': target,
                'inner_text': inner_text.strip()[:60],
                'location': loc
            })

print("\n--- SUMMARY ---")
print(f"Total internal link occurrences: {sum(all_internal_links.values())}")
print(f"Total valid internal link occurrences: {sum(valid_internal_links.values())}")
print(f"Total broken internal link occurrences: {sum(broken_internal_links.values())}")
print(f"Unique broken internal hrefs: {len(broken_internal_links)}")
print(f"Broken in Related Services occurrences: {sum(broken_in_related_services.values())}")
print(f"Broken in FAQ occurrences: {sum(broken_in_faq.values())}")
print(f"Broken in other body/sections occurrences: {sum(broken_in_body.values())}")

print("\n--- TOP BROKEN INTERNAL HREFS ---")
for h, c in broken_internal_links.most_common(40):
    print(f"{c:4d} occurrences : {h}")

print("\n--- SAMPLE BROKEN IN RELATED SERVICES ---")
for h, c in broken_in_related_services.most_common(20):
    print(f"{c:4d} occurrences in Related Services : {h}")

print("\n--- SAMPLE BROKEN IN FAQ ---")
for h, c in broken_in_faq.most_common(20):
    print(f"{c:4d} occurrences in FAQ : {h}")

print("\n--- SAMPLE BROKEN IN BODY ---")
for h, c in broken_in_body.most_common(20):
    print(f"{c:4d} occurrences in Body : {h}")
