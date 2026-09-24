import json
import os

html_content = """
<div class="read-more-content relative min-w-0 overflow-x-hidden">
  <div class="page-content break-words">
    
    <h2>What is a Private Limited Company Registration in India?</h2>
    <p>A Private Limited Company is one of the most highly recommended and robust business structures in India. Registered under the Companies Act, 2013 and governed by the Ministry of Corporate Affairs (MCA), it establishes a separate legal corporate entity distinct from its founders.</p>
    <p>This structure is considered the gold standard for startups and scaling businesses because it provides limited liability protection to its founders and offers the unique ability to raise equity funding from venture capitalists, angel investors, and financial institutions.</p>

    <h2>Key Benefits of a Private Limited Company</h2>
    <ul>
      <li><strong>Limited Liability Protection:</strong> The personal assets of directors and shareholders remain completely protected against business debts and liabilities.</li>
      <li><strong>Separate Legal Entity:</strong> The company can acquire property, open bank accounts, borrow money, and enter legal contracts in its own name.</li>
      <li><strong>Unmatched Fundraising Potential:</strong> It is the only preferred business structure for issuing equity shares to external investors, making it ideal for high-growth startups.</li>
      <li><strong>Perpetual Succession:</strong> The enterprise continues to exist regardless of changes in ownership, or the death or departure of directors.</li>
      <li><strong>High Credibility:</strong> Corporate structures inherently command higher trust from customers, vendors, and government bodies, and are eligible for various tax benefits and startup schemes.</li>
    </ul>

    <h2>Eligibility Criteria</h2>
    <p>To register a Private Limited Company with TCS, you must meet the following minimum requirements:</p>
    <ul>
      <li><strong>Minimum 2 Directors:</strong> At least one director must be an Indian Resident (stayed 182+ days in India in the previous financial year).</li>
      <li><strong>Minimum 2 Shareholders:</strong> Shareholders can be individuals or legal corporate bodies. (Maximum limit is 200).</li>
      <li><strong>Age Requirement:</strong> All directors and promoters must be at least 18 years of age.</li>
      <li>Foreign nationals and NRIs can seamlessly serve as directors or shareholders provided their KYC documents are apostilled.</li>
    </ul>

    <h2>Documents Required for Company Registration</h2>
    <p>The documentation process is fully digital. Ensure you have the following ready:</p>
    <ul>
      <li><strong>For Directors & Shareholders:</strong> PAN Card (mandatory for Indian citizens), Identity Proof (Aadhaar Card, Voter ID, or Passport), and recent Address Proof (Bank Statement, Mobile Bill, or Utility Bill).</li>
      <li><strong>For Registered Office:</strong> Proof of office space (Electricity bill, Gas bill, or Water bill not older than 2 months) and an NOC from the property owner along with the Rent Agreement (if rented).</li>
    </ul>

    <h2>The TCS 5-Step Online Registration Process</h2>
    <ul>
      <li><strong>Step 1: Obtain DSC & DIN.</strong> We procure Class-3 Digital Signature Certificates (DSC) and Director Identification Numbers (DIN) for all proposed directors.</li>
      <li><strong>Step 2: Name Approval.</strong> We file the SPICe+ Part A form to reserve a unique, compliant company name on the MCA portal.</li>
      <li><strong>Step 3: Document Drafting.</strong> Our experts draft the critical e-MOA (Memorandum of Association) and e-AOA (Articles of Association).</li>
      <li><strong>Step 4: Form Submission.</strong> We submit the comprehensive SPICe+ Part B form to the MCA, encompassing company incorporation, PAN, TAN, and AGILE-PRO-S (for GST, EPFO, ESIC, and Bank Account initialization).</li>
      <li><strong>Step 5: Incorporation Certificate.</strong> You receive the official Certificate of Incorporation (COI) containing your 21-digit Corporate Identification Number (CIN), signaling your business is legally established.</li>
    </ul>

  </div>
</div>
"""

faqs = [
    {
        "question": "What is a Company Registration?",
        "answer": "<p>Company Registration is the legal process of incorporating a business entity under the Companies Act, 2013, governed by the Ministry of Corporate Affairs (MCA). It gives the business a separate legal identity, limited liability protection, and the legal right to enter contracts, hold assets, and raise capital in its own name.</p>"
    },
    {
        "question": "Which type of company registration is best for a startup?",
        "answer": "<p>A Private Limited Company is the gold standard for startups. It provides limited liability protection, seamless equity fundraising options, a separate legal entity, and high credibility with venture capital investors and banking institutions.</p>"
    },
    {
        "question": "What is the difference between a Private Limited Company and an LLP?",
        "answer": "<p>A Private Limited Company is managed by directors and owned by shareholders, making it ideal for equity fundraising and rapid scaling. An LLP (Limited Liability Partnership) is managed directly by partners, offers internal operational flexibility, but cannot issue equity shares to external investors.</p>"
    },
    {
        "question": "What is the difference between a Private Limited Company and a Public Limited Company?",
        "answer": "<p>A Private Limited Company requires a minimum of 2 directors and 2 shareholders (capped at 200) and restricts share transfers. A Public Limited Company requires a minimum of 3 directors and 7 shareholders (with no maximum cap) and is eligible to offer shares to the public on the stock market.</p>"
    },
    {
        "question": "What are the minimum requirements for a Company Registration?",
        "answer": "<p>The basic prerequisites are a minimum of 2 directors (at least 1 Indian resident director), 2 shareholders, a unique company name ending in 'Private Limited', a registered address in India, and valid KYC/address proofs for all directors and subscribers.</p>"
    },
    {
        "question": "How long does the registration process take?",
        "answer": "<p>With TCS, the standard incorporation process typically takes 7 to 10 working days, assuming all documentation is complete and accurate upon submission to the MCA.</p>"
    }
]

data = {
    "id": "private-limited-company",
    "meta_title": "Private Limited Company Registration in India | TCS",
    "meta_description": "Register your Private Limited Company in India with Tirumala Consultancy Services. Get name approval, MOA & AOA drafting, PAN, and complete compliance support.",
    "hero_title": "Private Limited Company Registration in India",
    "hero_description": "Register your Private Limited Company in India with expert assistance from TCS. Get name approval, MOA & AOA drafting, PAN & TAN registration, and complete compliance support to start your business legally and securely.",
    "price": "2,899",
    "breadcrumbs": [
        {"name": "Home", "url": "/"},
        {"name": "Registrations", "url": "/registrations"},
        {"name": "Private Limited Company", "url": "/private-limited-company"}
    ],
    "main_content": html_content,
    "faqs": faqs
}

os.makedirs('d:/user/TCS_website/data', exist_ok=True)
with open('d:/user/TCS_website/data/private-limited-company.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
