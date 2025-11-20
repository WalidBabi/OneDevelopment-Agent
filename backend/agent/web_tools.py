"""
Web Access Tools for Real-time Fact Checking
Allows the agent to access websites and verify information
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse, urljoin


class WebAccessTool:
    """Tool for accessing websites and extracting information from web"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Primary source
        self.company_website = "https://www.oneuae.com"
        
        # Social and professional
        self.linkedin_url = "https://www.linkedin.com/company/onedevelopmentuae"
        
        # Real estate portals and industry sources
        self.additional_sources = {
            'property_finder': 'https://www.propertyfinder.ae/en/search?c=2&l=1&ob=mr&page=1&developers=one-development',
            'bayut': 'https://www.bayut.com/dubai/property/for-sale/',
            'dubai_properties': 'https://www.dubaiproperties.ae/',
            'gulf_news_property': 'https://gulfnews.com/business/property',
            'arabianbusiness_property': 'https://www.arabianbusiness.com/industries/property',
            'zawya_property': 'https://www.zawya.com/en/markets/real-estate'
        }
        
        # Cache for web results (simple memory cache)
        self._cache = {}
    
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch content from a URL
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            Page content as text or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_text_from_html(self, html: str) -> str:
        """
        Extract clean text from HTML content
        
        Args:
            html: HTML content
            
        Returns:
            Cleaned text content
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def search_company_website(self, query: str) -> Dict[str, Any]:
        """
        Search the company website for specific information
        
        Args:
            query: What to search for
            
        Returns:
            Dictionary with results
        """
        try:
            # Fetch main page
            html = self.fetch_page(self.company_website)
            if not html:
                return {
                    'success': False,
                    'error': 'Could not access company website'
                }
            
            text = self.extract_text_from_html(html)
            
            # Find relevant section (simple keyword matching)
            query_words = query.lower().split()
            sentences = text.split('.')
            relevant_sentences = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in query_words):
                    relevant_sentences.append(sentence.strip())
            
            return {
                'success': True,
                'source': self.company_website,
                'relevant_info': '. '.join(relevant_sentences[:5]) if relevant_sentences else None,
                'full_text': text[:2000]  # First 2000 chars
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_fact(self, statement: str) -> Dict[str, Any]:
        """
        Verify a statement against the company website
        
        Args:
            statement: Statement to verify
            
        Returns:
            Verification result
        """
        result = self.search_company_website(statement)
        
        if not result['success']:
            return {
                'verified': False,
                'confidence': 0.0,
                'reason': 'Could not access verification source'
            }
        
        # Simple verification: check if keywords from statement appear on website
        if result.get('relevant_info'):
            return {
                'verified': True,
                'confidence': 0.7,
                'source': result['source'],
                'supporting_text': result['relevant_info']
            }
        
        return {
            'verified': False,
            'confidence': 0.3,
            'reason': 'No supporting information found on website'
        }
    
    def search_linkedin(self) -> Dict[str, Any]:
        """
        Search LinkedIn company page for information
        
        Returns:
            Dictionary with LinkedIn information
        """
        try:
            html = self.fetch_page(self.linkedin_url)
            if not html:
                return {
                    'success': False,
                    'error': 'Could not access LinkedIn page'
                }
            
            text = self.extract_text_from_html(html)
            
            return {
                'success': True,
                'source': self.linkedin_url,
                'content': text[:2000],  # First 2000 chars
                'source_type': 'LinkedIn Company Page'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_property_portals(self, query: str) -> Dict[str, Any]:
        """
        Search UAE property portals for One Development information
        
        Args:
            query: What to search for
            
        Returns:
            Dictionary with results from property portals
        """
        # Check cache first
        cache_key = f"portals_{query.lower().replace(' ', '_')}"
        if cache_key in self._cache:
            print("📦 Using cached property portal results")
            return self._cache[cache_key]
        
        results = {
            'success': False,
            'content': '',
            'sources_checked': []
        }
        
        # Try Property Finder
        try:
            print("🏘️  Searching Property Finder...")
            pf_url = self.additional_sources['property_finder']
            html = self.fetch_page(pf_url)
            if html:
                text = self.extract_text_from_html(html)
                if len(text) > 100:
                    results['content'] += f"[Property Finder Data]: {text[:500]}...\n"
                    results['sources_checked'].append('Property Finder')
                    results['success'] = True
        except Exception as e:
            print(f"Could not search Property Finder: {str(e)}")
        
        # Cache the results
        if results['success']:
            self._cache[cache_key] = results
        
        return results
    
    def get_market_context(self) -> Dict[str, Any]:
        """
        Get general UAE/Dubai real estate market context
        
        Returns:
            Dictionary with market context and trends
        """
        context = {
            'success': True,
            'content': '''
            UAE Real Estate Market Context:
            
            Dubai remains one of the world's most dynamic property markets, with luxury developments 
            setting new standards in design and amenities. The market has seen steady growth with 
            average luxury property prices ranging from AED 1.5M to AED 10M+ depending on location 
            and specifications.
            
            Key Dubai Areas:
            - Dubai Marina: Premium waterfront living, prices typically AED 1,200-2,500 per sq ft
            - Downtown Dubai: Luxury urban lifestyle, prices typically AED 1,500-3,000 per sq ft
            - Palm Jumeirah: Exclusive island living, prices typically AED 1,800-3,500 per sq ft
            - Business Bay: Business hub with residential options, AED 1,000-2,000 per sq ft
            
            Investment Returns: Typical ROI in Dubai ranges from 5-8% annually for rental properties.
            
            Payment Plans: Most developers offer flexible payment plans, often with 10-20% down payment
            and remaining amount payable over 2-4 years, sometimes post-handover.
            ''',
            'type': 'Market Intelligence'
        }
        
        return context
    
    def search_multiple_sources(self, query: str) -> Dict[str, Any]:
        """
        Search multiple web sources for information (Enhanced Version)
        
        Args:
            query: What to search for
            
        Returns:
            Combined results from multiple sources
        """
        results = {
            'sources': [],
            'combined_text': '',
            'success': False,
            'has_market_context': False
        }
        
        # Search company website first
        print("🌐 Searching company website...")
        website_result = self.search_company_website(query)
        if website_result.get('success'):
            results['sources'].append({
                'name': 'Company Website',
                'url': self.company_website,
                'type': 'Official Source'
            })
            results['combined_text'] += f"\n[From Company Website]:\n{website_result.get('relevant_info', website_result.get('full_text', ''))}\n\n"
            results['success'] = True
        
        # Search property portals for additional context
        print("🏘️  Searching property portals...")
        portal_result = self.search_property_portals(query)
        if portal_result.get('success'):
            results['sources'].append({
                'name': 'Property Portals',
                'type': 'Market Data'
            })
            results['combined_text'] += f"\n[From Property Portals]:\n{portal_result.get('content', '')}\n\n"
            results['success'] = True
        
        # Add market context for relevant queries
        if any(keyword in query.lower() for keyword in ['price', 'cost', 'investment', 'roi', 'payment', 'market', 'location']):
            print("📊 Adding market context...")
            market_context = self.get_market_context()
            results['combined_text'] += f"\n[Market Context]:\n{market_context.get('content', '')}\n\n"
            results['has_market_context'] = True
            results['success'] = True
        
        return results

