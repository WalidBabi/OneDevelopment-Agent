"""
OneDevelopment AI Agent with LangGraph
Implements a sophisticated workflow with memory and decision-making
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from chromadb.config import Settings
import os
import re
from datetime import datetime
from agent.web_tools import WebAccessTool
from agent.memory_manager import MemoryManager


class AgentState(TypedDict):
    """State that flows through the agent graph"""
    messages: List[Dict[str, Any]]
    user_query: str
    intent: str
    entities: List[str]
    context: List[str]
    response: str
    needs_clarification: bool
    suggested_actions: List[str]
    memory_context: str
    session_id: str
    sources: List[Dict[str, Any]]  # Track sources used in response
    web_search_results: Dict[str, Any]  # Real-time web search results
    user_name: str  # Stored user name from memory
    user_preferences: Dict[str, str]  # User preferences


class OneDevelopmentAgent:
    """
    Intelligent agent for One Development with LangGraph workflow
    
    Workflow:
    1. Input Analysis: Analyze user query and extract intent
    2. Context Retrieval: Fetch relevant knowledge from vector database
    3. Memory Integration: Add conversation memory and user preferences
    4. Intent Classification: Determine the type of query
    5. Decision Node: Route to appropriate handler
    6. Response Generation: Generate contextual response
    7. Memory Update: Store important information
    """
    
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=self.api_key
        )
        
        # Initialize web access tool for real-time fact checking
        try:
            self.web_tool = WebAccessTool()
            print("✅ Web access tool initialized successfully")
        except Exception as e:
            print(f"⚠️  Web access not available: {str(e)}")
            self.web_tool = None
        
        # Initialize embeddings for semantic search (optional)
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✅ Vector embeddings initialized successfully")
        except Exception as e:
            print(f"⚠️  Vector embeddings not available (install sentence-transformers): {str(e)}")
            self.embeddings = None
        
        # Initialize ChromaDB for vector storage with persistence
        try:
            # Use persistent storage
            chroma_db_path = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')
            os.makedirs(chroma_db_path, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=chroma_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            
            try:
                self.collection = self.chroma_client.get_collection("onedevelopment_knowledge")
                print(f"✅ ChromaDB loaded: {self.collection.count()} documents")
            except:
                self.collection = self.chroma_client.create_collection(
                    name="onedevelopment_knowledge",
                    metadata={"description": "Knowledge base for One Development"}
                )
                # Auto-populate on first creation
                self._populate_vector_store()
                print(f"✅ ChromaDB created and populated: {self.collection.count()} documents")
        except Exception as e:
            print(f"⚠️  Vector store not available: {str(e)}")
            self.chroma_client = None
            self.collection = None
        
        # Build the agent graph
        self.graph = self._build_graph()
        
        # Define intent categories with keywords
        self.intent_patterns = {
            'company_info': ['company', 'about', 'history', 'establishment', 'founded', 'who', 'what is'],
            'projects': ['project', 'development', 'portfolio', 'built', 'constructed', 'properties'],
            'services': ['service', 'offer', 'provide', 'do', 'capabilities', 'specialization'],
            'location': ['where', 'location', 'address', 'office', 'headquarters', 'dubai', 'uae'],
            'contact': ['contact', 'phone', 'email', 'reach', 'call', 'message'],
            'career': ['job', 'career', 'hiring', 'opportunity', 'work', 'employment', 'vacancy'],
            'investment': ['invest', 'investment', 'roi', 'return', 'profit', 'financial'],
            'pricing': ['price', 'cost', 'how much', 'budget', 'affordable', 'payment'],
            'amenities': ['amenity', 'amenities', 'facility', 'facilities', 'feature', 'features'],
            'comparison': ['compare', 'versus', 'vs', 'difference', 'better', 'best'],
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("load_memory", self.load_memory)
        workflow.add_node("analyze_input", self.analyze_input)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("web_search", self.web_search)
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("check_clarification", self.check_clarification)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("update_memory", self.update_memory)
        
        # Define edges
        workflow.set_entry_point("load_memory")
        workflow.add_edge("load_memory", "analyze_input")
        workflow.add_edge("analyze_input", "retrieve_context")
        workflow.add_edge("retrieve_context", "web_search")
        workflow.add_edge("web_search", "classify_intent")
        workflow.add_edge("classify_intent", "check_clarification")
        
        # Conditional routing based on clarification need
        workflow.add_conditional_edges(
            "check_clarification",
            self.route_clarification,
            {
                "needs_clarification": "generate_response",
                "ready": "generate_response"
            }
        )
        
        workflow.add_edge("generate_response", "update_memory")
        workflow.add_edge("update_memory", END)
        
        return workflow.compile()
    
    def load_memory(self, state: AgentState) -> AgentState:
        """Load persistent memory for this session"""
        session_id = state.get('session_id', 'default')
        
        try:
            memory_manager = MemoryManager(session_id)
            
            # Get user name
            user_name = memory_manager.get_user_name()
            state['user_name'] = user_name or ""
            
            # Get user preferences
            preferences = memory_manager.get_user_preferences()
            state['user_preferences'] = preferences
            
            # Get conversation context
            context = memory_manager.get_conversation_context()
            state['memory_context'] = context
            
            print(f"✅ Loaded memory for session {session_id}: {context}")
            
        except Exception as e:
            print(f"⚠️  Could not load memory: {str(e)}")
            state['user_name'] = ""
            state['user_preferences'] = {}
            state['memory_context'] = ""
        
        return state
    
    def analyze_input(self, state: AgentState) -> AgentState:
        """Analyze user input and extract entities"""
        query = state['user_query'].lower()
        
        # Extract potential entities (simple implementation)
        entities = []
        
        # Check for specific keywords
        keywords = ['villa', 'apartment', 'townhouse', 'penthouse', 'studio', 
                   'bedroom', 'bathroom', 'sqft', 'dubai', 'marina', 'downtown']
        
        for keyword in keywords:
            if keyword in query:
                entities.append(keyword)
        
        state['entities'] = entities
        return state
    
    def retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context from knowledge base - DISABLED: Using web search only"""
        # Initialize empty context - we'll get everything from web search
        state['context'] = []
        state['sources'] = []
        
        print("⚠️  Knowledge base retrieval SKIPPED - using web search only")
        
        return state
    
    def web_search(self, state: AgentState) -> AgentState:
        """Search web for real-time information (Enhanced with multiple sources)"""
        query = state['user_query']
        
        # Check if web tool is available
        if not self.web_tool:
            print("⚠️  Web tool not available - continuing with existing knowledge")
            state['web_search_results'] = {}
            # Don't add error message to context - agent will use existing knowledge
            return state
        
        try:
            print(f"🌐 Searching multiple web sources for: {query}")
            
            # Search multiple sources (company website + property portals + market context)
            results = self.web_tool.search_multiple_sources(query)
            
            if results.get('success') and results.get('combined_text'):
                # Add combined text as context
                state['context'].append(results['combined_text'])
                print(f"✅ Retrieved information from {len(results['sources'])} web sources")
                
                # Add all sources to state
                for i, source in enumerate(results['sources'], 1):
                    state['sources'].append({
                        'title': source.get('name', 'Web Source'),
                        'source_type': source.get('type', 'External Source'),
                        'index': i,
                        'url': source.get('url', '')
                    })
                
                # Add market context flag if present
                if results.get('has_market_context'):
                    print("📊 Market context added to response")
            else:
                print(f"⚠️  No additional web results - using existing knowledge base")
                # Don't add error messages - agent will work with what it has
            
            state['web_search_results'] = results
            
        except Exception as e:
            print(f"❌ Web search error: {str(e)} - continuing with knowledge base")
            state['web_search_results'] = {}
            # Don't add error to context - agent will use existing knowledge intelligently
        
        return state
    
    def classify_intent(self, state: AgentState) -> AgentState:
        """Classify user intent based on keywords and patterns"""
        query = state['user_query'].lower()
        intent_scores = {}
        
        # Score each intent based on keyword matches
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                intent_scores[intent] = score
        
        # Get the intent with highest score
        if intent_scores:
            state['intent'] = max(intent_scores, key=intent_scores.get)
        else:
            state['intent'] = 'general'
        
        return state
    
    def check_clarification(self, state: AgentState) -> AgentState:
        """Check if we need clarification from user"""
        query = state['user_query']
        
        # Very short queries might need clarification
        if len(query.strip()) < 10:
            state['needs_clarification'] = True
        # Ambiguous queries
        elif any(word in query.lower() for word in ['this', 'that', 'it']) and len(state['messages']) < 2:
            state['needs_clarification'] = True
        else:
            state['needs_clarification'] = False
        
        return state
    
    def route_clarification(self, state: AgentState) -> str:
        """Route based on clarification need"""
        return "needs_clarification" if state['needs_clarification'] else "ready"
    
    def generate_response(self, state: AgentState) -> AgentState:
        """Generate contextual response using LLM"""
        
        # Build context for the LLM
        context_str = "\n".join(state['context']) if state['context'] else "No specific context available."
        
        # Create system prompt based on intent
        system_prompts = {
            'company_info': "You are Nova, a knowledgeable AI assistant for One Development, a leading real estate developer in the UAE. You have deep knowledge of the UAE real estate market and luxury property development.",
            'projects': "You are Nova, an expert on One Development's portfolio of luxury properties and projects. You understand Dubai's prime locations, property types, and development standards.",
            'services': "You are Nova, a specialist in One Development's comprehensive real estate services including property management, investment support, and after-sales care.",
            'contact': "You are Nova, helping people connect with One Development's team. You're knowledgeable about different departments and how to best assist clients.",
            'career': "You are Nova, assisting with career opportunities at One Development. You understand the real estate industry and what makes a great team member.",
            'investment': "You are Nova, a property investment advisor with knowledge of the UAE real estate market, ROI expectations, and investment strategies.",
            'pricing': "You are Nova, helping clients understand property pricing in Dubai's luxury market. You know about payment plans, market rates, and value factors.",
            'amenities': "You are Nova, describing the premium amenities and features that define luxury living in Dubai developments.",
            'comparison': "You are Nova, helping clients compare different property options and find their perfect match.",
            'general': "You are Nova, a helpful and knowledgeable AI assistant for One Development. You're here to guide clients through their real estate journey in the UAE."
        }
        
        intent = state.get('intent', 'general')
        system_prompt = system_prompts.get(intent, system_prompts['general'])
        
        # Build user context
        user_context = ""
        if state.get('user_name'):
            user_context = f"User's name: {state['user_name']}\n"
        if state.get('memory_context'):
            user_context += f"Previous context: {state['memory_context']}\n"
        if state.get('user_preferences'):
            prefs = ", ".join([f"{k}: {v}" for k, v in state['user_preferences'].items()])
            if prefs:
                user_context += f"User preferences: {prefs}\n"
        
        # Build the prompt
        prompt = f"""
{system_prompt}

{user_context}

Context from knowledge base:
{context_str}

User Query: {state['user_query']}

INTELLIGENT RESPONSE GUIDELINES:

**Primary Approach:**
1. If you know the user's name, address them by name naturally
2. Use information from previous context if relevant
3. Provide information that is supported by the context above

**When Specific Data is Missing:**
Instead of apologizing or saying "I don't have information", be HELPFUL:
- Provide general industry knowledge and UAE real estate context when relevant
- Offer typical ranges, examples, or what's common in similar developments
- Bridge to related information you DO have
- Always end with a clear path forward (e.g., "I can connect you with our sales team for exact details")
- Maintain confidence while being honest about limitations

**Examples of Intelligent Bridging:**
- Pricing: "Luxury properties in Dubai Marina typically range from AED 1.5M-5M. For our current pricing and available units, I recommend speaking with our sales team who can provide detailed quotes."
- Features: "Our properties typically include premium amenities like swimming pools, fitness centers, and 24/7 security. Let me share what specific amenities we offer..."
- Timeline: "Development timelines in Dubai typically range from 18-36 months. For specific completion dates on our projects, our team can provide exact schedules."

**Always Provide Value:**
- Share related information you DO have
- Offer to connect them with the right person/team
- Suggest next steps or alternatives
- Use industry knowledge to provide context

**FORMATTING:**
1. Write in short, clear paragraphs (2-3 sentences maximum per paragraph)
2. Use bullet points (with - or •) for listing features, benefits, or options
3. Use **bold text** for important terms, key features, or emphasis
4. Add blank lines between paragraphs for better readability
5. Use natural, conversational language
6. Keep your response concise and well-structured

**STYLE:** Be professional yet friendly, confident and helpful. Always provide actionable guidance. Break up long text into digestible sections.

**KEY RULE:** Never leave the user hanging. Every response should move the conversation forward productively.
"""
        
        # Generate response
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ])
        
        # Format response (sources section removed per user request)
        formatted_response = response.content.strip()
        
        # Sources section removed - no longer displaying "Learn more" links
        # Previous version included Company Website and LinkedIn links here
        
        state['response'] = formatted_response
        
        # Generate suggested actions based on intent
        suggested_actions = self._generate_suggested_actions(intent)
        state['suggested_actions'] = suggested_actions
        
        return state
    
    def _generate_suggested_actions(self, intent: str) -> List[str]:
        """Generate suggested follow-up actions"""
        suggestions = {
            'company_info': [
                "Tell me about recent projects",
                "What makes One Development unique?",
                "Show me your portfolio"
            ],
            'projects': [
                "What are the prices?",
                "What amenities are included?",
                "Can I schedule a viewing?"
            ],
            'services': [
                "Tell me about investment opportunities",
                "What is the buying process?",
                "Do you offer financing?"
            ],
            'contact': [
                "What are your office hours?",
                "Can I schedule a meeting?",
                "Where are you located?"
            ],
            'career': [
                "What positions are open?",
                "What is the application process?",
                "What are the benefits?"
            ],
            'pricing': [
                "What payment plans are available?",
                "Are there any promotions?",
                "What are the additional costs?"
            ],
            'general': [
                "Tell me about your company",
                "Show me available properties",
                "How can I contact you?"
            ]
        }
        
        return suggestions.get(intent, suggestions['general'])
    
    def update_memory(self, state: AgentState) -> AgentState:
        """Update agent memory with important information"""
        session_id = state.get('session_id', 'default')
        
        try:
            memory_manager = MemoryManager(session_id)
            
            # Extract and store user information from conversation
            memory_manager.extract_and_store_user_info(
                state['user_query'],
                state['response']
            )
            
            # Store important facts from this conversation
            if state.get('entities'):
                entities_str = ', '.join(state['entities'])
                memory_manager.store_memory(
                    'fact',
                    f'discussed_{state["intent"]}',
                    f'User asked about {state["intent"]}: {entities_str}',
                    importance=0.6
                )
            
            print(f"✅ Updated memory for session {session_id}")
            
        except Exception as e:
            print(f"⚠️  Could not update memory: {str(e)}")
        
        return state
    
    def process_query(self, query: str, session_id: str = None, 
                     conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a user query through the agent workflow
        
        Args:
            query: User's question or message
            session_id: Unique session identifier
            conversation_history: Previous messages in the conversation
            
        Returns:
            Dictionary with response and metadata including sources
        """
        
        # Initialize state
        initial_state = AgentState(
            messages=conversation_history or [],
            user_query=query,
            intent="",
            entities=[],
            context=[],
            response="",
            needs_clarification=False,
            suggested_actions=[],
            memory_context="",
            session_id=session_id or "default",
            sources=[],
            web_search_results={},
            user_name="",
            user_preferences={}
        )
        
        # Run through the graph
        final_state = self.graph.invoke(initial_state)
        
        return {
            'response': final_state['response'],
            'intent': final_state['intent'],
            'entities': final_state['entities'],
            'suggested_actions': final_state['suggested_actions'],
            'needs_clarification': final_state['needs_clarification'],
            'sources': final_state.get('sources', [])
        }
    
    def _populate_vector_store(self):
        """Automatically populate vector store from database"""
        try:
            from agent.models import KnowledgeBase
            knowledge = KnowledgeBase.objects.filter(is_active=True)
            
            for kb in knowledge:
                try:
                    self.collection.add(
                        documents=[kb.content],
                        metadatas=[{'title': kb.title, 'summary': kb.summary, 'source': kb.source_type}],
                        ids=[str(kb.id)]
                    )
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"Error adding {kb.title[:30]}: {str(e)[:50]}")
        except Exception as e:
            print(f"Could not auto-populate vector store: {str(e)[:100]}")
    
    def add_knowledge(self, content: str, metadata: Dict[str, Any] = None):
        """Add content to the knowledge base"""
        doc_id = f"doc_{datetime.now().timestamp()}"
        
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )

