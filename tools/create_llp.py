import json
import os

html_content = """
<div class="read-more-content relative min-w-0 overflow-x-hidden">
  <div class="page-content break-words">
    
    <h2>What Is a Limited Liability Partnership (LLP)?</h2>
    <p>A Limited Liability Partnership (LLP) is a modern, hybrid business structure governed by the Limited Liability Partnership Act, 2008. It uniquely combines the limited liability benefits of a private company with the operational flexibility of a traditional partnership.</p>
    <p>By creating a separate legal entity distinct from its partners, an LLP ensures that the personal assets of the partners are protected from business debts and liabilities. It is highly popular among professional service providers, consultancies, IT firms, and growing startups looking for a cost-effective and compliant business model.</p>

    <h2>Eligibility Criteria for LLP Registration</h2>
    <ul>
      <li><strong>Minimum Partners:</strong> At least 2 Designated Partners (natural persons) are required to form an LLP.</li>
      <li><strong>Residency Requirement:</strong> At least one Designated Partner must be a resident of India (having stayed in India for 120 days or more during the financial year).</li>
      <li><strong>Age and Qualifications:</strong> All Designated Partners must be at least 18 years old. There are no specific educational requirements.</li>
      <li><strong>Mandatory IDs:</strong> Designated Partners must possess a valid Designated Partner Identification Number (DPIN) and a Digital Signature Certificate (DSC).</li>
      <li><strong>Corporate Partners:</strong> Companies or other LLPs can become partners through an authorized nominee.</li>
      <li><strong>Capital Requirement:</strong> Unlike some structures, there is no mandatory minimum capital contribution required for an LLP.</li>
    </ul>

    <h2>What Are the Benefits of LLP Registration?</h2>
    <ul>
      <li><strong>Limited Liability:</strong> Partners are liable only up to their agreed capital contribution; their personal assets remain completely protected.</li>
      <li><strong>Separate Legal Entity:</strong> An LLP can acquire property, open bank accounts, enter into contracts, and sue or be sued in its own name.</li>
      <li><strong>Lower Compliance Burden:</strong> LLPs enjoy fewer statutory meetings and are exempt from mandatory audits if their annual turnover is less than ₹40 Lakhs or capital contribution is less than ₹25 Lakhs.</li>
      <li><strong>Tax Efficiency:</strong> Profits distributed to partners are tax-exempt in the partners' hands, and Dividend Distribution Tax (DDT) is not applicable.</li>
      <li><strong>No Minimum Capital:</strong> You can start an LLP with any amount of capital, offering ultimate financial flexibility for founders.</li>
    </ul>

    <h2>Documents Required for LLP Registration</h2>
    <p>The documentation process is fully digital. Ensure you have the following ready:</p>
    <ul>
      <li><strong>For Partners / Designated Partners:</strong> PAN Card (Mandatory for Indian nationals) or Passport (for Foreign Nationals/NRIs), Identity Proof (Aadhaar Card, Passport, Voter ID, or Driving License), Address Proof (Bank Statement, Electricity Bill, or Mobile Bill not older than 2 months), and a Passport-size photograph.</li>
      <li><strong>For Registered Office Address:</strong> Proof of Business Address (Electricity bill, Water bill, or Property Tax receipt not older than 2 months) and a Rent Agreement with a Landlord NOC (No Objection Certificate) for using the premises.</li>
    </ul>

    <h2>How to Register an LLP Online with TCS?</h2>
    <ul>
      <li><strong>Step 1: Obtain DSC & DPIN.</strong> We secure Digital Signature Certificates (DSC) and Designated Partner Identification Numbers (DPIN) for all proposed Designated Partners.</li>
      <li><strong>Step 2: Name Reservation.</strong> We apply for your proposed LLP name reservation on the MCA portal (RUN-LLP / FiLLiP), ensuring it complies with all naming guidelines and ends with "LLP".</li>
      <li><strong>Step 3: FiLLiP Form Filing.</strong> We submit the integrated Form FiLLiP along with required subscriber sheets, identity proofs, address proofs, and office NOC documents to the MCA.</li>
      <li><strong>Step 4: ROC Verification & Incorporation.</strong> The Registrar of Companies (ROC) reviews the application and issues the Certificate of Incorporation containing your unique LLPIN.</li>
      <li><strong>Step 5: Draft & File LLP Agreement (Form 3).</strong> We expertly prepare your customized LLP Agreement—defining partner roles, profit sharing, and capital contribution—and file Form 3 with the MCA within 30 days of incorporation.</li>
      <li><strong>Step 6: PAN & TAN Allocation.</strong> We facilitate the issuance of your PAN and TAN for immediate tax filing and bank account opening.</li>
    </ul>

  </div>
</div>
"""

faqs = [
    {
        "question": "Who is eligible to form an LLP?",
        "answer": "<p>Any individual aged 18 years or above with a valid identity proof and address proof can form an LLP. At least two Designated Partners are required, with at least one being a resident of India. Corporate bodies (Companies/LLPs) can also become partners through designated representatives.</p>"
    },
    {
        "question": "What is the minimum capital required for LLP Registration?",
        "answer": "<p>There is no prescribed minimum capital requirement. An LLP can be incorporated with any amount of capital contribution contributed by the partners, whether in cash, tangible property, or intangible property.</p>"
    },
    {
        "question": "Is GST registration mandatory for an LLP?",
        "answer": "<p>GST registration is only mandatory if the LLP's annual aggregate turnover exceeds ₹20 Lakhs for services (₹10 Lakhs in special category states) or ₹40 Lakhs for goods, or if the LLP engages in inter-state trade or e-commerce operations.</p>"
    },
    {
        "question": "How long does it take to register an LLP in India?",
        "answer": "<p>With TCS, the entire online LLP incorporation process typically takes between 7 to 14 business days, depending on document accuracy, name availability, and processing speed at the Ministry of Corporate Affairs (MCA).</p>"
    },
    {
        "question": "What is a DPIN and why is it necessary?",
        "answer": "<p>A DPIN (Designated Partner Identification Number) is a unique 8-digit identification number issued by the MCA to individuals acting as Designated Partners in an LLP. It is a mandatory requirement for incorporation.</p>"
    },
    {
        "question": "Can Foreign Nationals or NRIs be partners in an LLP?",
        "answer": "<p>Yes, NRIs and Foreign Nationals can become partners or Designated Partners in an LLP, provided at least one Designated Partner is a resident Indian and all foreign documents are notarized/apostilled.</p>"
    }
]

data = {
    "id": "llp-registration",
    "meta_title": "LLP Registration in India | Register Your LLP Online | TCS",
    "meta_description": "Register your Limited Liability Partnership (LLP) in India with expert assistance from TCS. Get MCA name approval, LLP Agreement drafting, and complete compliance support.",
    "hero_title": "LLP Registration in India",
    "hero_description": "Register your Limited Liability Partnership (LLP) in India with expert assistance from TCS. Get MCA name approval, LLP incorporation, LLP Agreement drafting, PAN & TAN registration, and complete compliance support to start your business legally.",
    "price": "1,999",
    "breadcrumbs": [
        {"name": "Home", "url": "/"},
        {"name": "Registrations", "url": "/registrations"},
        {"name": "LLP Registration", "url": "/llp-registration"}
    ],
    "main_content": html_content,
    "faqs": faqs
}

os.makedirs('d:/user/TCS_website/data', exist_ok=True)
with open('d:/user/TCS_website/data/llp-registration.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
