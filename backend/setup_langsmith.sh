#!/bin/bash
# LangSmith Setup Script for Luna

echo "🔍 LangSmith Setup for One Development Agent"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating one..."
    touch .env
fi

# Prompt for API key
read -p "Enter your LangSmith API key: " LANGCHAIN_API_KEY

if [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "❌ API key cannot be empty!"
    exit 1
fi

# Add/update LangSmith configuration
echo ""
echo "📝 Adding LangSmith configuration to .env..."

# Remove old LangSmith entries if they exist
sed -i '/^LANGCHAIN_TRACING_V2=/d' .env
sed -i '/^LANGCHAIN_API_KEY=/d' .env
sed -i '/^LANGCHAIN_PROJECT=/d' .env
sed -i '/^LANGSMITH_API_KEY=/d' .env

# Add new configuration
echo "" >> .env
echo "# LangSmith Tracing Configuration" >> .env
echo "LANGCHAIN_TRACING_V2=true" >> .env
echo "LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY" >> .env
echo "LANGCHAIN_PROJECT=luna-deepagent" >> .env

echo ""
echo "✅ LangSmith configuration added!"
echo ""
echo "Configuration:"
echo "  - Tracing: ENABLED"
echo "  - Project: luna-deepagent"
echo "  - API Key: ${LANGCHAIN_API_KEY:0:10}... (hidden)"
echo ""
echo "🔄 Please restart the backend server for changes to take effect:"
echo "   pkill -f 'manage.py runserver'"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "📊 View traces at: https://smith.langchain.com"







