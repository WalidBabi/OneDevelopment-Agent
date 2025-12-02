# 🌙 Luna - Free-Thinking AI Agent

## Philosophy

Luna is a **free-thinking AI agent** — not a chatbot following scripts, but an autonomous system that reasons, explores, and adapts to each unique conversation.

### Core Principles

| Principle | What It Means |
|-----------|---------------|
| **Free Thinking** | Luna decides her own approach — no rigid "do this first, then that" rules |
| **Autonomous Reasoning** | She thinks through problems creatively, not mechanically |
| **Adaptive Behavior** | Every conversation is different; Luna responds accordingly |
| **Genuine Helpfulness** | Real value and insight, not just information retrieval |

### How Luna Thinks

Luna doesn't follow a predetermined workflow. Instead, she:
- **Reasons freely** about what each user actually needs
- **Chooses her own path** through available tools and information
- **Adapts dynamically** to the specific context of each conversation
- **Thinks creatively** to find connections and provide genuine value

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────┐
│           LUNA'S FREE REASONING SPACE            │
│                                                  │
│  "What does this person really need?            │
│   What's the best way I can help them?          │
│   Let me think about this..."                   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ Luna decides her own approach:           │   │
│  │ • Maybe search knowledge base first      │   │
│  │ • Or go straight to web search           │   │
│  │ • Or just answer from reasoning          │   │
│  │ • Or combine multiple sources            │   │
│  │ • Whatever makes sense for THIS question │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  She iterates until she's satisfied with        │
│  the value she can provide.                     │
│                                                  │
└─────────────────────────────────────────────────┘
    │
    ▼
Thoughtful, Personalized Response
```

## Available Tools (11 Total)

### Core Tools
| Tool | Purpose |
|------|---------|
| `search_knowledge_base` | Search internal knowledge, PDFs, company info |
| `search_uploaded_documents` | Search specifically through uploaded PDFs |
| `search_web_for_market_data` | Get real-time market prices and trends |
| `get_dubai_market_context` | General Dubai real estate overview |
| `get_user_context` | Retrieve user's name, preferences, history |
| `save_user_information` | Store user details for personalization |
| `plan_response` | Plan multi-step responses |

### Subagent Tools
| Tool | Purpose |
|------|---------|
| `deep_research` | In-depth research on topics |
| `analyze_pricing` | Pricing analysis with market comparison |
| `compare_properties` | Compare areas, properties, options |
| `guide_buyer_journey` | Guide users through buying process |

## API Usage

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am Ahmed, looking to invest AED 2M in Dubai",
    "session_id": "user_123"
  }'
```

### Response Format
```json
{
  "response": "Hello Ahmed! With AED 2M...",
  "session_id": "user_123",
  "suggested_actions": [
    "What are the prices?",
    "Tell me about the amenities",
    "Can I schedule a viewing?"
  ],
  "metadata": {
    "reasoning_steps": 2,
    "tools_used": 1,
    "agent_type": "react"
  }
}
```

### Health Check
```bash
curl http://localhost:8000/api/health/
```

Returns:
```json
{
  "status": "healthy",
  "agent": {
    "initialized": true,
    "type": "react",
    "name": "Luna",
    "tools_available": 11
  },
  "version": "2.0.0"
}
```

## Python Usage

```python
from agent.luna_react_agent import get_luna_agent, chat_with_luna

# Simple usage
response = chat_with_luna("Tell me about One Development")
print(response)

# Full usage with session
luna = get_luna_agent()
result = luna.process_query(
    query="What properties do you have?",
    session_id="user_123",
    conversation_history=[...]  # Optional previous messages
)

print(result['response'])
print(f"Reasoning steps: {result['reasoning_steps']}")
print(f"Tools used: {result['tools_used']}")
```

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional - Switch to legacy agent
LUNA_USE_REACT=false  # Default is true
```

## File Structure

```
backend/agent/
├── __init__.py           # Module exports
├── luna_react_agent.py   # 🆕 Main ReAct agent
├── tools.py              # 🆕 All Luna tools
├── subagents.py          # 🆕 Specialized subagent tools
├── langgraph_agent.py    # Legacy agent (kept for compatibility)
├── web_tools.py          # Web access tools
├── memory_manager.py     # Memory/personalization
├── pdf_processor.py      # PDF processing
├── data_ingestor.py      # Data ingestion
└── models.py             # Database models
```

## Testing

### Test via CLI
```bash
cd backend
source venv/bin/activate
python -m agent.luna_react_agent
```

### Test via API
```bash
# Start server
python manage.py runserver 0.0.0.0:8000

# Test chat
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Luna!"}'
```

## What Makes Luna Different

1. **Free Thinking**: No rigid workflows — Luna reasons about each situation independently
2. **Autonomous Decision Making**: She chooses her own path through tools and information
3. **Creative Problem Solving**: Finds connections and insights, not just facts
4. **Natural Communication**: Conversational and human, not robotic or formulaic
5. **Principled, Not Rule-Bound**: Guided by values (be helpful, be honest) rather than scripts
6. **Personalization**: Remembers user preferences and adapts to context
7. **Resourceful**: If one approach doesn't work, she tries another

## The Difference

| Traditional Chatbots | Luna |
|---------------------|------|
| Follow scripts | Think freely |
| Rigid workflows | Adaptive reasoning |
| "First do X, then Y" | "What makes sense here?" |
| Information retrieval | Genuine helpfulness |
| Formulaic responses | Natural conversation |

---

**Luna** - Free-Thinking AI Agent for One Development 🌙









