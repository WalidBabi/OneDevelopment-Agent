"""
Luna Streaming Agent
True token-by-token streaming like Cursor - shows actual LLM thinking

This agent streams:
1. The actual reasoning tokens as the LLM thinks
2. Tool call decisions as they happen
3. Response tokens as they're generated
"""

import os
import json
from typing import Generator, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from datetime import datetime

from agent.tools import get_all_tools


class LunaStreamingAgent:
    """
    Streaming agent that shows actual LLM thinking token by token.
    Like Cursor's agent mode - you see every token as Luna thinks.
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.tools = get_all_tools()
        
        # Non-streaming LLM for tool execution
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=self.api_key
        ).bind_tools(self.tools)
        
        # Streaming LLM for visible thinking
        self.streaming_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=self.api_key,
            streaming=True
        )
    
    def _get_thinking_prompt(self, query: str, context: str = "") -> str:
        """Prompt that makes the LLM think out loud"""
        return f"""You are Luna, an AI assistant for One Development (oneuae.com).

TASK: Think through how to answer this user question. Think out loud step by step.

USER QUESTION: {query}

{f"AVAILABLE CONTEXT: {context}" if context else ""}

INSTRUCTIONS:
1. First, analyze what the user is asking
2. Think about what information you need
3. Decide if you need to search the knowledge base
4. Consider what you know vs what you need to find
5. Plan your response approach

Think out loud now. Be concise but show your reasoning:"""

    def _get_response_prompt(self, query: str, context: str, thinking: str) -> str:
        """Generate final response based on thinking and context"""
        return f"""You are Luna, an AI assistant for One Development.

USER QUESTION: {query}

YOUR THINKING PROCESS:
{thinking}

INFORMATION FOUND:
{context if context else "No specific information found in knowledge base."}

Now provide a helpful response. Be honest about limitations.
- If you found specific One Development info, share it
- If not, direct them to www.oneuae.com or the sales team
- Don't make up specific details about properties, prices, or availability

Respond naturally and helpfully:"""

    def stream_thinking_and_response(
        self,
        query: str,
        session_id: str = "default"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream the complete thinking and response process.
        
        Yields events:
        - {"type": "thinking_token", "content": "..."} - Each thinking token
        - {"type": "tool_start", "tool": "...", "query": "..."} - Tool being called
        - {"type": "tool_result", "content": "..."} - Tool result
        - {"type": "response_token", "content": "..."} - Response tokens
        - {"type": "done"} - Complete
        """
        
        thinking_content = ""
        context_content = ""
        
        # Phase 1: Stream thinking tokens
        yield {"type": "phase", "content": "thinking"}
        
        thinking_prompt = self._get_thinking_prompt(query)
        
        for chunk in self.streaming_llm.stream([
            SystemMessage(content="You are Luna, thinking through a user's question."),
            HumanMessage(content=thinking_prompt)
        ]):
            if chunk.content:
                thinking_content += chunk.content
                yield {"type": "thinking_token", "content": chunk.content}
        
        yield {"type": "thinking_complete", "content": thinking_content}
        
        # Phase 2: Execute tool if thinking suggests it
        should_search = any(word in thinking_content.lower() for word in [
            'search', 'look up', 'find', 'check', 'knowledge base', 
            'need to find', 'let me search', 'information about'
        ])
        
        if should_search:
            yield {"type": "phase", "content": "searching"}
            yield {"type": "tool_start", "tool": "search_knowledge_base", "query": query}
            
            try:
                from agent.tools import search_knowledge_base
                result = search_knowledge_base.invoke({"query": query, "n_results": 3})
                context_content = result
                
                # Stream the result
                preview = result[:200] + "..." if len(result) > 200 else result
                yield {"type": "tool_result", "content": preview}
            except Exception as e:
                yield {"type": "tool_error", "content": str(e)}
        
        # Phase 3: Stream response tokens
        yield {"type": "phase", "content": "responding"}
        
        response_prompt = self._get_response_prompt(query, context_content, thinking_content)
        response_content = ""
        
        for chunk in self.streaming_llm.stream([
            SystemMessage(content="You are Luna, the One Development AI assistant."),
            HumanMessage(content=response_prompt)
        ]):
            if chunk.content:
                response_content += chunk.content
                yield {"type": "response_token", "content": chunk.content}
        
        yield {"type": "done", "full_response": response_content}


# Singleton instance
_streaming_agent = None

def get_streaming_agent() -> LunaStreamingAgent:
    global _streaming_agent
    if _streaming_agent is None:
        _streaming_agent = LunaStreamingAgent()
    return _streaming_agent







