#!/bin/bash

# Cloud Agents Setup Verification Script
# This script checks if your Cloud Agents setup is complete

echo "🔍 Cloud Agents Setup Verification"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ALL_GOOD=true

# Check 1: Snapshot Configuration
echo "1️⃣  Checking Snapshot Configuration..."
if [ -f ".cursor/environment.json" ]; then
    SNAPSHOT=$(grep -o '"snapshot": "[^"]*"' .cursor/environment.json 2>/dev/null | cut -d'"' -f4)
    if [ ! -z "$SNAPSHOT" ] && [ "$SNAPSHOT" != "null" ]; then
        echo -e "   ${GREEN}✅ Snapshot found: $SNAPSHOT${NC}"
    else
        echo -e "   ${RED}❌ No snapshot ID found in environment.json${NC}"
        ALL_GOOD=false
    fi
else
    echo -e "   ${RED}❌ .cursor/environment.json not found${NC}"
    ALL_GOOD=false
fi
echo ""

# Check 2: Dockerfile
echo "2️⃣  Checking Dockerfile..."
if [ -f "Dockerfile" ]; then
    echo -e "   ${GREEN}✅ Dockerfile exists${NC}"
    DOCKERFILE_SIZE=$(wc -l < Dockerfile)
    echo "   📄 Dockerfile has $DOCKERFILE_SIZE lines"
else
    echo -e "   ${RED}❌ Dockerfile not found${NC}"
    ALL_GOOD=false
fi
echo ""

# Check 3: Git Repository
echo "3️⃣  Checking Git Repository..."
if [ -d ".git" ]; then
    echo -e "   ${GREEN}✅ Git repository detected${NC}"
    
    # Check remote
    REMOTE=$(git remote get-url origin 2>/dev/null)
    if [ ! -z "$REMOTE" ]; then
        echo "   🔗 Remote: $REMOTE"
        
        # Test GitHub connection
        if git ls-remote origin &>/dev/null 2>&1; then
            echo -e "   ${GREEN}✅ GitHub connection working${NC}"
        else
            echo -e "   ${YELLOW}⚠️  GitHub connection test failed (may need authentication)${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️  No remote configured${NC}"
    fi
else
    echo -e "   ${RED}❌ Not a Git repository${NC}"
    ALL_GOOD=false
fi
echo ""

# Check 4: Environment Files
echo "4️⃣  Checking Environment Configuration..."
if [ -f "backend/.env" ]; then
    echo -e "   ${GREEN}✅ backend/.env exists${NC}"
    if grep -q "OPENAI_API_KEY" backend/.env 2>/dev/null; then
        echo -e "   ${GREEN}✅ OPENAI_API_KEY configured${NC}"
    else
        echo -e "   ${YELLOW}⚠️  OPENAI_API_KEY not found in .env${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  backend/.env not found (may be optional)${NC}"
fi
echo ""

# Check 5: Docker Configuration
echo "5️⃣  Checking Docker Configuration..."
if [ -f "docker-compose.yml" ]; then
    echo -e "   ${GREEN}✅ docker-compose.yml exists${NC}"
fi
if [ -f ".dockerignore" ]; then
    echo -e "   ${GREEN}✅ .dockerignore exists${NC}"
fi
echo ""

# Check 6: Project Structure
echo "6️⃣  Checking Project Structure..."
if [ -d "backend" ]; then
    echo -e "   ${GREEN}✅ backend/ directory exists${NC}"
    if [ -f "backend/requirements.txt" ]; then
        echo -e "   ${GREEN}✅ backend/requirements.txt exists${NC}"
    fi
else
    echo -e "   ${RED}❌ backend/ directory not found${NC}"
    ALL_GOOD=false
fi

if [ -d "frontend" ]; then
    echo -e "   ${GREEN}✅ frontend/ directory exists${NC}"
    if [ -f "frontend/package.json" ]; then
        echo -e "   ${GREEN}✅ frontend/package.json exists${NC}"
    fi
else
    echo -e "   ${RED}❌ frontend/ directory not found${NC}"
    ALL_GOOD=false
fi
echo ""

# Check 7: Runtime Dependencies (if in snapshot environment)
echo "7️⃣  Checking Runtime Dependencies..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "   ${GREEN}✅ Python: $PYTHON_VERSION${NC}"
    
    # Check Django
    if python3 -c "import django" &>/dev/null 2>&1; then
        DJANGO_VERSION=$(python3 -c "import django; print(django.get_version())" 2>/dev/null)
        echo -e "   ${GREEN}✅ Django installed (v$DJANGO_VERSION)${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Django not found${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  Python3 not found in PATH${NC}"
fi

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    echo -e "   ${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "   ${YELLOW}⚠️  Node.js not found in PATH${NC}"
fi

if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version 2>&1 | head -n1)
    echo -e "   ${GREEN}✅ PostgreSQL client: $PSQL_VERSION${NC}"
else
    echo -e "   ${YELLOW}⚠️  PostgreSQL client not found${NC}"
fi
echo ""

# Summary
echo "===================================="
echo "📊 Summary"
echo "===================================="
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ Setup appears to be complete!${NC}"
    echo ""
    echo "💡 If Cursor still shows 'Resume Setup':"
    echo "   1. Try restarting Cursor"
    echo "   2. Don't click 'Resume Setup' - try creating a new agent instead"
    echo "   3. Check GitHub App installation: Settings → Integrations → Installed Apps"
else
    echo -e "${YELLOW}⚠️  Some issues detected. Review the checks above.${NC}"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Complete missing setup steps"
    echo "   2. Re-run this script to verify"
    echo "   3. See CLOUD-AGENTS-SETUP-TROUBLESHOOTING.md for detailed help"
fi
echo ""

# Show snapshot ID if available
if [ -f ".cursor/environment.json" ]; then
    SNAPSHOT=$(grep -o '"snapshot": "[^"]*"' .cursor/environment.json 2>/dev/null | cut -d'"' -f4)
    if [ ! -z "$SNAPSHOT" ] && [ "$SNAPSHOT" != "null" ]; then
        echo "📸 Your Snapshot ID: $SNAPSHOT"
        echo "   (Save this for reference)"
    fi
fi

echo ""
echo "✨ Verification complete!"


