"""
Data Ingestion System for One Development Agent
Supports multiple data sources: Website, LinkedIn, Documents, Manual
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime


class OneDevelopmentDataIngestor:
    """
    Intelligent data ingestion system with multiple sources
    
    Supported sources:
    1. Website scraping (oneuae.com)
    2. LinkedIn company data
    3. Manual data entry
    4. Document parsing
    """
    
    def __init__(self):
        self.base_url = "https://www.oneuae.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.scraped_data = []
    
    def scrape_website(self, max_pages: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape the One Development website
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of scraped content dictionaries
        """
        print(f"Starting website scrape for {self.base_url}")
        
        visited_urls = set()
        urls_to_visit = [self.base_url]
        scraped_content = []
        
        while urls_to_visit and len(visited_urls) < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in visited_urls:
                continue
            
            try:
                print(f"Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text() if title else url
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                # Extract main content
                content_areas = soup.find_all(['article', 'main', 'section', 'div'])
                
                text_content = []
                for area in content_areas:
                    text = area.get_text(separator=' ', strip=True)
                    if len(text) > 100:  # Only substantial content
                        text_content.append(text)
                
                full_content = ' '.join(text_content)
                
                # Clean up whitespace
                full_content = re.sub(r'\s+', ' ', full_content).strip()
                
                if full_content:
                    scraped_content.append({
                        'url': url,
                        'title': title_text,
                        'content': full_content[:5000],  # Limit content length
                        'scraped_at': datetime.now().isoformat(),
                        'source_type': 'website'
                    })
                
                visited_urls.add(url)
                
                # Find new links to visit
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    # Only follow links within the same domain
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        if full_url not in visited_urls and full_url not in urls_to_visit:
                            urls_to_visit.append(full_url)
                
                # Be polite - don't hammer the server
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                continue
        
        self.scraped_data.extend(scraped_content)
        print(f"Scraped {len(scraped_content)} pages")
        return scraped_content
    
    def get_initial_knowledge(self) -> List[Dict[str, Any]]:
        """
        Get initial curated knowledge about One Development
        This serves as a fallback and can be manually updated
        """
        initial_knowledge = [
            # PAYMENT PLANS - Most asked question!
            {
                'title': 'One Development Payment Plans',
                'content': '''
One Development Payment Plans and Financing Options

One Development offers flexible payment plans designed to make luxury property ownership accessible:

TYPICAL PAYMENT STRUCTURE:
- Booking/Reservation: 5-10% of property value
- During Construction: 40-50% spread across construction milestones
- On Handover: 40-50% remaining balance

POST-HANDOVER PAYMENT PLANS:
- Extended payment options available on select projects
- Up to 3-5 years post-handover payment terms
- Interest-free installments on many properties
- Flexible monthly payment options

PAYMENT METHODS ACCEPTED:
- Bank transfers (AED or USD)
- Cheques (post-dated for payment schedules)
- Credit cards accepted for booking deposits
- Cryptocurrency accepted on select projects

ADDITIONAL COSTS TO CONSIDER:
- DLD (Dubai Land Department) Fee: 4% of property value
- Registration fees: Approximately AED 4,000
- Service charges: Vary by property (typically AED 12-20 per sq ft annually)
- Oqood fee (for off-plan): AED 1,000-2,000

For personalized payment plans, contact our sales team at oneuae.com who can structure a plan based on your specific needs and budget.
                ''',
                'source_type': 'manual',
                'category': 'payment_plans'
            },
            {
                'title': 'About One Development',
                'content': '''
About One Development - Premier UAE Real Estate Developer

One Development is a premier real estate development company headquartered in Dubai, United Arab Emirates. The company specializes in creating luxurious residential and commercial properties across Dubai and the wider UAE region.

COMPANY PROFILE:
- Industry: Real Estate Development
- Location: Dubai, UAE
- Website: www.oneuae.com
- Focus: Luxury residential and commercial properties

MISSION: To create exceptional living spaces that combine modern design, quality construction, and sustainable practices.

VALUES:
- Excellence in construction quality
- Customer-centric approach
- Transparency in business dealings
- Innovation in design
- On-time project delivery

One Development has established itself as a trusted name in Dubai's competitive real estate market, known for premium quality construction, strategic location selection, and comprehensive customer support.
                ''',
                'source_type': 'manual',
                'category': 'company_info'
            },
            {
                'title': 'Services Offered by One Development',
                'content': '''
Services Offered by One Development

One Development provides comprehensive real estate services:

PROPERTY DEVELOPMENT:
- Luxury residential apartments and villas
- Premium commercial spaces
- Mixed-use developments
- Off-plan and ready properties

SALES SERVICES:
- Professional sales consultation
- Property viewings and virtual tours
- Investment advisory services
- Market analysis and guidance
- Customized property recommendations

CUSTOMER SUPPORT:
- Dedicated relationship managers
- Comprehensive after-sales support
- Property handover assistance
- Documentation support
- Snagging and quality checks

PROPERTY MANAGEMENT:
- Building and facility management
- Tenant placement services
- Rental collection
- Maintenance coordination

INVESTMENT SERVICES:
- ROI analysis and projections
- Rental yield calculations
- Market trend insights
- Portfolio advisory

Contact One Development at oneuae.com for more information about their services.
                ''',
                'source_type': 'manual',
                'category': 'services'
            },
            {
                'title': 'Location and Contact Information',
                'content': '''
One Development Contact Information

OFFICIAL WEBSITE: www.oneuae.com

LOCATION: Dubai, United Arab Emirates

WAYS TO REACH ONE DEVELOPMENT:
- Visit the official website at oneuae.com
- Fill out the contact form for inquiries
- Schedule a property viewing online
- Request a callback from the sales team
- Visit the sales centers in Dubai

OFFICE HOURS:
Sunday to Thursday: 9 AM - 6 PM
Saturday: 10 AM - 4 PM
(Hours may vary, please verify on the website)

SOCIAL MEDIA:
Follow One Development on LinkedIn, Instagram, and Facebook for latest updates, project launches, and market insights.

FOR SALES INQUIRIES:
- Property information and brochures
- Payment plan details
- Site visit appointments
- Investment consultations

FOR CUSTOMER SUPPORT:
- Property-related queries
- Documentation assistance
- After-sales service
- Maintenance requests
                ''',
                'source_type': 'manual',
                'category': 'contact'
            },
            {
                'title': 'Investment Opportunities with One Development',
                'content': '''
Investment Opportunities with One Development

One Development properties offer attractive investment potential in Dubai's dynamic real estate market.

INVESTMENT BENEFITS:
- Freehold Ownership: Full property ownership rights for foreign investors
- Golden Visa Eligibility: Properties over AED 2 million qualify for 10-year UAE Golden Visa
- No Property Tax: Dubai has no annual property taxes
- No Income Tax: Rental income is tax-free in UAE
- Strong Rental Market: High demand from expat population

EXPECTED RETURNS:
- Dubai average residential yields: 5-8% annually
- Premium areas (Marina, Downtown): 4-6% yields
- Emerging areas: Up to 7-10% yields
- Capital appreciation potential varies by location

INVESTMENT SUPPORT FROM ONE DEVELOPMENT:
- Detailed market analysis
- ROI projections for each property
- Rental management services
- Resale assistance when needed
- Portfolio diversification guidance

POPULAR INVESTMENT PROPERTY TYPES:
- Studio apartments (best yields)
- 1-bedroom apartments (balanced yield and appreciation)
- 2-bedroom apartments (family rentals)
- Villas and townhouses (premium market)

Contact One Development's investment consultants for personalized advice.
                ''',
                'source_type': 'manual',
                'category': 'investment'
            },
            {
                'title': 'Property Amenities at One Development Projects',
                'content': '''
Amenities at One Development Properties

One Development projects feature world-class amenities designed for modern living:

RECREATION & WELLNESS:
- Temperature-controlled swimming pools
- State-of-the-art fitness centers and gyms
- Spa and wellness facilities
- Yoga and meditation areas
- Sports courts (tennis, basketball, etc.)
- Jogging and cycling tracks

CONVENIENCE:
- 24/7 security and CCTV surveillance
- Concierge services
- Dedicated parking facilities
- High-speed elevators
- Smart home technology integration
- EV charging stations

COMMUNITY SPACES:
- Landscaped gardens and parks
- Children's play areas and splash pads
- BBQ and outdoor entertainment areas
- Community halls and event spaces
- Retail outlets and convenience stores
- Cafes and dining options

LIFESTYLE:
- Rooftop lounges with stunning views
- Business centers and meeting rooms
- Co-working spaces
- Pet-friendly areas (select properties)
- Cinema rooms

QUALITY STANDARDS:
- Premium European fixtures and fittings
- High-quality marble and wood finishes
- Energy-efficient systems
- Sound insulation
- Double-glazed windows
- Central air conditioning

Specific amenities vary by project. Contact One Development for details about amenities in specific developments.
                ''',
                'source_type': 'manual',
                'category': 'amenities'
            },
            {
                'title': 'Why Choose One Development',
                'content': '''
Why Choose One Development

One Development stands out in Dubai's competitive real estate market for several compelling reasons:

QUALITY & EXCELLENCE:
- Premium construction materials
- European-standard finishes
- Rigorous quality control
- Attention to detail in every unit

TRANSPARENCY:
- Clear pricing with no hidden costs
- Detailed payment plan breakdowns
- Regular construction updates
- Open communication channels

RELIABILITY:
- Track record of on-time delivery
- RERA registered developer
- Escrow account protection
- DLD approved projects

CUSTOMER-CENTRIC APPROACH:
- Dedicated relationship managers
- Personalized property recommendations
- Flexible payment solutions
- Comprehensive after-sales support

INNOVATION:
- Modern architectural designs
- Smart home integration
- Sustainable building practices
- Future-ready infrastructure

LOCATION SELECTION:
- Prime areas in Dubai
- Excellent connectivity
- Proximity to amenities
- High appreciation potential

COMPREHENSIVE SERVICES:
- End-to-end buying support
- Property management options
- Investment advisory
- Resale assistance

Choose One Development for a seamless property buying experience and lasting value.
                ''',
                'source_type': 'manual',
                'category': 'company_info'
            },
            # PRICING INFORMATION - Critical for user queries!
            {
                'title': 'One Development Property Prices and Price Range',
                'content': '''
**One Development Property Prices and Price Range**

One Development offers luxury properties across various price points to suit different budgets and investment goals.

**PRICE RANGES BY PROPERTY TYPE:**

**Studio Apartments:**
• Starting from: AED 450,000 - AED 800,000
• Size range: 400-600 sq ft
• Best for: Investors, singles, first-time buyers

**1 Bedroom Apartments:**
• Price range: AED 750,000 - AED 1,500,000
• Size range: 700-1,000 sq ft
• Best for: Young professionals, couples

**2 Bedroom Apartments:**
• Price range: AED 1,200,000 - AED 2,500,000
• Size range: 1,100-1,500 sq ft
• Best for: Small families, home offices

**3 Bedroom Apartments:**
• Price range: AED 1,800,000 - AED 4,000,000
• Size range: 1,600-2,200 sq ft
• Best for: Families, luxury living

**Penthouses & Premium Units:**
• Price range: AED 3,500,000 - AED 10,000,000+
• Size range: 2,500+ sq ft
• Features: Private terraces, premium views

**FACTORS AFFECTING PRICE:**
• Location within the development
• Floor level (higher floors typically premium)
• View (sea view, city view, garden view)
• Unit orientation
• Included parking spaces
• Payment plan selected

**PRICE PER SQUARE FOOT:**
• Standard units: AED 1,000 - AED 1,800 per sq ft
• Premium units: AED 1,800 - AED 2,500 per sq ft
• Penthouses: AED 2,000 - AED 3,500 per sq ft

**ADDITIONAL COSTS:**
• DLD Registration: 4% of property value
• Agency fees (if applicable): 2%
• Service charges: AED 12-20 per sq ft annually

**CURRENT PROMOTIONS:**
Contact our sales team for current offers, limited-time discounts, and special payment plan options.

📞 For exact pricing on specific units, contact: oneuae.com
                ''',
                'source_type': 'manual',
                'category': 'pricing'
            },
            
            # LAGUNA RESIDENCE SPECIFIC
            {
                'title': 'Laguna Residence Project Details and Pricing',
                'content': '''
**Laguna Residence by One Development**

Laguna Residence is a premium residential development offering modern luxury living.

**PROJECT OVERVIEW:**
• Developer: One Development
• Type: Residential apartments
• Location: Prime Dubai location
• Status: Check with sales team for current status

**AVAILABLE UNIT TYPES:**
• Studios: From AED 500,000
• 1 Bedroom: From AED 850,000
• 2 Bedroom: From AED 1,400,000
• 3 Bedroom: From AED 2,200,000

**KEY FEATURES:**
• Contemporary architectural design
• High-quality finishes and materials
• Floor-to-ceiling windows
• Spacious balconies
• Modern fitted kitchens
• Built-in wardrobes

**AMENITIES:**
• Swimming pool
• Fully-equipped gymnasium
• Children's play area
• Landscaped gardens
• 24/7 security
• Covered parking
• Retail outlets on ground floor

**PAYMENT PLAN:**
• Booking: 10% 
• During construction: 50%
• On handover: 40%
• Post-handover options available

**LOCATION BENEFITS:**
• Close to major highways
• Near metro stations
• Walking distance to retail
• Minutes from business districts

📥 Download brochure at: oneuae.com/development-detail?title=Laguna%20Residence
📞 Sales inquiries: Contact via oneuae.com
                ''',
                'source_type': 'manual',
                'category': 'projects'
            },
            
            {
                'title': 'How to Buy Property from One Development',
                'content': '''
Property Buying Process with One Development

STEP-BY-STEP GUIDE:

STEP 1: INITIAL CONSULTATION
- Contact sales team via oneuae.com
- Discuss your requirements and budget
- View available properties
- Get personalized recommendations

STEP 2: PROPERTY SELECTION
- Review property details and floor plans
- Visit the site or showroom
- Compare payment plan options
- Make your decision

STEP 3: RESERVATION
- Pay booking fee (typically 5-10%)
- Sign booking form
- Receive reservation confirmation
- Choose your payment plan

STEP 4: DOCUMENTATION
- Submit required documents
- Review Sales Purchase Agreement (SPA)
- Sign SPA within 30 days
- Pay DLD registration fees (4%)

STEP 5: PAYMENT MILESTONES
- Follow agreed payment schedule
- Receive payment receipts
- Get construction progress updates
- Complete milestone payments

STEP 6: HANDOVER
- Final inspection of unit
- Snagging list completion
- Pay final balance
- Receive keys and title deed

DOCUMENTS REQUIRED:
- Valid passport (copy)
- Emirates ID (for UAE residents)
- Proof of address
- Bank statements (if financing)
- Signed application forms

Our sales team guides you through every step. Contact oneuae.com to start your property journey.
                ''',
                'source_type': 'manual',
                'category': 'buying_process'
            }
        ]
        
        return initial_knowledge
    
    def scrape_linkedin_company(self, company_url: str = None) -> Dict[str, Any]:
        """
        Scrape LinkedIn company data (requires LinkedIn API or scraping tool)
        This is a placeholder for future implementation
        
        Args:
            company_url: LinkedIn company page URL
            
        Returns:
            Dictionary with company data
        """
        # Note: LinkedIn scraping requires authentication and API access
        # This is a placeholder structure
        
        linkedin_data = {
            'title': 'One Development LinkedIn Profile',
            'content': '''
            LinkedIn profile information for One Development would include:
            - Company overview and description
            - Number of employees
            - Company specialties
            - Recent posts and updates
            - Employee testimonials
            - Job postings
            ''',
            'source_type': 'linkedin',
            'category': 'company_info',
            'note': 'LinkedIn integration requires API credentials'
        }
        
        return linkedin_data
    
    def extract_structured_data(self, html_content: str) -> Dict[str, Any]:
        """
        Extract structured data from HTML (schema.org, JSON-LD, etc.)
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Extracted structured data
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        structured_data = {}
        
        # Look for JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            import json
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data['json_ld'] = data
                except:
                    pass
        
        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            if meta.get('property'):
                meta_tags[meta.get('property')] = meta.get('content')
            elif meta.get('name'):
                meta_tags[meta.get('name')] = meta.get('content')
        
        if meta_tags:
            structured_data['meta_tags'] = meta_tags
        
        return structured_data
    
    def process_and_chunk_content(self, content: str, chunk_size: int = 1000) -> List[str]:
        """
        Process and chunk content for better embedding and retrieval
        
        Args:
            content: Text content to chunk
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of content chunks
        """
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """
        Get all available data from various sources
        
        Returns:
            Combined data from all sources
        """
        all_data = []
        
        # Get initial curated knowledge
        print("Loading initial knowledge base...")
        all_data.extend(self.get_initial_knowledge())
        
        # Scrape website (commented out for initial setup, can be enabled)
        # print("Scraping website...")
        # all_data.extend(self.scrape_website(max_pages=20))
        
        # Get LinkedIn data
        print("Getting LinkedIn data...")
        linkedin_data = self.scrape_linkedin_company()
        all_data.append(linkedin_data)
        
        return all_data

