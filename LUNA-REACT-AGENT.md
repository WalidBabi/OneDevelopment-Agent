# 🌙 Luna ReAct Agent - Quick Reference

## Overview

Luna has been upgraded to a **Cursor-like ReAct Agent** that dynamically reasons about what tools to use based on each user query.

### Key Difference: Before vs After

| Aspect | Old (Fixed Pipeline) | New (ReAct Agent) |
|--------|---------------------|-------------------|
| Tool Selection | Always runs all steps | Dynamically chooses tools |
| Reasoning | None - fixed flow | Think → Act → Observe → Repeat |
| Adaptability | Same for all queries | Tailored to each question |
| Complexity Handling | One-size-fits-all | Plans multi-step tasks |

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────┐
│            LUNA ReAct REASONING LOOP             │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ 1. THINK: What does the user need?       │   │
│  │    Which tools should I use?             │   │
│  └──────────────────────────────────────────┘   │
│                      │                          │
│                      ▼                          │
│  ┌──────────────────────────────────────────┐   │
│  │ 2. ACT: Call selected tools              │   │
│  │    - search_knowledge_base               │   │
│  │    - search_web_for_market_data          │   │
│  │    - get_user_context                    │   │
│  │    - etc.                                │   │
│  └──────────────────────────────────────────┘   │
│                      │                          │
│                      ▼                          │
│  ┌──────────────────────────────────────────┐   │
│  │ 3. OBSERVE: Process results              │   │
│  │    Need more info? → Loop back           │   │
│  │    Ready? → Generate response            │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
└─────────────────────────────────────────────────┘
    │
    ▼
Response to User
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

## What Makes Luna Different Now

1. **Dynamic Tool Selection**: Luna decides which tools to use based on the question
2. **Multi-step Reasoning**: Can plan and execute complex queries
3. **Personalization**: Remembers user preferences across conversations
4. **Market Awareness**: Combines internal knowledge with real-time data
5. **Helpful Fallbacks**: Always provides value even if data is limited

## Next Steps (After Delivery)

1. **Add More Data**: Upload PDFs, scrape website, add price lists
2. **Integration**: Connect CRM, property database, booking system
3. **Streaming**: Add response streaming for better UX
4. **Analytics**: Track tool usage and optimize prompts

---

**Luna v2.0.0** - ReAct Agent powered by LangGraph 🚀







