"""
Luna Streaming Agent
True token-by-token streaming like Cursor - shows actual LLM thinking

This agent:
1. Streams actual reasoning tokens as the LLM thinks
2. Persists in finding answers through multiple sources
3. Uses web search when knowledge base doesn't have information
4. Scrapes official website when needed
5. Never gives up without trying all available tools
"""

import os
import json
from typing import Generator, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from datetime import datetime

from agent.tools import (
    search_knowledge_base, 
    search_web, 
    search_one_development_website,
    search_web_for_market_data,
    get_dubai_market_context,
    fetch_project_brochure,
    get_project_details,
    find_and_read_brochure,
    download_and_read_pdf
)
from agent.verification_guardrails import get_verification_guardrails, VerificationLevel


class LunaStreamingAgent:
    """
    Streaming agent that shows actual LLM thinking token by token.
    Like Cursor's agent mode - you see every token as Luna thinks.
    
    Key improvement: Never say "I don't know" without trying all available tools.
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        # Streaming LLM for visible thinking and responses
        self.streaming_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=self.api_key,
            streaming=True
        )
    
    def _get_thinking_prompt(self, query: str, context: str = "") -> str:
        """Prompt that makes the LLM think out loud and plan tool usage"""
        return f"""You are Luna, an AI assistant for One Development (oneuae.com).

TASK: Think through how to answer this user question. Be THOROUGH - never give up without trying to find the answer.

USER QUESTION: {query}

{f"AVAILABLE CONTEXT: {context}" if context else ""}

YOUR AVAILABLE TOOLS:
1. search_knowledge_base - One Development's internal knowledge
2. search_one_development_website - Search oneuae.com directly  
3. search_web - General web search for any information
4. search_web_for_market_data - Dubai market trends and data
5. get_dubai_market_context - General Dubai real estate context

🆕 PDF & BROCHURE TOOLS (I CAN READ PDFs!):
6. fetch_project_brochure - Get project brochure details (e.g., "Laguna Residence")
7. get_project_details - Comprehensive project info from multiple sources
8. find_and_read_brochure - Search for and READ PDF brochures automatically
9. download_and_read_pdf - Download and read any PDF from a URL

INSTRUCTIONS - Think step by step:
1. What is the user actually asking for?
2. Is this about a specific project? → Use fetch_project_brochure or get_project_details
3. Are they asking about brochures or documents? → Use find_and_read_brochure
4. Is this general info? → Use knowledge base, then website, then web search
5. How will I provide maximum value?

IMPORTANT: 
- I CAN read PDF brochures directly - I should USE these tools!
- If asking about projects like "Laguna Residence", use project-specific tools
- NEVER just tell users to "download the brochure" - I can read it for them!
- ALWAYS try to find the answer using available tools
- Provide helpful context even if exact info isn't found

Think out loud now. Be concise but show your reasoning:"""

    def _get_response_prompt(self, query: str, context: str, thinking: str, tool_results: Dict[str, str]) -> str:
        """Generate final response based on thinking and all gathered context"""
        
        # Format tool results
        tool_context = ""
        for tool_name, result in tool_results.items():
            if result and "No relevant information" not in result and "not found" not in result.lower():
                tool_context += f"\n\n**From {tool_name}:**\n{result}"
        
        if not tool_context:
            tool_context = "No specific information found from tools."
        
        return f"""You are Luna, an AI assistant for One Development (oneuae.com).

USER QUESTION: {query}

YOUR ANALYSIS:
{thinking}

INFORMATION GATHERED:
{tool_context}

RESPONSE GUIDELINES:
1. **If you found relevant information**: Share it clearly and helpfully
2. **If partially relevant info found**: Share what you found, acknowledge gaps, suggest next steps
3. **If no specific info found**: 
   - Provide general helpful context about the topic
   - Suggest contacting the sales team at oneuae.com
   - NEVER just say "I don't know" - always provide VALUE

FORMATTING:
- Use **bold** for key points
- Use bullet points for lists
- Keep paragraphs short (2-3 sentences max)
- End with a clear call to action when appropriate

REMEMBER: You represent One Development. Be confident, helpful, and always guide the user forward.

Respond naturally and helpfully:"""

    def stream_thinking_and_response(
        self,
        query: str,
        session_id: str = "default"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream the complete thinking and response process.
        
        This is the CORE improvement: Uses multiple tools to find answers.
        
        Yields events:
        - {"type": "phase", "content": "..."} - Current phase
        - {"type": "thinking_token", "content": "..."} - Each thinking token
        - {"type": "tool_start", "tool": "...", "query": "..."} - Tool being called
        - {"type": "tool_result", "content": "..."} - Tool result
        - {"type": "response_token", "content": "..."} - Response tokens
        - {"type": "done"} - Complete
        """
        
        thinking_content = ""
        tool_results = {}
        
        # ====================================================================
        # PHASE 1: Stream thinking tokens
        # ====================================================================
        yield {"type": "phase", "content": "thinking"}
        
        thinking_prompt = self._get_thinking_prompt(query)
        
        for chunk in self.streaming_llm.stream([
            SystemMessage(content="You are Luna, thinking through a user's question. Plan which tools to use."),
            HumanMessage(content=thinking_prompt)
        ]):
            if chunk.content:
                thinking_content += chunk.content
                yield {"type": "thinking_token", "content": chunk.content}
        
        yield {"type": "thinking_complete", "content": thinking_content}
        
        # ====================================================================
        # PHASE 2: Execute tools based on thinking - BE PERSISTENT!
        # ====================================================================
        yield {"type": "phase", "content": "searching"}
        
        query_lower = query.lower()
        
        # Detect if this is about a specific project or brochure
        project_keywords = ['laguna', 'residence', 'project', 'development', 'tower', 'villa']
        brochure_keywords = ['brochure', 'pdf', 'download', 'document', 'fact sheet', 'floor plan']
        is_project_query = any(kw in query_lower for kw in project_keywords)
        is_brochure_query = any(kw in query_lower for kw in brochure_keywords)
        
        # Step 1: If asking about a specific project, use project tools first
        if is_project_query:
            # Extract project name (e.g., "Laguna Residence")
            project_name = query  # Use full query as search term
            if 'laguna' in query_lower:
                project_name = "Laguna Residence"
            
            yield {"type": "tool_start", "tool": "get_project_details", "query": project_name}
            try:
                project_result = get_project_details.invoke({"project_name": project_name})
                tool_results['project_details'] = project_result
                preview = project_result[:200] + "..." if len(project_result) > 200 else project_result
                yield {"type": "tool_result", "content": preview}
            except Exception as e:
                tool_results['project_details'] = f"Error: {str(e)}"
                yield {"type": "tool_error", "content": str(e)}
        
        # Step 2: If asking about brochures, try to find and read them
        if is_brochure_query:
            yield {"type": "tool_start", "tool": "find_and_read_brochure", "query": query}
            try:
                brochure_result = find_and_read_brochure.invoke({"search_query": query})
                tool_results['brochure_content'] = brochure_result
                preview = brochure_result[:200] + "..." if len(brochure_result) > 200 else brochure_result
                yield {"type": "tool_result", "content": preview}
            except Exception as e:
                tool_results['brochure_content'] = f"Error: {str(e)}"
                yield {"type": "tool_error", "content": str(e)}
        
        # Step 3: Always search knowledge base
        yield {"type": "tool_start", "tool": "search_knowledge_base", "query": query}
        try:
            kb_result = search_knowledge_base.invoke({"query": query, "n_results": 5})
            tool_results['knowledge_base'] = kb_result
            preview = kb_result[:200] + "..." if len(kb_result) > 200 else kb_result
            yield {"type": "tool_result", "content": preview}
        except Exception as e:
            tool_results['knowledge_base'] = f"Error: {str(e)}"
            yield {"type": "tool_error", "content": str(e)}
        
        # Step 4: If knowledge base didn't have good results, search the website
        kb_has_info = (
            tool_results.get('knowledge_base') and 
            "No relevant information" not in tool_results.get('knowledge_base', '') and
            len(tool_results.get('knowledge_base', '')) > 50
        )
        
        if not kb_has_info and not is_project_query:
            yield {"type": "tool_start", "tool": "search_one_development_website", "query": query}
            try:
                website_result = search_one_development_website.invoke({"query": query})
                tool_results['website_search'] = website_result
                preview = website_result[:200] + "..." if len(website_result) > 200 else website_result
                yield {"type": "tool_result", "content": preview}
            except Exception as e:
                tool_results['website_search'] = f"Error: {str(e)}"
                yield {"type": "tool_error", "content": str(e)}
        
        # Step 5: For market/price questions, also get market data
        market_keywords = ['price', 'cost', 'payment', 'plan', 'roi', 'return', 'invest', 
                         'market', 'trend', 'average', 'typical', 'range']
        needs_market_data = any(kw in query_lower for kw in market_keywords)
        
        if needs_market_data:
            yield {"type": "tool_start", "tool": "search_web_for_market_data", "query": query}
            try:
                market_result = search_web_for_market_data.invoke({"query": query})
                tool_results['market_data'] = market_result
                preview = market_result[:200] + "..." if len(market_result) > 200 else market_result
                yield {"type": "tool_result", "content": preview}
            except Exception as e:
                tool_results['market_data'] = f"Error: {str(e)}"
        
        # Step 6: If still no good results, do a general web search
        has_any_good_result = any(
            result and "No relevant" not in result and "Error" not in result and len(result) > 50
            for result in tool_results.values()
        )
        
        if not has_any_good_result:
            web_query = f"One Development UAE {query}"
            yield {"type": "tool_start", "tool": "search_web", "query": web_query}
            try:
                web_result = search_web.invoke({"query": web_query})
                tool_results['web_search'] = web_result
                preview = web_result[:200] + "..." if len(web_result) > 200 else web_result
                yield {"type": "tool_result", "content": preview}
            except Exception as e:
                tool_results['web_search'] = f"Error: {str(e)}"
        
        # Step 7: Get general context for certain topics
        context_keywords = ['payment', 'process', 'buy', 'invest', 'roi']
        if any(kw in query_lower for kw in context_keywords):
            try:
                context_result = get_dubai_market_context.invoke({"topic": query})
                tool_results['market_context'] = context_result
            except:
                pass
        
        # ====================================================================
        # PHASE 3: Stream response tokens
        # ====================================================================
        yield {"type": "phase", "content": "responding"}
        
        response_prompt = self._get_response_prompt(query, "", thinking_content, tool_results)
        response_content = ""
        
        for chunk in self.streaming_llm.stream([
            SystemMessage(content="""You are Luna, One Development's AI assistant. 
Be helpful, confident, and always provide value. Never leave the user without guidance.
Use the information gathered to give the best possible answer."""),
            HumanMessage(content=response_prompt)
        ]):
            if chunk.content:
                response_content += chunk.content
                yield {"type": "response_token", "content": chunk.content}
        
        # ====================================================================
        # PHASE 4: Verify and improve response (NEW!)
        # ====================================================================
        yield {"type": "phase", "content": "verifying"}
        
        # Get context for verification
        context_list = [str(result) for result in tool_results.values() if result]
        
        # Verify the response
        verification_system = get_verification_guardrails()
        verification_result = verification_system.verify_response(
            query=query,
            response=response_content,
            context=context_list,
            tool_results=tool_results
        )
        
        # Send verification status
        yield {
            "type": "verification",
            "confidence": verification_result.confidence_score,
            "level": verification_result.verification_level.value,
            "sources": verification_result.sources,
            "issues": verification_result.issues_found
        }
        
        # If verification found issues or low confidence, improve response
        if not verification_result.is_verified or verification_result.verification_level == VerificationLevel.LOW:
            yield {"type": "phase", "content": "improving"}
            
            improved_response = verification_system.improve_response(
                query=query,
                response=response_content,
                verification_result=verification_result,
                context=context_list,
                tool_results=tool_results
            )
            
            # If improved response is different, stream the difference
            if improved_response != response_content:
                response_content = improved_response
                yield {"type": "response_improved", "content": improved_response}
        
        yield {"type": "done", "full_response": response_content, "verification": {
            "confidence": verification_result.confidence_score,
            "level": verification_result.verification_level.value,
            "sources": verification_result.sources
        }}


# Singleton instance
_streaming_agent = None

def get_streaming_agent() -> LunaStreamingAgent:
    global _streaming_agent
    if _streaming_agent is None:
        _streaming_agent = LunaStreamingAgent()
    return _streaming_agent
