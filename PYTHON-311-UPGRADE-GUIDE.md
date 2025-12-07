# Python 3.11+ Upgrade Guide for Full DeepAgents

**Current Status:** Luna is running in **compatibility mode** on Python 3.9  
**Target:** Upgrade to Python 3.11+ to enable full autonomous DeepAgents features

---

## 🎯 What You'll Get After Upgrading

### Current (Python 3.9 Compatibility Mode)
- ⚠️ Agent returns helpful message but can't execute queries
- ❌ No tool usage (24 tools available but not accessible)
- ❌ No autonomous reasoning or planning
- ❌ No subagent delegation
- ❌ No middleware (todos, filesystem, human-in-the-loop, etc.)
- ❌ No long-term memory backend

### After Upgrade (Python 3.11+ with DeepAgents)
- ✅ **Full autonomous agent** using `deepagents.create_deep_agent()`
- ✅ **24 tools active**: web search (Tavily), PDF reading, knowledge base, market data
- ✅ **4 specialized subagents**: research, pricing, comparison, buyer journey
- ✅ **5 middleware layers**: TodoList, Filesystem, SubAgent, Summarization, HumanInTheLoop
- ✅ **Long-term memory**: CompositeBackend with StateBackend + StoreBackend
- ✅ **Multi-step reasoning**: Planning, execution, verification, synthesis
- ✅ **LangSmith tracing**: Full observability into agent decisions

---

## 📋 Upgrade Methods

Choose based on your deployment:

### Option A: Docker Deployment (Recommended)
**Best for:** Production deployments, clean isolated environments

### Option B: Direct EC2 Python Upgrade
**Best for:** Development, testing, or if not using Docker

---

## 🐳 Option A: Docker Deployment

### Step 1: Create Backend Dockerfile

Create `/home/ec2-user/OneDevelopment-Agent/backend/Dockerfile`:

```dockerfile
# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install DeepAgents
RUN pip install --no-cache-dir deepagents

# Copy backend code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --clear || true

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
```

### Step 2: Update docker-compose.yml

Add or update the backend service in `/home/ec2-user/OneDevelopment-Agent/docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: onedev-backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LUNA_MODEL=openai:gpt-4o
      - LANGCHAIN_TRACING_V2=true
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
      - LANGCHAIN_PROJECT=luna-deepagent
      - TAVILY_API_KEY=${TAVILY_API_KEY}  # Optional for enhanced web search
    volumes:
      - ./backend:/app
      - ./backend/chroma_db:/app/chroma_db
    restart: unless-stopped
    
  frontend:
    # ... your existing frontend config ...
```

### Step 3: Update .env File

Create or update `/home/ec2-user/OneDevelopment-Agent/.env`:

```bash
# OpenAI (required)
OPENAI_API_KEY=sk-...

# LangSmith (optional but recommended for debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=luna-deepagent

# Tavily (optional - enhanced web search)
TAVILY_API_KEY=tvly-...

# Luna model (optional - defaults to gpt-4o)
LUNA_MODEL=openai:gpt-4o
```

### Step 4: Build and Deploy

```bash
cd /home/ec2-user/OneDevelopment-Agent

# Build with no cache to ensure clean Python 3.11 environment
docker-compose build --no-cache backend

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Wait for "Listening at: http://0.0.0.0:8000" message
```

### Step 5: Verify DeepAgents is Active

```bash
# Health check - should show version 4.0.0
curl http://localhost:8000/api/health/ | python -m json.tool

# Chat test - should use tools and reasoning
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about One Development projects",
    "session_id": "deepagents_test"
  }' | python -m json.tool

# Look for:
# - "tools_used" > 0 (agent is using tools!)
# - "reasoning_steps" > 0 (agent is thinking!)
# - Actual project information in "response"
```

---

## 🖥️ Option B: Direct EC2 Python Upgrade

### Step 1: Install Python 3.11

**Using pyenv (recommended):**

```bash
# Install pyenv if not already installed
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
exec $SHELL

# Install Python 3.11
pyenv install 3.11.8

# Set as local version for the project
cd /home/ec2-user/OneDevelopment-Agent/backend
pyenv local 3.11.8
```

**Or using system packages (Amazon Linux 2023):**

```bash
sudo dnf install python3.11 python3.11-pip python3.11-devel -y
```

### Step 2: Create New Virtual Environment

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend

# Remove old Python 3.9 venv
rm -rf venv

# Create new Python 3.11 venv
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Verify Python version
python --version  # Should show Python 3.11.x
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install backend dependencies
pip install -r requirements.txt

# Install DeepAgents
pip install deepagents

# Verify installation
python -c "import deepagents; print(f'DeepAgents {deepagents.__version__} installed!')"
```

### Step 4: Set Environment Variables

Add to `~/.bashrc` or create a `.env` file:

```bash
export OPENAI_API_KEY="sk-..."
export LUNA_MODEL="openai:gpt-4o"

# Optional: LangSmith tracing
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="lsv2-..."
export LANGCHAIN_PROJECT="luna-deepagent"

# Optional: Tavily for enhanced web search
export TAVILY_API_KEY="tvly-..."
```

Then reload:

```bash
source ~/.bashrc
```

### Step 5: Run Backend

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate

# Run tests first
python test_deepagent.py

# Expected: All tests pass WITHOUT compatibility mode warning

# Start server
python manage.py runserver 0.0.0.0:8000
```

### Step 6: Verify DeepAgents is Active

Same as Docker verification above.

---

## 🧪 Testing Full DeepAgents Features

Once upgraded, test these key capabilities:

### 1. Simple Query (Tool Usage)

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What projects does One Development have?",
    "session_id": "test_1"
  }'
```

**Expected:**
- `tools_used` ≥ 1 (should use `search_knowledge_base`)
- Actual project names in response (Laguna Residence, DO Dubai Islands, etc.)

### 2. Complex Multi-Step Query (Subagents + Middleware)

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to invest in Dubai real estate with good ROI. Compare Dubai Marina vs Palm Jumeirah.",
    "session_id": "test_2"
  }'
```

**Expected:**
- `tools_used` ≥ 3 (planning, research, comparison, context tools)
- `reasoning_steps` ≥ 5 (thinking → planning → research → comparison → synthesis)
- Structured comparison with pricing, ROI, pros/cons
- Evidence of subagent delegation (research-agent, pricing-agent, comparison-agent)

### 3. Conversation Memory (Long-term Memory)

```bash
# First message
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am interested in luxury villas",
    "session_id": "memory_test"
  }'

# Follow-up (same session)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do you recommend based on what I just told you?",
    "session_id": "memory_test"
  }'
```

**Expected:**
- Second response references "luxury villas" without re-asking
- Context is preserved across messages

### 4. Interactive CLI Mode

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate

python -m agent.luna_deepagent

# Interactive chat:
# 👤 You: Compare Laguna Residence vs DO Dubai Islands
# 🤔 Luna is thinking...
# [Shows tool usage in real-time]
# 🌙 Luna: [Comprehensive comparison with reasoning]
```

---

## 📊 Monitoring DeepAgents Activity

### LangSmith Dashboard

If you enabled LangSmith tracing:

1. Go to https://smith.langchain.com
2. Select project "luna-deepagent"
3. See full traces of:
   - Agent reasoning steps
   - Tool calls with inputs/outputs
   - Subagent delegations
   - Token usage and latency
   - Errors and debugging info

### Server Logs

```bash
# Docker
docker-compose logs -f backend | grep -E "(🔍|📊|🧠|💾|🌐|🏢)"

# Direct
tail -f /path/to/django/logs | grep -E "Luna|tool|agent"
```

Look for:
- `✅ Luna DeepAgent initialized with 24 tools`
- Tool call logs with emoji indicators
- Subagent delegation messages
- Planning and verification steps

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'deepagents'"

**Solution:**
```bash
pip install deepagents
python -c "import deepagents; print(deepagents.__version__)"
```

### Issue: "deepagents requires Python >=3.11"

**Solution:**
```bash
python --version  # Must show 3.11.x or higher
# If not, reinstall Python 3.11 and recreate venv
```

### Issue: Agent still shows compatibility mode

**Solution:**
```bash
# Restart the backend completely
docker-compose down && docker-compose up -d
# OR
pkill -f "python manage.py runserver"
python manage.py runserver 0.0.0.0:8000
```

### Issue: Tools not working after upgrade

**Solution:**
```bash
# Check tool dependencies are installed
pip list | grep -E "(duckduckgo|PyPDF2|chromadb|tavily)"

# Reinstall if missing
pip install duckduckgo-search PyPDF2 pypdf chromadb tavily-python
```

### Issue: High latency on complex queries

**Expected behavior** - DeepAgents runs multiple reasoning steps.

**To optimize:**
- Use faster model: `LUNA_MODEL=openai:gpt-4o-mini`
- Reduce max_iterations in `luna_deepagent.py` (currently 10)
- Monitor with LangSmith to identify slow tools

---

## 📝 Configuration Options

In `/home/ec2-user/OneDevelopment-Agent/backend/agent/luna_deepagent.py`:

```python
# Line ~180: Model selection
self.model_name = os.getenv("LUNA_MODEL", "openai:gpt-4o")

# Options:
# - "openai:gpt-4o" (best quality, slower)
# - "openai:gpt-4o-mini" (faster, good quality)
# - "anthropic:claude-sonnet-4-20250514" (if you have Anthropic key)

# Line ~260: Max iterations
# Default: 10 reasoning loops max
# Increase for more complex tasks, decrease for speed
```

---

## ✅ Verification Checklist

After upgrade, confirm:

- [ ] `python --version` shows 3.11.x or higher
- [ ] `python -c "import deepagents"` works without error
- [ ] `python test_deepagent.py` shows NO compatibility mode warning
- [ ] All 5 tests pass
- [ ] `curl http://localhost:8000/api/health/` shows version 4.0.0
- [ ] Chat endpoint uses tools (`tools_used > 0`)
- [ ] Complex queries show multi-step reasoning
- [ ] LangSmith dashboard shows traces (if enabled)
- [ ] CLI mode works: `python -m agent.luna_deepagent`

---

## 🎉 You're Done!

Luna is now running with **full DeepAgents autonomy**:

✅ 24 tools active and working  
✅ 4 specialized subagents  
✅ 5 middleware layers  
✅ Long-term memory  
✅ Multi-step planning and reasoning  
✅ Human-in-the-loop hooks  
✅ LangSmith tracing  

Luna can now:
- Research complex topics autonomously
- Plan multi-step solutions
- Delegate to specialized subagents
- Remember context across sessions
- Verify information before responding
- Request human approval for sensitive operations

---

**Questions?** Check the documentation:
- `DEEPAGENTS-MIGRATION.md` - Technical migration details
- `DEEPAGENTS-ENHANCEMENTS.md` - Feature descriptions
- `LUNA-REACT-AGENT.md` - Luna's philosophy (unchanged)

**Next:** Start asking Luna complex questions and watch her autonomous reasoning in action! 🌙✨







