import os
import re
import urllib.request
import urllib.parse
import bs4

BASE = 'd:/user/TCS_website'

services_to_build = [
    # Core Company & Startup Registrations
    {
        'slug': 'partnership',
        'raw_file': 'partnership_raw.html',
        'out_file': 'partnership.html',
        'url': 'https://www.indiafilings.com/partnership',
        'title': 'Partnership Firm Registration Online in India | TCS'
    },
    {
        'slug': 'section-8-company-registration',
        'raw_file': 'section_8_raw.html',
        'out_file': 'section-8-company-registration.html',
        'url': 'https://www.indiafilings.com/section-8-company-registration',
        'title': 'Section 8 Company Registration in India | TCS'
    },
    {
        'slug': 'indian-subsidiary',
        'raw_file': 'indian_subsidiary_raw.html',
        'out_file': 'indian-subsidiary.html',
        'url': 'https://www.indiafilings.com/indian-subsidiary',
        'title': 'Indian Subsidiary Company Registration | TCS'
    },
    {
        'slug': 'producer-company-registration',
        'raw_file': 'producer_company_raw.html',
        'out_file': 'producer-company-registration.html',
        'url': 'https://www.indiafilings.com/producer-company-registration',
        'title': 'Producer Company Registration in India | TCS'
    },
    {
        'slug': 'trust-registration',
        'raw_file': 'trust_raw.html',
        'out_file': 'trust-registration.html',
        'url': 'https://www.indiafilings.com/trust-registration',
        'title': 'Trust Registration Online in India | TCS'
    },
    # Key Business & Tax Registrations
    {
        'slug': 'gst-registration',
        'raw_file': 'gst_raw.html',
        'out_file': 'gst-registration.html',
        'url': 'https://www.indiafilings.com/gst-registration',
        'title': 'GST Registration Online in India | TCS'
    },
    {
        'slug': 'udyam-registration',
        'raw_file': 'udyam_raw.html',
        'out_file': 'udyam-registration.html',
        'url': 'https://www.indiafilings.com/udyam-registration',
        'title': 'Udyam MSME Registration Online | TCS'
    },
    {
        'slug': 'trademark-registration',
        'raw_file': 'trademark_raw.html',
        'out_file': 'trademark-registration.html',
        'url': 'https://www.indiafilings.com/trademark-registration',
        'title': 'Trademark Registration Online in India | TCS'
    }
]

# Fetch missing raw files
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
for item in services_to_build:
    raw_path = os.path.join(BASE, item['raw_file'])
    if not os.path.exists(raw_path):
        print(f"Fetching {item['url']} -> {item['raw_file']}...")
        try:
            req = urllib.request.Request(item['url'], headers=headers)
            with urllib.request.urlopen(req) as resp:
                data = resp.read().decode('utf-8', errors='ignore')
                with open(raw_path, 'w', encoding='utf-8') as f:
                    f.write(data)
            print(f"Saved {item['raw_file']} ({len(data)} bytes)")
        except Exception as e:
            print(f"Failed to fetch {item['url']}: {e}")

# Fetch any missing images found across these raw files
local_imgs = set(os.listdir(os.path.join(BASE, 'images')))
for item in services_to_build:
    raw_path = os.path.join(BASE, item['raw_file'])
    if not os.path.exists(raw_path):
        continue
    with open(raw_path, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src and src.startswith('http') and 'indiafilings' in src:
            filename = src.split('/')[-1].split('?')[0]
            if filename and filename not in local_imgs and filename != 'logo-110x52.png':
                try:
                    dest = os.path.join(BASE, 'images', filename)
                    urllib.request.urlretrieve(src, dest)
                    local_imgs.add(filename)
                    print(f"Downloaded image: {filename}")
                except Exception as e:
                    print(f"Failed to download image {src}: {e}")

# Now build all pages using our standalone builder
import build_standalone_all

for item in services_to_build:
    raw_path = os.path.join(BASE, item['raw_file'])
    if os.path.exists(raw_path):
        build_standalone_all.build_standalone_page(item)

print("\nAll requested service pages successfully built and verified!")
