import json
import os

html_content = """
<div class="read-more-content relative min-w-0 overflow-x-hidden">
  <div class="page-content break-words">
    
    <h2>What Is a One Person Company (OPC)?</h2>
    <p>Introduced under the Companies Act of 2013, a One Person Company (OPC) is an innovative business structure designed specifically for solo entrepreneurs. It allows a single individual to establish a corporate entity with limited liability protection—combining the complete control of a sole proprietorship with the legal advantages of a private limited company.</p>
    <p>An OPC requires exactly 1 Director, 1 Shareholder (who can be the same person), and 1 Nominee. It is the ideal launchpad for consultants, professionals, and single-founder startups aiming for formal corporate identity.</p>

    <h2>Who Can Start an OPC in India? (Eligibility)</h2>
    <ul>
      <li><strong>Indian Citizens:</strong> The founder must be a natural person, an Indian citizen, and a resident of India (having stayed at least 182 days in the previous calendar year).</li>
      <li><strong>Age Requirement:</strong> The director and nominee must both be at least 18 years of age with a valid PAN and Aadhaar.</li>
      <li><strong>Entrepreneurs & Solo Founders:</strong> Perfect for freelancers, doctors, and independent contractors seeking liability protection.</li>
      <li><strong>NRIs:</strong> Non-Resident Indians are also eligible to incorporate an OPC in India, provided they meet specific compliance criteria.</li>
    </ul>

    <h2>Key Benefits of One Person Company Registration</h2>
    <ul>
      <li><strong>Limited Liability:</strong> Your personal assets remain completely protected against business debts and financial losses.</li>
      <li><strong>Single Ownership & Full Control:</strong> Maintain 100% decision-making authority without partner conflicts or board disputes.</li>
      <li><strong>Enhanced Corporate Credibility:</strong> Operating as a registered company builds significant trust with banks, suppliers, and enterprise clients.</li>
      <li><strong>Lower Compliance Burden:</strong> OPCs are exempt from holding Annual General Meetings (AGMs) and enjoy relaxed board meeting quorum requirements compared to traditional Private Limited Companies.</li>
    </ul>

    <h2>Documents Required for OPC Registration</h2>
    <p>The documentation process is entirely digital. Ensure you have the following ready for both the Director and the Nominee:</p>
    <ul>
      <li><strong>Identity Proof:</strong> PAN Card (mandatory for Indian citizens) and Aadhaar Card / Passport / Voter ID.</li>
      <li><strong>Address Proof:</strong> Bank Statement, Electricity Bill, or Mobile Bill (not older than 2 months).</li>
      <li><strong>Registered Office Proof:</strong> Recent Utility bill (electricity/gas), NOC from the property owner, and rent agreement (if the premises are rented).</li>
    </ul>

    <h2>How to Register an OPC Online with TCS?</h2>
    <ul>
      <li><strong>Step 1: Obtain DSC & DIN.</strong> We procure a Class-3 Digital Signature Certificate (DSC) and Director Identification Number (DIN) for the proposed director.</li>
      <li><strong>Step 2: Name Approval.</strong> We file the SPICe+ RUN form to reserve a unique company name ending with "(OPC) Private Limited".</li>
      <li><strong>Step 3: Document Drafting.</strong> Our experts draft your Memorandum of Association (MOA), Articles of Association (AOA), and secure the mandatory Consent Form (INC-3) from your Nominee.</li>
      <li><strong>Step 4: SPICe+ Form Submission.</strong> We submit the comprehensive incorporation form to the Ministry of Corporate Affairs (MCA), simultaneously applying for your company's PAN and TAN.</li>
      <li><strong>Step 5: Certificate of Incorporation.</strong> Upon approval, the MCA issues the Certificate of Incorporation (CoI) containing your 21-digit Corporate Identification Number (CIN).</li>
    </ul>

  </div>
</div>
"""

faqs = [
    {
        "question": "What is an OPC, and how does it differ from a Sole Proprietorship?",
        "answer": "<p>An OPC (One Person Company) is a registered corporate entity offering limited liability protection to its single owner. A Sole Proprietorship, while also run by one person, is not a separate legal entity, meaning the owner's personal assets are fully exposed to business liabilities.</p>"
    },
    {
        "question": "What is the role of a Nominee in an OPC?",
        "answer": "<p>A nominee is a mandatory requirement for an OPC. In the event of the sole director's death or permanent incapacity, the nominee assumes ownership and management of the company to ensure perpetual succession.</p>"
    },
    {
        "question": "When does an OPC need to be converted into a Private Limited Company?",
        "answer": "<p>Historically, an OPC had to convert if its paid-up capital exceeded ₹50 Lakhs or annual turnover exceeded ₹2 Crores. However, recent amendments have removed these mandatory conversion thresholds, allowing an OPC to grow without forced conversion.</p>"
    },
    {
        "question": "Can an OPC engage in financial activities like banking or insurance?",
        "answer": "<p>No, an OPC is strictly prohibited from engaging in Non-Banking Financial Investment activities (NBFC), banking, insurance, or investment in securities of any body corporate.</p>"
    },
    {
        "question": "How many OPCs can an individual establish?",
        "answer": "<p>An individual is legally permitted to establish and be the sole member of only one One Person Company (OPC) at any given time.</p>"
    },
    {
        "question": "What are the annual compliance requirements for an OPC?",
        "answer": "<p>An OPC must file Annual Financial Statements (Form AOC-4) within 180 days of the financial year-end and an Annual Return (Form MGT-7A). It must also file an Income Tax Return (ITR-6) and maintain statutory books of accounts.</p>"
    }
]

data = {
    "id": "one-person-company",
    "meta_title": "One Person Company Registration Online in India | TCS",
    "meta_description": "Register your One Person Company (OPC) in India with expert assistance from TCS. Get MCA name approval, MOA drafting, PAN, and complete compliance support.",
    "hero_title": "One Person Company Registration",
    "hero_description": "Register your One Person Company (OPC) in India with expert assistance from TCS. Combine the absolute control of a sole proprietorship with the robust limited liability protection of a corporate entity.",
    "price": "2,499",
    "breadcrumbs": [
        {"name": "Home", "url": "/"},
        {"name": "Registrations", "url": "/registrations"},
        {"name": "OPC Registration", "url": "/one-person-company"}
    ],
    "main_content": html_content,
    "faqs": faqs
}

os.makedirs('d:/user/TCS_website/data', exist_ok=True)
with open('d:/user/TCS_website/data/one-person-company.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
