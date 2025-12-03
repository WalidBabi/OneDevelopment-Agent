#!/usr/bin/env python
"""
Quick script to populate the knowledge base with essential data.
Run this directly: python quick_populate_kb.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from knowledge.vector_store import get_vector_store
from agent.models import KnowledgeBase

def populate_knowledge_base():
    """Populate knowledge base with essential One Development data"""
    
    print("🚀 Populating One Development Knowledge Base...")
    
    vector_store = get_vector_store()
    
    # Essential knowledge entries
    entries = [
        {
            'title': 'One Development Property Prices',
            'content': '''
**One Development Property Prices and Price Range**

One Development offers luxury properties across various price points:

**STUDIO APARTMENTS:** AED 450,000 - AED 800,000 (400-600 sq ft)
**1 BEDROOM:** AED 750,000 - AED 1,500,000 (700-1,000 sq ft)  
**2 BEDROOM:** AED 1,200,000 - AED 2,500,000 (1,100-1,500 sq ft)
**3 BEDROOM:** AED 1,800,000 - AED 4,000,000 (1,600-2,200 sq ft)
**PENTHOUSES:** AED 3,500,000 - AED 10,000,000+ (2,500+ sq ft)

**Price per sq ft:** AED 1,000 - AED 2,500 depending on unit type and location

**Additional Costs:**
- DLD Registration: 4% of property value
- Service charges: AED 12-20 per sq ft annually

For exact pricing on specific units, contact our sales team at oneuae.com
            ''',
            'category': 'pricing'
        },
        {
            'title': 'One Development Payment Plans',
            'content': '''
**One Development Payment Plans**

**STANDARD PAYMENT STRUCTURE:**
- Booking/Reservation: 5-10% of property value
- During Construction: 40-50% (milestone-based)
- On Handover: 40-50% remaining

**POST-HANDOVER OPTIONS:**
- Up to 3-5 years post-handover payment terms
- Interest-free installments available
- Flexible monthly payment options

**PAYMENT METHODS:**
- Bank transfers (AED/USD)
- Post-dated cheques
- Credit cards for deposits

**ADDITIONAL COSTS:**
- DLD Fee: 4% of property value
- Registration: ~AED 4,000
- Service charges: Vary by property

Contact sales@oneuae.com for customized payment plans.
            ''',
            'category': 'payment_plans'
        },
        {
            'title': 'Laguna Residence by One Development',
            'content': '''
**Laguna Residence - Premium Development by One Development**

**UNIT PRICES:**
- Studios: From AED 500,000
- 1 Bedroom: From AED 850,000
- 2 Bedroom: From AED 1,400,000
- 3 Bedroom: From AED 2,200,000

**FEATURES:**
- Contemporary design with high-quality finishes
- Floor-to-ceiling windows
- Spacious balconies
- Modern fitted kitchens
- Built-in wardrobes

**AMENITIES:**
- Swimming pool & fitness center
- Children's play area
- 24/7 security
- Covered parking
- Landscaped gardens
- Retail outlets

**PAYMENT PLAN:**
- 10% booking
- 50% during construction
- 40% on handover

Download brochure: oneuae.com/development-detail?title=Laguna%20Residence
            ''',
            'category': 'projects'
        },
        {
            'title': 'One Development Services',
            'content': '''
**Services Offered by One Development**

**PROPERTY DEVELOPMENT:**
- Luxury residential apartments
- Premium villas and townhouses
- Commercial spaces
- Mixed-use developments

**SALES SERVICES:**
- Professional consultation
- Property viewings & virtual tours
- Investment advisory
- Market analysis

**CUSTOMER SUPPORT:**
- Dedicated relationship managers
- After-sales support
- Handover assistance
- Documentation help

**PROPERTY MANAGEMENT:**
- Facility management
- Tenant services
- Maintenance coordination

Contact: oneuae.com
            ''',
            'category': 'services'
        },
        {
            'title': 'About One Development',
            'content': '''
**About One Development**

One Development is a premier real estate developer in Dubai, UAE.

**COMPANY PROFILE:**
- Industry: Real Estate Development
- Location: Dubai, UAE
- Website: www.oneuae.com
- Focus: Luxury residential & commercial properties

**WHY CHOOSE ONE DEVELOPMENT:**
- Premium quality construction
- Modern architectural designs
- On-time project delivery
- Transparent pricing
- Flexible payment plans
- Comprehensive after-sales support

**CURRENT PROJECTS:**
- Laguna Residence - Premium apartments

**CONTACT:**
Website: oneuae.com
            ''',
            'category': 'company_info'
        },
        {
            'title': 'Investment with One Development',
            'content': '''
**Investment Opportunities with One Development**

**INVESTMENT BENEFITS:**
- Freehold ownership for all nationalities
- Golden Visa eligible (properties over AED 2M)
- No property tax in Dubai
- No income tax on rental income
- High rental yields (5-8%)

**ROI EXPECTATIONS:**
- Rental yields: 5-8% annually
- Capital appreciation potential
- Strong rental demand in Dubai

**INVESTOR SERVICES:**
- ROI analysis
- Market insights
- Property management
- Resale assistance

Contact our investment team at oneuae.com
            ''',
            'category': 'investment'
        },
        {
            'title': 'Contact One Development',
            'content': '''
**Contact One Development**

**OFFICIAL WEBSITE:** www.oneuae.com

**INQUIRIES:**
- Sales: Visit oneuae.com
- Property viewings: Book online
- Brochures: Download from website

**LOCATION:** Dubai, UAE

**OFFICE HOURS:**
Sunday-Thursday: 9 AM - 6 PM
Saturday: 10 AM - 4 PM

**SOCIAL MEDIA:**
Follow One Development on LinkedIn, Instagram, Facebook

For sales inquiries, fill out the contact form at oneuae.com
            ''',
            'category': 'contact'
        },
    ]
    
    count = 0
    for entry in entries:
        try:
            # Add to database
            kb_entry, created = KnowledgeBase.objects.update_or_create(
                title=entry['title'],
                defaults={
                    'content': entry['content'].strip(),
                    'summary': entry['content'][:500].strip(),
                    'source_type': 'curated',
                    'metadata': {'category': entry['category']},
                    'is_active': True
                }
            )
            
            # Add to vector store
            vector_store.add_texts(
                texts=[entry['content'].strip()],
                metadatas=[{'title': entry['title'], 'category': entry['category']}]
            )
            
            status = "✅ Added" if created else "🔄 Updated"
            print(f"  {status}: {entry['title']}")
            count += 1
            
        except Exception as e:
            print(f"  ❌ Error with {entry['title']}: {str(e)}")
    
    print(f"\n✅ Knowledge base populated with {count} entries!")
    print("Luna should now be able to answer questions about pricing, payment plans, etc.")

if __name__ == '__main__':
    populate_knowledge_base()







