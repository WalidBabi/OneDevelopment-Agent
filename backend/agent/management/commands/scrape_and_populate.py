"""
Management command to scrape and populate the knowledge base with One Development data.
This command will:
1. Scrape the One Development website (oneuae.com)
2. Search the web for additional information
3. Add curated knowledge about common questions
4. Populate the vector store for semantic search
"""

from django.core.management.base import BaseCommand
from agent.models import KnowledgeBase
from knowledge.vector_store import get_vector_store
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse


class Command(BaseCommand):
    help = 'Scrape One Development website and populate knowledge base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-pages',
            type=int,
            default=30,
            help='Maximum number of pages to scrape'
        )
        parser.add_argument(
            '--skip-scrape',
            action='store_true',
            help='Skip website scraping, only add curated knowledge'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Starting One Development Knowledge Base Population...'))
        
        vector_store = get_vector_store()
        total_added = 0
        
        # Step 1: Add curated knowledge (always)
        self.stdout.write('\n📚 Adding curated knowledge base entries...')
        curated_count = self.add_curated_knowledge(vector_store)
        total_added += curated_count
        
        # Step 2: Scrape website (unless skipped)
        if not options['skip_scrape']:
            self.stdout.write('\n🌐 Scraping One Development website...')
            scraped_count = self.scrape_website(vector_store, options['max_pages'])
            total_added += scraped_count
        
        # Step 3: Add web-sourced information
        self.stdout.write('\n🔍 Adding web-sourced information...')
        web_count = self.add_web_sourced_info(vector_store)
        total_added += web_count
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully added {total_added} knowledge entries!'))
        self.stdout.write(self.style.SUCCESS('Knowledge base is now populated and ready.'))

    def add_curated_knowledge(self, vector_store):
        """Add comprehensive curated knowledge about One Development"""
        
        curated_entries = [
            # ============================================================
            # PAYMENT PLANS - Most asked question!
            # ============================================================
            {
                'title': 'One Development Payment Plans',
                'content': '''
**One Development Payment Plans**

One Development offers flexible payment plans to make property ownership accessible:

**Typical Payment Structure:**
• **Booking/Reservation**: 5-10% of property value
• **During Construction**: 40-50% spread across milestones
• **On Handover**: 40-50% remaining balance

**Post-Handover Payment Plans:**
• Extended payment options available on select projects
• Up to 3-5 years post-handover payment terms
• Interest-free installments on many properties

**Payment Methods Accepted:**
• Bank transfers
• Cheques
• Credit cards for booking deposits

**Additional Costs:**
• DLD (Dubai Land Department) Fee: 4% of property value
• Registration fees and admin charges may apply
• Service charges vary by property

For specific payment plans on current projects, please contact our sales team at oneuae.com or speak with a sales consultant who can provide customized payment options based on your needs.
                ''',
                'category': 'payment_plans',
                'source_type': 'curated'
            },
            
            # ============================================================
            # SERVICES
            # ============================================================
            {
                'title': 'One Development Services',
                'content': '''
**Services Offered by One Development**

One Development provides comprehensive real estate services:

**Property Development:**
• Luxury residential apartments and villas
• Premium commercial spaces
• Mixed-use developments
• Off-plan and ready properties

**Sales Services:**
• Professional sales consultation
• Property viewings and tours
• Investment advisory
• Market analysis and guidance

**Customer Support:**
• Dedicated relationship managers
• After-sales support
• Property handover assistance
• Documentation support

**Property Management:**
• Building maintenance
• Facility management
• Tenant services
• Community management

**Investment Services:**
• ROI analysis
• Rental yield projections
• Market trend insights
• Portfolio advisory

Contact One Development at oneuae.com for more information about our services.
                ''',
                'category': 'services',
                'source_type': 'curated'
            },
            
            # ============================================================
            # COMPANY INFORMATION
            # ============================================================
            {
                'title': 'About One Development - Company Overview',
                'content': '''
**About One Development**

One Development is a premier real estate developer headquartered in the United Arab Emirates.

**Company Profile:**
• Industry: Real Estate Development
• Location: Dubai, UAE
• Website: www.oneuae.com
• Focus: Luxury residential and commercial properties

**Mission:**
To create exceptional living spaces that combine modern design, quality construction, and sustainable practices.

**Values:**
• Excellence in construction quality
• Customer-centric approach
• Transparency in business dealings
• Innovation in design
• On-time project delivery

**Market Position:**
One Development has established itself as a trusted name in Dubai's competitive real estate market, known for:
• Prime location selection
• High-quality finishes
• Attention to detail
• Strong after-sales support

For more information, visit our official website at www.oneuae.com
                ''',
                'category': 'company_info',
                'source_type': 'curated'
            },
            
            # ============================================================
            # INVESTMENT & ROI
            # ============================================================
            {
                'title': 'Investment Opportunities with One Development',
                'content': '''
**Investment Opportunities with One Development**

One Development properties offer attractive investment potential in Dubai's dynamic real estate market.

**Investment Benefits:**
• **Freehold Ownership**: Full property ownership rights for foreign investors
• **Golden Visa Eligibility**: Properties over AED 2 million qualify for UAE Golden Visa
• **No Property Tax**: Dubai has no annual property taxes
• **No Income Tax**: Rental income is tax-free in UAE

**Rental Yields:**
• Dubai average residential yields: 5-8% annually
• Premium areas may offer 4-6% yields
• Emerging areas can offer up to 7-10% yields

**Capital Appreciation:**
• Dubai property market shows strong growth trends
• Prime locations historically appreciate well
• Off-plan properties often offer better entry prices

**Investment Support:**
One Development provides:
• Market analysis and insights
• Rental yield projections
• Property management services
• Resale assistance

For personalized investment advice, contact our investment consultants at oneuae.com
                ''',
                'category': 'investment',
                'source_type': 'curated'
            },
            
            # ============================================================
            # BUYING PROCESS
            # ============================================================
            {
                'title': 'Property Buying Process with One Development',
                'content': '''
**How to Buy Property from One Development**

**Step-by-Step Buying Process:**

**1. Initial Consultation**
• Contact our sales team or visit our sales center
• Discuss requirements, budget, and preferences
• View available properties and floor plans

**2. Property Selection**
• Choose your preferred unit
• Review payment plan options
• Understand all terms and conditions

**3. Reservation**
• Pay reservation/booking fee (typically 5-10%)
• Sign booking form
• Receive reservation confirmation

**4. Sales Purchase Agreement (SPA)**
• Review and sign the SPA
• Pay DLD registration fees (4%)
• Complete initial payment milestone

**5. Construction Phase (for off-plan)**
• Receive regular project updates
• Make milestone payments as per schedule
• Property progress communications

**6. Handover**
• Final inspection and snagging
• Complete remaining payments
• Receive keys and title deed

**Documents Required:**
• Valid passport (copy)
• Emirates ID (for residents)
• Proof of funds/bank statements
• Signed application forms

Contact our sales team for assistance throughout the buying process.
                ''',
                'category': 'buying_process',
                'source_type': 'curated'
            },
            
            # ============================================================
            # AMENITIES & FEATURES
            # ============================================================
            {
                'title': 'Property Amenities at One Development Projects',
                'content': '''
**Amenities at One Development Properties**

Our developments feature world-class amenities designed for modern living:

**Recreation & Wellness:**
• Temperature-controlled swimming pools
• State-of-the-art fitness centers/gyms
• Spa and wellness facilities
• Yoga and meditation areas
• Sports courts (tennis, basketball, etc.)

**Convenience:**
• 24/7 security and CCTV surveillance
• Concierge services
• Dedicated parking facilities
• High-speed elevators
• Smart home technology

**Community Spaces:**
• Landscaped gardens and parks
• Children's play areas
• BBQ and outdoor entertainment areas
• Community halls and event spaces
• Retail outlets and convenience stores

**Lifestyle:**
• Rooftop lounges
• Business centers
• Co-working spaces
• Pet-friendly areas (select properties)

**Quality Standards:**
• Premium European fixtures
• High-quality finishes
• Energy-efficient systems
• Sound insulation
• Double-glazed windows

Specific amenities vary by project. Contact us for details about amenities in specific developments.
                ''',
                'category': 'amenities',
                'source_type': 'curated'
            },
            
            # ============================================================
            # CONTACT INFORMATION
            # ============================================================
            {
                'title': 'Contact One Development',
                'content': '''
**Contact One Development**

**Official Website:**
www.oneuae.com

**Ways to Reach Us:**
• Visit our website for inquiries
• Schedule a property viewing
• Request a callback from our sales team
• Visit our sales centers in Dubai

**Office Hours:**
Typically 9 AM - 6 PM, Sunday to Thursday
(Please verify current hours on our website)

**Location:**
Dubai, United Arab Emirates

**Social Media:**
Follow One Development on LinkedIn, Instagram, and Facebook for:
• Latest project updates
• New property launches
• Market insights
• Company news

**For Sales Inquiries:**
• Fill out the contact form on oneuae.com
• Request property brochures
• Book a site visit
• Get payment plan details

**Customer Support:**
Our dedicated support team assists with:
• Property-related queries
• Documentation assistance
• After-sales service
• Maintenance requests

Visit www.oneuae.com for the most current contact information.
                ''',
                'category': 'contact',
                'source_type': 'curated'
            },
            
            # ============================================================
            # UAE REAL ESTATE CONTEXT
            # ============================================================
            {
                'title': 'Dubai Real Estate Market Overview',
                'content': '''
**Dubai Real Estate Market Context**

**Why Invest in Dubai Real Estate:**
• Tax-free environment (no income tax, no property tax)
• Strong rental yields (5-8% average)
• World-class infrastructure
• Safe and stable economy
• Strategic global location
• Golden Visa opportunities

**Freehold Areas:**
Foreign investors can own property in designated freehold areas including:
• Dubai Marina
• Downtown Dubai
• Palm Jumeirah
• Business Bay
• JBR (Jumeirah Beach Residence)
• Dubai Hills
• And many more

**Market Regulations:**
• RERA (Real Estate Regulatory Agency) oversight
• DLD (Dubai Land Department) registration
• Escrow account protection for buyers
• Transparent transaction processes

**Property Types Available:**
• Studio, 1BR, 2BR, 3BR+ apartments
• Penthouses and duplexes
• Townhouses
• Villas
• Commercial spaces

**Note:** This is general market information. For One Development specific details, please contact our sales team.
                ''',
                'category': 'market_context',
                'source_type': 'curated'
            },
            
            # ============================================================
            # FREQUENTLY ASKED QUESTIONS
            # ============================================================
            {
                'title': 'Frequently Asked Questions - One Development',
                'content': '''
**Frequently Asked Questions**

**Q: Do you offer payment plans?**
A: Yes! One Development offers flexible payment plans including post-handover options. Typical structures include 5-10% booking, 40-50% during construction, and 40-50% on handover. Contact our sales team for specific plans.

**Q: Can foreigners buy property?**
A: Yes, foreign nationals can purchase freehold property in designated areas of Dubai. No residency is required to buy property.

**Q: What is the minimum investment for Golden Visa?**
A: Properties valued at AED 2 million or above qualify for the UAE Golden Visa (10-year residency).

**Q: Are there any hidden costs?**
A: Main additional costs include DLD fees (4%), registration fees, and service charges. Our sales team provides full cost breakdowns.

**Q: Can I get financing?**
A: Yes, several UAE banks offer mortgage financing for property purchases. We can recommend mortgage advisors.

**Q: What warranty do you provide?**
A: Our properties come with developer warranties covering structural and mechanical systems. Specific terms vary by project.

**Q: Can I rent out my property?**
A: Yes, you can rent out your property. We can assist with property management services.

**Q: When is handover?**
A: Handover timelines vary by project. Contact our sales team for specific project completion dates.

For more questions, visit www.oneuae.com or contact our team.
                ''',
                'category': 'faq',
                'source_type': 'curated'
            },
        ]
        
        count = 0
        for entry in curated_entries:
            try:
                # Save to database
                kb_entry, created = KnowledgeBase.objects.get_or_create(
                    title=entry['title'],
                    defaults={
                        'content': entry['content'].strip(),
                        'summary': entry['content'][:500].strip(),
                        'source_type': entry['source_type'],
                        'metadata': {'category': entry['category']},
                        'is_active': True
                    }
                )
                
                if created:
                    # Add to vector store
                    vector_store.add_texts(
                        texts=[entry['content'].strip()],
                        metadatas=[{'title': entry['title'], 'category': entry['category']}]
                    )
                    count += 1
                    self.stdout.write(f"  ✅ Added: {entry['title']}")
                else:
                    self.stdout.write(f"  ⏭️  Already exists: {entry['title']}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error adding {entry['title']}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f'  Added {count} curated entries'))
        return count

    def scrape_website(self, vector_store, max_pages):
        """Scrape the One Development website"""
        
        base_url = "https://www.oneuae.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        visited_urls = set()
        urls_to_visit = [base_url]
        count = 0
        
        while urls_to_visit and len(visited_urls) < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in visited_urls:
                continue
            
            try:
                self.stdout.write(f"  Scraping: {url}")
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else url
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript']):
                    element.decompose()
                
                # Extract main content
                main_content = soup.find('main') or soup.find('article') or soup.find('body')
                
                if main_content:
                    text_content = main_content.get_text(separator='\n', strip=True)
                    # Clean up
                    text_content = re.sub(r'\n+', '\n', text_content)
                    text_content = re.sub(r'\s+', ' ', text_content)
                    
                    if len(text_content) > 200:  # Only substantial content
                        # Save to database
                        kb_entry, created = KnowledgeBase.objects.get_or_create(
                            source_url=url,
                            defaults={
                                'title': title_text[:200],
                                'content': text_content[:5000],
                                'summary': text_content[:500],
                                'source_type': 'website',
                                'is_active': True
                            }
                        )
                        
                        if created:
                            vector_store.add_texts(
                                texts=[text_content[:5000]],
                                metadatas=[{'title': title_text, 'url': url, 'source': 'website'}]
                            )
                            count += 1
                            self.stdout.write(f"    ✅ Saved: {title_text[:50]}...")
                
                visited_urls.add(url)
                
                # Find links to follow
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    # Only follow internal links
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        if full_url not in visited_urls and full_url not in urls_to_visit:
                            # Skip common non-content pages
                            skip_patterns = ['#', 'javascript:', 'mailto:', 'tel:', '.pdf', '.jpg', '.png']
                            if not any(p in full_url.lower() for p in skip_patterns):
                                urls_to_visit.append(full_url)
                
                time.sleep(1)  # Be polite
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    ⚠️ Error: {str(e)[:50]}"))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'  Scraped {count} pages from website'))
        return count

    def add_web_sourced_info(self, vector_store):
        """Add information gathered from web searches"""
        
        # Try to search for One Development info
        try:
            from duckduckgo_search import DDGS
            
            search_queries = [
                "One Development Dubai real estate projects",
                "One Development UAE property developer",
                "oneuae.com developer properties"
            ]
            
            count = 0
            for query in search_queries:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(query, max_results=3))
                    
                    for result in results:
                        title = result.get('title', '')
                        body = result.get('body', '')
                        href = result.get('href', '')
                        
                        if 'one development' in (title + body).lower() or 'oneuae' in href.lower():
                            content = f"{title}\n\n{body}\n\nSource: {href}"
                            
                            kb_entry, created = KnowledgeBase.objects.get_or_create(
                                source_url=href,
                                defaults={
                                    'title': title[:200],
                                    'content': content,
                                    'summary': body[:500],
                                    'source_type': 'web_search',
                                    'is_active': True
                                }
                            )
                            
                            if created:
                                vector_store.add_texts(
                                    texts=[content],
                                    metadatas=[{'title': title, 'url': href, 'source': 'web_search'}]
                                )
                                count += 1
                                self.stdout.write(f"  ✅ Added from web: {title[:50]}...")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠️ Search error: {str(e)[:50]}"))
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'  Added {count} web-sourced entries'))
            return count
            
        except ImportError:
            self.stdout.write(self.style.WARNING('  ⚠️ duckduckgo-search not installed, skipping web search'))
            return 0

