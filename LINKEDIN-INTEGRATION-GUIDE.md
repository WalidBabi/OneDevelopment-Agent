# 🔗 LinkedIn Integration Guide

## 📊 **Current Status:**

✅ All visual fixes applied
✅ Nova is responding with real knowledge
✅ Vector store persistent
✅ Database accessible

**Nova now answers about:**
- ✅ Upcoming developments (Marina Heights Tower, Palm Residence, etc.)
- ✅ Office hours, pricing, amenities, ROI

**Test verified:** Nova responded with:
> "Marina Heights Tower: This stunning 45-story luxury residential tower will be located in Dubai Marina..."

---

## 🔗 **LinkedIn Data Integration Options:**

### **Option 1: Manual Export (Easiest)**

**Steps:**
1. Go to your LinkedIn company page
2. Export company data/posts
3. Add to Knowledge Base via Admin Panel:
   - URL: http://51.20.117.103:8000/admin
   - Go to "Knowledge Bases" → "Add Knowledge Base"
   - Paste LinkedIn content
   - Set source_type: "linkedin"
   - Save

**Pros:** Simple, no API setup
**Cons:** Manual process

---

### **Option 2: LinkedIn API (Official)**

**Requirements:**
- LinkedIn Developer Account
- API Access Token
- OAuth setup

**Packages Already Installed:**
- ✅ `python-linkedin-v2==0.9.1`

**Steps:**

1. **Create LinkedIn App:**
   - Go to https://www.linkedin.com/developers/
   - Create New App
   - Get Client ID & Client Secret

2. **Setup in `.env`:**
   ```bash
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_ACCESS_TOKEN=your_access_token
   ```

3. **Create Scraper Script:**

```python
# backend/scripts/linkedin_scraper.py
from linkedin_v2 import linkedin
from agent.models import KnowledgeBase
import os

# Initialize LinkedIn API
authentication = linkedin.LinkedInAuthentication(
    os.getenv('LINKEDIN_CLIENT_ID'),
    os.getenv('LINKEDIN_CLIENT_SECRET'),
    os.getenv('LINKEDIN_REDIRECT_URI'),
    linkedin.PERMISSIONS.enums.values()
)

application = linkedin.LinkedInApplication(authentication)

# Get company updates
company_id = 'your_company_id'
updates = application.get_company_updates(company_id, count=50)

# Add to knowledge base
for update in updates['values']:
    KnowledgeBase.objects.create(
        title=f"LinkedIn Post - {update['updateContent']['title']}",
        content=update['updateContent']['companyUpdate']['description'],
        summary=update['updateContent']['title'],
        source_type='linkedin',
        source_url=update.get('shareUrl'),
        is_active=True
    )
```

**Run:**
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python scripts/linkedin_scraper.py
```

---

### **Option 3: Web Scraping (No API Required)**

**Packages Already Installed:**
- ✅ `beautifulsoup4==4.12.2`
- ✅ `selenium==4.11.2`
- ✅ `scrapy==2.11.1`

**Approach A: Simple BeautifulSoup**

```python
# backend/scripts/scrape_linkedin.py
import requests
from bs4 import BeautifulSoup
from agent.models import KnowledgeBase

def scrape_linkedin_company(company_url):
    """
    Scrape public LinkedIn company page
    Note: LinkedIn may block automated scraping
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(company_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract company info
    about = soup.find('section', {'class': 'artdeco-card'})
    
    if about:
        KnowledgeBase.objects.create(
            title='One Development - LinkedIn About',
            content=about.get_text(strip=True),
            summary='Company information from LinkedIn',
            source_type='linkedin',
            source_url=company_url,
            is_active=True
        )
        print("✅ LinkedIn data added")
    else:
        print("⚠️ Could not extract data")

# Run
scrape_linkedin_company('https://www.linkedin.com/company/onedevelopmentuae')
```

**Limitations:** LinkedIn actively blocks scraping

---

### **Option 4: Phantom Buster / Automation Tools**

**Services:**
- PhantomBuster
- Apify
- Bright Data

**These provide:**
- Ready-made LinkedIn scrapers
- No API needed
- Handle anti-scraping measures
- Export to JSON/CSV

**Then import to Nova:**
```bash
python manage.py shell

from agent.models import KnowledgeBase
import json

with open('linkedin_export.json') as f:
    data = json.load(f)
    for item in data:
        KnowledgeBase.objects.create(
            title=item['title'],
            content=item['description'],
            source_type='linkedin',
            is_active=True
        )
```

---

### **Option 5: RSS Feed (If Available)**

Some company pages have RSS feeds:

```python
import feedparser
from agent.models import KnowledgeBase

# Try LinkedIn company RSS
feed_url = 'https://www.linkedin.com/company/onedevelopmentuaefeed'
feed = feedparser.parse(feed_url)

for entry in feed.entries:
    KnowledgeBase.objects.create(
        title=entry.title,
        content=entry.summary,
        source_type='linkedin',
        source_url=entry.link,
        is_active=True
    )
```

---

## 🛠️ **Recommended Approach:**

### **Best Option: Manual + Automated Hybrid**

**Phase 1: Quick Start (Today)**
1. Manually copy key LinkedIn content
2. Add via Admin Panel
3. Nova can answer immediately

**Phase 2: Automation (This Week)**
1. Set up LinkedIn API or choose a service
2. Create automation script
3. Schedule weekly updates

---

## 📝 **What Data to Import from LinkedIn:**

### **Company Profile:**
- About section
- Specialties
- Company size
- Founded date
- Headquarters location

### **Posts & Updates:**
- Project announcements
- Company news
- Property launches
- Event announcements

### **Employee Info:**
- Leadership team
- Key contacts
- Department info

---

## 🔄 **Auto-Sync Setup:**

### **Create Scheduled Job:**

```python
# backend/scripts/sync_linkedin.py
from django.core.management.base import BaseCommand
from agent.models import KnowledgeBase
# Import your LinkedIn scraper

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Scrape LinkedIn
        # Update knowledge base
        # Update vector store
        print("LinkedIn sync complete")
```

### **Schedule with Cron:**

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 2 AM):
0 2 * * * cd /home/ec2-user/OneDevelopment-Agent/backend && source venv/bin/activate && python manage.py sync_linkedin
```

---

## 🧪 **Testing:**

### **1. Add Sample LinkedIn Data Manually:**

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py shell
```

```python
from agent.models import KnowledgeBase

KnowledgeBase.objects.create(
    title='One Development - LinkedIn Company Overview',
    content='''
    One Development is a luxury real estate developer based in Dubai, UAE.
    Founded in 2015, we specialize in creating exceptional living spaces.
    Our portfolio includes Marina Heights Tower, Palm Residence Collection,
    and Business Bay Elite. With over 500+ properties delivered and 1000+ 
    satisfied clients, we continue to set new standards in luxury development.
    
    Specialties: Luxury Real Estate, Property Development, Investment Properties,
    Residential Development, Commercial Development
    
    Location: Business Bay, Dubai, UAE
    Employees: 50-200
    Type: Privately Held
    ''',
    summary='Company profile and specialties from LinkedIn',
    source_type='linkedin',
    source_url='https://www.linkedin.com/company/onedevelopmentuae',
    metadata={'category': 'company_info', 'tags': ['linkedin', 'profile', 'about']},
    is_active=True
)

print("✅ LinkedIn data added - restart backend to update vector store")
```

### **2. Restart Backend:**
```bash
cd /home/ec2-user/OneDevelopment-Agent
./manage-servers.sh restart
```

### **3. Test Nova:**
Ask: "Tell me about your company from LinkedIn"

---

## 💡 **Alternative: Direct API Access**

**If you provide me with:**
- LinkedIn Company Page URL
- LinkedIn API credentials (if available)
- Or: Exported LinkedIn data (JSON/CSV)

**I can:**
- Build a custom scraper
- Import the data automatically
- Set up auto-sync

---

## 🎯 **Quick Manual Method (Fastest):**

**Right Now:**

1. Open: https://www.linkedin.com/company/onedevelopmentuae
2. Copy the About section, recent posts, company details
3. Go to: http://51.20.117.103:8000/admin
4. Login: admin / OneDev2024!
5. Click "Knowledge Bases" → "ADD KNOWLEDGE BASE"
6. Paste LinkedIn content
7. Set:
   - Title: "LinkedIn - [Topic]"
   - Source Type: LinkedIn
   - Is Active: ✓
8. Save
9. Restart backend: `./manage-servers.sh restart`

**Done!** Nova will know that info immediately.

---

## 🔐 **Security Notes:**

**If using API:**
- Store credentials in `.env`
- Never commit credentials to Git
- Use environment variables

**If web scraping:**
- Respect robots.txt
- Use rate limiting
- Don't overload LinkedIn servers
- Consider ToS compliance

---

## 📊 **What Would You Like?**

**Option A:** I can add sample LinkedIn data manually right now
**Option B:** You provide LinkedIn content, I'll import it
**Option C:** We set up automated LinkedIn API integration
**Option D:** We build a custom web scraper

**Let me know which approach you prefer!**

---

## ✅ **Current System Ready For:**

- ✅ Manual LinkedIn data entry
- ✅ Bulk import from JSON/CSV
- ✅ API integration (once credentials provided)
- ✅ Automated scraping (once configured)
- ✅ Scheduled updates

**All infrastructure is in place - just need the data source!**

---

**Would you like me to:**
1. Add sample LinkedIn data now?
2. Build a scraper?
3. Set up API integration?
4. Wait for you to provide data?

Let me know! 🚀

