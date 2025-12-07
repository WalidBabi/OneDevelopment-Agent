"""
Source Tracker and Citation System for Luna

This module extracts, verifies, and formats sources from tool responses,
ensuring Luna always provides verified citations like Copilot.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class Source:
    """Represents a verified source citation"""
    title: str
    url: str
    source_type: str  # 'official', 'market_data', 'general_web', 'internal'
    snippet: Optional[str] = None
    reliability: str = 'verified'  # 'verified', 'general', 'unverified'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'type': self.source_type,
            'snippet': self.snippet,
            'reliability': self.reliability
        }


class SourceTracker:
    """Tracks and extracts sources from tool responses"""
    
    # Official/trusted domains for One Development
    OFFICIAL_DOMAINS = [
        'oneuae.com',
        'one-development.ae',
        'onedev.ae'
    ]
    
    # Trusted market data sources
    TRUSTED_DOMAINS = [
        'dubailand.gov.ae',
        'bayut.com',
        'propertyfinder.ae',
        'zawya.com',
        'arabianbusiness.com',
        'khaleejtimes.com',
        'gulfnews.com',
        'constructionweekonline.com',
        'businessnewse.com',
        'cbnme.com'
    ]
    
    def __init__(self):
        self.sources: List[Source] = []
        self.seen_urls = set()
    
    def extract_sources_from_tool_result(
        self, 
        tool_name: str, 
        tool_result: str
    ) -> List[Source]:
        """
        Extract sources from a tool's response.
        
        Args:
            tool_name: Name of the tool that was called
            tool_result: The result/output from the tool
            
        Returns:
            List of extracted Source objects
        """
        extracted = []
        
        # Extract URLs using regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?)]'
        urls = re.findall(url_pattern, tool_result)
        
        # Also look for "URL: " or "Source: " patterns
        structured_urls = re.findall(r'(?:URL|Source|Link):\s*(https?://[^\s\n]+)', tool_result, re.IGNORECASE)
        urls.extend(structured_urls)
        
        # Remove duplicates while preserving order
        unique_urls = []
        for url in urls:
            if url not in unique_urls:
                unique_urls.append(url)
        
        # Extract title and context for each URL
        for url in unique_urls:
            if url in self.seen_urls:
                continue
            
            self.seen_urls.add(url)
            
            # Determine source type and reliability
            source_type, reliability = self._classify_source(url, tool_name)
            
            # Extract title (look for markdown links or nearby text)
            title = self._extract_title(url, tool_result)
            
            # Extract snippet (text near the URL)
            snippet = self._extract_snippet(url, tool_result)
            
            source = Source(
                title=title,
                url=url,
                source_type=source_type,
                snippet=snippet,
                reliability=reliability
            )
            
            extracted.append(source)
            self.sources.append(source)
        
        return extracted
    
    def _classify_source(self, url: str, tool_name: str) -> tuple[str, str]:
        """
        Classify a source by type and reliability.
        
        Returns:
            (source_type, reliability)
        """
        domain = self._extract_domain(url)
        
        # Check if it's from knowledge base or internal
        if tool_name in ['search_knowledge_base', 'search_uploaded_documents']:
            return ('internal', 'verified')
        
        # Check if it's official One Development
        if any(official in domain for official in self.OFFICIAL_DOMAINS):
            return ('official', 'verified')
        
        # Check if it's a trusted market source
        if any(trusted in domain for trusted in self.TRUSTED_DOMAINS):
            return ('market_data', 'verified')
        
        # For Tavily searches
        if tool_name in ['tavily_search', 'tavily_research']:
            return ('general_web', 'verified')
        
        # For general web searches
        if tool_name in ['search_web', 'search_web_for_market_data']:
            return ('market_data', 'general')
        
        # Default
        return ('general_web', 'general')
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ''
    
    def _extract_title(self, url: str, text: str) -> str:
        """Extract title for a URL from surrounding text"""
        
        # Look for markdown link format: [title](url)
        markdown_pattern = rf'\[([^\]]+)\]\({re.escape(url)}\)'
        match = re.search(markdown_pattern, text)
        if match:
            return match.group(1).strip()
        
        # Look for **Title** before URL
        title_pattern = rf'\*\*([^*]+)\*\*[^\n]*{re.escape(url)}'
        match = re.search(title_pattern, text)
        if match:
            return match.group(1).strip()
        
        # Look for "Title - URL:" pattern
        line_pattern = rf'([^\n]+)[:\s]+{re.escape(url)}'
        match = re.search(line_pattern, text)
        if match:
            title = match.group(1).strip()
            # Clean up common prefixes
            title = re.sub(r'^\d+\.\s*', '', title)  # Remove "1. "
            title = re.sub(r'^[•\-*]\s*', '', title)  # Remove "• "
            if len(title) > 10 and len(title) < 200:
                return title
        
        # Extract domain as fallback
        domain = self._extract_domain(url)
        return domain.replace('www.', '').title() if domain else 'Source'
    
    def _extract_snippet(self, url: str, text: str, max_length: int = 150) -> str:
        """Extract a relevant snippet near the URL"""
        
        # Find the line containing the URL
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if url in line:
                # Get context: current line and next line
                snippet_lines = []
                if i > 0:
                    snippet_lines.append(lines[i-1])
                snippet_lines.append(line)
                if i < len(lines) - 1:
                    snippet_lines.append(lines[i+1])
                
                snippet = ' '.join(snippet_lines)
                
                # Clean up the snippet
                snippet = re.sub(r'https?://[^\s]+', '', snippet)  # Remove URLs
                snippet = re.sub(r'\*\*([^*]+)\*\*', r'\1', snippet)  # Remove markdown bold
                snippet = re.sub(r'^\d+\.\s*', '', snippet)  # Remove numbering
                snippet = re.sub(r'^[•\-*]\s*', '', snippet)  # Remove bullets
                snippet = snippet.strip()
                
                # Truncate if too long
                if len(snippet) > max_length:
                    snippet = snippet[:max_length].rsplit(' ', 1)[0] + '...'
                
                return snippet if snippet else None
        
        return None
    
    def get_all_sources(self) -> List[Source]:
        """Get all tracked sources"""
        return self.sources
    
    def get_sources_by_type(self, source_type: str) -> List[Source]:
        """Get sources filtered by type"""
        return [s for s in self.sources if s.source_type == source_type]
    
    def format_sources_for_response(self) -> str:
        """
        Format sources for inclusion in Luna's response.
        Returns a markdown-formatted sources section.
        """
        if not self.sources:
            return ""
        
        # Group sources by type
        official = self.get_sources_by_type('official')
        internal = self.get_sources_by_type('internal')
        market = self.get_sources_by_type('market_data')
        web = self.get_sources_by_type('general_web')
        
        formatted = ["\n\n---\n\n### 📚 Sources\n"]
        
        # Official sources first
        if official:
            formatted.append("\n**Official Sources:**")
            for i, source in enumerate(official, 1):
                formatted.append(f"{i}. [{source.title}]({source.url})")
        
        # Internal knowledge base
        if internal:
            formatted.append("\n**Internal Knowledge Base:**")
            for i, source in enumerate(internal, 1):
                formatted.append(f"{i}. {source.title}")
        
        # Market data
        if market:
            formatted.append("\n**Market Data & News:**")
            for i, source in enumerate(market[:5], 1):  # Limit to 5
                formatted.append(f"{i}. [{source.title}]({source.url})")
        
        # General web sources
        if web:
            formatted.append("\n**Additional References:**")
            for i, source in enumerate(web[:3], 1):  # Limit to 3
                formatted.append(f"{i}. [{source.title}]({source.url})")
        
        return '\n'.join(formatted)
    
    def get_sources_json(self) -> List[Dict[str, Any]]:
        """Get sources as JSON-serializable list"""
        return [source.to_dict() for source in self.sources]
    
    def clear(self):
        """Clear all tracked sources"""
        self.sources.clear()
        self.seen_urls.clear()


def extract_sources_from_tools(tool_calls: List[Dict[str, Any]]) -> SourceTracker:
    """
    Extract sources from multiple tool calls.
    
    Args:
        tool_calls: List of dicts with 'tool' and 'result' keys
        
    Returns:
        SourceTracker with all extracted sources
    """
    tracker = SourceTracker()
    
    for call in tool_calls:
        tool_name = call.get('tool', '')
        result = call.get('result', '')
        
        if result and isinstance(result, str):
            tracker.extract_sources_from_tool_result(tool_name, result)
    
    return tracker


# Example usage
if __name__ == "__main__":
    # Test the source tracker
    tracker = SourceTracker()
    
    # Simulate tool results
    tool_result = """
    **Results from One Development Website:**
    
    1. **Laguna Residence - Luxury Living**
       URL: https://oneuae.com/development-detail?title=Laguna%20Residence
       Premium beachfront development in City of Arabia
    
    2. **Market Analysis Report**
       https://constructionweekonline.com/dubai-real-estate-2025
       Dubai real estate market shows strong growth
    """
    
    sources = tracker.extract_sources_from_tool_result('search_web', tool_result)
    
    print("Extracted sources:")
    for source in sources:
        print(f"- {source.title} ({source.source_type}): {source.url}")
    
    print("\n" + tracker.format_sources_for_response())







