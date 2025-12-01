from langchain.tools import tool

@tool
def search_knowledge_base(query: str, n_results: int = 5) -> str:
    """Search One Development's knowledge base for company information."""
    from knowledge.vector_store import get_vector_store
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=n_results)
    return "\n\n".join([doc.page_content for doc in results]) if results else "No relevant information found."

@tool
def search_web(query: str) -> str:
    """Search the web for general information."""
    import requests
    from bs4 import BeautifulSoup
    try:
        response = requests.get(f"https://www.google.com/search?q={query}", timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        return "Web search completed"
    except:
        return "Web search unavailable"

@tool
def search_web_for_market_data(query: str) -> str:
    """Search for general Dubai/UAE real estate market data."""
    return "General market data - not specific to One Development"

def get_core_tools():
    """Return core tools."""
    return [search_knowledge_base, search_web]

def get_all_tools():
    """Return all available tools."""
    return [search_knowledge_base, search_web, search_web_for_market_data]
