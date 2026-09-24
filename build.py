import os
import re
import sys
import urllib.parse
from bs4 import BeautifulSoup

def clean_html(raw_file, out_file):
    if not os.path.exists(raw_file):
        print(f"Skipping {raw_file} - not found.")
        return
        
    with open(raw_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Text Replacements (IndiaFilings -> TCS)
    copy_replacements = {
        "IndiaFilings": "Tirumala Consultancy Services",
        "indiafilings": "tirumalaconsultancy",
        "India's Largest AI-Powered Corporate Services & Compliance Platform": "Strategic Corporate Services & Compliance Platform",
        "Join millions who trust IndiaFilings": "Join thousands who trust TCS",
        "Lionel Charles": "TCS Team"
    }

    # 1. Remove Next.js Scripts and JSON-LD
    for script in soup.find_all('script'):
        src = script.get('src', '')
        if '/_next/' in src or 'googletagmanager' in src or 'google-analytics' in src or 'GTM-' in src:
            script.decompose()
            continue
        if script.get('type') == 'application/ld+json' or script.get('id') == '__NEXT_DATA__':
            script.decompose()
            continue
        # Decompose inline next js scripts
        if script.string and ('__next_s' in script.string or 'googletagmanager' in script.string or 'GTM-' in script.string):
            script.decompose()
            continue

    # Remove noscript tags (GTM usually uses these)
    for noscript in soup.find_all('noscript'):
        noscript.decompose()

    # 2. Localize CSS
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href', '')
        if href:
            filename = href.split('/')[-1]
            if not filename.endswith('.css'):
                filename += '.css'
            link['href'] = f'./css/{filename}'
            # Remove crossorigin
            if link.has_attr('crossorigin'):
                del link['crossorigin']

    # 3. Localize Images
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            # Handle next/image
            if src.startswith('/_next/image'):
                parsed = urllib.parse.urlparse(src)
                query = urllib.parse.parse_qs(parsed.query)
                if 'url' in query:
                    actual_url = query['url'][0]
                    filename = actual_url.split('/')[-1].split('?')[0]
                else:
                    filename = "image.png"
            else:
                filename = src.split('/')[-1].split('?')[0]
                
            if filename:
                img['src'] = f'./images/{filename}'
                
        # Strip srcset to force loading the local src
        if img.has_attr('srcset'):
            del img['srcset']
        # beautifulsoup converts attributes to lowercase, but let's be safe
        if img.has_attr('srcSet'):
            del img['srcSet']

    # Localize preload images
    for link in soup.find_all('link', rel='preload', as_='image'):
        if link.has_attr('imagesrcset'):
            del link['imagesrcset']
        href = link.get('href', '')
        if href:
            filename = href.split('/')[-1].split('?')[0]
            link['href'] = f'./images/{filename}'

    # 4. Text Replacements in DOM
    # Replace in text nodes
    for el in soup.find_all(string=True):
        if el.parent.name not in ['script', 'style']:
            original = el.string
            changed = False
            for old_text, new_text in copy_replacements.items():
                if old_text in original:
                    original = original.replace(old_text, new_text)
                    changed = True
            if changed:
                el.replace_with(original)
                    
    # Replace the logo image source and adjust sizing
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if 'logo-110x52.png' in src:
            img['src'] = './images/tcs_logo.png'
            # Adjust classes to prevent squishing the new logo and make it larger
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

    # Update global image alt and title tags
    for img in soup.find_all('img'):
        if img.has_attr('alt') and 'IndiaFilings' in img['alt']:
            img['alt'] = img['alt'].replace('IndiaFilings', 'TCS')
        if img.has_attr('title') and 'IndiaFilings' in img['title']:
            img['title'] = img['title'].replace('IndiaFilings', 'TCS')
            
        # Also clean up any lingering srcset that might load original images
        if img.has_attr('srcset'):
            del img['srcset']

    # Replace specific logo in the AI Compliance Cloud card with favicon
    for small in soup.find_all('small'):
        if 'AI COMPLIANCE CLOUD' in small.get_text() or 'AI COMPLIANCE' in small.get_text().upper():
            parent = small.find_parent('div')
            if parent:
                logo = parent.find('img')
                if logo:
                    logo['src'] = './images/tcs_favicon.png'
                    # Reset any custom sizing applied globally
                    if logo.has_attr('class'):
                        classes = ' '.join(logo['class'])
                        classes = classes.replace('w-auto', '')
                        classes = classes.replace('h-16', '')
                        classes = classes.replace('sm:h-16', '')
                    # Center the logo, make background light, and decrease size by 30% (from 128px to ~90px)
                    # Since Tailwind classes might not be compiled in the static bundle, we use explicit inline styles
                    logo['style'] = "width: 90px !important; height: 90px !important; object-fit: contain;"
                    
                    # Ensure parent is flex center to center the logo after removing the text
                    parent_classes = parent.get('class', [])
                    if 'flex' not in parent_classes:
                        parent_classes.append('flex')
                    if 'items-center' not in parent_classes:
                        parent_classes.append('items-center')
                    if 'justify-center' not in parent_classes:
                        parent_classes.append('justify-center')
                    parent['class'] = parent_classes
                    
                    # Override the background color to match the user's specific dark color request
                    # Removing background-image ensures any existing dark gradients are hidden
                    parent['style'] = "background-color: #071A2D !important; background-image: none !important;"
                    
                    # Remove the small text
                    small.decompose()

    # Replace favicon
    for link in soup.find_all('link'):
        rel = link.get('rel', [])
        if isinstance(rel, str):
            rel = [rel]
        # Check if any element in rel contains 'icon'
        if any('icon' in r.lower() for r in rel):
            link['href'] = './images/tcs_favicon.png'

    # Remove specific navigation links
    for a in soup.find_all('a', href=True):
        if '/careers' in a['href'] or '/referral' in a['href']:
            a.decompose()
            
    # Replace Login with Talk to experts
    for btn in soup.find_all('button'):
        if btn.string and 'Login' in btn.string:
            btn.string = btn.string.replace('Login', 'Talk to experts')
            # Adjust padding to accommodate the longer text without breaking the layout
            if btn.has_attr('class'):
                classes = ' '.join(btn['class'])
                classes = classes.replace('px-5', 'px-4')
                classes = classes.replace('py-2.5', 'py-2')
                btn['class'] = classes.split(' ')

    # Inject Original IndiaFilings Mega Menus for Navbar
    import json
    try:
        with open('menus_fixed.json', 'r', encoding='utf-8') as f:
            scraped_menus = json.load(f)
    except Exception:
        scraped_menus = {}
        
    nav = soup.find('nav')
    if nav:
        for a in nav.find_all('a', href=True):
            href = a['href']
            if href in scraped_menus:
                # Disable the top-level link so it doesn't redirect when clicked
                a['href'] = 'javascript:void(0)'
                
                parent = a.find_parent('div')
                if parent:
                    # Add group class for hover
                    classes = parent.get('class', [])
                    if 'group' not in classes:
                        classes.append('group')
                        parent['class'] = classes
                    
                    # Ensure parent has relative class
                    if 'relative' not in classes:
                        classes.append('relative')
                        parent['class'] = classes
                        
                    raw_html = scraped_menus[href]
                    
                    # Apply branding replacements directly to the raw HTML string
                    for old_text, new_text in copy_replacements.items():
                        raw_html = raw_html.replace(old_text, new_text)
                        
                    # Parse the injected HTML
                    dropdown_soup = BeautifulSoup(raw_html, 'html.parser')
                    
                    # Find the mega menu wrapper (which has absolute top-full) and add tailwind hover classes
                    for div in dropdown_soup.find_all('div', class_=True):
                        if 'absolute' in div.get('class', []) and 'top-full' in div.get('class', []):
                            # Add group-hover:block or group-hover:visible
                            div_classes = div.get('class', [])
                            if 'z-[130]' in div_classes or 'w-auto' in div_classes:
                                # This is the actual mega menu box
                                if 'hidden' not in div_classes:
                                    div_classes.append('hidden')
                                div_classes.append('group-hover:block')
                                div['class'] = div_classes

                    parent.clear()
                    # Append all children from the parsed soup
                    for child in list(dropdown_soup.children):
                        parent.append(child)

    # Globally disable ALL main category links across the entire site to prevent accidental redirects
    if scraped_menus:
        for a in soup.find_all('a', href=True):
            if a['href'] in scraped_menus.keys():
                a['href'] = 'javascript:void(0)'
                classes = a.get('class', [])
                if 'cursor-pointer' not in classes:
                    classes.append('cursor-pointer')
                    a['class'] = classes
            
    # Remove Customer Stories / Video section
    import re
    cs = soup.find(string=re.compile('Customer stories', re.I))
    if cs:
        parent_section = cs.find_parent('section')
        if parent_section:
            parent_section.decompose()
        elif cs.find_parent('div'):
            # Fallback if there is no section tag, just remove the top-level div wrapper
            p = cs
            while p.parent and p.parent.name != 'body':
                if 'container' in p.parent.get('class', []) or p.parent.name == 'section':
                    p.parent.decompose()
                    break
                p = p.parent

    # Remove Lead Capture Form / "Start Your" sections across service pages
    start_heading = soup.find(string=re.compile(r'^Start Your ', re.I))
    if start_heading:
        h2 = start_heading.find_parent('h2')
        if h2:
            section = h2.find_parent('section')
            if section:
                section.decompose()

    # Layout Restructuring: Convert grid to single column, remove sidebar, add top spacing
    grid = soup.find('div', class_=lambda c: c and 'lg:grid-cols-[1fr_0.3fr]' in c)
    if grid:
        # 1. Change grid to single column
        classes = ' '.join(grid['class'])
        classes = classes.replace('lg:grid-cols-[1fr_0.3fr]', 'lg:grid-cols-1')
        grid['class'] = classes.split(' ')
        
        # 2. Decompose the sidebar (second child)
        children = [child for child in grid.children if child.name == 'div']
        if len(children) > 1:
            children[1].decompose()
            
        # 3. Add top padding to the hero wrapper (which is a section)
        # We find the true hero section
        hero_h2 = soup.find('h2', id='hero-title-proprietor')
        if hero_h2:
            hero_section = hero_h2.find_parent('section')
            if hero_section:
                hero_section['style'] = 'padding-top: 90px !important; padding-bottom: 12px !important;' # Reduced by ~45px
                
        # Completely remove the redundant H1 inside the page content
        redundant_h1 = soup.find('h1')
        if redundant_h1:
            redundant_p = redundant_h1.find_next_sibling('p')
            redundant_h1.decompose()
            if redundant_p:
                redundant_p.decompose()

        # Style breadcrumbs
        breadcrumb_nav = soup.find('nav', class_=lambda c: c and 'gap-2' in c and 'text-zinc-600' in c)
        if breadcrumb_nav:
            breadcrumb_nav['id'] = 'custom-breadcrumb'
            
        # Target the main card container for unified width
        wrapper = grid.find_parent('div', class_=lambda c: c and 'relative' in c and 'mx-auto' in c)
        if wrapper:
            wrapper['id'] = 'custom-main-container'
            wrapper['style'] = 'padding-bottom: 24px !important;'
            # Remove the top padding we added previously, as we now put it on the hero section
            classes = ' '.join(wrapper.get('class', []))
            classes = re.sub(r'pt-\d+', '', classes)
            classes = re.sub(r'sm:pt-\d+', '', classes)
            classes = re.sub(r'md:pt-\d+', '', classes)
            wrapper['class'] = [c for c in classes.split(' ') if c]
            if wrapper.has_attr('style'):
                del wrapper['style']
            classes = re.sub(r'sm:pt-\d+', '', classes)
            classes = re.sub(r'md:pt-\d+', '', classes)
            wrapper['class'] = [c for c in classes.split(' ') if c]
            if wrapper.has_attr('style'):
                del wrapper['style']
                
        # Target the inner card for padding adjustments
        card = grid.find('div', class_=lambda c: c and 'overflow-hidden' in c and 'rounded-xl' in c)
        if card:
            card['id'] = 'custom-main-card'
            inner_padding_div = card.find('div', class_=lambda c: c and 'p-4' in c)
            if inner_padding_div:
                inner_padding_div['id'] = 'custom-card-inner'

        # Target the FAQ section for unified width
        faq_section = soup.find('section', id='faq-section')
        if faq_section:
            faq_section['id'] = 'custom-faq-container'
            
            # --- CREATE RELATED SERVICES SECTION ---
            related_section = soup.new_tag('section', attrs={'class': 'py-8', 'id': 'related-services'})
            related_container = soup.new_tag('div', attrs={'class': 'mx-auto', 'style': 'width: min(1480px, calc(100% - 120px)); max-width: none;'})
            
            # Using Tirumala's rounded-2xl for main cards
            card_div = soup.new_tag('div', attrs={'class': 'bg-white border border-gray-200 rounded-2xl mb-8'})
            
            # Header matching reference hierarchy but with Tirumala font sizes
            header_div = soup.new_tag('div', attrs={'class': 'border-b border-gray-100 px-6 py-4'})
            heading = soup.new_tag('h3', attrs={'class': 'text-[15px] font-medium text-gray-900'})
            heading.string = 'Related Services - Business Registration'
            header_div.append(heading)
            card_div.append(header_div)
            
            # Pills container
            pills_div = soup.new_tag('div', attrs={'class': 'p-6 flex flex-wrap gap-2.5'})
            
            services_data = [
                ("Company Registration", "/company-registration", False),
                ("OPC Registration", "/one-person-company", False),
                ("Partnership Firm Registration", "/partnership", False),
                ("Private Limited Company", "/private-limited-company", False),
                ("Section 8 Company", "/section-8-company-registration", False),
                ("India Business Setup", "/indian-subsidiary", False),
                ("LLP Registration", "/llp-registration", False),
                ("Virtual Office Address", "/virtual-office", False),
                ("Proprietorship", "/proprietorship", True), # Active Item
                ("Public Limited Company", "/public-limited-company", False),
                ("Producer Company", "/producer-company-registration", False),
                ("Pitch Deck", "/pitch-deck", False)
            ]
            
            for title, link, is_active in services_data:
                pill = soup.new_tag('a', attrs={'href': link})
                pill.string = title
                
                if is_active:
                    pill['class'] = 'inline-flex items-center rounded-lg border border-green-200 bg-green-50 px-3 py-1.5 text-[13px] font-medium text-green-700 pointer-events-none'
                    pill['aria-current'] = 'page'
                else:
                    pill['class'] = 'inline-flex items-center rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-[13px] font-medium text-gray-700 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:text-gray-900'
                
                pills_div.append(pill)
                
            card_div.append(pills_div)
            related_container.append(card_div)
            related_section.append(related_container)
            
            faq_section.insert_after(related_section)

        # --- FAQ DATA EXTRACTION & INJECTION ---
        # Extract FAQ answers from the __next_f RSC payload
        scripts = soup.find_all('script')
        next_data = ''
        for s in scripts:
            if s.string and 'self.__next_f.push' in s.string:
                next_data += s.string

        start_idx = next_data.find('\\"faqs\\":[')
        if start_idx != -1:
            data_substr = next_data[start_idx + len('\\"faqs\\":'):]
            bracket_count = 0
            end_idx = 0
            for i, char in enumerate(data_substr):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
            array_str = data_substr[:end_idx]
            clean_str = array_str.replace('\\\\', '\\').replace('\\"', '"').replace('\\n', '\\\\n').replace('\\t', '\\\\t')
            try:
                faqs = json.loads(clean_str)
                # Inject the answers into the DOM
                for faq in faqs:
                    faq_id = faq.get('id')
                    answer_text = faq.get('answer', '')
                    if faq_id and answer_text:
                        ans_div = soup.find('div', id=f'faq-answer-{faq_id}')
                        if ans_div:
                            # Create inner wrapper for smooth animation
                            inner_div = soup.new_tag('div', attrs={'class': 'overflow-hidden', 'style': 'min-height: 0;'})
                            # Match IndiaFilings reference exactly using ifcFaqCardA
                            text_div = soup.new_tag('div', attrs={'class': 'ifcFaqCardA break-words whitespace-normal'})
                            # Parse answer as HTML so tags (if any) render properly
                            parsed_ans = BeautifulSoup(answer_text, 'html.parser')
                            text_div.append(parsed_ans)
                            inner_div.append(text_div)
                            ans_div.append(inner_div)
            except Exception as e:
                print(f"Error parsing FAQ JSON: {e}")

    # Remove "Watch the Video" section
    wv = soup.find(string=re.compile('Watch the Video', re.I))
    if wv:
        parent_section = wv.find_parent('section')
        if parent_section:
            parent_section.decompose()
        elif wv.find_parent('div'):
            p = wv
            while p.parent and p.parent.name != 'body':
                if 'container' in p.parent.get('class', []) or p.parent.name == 'section':
                    p.parent.decompose()
                    break
                p = p.parent

    # Replace in attributes
    for meta in soup.find_all('meta'):
        if meta.has_attr('content'):
            for old_text, new_text in copy_replacements.items():
                if old_text in meta['content']:
                    meta['content'] = meta['content'].replace(old_text, new_text)
                    
    for title in soup.find_all('title'):
        if title.string:
            for old_text, new_text in copy_replacements.items():
                if old_text in title.string:
                    title.string = title.string.replace(old_text, new_text)
                    
    # Remove template tags that NextJS uses for hydration which can cause issues
    for template in soup.find_all('template'):
        template.decompose()

    # Inject Google Fonts for Inter, since NextJS local fonts might be broken offline
    google_fonts = soup.new_tag("link", rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap")
    preconnect1 = soup.new_tag("link", rel="preconnect", href="https://fonts.googleapis.com")
    preconnect2 = soup.new_tag("link", rel="preconnect", href="https://fonts.gstatic.com", crossorigin="anonymous")
    
    # Increase overall font size by 2px (by changing the base rem size from 16px to 18px)
    # Also inject necessary hover classes for the new dropdowns that are missing from original Tailwind bundle
    font_style = soup.new_tag("style")
    font_style.string = """
    html, body { 
        font-size: 18px !important; 
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }
    .group:hover .group-hover\\:block { display: block !important; }
    .group:hover .group-hover\\:opacity-100 { opacity: 1 !important; }
    
    /* Layout Redesign Styles */
    #custom-breadcrumb {
        font-size: 14px !important;
        gap: 10px !important;
        margin-bottom: 24px !important;
    }
    #custom-breadcrumb a, #custom-breadcrumb span {
        color: #9ca3af !important; /* subtle muted gray */
    }
    #custom-breadcrumb span:last-child {
        color: #059669 !important; /* stronger green */
        font-weight: 500 !important;
    }
    
    /* Unified Container Widths for Main Card and FAQ */
    #custom-main-container, #custom-faq-container {
        width: min(1480px, calc(100% - 120px)) !important;
        margin: 0 auto !important;
        max-width: none !important; /* Override tailwind max-w */
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    #custom-main-card {
        border-radius: 22px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
    }
    #custom-card-inner {
        padding: 42px 48px 52px !important;
    }
    
    /* FAQ Specific Refinements */
    #custom-faq-container {
        margin-top: 0px !important;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        #custom-main-container, #custom-faq-container {
            width: calc(100% - 32px) !important;
        }
        #custom-card-inner {
            padding: 24px 20px 32px !important;
        }
    }
    """
    if soup.head:
        soup.head.insert(0, preconnect1)
        soup.head.insert(1, preconnect2)
        soup.head.insert(2, google_fonts)
        soup.head.append(font_style)

    # Inject robust vanilla JS to handle scroll animations
    scroll_script = soup.new_tag("script")
    scroll_script.string = """
    (function() {
        // Scroll Intersection Observer
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('opacity-100', 'translate-y-0');
                    entry.target.classList.remove('opacity-0', 'translate-y-8');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.ifcFeatureCard, .ifcProcessCard').forEach(el => {
            el.classList.add('opacity-0', 'translate-y-8', 'transition-all', 'duration-700', 'ease-out');
            observer.observe(el);
        });

        // Main Card one-time entrance animation with intersection observer
        const mainCard = document.getElementById('custom-main-card');
        if (mainCard) {
            mainCard.style.opacity = '0';
            mainCard.style.transform = 'translateY(15px)';
            mainCard.style.transition = 'opacity 600ms ease-out, transform 600ms ease-out';
            
            const cardObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                        cardObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.05 }); // Small threshold so it triggers early
            
            cardObserver.observe(mainCard);
        }

        // FAQ Accordion & Load More Logic
        const faqCards = document.querySelectorAll('.ifcFaqCard');
        const loadMoreBtn = document.querySelector('.ifcFaqBtnPrimary'); // Fixed selector to match the actual button class
        let visibleCount = 6;

        // Initialize visibility
        faqCards.forEach((card, index) => {
            if (index >= visibleCount) {
                card.style.display = 'none';
            }
            
            const btn = card.querySelector('.ifcFaqCardBtn');
            const answer = card.querySelector('[role="region"]');
            const chevron = card.querySelector('.ifcFaqCardChevron');
            
            if (btn && answer && chevron) {
                btn.addEventListener('click', () => {
                    const isExpanded = btn.getAttribute('aria-expanded') === 'true';
                    
                    // Close all others
                    document.querySelectorAll('.ifcFaqCardBtn').forEach(otherBtn => {
                        if (otherBtn !== btn) {
                            otherBtn.setAttribute('aria-expanded', 'false');
                            const otherAns = document.getElementById(otherBtn.getAttribute('aria-controls'));
                            const otherChev = otherBtn.querySelector('.ifcFaqCardChevron');
                            const otherCard = otherBtn.closest('.ifcFaqCard');
                            if (otherAns) otherAns.style.gridTemplateRows = '0fr';
                            if (otherChev) otherChev.classList.remove('ifcFaqCardChevronOpen');
                            if (otherCard) otherCard.classList.remove('ifcFaqCardOpen');
                        }
                    });

                    // Toggle current
                    btn.setAttribute('aria-expanded', !isExpanded);
                    answer.style.gridTemplateRows = isExpanded ? '0fr' : '1fr';
                    if (isExpanded) {
                        chevron.classList.remove('ifcFaqCardChevronOpen');
                        card.classList.remove('ifcFaqCardOpen');
                    } else {
                        chevron.classList.add('ifcFaqCardChevronOpen');
                        card.classList.add('ifcFaqCardOpen');
                    }
                });
            }
        });

        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                const isExpanded = visibleCount > 6;
                
                if (isExpanded) {
                    // Collapse back to 6
                    visibleCount = 6;
                    loadMoreBtn.innerText = 'Load more questions';
                } else {
                    // Expand all
                    visibleCount = faqCards.length;
                    loadMoreBtn.innerText = 'Show less';
                }
                
                faqCards.forEach((card, index) => {
                    if (index < visibleCount) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                        // Clean up expanded state for hidden cards
                        const btn = card.querySelector('.ifcFaqCardBtn');
                        const answer = card.querySelector('[role="region"]');
                        const chevron = card.querySelector('.ifcFaqCardChevron');
                        if (btn) btn.setAttribute('aria-expanded', 'false');
                        if (answer) answer.style.gridTemplateRows = '0fr';
                        if (chevron) chevron.classList.remove('ifcFaqCardChevronOpen');
                        card.classList.remove('ifcFaqCardOpen');
                    }
                });
            });
        }
    })();
    """
    # Inject Custom Tailwind Theme & CSS Variables (Semantic Tokens)
    theme_script = soup.new_tag('script')
    theme_script.string = """
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            brand: {
              DEFAULT: 'var(--color-brand)',
              hover: 'var(--color-brand-hover)',
              light: 'var(--color-brand-light)'
            },
            accent: 'var(--color-accent)',
            background: 'var(--color-background)',
            surface: {
              DEFAULT: 'var(--color-surface)',
              hover: 'var(--color-surface-hover)'
            },
            border: {
              DEFAULT: 'var(--color-border)',
              subtle: 'var(--color-border-subtle)'
            },
            text: {
              DEFAULT: 'var(--color-text)',
              secondary: 'var(--color-text-secondary)',
              muted: 'var(--color-text-muted)'
            },
            success: 'var(--color-success)',
            warning: 'var(--color-warning)',
            error: 'var(--color-error)'
          }
        }
      }
    }
    """
    if soup.head:
        soup.head.append(theme_script)

    style_tag = soup.new_tag('style')
    style_tag.string = """
    :root {
        --color-brand: #10b981;
        --color-brand-hover: #059669;
        --color-brand-light: #ecfdf5;
        --color-accent: #0ea5e9;
        
        --color-background: #f9fafb;
        --color-surface: #ffffff;
        --color-surface-hover: #f3f4f6;
        
        --color-border: #e5e7eb;
        --color-border-subtle: #f3f4f6;
        
        --color-text: #111827;
        --color-text-secondary: #374151;
        --color-text-muted: #6b7280;
        
        --color-success: #10b981;
        --color-warning: #f59e0b;
        --color-error: #ef4444;
    }
    """
    if soup.head:
        soup.head.append(style_tag)

    if soup.body:
        soup.body.append(scroll_script)

    # Convert to string and apply global semantic mapping
    html_str = str(soup)
    import re
    
    # 1. Backgrounds & Surfaces
    html_str = re.sub(r'\bbg-(gray|zinc|slate)-50\b', 'bg-background', html_str)
    html_str = re.sub(r'\bbg-(gray|zinc|slate)-100\b', 'bg-surface-hover', html_str)
    
    # 2. Text
    html_str = re.sub(r'\btext-(gray|zinc|slate)-900\b', 'text-text', html_str)
    html_str = re.sub(r'\btext-(gray|slate|zinc)-700\b', 'text-text-secondary', html_str)
    html_str = re.sub(r'\btext-(gray|zinc|slate)-500\b', 'text-text-muted', html_str)
    html_str = re.sub(r'\btext-(gray|zinc|slate)-400\b', 'text-text-muted', html_str) # group muted
    
    # 3. Borders
    html_str = re.sub(r'\bborder-(gray|zinc|slate)-200\b', 'border-border', html_str)
    html_str = re.sub(r'\bborder-(gray|zinc|slate)-100\b', 'border-border-subtle', html_str)
    html_str = html_str.replace('border-[#e5e7eb]', 'border-border')
    html_str = html_str.replace('border-[#f3f4f6]', 'border-border-subtle')
    
    # 4. Brand
    html_str = re.sub(r'\bbg-(green|emerald|teal)-500\b', 'bg-brand', html_str)
    html_str = re.sub(r'\btext-(green|emerald|teal)-500\b', 'text-brand', html_str)
    html_str = re.sub(r'\btext-(green|emerald|teal)-600\b', 'text-brand-hover', html_str)
    html_str = re.sub(r'\btext-(green|emerald|teal)-700\b', 'text-brand-hover', html_str)
    html_str = re.sub(r'\bbg-(green|emerald)-50\b', 'bg-brand-light', html_str)
    
    # 5. Accent
    html_str = re.sub(r'\b(text|bg|border)-(blue|sky)-(500|600)\b', r'\1-accent', html_str)
    
    # 6. Highlights & Warnings (Hardcoded Hex mappings)
    html_str = html_str.replace('bg-[#FFF7ED]', 'bg-warning/10')
    html_str = html_str.replace('bg-[#FFFBEB]', 'bg-warning/10')
    html_str = html_str.replace('text-[#EA580C]', 'text-warning')
    html_str = html_str.replace('text-[#D97706]', 'text-warning')
    html_str = html_str.replace('bg-[#FFF1F2]', 'bg-error/10')
    html_str = html_str.replace('text-[#E11D48]', 'text-error')
    
    # Hex fix for replaced texts
    html_str = html_str.replace('text-[#374151]', 'text-text-secondary')
    html_str = html_str.replace('text-[#4b5563]', 'text-text-muted')

    # Save
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html_str)
    print(f"Built {out_file} from {raw_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build.py <input_raw.html> <output.html>")
        sys.exit(1)
    clean_html(sys.argv[1], sys.argv[2])
