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
            {
                'title': 'About One Development',
                'content': '''
                One Development is a premier real estate development company based in the United Arab Emirates.
                The company specializes in creating luxurious residential and commercial properties across Dubai
                and the wider UAE region. Known for innovative designs and high-quality construction, One Development
                has established itself as a trusted name in the UAE real estate market.
                ''',
                'source_type': 'manual',
                'category': 'company_info'
            },
            {
                'title': 'Services Offered',
                'content': '''
                One Development offers comprehensive real estate services including:
                - Luxury residential property development
                - Commercial real estate projects
                - Property management services
                - Investment opportunities
                - After-sales support and maintenance
                - Flexible payment plans
                - Interior design consultation
                ''',
                'source_type': 'manual',
                'category': 'services'
            },
            {
                'title': 'Location and Contact',
                'content': '''
                One Development operates primarily in the United Arab Emirates, with a focus on Dubai.
                The company's developments are located in prime areas offering excellent connectivity
                and access to key amenities. For inquiries, clients can reach out through the official
                website at www.oneuae.com or visit their offices in Dubai.
                ''',
                'source_type': 'manual',
                'category': 'contact'
            },
            {
                'title': 'Investment Opportunities',
                'content': '''
                One Development provides attractive investment opportunities in the UAE real estate market.
                Their properties offer:
                - High ROI potential
                - Prime locations with appreciation prospects
                - Flexible payment plans
                - Freehold ownership options
                - Handover-ready and off-plan properties
                - Professional property management
                ''',
                'source_type': 'manual',
                'category': 'investment'
            },
            {
                'title': 'Property Features and Amenities',
                'content': '''
                Properties by One Development typically include:
                - Modern architecture and design
                - Smart home technology
                - Swimming pools and fitness centers
                - 24/7 security and concierge services
                - Parking facilities
                - Children's play areas
                - Landscaped gardens
                - Proximity to schools, shopping, and healthcare
                ''',
                'source_type': 'manual',
                'category': 'amenities'
            },
            {
                'title': 'Why Choose One Development',
                'content': '''
                One Development stands out for several reasons:
                - Commitment to quality and excellence
                - Transparent business practices
                - On-time project delivery
                - Customer-centric approach
                - Experienced team of professionals
                - Strong track record in the UAE market
                - Innovative and sustainable designs
                - Comprehensive after-sales support
                ''',
                'source_type': 'manual',
                'category': 'company_info'
            },
            {
                'title': 'Career Opportunities at One Development',
                'content': '''
                One Development continues to scale its teams across sales, delivery, brand, and corporate functions in Dubai.
                
                Current focus areas include:
                - Sales & Advisory: Property Consultants, Senior Relationship Managers, and Investment Advisors who can guide high-net-worth clients through Dubai off-plan and ready inventory.
                - Project Delivery & Design: Development Managers, Project Coordinators, Site Engineers, Interior Designers, and QA/QC specialists who keep construction milestones on track.
                - Marketing & Brand: Digital Marketing Strategists, Content Producers, Event Leads, and Partnerships Managers who amplify the Nova/Luna brand rollouts.
                - Customer Experience & After-Sales: Handover Coordinators, Client Relationship Executives, and Service Operations Leads who manage snagging, handovers, and post-sales service.
                - Corporate Operations: Finance Analysts, Procurement Specialists, HR Business Partners, and Legal/Compliance Officers supporting day-to-day operations.
                - Early Talent: 3-6 month internships in marketing, design, operations, and data, with mentorship from senior leaders.
                
                Candidate expectations:
                - Demonstrated UAE real estate or large-project experience (RERA certification preferred for client-facing roles).
                - Strong negotiation, stakeholder management, and CRM/PropTech proficiency.
                - Multilingual communication (English plus Arabic, Russian, or Mandarin is highly valued).
                - Portfolio or case studies for design, marketing, and delivery roles.
                
                Application process:
                1. Submit a CV (and portfolio if applicable) via the careers section on www.oneuae.com or the One Development LinkedIn page.
                2. Highlight target role, notice period, visa status, and relevant project experience.
                3. HR screens profiles within 3 business days and coordinates two interview rounds (capabilities + leadership fit). Some roles include a short practical assignment.
                4. Successful candidates receive written offers with role scope, compensation structure, and onboarding timeline.
                ''',
                'source_type': 'manual',
                'category': 'career'
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

