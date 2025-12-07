# 🔍 LangSmith Setup Guide

LangSmith provides observability and monitoring for Luna's AI interactions. This guide will help you set it up.

## Quick Setup

### Option 1: Interactive Script (Recommended)

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
./setup_langsmith.sh
```

The script will:
- Prompt for your LangSmith API key
- Add configuration to `.env`
- Enable tracing automatically

### Option 2: Manual Setup

1. **Get your LangSmith API key:**
   - Go to https://smith.langchain.com
   - Sign in or create account
   - Go to Settings → API Keys
   - Copy your API key

2. **Add to `.env` file:**
   ```bash
   cd /home/ec2-user/OneDevelopment-Agent/backend
   nano .env  # or use your preferred editor
   ```

3. **Add these lines:**
   ```env
   # LangSmith Tracing Configuration
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-api-key-here
   LANGCHAIN_PROJECT=luna-deepagent
   ```

4. **Restart backend:**
   ```bash
   pkill -f "manage.py runserver"
   python manage.py runserver 0.0.0.0:8000
   ```

## What Gets Tracked

LangSmith will track:
- ✅ All LLM calls (prompts, responses)
- ✅ Tool calls (web searches, knowledge base queries)
- ✅ Token usage and costs
- ✅ Latency and performance
- ✅ Errors and exceptions
- ✅ Conversation flows

## Viewing Traces

1. Go to https://smith.langchain.com
2. Navigate to **Projects** → **luna-deepagent**
3. See all Luna's interactions in real-time!

## Configuration Details

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LANGCHAIN_TRACING_V2` | Enable/disable tracing | Yes |
| `LANGCHAIN_API_KEY` | Your LangSmith API key | Yes |
| `LANGCHAIN_PROJECT` | Project name in LangSmith | Optional |

### Current Setup

The code already includes LangSmith integration:
- **File:** `backend/agent/luna_deepagent.py`
- **Function:** `setup_langsmith()`
- **Status:** Ready to use (just needs API key)

## Verification

After setup, check backend logs for:
```
🔍 LangSmith tracing ENABLED - Project: luna-deepagent
```

If you see this, LangSmith is working! ✅

## Troubleshooting

### Tracing Not Working?

1. **Check API key:**
   ```bash
   grep LANGCHAIN_API_KEY backend/.env
   ```

2. **Check tracing enabled:**
   ```bash
   grep LANGCHAIN_TRACING_V2 backend/.env
   ```
   Should show: `LANGCHAIN_TRACING_V2=true`

3. **Check backend logs:**
   ```bash
   tail -f /tmp/luna*.log | grep LangSmith
   ```

### No Traces Appearing?

- Wait 1-2 minutes (traces are batched)
- Make a test query to Luna
- Refresh LangSmith dashboard
- Check API key is correct

## Benefits

With LangSmith enabled, you can:
- 🔍 **Debug** - See exactly what Luna is doing
- 📊 **Monitor** - Track performance and costs
- 🐛 **Fix Issues** - Identify problems quickly
- 📈 **Optimize** - Improve prompts and tool usage
- 💰 **Track Costs** - Monitor API spending

## Security Note

⚠️ **Never commit `.env` file to git!**
- It contains your API keys
- Already in `.gitignore`
- Keep it secure

---

**Ready to set up?** Run: `./backend/setup_langsmith.sh`







