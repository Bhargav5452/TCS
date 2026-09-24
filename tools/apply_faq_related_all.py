import glob
import os
import re
import json

BASE_DIR = 'd:/user/TCS_website'

built_files = sorted([
    f for f in os.listdir(BASE_DIR)
    if f.endswith('.html') and not f.endswith('_raw.html') and f not in ['index.html', 'proprietorship.html']
])

print(f"Total target service pages to process: {len(built_files)}")

raw_files_set = set(os.listdir(BASE_DIR))

special_raw_map = {
    'one-person-company.html': 'opc_raw.html',
    'private-limited-company.html': 'plc_raw.html',
    'producer-company-registration.html': 'producer_company_raw.html',
    'public-limited-company.html': 'publc_raw.html',
    'section-8-company-registration.html': 'section_8_raw.html',
    'income-tax-filing.html': 'income_tax_filing_raw.html',
    'indian-subsidiary.html': 'indian_subsidiary_raw.html',
    'trust-registration.html': 'trust_raw.html',
    'udyam-registration.html': 'udyam_raw.html',
    'gst-registration.html': 'gst_raw.html',
    'llp-registration.html': 'llp_raw.html',
    'trademark-registration.html': 'trademark_raw.html',
    'partnership.html': 'partnership_raw.html',
    'fssai.html': 'fssai_raw.html',
}

def get_raw_file(built_filename):
    if built_filename in special_raw_map:
        return special_raw_map[built_filename]
    stem = built_filename[:-5]
    if f"{stem}_raw.html" in raw_files_set:
        return f"{stem}_raw.html"
    if f"{stem.replace('-', '_')}_raw.html" in raw_files_set:
        return f"{stem.replace('-', '_')}_raw.html"
    if stem.endswith('-registration') and f"{stem[:-13]}_raw.html" in raw_files_set:
        return f"{stem[:-13]}_raw.html"
    for r in raw_files_set:
        if r.endswith('_raw.html'):
            if stem in r or r[:-9] in stem:
                return r
    return None

all_local_stems = {f[:-5]: f for f in os.listdir(BASE_DIR) if f.endswith('.html') and not f.endswith('_raw.html')}

def resolve_service_url(name, if_url, current_built_file):
    slug = if_url.rstrip('/').split('/')[-1] if if_url else ""
    
    if slug and f"{slug}.html" == current_built_file:
        return None, True # active page
    
    if slug in all_local_stems:
        return f"./{all_local_stems[slug]}", False
    
    synonyms = {
        'startup': 'company-registration.html',
        'company-registration': 'private-limited-company.html',
        'opc-registration': 'one-person-company.html',
        'one-person-company': 'one-person-company.html',
        'llp': 'llp-registration.html',
        'llp-registration': 'llp-registration.html',
        'gst': 'gst-registration.html',
        'gst-registration': 'gst-registration.html',
        'trademark': 'trademark-registration.html',
        'trademark-registration': 'trademark-registration.html',
        'copyright': 'copyright-registration.html',
        'patent': 'patent-registration.html',
        'fssai': 'fssai-license.html',
        'udyam': 'udyam-registration.html',
        'msme': 'udyam-registration.html',
        'iec': 'import-export-code.html',
        'pf': 'pf-registration.html',
        'esi': 'esi-registration.html',
        'virtual-office-address': 'virtual-office.html',
        'section-8': 'section-8-company-registration.html',
        'producer-company': 'producer-company-registration.html',
        'public-limited': 'public-limited-company.html',
        'foreign-subsidiary': 'indian-subsidiary.html',
        'proprietorship': 'proprietorship.html'
    }
    if slug in synonyms:
        target = synonyms[slug]
        if target == current_built_file:
            return None, True
        if target[:-5] in all_local_stems:
            return f"./{target}", False

    if f"{slug}-registration" in all_local_stems:
        target = all_local_stems[f"{slug}-registration"]
        if target == current_built_file:
            return None, True
        return f"./{target}", False

    if slug.endswith('-registration') and slug[:-13] in all_local_stems:
        target = all_local_stems[slug[:-13]]
        if target == current_built_file:
            return None, True
        return f"./{target}", False

    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
    for stem, fname in all_local_stems.items():
        clean_stem = stem.replace('-', ' ')
        if clean_stem in clean_name or clean_name in clean_stem:
            if fname == current_built_file:
                return None, True
            return f"./{fname}", False

    return "modal", False

def clean_brand_text(text):
    if not text:
        return ""
    t = text
    t = re.sub(r'IndiaFilings\.com', 'Tirumala Consultancy Services', t, flags=re.I)
    t = re.sub(r'IndiaFilings\'s', 'Tirumala Consultancy Services\'', t, flags=re.I)
    t = re.sub(r'IndiaFilings\'', 'Tirumala Consultancy Services\'', t, flags=re.I)
    t = re.sub(r'IndiaFilings', 'Tirumala Consultancy Services', t, flags=re.I)
    t = re.sub(r'support@indiafilings\.com', 'contact@tirumalaconsultancy.com', t, flags=re.I)
    t = re.sub(r'Ledgers', 'TCS Platform', t)
    return t.strip()

def format_answer_html(answer_raw):
    answer = clean_brand_text(answer_raw)
    if '<ul' in answer or '<ol' in answer or '<p' in answer:
        answer = answer.replace('<ul>', "<ul class='list-disc pl-5 mt-2 space-y-1'>")
        answer = answer.replace('<ol>', "<ol class='list-decimal pl-5 mt-2 space-y-1'>")
        return answer

    if re.search(r'(?:\d+\.\s+|\n\s*[-•]\s+)', answer):
        lines = [l.strip() for l in answer.split('\n') if l.strip()]
        html_parts = []
        in_list = False
        for line in lines:
            m_num = re.match(r'^(?:\d+\.\s+|[-•]\s+)(.*)$', line)
            if m_num:
                if not in_list:
                    html_parts.append("<ul class='list-disc pl-5 mt-2 space-y-1'>")
                    in_list = True
                html_parts.append(f"<li>{m_num.group(1)}</li>")
            else:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                html_parts.append(f"<p class='mt-1'>{line}</p>")
        if in_list:
            html_parts.append("</ul>")
        return "".join(html_parts)

    return answer

# Explicit curated FAQs for the 6 services without RSC arrays on IndiaFilings
curated_faqs = {
    'singapore-company-registration.html': [
        ("Can a foreign national or non-resident register a company in Singapore?",
         "Yes, foreign individuals and corporations can own 100% of a Singapore Private Limited Company. However, Singapore law requires appointing at least one ordinarily resident director, which Tirumala Consultancy Services can assist with."),
        ("Is physical travel to Singapore required for company incorporation?",
         "No, the entire incorporation process with ACRA (Accounting and Corporate Regulatory Authority) can be completed remotely through Tirumala Consultancy Services without traveling."),
        ("What are the key requirements for incorporating in Singapore?",
         "<ul class='list-disc pl-5 mt-2 space-y-1'><li>Unique company name approved by ACRA.</li><li>At least one shareholder (individual or corporate).</li><li>At least one resident director (citizen, permanent resident, or EntrePass/EP holder).</li><li>Local registered office address in Singapore.</li><li>Minimum paid-up capital of SGD 1.</li></ul>"),
        ("What documents are required for Singapore company registration?",
         "Valid passport copies, proof of residential address (bank statement or utility bill not older than 3 months), and brief profile of the proposed business activities."),
        ("How long does it take to register a company in Singapore?",
         "Once documentation and name approval are completed, incorporation typically takes 1 to 3 business days.")
    ],
    'usa-company-registration.html': [
        ("Can a non-US resident register an LLC or C-Corp in the USA?",
         "Yes, non-US residents can legally register and 100% own a US business entity (such as a Delaware or Wyoming LLC/C-Corp) without US citizenship or residency."),
        ("Is a visit to the United States required for registration?",
         "No, the entire filing with the respective Secretary of State and obtaining your EIN (Employer Identification Number) from the IRS can be handled remotely by Tirumala Consultancy Services."),
        ("Which US state is best for company registration?",
         "Delaware and Wyoming are the most popular states for non-residents due to business-friendly corporate laws, strong privacy protections, and minimal annual reporting burdens."),
        ("What is an EIN and why is it needed?",
         "An Employer Identification Number (EIN) is a federal tax ID issued by the IRS. It is required to open a US business bank account, process international payments (via Stripe, PayPal, etc.), and file US tax returns."),
        ("How long does USA company registration take?",
         "State incorporation usually takes 3 to 7 business days, while obtaining an EIN for non-US residents generally takes 2 to 3 weeks.")
    ],
    'uk-company-registration.html': [
        ("Can a non-UK resident register a company in the United Kingdom?",
         "Yes, anyone of any nationality can incorporate a UK Private Limited Company (Ltd) with Companies House. There is no requirement to be a UK resident or citizen."),
        ("Is a UK physical office address required?",
         "Yes, Companies House requires an official UK registered office address. Tirumala Consultancy Services provides registered office address facilities in the UK as part of the service."),
        ("What documents are required for UK company formation?",
         "A valid passport, proof of residential address, proposed company name, details of at least one director and shareholder, and Memorandum & Articles of Association."),
        ("How fast can a UK company be incorporated?",
         "UK incorporation with Companies House is typically processed within 24 to 48 hours once details are submitted."),
        ("Can I open a UK business bank account as a non-resident?",
         "Yes, once your company is incorporated, you can apply for UK business multi-currency accounts (such as Wise, Payoneer, or Revolut Business) with support from Tirumala Consultancy Services.")
    ],
    'usa-trademark-registration.html': [
        ("Can a foreign business register a trademark in the United States?",
         "Yes, foreign individuals and businesses can register trademarks with the United States Patent and Trademark Office (USPTO). Under USPTO rules, foreign applicants must be represented by a licensed US attorney, which Tirumala Consultancy Services coordinates."),
        ("What is the difference between intent-to-use and actual use applications?",
         "An Actual Use application is filed when the trademark is already in commercial use in US interstate commerce, while an Intent-to-Use (ITU) application reserves your trademark rights before launching."),
        ("How long does USA trademark registration take?",
         "The USPTO review process typically takes 8 to 12 months from initial application to final registration."),
        ("What protection does a US trademark provide?",
         "A registered US trademark grants nationwide legal protection, the exclusive right to use the mark with your goods/services, and the legal ability to use the official ® symbol.")
    ],
    'barcode-registration.html': [
        ("What is Barcode Registration in India?",
         "Barcode registration is the process of acquiring unique GS1-compliant barcodes (such as EAN-13 or UPC) for commercial products sold in retail stores, supermarkets, and online marketplaces like Amazon and Flipkart."),
        ("Who issues authentic barcodes in India?",
         "Official barcodes in India are allocated through GS1 India, the authorized standards organization affiliated with GS1 Global. Tirumala Consultancy Services assists businesses with the entire allocation process."),
        ("What are the documents required for barcode registration?",
         "<ul class='list-disc pl-5 mt-2 space-y-1'><li>Business registration proof (GST, PAN, Incorporation Certificate).</li><li>Balance sheet or annual turnover proof.</li><li>Product category and packaging specifications.</li></ul>"),
        ("How long does it take to obtain barcodes?",
         "Barcode allotment through GS1 India generally takes 2 to 4 business days after document verification.")
    ],
    'bookkeeping-services.html': [
        ("What are bookkeeping services?",
         "Bookkeeping services involve recording, classifying, and reconciling all daily financial transactions of a business, including sales, purchases, receipts, payments, and bank accounts."),
        ("Why should a business outsource bookkeeping to Tirumala Consultancy Services?",
         "Outsourcing eliminates the overhead of hiring in-house accountants while ensuring audit-ready books, accurate financial statements, and timely GST and TDS compliance."),
        ("Which accounting software do you support?",
         "We support all major cloud accounting platforms including Tally Prime, Zoho Books, QuickBooks, and Excel-based systems."),
        ("How frequently are financial reports provided?",
         "Reports including Profit & Loss statements, Balance Sheets, Cash Flow reports, and accounts receivables/payables are updated on a monthly or quarterly basis according to your plan.")
    ]
}

def extract_faqs(raw_content, built_content, built_filename):
    if built_filename in curated_faqs:
        return [(q, format_answer_html(a)) for q, a in curated_faqs[built_filename]]

    faqs = []

    # Method 1: Schema / JSON-LD in raw content
    faq_idx = raw_content.find('"FAQPage"')
    if faq_idx == -1:
        faq_idx = raw_content.find(r'\"FAQPage\"')
    
    if faq_idx != -1:
        me_pos = raw_content.find('"mainEntity":', max(0, faq_idx - 100))
        if me_pos == -1:
            me_pos = raw_content.find(r'\"mainEntity\":', max(0, faq_idx - 100))
        if me_pos != -1:
            ob = raw_content.find('[', me_pos)
            if ob != -1 and ob - me_pos < 30:
                bc = 0
                end_b = -1
                for i in range(ob, min(ob + 100000, len(raw_content))):
                    if raw_content[i] == '[': bc += 1
                    elif raw_content[i] == ']':
                        bc -= 1
                        if bc == 0:
                            end_b = i + 1
                            break
                if end_b != -1:
                    raw_str = raw_content[ob:end_b]
                    clean = raw_str.replace(r'\"', '"').replace(r'\\"', r'\"').replace(r'\\\\', r'\\')
                    try:
                        items = json.loads(clean)
                        for it in items:
                            q = it.get('name')
                            a = it.get('acceptedAnswer', {}).get('text')
                            if q and a:
                                faqs.append((clean_brand_text(q), format_answer_html(a)))
                    except:
                        pass

    # Method 2: RSC payload
    if not faqs:
        rsc_pos = raw_content.find(r'\"faqs\":[')
        if rsc_pos == -1:
            rsc_pos = raw_content.find('"faqs":[')
        if rsc_pos != -1:
            ob = raw_content.find('[', rsc_pos)
            if ob != -1:
                bc = 0
                end_b = -1
                for i in range(ob, min(ob + 100000, len(raw_content))):
                    if raw_content[i] == '[': bc += 1
                    elif raw_content[i] == ']':
                        bc -= 1
                        if bc == 0:
                            end_b = i + 1
                            break
                if end_b != -1:
                    raw_str = raw_content[ob:end_b]
                    clean = raw_str.replace(r'\"', '"').replace(r'\\"', r'\"').replace(r'\\\\', r'\\')
                    try:
                        items = json.loads(clean)
                        for it in items:
                            q = it.get('question')
                            a = it.get('answer')
                            if q and a:
                                faqs.append((clean_brand_text(q), format_answer_html(a)))
                    except:
                        pass

    # Method 3: Fallback from built content
    if not faqs and built_content:
        q_matches = re.findall(r'<span class="ifcFaqCardQ">([^<]+)</span>', built_content)
        a_matches = re.findall(r'<div class="ifcFaqCardA[^"]*">(.*?)</div>\s*</div>\s*</div>', built_content, re.DOTALL)
        for q, a in zip(q_matches, a_matches):
            faqs.append((clean_brand_text(q), format_answer_html(a)))

    return faqs

def extract_related_services(raw_content):
    category = ""
    services = []

    rel_idx = raw_content.find("Related Services - ")
    if rel_idx != -1:
        end_q = raw_content.find('"', rel_idx)
        if end_q != -1 and end_q - rel_idx < 80:
            category = raw_content[rel_idx + len("Related Services - "):end_q].replace('\\', '').strip()
        
        item_pos = raw_content.find("itemListElement", rel_idx)
        if item_pos != -1 and item_pos - rel_idx < 500:
            ob = raw_content.find('[', item_pos)
            if ob != -1 and ob - item_pos < 30:
                bc = 0
                end_b = -1
                for i in range(ob, min(ob + 50000, len(raw_content))):
                    if raw_content[i] == '[': bc += 1
                    elif raw_content[i] == ']':
                        bc -= 1
                        if bc == 0:
                            end_b = i + 1
                            break
                if end_b != -1:
                    clean = raw_content[ob:end_b].replace(r'\"', '"').replace(r'\\"', r'\"').replace(r'\\\\', r'\\')
                    try:
                        items = json.loads(clean)
                        for it in items:
                            svc = it.get('item', {})
                            name = svc.get('name')
                            url = svc.get('url')
                            if name:
                                services.append((clean_brand_text(name), url.strip() if url else ""))
                    except:
                        pass

    return category, services

category_fallbacks = {
    'company': ('Business Registration', [
        ('Startup / Business Setup', 'https://www.indiafilings.com/company-registration'),
        ('OPC Registration', 'https://www.indiafilings.com/one-person-company'),
        ('Partnership Firm Registration', 'https://www.indiafilings.com/partnership'),
        ('Private Limited Company', 'https://www.indiafilings.com/private-limited-company'),
        ('Section 8 Company', 'https://www.indiafilings.com/section-8-company-registration'),
        ('India Business Setup', 'https://www.indiafilings.com/indian-subsidiary'),
        ('LLP Registration', 'https://www.indiafilings.com/llp-registration'),
        ('Public Limited Company', 'https://www.indiafilings.com/public-limited-company'),
        ('Virtual Office Address', 'https://www.indiafilings.com/virtual-office'),
        ('Producer Company', 'https://www.indiafilings.com/producer-company-registration')
    ]),
    'gst': ('GST', [
        ('GST Registration', 'https://www.indiafilings.com/gst-registration'),
        ('GST Return Filing', 'https://www.indiafilings.com/gst-return-filing'),
        ('GST Annual Return', 'https://www.indiafilings.com/gst-annual-return'),
        ('GST LUT Form', 'https://www.indiafilings.com/gst-lut'),
        ('GST Notice Reply', 'https://www.indiafilings.com/gst-notice'),
        ('GST Amendment', 'https://www.indiafilings.com/gst-amendment'),
        ('GST Revocation', 'https://www.indiafilings.com/gst-revocation'),
        ('GSTR-10 Return', 'https://www.indiafilings.com/gstr-10')
    ]),
    'tax': ('Income Tax', [
        ('Income Tax Filing', 'https://www.indiafilings.com/income-tax-filing'),
        ('Business ITR Filing', 'https://www.indiafilings.com/business-itr-filing'),
        ('TDS Return Filing', 'https://www.indiafilings.com/tds-return-filing'),
        ('Income Tax Notice', 'https://www.indiafilings.com/income-tax-notice'),
        ('Form 15CA 15CB', 'https://www.indiafilings.com/15ca-15cb-filing'),
        ('ITR-5 Filing', 'https://www.indiafilings.com/itr-5-form'),
        ('ITR-6 Filing', 'https://www.indiafilings.com/itr-6-form'),
        ('ITR-7 Filing', 'https://www.indiafilings.com/itr-7-form')
    ]),
    'trademark': ('Trademark', [
        ('Trademark Registration', 'https://www.indiafilings.com/trademark-registration'),
        ('Trademark Objection', 'https://www.indiafilings.com/trademark-objection'),
        ('Trademark Opposition', 'https://www.indiafilings.com/trademark-opposition'),
        ('Trademark Hearing', 'https://www.indiafilings.com/trademark-hearing'),
        ('Trademark Renewal', 'https://www.indiafilings.com/trademark-renewal'),
        ('Trademark Rectification', 'https://www.indiafilings.com/trademark-rectification'),
        ('Logo Designing', 'https://www.indiafilings.com/logo-designing'),
        ('Copyright Registration', 'https://www.indiafilings.com/copyright-registration')
    ]),
    'ngo': ('Registrations', [
        ('12A Registration', 'https://www.indiafilings.com/12a-registration'),
        ('80G Registration', 'https://www.indiafilings.com/80g-registration'),
        ('12A & 80G Registration', 'https://www.indiafilings.com/12a-80g-registration'),
        ('Trust Registration', 'https://www.indiafilings.com/trust-registration'),
        ('NGO Darpan Registration', 'https://www.indiafilings.com/darpan-registration'),
        ('Section 8 Company', 'https://www.indiafilings.com/section-8-company-registration')
    ]),
    'compliance': ('MCA Compliance', [
        ('Company Annual Filing', 'https://www.indiafilings.com/company-annual-filing'),
        ('DIR-3 KYC', 'https://www.indiafilings.com/dir-3-kyc'),
        ('ADT-1 Filing', 'https://www.indiafilings.com/adt-1-filing'),
        ('DPT-3 Filing', 'https://www.indiafilings.com/dpt-3-filing'),
        ('Appointment of Director', 'https://www.indiafilings.com/appointment-of-director'),
        ('Resignation of Director', 'https://www.indiafilings.com/resignation-of-director'),
        ('AOA Amendment', 'https://www.indiafilings.com/aoa-amendment'),
        ('Company Name Change', 'https://www.indiafilings.com/company-name-change'),
        ('Share Transfer', 'https://www.indiafilings.com/company-share-transfer')
    ]),
    'international': ('International Business', [
        ('USA Company Registration', 'https://www.indiafilings.com/usa-company-registration'),
        ('UK Company Registration', 'https://www.indiafilings.com/uk-company-registration'),
        ('Dubai Company Registration', 'https://www.indiafilings.com/dubai-company-registration'),
        ('Singapore Company Registration', 'https://www.indiafilings.com/singapore-company-registration'),
        ('USA Trademark Registration', 'https://www.indiafilings.com/usa-trademark-registration'),
        ('Indian Subsidiary Registration', 'https://www.indiafilings.com/indian-subsidiary'),
        ('Import Export Code', 'https://www.indiafilings.com/import-export-code')
    ]),
    'default': ('Business Registrations & Licenses', [
        ('Startup Registration', 'https://www.indiafilings.com/company-registration'),
        ('GST Registration', 'https://www.indiafilings.com/gst-registration'),
        ('Udyam MSME Registration', 'https://www.indiafilings.com/udyam-registration'),
        ('Trademark Registration', 'https://www.indiafilings.com/trademark-registration'),
        ('FSSAI Food License', 'https://www.indiafilings.com/fssai-license'),
        ('Import Export Code', 'https://www.indiafilings.com/import-export-code'),
        ('PF & ESI Registration', 'https://www.indiafilings.com/pf-registration'),
        ('Virtual Office Address', 'https://www.indiafilings.com/virtual-office')
    ])
}

def get_fallback_category(stem):
    s = stem.lower()
    if any(k in s for k in ['usa', 'uk-', 'dubai', 'singapore']):
        return category_fallbacks['international']
    if any(k in s for k in ['gst', 'gstr']):
        return category_fallbacks['gst']
    if any(k in s for k in ['itr', 'tax', 'tds', '15ca']):
        return category_fallbacks['tax']
    if any(k in s for k in ['trademark', 'copyright', 'patent', 'design-']):
        return category_fallbacks['trademark']
    if any(k in s for k in ['12a', '80g', 'darpan', 'trust']):
        return category_fallbacks['ngo']
    if any(k in s for k in ['director', 'annual-filing', 'amendment', 'kyc', 'adt', 'dpt', 'share-transfer', 'din-']):
        return category_fallbacks['compliance']
    if any(k in s for k in ['company', 'llp', 'opc', 'partnership', 'proprietorship', 'subsidiary', 'producer']):
        return category_fallbacks['company']
    return category_fallbacks['default']

def build_faq_section_html(faqs, service_title):
    html = f"""<!-- Frequently Asked Questions Section -->
<section id="faq-section" aria-labelledby="faq-heading" class="relative isolate mx-auto max-w-[1600px] px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8 pb-8 sm:pb-12 z-30 scroll-mt-24">
  <style>
    .tcs-faq-accent-bar {{
      width: 40px;
      height: 3px;
      border-radius: 2px;
      background: #0d9488;
      margin-bottom: 16px;
    }}
    .tcs-faq-heading {{
      font-size: 22px;
      line-height: 1.25;
      color: #111827;
      margin: 0 0 4px;
      font-weight: 400;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }}
    @media (min-width: 640px) {{
      .tcs-faq-heading {{ font-size: 26px; }}
    }}
    .tcs-faq-subtitle {{
      font-size: 13px;
      color: #6b7280;
      margin: 0 0 24px;
      line-height: 1.5;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }}
    .tcs-faq-grid {{
      display: grid;
      grid-template-columns: 1fr;
      align-items: start;
      gap: 10px;
    }}
    @media (min-width: 768px) {{
      .tcs-faq-grid {{
        grid-template-columns: 1fr 1fr;
        gap: 12px;
      }}
    }}
    .tcs-faq-card {{
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      overflow: hidden;
      transition: border-color 0.18s ease, box-shadow 0.18s ease;
    }}
    .tcs-faq-card:hover {{
      border-color: #0d9488;
      box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.07);
    }}
    .tcs-faq-card.is-open {{
      border-color: #0d9488 !important;
      box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.08) !important;
    }}
    .tcs-faq-card-btn {{
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 18px;
      background: none;
      border: 0;
      cursor: pointer;
      text-align: left;
    }}
    .tcs-faq-card-q {{
      font-size: 13px;
      line-height: 1.45;
      font-weight: 500;
      color: #111827;
      flex: 1;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      transition: color 0.18s ease;
    }}
    .tcs-faq-card:hover .tcs-faq-card-q,
    .tcs-faq-card.is-open .tcs-faq-card-q {{
      color: #0f766e;
    }}
    .tcs-faq-chevron {{
      flex-shrink: 0;
      width: 16px;
      height: 16px;
      color: #9ca3af;
      transition: transform 0.25s ease, color 0.18s ease;
    }}
    .tcs-faq-card.is-open .tcs-faq-chevron {{
      transform: rotate(180deg);
      color: #0d9488;
    }}
    .tcs-faq-region {{
      display: grid;
      transition: grid-template-rows 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .tcs-faq-card-a {{
      padding: 0 18px 14px;
      font-size: 13px;
      line-height: 1.65;
      color: #4b5563;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      border-top: 1px solid #f3f4f6;
      padding-top: 10px;
    }}
    .tcs-faq-btn-row {{
      display: flex;
      justify-content: center;
      margin-top: 24px;
    }}
    .tcs-faq-toggle-btn {{
      padding: 9px 22px;
      font-size: 13px;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.15s, border-color 0.15s, color 0.15s;
      font-weight: 500;
      background: transparent;
      color: #6b7280;
      border: 1px solid #e5e7eb;
    }}
    .tcs-faq-toggle-btn:hover {{
      border-color: #0d9488;
      color: #0d9488;
      background: #f0fdfa;
    }}
  </style>

  <div>
    <div class="tcs-faq-accent-bar"></div>
    <h2 id="faq-heading" class="tcs-faq-heading">Frequently asked questions</h2>
    <p class="tcs-faq-subtitle">Common questions about {service_title} Online in India.</p>

    <!-- 2-Column Responsive Grid matching approved layout -->
    <div class="tcs-faq-grid">
"""
    for i, (q, a) in enumerate(faqs, start=1):
        html += f"""      <div class="tcs-faq-card" data-faq-index="{i}">
        <button type="button" class="tcs-faq-card-btn" aria-expanded="false" aria-controls="faq-ans-{i}">
          <span class="tcs-faq-card-q">{q}</span>
          <svg class="tcs-faq-chevron" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"></path></svg>
        </button>
        <div id="faq-ans-{i}" role="region" aria-hidden="true" class="tcs-faq-region" style="grid-template-rows: 0fr;">
          <div class="overflow-hidden">
            <div class="tcs-faq-card-a">
              {a}
            </div>
          </div>
        </div>
      </div>
"""
    html += "    </div>\n"

    if len(faqs) > 10:
        html += """
    <!-- Toggle Button Row -->
    <div class="tcs-faq-btn-row">
      <button type="button" id="tcs-faq-toggle-btn" class="tcs-faq-toggle-btn">
        Load more questions
      </button>
    </div>
"""
    html += "  </div>\n</section>\n"
    return html

def build_related_services_html(category, services, current_built_file):
    html = f"""<!-- Related Services Section matching approved layout -->
<section id="related-services-section" aria-labelledby="related-services-heading" class="relative isolate mx-auto max-w-[1600px] px-4 sm:px-6 lg:px-8 pb-10 sm:pb-14 z-20 scroll-mt-24">
  <div class="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-xs">
    <div class="border-b border-slate-100 px-5 sm:px-6 py-4">
      <h3 id="related-services-heading" class="text-[13.5px] font-semibold text-slate-900 tracking-tight">
        Related Services - {category}
      </h3>
    </div>
    <div class="p-4 sm:p-6">
      <div class="flex flex-wrap gap-2.5 sm:gap-3">
"""
    seen_names = set()
    for name, url in services:
        if name in seen_names:
            continue
        seen_names.add(name)
        resolved_url, is_active = resolve_service_url(name, url, current_built_file)
        if is_active:
            html += f"""        <span class="inline-flex items-center rounded-md border border-teal-200 bg-teal-50 px-3.5 py-2 text-[13px] font-medium text-teal-800" aria-current="page">
          {name}
        </span>
"""
        elif resolved_url and resolved_url != "modal":
            html += f"""        <a href="{resolved_url}" class="inline-flex items-center rounded-md border border-slate-200 bg-slate-50/80 px-3.5 py-2 text-[13px] font-medium text-slate-700 transition-colors hover:border-teal-500 hover:bg-teal-50/60 hover:text-teal-700">
          {name}
        </a>
"""
        else:
            html += f"""        <a href="javascript:void(0)" onclick="if(window.TCSConsultModal){{window.TCSConsultModal.open()}}else{{alert('Our legal specialists will connect with you.')}}" class="inline-flex items-center rounded-md border border-slate-200 bg-slate-50/80 px-3.5 py-2 text-[13px] font-medium text-slate-700 transition-colors hover:border-teal-500 hover:bg-teal-50/60 hover:text-teal-700">
          {name}
        </a>
"""
    html += """      </div>
    </div>
  </div>
</section>
"""
    return html

FAQ_ACCORDION_SCRIPT = """
<script>
(function() {
  function initFaq() {
    const faqContainer = document.getElementById('faq-section');
    if (!faqContainer) return;
    const cards = faqContainer.querySelectorAll('.tcs-faq-card');
    const toggleBtn = document.getElementById('tcs-faq-toggle-btn');
    let isExpandedAll = false;

    // Initial visibility: hide cards beyond index 10
    cards.forEach((card, i) => {
      if (i >= 10) card.style.display = 'none';
    });

    cards.forEach(card => {
      const btn = card.querySelector('.tcs-faq-card-btn');
      const region = card.querySelector('.tcs-faq-region');

      if (btn && region) {
        btn.onclick = function(e) {
          e.preventDefault();
          const isOpen = btn.getAttribute('aria-expanded') === 'true';

          // Close all other cards for clean accordion feel
          cards.forEach(otherCard => {
            if (otherCard !== card) {
              const otherBtn = otherCard.querySelector('.tcs-faq-card-btn');
              const otherRegion = otherCard.querySelector('.tcs-faq-region');
              if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
              if (otherRegion) {
                otherRegion.style.gridTemplateRows = '0fr';
                otherRegion.setAttribute('aria-hidden', 'true');
              }
              otherCard.classList.remove('is-open');
            }
          });

          // Toggle current card
          if (isOpen) {
            btn.setAttribute('aria-expanded', 'false');
            region.style.gridTemplateRows = '0fr';
            region.setAttribute('aria-hidden', 'true');
            card.classList.remove('is-open');
          } else {
            btn.setAttribute('aria-expanded', 'true');
            region.style.gridTemplateRows = '1fr';
            region.setAttribute('aria-hidden', 'false');
            card.classList.add('is-open');
          }
        };
      }
    });

    if (toggleBtn) {
      toggleBtn.onclick = function(e) {
        e.preventDefault();
        isExpandedAll = !isExpandedAll;
        cards.forEach((card, i) => {
          if (i >= 10) {
            card.style.display = isExpandedAll ? 'block' : 'none';
          }
        });
        toggleBtn.textContent = isExpandedAll ? 'Show less' : 'Load more questions';
      };
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFaq);
  } else {
    initFaq();
  }
})();
</script>
"""

success_count = 0
failed_pages = []

for idx, built_file in enumerate(built_files, start=1):
    built_path = os.path.join(BASE_DIR, built_file)
    with open(built_path, 'r', encoding='utf-8', errors='ignore') as f:
        built_text = f.read()

    raw_file = get_raw_file(built_file)
    raw_text = ""
    if raw_file and os.path.exists(os.path.join(BASE_DIR, raw_file)):
        with open(os.path.join(BASE_DIR, raw_file), 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()

    m_title = re.search(r'<title>([^<|]+)', built_text)
    service_title = m_title.group(1).strip() if m_title else built_file[:-5].replace('-', ' ').title()
    service_title = re.sub(r'\s+Online.*$', '', service_title, flags=re.I).strip()

    # Extract FAQs
    faqs = extract_faqs(raw_text, built_text, built_file)

    # Extract Related Services
    category, rel_services = extract_related_services(raw_text)
    if not category or not rel_services:
        category, rel_services = get_fallback_category(built_file[:-5])

    faq_html = build_faq_section_html(faqs, service_title)
    rel_html = build_related_services_html(category, rel_services, built_file)
    combined_sections = "\n" + faq_html + "\n" + rel_html

    # Find aside boundary in built_text
    m_aside = re.search(r'</aside>\s*</div>\s*</div>\s*</div>\s*</section>', built_text)
    if not m_aside:
        print(f"Error: Could not locate aside boundary in {built_file}")
        failed_pages.append(built_file)
        continue

    prefix = built_text[:m_aside.end()]
    suffix_start = built_text[m_aside.end():]
    
    main_idx = suffix_start.find('</main>')
    if main_idx == -1:
        print(f"Error: Could not locate </main> in {built_file}")
        failed_pages.append(built_file)
        continue

    suffix = suffix_start[main_idx:]

    # Remove older inline FAQ scripts from suffix
    suffix = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\',\s*function\(\)\s*\{\s*const faqContainer[\s\S]*?</script>', '', suffix)
    suffix = re.sub(r'<script>\s*\(function\(\)\s*\{\s*function initFaq\(\)[\s\S]*?</script>', '', suffix)

    # Inject the FAQ accordion script right before </body>
    body_idx = suffix.rfind('</body>')
    if body_idx != -1:
        suffix = suffix[:body_idx] + FAQ_ACCORDION_SCRIPT + '\n</body>' + suffix[body_idx+7:]
    else:
        suffix += FAQ_ACCORDION_SCRIPT

    new_html = prefix + combined_sections + suffix

    with open(built_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    success_count += 1
    if idx % 15 == 0 or idx == len(built_files):
        print(f"[{idx}/{len(built_files)}] Successfully updated {built_file} (FAQs: {len(faqs)}, Related: {len(rel_services)})")

print(f"\n==========================================")
print(f"Successfully updated {success_count} / {len(built_files)} service pages!")
if failed_pages:
    print(f"Failed pages: {failed_pages}")
print(f"==========================================")
