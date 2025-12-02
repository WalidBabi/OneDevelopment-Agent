"""
Luna's Tools - Real Web Search and Knowledge Base Tools
Implements actual web search, scraping, and knowledge retrieval
"""

from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import os


# ============================================================================
# KNOWLEDGE BASE TOOLS
# ============================================================================

@tool
def search_knowledge_base(query: str, n_results: int = 5) -> str:
    """Search One Development's internal knowledge base for company information, properties, and services.
    
    Use this for questions specifically about One Development's offerings.
    """
    from knowledge.vector_store import get_vector_store
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=n_results)
    return "\n\n".join([doc.page_content for doc in results]) if results else "No relevant information found in knowledge base."


@tool
def search_uploaded_documents(query: str, n_results: int = 3) -> str:
    """Search uploaded PDF documents for specific information about One Development.
    
    Use this when looking for detailed information that might be in official documents.
    """
    from knowledge.vector_store import get_vector_store
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=n_results)
    return "\n\n".join([doc.page_content for doc in results]) if results else "No relevant information found in documents."


# ============================================================================
# WEB SEARCH TOOLS
# ============================================================================

@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo for general information.
    
    Use this when you need to find information that's not in the knowledge base.
    This searches the entire web and returns relevant results.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default 5)
    
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return f"No web results found for '{query}'. Try a different search term."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            href = result.get('href', result.get('link', 'No URL'))
            body = result.get('body', result.get('snippet', 'No description'))
            formatted_results.append(f"{i}. **{title}**\n   URL: {href}\n   {body}")
        
        return f"Web search results for '{query}':\n\n" + "\n\n".join(formatted_results)
        
    except ImportError:
        # Fallback to basic scraping if duckduckgo-search not installed
        return _fallback_web_search(query)
    except Exception as e:
        return f"Web search error: {str(e)}. Try rephrasing your query."


def _fallback_web_search(query: str) -> str:
    """Fallback web search using basic scraping"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Use DuckDuckGo HTML version
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for result in soup.select('.result__body')[:5]:
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                if title_elem and snippet_elem:
                    results.append(f"- {title_elem.get_text(strip=True)}: {snippet_elem.get_text(strip=True)}")
            
            if results:
                return f"Web results for '{query}':\n" + "\n".join(results)
        
        return f"No results found for '{query}'"
    except Exception as e:
        return f"Search unavailable: {str(e)}"


@tool
def search_web_for_market_data(query: str) -> str:
    """Search for Dubai/UAE real estate market data and statistics.
    
    Use this for general market trends, prices, and statistics (NOT One Development specific).
    Results should always be labeled as 'general market data'.
    
    Args:
        query: Search query about Dubai real estate market
    
    Returns:
        Market data with clear labeling that it's general market info
    """
    search_query = f"Dubai UAE real estate {query} 2024 2025"
    
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=5))
        
        if not results:
            return "No market data found. Try a more specific query."
        
        formatted = ["**GENERAL MARKET DATA** (Not specific to One Development):\n"]
        for result in results[:3]:
            title = result.get('title', '')
            body = result.get('body', result.get('snippet', ''))
            formatted.append(f"• {title}\n  {body}")
        
        formatted.append("\n⚠️ This is general market data. For One Development specific information, contact the sales team.")
        
        return "\n\n".join(formatted)
        
    except Exception as e:
        return f"Market data search unavailable: {str(e)}"


@tool 
def scrape_webpage(url: str) -> str:
    """Scrape and extract text content from a specific webpage.
    
    Use this when you have a specific URL and need to extract information from it.
    
    Args:
        url: The URL to scrape
    
    Returns:
        Extracted text content from the webpage
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up multiple newlines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        # Limit to first 3000 characters to avoid overwhelming the context
        if len(cleaned_text) > 3000:
            cleaned_text = cleaned_text[:3000] + "\n\n[Content truncated...]"
        
        return f"Content from {url}:\n\n{cleaned_text}"
        
    except requests.exceptions.Timeout:
        return f"Timeout while accessing {url}. The page took too long to load."
    except requests.exceptions.RequestException as e:
        return f"Could not access {url}: {str(e)}"
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"


@tool
def search_one_development_website(query: str) -> str:
    """Search the official One Development website (oneuae.com) for specific information.
    
    Use this to find information directly from One Development's official website.
    
    Args:
        query: What to search for on the One Development website
    """
    search_query = f"site:oneuae.com {query}"
    
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=5))
        
        if not results:
            return f"No results found on oneuae.com for '{query}'. Try contacting the sales team directly."
        
        formatted = [f"**Results from One Development Website (oneuae.com):**\n"]
        for result in results:
            title = result.get('title', '')
            href = result.get('href', result.get('link', ''))
            body = result.get('body', result.get('snippet', ''))
            formatted.append(f"• **{title}**\n  {body}\n  URL: {href}")
        
        return "\n\n".join(formatted)
        
    except Exception as e:
        return f"Could not search One Development website: {str(e)}"


# ============================================================================
# PDF & DOCUMENT TOOLS - Luna can read PDFs directly!
# ============================================================================

@tool
def download_and_read_pdf(url: str) -> str:
    """Download a PDF from a URL and extract its text content.
    
    Use this when you need to read a PDF brochure, document, or fact sheet from a URL.
    This tool downloads the PDF and extracts all readable text from it.
    
    Args:
        url: The URL of the PDF file to download and read
    
    Returns:
        Extracted text content from the PDF
    """
    try:
        from PyPDF2 import PdfReader
        from io import BytesIO
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if it's actually a PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower() and not url.lower().endswith('.pdf'):
            return f"The URL does not appear to be a PDF file: {url}"
        
        # Read PDF from memory
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        text_content = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"--- Page {i+1} ---\n{page_text}")
        
        if not text_content:
            return f"PDF downloaded but no text could be extracted from {url}"
        
        full_text = "\n\n".join(text_content)
        
        # Limit output size
        if len(full_text) > 8000:
            full_text = full_text[:8000] + "\n\n[Content truncated - PDF has more content...]"
        
        return f"**PDF Content from {url}:**\n\n{full_text}"
        
    except requests.exceptions.Timeout:
        return f"Timeout downloading PDF from {url}"
    except requests.exceptions.RequestException as e:
        return f"Could not download PDF from {url}: {str(e)}"
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


@tool
def fetch_project_brochure(project_name: str) -> str:
    """Fetch and read the brochure/details for a One Development project.
    
    Use this when users ask about specific projects like "Laguna Residence" to get
    detailed information including features, amenities, and specifications.
    
    Args:
        project_name: Name of the project (e.g., "Laguna Residence")
    
    Returns:
        Project details and brochure content if available
    """
    # Known project URLs and their brochure endpoints
    projects = {
        'laguna residence': {
            'page': 'https://www.oneuae.com/development-detail?title=Laguna%20Residence',
            'search_term': 'Laguna Residence One Development Dubai'
        },
        'laguna': {
            'page': 'https://www.oneuae.com/development-detail?title=Laguna%20Residence',
            'search_term': 'Laguna Residence One Development Dubai'
        }
    }
    
    project_key = project_name.lower().strip()
    
    # First, try to get info from web search about the project
    try:
        from duckduckgo_search import DDGS
        
        # Search for project information
        search_term = f"One Development {project_name} Dubai brochure details"
        if project_key in projects:
            search_term = projects[project_key]['search_term']
        
        with DDGS() as ddgs:
            results = list(ddgs.text(search_term, max_results=5))
        
        if results:
            content = [f"**Information about {project_name}:**\n"]
            
            for result in results:
                title = result.get('title', '')
                body = result.get('body', '')
                href = result.get('href', '')
                
                if 'one' in title.lower() or 'one' in href.lower() or project_key in title.lower():
                    content.append(f"• **{title}**\n  {body}")
                    
                    # If we found a PDF link, try to read it
                    if '.pdf' in href.lower():
                        pdf_content = download_and_read_pdf.invoke({"url": href})
                        if "Error" not in pdf_content and "Could not" not in pdf_content:
                            content.append(f"\n📄 **Brochure Content:**\n{pdf_content}")
            
            if len(content) > 1:
                content.append(f"\n\n📍 For more details, visit: oneuae.com")
                return "\n\n".join(content)
        
        return f"I couldn't find detailed information about {project_name}. Please visit oneuae.com or contact the sales team for brochures and details."
        
    except Exception as e:
        return f"Error fetching project information: {str(e)}. Please visit oneuae.com for brochure downloads."


@tool
def get_project_details(project_name: str) -> str:
    """Get comprehensive details about a One Development project.
    
    This tool searches multiple sources to gather all available information about a project
    including features, pricing context, amenities, and location details.
    
    Args:
        project_name: Name of the project to get details for
    
    Returns:
        Comprehensive project information
    """
    from knowledge.vector_store import get_vector_store
    
    results = []
    
    # 1. Search internal knowledge base
    try:
        vector_store = get_vector_store()
        kb_results = vector_store.similarity_search(project_name, k=3)
        if kb_results:
            results.append("**From One Development Knowledge Base:**")
            for doc in kb_results:
                results.append(doc.page_content[:1000])
    except:
        pass
    
    # 2. Search web for project info
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            web_results = list(ddgs.text(f"One Development {project_name} Dubai", max_results=3))
        
        if web_results:
            results.append("\n**From Web Search:**")
            for r in web_results:
                if 'one' in r.get('title', '').lower() or 'one' in r.get('href', '').lower():
                    results.append(f"• {r.get('title', '')}: {r.get('body', '')}")
    except:
        pass
    
    # 3. Add standard project context
    results.append(f"""
**Standard One Development Project Features:**
• Premium quality construction and finishes
• Modern architectural design
• Comprehensive amenities (pool, gym, parking, security)
• Flexible payment plans available
• Freehold ownership for all nationalities

📞 **For detailed brochures and pricing for {project_name}:**
Contact One Development sales team at oneuae.com
""")
    
    return "\n\n".join(results) if results else f"Contact oneuae.com for details about {project_name}"


@tool
def find_and_read_brochure(search_query: str) -> str:
    """Search for and read PDF brochures related to a query.
    
    This tool searches for PDF brochures online and automatically reads their content.
    Use this when users want to know what's in a brochure or need detailed specifications.
    
    Args:
        search_query: What to search for (e.g., "Laguna Residence brochure", "One Development floor plans")
    
    Returns:
        Content from found brochures or guidance on how to get them
    """
    try:
        from duckduckgo_search import DDGS
        
        # Search for PDFs
        query = f"{search_query} filetype:pdf site:oneuae.com OR One Development"
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        
        pdf_urls = []
        other_results = []
        
        for result in results:
            href = result.get('href', '')
            if '.pdf' in href.lower():
                pdf_urls.append(href)
            else:
                other_results.append(result)
        
        # Try to read found PDFs
        if pdf_urls:
            for pdf_url in pdf_urls[:2]:  # Limit to 2 PDFs
                pdf_content = download_and_read_pdf.invoke({"url": pdf_url})
                if "Error" not in pdf_content and "Could not" not in pdf_content:
                    return pdf_content
        
        # If no PDFs found, return search results
        if other_results:
            content = [f"**Search results for '{search_query}':**\n"]
            for r in other_results[:3]:
                content.append(f"• **{r.get('title', '')}**\n  {r.get('body', '')}\n  URL: {r.get('href', '')}")
            content.append("\n\n📥 **To download brochures:** Visit oneuae.com and click 'Download Brochure' on any project page.")
            return "\n\n".join(content)
        
        return f"No brochures found for '{search_query}'. Visit oneuae.com to download brochures directly."
        
    except Exception as e:
        return f"Error searching for brochures: {str(e)}. Visit oneuae.com for brochure downloads."


# ============================================================================
# CONTEXT TOOLS
# ============================================================================

@tool
def get_dubai_market_context(topic: str) -> str:
    """Get general Dubai real estate market context for background information.
    
    Use for providing context about Dubai's property market - always label as 'general context'.
    
    Args:
        topic: Topic to get context about (e.g., 'luxury villas', 'payment plans', 'ROI')
    """
    # Common market context that's useful
    context_data = {
        'payment_plans': """**General Dubai Market Payment Plans (for context):**
• Most developers offer post-handover payment plans
• Typical structure: 20-40% during construction, 60-80% after handover
• Payment plans ranging from 3-7 years are common
• Some developers offer 10-year plans for premium projects
• DLD (Dubai Land Department) fees typically 4% of property value

⚠️ Contact One Development's sales team for their specific payment plan options.""",

        'roi': """**General Dubai ROI Context:**
• Dubai rental yields typically 5-8% for residential properties
• Premium areas like Palm Jumeirah, Downtown can yield 4-6%
• Emerging areas may offer higher yields (7-10%)
• Capital appreciation varies by area and market conditions

⚠️ For One Development specific ROI projections, speak with their investment advisors.""",

        'buying_process': """**General Dubai Property Buying Process:**
1. Choose property and reserve (typically 5-10% deposit)
2. Sign Sales Purchase Agreement (SPA)
3. Pay DLD fees (4%) and registration
4. Follow payment plan milestones
5. Final payment and handover

⚠️ One Development's sales team can guide you through their specific process.""",

        'default': """**General Dubai Real Estate Context:**
• Dubai offers freehold ownership for foreign buyers in designated areas
• No property taxes or income taxes
• Golden Visa available for property investments over AED 2M
• Strong regulatory framework (RERA, DLD)
• Diverse property options from studios to luxury penthouses

⚠️ For One Development specific information, please contact their sales team."""
    }
    
    # Find matching context
    topic_lower = topic.lower()
    if 'payment' in topic_lower or 'plan' in topic_lower:
        return context_data['payment_plans']
    elif 'roi' in topic_lower or 'return' in topic_lower or 'yield' in topic_lower or 'invest' in topic_lower:
        return context_data['roi']
    elif 'buy' in topic_lower or 'process' in topic_lower or 'purchase' in topic_lower:
        return context_data['buying_process']
    else:
        return context_data['default']


# ============================================================================
# USER PERSONALIZATION TOOLS
# ============================================================================

@tool
def get_user_context(session_id: str) -> str:
    """Get stored context and preferences for a user session.
    
    Use this to personalize responses based on previous interactions.
    """
    try:
        from knowledge.vector_store import get_vector_store
        vector_store = get_vector_store()
        results = vector_store.similarity_search(f"user preferences session {session_id}", k=2)
        if results:
            return f"User context: {results[0].page_content}"
        return "No previous user context found."
    except:
        return "User context not available."


@tool
def save_user_information(session_id: str, information: str) -> str:
    """Save user preferences or important information for future reference.
    
    Use this to remember user preferences like budget, location preferences, etc.
    """
    try:
        from knowledge.vector_store import get_vector_store
        vector_store = get_vector_store()
        # Store user preference
        vector_store.add_texts([f"User session {session_id}: {information}"])
        return f"Saved: {information}"
    except Exception as e:
        return f"Could not save user information: {str(e)}"


# ============================================================================
# TOOL GETTERS
# ============================================================================

def get_core_tools():
    """Return core essential tools."""
    return [
        search_knowledge_base,
        search_web,
        search_one_development_website
    ]


def get_all_tools():
    """Return all available tools for the agent."""
    return [
        # Knowledge base
        search_knowledge_base,
        search_uploaded_documents,
        # Web search
        search_web,
        search_web_for_market_data,
        search_one_development_website,
        scrape_webpage,
        # PDF & Document tools - Luna can read PDFs!
        download_and_read_pdf,
        fetch_project_brochure,
        get_project_details,
        find_and_read_brochure,
        # Context
        get_dubai_market_context,
        # User personalization
        get_user_context,
        save_user_information
    ]
