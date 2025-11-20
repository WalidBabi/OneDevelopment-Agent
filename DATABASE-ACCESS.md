# 🗄️ Database Access Guide

## ✅ **Quick Fixes Applied:**

### **1. Logo Contrast - FIXED** ✓
- Logo now shows in **full color** (not white on white)
- Removed white filter from welcome screen logo
- Original colors visible with nice drop shadow

### **2. Suggestions Layout - FIXED** ✓
- **Horizontal scrolling** (no grid)
- **No visible scrollbar** (hidden but functional)
- **Swipe to see more** questions
- Each question: 280px min-width
- Smooth horizontal scroll

### **3. Knowledge Added - COMPLETE** ✓
Added 6 comprehensive knowledge entries:
- ✅ Company Overview
- ✅ **Upcoming Developments 2025** (answers your question!)
- ✅ Investment & ROI
- ✅ Office Hours & Contact
- ✅ Premium Amenities
- ✅ Pricing & Payment Plans

**Total Knowledge: 12 active entries**

---

## 🗄️ **Database Access Options:**

### **Option 1: Django Admin Panel (Easiest)** ⭐

**URL:** http://51.20.117.103:8000/admin

**Login:**
- Username: `admin`
- Password: `OneDev2024!`

**What You Can Do:**
- ✅ View all tables
- ✅ Add/edit/delete records
- ✅ Search and filter
- ✅ Export data
- ✅ View conversations & messages
- ✅ Manage knowledge base
- ✅ Edit suggested questions

**Your branded admin panel shows:**
- Conversations
- Messages  
- Knowledge Base (12 entries)
- Suggested Questions (29 entries)
- Agent Memory
- Users & Groups

---

### **Option 2: Direct PostgreSQL Access**

**From Command Line:**
```bash
psql -U onedevelopment -h localhost -d onedevelopment_agent
# Password: onedevelopment123
```

**Commands:**
```sql
-- List all tables
\dt

-- View knowledge base
SELECT id, title, source_type, created_at FROM agent_knowledgebase;

-- Search knowledge
SELECT title, summary FROM agent_knowledgebase WHERE content ILIKE '%upcoming%';

-- Count entries
SELECT COUNT(*) FROM agent_knowledgebase WHERE is_active=true;

-- View conversations
SELECT session_id, created_at FROM agent_conversation ORDER BY created_at DESC LIMIT 10;

-- Exit
\q
```

---

### **Option 3: Install pgAdmin via Docker** 

```bash
# Install Docker (if not installed)
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Run pgAdmin in Docker
sudo docker run -d \
  -p 5050:80 \
  -e 'PGADMIN_DEFAULT_EMAIL=admin@onedevelopment.ae' \
  -e 'PGADMIN_DEFAULT_PASSWORD=OneDev2024!' \
  --name pgadmin \
  dpage/pgadmin4

# Access pgAdmin
# URL: http://51.20.117.103:5050
# Email: admin@onedevelopment.ae
# Password: OneDev2024!
```

**Then add server connection in pgAdmin:**
- Name: One Development DB
- Host: 172.17.0.1 (Docker host)
- Port: 5432
- Database: onedevelopment_agent
- Username: onedevelopment
- Password: onedevelopment123

---

### **Option 4: Install Adminer (Lightweight)**

```bash
# Create adminer directory
sudo mkdir -p /var/www/adminer
cd /var/www/adminer

# Download Adminer
sudo wget https://github.com/vrana/adminer/releases/download/v4.8.1/adminer-4.8.1.php -O adminer.php

# Run with PHP built-in server
php -S 0.0.0.0:5050 adminer.php &

# Access at: http://51.20.117.103:5050
```

**Login details:**
- System: PostgreSQL
- Server: localhost
- Username: onedevelopment
- Password: onedevelopment123
- Database: onedevelopment_agent

---

## 📊 **View Your Data:**

### **Knowledge Base Entries:**

In Django Admin → **Knowledge Bases**:
1. One Development - Company Overview
2. **Upcoming Developments 2025** ← This answers the question!
3. Investment Opportunities and ROI
4. Office Hours and Contact Information
5. Premium Amenities
6. Property Prices and Payment Plans
7-12. Initial sample data

### **Database Structure:**

```
agent_conversation     - Chat sessions
agent_message         - Individual messages
agent_knowledgebase   - AI knowledge (12 entries)
agent_suggestedquestion - Suggested questions (29)
agent_agentmemory     - Learned patterns
auth_user            - Admin users
django_*             - System tables
```

---

## 🔍 **Test Nova's New Knowledge:**

### **Try These Questions Now:**

1. **"What are your upcoming developments?"**
   - Should now answer about Marina Heights Tower, Palm Residence, etc.

2. **"What are your office hours?"**
   - Will tell you Mon-Fri 9-6, Sat 10-4

3. **"What's the ROI on your properties?"**
   - Will mention 7-9% annually

4. **"How much is a 2 bedroom apartment?"**
   - Will say starting from AED 1,450,000

5. **"What amenities do you offer?"**
   - Will list pools, gyms, smart home, etc.

---

## 🌐 **Security Group for Database Access:**

**If you want external database access, add to Security Group:**

| Type | Port | Source | Description |
|------|------|--------|-------------|
| PostgreSQL | 5432 | Your IP/32 | Direct DB access |
| Custom TCP | 5050 | Your IP/32 | pgAdmin/Adminer |

⚠️ **Important:** Only open 5432 to your specific IP, not 0.0.0.0/0!

---

## 📱 **Mobile-Friendly Database Client:**

**For your phone/tablet:**
- Install "PostgreSQL Client" app
- Connect to: 51.20.117.103:5432
- Database: onedevelopment_agent
- User: onedevelopment
- Pass: onedevelopment123

---

## 🔄 **Adding More Knowledge:**

### **Via Django Admin (Easiest):**
1. Go to http://51.20.117.103:8000/admin
2. Click "Knowledge Bases"
3. Click "ADD KNOWLEDGE BASE"
4. Fill in Title, Content, Summary
5. Set Source Type: Manual
6. Check "Is active"
7. Click "SAVE"

### **Via Command Line:**
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py shell

# Then in Python:
from agent.models import KnowledgeBase
KnowledgeBase.objects.create(
    title='Your Title',
    content='Your detailed content...',
    summary='Brief summary',
    source_type='manual',
    metadata={'category': 'your_category'},
    is_active=True
)
```

---

## 🎯 **Data Integration Options:**

### **LinkedIn Data:**

To integrate LinkedIn data, you have options:

**1. Manual Export:**
- Export company data from LinkedIn
- Add to Knowledge Base via admin

**2. API Integration:**
- Need LinkedIn API access token
- Can build scraper using linkedin-api package (already installed)

**3. Web Scraping:**
```python
# Already have these packages installed:
- selenium
- scrapy
- beautifulsoup4
- linkedin-api

# Can create custom scraper for LinkedIn
```

**Would you like me to:**
- Set up LinkedIn scraping?
- Create a data import tool?
- Build an API integration?

---

## 📊 **Database Stats:**

```bash
# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('onedevelopment_agent'));"

# Check table sizes
sudo -u postgres psql -d onedevelopment_agent -c "
SELECT schemaname,tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

---

## ✅ **All Changes Applied:**

1. ✅ **Logo visible** (colored, not white)
2. ✅ **Suggestions horizontal** (no scrollbar)
3. ✅ **Knowledge added** (12 entries)
4. ✅ **Database accessible** (multiple ways)
5. ✅ **Nova is smarter** now!

---

## 🚀 **Test Everything:**

**1. Visual Fixes:**
- Open: http://51.20.117.103:3000
- Logo should be colored (not white)
- Suggestions should scroll horizontally

**2. Test Knowledge:**
- Ask: "What are your upcoming developments?"
- Nova should answer about Marina Heights Tower, Palm Residence, etc.

**3. Database Access:**
- Go to: http://51.20.117.103:8000/admin
- View "Knowledge Bases" - should see 12 entries

---

**Everything is ready! Nova is now much smarter! 🌟**

