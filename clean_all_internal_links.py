import os
import glob
import re
from collections import Counter

PAGES_DIR = 'd:/user/TCS_website'

# All production HTML files
production_files = [os.path.basename(f) for f in glob.glob(os.path.join(PAGES_DIR, '*.html')) if not f.endswith('_raw.html')]
valid_pages = set(production_files)

print(f"Total production files to process: {len(production_files)}")

def clean_html_content(content, filename):
    original = content
    changes = []

    # 1. Related Services removal of any links to pages that don't exist
    rel_match = re.search(r'(<section\b[^>]*id=[\"\']related-services-section[\"\'][^>]*>)(.*?)(</section>)', content, re.DOTALL | re.I)
    if rel_match:
        before_rel, rel_body, after_rel = rel_match.groups()
        # Find all <a> tags inside related services
        def filter_related_pill(m):
            a_tag = m.group(0)
            hm = re.search(r'href=[\"\']([^\"\']*)[\"\']', a_tag)
            if not hm:
                return a_tag
            href = hm.group(1).strip()
            clean = href.split('#')[0].split('?')[0].strip().lstrip('/').lstrip('./')
            if not clean:
                clean = 'index.html'
            elif not clean.endswith('.html'):
                clean = clean.rstrip('/') + '.html'
            basename = os.path.basename(clean)
            if basename not in valid_pages:
                # Remove this pill
                changes.append(f"Removed non-existent Related Service pill: {href}")
                return ''
            return a_tag

        new_rel_body = re.sub(r'\s*<a\b[^>]*>.*?</a>\s*', filter_related_pill, rel_body, flags=re.DOTALL | re.I)
        if new_rel_body != rel_body:
            content = content[:rel_match.start(2)] + new_rel_body + content[rel_match.end(2):]

    # 2. Hero review badges
    # Mobile badge: <a class="flex w-[44%] shrink-0 snap-start rounded-2xl border border-gray-100 bg-white px-3 py-3 shadow-sm transition-opacity hover:opacity-75" href="/.../reviews">
    def repl_mobile_badge(m):
        inner = m.group(1)
        cls = "flex w-[44%] shrink-0 snap-start rounded-2xl border border-gray-100 bg-white px-3 py-3 shadow-sm"
        changes.append("Converted mobile hero review badge to static div")
        return f'<div class="{cls}">{inner}</div>'

    content = re.sub(
        r'<a\b[^>]*\bclass=[\"\'][^\"\']*flex w-\[44%\][^\"\']*[\"\'][^>]*href=[\"\'][^\"\']*/reviews[\"\'][^>]*>(.*?)</a>',
        repl_mobile_badge,
        content,
        flags=re.DOTALL | re.I
    )

    # Desktop badge: <a class="flex items-center gap-2.5 transition-opacity hover:opacity-75" href="/.../reviews">
    def repl_desktop_badge(m):
        inner = m.group(1)
        cls = "flex items-center gap-2.5"
        changes.append("Converted desktop hero review badge to static div")
        return f'<div class="{cls}">{inner}</div>'

    content = re.sub(
        r'<a\b[^>]*\bclass=[\"\'][^\"\']*flex items-center gap-2\.5[^\"\']*[\"\'][^>]*href=[\"\'][^\"\']*/reviews[\"\'][^>]*>(.*?)</a>',
        repl_desktop_badge,
        content,
        flags=re.DOTALL | re.I
    )

    # 3. Breadcrumb category links:
    # <a class="text-zinc-700 hover:text-emerald-600 transition-colors" href="/(startup|registrations|mca-services|trademark|income-tax|gst|hr-services|close-business|consultation)">Text</a>
    def repl_breadcrumb(m):
        inner = m.group(1)
        changes.append(f"Converted breadcrumb category link to span: {inner}")
        return f'<span class="text-zinc-700">{inner}</span>'

    content = re.sub(
        r'<a\b[^>]*\bclass=[\"\']text-zinc-700 hover:text-emerald-600 transition-colors[\"\'][^>]*\bhref=[\"\']/(?:startup|registrations|mca-services|trademark|income-tax|gst|hr-services|close-business|consultation)[\"\'][^>]*>(.*?)</a>',
        repl_breadcrumb,
        content,
        flags=re.DOTALL | re.I
    )

    # 4. Footer links:
    # 12 items: /about-us, /learn, /contact-us, /founders-guide, /search, /developers, /termsconditions, /privacypolicy, /refund-policy, /confidentiality-policy, /disclaimer, /review
    broken_footer_slugs = r'(?:about-us|learn|contact-us|founders-guide|search|developers|termsconditions|privacypolicy|refund-policy|confidentiality-policy|disclaimer|review)'
    
    def repl_footer_li(m):
        full_li = m.group(0)
        # extract text inside <span class="group-hover:text-blue-600">Text</span> or general text inside <a>
        text_m = re.search(r'<span class=[\"\']group-hover:text-blue-600[\"\']>(.*?)</span>', full_li, re.DOTALL | re.I)
        if text_m:
            link_text = text_m.group(1).strip()
        else:
            a_m = re.search(r'<a\b[^>]*>(.*?)</a>', full_li, re.DOTALL | re.I)
            link_text = re.sub(r'<[^>]+>', '', a_m.group(1)).strip() if a_m else ""
            
        changes.append(f"Converted footer link to text span: {link_text}")
        return f'<li><span class="relative inline-block" style="font-size:15px;font-weight:400;line-height:23px;color:#6b7280">{link_text}</span></li>'

    footer_li_pattern = re.compile(rf'<li>\s*<a\b[^>]*\bhref=[\"\']/{broken_footer_slugs}[\"\'][^>]*>.*?</a>\s*</li>', re.DOTALL | re.I)
    content = footer_li_pattern.sub(repl_footer_li, content)

    # 5. General check for any remaining <a> pointing to non-existent pages in editorial text
    # Exclude external links, hashes, javascript, tel, mailto
    def repl_general_broken_a(m):
        full_tag = m.group(0)
        attrs = m.group(1)
        inner = m.group(2)
        hm = re.search(r'href=[\"\']([^\"\']*)[\"\']', attrs)
        if not hm:
            return full_tag
        href = hm.group(1).strip()
        h_lower = href.lower()
        if not href or h_lower.startswith('#') or h_lower.startswith('http://') or h_lower.startswith('https://') or h_lower.startswith('//') or h_lower.startswith('tel:') or h_lower.startswith('mailto:') or h_lower.startswith('javascript:'):
            return full_tag
        clean = href.split('#')[0].split('?')[0].strip().lstrip('/').lstrip('./')
        if not clean:
            clean = 'index.html'
        elif not clean.endswith('.html'):
            clean = clean.rstrip('/') + '.html'
        basename = os.path.basename(clean)
        if basename not in valid_pages:
            # Broken editorial link: strip <a> tag per Rule 2, preserving inner visible text
            changes.append(f"Unwrapped broken editorial link {href} -> {inner}")
            return inner
        return full_tag

    content = re.sub(r'<a\b([^>]*)>(.*?)</a>', repl_general_broken_a, content, flags=re.DOTALL | re.I)

    return content, changes

# Execute across all production files
total_files_modified = 0
all_changes_summary = Counter()

for filename in production_files:
    fpath = os.path.join(PAGES_DIR, filename)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content, changes = clean_html_content(content, filename)
    if new_content != content:
        total_files_modified += 1
        for c in changes:
            # summarize category
            cat = c.split(':')[0]
            all_changes_summary[cat] += 1
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)

print(f"\nSuccessfully cleaned {total_files_modified} files.")
print("Summary of actions performed:")
for cat, count in all_changes_summary.most_common():
    print(f"  {count:4d}x {cat}")

# Also clean templates/partials/footer.html if it exists
tpl_footer = os.path.join(PAGES_DIR, 'templates', 'partials', 'footer.html')
if os.path.exists(tpl_footer):
    with open(tpl_footer, 'r', encoding='utf-8') as f:
        c = f.read()
    new_c, changes = clean_html_content(c, 'footer.html')
    if new_c != c:
        with open(tpl_footer, 'w', encoding='utf-8') as f:
            f.write(new_c)
        print("Updated templates/partials/footer.html")

# Also clean templates/service_page.html if it exists
tpl_sp = os.path.join(PAGES_DIR, 'templates', 'service_page.html')
if os.path.exists(tpl_sp):
    with open(tpl_sp, 'r', encoding='utf-8') as f:
        c = f.read()
    new_c, changes = clean_html_content(c, 'service_page.html')
    if new_c != c:
        with open(tpl_sp, 'w', encoding='utf-8') as f:
            f.write(new_c)
        print("Updated templates/service_page.html")
