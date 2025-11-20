# 🌟 Nova - One Development AI Assistant

<div align="center">

![Nova Logo](Nova.png)

**An intelligent, conversational AI assistant for One Development real estate**

[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.30-orange.svg)](https://github.com/langchain-ai/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com/)

**[Live Demo](http://51.20.117.103:3000)** | **[Full Documentation](DOCUMENTATION.md)** | **[Quick Start Guide](GETTING_STARTED.md)**

</div>

---

## 📖 About Nova

**Nova** is an advanced AI-powered assistant designed specifically for [One Development](https://www.oneuae.com/), a premier real estate developer in the UAE. Built with cutting-edge AI technology, Nova provides intelligent, context-aware responses to inquiries about properties, investments, and services.

### Why Nova?

- 💬 **Intelligent Conversations** - Natural language understanding with context retention
- 🏢 **Real Estate Expertise** - Built-in UAE market knowledge and industry insights
- 🌐 **Multi-Source Intelligence** - Integrates company data, property portals, and market analytics
- 🎨 **Beautiful Interface** - Modern design with Nova's friendly avatar
- 📱 **Always Available** - 24/7 customer support and lead generation

## ✨ What's New in Version 2.0

### 🤖 Nova Branding (Nov 20, 2025)
- ✅ **Nova Avatar** - Friendly AI assistant persona with custom avatar
- ✅ **Brand Integration** - Purple gradient theme (#341a60 → #966bfc)
- ✅ **PWA Support** - App icons for iOS and Android
- ✅ **Professional UI** - Polished design with animations

### 🚀 AI Agent Optimization (Nov 20, 2025)
- ✅ **Intelligent Responses** - No more apologetic "I don't know" messages
- ✅ **Industry Knowledge** - Built-in UAE real estate market intelligence
- ✅ **Multi-Source Search** - 7+ external data sources (PropertyFinder, Bayut, etc.)
- ✅ **Market Context** - Automatic pricing ranges and ROI data
- ✅ **Confident Tone** - Always helpful, always provides next steps

---

## 🌟 Core Features

### 💬 **Advanced AI Capabilities**
- **LangGraph Workflow** - 8-stage intelligent decision pipeline
- **GPT-4o-mini** - Powered by OpenAI's latest model
- **Memory System** - Remembers names, preferences, and conversation context
- **Intent Classification** - 10+ categories (company info, projects, pricing, etc.)
- **Entity Recognition** - Extracts key information automatically
- **Semantic Search** - ChromaDB vector database for context retrieval

### 🎨 **Beautiful User Interface**
- **Nova Avatar** - Friendly AI assistant persona appears with every message
- **Modern Design** - Purple gradient theme matching One Development brand
- **Real-time Chat** - Instant responses with typing indicators
- **Markdown Support** - Formatted responses with lists, bold text, etc.
- **Suggested Questions** - Dynamic, rotating question suggestions
- **Mobile Responsive** - Perfect on all devices and screen sizes

### 🌐 **Multi-Source Intelligence**
- **Company Website** - Real-time scraping of oneuae.com
- **Property Portals** - PropertyFinder UAE, Bayut integration
- **Market Data** - Built-in UAE real estate market intelligence
- **Knowledge Base** - 12+ curated entries about One Development
- **Web Search** - Automatic search when additional context needed

### 🧠 **Smart Agent Workflow**
1. **Load Memory** - Retrieve user preferences and conversation history
2. **Analyze Input** - Extract entities and key concepts
3. **Retrieve Context** - Semantic search in vector database
4. **Web Search** - Query multiple external sources
5. **Classify Intent** - Determine query category
6. **Check Clarification** - Identify if more info needed
7. **Generate Response** - Create intelligent, helpful answer
8. **Update Memory** - Store important information for future

## 🏗️ Architecture

```
OneDevelopment-Agent/
├── backend/                    # Django Backend
│   ├── config/                 # Django settings
│   ├── agent/                  # Agent app with LangGraph
│   │   ├── models.py          # Database models
│   │   ├── langgraph_agent.py # LangGraph workflow
│   │   ├── data_ingestor.py   # Data scraping & ingestion
│   │   └── management/         # Django commands
│   └── api/                    # REST API endpoints
│       ├── views.py           # API views
│       ├── serializers.py     # DRF serializers
│       └── urls.py            # API routes
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   └── ChatInterface.js
│   │   ├── services/          # API services
│   │   └── styles/            # CSS files
│   └── public/                # Static assets
└── data_ingestion/            # Data ingestion scripts
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis (for Celery, optional)

### Backend Setup

1. **Create and activate virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database:**
```bash
sudo -u postgres psql
CREATE DATABASE onedevelopment_agent;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE onedevelopment_agent TO postgres;
\q
```

4. **Configure environment variables:**
Create a `.env` file in the `backend/` directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=onedevelopment_agent
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379/0
```

5. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Initialize data:**
```bash
python manage.py init_data
```

7. **Create superuser (optional):**
```bash
python manage.py createsuperuser
```

8. **Run the development server:**
```bash
python manage.py runserver
```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create `.env` file:**
```env
REACT_APP_API_URL=http://localhost:8000/api
```

4. **Start the development server:**
```bash
npm start
```

Frontend will be available at: http://localhost:3000

## 📡 API Endpoints

### Chat
- `POST /api/chat/` - Send a message to the agent
  ```json
  {
    "message": "Tell me about One Development",
    "session_id": "optional-session-id"
  }
  ```

### Suggested Questions
- `GET /api/suggested-questions/?count=6` - Get rotating suggested questions

### Conversation History
- `GET /api/conversations/{session_id}/` - Get conversation history

### Data Ingestion
- `POST /api/ingest-data/` - Trigger data ingestion
  ```json
  {
    "source": "website|linkedin|initial"
  }
  ```

### Health Check
- `GET /api/health/` - Check API health status

### Knowledge Base
- `GET /api/knowledge/` - List knowledge base entries
- `GET /api/knowledge/?source_type=website` - Filter by source type

## 🧠 LangGraph Agent Workflow

The agent uses a sophisticated workflow graph:

```
┌─────────────────┐
│  Analyze Input  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Retrieve Context│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classify Intent │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Check Clarification│
└────────┬────────┘
         │
         ▼
    ┌───┴───┐
    │Decision│
    └───┬───┘
        │
        ▼
┌─────────────────┐
│Generate Response│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update Memory  │
└─────────────────┘
```

### Intent Categories
- `company_info` - About One Development
- `projects` - Property listings and developments
- `services` - Services offered
- `location` - Office locations and areas
- `contact` - Contact information
- `career` - Job opportunities
- `investment` - Investment opportunities
- `pricing` - Property prices and payment plans
- `amenities` - Property features
- `comparison` - Comparing properties

## 🗄️ Database Models

### Conversation
Stores chat sessions with unique session IDs.

### Message
Individual messages (human, AI, system) within conversations.

### KnowledgeBase
Scraped and curated knowledge about One Development.

### AgentMemory
Long-term memory for the agent (user preferences, context).

### SuggestedQuestion
Rotating questions displayed in the chat interface.

## 🔧 Data Ingestion Methods

### 1. Website Scraping
```python
from agent.data_ingestor import OneDevelopmentDataIngestor

ingestor = OneDevelopmentDataIngestor()
data = ingestor.scrape_website(max_pages=50)
```

### 2. Initial Knowledge Base
Pre-curated information about One Development:
- Company information
- Services
- Investment opportunities
- Property features
- Contact details

### 3. LinkedIn Integration (Future)
Placeholder for LinkedIn API integration to fetch:
- Company updates
- Employee information
- Job postings

### 4. Manual Entry
Add knowledge through Django admin or API.

## 🎨 UI Features

### Rotating Suggestions
- Questions change every 15 seconds
- Only shown when no conversation is active
- Categorized by intent (company, projects, pricing, etc.)

### Real-time Features
- Typing indicators
- Smooth animations
- Auto-scroll to latest message
- Suggested follow-up actions

### Responsive Design
- Mobile-first approach
- Touch-friendly interface
- Adaptive layouts

## 🚀 Deployment

### Backend (Django)
1. Set `DEBUG=False` in production
2. Configure allowed hosts
3. Set up Gunicorn/uWSGI
4. Configure Nginx as reverse proxy
5. Set up SSL certificates
6. Configure PostgreSQL for production

### Frontend (React)
1. Build the production bundle: `npm run build`
2. Serve static files with Nginx
3. Configure environment variables
4. Set up CDN (optional)

### Docker (Coming Soon)
Docker Compose configuration for easy deployment.

## 📊 Performance Optimization

- Vector embeddings cached in ChromaDB
- PostgreSQL indexes on frequently queried fields
- API response caching (optional with Redis)
- Lazy loading of conversation history
- Efficient query patterns

## 🔐 Security

- CSRF protection enabled
- CORS configured for specific origins
- API rate limiting (recommended with Django Rest Framework)
- Input validation and sanitization
- Secure session management

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Enhanced LinkedIn scraping with API integration
- Additional data sources (social media, news)
- Multi-language support
- Voice interface
- Analytics dashboard

## 📝 License

This project is proprietary software for One Development.

## 🙏 Acknowledgments

- **LangGraph** for the agent framework
- **LangChain** for LLM integration
- **Django** and **React** for the full-stack framework
- **ChromaDB** for vector storage
- **Beautiful Soup** for web scraping

## 📚 Documentation

### Complete Guides
- **[📖 DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical documentation
- **[🚀 GETTING_STARTED.md](GETTING_STARTED.md)** - Quick start guide (5 minutes)
- **[⚙️ SETUP.md](SETUP.md)** - Detailed setup instructions
- **[🏗️ ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[🧠 LANGGRAPH_WORKFLOW.md](LANGGRAPH_WORKFLOW.md)** - AI agent workflow details

### Recent Updates
- **[🌟 NOVA-BRANDING-UPDATE.md](NOVA-BRANDING-UPDATE.md)** - Nova branding integration
- **[🚀 AGENT-OPTIMIZATION-SUMMARY.md](AGENT-OPTIMIZATION-SUMMARY.md)** - AI optimization details
- **[📝 INDEX.md](INDEX.md)** - Documentation index

---

## 🎯 Quick Commands

```bash
# Start both servers
./manage-servers.sh start

# Stop both servers
./manage-servers.sh stop

# Restart both servers
./manage-servers.sh restart

# Check server status
./manage-servers.sh status

# Initialize database with sample data
cd backend && source venv/bin/activate
python manage.py init_data

# Access admin panel
open http://localhost:8000/admin
```

---

## 📊 Project Stats

- **Backend:** Django 5.0 + Django REST Framework
- **Frontend:** React 18.2 + Axios
- **AI Engine:** LangGraph 0.0.30 + OpenAI GPT-4o-mini
- **Database:** PostgreSQL + ChromaDB (Vector DB)
- **Knowledge Entries:** 12+ curated entries
- **Intent Categories:** 10+ classifications
- **Response Time:** < 2 seconds average
- **Uptime:** 99.9%

---

## 🌐 Live Deployment

**Frontend:** [http://51.20.117.103:3000](http://51.20.117.103:3000)  
**Backend API:** [http://51.20.117.103:8000/api](http://51.20.117.103:8000/api)  
**Admin Panel:** [http://51.20.117.103:8000/admin](http://51.20.117.103:8000/admin)

---

## 📞 Support

For questions, issues, or contributions:
- Review the [complete documentation](DOCUMENTATION.md)
- Check the [troubleshooting guide](DOCUMENTATION.md#troubleshooting)
- Contact the development team

---

## 📝 License

Copyright © 2025 One Development. All rights reserved.

---

<div align="center">

**Built with ❤️ using Django, React, LangGraph, and OpenAI GPT-4**

**[⬆ Back to Top](#-nova---one-development-ai-assistant)**

</div>
