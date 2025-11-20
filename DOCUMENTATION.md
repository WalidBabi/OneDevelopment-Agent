# 📚 OneDevelopment Agent - Complete Documentation

**Version:** 2.0  
**Last Updated:** November 20, 2025  
**Status:** Production Ready ✅

---

## 📖 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [API Documentation](#api-documentation)
9. [Frontend Components](#frontend-components)
10. [Backend Components](#backend-components)
11. [AI Agent System](#ai-agent-system)
12. [Database Schema](#database-schema)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)
15. [Contributing](#contributing)
16. [Recent Updates](#recent-updates)

---

## 🎯 Project Overview

### What is OneDevelopment Agent?

**Nova** (OneDevelopment AI Agent) is an intelligent, conversational AI assistant designed to provide real-time information about One Development's real estate properties, services, and offerings in the UAE. Built with cutting-edge AI technology, Nova delivers personalized, context-aware responses to user queries.

### Key Objectives

- ✅ Provide 24/7 intelligent customer support
- ✅ Answer questions about properties, pricing, and services
- ✅ Offer investment guidance and market insights
- ✅ Capture and qualify leads
- ✅ Deliver personalized user experiences
- ✅ Integrate with multiple data sources

### Use Cases

1. **Customer Inquiries** - Property details, amenities, locations
2. **Investment Consultation** - ROI information, market trends
3. **Lead Generation** - Contact information capture
4. **Property Comparison** - Feature and pricing comparisons
5. **General Information** - Company info, services, career opportunities

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React 18 SPA                                        │  │
│  │  - ChatInterface Component                           │  │
│  │  - Nova Avatar Integration                           │  │
│  │  - Real-time Message Display                         │  │
│  │  - Markdown Rendering                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Django 5.0 REST API                                 │  │
│  │  - Message Handling                                  │  │
│  │  - Session Management                                │  │
│  │  - Conversation History                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LangGraph AI Agent (Nova)                           │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ Workflow:                                      │  │  │
│  │  │ 1. Load Memory                                │  │  │
│  │  │ 2. Analyze Input                              │  │  │
│  │  │ 3. Retrieve Context (Vector DB)               │  │  │
│  │  │ 4. Web Search (Multiple Sources)              │  │  │
│  │  │ 5. Classify Intent                            │  │  │
│  │  │ 6. Check Clarification                        │  │  │
│  │  │ 7. Generate Response (GPT-4o-mini)            │  │  │
│  │  │ 8. Update Memory                              │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  PostgreSQL  │  │  ChromaDB    │  │  External APIs   │  │
│  │  Database    │  │  Vector DB   │  │  - PropertyFinder│  │
│  │              │  │              │  │  - Market Data   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → Frontend React Component
2. **API Request** → Django Backend (POST /api/chat/)
3. **Agent Processing** → LangGraph Workflow
4. **Context Retrieval** → ChromaDB Vector Search
5. **Web Search** → Multiple External Sources
6. **Response Generation** → OpenAI GPT-4o-mini
7. **Response Return** → Frontend Display

---

## ✨ Features

### Core Features

#### 1. **Intelligent Conversational AI**
- Natural language understanding
- Context-aware responses
- Multi-turn conversations
- Intent classification (10+ categories)
- Entity extraction

#### 2. **Knowledge Base Integration**
- Vector database (ChromaDB) for semantic search
- 12+ curated knowledge entries
- Real-time web scraping capability
- Multiple data source integration

#### 3. **Web Search & Market Intelligence**
- Company website scraping
- Property portal integration (PropertyFinder, Bayut)
- Real-time market data
- UAE real estate context
- Automatic market intelligence injection

#### 4. **Memory Management**
- Session-based conversation memory
- User preference tracking
- Name recognition and personalization
- Conversation history storage

#### 5. **Beautiful User Interface**
- Modern gradient design (Purple brand theme)
- Nova avatar integration
- Markdown rendering for formatted responses
- Typing indicators
- Smooth animations
- Mobile responsive

#### 6. **Lead Management**
- Suggested question system
- Dynamic follow-up suggestions
- Contact information capture
- Session tracking

### Advanced Features

#### 1. **Intelligent Response System**
- No apologetic responses
- Industry knowledge application
- Helpful bridging when data is missing
- Always provides next steps
- Confident and professional tone

#### 2. **Multi-Source Data Integration**
```
Primary Sources:
- oneuae.com (Company Website)
- Knowledge Base (Curated Content)

Secondary Sources:
- PropertyFinder UAE
- Bayut
- Dubai Properties Portals

Market Intelligence:
- Built-in UAE market data
- Area-specific pricing
- ROI benchmarks
- Payment plan standards
```

#### 3. **Admin Panel**
- Django Admin interface
- Knowledge base management
- Conversation history viewing
- User session monitoring
- Suggested questions management

---

## 🛠️ Technology Stack

### Frontend
```json
{
  "framework": "React 18.2.0",
  "ui_library": "Custom CSS with animations",
  "markdown": "react-markdown 8.0.7",
  "icons": "uuid 9.0.0",
  "state_management": "React Hooks",
  "http_client": "Axios"
}
```

### Backend
```json
{
  "framework": "Django 5.0",
  "rest_api": "Django REST Framework 3.14",
  "database": "PostgreSQL 14+",
  "vector_db": "ChromaDB 0.4.18",
  "ai_orchestration": "LangGraph 0.0.30",
  "llm": "OpenAI GPT-4o-mini",
  "embeddings": "HuggingFace MiniLM-L6-v2",
  "web_scraping": "BeautifulSoup4 4.12",
  "cors": "django-cors-headers"
}
```

### Infrastructure
```json
{
  "os": "Amazon Linux 2023",
  "server": "Development Server (Django + React)",
  "deployment": "EC2 Instance",
  "ports": {
    "frontend": 3000,
    "backend": 8000
  }
}
```

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- OpenAI API Key
- 4GB+ RAM
- Linux/Unix environment

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd OneDevelopment-Agent

# 2. Run automated setup
chmod +x quick-start.sh
./quick-start.sh

# 3. Configure environment variables
cd backend
nano .env
# Add your OpenAI API key and database credentials

# 4. Initialize database
python manage.py migrate
python manage.py init_data

# 5. Start servers
cd ..
./manage-servers.sh start
```

### Manual Installation

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
DB_NAME=onedevelopment_db
DB_USER=onedevelopment_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your_domain
EOF

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Initialize data
python manage.py init_data

# Start backend server
python manage.py runserver 0.0.0.0:8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure API endpoint
nano src/services/api.js
# Update BASE_URL to your backend URL

# Start frontend server
npm start
```

---

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...your-key-here

# Database Configuration
DB_NAME=onedevelopment_db
DB_USER=onedevelopment_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your.domain.com

# CORS Configuration (if frontend on different domain)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
```

#### Frontend (src/services/api.js)
```javascript
const BASE_URL = 'http://your-backend-url:8000/api';
```

### Agent Configuration

Edit `backend/agent/langgraph_agent.py`:

```python
# LLM Configuration
self.llm = ChatOpenAI(
    model="gpt-4o-mini",  # or "gpt-4" for better quality
    temperature=0.7,      # 0.0-1.0, higher = more creative
    api_key=self.api_key
)

# Intent Patterns
self.intent_patterns = {
    'company_info': ['about', 'company', 'who', 'what is', 'tell me'],
    'projects': ['project', 'development', 'property', 'building'],
    # Add more patterns...
}
```

### Web Sources Configuration

Edit `backend/agent/web_tools.py`:

```python
self.additional_sources = {
    'property_finder': 'https://www.propertyfinder.ae/...',
    'bayut': 'https://www.bayut.com/...',
    # Add more sources...
}
```

---

## 📘 Usage Guide

### For End Users

#### Starting a Conversation

1. Visit the web application
2. You'll see Nova's welcome screen with suggested questions
3. Click a suggested question or type your own
4. Nova will respond with helpful information

#### Example Queries

```
✅ "Tell me about One Development"
✅ "What properties do you have in Dubai Marina?"
✅ "How much does a 2-bedroom apartment cost?"
✅ "What's the investment return?"
✅ "Do you offer payment plans?"
✅ "What amenities do your properties have?"
✅ "I'm looking for a property under AED 2M"
```

#### Tips for Best Results

- Be specific about your requirements
- Ask one question at a time
- Use follow-up questions for details
- Mention your name for personalization
- Save the session URL to continue later

### For Administrators

#### Accessing Admin Panel

```
URL: http://your-domain:8000/admin
Username: (your superuser username)
Password: (your superuser password)
```

#### Managing Knowledge Base

1. Login to admin panel
2. Navigate to "Knowledge Base"
3. Click "Add Knowledge Base" to create new entries
4. Fill in:
   - Title
   - Content
   - Source Type
   - Category
   - Metadata

#### Viewing Conversations

1. Navigate to "Messages" in admin panel
2. Filter by session, date, or message type
3. View full conversation threads

#### Adding Suggested Questions

1. Navigate to "Suggested Questions"
2. Click "Add Suggested Question"
3. Enter question, category, and priority
4. Save

---

## 🔌 API Documentation

### Base URL
```
http://your-domain:8000/api
```

### Endpoints

#### 1. Send Chat Message
```http
POST /api/chat/
```

**Request Body:**
```json
{
  "message": "Tell me about One Development",
  "session_id": "optional-session-uuid"
}
```

**Response:**
```json
{
  "response": "One Development is a premier real estate...",
  "intent": "company_info",
  "entities": ["One Development", "real estate"],
  "suggested_actions": [
    "Show me your latest projects",
    "What makes you unique?"
  ],
  "session_id": "uuid-here"
}
```

#### 2. Get Suggested Questions
```http
GET /api/suggested-questions/?limit=6
```

**Response:**
```json
[
  {
    "id": 1,
    "question": "Tell me about One Development",
    "category": "company_info",
    "priority": 10
  },
  ...
]
```

#### 3. Get Conversation History
```http
GET /api/conversation-history/{session_id}/
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "messages": [
    {
      "id": 1,
      "message_type": "user",
      "content": "Hello",
      "timestamp": "2025-11-20T10:30:00Z"
    },
    {
      "id": 2,
      "message_type": "assistant",
      "content": "Hello! How can I help?",
      "timestamp": "2025-11-20T10:30:05Z"
    }
  ]
}
```

#### 4. Health Check
```http
GET /api/health/
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-20T10:30:00Z"
}
```

#### 5. Data Ingestion (Admin Only)
```http
POST /api/ingest-data/
```

**Request Body:**
```json
{
  "source": "website|linkedin|manual",
  "data": { ... }
}
```

---

## 🎨 Frontend Components

### ChatInterface Component

**Location:** `frontend/src/components/ChatInterface.js`

**Features:**
- Real-time message display
- Nova avatar integration
- Typing indicators
- Suggested questions
- Markdown rendering
- Auto-scroll
- Session management

**Props:** None (standalone component)

**State:**
```javascript
{
  messages: [],              // Conversation messages
  inputMessage: '',          // Current user input
  isLoading: false,          // Loading state
  sessionId: null,           // Session UUID
  suggestedQuestions: [],    // Dynamic suggestions
  error: null               // Error messages
}
```

### Styling

**Location:** `frontend/src/components/ChatInterface.css`

**Brand Colors:**
```css
--primary-purple: #341a60
--secondary-purple: #966bfc
--light-font: #e6dafe
```

**Key Animations:**
- slideIn (messages)
- fadeInAvatar (Nova avatar)
- fadeInLogo (welcome screen)
- slideInPill (suggested questions)
- typing (loading indicator)

---

## 🧠 AI Agent System

### LangGraph Workflow

**File:** `backend/agent/langgraph_agent.py`

#### Workflow Nodes

1. **load_memory**
   - Retrieves session memory
   - Loads user name and preferences
   - Gets conversation context

2. **analyze_input**
   - Extracts entities from user query
   - Identifies key terms and concepts

3. **retrieve_context**
   - Performs semantic search in ChromaDB
   - Retrieves top 3 relevant knowledge entries

4. **web_search**
   - Searches company website
   - Queries property portals
   - Adds market intelligence

5. **classify_intent**
   - Classifies query into 10+ categories
   - Uses keyword pattern matching

6. **check_clarification**
   - Determines if clarification needed
   - Checks query ambiguity

7. **generate_response**
   - Builds context for LLM
   - Generates intelligent response
   - Applies formatting guidelines

8. **update_memory**
   - Stores important entities
   - Updates user preferences
   - Saves conversation context

### Intent Categories

```python
{
    'company_info': Company information queries
    'projects': Property and project inquiries
    'services': Service offerings
    'contact': Contact information
    'career': Job opportunities
    'investment': Investment queries
    'pricing': Pricing questions
    'amenities': Amenity inquiries
    'comparison': Property comparisons
    'general': General questions
}
```

### Memory System

**File:** `backend/agent/memory_manager.py`

**Features:**
- Session-based memory storage
- User name extraction and storage
- Preference tracking
- Entity accumulation
- Conversation context

---

## 🗄️ Database Schema

### Models

#### 1. Message
```python
class Message(models.Model):
    session_id = CharField(max_length=255)
    message_type = CharField(choices=['user', 'assistant'])
    content = TextField()
    intent = CharField(max_length=50, blank=True)
    entities = JSONField(default=list)
    timestamp = DateTimeField(auto_now_add=True)
```

#### 2. KnowledgeBase
```python
class KnowledgeBase(models.Model):
    source_type = CharField(choices=['manual', 'website', 'linkedin'])
    source_url = URLField(blank=True)
    title = CharField(max_length=500)
    content = TextField()
    summary = TextField()
    metadata = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
```

#### 3. AgentMemory
```python
class AgentMemory(models.Model):
    session_id = CharField(max_length=255)
    memory_type = CharField(choices=['user_info', 'preference', 'context'])
    key = CharField(max_length=255)
    value = TextField()
    timestamp = DateTimeField(auto_now_add=True)
```

#### 4. SuggestedQuestion
```python
class SuggestedQuestion(models.Model):
    question = CharField(max_length=500)
    category = CharField(max_length=50)
    priority = IntegerField(default=5)
    is_active = BooleanField(default=True)
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set DEBUG=False in backend/.env
- [ ] Configure proper SECRET_KEY
- [ ] Set up PostgreSQL production database
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS properly
- [ ] Set up proper logging
- [ ] Configure static file serving
- [ ] Set up monitoring and alerts
- [ ] Configure backup systems
- [ ] Test all endpoints
- [ ] Load test the system

### Server Management

```bash
# Start servers
./manage-servers.sh start

# Stop servers
./manage-servers.sh stop

# Restart servers
./manage-servers.sh restart

# Check status
./manage-servers.sh status
```

### Nginx Configuration (Production)

```nginx
# Backend
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    
    root /path/to/frontend/build;
    index index.html;
    
    location / {
        try_files $uri /index.html;
    }
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Symptoms:** Django server crashes on startup

**Solutions:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check database connection
python manage.py dbshell

# Check migrations
python manage.py showmigrations
python manage.py migrate
```

#### 2. Frontend Can't Connect to Backend

**Symptoms:** CORS errors, API requests fail

**Solutions:**
```javascript
// Check API URL in src/services/api.js
const BASE_URL = 'http://correct-backend-url:8000/api';

// Check backend CORS settings
// backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://your-frontend-url"
]
```

#### 3. Agent Not Responding

**Symptoms:** Empty or error responses from agent

**Solutions:**
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Check ChromaDB
ls backend/chroma_db/

# Reinitialize vector store
python manage.py shell
>>> from agent.langgraph_agent import OneDevelopmentAgent
>>> agent = OneDevelopmentAgent()
>>> # Add knowledge manually if needed
```

#### 4. Nova Avatar Not Showing

**Symptoms:** Broken image in chat

**Solutions:**
```bash
# Verify files exist
ls frontend/public/Nova.png
ls frontend/public/favicon.ico

# Clear browser cache
# Check browser console for errors
```

---

## 🔄 Recent Updates

### Version 2.0 (November 20, 2025)

#### Nova Branding Integration ✨
- Added Nova avatar to all assistant messages
- Integrated Nova.png and Nova.ico
- Updated manifest.json with Nova branding
- Created welcome screen avatar
- Added circular avatar with gradient border

#### Agent Optimization 🚀
- **Option 2:** Intelligent prompt system implemented
  - Removed apologetic responses
  - Added industry knowledge bridging
  - Enhanced system prompts with UAE real estate context
  - Confident and helpful tone

- **Option 3:** Enhanced web search integration
  - Added 7+ additional web sources
  - Property portal integration (PropertyFinder, Bayut)
  - Built-in UAE market intelligence
  - Automatic market context injection
  - Result caching for performance

#### Improvements
- Better error handling
- Graceful degradation
- No error messages shown to users
- Always provides value
- Market-aware responses

---

## 🤝 Contributing

### Development Guidelines

1. **Code Style**
   - Follow PEP 8 for Python
   - Use ESLint for JavaScript
   - Write descriptive commit messages

2. **Testing**
   - Test all API endpoints
   - Test frontend components
   - Test agent responses

3. **Documentation**
   - Update this documentation
   - Add inline code comments
   - Document new features

### Adding New Knowledge

```python
# In Django shell
from agent.models import KnowledgeBase

KnowledgeBase.objects.create(
    title="New Knowledge Entry",
    content="Detailed content here...",
    source_type="manual",
    metadata={"category": "category_name"}
)

# Add to vector store
from agent.langgraph_agent import OneDevelopmentAgent
agent = OneDevelopmentAgent()
agent.add_knowledge(
    content="Content here...",
    metadata={"title": "Title", "category": "category"}
)
```

---

## 📞 Support & Contact

### Documentation Files
- **INDEX.md** - Documentation index
- **GETTING_STARTED.md** - Quick start guide
- **SETUP.md** - Detailed setup
- **ARCHITECTURE.md** - System design
- **LANGGRAPH_WORKFLOW.md** - AI workflow
- **AGENT-OPTIMIZATION-SUMMARY.md** - Optimization details
- **NOVA-BRANDING-UPDATE.md** - Branding changes

### Useful Commands

```bash
# Backend
python manage.py migrate          # Run migrations
python manage.py init_data        # Initialize data
python manage.py createsuperuser  # Create admin user
python manage.py runserver        # Start backend

# Frontend
npm install                       # Install dependencies
npm start                         # Start development server
npm run build                     # Build for production

# Server Management
./manage-servers.sh start         # Start both servers
./manage-servers.sh stop          # Stop both servers
./manage-servers.sh restart       # Restart both servers
./manage-servers.sh status        # Check status
```

---

## 📝 License

Copyright © 2025 One Development. All rights reserved.

---

## 🎉 Conclusion

Nova (OneDevelopment AI Agent) is a production-ready, intelligent conversational assistant powered by cutting-edge AI technology. With comprehensive documentation, robust architecture, and continuous improvements, it's designed to provide exceptional customer experiences and drive business growth.

**Current Status:** ✅ Production Ready  
**Live URL:** http://51.20.117.103:3000  
**Admin Panel:** http://51.20.117.103:8000/admin

---

**Built with ❤️ using Django, React, LangGraph, and OpenAI GPT-4**


