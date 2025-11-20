# 🧠 LangGraph Workflow Documentation

## Overview

The LangGraph workflow implements a sophisticated state machine for processing user queries with intelligent decision-making and context awareness.

## Workflow Visualization

```
                    ┌─────────────────────┐
                    │   USER QUERY IN     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ANALYZE INPUT     │
                    │                     │
                    │ • Extract keywords  │
                    │ • Identify entities │
                    │ • Parse structure   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  RETRIEVE CONTEXT   │
                    │                     │
                    │ • Query ChromaDB    │
                    │ • Semantic search   │
                    │ • Top-3 documents   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  CLASSIFY INTENT    │
                    │                     │
                    │ • Match patterns    │
                    │ • Score keywords    │
                    │ • Determine category│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ CHECK CLARIFICATION │
                    │                     │
                    │ • Query length      │
                    │ • Ambiguity check   │
                    │ • Context available │
                    └──────────┬──────────┘
                               │
                         ┌─────┴─────┐
                         │ DECISION  │
                         └─────┬─────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
        ┌────────▼────────┐        ┌────────▼────────┐
        │ NEEDS           │        │ READY TO        │
        │ CLARIFICATION   │        │ RESPOND         │
        └────────┬────────┘        └────────┬────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ GENERATE RESPONSE   │
                    │                     │
                    │ • Build prompt      │
                    │ • Call GPT-4        │
                    │ • Format response   │
                    │ • Add suggestions   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  UPDATE MEMORY      │
                    │                     │
                    │ • Store context     │
                    │ • Save preferences  │
                    │ • Update history    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   RESPONSE OUT      │
                    └─────────────────────┘
```

## Node Descriptions

### 1. Analyze Input

**Purpose:** Parse and understand the user's query

**Operations:**
- Extract entities (e.g., "villa", "Dubai Marina", "3 bedroom")
- Identify keywords
- Detect question type
- Parse numerical values

**Output:**
```python
{
    'entities': ['villa', 'dubai marina', '3 bedroom'],
    'query': 'Tell me about villas in Dubai Marina'
}
```

**Example Code:**
```python
def analyze_input(self, state: AgentState) -> AgentState:
    query = state['user_query'].lower()
    entities = []
    
    keywords = ['villa', 'apartment', 'townhouse', 'penthouse', 
                'bedroom', 'bathroom', 'sqft', 'dubai', 'marina']
    
    for keyword in keywords:
        if keyword in query:
            entities.append(keyword)
    
    state['entities'] = entities
    return state
```

### 2. Retrieve Context

**Purpose:** Find relevant information from the knowledge base

**Operations:**
- Query ChromaDB with semantic search
- Retrieve top-N most relevant documents
- Extract content snippets
- Rank by relevance score

**Vector Search:**
```python
results = self.collection.query(
    query_texts=[query],
    n_results=3
)

if results['documents']:
    state['context'] = results['documents'][0]
```

**Example Output:**
```python
{
    'context': [
        "One Development offers luxury villas in Dubai Marina...",
        "Our properties feature 3-5 bedroom configurations...",
        "Dubai Marina is a prime waterfront location..."
    ]
}
```

### 3. Classify Intent

**Purpose:** Determine the type of query and user's goal

**Intent Categories:**

| Intent | Keywords | Example Query |
|--------|----------|---------------|
| company_info | company, about, history | "Tell me about One Development" |
| projects | project, property, villa | "Show me available villas" |
| services | service, offer, provide | "What services do you offer?" |
| location | where, location, address | "Where are you located?" |
| contact | contact, phone, email | "How can I reach you?" |
| career | job, career, hiring | "Are you hiring?" |
| investment | invest, ROI, return | "What's the ROI?" |
| pricing | price, cost, payment | "How much does it cost?" |
| amenities | amenity, facility, feature | "What amenities are included?" |
| comparison | compare, versus, better | "Compare villa vs apartment" |

**Classification Algorithm:**
```python
def classify_intent(self, state: AgentState) -> AgentState:
    query = state['user_query'].lower()
    intent_scores = {}
    
    for intent, keywords in self.intent_patterns.items():
        score = sum(1 for keyword in keywords if keyword in query)
        if score > 0:
            intent_scores[intent] = score
    
    if intent_scores:
        state['intent'] = max(intent_scores, key=intent_scores.get)
    else:
        state['intent'] = 'general'
    
    return state
```

### 4. Check Clarification

**Purpose:** Determine if the query needs clarification

**Checks:**
- Query length (< 10 characters)
- Ambiguous pronouns ("this", "that", "it")
- Missing context in new conversations
- Incomplete questions

**Decision Logic:**
```python
def check_clarification(self, state: AgentState) -> AgentState:
    query = state['user_query']
    
    if len(query.strip()) < 10:
        state['needs_clarification'] = True
    elif any(word in query.lower() for word in ['this', 'that', 'it']) \
         and len(state['messages']) < 2:
        state['needs_clarification'] = True
    else:
        state['needs_clarification'] = False
    
    return state
```

### 5. Generate Response

**Purpose:** Create a contextual, helpful response

**Process:**
1. Select appropriate system prompt based on intent
2. Build context from retrieved documents
3. Construct comprehensive prompt
4. Call GPT-4 for response generation
5. Generate suggested follow-up actions

**System Prompts by Intent:**
```python
system_prompts = {
    'company_info': "You are a knowledgeable assistant about One Development...",
    'projects': "You are an expert on One Development's portfolio...",
    'services': "You are a specialist in One Development's services...",
    'pricing': "You provide pricing information for properties...",
    # ... more prompts
}
```

**Prompt Template:**
```python
prompt = f"""
{system_prompt}

Context from knowledge base:
{context_str}

User Query: {state['user_query']}
Intent: {intent}
Entities: {', '.join(state['entities'])}

Please provide a helpful, accurate, and engaging response.
Be conversational and friendly.
If you don't have specific information, acknowledge it honestly.
"""
```

**Response Generation:**
```python
response = self.llm.invoke([
    SystemMessage(content=system_prompt),
    HumanMessage(content=prompt)
])

state['response'] = response.content
```

### 6. Update Memory

**Purpose:** Store important information for future reference

**Memory Types:**
- `user_preference`: User's stated preferences
- `fact`: Important facts mentioned
- `context`: Conversation context
- `clarification`: Resolved clarifications

**Storage:**
```python
def update_memory(self, state: AgentState) -> AgentState:
    state['memory_context'] = f"Intent: {state['intent']}, Entities: {state['entities']}"
    
    # Would integrate with Django AgentMemory model
    # to persist long-term memory
    
    return state
```

## State Management

**AgentState Structure:**
```python
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]      # Full conversation history
    user_query: str                      # Current user question
    intent: str                          # Classified intent
    entities: List[str]                  # Extracted entities
    context: List[str]                   # Retrieved documents
    response: str                        # Generated response
    needs_clarification: bool            # Clarification flag
    suggested_actions: List[str]         # Follow-up suggestions
    memory_context: str                  # Memory summary
    session_id: str                      # Session identifier
```

## Decision Points

### Clarification Router

```python
def route_clarification(self, state: AgentState) -> str:
    return "needs_clarification" if state['needs_clarification'] else "ready"
```

**Paths:**
- `needs_clarification` → Generate response asking for more details
- `ready` → Generate normal response

## Integration with Django

**API Call Flow:**

```python
# In Django view (api/views.py)
def chat(request):
    # Get user message
    message = request.data['message']
    session_id = request.data.get('session_id', str(uuid.uuid4()))
    
    # Initialize agent
    agent = OneDevelopmentAgent()
    
    # Process through LangGraph
    result = agent.process_query(
        query=message,
        session_id=session_id,
        conversation_history=history
    )
    
    # Save to database
    Message.objects.create(
        conversation=conversation,
        message_type='ai',
        content=result['response'],
        metadata={
            'intent': result['intent'],
            'entities': result['entities']
        }
    )
    
    return Response(result)
```

## Example Workflows

### Example 1: Simple Query

**User:** "Tell me about One Development"

```
1. Analyze Input
   entities: ['one development']
   
2. Retrieve Context
   context: ["One Development is a premier real estate developer..."]
   
3. Classify Intent
   intent: 'company_info' (score: 3)
   
4. Check Clarification
   needs_clarification: False
   
5. Generate Response
   system_prompt: "You are a knowledgeable assistant about One Development..."
   response: "One Development is a leading real estate developer in the UAE..."
   suggested_actions: ["Tell me about recent projects", "Show me your portfolio"]
   
6. Update Memory
   memory_context: "Intent: company_info, Entities: ['one development']"
```

### Example 2: Ambiguous Query

**User:** "How much?"

```
1. Analyze Input
   entities: []
   
2. Retrieve Context
   context: []
   
3. Classify Intent
   intent: 'pricing' (score: 1)
   
4. Check Clarification
   needs_clarification: True (query too short)
   
5. Generate Response
   response: "I'd be happy to help with pricing information! Could you please
             specify which property or project you're interested in?"
   suggested_actions: ["Show me villa prices", "What are apartment costs?"]
   
6. Update Memory
   memory_context: "Intent: pricing, Needs: clarification"
```

### Example 3: Complex Query

**User:** "Compare 3-bedroom villas in Dubai Marina vs Downtown"

```
1. Analyze Input
   entities: ['3 bedroom', 'villa', 'dubai marina', 'downtown']
   
2. Retrieve Context
   context: [
     "Dubai Marina villas offer waterfront views...",
     "Downtown properties provide urban lifestyle...",
     "3-bedroom configurations available in both..."
   ]
   
3. Classify Intent
   intent: 'comparison' (score: 5)
   
4. Check Clarification
   needs_clarification: False
   
5. Generate Response
   system_prompt: "You help compare different properties..."
   response: "Great question! Let me compare 3-bedroom villas in these areas..."
   suggested_actions: [
     "What are the prices?",
     "Show me amenities",
     "Can I schedule viewings?"
   ]
   
6. Update Memory
   memory_context: "Intent: comparison, Entities: ['3 bedroom', 'villa', 
                   'dubai marina', 'downtown'], Preference: comparing locations"
```

## Performance Optimization

### Caching Strategies

1. **Context Caching:**
   ```python
   # Cache frequently retrieved contexts
   cache_key = f"context:{hash(query)}"
   if cache_key in cache:
       return cache[cache_key]
   ```

2. **Intent Caching:**
   ```python
   # Cache intent classifications for similar queries
   similar_queries = find_similar_in_cache(query)
   if similar_queries:
       return cached_intent
   ```

### Parallel Processing

```python
# Retrieve context and classify intent in parallel
import asyncio

async def process_parallel(state):
    context_task = asyncio.create_task(retrieve_context(state))
    intent_task = asyncio.create_task(classify_intent(state))
    
    await asyncio.gather(context_task, intent_task)
```

## Monitoring & Debugging

### Logging Strategy

```python
import logging

logger = logging.getLogger('langgraph_agent')

def log_state_transition(from_node, to_node, state):
    logger.info(f"""
    Transition: {from_node} → {to_node}
    Query: {state['user_query']}
    Intent: {state.get('intent', 'unknown')}
    Entities: {state.get('entities', [])}
    Context Length: {len(state.get('context', []))}
    """)
```

### Metrics to Track

- Average workflow execution time
- Intent classification accuracy
- Context retrieval relevance
- Clarification request rate
- Response generation time
- User satisfaction (via feedback)

## Future Enhancements

1. **Multi-turn Context:**
   - Maintain conversation context across turns
   - Reference previous questions
   - Aggregate information

2. **Learning from Feedback:**
   - Collect user ratings
   - Adjust intent weights
   - Improve context retrieval

3. **Proactive Suggestions:**
   - Predict next questions
   - Offer relevant information
   - Guide conversation flow

4. **Advanced NLU:**
   - Named Entity Recognition (NER)
   - Sentiment analysis
   - Emotion detection

---

This workflow provides a robust foundation for intelligent conversation handling with continuous improvement potential.

