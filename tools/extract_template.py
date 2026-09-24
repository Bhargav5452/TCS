import bs4
import json
import re
import os

with open('d:/user/TCS_website/proprietorship.html', encoding='utf-8') as f:
    html_content = f.read()

soup = bs4.BeautifulSoup(html_content, 'html.parser')

# 1. Title & Meta
title_tag = soup.find('title')
if title_tag:
    title_tag.string = "{{ page.meta_title }}"

meta_desc = soup.find('meta', attrs={'name': 'description'})
if meta_desc:
    meta_desc['content'] = "{{ page.meta_description }}"

# 2. Hero Section
# The hero section has the H1
h1 = soup.find('h1')
if h1:
    h1.string = "{{ page.hero_title }}"
    
    # Description is usually the paragraph immediately following
    hero_p = h1.find_next_sibling('p')
    if hero_p:
        hero_p.string = "{{ page.hero_description }}"

# Price in Hero (Assuming ₹1,499 is there)
price_spans = soup.find_all(string=re.compile(r'1,499'))
for s in price_spans:
    s.replace_with(s.replace('1,499', '{{ page.price }}'))

# Breadcrumbs
# Find the breadcrumb nav
navs = soup.find_all('nav', attrs={'aria-label': 'Breadcrumb'})
if navs:
    breadcrumb_ol = navs[0].find('ol')
    if breadcrumb_ol:
        breadcrumb_ol.clear()
        breadcrumb_ol.append(bs4.BeautifulSoup("""
        {% for crumb in page.breadcrumbs %}
            <li class="flex items-center">
                {% if loop.index0 > 0 %}
                <svg class="h-4 w-4 flex-shrink-0 text-text-muted mx-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
                {% endif %}
                <a href="{{ crumb.url }}" class="text-sm font-medium {% if loop.last %}text-brand pointer-events-none{% else %}text-text-secondary hover:text-brand transition-colors{% endif %}" {% if loop.last %}aria-current="page"{% endif %}>{{ crumb.name }}</a>
            </li>
        {% endfor %}
        """, 'html.parser'))

# 3. Main Content Card
main_card = soup.find(id='custom-main-card')
if main_card:
    inner = main_card.find(id='custom-card-inner')
    if inner:
        # Extract the original content for proprietorship.json
        proprietorship_content = inner.decode_contents()
        
        inner.clear()
        inner.append(bs4.BeautifulSoup("{{ page.main_content | safe }}", 'html.parser'))

# 4. FAQ Section
faq_container = soup.find(id='custom-faq-container')
if faq_container:
    subtitle = faq_container.find('p', class_='ifcFaqSubtitle')
    if subtitle:
        subtitle.string = "Common questions about {{ page.hero_title }}."
        
    grid = faq_container.find('div', class_='ifcFaqGrid')
    if grid:
        # Extract the original FAQs
        cards = grid.find_all('div', class_='ifcFaqCard')
        extracted_faqs = []
        for c in cards:
            q = c.find(class_='ifcFaqCardQ').get_text(strip=True)
            a_div = c.find('div', class_='ifcFaqCardA')
            a_html = a_div.decode_contents() if a_div else ""
            extracted_faqs.append({'question': q, 'answer': a_html})
            
        grid.clear()
        grid.append(bs4.BeautifulSoup("""
        {% for faq in page.faqs %}
        <div class="ifcFaqCard">
            <button aria-controls="faq-answer-{{ loop.index }}" aria-expanded="false" class="ifcFaqCardBtn" type="button">
                <span class="ifcFaqCardQ">{{ faq.question }}</span>
                <svg aria-hidden="true" class="lucide lucide-chevron-down ifcFaqCardChevron" fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="m6 9 6 6 6-6"></path></svg>
            </button>
            <div aria-labelledby="faq-heading-{{ loop.index }}" class="overflow-hidden transition-[grid-template-rows] duration-300 grid grid-rows-[0fr]" id="faq-answer-{{ loop.index }}" role="region" style="grid-template-rows: 0fr;">
                <div class="min-h-0">
                    <div class="ifcFaqCardA">{{ faq.answer | safe }}</div>
                </div>
            </div>
        </div>
        {% endfor %}
        """, 'html.parser'))

# 5. Related Services
related_container = soup.find(id='related-services')
if related_container:
    # Instead of rewriting, just let it use Jinja for the active state
    pills_div = related_container.find('div', class_='flex-wrap')
    if pills_div:
        pills_div.clear()
        pills_div.append(bs4.BeautifulSoup("""
        {% for service in site.related_services %}
            <a href="{{ service.url }}" class="inline-flex items-center rounded-lg border {% if service.id == page.id %}border-green-200 bg-brand-light text-brand-hover pointer-events-none{% else %}border-border bg-background text-text-secondary hover:border-gray-300 hover:bg-surface-hover hover:text-text{% endif %} px-3 py-1.5 text-[13px] font-medium transition-colors" {% if service.id == page.id %}aria-current="page"{% endif %}>
                {{ service.name }}
            </a>
        {% endfor %}
        """, 'html.parser'))

# Create data directory if it doesn't exist
os.makedirs('d:/user/TCS_website/data', exist_ok=True)

# Write base.html
with open('d:/user/TCS_website/templates/service_page.html', 'w', encoding='utf-8') as f:
    # Fix the brackets mapping since python bs4 might escape jinja tags
    out = str(soup)
    out = out.replace('&lt;%', '{%').replace('%&gt;', '%}').replace('&lt;{', '{{').replace('}&gt;', '}}')
    f.write(out)

# Write proprietorship.json
data = {
    "id": "proprietorship",
    "meta_title": "Solo Proprietorship Company Registration Online in India - Starts ₹1,499",
    "meta_description": "Register your sole proprietorship online in India with a simple process, complete documents checklist, registration fees, compliance requirements, and expert support.",
    "hero_title": "Proprietorship Registration in India",
    "hero_description": "A sole proprietorship is a business owned, managed, and controlled by a single individual. It is one of the most common and simplest forms of business in India, ideal for micro and small enterprises. TCS provides expert guidance for Sole Proprietorship Company Registration.",
    "price": "1,499",
    "breadcrumbs": [
        {"name": "Home", "url": "/"},
        {"name": "Registrations", "url": "/registrations"},
        {"name": "Proprietorship", "url": "/proprietorship"}
    ],
    "main_content": proprietorship_content,
    "faqs": extracted_faqs
}

with open('d:/user/TCS_website/data/proprietorship.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("Extraction complete. Templates and JSON saved.")
