import os
import json
import jinja2

# Setup Jinja2 Environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=jinja2.select_autoescape(['html']))
template = env.get_template('service_page.html')

with open(os.path.join(os.path.dirname(__file__), 'site', 'services.json'), encoding='utf-8') as f:
    service_registry = {service['id']: service for service in json.load(f)}

def prepare_page(page_data):
    """Enrich local content with navbar identity without changing the UI shell."""
    page_data = dict(page_data)
    service = service_registry.get(page_data['id'])
    if service and page_data['id'] != 'proprietorship':
        page_data.setdefault('nav_label', service['name'])
        page_data.setdefault('category', service['category'])
    return page_data

# Related Services are global to the site, so we pass them in as site data
site_data = {
    "related_services": [
        {"id": "company-registration", "name": "Company Registration", "url": "/company-registration"},
        {"id": "one-person-company", "name": "OPC Registration", "url": "/one-person-company"},
        {"id": "partnership", "name": "Partnership Firm Registration", "url": "/partnership"},
        {"id": "private-limited-company", "name": "Private Limited Company", "url": "/private-limited-company"},
        {"id": "section-8-company-registration", "name": "Section 8 Company", "url": "/section-8-company-registration"},
        {"id": "indian-subsidiary", "name": "India Business Setup", "url": "/indian-subsidiary"},
        {"id": "llp-registration", "name": "LLP Registration", "url": "/llp-registration"},
        {"id": "virtual-office", "name": "Virtual Office Address", "url": "/virtual-office"},
        {"id": "proprietorship", "name": "Proprietorship", "url": "/proprietorship"},
        {"id": "public-limited-company", "name": "Public Limited Company", "url": "/public-limited-company"},
        {"id": "producer-company-registration", "name": "Producer Company", "url": "/producer-company-registration"},
        {"id": "pitch-deck", "name": "Pitch Deck", "url": "/pitch-deck"}
    ]
}

def build_page(json_file, output_html):
    with open(json_file, 'r', encoding='utf-8') as f:
        page_data = json.load(f)
    
    html_out = template.render(page=prepare_page(page_data), site=site_data)
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_out)
    
    print(f"Built {output_html} successfully.")

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            json_path = os.path.join(data_dir, filename)
            output_name = filename.replace('.json', '.html')
            output_path = os.path.join(os.path.dirname(__file__), output_name)
            build_page(json_path, output_path)
