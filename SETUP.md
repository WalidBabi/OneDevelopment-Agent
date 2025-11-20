# 🚀 Quick Setup Guide

## Step-by-Step Setup

### 1. PostgreSQL Setup

```bash
# Install PostgreSQL (if not already installed)
# On Ubuntu/Debian:
sudo apt update
sudo apt install postgresql postgresql-contrib

# On macOS:
brew install postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE onedevelopment_agent;
CREATE USER agentuser WITH PASSWORD 'securepassword123';
ALTER ROLE agentuser SET client_encoding TO 'utf8';
ALTER ROLE agentuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE agentuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE onedevelopment_agent TO agentuser;
\q
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DEBUG=True
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=onedevelopment_agent
DB_USER=agentuser
DB_PASSWORD=securepassword123
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-api-key-here
REDIS_URL=redis://localhost:6379/0
EOF

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Initialize data
python manage.py init_data

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env

# Start development server
npm start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin

## 🔧 Configuration Options

### OpenAI API Key

Get your API key from: https://platform.openai.com/api-keys

Update in `backend/.env`:
```env
OPENAI_API_KEY=sk-your-actual-api-key
```

### Data Ingestion

To scrape One Development website:

```bash
cd backend
source venv/bin/activate
python manage.py shell

from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.langgraph_agent import OneDevelopmentAgent

# Initialize ingestor
ingestor = OneDevelopmentDataIngestor()

# Scrape website (adjust max_pages as needed)
data = ingestor.scrape_website(max_pages=20)

# Add to knowledge base
from agent.models import KnowledgeBase
agent = OneDevelopmentAgent()

for item in data:
    # Save to database
    KnowledgeBase.objects.create(
        source_type=item.get('source_type', 'website'),
        source_url=item.get('url'),
        title=item.get('title', 'Untitled'),
        content=item.get('content', ''),
        summary=item.get('content', '')[:500],
        metadata=item
    )
    
    # Add to vector store
    agent.add_knowledge(
        content=item.get('content', ''),
        metadata={'source': item.get('source_type'), 'title': item.get('title')}
    )
```

Or use the API endpoint:

```bash
curl -X POST http://localhost:8000/api/ingest-data/ \
  -H "Content-Type: application/json" \
  -d '{"source": "website"}'
```

## 🧪 Testing the Agent

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health/

# Send a message
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about One Development"}'

# Get suggested questions
curl http://localhost:8000/api/suggested-questions/?count=5
```

### Test in Python Shell

```bash
cd backend
python manage.py shell

from agent.langgraph_agent import OneDevelopmentAgent

agent = OneDevelopmentAgent()

# Test a query
result = agent.process_query(
    query="What properties do you have?",
    session_id="test-session"
)

print(result['response'])
print(result['intent'])
print(result['suggested_actions'])
```

## 🎨 Customization

### Add More Suggested Questions

```bash
python manage.py shell

from agent.models import SuggestedQuestion

SuggestedQuestion.objects.create(
    question="Your custom question here",
    category="general",
    priority=10,
    is_active=True
)
```

### Update Agent Prompts

Edit `backend/agent/langgraph_agent.py` and modify the `system_prompts` dictionary in the `generate_response` method.

### Customize UI Theme

Edit `frontend/src/components/ChatInterface.css` to change colors, fonts, and styles.

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify credentials
psql -U agentuser -d onedevelopment_agent -h localhost
```

### OpenAI API Error

- Verify API key is correct
- Check API quota/credits: https://platform.openai.com/usage
- Ensure no firewall blocking OpenAI API

### Frontend Can't Connect to Backend

- Verify backend is running on port 8000
- Check CORS settings in `backend/config/settings.py`
- Verify proxy setting in `frontend/package.json`

### Missing Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📚 Next Steps

1. **Add Real Data**: Scrape One Development website or add manual entries
2. **Customize Branding**: Update colors, logos, and text
3. **Deploy to Production**: Follow deployment guide in README.md
4. **Add Analytics**: Track user interactions and popular queries
5. **Enhance Agent**: Add more intents and refine responses

## 🆘 Getting Help

If you encounter issues:
1. Check the logs in `backend/` for error messages
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Check database connectivity
5. Verify OpenAI API key is valid

---

Happy building! 🎉

