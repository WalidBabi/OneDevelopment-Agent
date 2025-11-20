# 🏗️ Architecture Documentation

## System Overview

The One Development AI Agent is a full-stack application with advanced AI capabilities powered by LangGraph.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              React Application (Port 3000)             │ │
│  │  - ChatInterface Component (rotating suggestions)     │ │
│  │  - Real-time messaging with beautiful UI              │ │
│  │  - Session management with localStorage               │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (HTTP)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Django REST API (Port 8000)                    │ │
│  │  - /api/chat/            - Main chat endpoint          │ │
│  │  - /api/suggested-questions/  - Get suggestions        │ │
│  │  - /api/conversations/   - History management          │ │
│  │  - /api/ingest-data/     - Data ingestion             │ │
│  │  - /api/knowledge/       - Knowledge base CRUD         │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           LangGraph Agent Engine                       │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │    State Graph Workflow                          │ │ │
│  │  │  1. Analyze Input                                │ │ │
│  │  │  2. Retrieve Context (Vector Search)             │ │ │
│  │  │  3. Classify Intent                              │ │ │
│  │  │  4. Check Clarification                          │ │ │
│  │  │  5. Generate Response (GPT-4)                    │ │ │
│  │  │  6. Update Memory                                │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                     ┌─────┴─────┐                           │
│                     ▼           ▼                            │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │   ChromaDB           │  │   OpenAI API         │        │
│  │  Vector Storage      │  │   GPT-4              │        │
│  │  - Embeddings        │  │   Response Gen       │        │
│  │  - Semantic Search   │  │                      │        │
│  └──────────────────────┘  └──────────────────────┘        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                PostgreSQL Database                     │ │
│  │  - Conversations  - Message history                    │ │
│  │  - Messages       - Chat records                       │ │
│  │  - KnowledgeBase  - Scraped content                    │ │
│  │  - AgentMemory    - Long-term memory                   │ │
│  │  - SuggestedQuestions - UI suggestions                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                  Data Ingestion Layer                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            OneDevelopmentDataIngestor                  │ │
│  │  - Website Scraper (Beautiful Soup)                   │ │
│  │  - LinkedIn API Integration (placeholder)             │ │
│  │  - Manual Data Entry                                   │ │
│  │  - Document Parser (future)                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React)

**Technology Stack:**
- React 18.2
- Axios for HTTP requests
- Framer Motion for animations
- CSS3 for styling

**Key Features:**
- Single Page Application (SPA)
- Real-time chat interface
- Rotating suggested questions (15-second intervals)
- Session persistence with localStorage
- Responsive design (mobile-first)

**State Management:**
```javascript
{
  messages: [],           // Chat history
  inputMessage: '',       // Current input
  isLoading: false,       // Loading state
  sessionId: 'uuid',      // Session identifier
  suggestedQuestions: [], // Rotating suggestions
  error: null            // Error messages
}
```

### 2. Backend API (Django REST Framework)

**Technology Stack:**
- Django 5.0
- Django REST Framework
- CORS Headers for cross-origin requests
- PostgreSQL adapter (psycopg2)

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/` | POST | Send message, get AI response |
| `/api/suggested-questions/` | GET | Fetch rotating questions |
| `/api/conversations/{id}/` | GET | Get conversation history |
| `/api/ingest-data/` | POST | Trigger data ingestion |
| `/api/knowledge/` | GET | List knowledge base |
| `/api/health/` | GET | Health check |

### 3. LangGraph Agent

**Workflow Graph:**

```python
StateGraph(AgentState)
  ├─ analyze_input()
  │   └─> Extract entities and keywords
  ├─ retrieve_context()
  │   └─> Query ChromaDB for relevant docs
  ├─ classify_intent()
  │   └─> Determine query category
  ├─ check_clarification()
  │   └─> Decide if more info needed
  ├─ generate_response()
  │   └─> GPT-4 generates answer
  └─ update_memory()
      └─> Store conversation context
```

**State Object:**
```python
{
    'messages': List[Dict],
    'user_query': str,
    'intent': str,              # company_info, projects, pricing, etc.
    'entities': List[str],      # Extracted entities
    'context': List[str],       # Retrieved documents
    'response': str,            # AI response
    'needs_clarification': bool,
    'suggested_actions': List[str],
    'memory_context': str,
    'session_id': str
}
```

**Intent Categories:**
1. `company_info` - About One Development
2. `projects` - Property listings
3. `services` - Services offered
4. `location` - Office/property locations
5. `contact` - Contact information
6. `career` - Job opportunities
7. `investment` - Investment info
8. `pricing` - Property prices
9. `amenities` - Features and amenities
10. `comparison` - Property comparisons
11. `general` - Fallback category

### 4. Vector Database (ChromaDB)

**Purpose:**
- Store document embeddings
- Semantic search for context retrieval
- Fast similarity matching

**Embedding Model:**
- `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional vectors
- Optimized for semantic search

**Operations:**
```python
# Add knowledge
collection.add(
    documents=[content],
    metadatas=[metadata],
    ids=[doc_id]
)

# Query for context
results = collection.query(
    query_texts=[user_query],
    n_results=3
)
```

### 5. Database Schema (PostgreSQL)

**Conversations Table:**
```sql
id              UUID PRIMARY KEY
session_id      VARCHAR(255) UNIQUE
created_at      TIMESTAMP
updated_at      TIMESTAMP
metadata        JSONB
```

**Messages Table:**
```sql
id              UUID PRIMARY KEY
conversation_id UUID FOREIGN KEY
message_type    VARCHAR(10)  -- 'human', 'ai', 'system'
content         TEXT
metadata        JSONB
created_at      TIMESTAMP
```

**KnowledgeBase Table:**
```sql
id              UUID PRIMARY KEY
source_type     VARCHAR(20)  -- 'website', 'linkedin', 'manual'
source_url      VARCHAR(500)
title           VARCHAR(500)
content         TEXT
summary         TEXT
embedding       JSONB
metadata        JSONB
created_at      TIMESTAMP
updated_at      TIMESTAMP
is_active       BOOLEAN
```

**AgentMemory Table:**
```sql
id              UUID PRIMARY KEY
conversation_id UUID FOREIGN KEY
memory_type     VARCHAR(50)
key             VARCHAR(255)
value           TEXT
importance_score FLOAT
created_at      TIMESTAMP
last_accessed   TIMESTAMP
```

**SuggestedQuestions Table:**
```sql
id              UUID PRIMARY KEY
question        VARCHAR(500)
category        VARCHAR(100)
priority        INTEGER
is_active       BOOLEAN
created_at      TIMESTAMP
```

### 6. Data Ingestion System

**Sources:**

1. **Website Scraping:**
   - Target: https://www.oneuae.com
   - Technology: Beautiful Soup, Requests
   - Features: Recursive crawling, content extraction, deduplication

2. **LinkedIn (Placeholder):**
   - Company profile data
   - Recent updates
   - Job postings
   - Requires API credentials

3. **Manual Entry:**
   - Django admin interface
   - REST API endpoints
   - Direct database access

4. **Future Sources:**
   - PDF documents
   - Social media feeds
   - News articles
   - Customer reviews

**Data Flow:**
```
Source → Scraper → Parser → Database + Vector Store
```

## Communication Flow

### User Query Flow:

```
1. User types message in React app
   ↓
2. Frontend sends POST to /api/chat/
   ↓
3. Django creates/retrieves Conversation
   ↓
4. Message stored in database
   ↓
5. LangGraph agent processes query:
   a. Analyze input
   b. Retrieve context from ChromaDB
   c. Classify intent
   d. Generate response with GPT-4
   e. Update memory
   ↓
6. Response stored in database
   ↓
7. JSON response sent to frontend
   ↓
8. UI displays response with animations
   ↓
9. Suggested actions shown to user
```

### Data Ingestion Flow:

```
1. Trigger ingestion (API or management command)
   ↓
2. DataIngestor fetches content
   ↓
3. Content parsed and cleaned
   ↓
4. Stored in KnowledgeBase table
   ↓
5. Embeddings generated
   ↓
6. Added to ChromaDB vector store
   ↓
7. Available for context retrieval
```

## Scalability Considerations

### Current Setup (Development):
- Single server
- SQLite for ChromaDB
- In-memory caching

### Production Recommendations:

1. **Database:**
   - PostgreSQL with connection pooling
   - Read replicas for scaling
   - Regular backups

2. **Vector Store:**
   - Persistent ChromaDB storage
   - Consider migration to Pinecone/Weaviate for scale

3. **Caching:**
   - Redis for API response caching
   - Cache embeddings
   - Session storage in Redis

4. **Load Balancing:**
   - Multiple Django instances
   - Nginx as reverse proxy
   - Container orchestration (Kubernetes)

5. **Async Processing:**
   - Celery for background tasks
   - Redis as message broker
   - Separate worker processes for data ingestion

## Security Architecture

**Authentication & Authorization:**
- CSRF protection (Django)
- CORS configured for specific origins
- API rate limiting (recommended)
- Session-based authentication

**Data Protection:**
- Environment variables for secrets
- Database connection encryption
- HTTPS in production
- Input sanitization

**API Security:**
- Input validation
- SQL injection prevention (Django ORM)
- XSS protection
- Request size limits

## Monitoring & Logging

**Logs:**
- Django request logs
- Agent decision logs
- Error tracking
- Performance metrics

**Metrics to Track:**
- Response time
- Intent classification accuracy
- User satisfaction
- Popular queries
- Error rates

## Future Enhancements

1. **Multi-language Support:**
   - Translation API integration
   - Language detection
   - Localized responses

2. **Voice Interface:**
   - Speech-to-text
   - Text-to-speech
   - Voice commands

3. **Analytics Dashboard:**
   - User interaction metrics
   - Popular queries
   - Intent distribution
   - Conversion tracking

4. **Advanced Features:**
   - Multi-turn conversations with context
   - Personalization based on history
   - Proactive suggestions
   - Integration with CRM systems

5. **Mobile Apps:**
   - Native iOS app
   - Native Android app
   - Push notifications

---

This architecture provides a solid foundation for an intelligent, scalable AI agent system.

