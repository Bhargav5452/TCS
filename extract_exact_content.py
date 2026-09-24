import bs4
import json
import os

files_map = {
    'plc_raw.html': 'private-limited-company.json',
    'publc_raw.html': 'public-limited-company.json',
    'opc_raw.html': 'one-person-company.json',
    'llp_raw.html': 'llp-registration.json'
}

copy_replacements = {
    'IndiaFilings': 'Tirumala Consultancy Services',
    'indiafilings': 'tirumalaconsultancy',
}

BASE = 'd:/user/TCS_website'

for raw_html_file, json_file in files_map.items():
    raw_path = os.path.join(BASE, raw_html_file)
    json_path = os.path.join(BASE, 'data', json_file)

    if not os.path.exists(raw_path):
        print(f'Skipping {raw_html_file} - not found')
        continue

    with open(raw_path, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')

    # ---- Main content: extract only the inner page-content div ----
    page_content_div = soup.find('div', class_='page-content')
    if page_content_div:
        main_content_html = str(page_content_div)
    else:
        content_div = soup.find('div', class_='read-more-content')
        main_content_html = content_div.decode_contents() if content_div else ''

    # Apply text replacements
    for old, new in copy_replacements.items():
        main_content_html = main_content_html.replace(old, new)

    # ---- FAQs ----
    faq_grid = soup.find('div', class_='ifcFaqGrid')
    extracted_faqs = []
    if faq_grid:
        for card in faq_grid.find_all('div', class_='ifcFaqCard'):
            q_el = card.find(class_='ifcFaqCardQ')
            a_el = card.find('div', class_='ifcFaqCardA')
            if not q_el or not a_el:
                continue
            q_text = q_el.get_text(strip=True)
            a_html = a_el.decode_contents()
            for old, new in copy_replacements.items():
                q_text = q_text.replace(old, new)
                a_html = a_html.replace(old, new)
            extracted_faqs.append({'question': q_text, 'answer': a_html})

    # ---- Hero title from H1 ----
    h1 = soup.find('h1')
    hero_title = h1.get_text(strip=True) if h1 else ''
    for old, new in copy_replacements.items():
        hero_title = hero_title.replace(old, new)

    # ---- Load existing JSON and update ----
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    data['main_content'] = main_content_html
    data['faqs'] = extracted_faqs
    if hero_title:
        data['hero_title'] = hero_title

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f'Updated {json_file} — {len(extracted_faqs)} FAQs, hero: {hero_title[:50]}')
