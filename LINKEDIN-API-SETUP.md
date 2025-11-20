# LinkedIn API Integration Setup Guide

## Overview
This guide explains how to integrate LinkedIn API to automatically fetch company information, job postings, and updates from your LinkedIn company page.

---

## ⚠️ Important: LinkedIn API Costs

### Is LinkedIn API Free?

**Short Answer: Partially Free, with Limitations**

### LinkedIn API Access Tiers:

#### 1. **LinkedIn Developer Program (Free Tier)**
- ✅ **Free** for basic access
- ✅ Includes: Basic profile API, Share on LinkedIn
- ❌ **DOES NOT** include: Company data access, Job postings API
- ❌ Very limited for business use

#### 2. **LinkedIn Marketing Developer Platform (Paid)**
- 💰 **Requires LinkedIn Marketing Solutions subscription**
- Pricing: **Starts at ~$5,000/month** for Enterprise
- Includes: Company pages API, Analytics, Ads API
- Required for: Automated company data fetching

#### 3. **LinkedIn Talent Solutions API (Paid)**
- 💰 **Very expensive** - Enterprise pricing
- Includes: Job posting API, Applicant tracking
- Typically **$10,000+/year**

#### 4. **Partner Program (Custom Pricing)**
- Must apply and be approved
- Custom pricing based on usage
- Full API access

### Recommended Alternative: **Web Scraping** (What we're using now)

Since LinkedIn API for company data is expensive, we use:
- ✅ **Web scraping** - Already implemented
- ✅ **Free** - No API costs
- ✅ **Effective** - Gets public company information
- ⚠️ **Rate limited** - Must be respectful
- ⚠️ **May break** - If LinkedIn changes their HTML

---

## Current Implementation

Our current implementation (`backend/agent/data_ingestor.py`) uses **web scraping**:

```python
def scrape_linkedin_company(self):
    """Scrape public LinkedIn company page"""
    linkedin_url = "https://www.linkedin.com/company/onedevelopmentuae"
    # ... scraping logic ...
```

### What It Does:
1. ✅ Fetches public company information
2. ✅ Gets company description
3. ✅ Retrieves employee count
4. ✅ Collects industry information
5. ✅ No API costs

### Limitations:
- ⚠️ Doesn't get private data
- ⚠️ Requires LinkedIn to allow scraping
- ⚠️ Rate limited to prevent blocking

---

## If You Want Official LinkedIn API Access

### Step 1: Create LinkedIn App

1. **Go to**: https://www.linkedin.com/developers/apps
2. **Click**: "Create app"
3. **Fill in**:
   - App name: "One Development AI Agent"
   - LinkedIn Page: Select your company page
   - App logo: Upload company logo
   - Privacy policy URL: Your website
   - Terms of use URL: Your website

4. **Verify**: Verify app with your company page

### Step 2: Request API Access

1. **Products Tab**: Request access to:
   - "Share on LinkedIn" (Free - Basic)
   - "Marketing Developer Platform" (Paid - Required for company data)
   
2. **Wait for Approval**: Can take 2-4 weeks

3. **Get Credentials**:
   - Client ID
   - Client Secret

### Step 3: Add Credentials to .env

```bash
# LinkedIn API Credentials
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_COMPANY_ID=your_company_id
```

### Step 4: Update Code

We've prepared the code structure. To activate LinkedIn API:

```python
# In backend/agent/linkedin_api.py (create this file)

import requests
import os

class LinkedInAPI:
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.company_id = os.getenv('LINKEDIN_COMPANY_ID')
        self.access_token = None
    
    def get_access_token(self):
        """Get OAuth 2.0 access token"""
        # OAuth implementation
        pass
    
    def get_company_info(self):
        """Fetch company information"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            f'https://api.linkedin.com/v2/organizations/{self.company_id}',
            headers=headers
        )
        return response.json()
    
    def get_company_updates(self):
        """Fetch company posts/updates"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            f'https://api.linkedin.com/v2/shares?q=owners&owners=urn:li:organization:{self.company_id}',
            headers=headers
        )
        return response.json()
```

---

## Cost Comparison

| Method | Setup Cost | Monthly Cost | Data Access | Reliability |
|--------|-----------|--------------|-------------|-------------|
| **Web Scraping (Current)** | $0 | $0 | Public only | Medium |
| **LinkedIn Free API** | $0 | $0 | Very limited | High |
| **LinkedIn Marketing API** | $5,000+ | $5,000+ | Full access | Very High |
| **Partner Program** | Varies | $10,000+ | Full access | Very High |

---

## Recommendations

### For Most Businesses (Recommended):
1. ✅ **Use web scraping** (current implementation)
2. ✅ **Manual data entry** for important updates
3. ✅ **Scrape your own website** (already implemented)
4. ✅ **Cost**: $0/month

### For Large Enterprises:
1. Apply for LinkedIn Marketing Developer Platform
2. Budget: $5,000-10,000/month
3. Get full API access
4. Automate everything

### Hybrid Approach (Best Value):
1. ✅ Use web scraping for public data
2. ✅ Manual entry for critical updates
3. ✅ Apply for free LinkedIn API for basic sharing
4. ✅ Upgrade to paid only if you need real-time job posting integration

---

## Current Data Sources (Already Working)

Your agent currently uses these sources:

1. **✅ Manual Knowledge Base** (6 entries)
   - Company info
   - Services
   - Contact details
   - Features
   - Cost: $0

2. **✅ Website Scraping** (https://www.oneuae.com)
   - Real-time data
   - Automatically updated
   - Cost: $0

3. **✅ LinkedIn Scraping** (Public page)
   - Company overview
   - Employee count
   - Industry info
   - Cost: $0

4. **🆕 Real-time Web Search** (Just added!)
   - Fact-checking
   - Website verification
   - Cost: $0

---

## How to Improve Data Quality (Without LinkedIn API)

### 1. Scrape Your Website More Frequently

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py shell

from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.langgraph_agent import OneDevelopmentAgent

ingestor = OneDevelopmentDataIngestor()
data = ingestor.scrape_website(max_pages=50)
# This updates your knowledge base with latest website content
```

### 2. Add Manual High-Quality Content

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py shell

from agent.models import KnowledgeBase

# Add important content
KnowledgeBase.objects.create(
    source_type='manual',
    title='Latest Project - Marina Heights',
    content='Detailed description of your latest project...',
    summary='New luxury development in Dubai Marina',
    is_active=True
)
```

### 3. Setup Automatic Daily Updates

Create a cron job:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /home/ec2-user/OneDevelopment-Agent/backend && source venv/bin/activate && python manage.py scrape_website
```

---

## Summary

### ❓ "Is LinkedIn API Free?"
**Answer**: Basic features are free, but company data access requires expensive enterprise subscriptions ($5,000-10,000+/month).

### ✅ What We're Using (FREE):
- Web scraping (your website + LinkedIn public page)
- Manual knowledge base
- Real-time web access for fact-checking
- Persistent memory for user context

### 💡 Recommendation:
**Stick with the current implementation** (web scraping) unless you have a large budget and need real-time job posting integration or private company analytics.

---

## Questions?

**Q: Can we get job postings without the API?**
A: Yes, by scraping your careers page or manually adding them to the knowledge base.

**Q: Will LinkedIn block our scraping?**
A: Unlikely if done respectfully (rate-limited, not excessive). We only scrape public information.

**Q: How often should we update the data?**
A: Daily or weekly scraping is usually sufficient. Real-time updates require paid API.

**Q: What about other social media APIs?**
A: Most are similar - basic access is free, business features are paid. Twitter, Facebook, Instagram all have tiered pricing.

---

For more information:
- LinkedIn Developer Documentation: https://docs.microsoft.com/en-us/linkedin/
- LinkedIn Marketing Solutions: https://business.linkedin.com/marketing-solutions
- LinkedIn Partner Program: https://partner.linkedin.com/

