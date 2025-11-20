# 🚀 Getting Started with One Development AI Agent

Welcome! This guide will help you get the One Development AI Agent up and running in minutes.

## 📋 What You'll Need

Before starting, ensure you have:

- [ ] **Python 3.9+** installed
- [ ] **Node.js 16+** installed  
- [ ] **PostgreSQL 13+** installed and running
- [ ] **OpenAI API Key** (get from https://platform.openai.com/api-keys)
- [ ] **Git** installed (if cloning from repository)

## ⚡ Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

```bash
cd /home/ec2-user/OneDevelopment-Agent
./quick-start.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Set up Python virtual environment
3. ✅ Install all dependencies
4. ✅ Create configuration files
5. ✅ Initialize database
6. ✅ Load initial data

### Option 2: Manual Setup

If you prefer to understand each step:

**1. Backend Setup (3 minutes)**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DEBUG=True
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=onedevelopment_agent
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-api-key-here
REDIS_URL=redis://localhost:6379/0
EOF

# Setup database
python manage.py migrate
python manage.py init_data

# Create admin user (optional)
python manage.py createsuperuser
```

**2. Frontend Setup (2 minutes)**

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
```

## 🎯 Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

✅ Backend running at: **http://localhost:8000**

### Start Frontend (New Terminal)

```bash
cd frontend
npm start
```

✅ Frontend running at: **http://localhost:3000**

## 🎨 First Look

Open your browser and navigate to **http://localhost:3000**

You should see:
- 🏢 **Beautiful gradient interface**
- 💬 **Welcome message**
- ❓ **6 suggested questions** (rotating every 15 seconds)
- 📝 **Chat input box**

### Try These Questions:

1. "Tell me about One Development"
2. "What properties do you have?"
3. "How can I contact you?"
4. "What are the investment opportunities?"

## 🔧 Configuration

### Update OpenAI API Key

**IMPORTANT**: The system won't work without a valid OpenAI API key!

```bash
# Edit backend/.env
nano backend/.env

# Update this line:
OPENAI_API_KEY=sk-your-actual-openai-api-key
```

Get your API key from: https://platform.openai.com/api-keys

### Database Configuration

If you're not using default PostgreSQL settings:

```bash
# Edit backend/.env
nano backend/.env

# Update these lines:
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

## 📚 Next Steps

### 1. Access Django Admin

Create a superuser if you haven't:

```bash
cd backend
python manage.py createsuperuser
```

Visit: **http://localhost:8000/admin**

You can manage:
- 📊 Conversations and messages
- 📚 Knowledge base entries
- ❓ Suggested questions
- 💾 Agent memory

### 2. Add Real Data

The system comes with initial sample data. To add real One Development data:

**Method 1: Using API**
```bash
curl -X POST http://localhost:8000/api/ingest-data/ \
  -H "Content-Type: application/json" \
  -d '{"source": "initial"}'
```

**Method 2: Using Django Shell**
```python
cd backend
source venv/bin/activate
python manage.py shell

from agent.data_ingestor import OneDevelopmentDataIngestor
ingestor = OneDevelopmentDataIngestor()
data = ingestor.scrape_website(max_pages=20)
```

See **DATA_INGESTION_GUIDE.md** for detailed instructions.

### 3. Customize Suggested Questions

```bash
cd backend
python manage.py shell

from agent.models import SuggestedQuestion

# Add a new question
SuggestedQuestion.objects.create(
    question="Your custom question here?",
    category="general",
    priority=10,
    is_active=True
)
```

### 4. Test the Agent

```python
cd backend
python manage.py shell

from agent.langgraph_agent import OneDevelopmentAgent

agent = OneDevelopmentAgent()
result = agent.process_query("Tell me about luxury villas")

print("Response:", result['response'])
print("Intent:", result['intent'])
print("Suggestions:", result['suggested_actions'])
```

## 🔍 Verify Everything Works

### Health Check

```bash
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T...",
  "agent_initialized": true
}
```

### Test Chat API

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, tell me about One Development"}'
```

### Check Frontend

Visit http://localhost:3000 and:
1. ✅ See the welcome screen
2. ✅ Click a suggested question
3. ✅ Get a response from the AI
4. ✅ See follow-up suggestions

## 🐛 Troubleshooting

### Backend Won't Start

**Issue**: `django.db.utils.OperationalError`
**Solution**: Verify PostgreSQL is running and credentials are correct

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U postgres -d onedevelopment_agent
```

### Frontend Can't Connect

**Issue**: API calls failing
**Solution**: Verify backend is running on port 8000

```bash
# Check if port 8000 is in use
lsof -i :8000

# Restart backend
cd backend
python manage.py runserver
```

### OpenAI API Errors

**Issue**: `AuthenticationError`
**Solution**: Check your API key

```bash
# Verify API key is set
cd backend
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### Dependencies Missing

**Issue**: `ModuleNotFoundError`
**Solution**: Reinstall dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📖 Learn More

Now that you're up and running, explore:

1. **README.md** - Full feature overview
2. **ARCHITECTURE.md** - System design details
3. **LANGGRAPH_WORKFLOW.md** - How the AI works
4. **DATA_INGESTION_GUIDE.md** - Adding more knowledge
5. **DEPLOYMENT.md** - Production deployment

## 🎯 Common Tasks

### Add Knowledge Manually

```python
from agent.models import KnowledgeBase

KnowledgeBase.objects.create(
    source_type='manual',
    title='New Property Launch',
    content='Exciting new development in Dubai Marina...',
    summary='New Marina property',
    is_active=True
)
```

### View Conversations

```python
from agent.models import Conversation, Message

# Get recent conversations
convos = Conversation.objects.order_by('-created_at')[:5]

for convo in convos:
    print(f"Session: {convo.session_id}")
    print(f"Messages: {convo.messages.count()}")
```

### Update Suggested Questions

```python
from agent.models import SuggestedQuestion

# Make a question inactive
question = SuggestedQuestion.objects.get(question="Old question")
question.is_active = False
question.save()

# Change priority
question = SuggestedQuestion.objects.get(question="Important question")
question.priority = 20
question.save()
```

## 💡 Tips for Best Experience

### 1. Keep OpenAI API Key Valid
- Monitor usage: https://platform.openai.com/usage
- Set up billing alerts
- Keep key secure (never commit to git)

### 2. Regular Data Updates
- Scrape website weekly
- Add new properties as they launch
- Update suggested questions seasonally

### 3. Monitor Performance
- Check logs regularly
- Review conversation history
- Track popular questions

### 4. Customize for Your Brand
- Update colors in `frontend/src/components/ChatInterface.css`
- Modify welcome message in `ChatInterface.js`
- Add your logo in `frontend/public/`

## 🚀 Ready for Production?

When you're ready to deploy:

1. **Read DEPLOYMENT.md**
2. **Set up proper PostgreSQL database**
3. **Configure SSL certificates**
4. **Set up monitoring**
5. **Configure backups**

## 🎉 You're All Set!

Your One Development AI Agent is ready to:
- ✅ Answer questions about One Development
- ✅ Classify user intent automatically
- ✅ Remember conversation context
- ✅ Provide relevant suggestions
- ✅ Learn from interactions

## 🆘 Need Help?

- 📖 Check the documentation files
- 🐛 Review troubleshooting section
- 💬 Test with simple queries first
- 🔍 Check Django logs: `backend/logs/`

## 📞 Quick Reference

```bash
# Start backend
cd backend && source venv/bin/activate && python manage.py runserver

# Start frontend
cd frontend && npm start

# Run migrations
cd backend && python manage.py migrate

# Initialize data
cd backend && python manage.py init_data

# Django shell
cd backend && python manage.py shell

# Create superuser
cd backend && python manage.py createsuperuser

# Health check
curl http://localhost:8000/api/health/
```

---

**Enjoy your intelligent AI agent! 🤖✨**

Built with ❤️ for One Development

