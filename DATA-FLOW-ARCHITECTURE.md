# 🏗️ Nova AI Agent - Data Flow & Architecture

## 📊 **How Nova Gets Its Data**

### **Overview:**
Nova uses a **RAG (Retrieval-Augmented Generation)** architecture with **LangGraph** orchestration and **vector embeddings** for semantic search.

---

## 🔄 **Complete Data Flow:**

```
User Question
     ↓
Frontend (React)
     ↓
Backend API (Django REST)
     ↓
LangGraph Agent (Orchestration)
     ↓
├─→ Vector Store (ChromaDB) ← Embeddings
│   └─→ Retrieves relevant knowledge
│
├─→ PostgreSQL Database
│   └─→ Knowledge Base table
│
└─→ OpenAI GPT-4 API
    └─→ Generates response with context
     ↓
Response back to user
```

---

## 📁 **Data Sources:**

### **1. PostgreSQL Database**
**Location:** `localhost:5432/onedevelopment_agent`

**Tables:**
```sql
agent_knowledgebase  -- 12 entries about One Development
  ├─ id (UUID)
  ├─ title (VARCHAR)
  ├─ content (TEXT)           ← Main knowledge
  ├─ summary (TEXT)
  ├─ source_type (VARCHAR)    ← 'manual', 'linkedin', 'website'
  ├─ metadata (JSONB)
  ├─ is_active (BOOLEAN)
  └─ created_at, updated_at

agent_conversation    -- Chat sessions
agent_message        -- Individual messages
agent_suggestedquestion  -- 29 suggested questions
```

**View in database:**
```bash
psql -U onedevelopment -h localhost -d onedevelopment_agent
SELECT title, source_type FROM agent_knowledgebase WHERE is_active=true;
```

---

### **2. ChromaDB Vector Store**
**Location:** `/home/ec2-user/OneDevelopment-Agent/backend/chroma_db/`

**Purpose:** Semantic search using embeddings

**How it works:**
1. Knowledge from PostgreSQL is converted to **vector embeddings**
2. User queries are also converted to vectors
3. ChromaDB finds **similar vectors** (semantic matching)
4. Returns most relevant knowledge chunks

**Current Status:**
- 📊 **12 documents** indexed
- 💾 **248 KB** on disk
- 🔄 **Persistent** (survives restarts)

**Embedding Model:**
- `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional vectors

---

## 🧠 **LangGraph Agent Workflow:**

**File:** `/backend/agent/langgraph_agent.py`

### **Step-by-Step Process:**

```python
1. analyze_input(user_query)
   ↓ Extracts entities, analyzes intent
   
2. retrieve_context(query)
   ↓ Searches ChromaDB for relevant knowledge
   ↓ Queries: collection.query(query_texts=[query], n_results=3)
   
3. classify_intent(query)
   ↓ Determines: 'projects', 'pricing', 'contact', etc.
   
4. check_clarification()
   ↓ Decides if more info needed
   
5. generate_response(context + query)
   ↓ Calls OpenAI GPT-4 with:
   ↓   - User question
   ↓   - Retrieved knowledge context
   ↓   - System instructions
   
6. update_memory()
   ↓ Stores conversation in PostgreSQL
   
7. Return response to frontend
```

---

## 📝 **Code Walkthrough:**

### **1. Frontend → Backend**
**File:** `/frontend/src/services/api.js`

```javascript
export const sendMessage = async (message, sessionId) => {
  const response = await axios.post(`${API_URL}/chat/`, {
    message: message,
    session_id: sessionId
  });
  return response.data;
};
```

---

### **2. Backend API Endpoint**
**File:** `/backend/agent/views.py`

```python
@api_view(['POST'])
def chat_view(request):
    user_message = request.data.get('message')
    session_id = request.data.get('session_id')
    
    # Initialize agent
    agent = OneDevelopmentAgent()
    
    # Process query through LangGraph
    result = agent.process_query(user_message, session_id)
    
    return Response({
        'response': result['response'],
        'intent': result['intent'],
        'suggested_actions': result['suggested_actions']
    })
```

---

### **3. Agent Initialization**
**File:** `/backend/agent/langgraph_agent.py`

```python
class OneDevelopmentAgent:
    def __init__(self):
        # 1. Initialize OpenAI
        self.llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # 2. Initialize Embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # 3. Initialize ChromaDB (Persistent)
        chroma_db_path = BASE_DIR / 'chroma_db'
        self.chroma_client = chromadb.PersistentClient(
            path=str(chroma_db_path)
        )
        
        # 4. Get or create collection
        self.collection = self.chroma_client.get_collection(
            "onedevelopment_knowledge"
        )
        
        # 5. Build LangGraph workflow
        self.graph = self._build_graph()
```

---

### **4. Knowledge Retrieval**
**File:** `/backend/agent/langgraph_agent.py` (line ~200)

```python
def retrieve_context(self, state: AgentState) -> AgentState:
    """Retrieve relevant context from knowledge base"""
    query = state['user_query']
    
    # Query ChromaDB for similar documents
    if self.collection is not None:
        try:
            results = self.collection.query(
                query_texts=[query],    # User's question
                n_results=3             # Get top 3 matches
            )
            
            if results['documents']:
                # Extract matched knowledge
                state['context'] = results['documents'][0]
            else:
                state['context'] = []
        except Exception as e:
            print(f"Vector search failed: {str(e)}")
            
            # Fallback: Direct database query
            from agent.models import KnowledgeBase
            kb_entries = KnowledgeBase.objects.filter(
                is_active=True
            )[:3]
            state['context'] = [entry.content for entry in kb_entries]
    
    return state
```

---

### **5. Response Generation**
**File:** `/backend/agent/langgraph_agent.py` (line ~250)

```python
def generate_response(self, state: AgentState) -> AgentState:
    """Generate response using LLM with retrieved context"""
    
    # Build prompt with context
    context_str = "\n\n".join(state['context']) if state['context'] else ""
    
    prompt = f"""You are Nova, an AI agent for One Development.
    
Context from knowledge base:
{context_str}

User question: {state['user_query']}

Provide a helpful, accurate response based on the context above."""
    
    # Call OpenAI GPT-4
    response = self.llm.invoke(prompt)
    
    state['response'] = response.content
    return state
```

---

## 🗄️ **Where Knowledge Is Stored:**

### **Locations:**

1. **Source of Truth: PostgreSQL**
   ```
   /var/lib/pgsql/data/
   Database: onedevelopment_agent
   Table: agent_knowledgebase (12 rows)
   ```

2. **Vector Store: ChromaDB**
   ```
   /home/ec2-user/OneDevelopment-Agent/backend/chroma_db/
   Collection: onedevelopment_knowledge (12 docs)
   Format: SQLite + vectors
   ```

3. **Application Code:**
   ```
   /home/ec2-user/OneDevelopment-Agent/backend/agent/
   ├── langgraph_agent.py  (Main agent logic)
   ├── models.py           (Database models)
   └── views.py            (API endpoints)
   ```

---

## 📊 **Current Knowledge Base Content:**

**Run this to see all knowledge:**
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py shell

from agent.models import KnowledgeBase
for kb in KnowledgeBase.objects.filter(is_active=True):
    print(f"{kb.id}: {kb.title} ({kb.source_type})")
```

**Current Entries (12 total):**
1. One Development - Company Overview
2. **Upcoming Developments 2025** (Marina Heights, etc.)
3. Investment Opportunities and ROI
4. Office Hours and Contact Information
5. Premium Amenities
6. Property Prices and Payment Plans
7. Why Choose One Development
8. Property Features and Amenities
9. Investment Opportunities
10. Location and Contact
11. Services Offered
12. About One Development

---

## 🔧 **How to Add New Knowledge:**

### **Method 1: Django Admin (GUI)**
```
1. Go to: http://51.20.117.103:8000/admin
2. Login: admin / OneDev2024!
3. Click "Knowledge Bases"
4. Click "ADD KNOWLEDGE BASE"
5. Fill in details
6. Save
7. Restart backend (it will auto-sync to ChromaDB)
```

### **Method 2: Python Shell**
```python
from agent.models import KnowledgeBase

KnowledgeBase.objects.create(
    title='New Knowledge Title',
    content='Detailed content here...',
    summary='Brief summary',
    source_type='manual',  # or 'linkedin', 'website'
    metadata={'category': 'your_category'},
    is_active=True
)

# Restart backend to sync to ChromaDB
```

### **Method 3: API (Future)**
```bash
curl -X POST http://51.20.117.103:8000/api/knowledge/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Info",
    "content": "Content here...",
    "source_type": "manual"
  }'
```

---

## 🔍 **Debugging & Monitoring:**

### **See What Nova Knows:**
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py shell

from agent.langgraph_agent import OneDevelopmentAgent
agent = OneDevelopmentAgent()

# Check vector store
print(f"Vector store has {agent.collection.count()} documents")

# Test query
result = agent.process_query("What are your upcoming developments?", "test")
print(result['response'][:200])
```

### **Check What Context Was Retrieved:**
```python
# In langgraph_agent.py, add logging:
def retrieve_context(self, state: AgentState) -> AgentState:
    results = self.collection.query(...)
    
    print("🔍 Retrieved context:")
    for doc in results['documents'][0]:
        print(f"  - {doc[:100]}...")  # Print first 100 chars
    
    return state
```

### **View Logs:**
```bash
# Backend logs
tail -f /tmp/backend.log

# See agent activity
cd /home/ec2-user/OneDevelopment-Agent
./manage-servers.sh logs backend
```

---

## 🎯 **Data Flow Example:**

**User asks:** "What are your upcoming developments?"

```
1. Frontend sends:
   POST /api/chat/
   { "message": "What are your upcoming developments?" }

2. Backend receives, calls agent:
   agent.process_query(query, session_id)

3. Agent workflow:
   a) analyze_input()
      → Extracts: "upcoming", "developments"
   
   b) retrieve_context()
      → Converts query to vector embedding
      → ChromaDB searches similar vectors
      → Finds: "Upcoming Developments 2025" entry
      → Returns: Marina Heights Tower, Palm Residence content
   
   c) classify_intent()
      → Intent: "projects"
   
   d) generate_response()
      → Calls OpenAI with:
         Context: "Marina Heights Tower - 45-story..."
         Question: "What are your upcoming developments?"
      → GPT-4 generates response
   
   e) update_memory()
      → Saves conversation to PostgreSQL

4. Response sent back:
   {
     "response": "We have exciting projects launching in 2025...",
     "intent": "projects",
     "suggested_actions": ["What are the prices?", ...]
   }

5. Frontend displays response
```

---

## 📈 **Performance Metrics:**

- **Vector search**: ~50-100ms
- **OpenAI API call**: ~1-3 seconds
- **Total response time**: ~1.5-3.5 seconds
- **Knowledge base size**: 12 entries
- **Vector store size**: 248 KB

---

## 🚀 **Scaling Considerations:**

### **Current Setup (Development):**
- PostgreSQL: Local instance
- ChromaDB: File-based persistent storage
- OpenAI: Direct API calls

### **For Production:**
- PostgreSQL: RDS or managed service
- ChromaDB: Could move to Pinecone, Weaviate, or hosted ChromaDB
- Caching: Redis for frequent queries
- Load balancing: Multiple backend instances

---

## 📁 **Key Files Reference:**

```
Backend:
├── agent/
│   ├── langgraph_agent.py    ← Main agent logic (500 lines)
│   ├── models.py              ← Database models
│   ├── views.py               ← API endpoints
│   └── urls.py                ← API routes
├── chroma_db/                 ← Vector store (persistent)
├── config/
│   └── settings.py            ← Django settings
└── .env                       ← Credentials (OpenAI key, DB password)

Frontend:
├── src/
│   ├── services/api.js        ← API calls
│   └── components/
│       ├── ChatInterface.js   ← Main UI
│       └── ChatInterface.css  ← Styling

Database:
└── PostgreSQL (port 5432)
    └── onedevelopment_agent
        └── agent_knowledgebase (12 rows)
```

---

## 🔑 **Configuration:**

**Backend `.env`:**
```bash
OPENAI_API_KEY=sk-proj-...
DB_NAME=onedevelopment_agent
DB_USER=onedevelopment
DB_PASSWORD=onedevelopment123
DEBUG=True
```

**Access:**
- Frontend: http://51.20.117.103:3000
- Backend API: http://51.20.117.103:8000/api/
- Admin Panel: http://51.20.117.103:8000/admin
- Database: localhost:5432

---

## 🎓 **Understanding the Architecture:**

**RAG (Retrieval-Augmented Generation):**
- Instead of training a custom model (expensive!)
- We give GPT-4 relevant context from our knowledge base
- GPT-4 generates responses based on that context
- This keeps responses accurate and up-to-date

**Why ChromaDB + Embeddings?**
- Simple keyword search misses semantic meaning
- "upcoming properties" and "new developments" = same meaning
- Embeddings understand context and meaning
- ChromaDB finds similar meanings, not just matching words

**Why LangGraph?**
- Orchestrates multi-step workflows
- Each node does one thing (retrieve, classify, generate)
- Easy to add new steps (e.g., validation, fact-checking)
- Better than simple prompt → response

---

## 🔧 **Adding More Data Sources:**

**LinkedIn (as discussed):**
1. Export LinkedIn data
2. Add to Knowledge Base via admin
3. Auto-syncs to ChromaDB
4. Nova can answer LinkedIn questions

**Website Scraping:**
```python
# Can scrape onedevelopment.ae
# Add scraped content to Knowledge Base
# Automatic indexing in ChromaDB
```

**Documents (PDFs, etc.):**
```python
from PyPDF2 import PdfReader

# Extract text from PDF
reader = PdfReader('brochure.pdf')
text = ''.join([page.extract_text() for page in reader.pages])

# Add to knowledge base
KnowledgeBase.objects.create(
    title='Property Brochure',
    content=text,
    source_type='document'
)
```

---

**That's the complete data flow!** 🎯

**Questions? Check the code in these files:**
- `/backend/agent/langgraph_agent.py` (main logic)
- `/backend/agent/models.py` (data structure)
- `/backend/agent/views.py` (API endpoints)

