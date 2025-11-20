# 📥 Data Ingestion Guide

## Overview

This guide explains how to populate the One Development AI Agent with knowledge from various sources.

## Data Sources

### 1. Initial Knowledge Base (Pre-loaded)

The system comes with curated information about One Development:

**6 Knowledge Categories:**
1. **Company Information**: About One Development
2. **Services**: Offerings and capabilities
3. **Contact**: Location and contact details
4. **Investment**: Investment opportunities
5. **Amenities**: Property features
6. **Why Choose**: Unique selling points

**Loading Initial Data:**
```bash
cd backend
source venv/bin/activate
python manage.py init_data
```

This command creates:
- 30+ suggested questions
- 6 knowledge base entries
- Vector embeddings for semantic search

### 2. Website Scraping

Automatically scrape content from https://www.oneuae.com/

**Method 1: Using Django Shell**

```python
cd backend
source venv/bin/activate
python manage.py shell

from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.langgraph_agent import OneDevelopmentAgent
from agent.models import KnowledgeBase

# Initialize
ingestor = OneDevelopmentDataIngestor()
agent = OneDevelopmentAgent()

# Scrape website (adjust max_pages as needed)
print("Starting website scrape...")
data = ingestor.scrape_website(max_pages=50)

print(f"Scraped {len(data)} pages")

# Store in database and vector store
count = 0
for item in data:
    # Save to PostgreSQL
    kb = KnowledgeBase.objects.create(
        source_type=item.get('source_type', 'website'),
        source_url=item.get('url'),
        title=item.get('title', 'Untitled'),
        content=item.get('content', ''),
        summary=item.get('content', '')[:500],
        metadata=item
    )
    
    # Add to ChromaDB vector store
    agent.add_knowledge(
        content=item.get('content', ''),
        metadata={
            'source': item.get('source_type'),
            'title': item.get('title'),
            'url': item.get('url')
        }
    )
    count += 1
    print(f"Processed {count}/{len(data)}")

print(f"Successfully ingested {count} items!")
```

**Method 2: Using API Endpoint**

```bash
curl -X POST http://localhost:8000/api/ingest-data/ \
  -H "Content-Type: application/json" \
  -d '{"source": "website"}'
```

**Method 3: Custom Python Script**

```python
#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append('/path/to/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.langgraph_agent import OneDevelopmentAgent
from agent.models import KnowledgeBase

def ingest_website_data():
    ingestor = OneDevelopmentDataIngestor()
    agent = OneDevelopmentAgent()
    
    # Scrape
    data = ingestor.scrape_website(max_pages=100)
    
    # Store
    for item in data:
        KnowledgeBase.objects.create(
            source_type='website',
            source_url=item.get('url'),
            title=item.get('title', 'Untitled'),
            content=item.get('content', ''),
            summary=item.get('content', '')[:500],
            metadata=item
        )
        
        agent.add_knowledge(
            item.get('content', ''),
            metadata={'source': 'website', 'url': item.get('url')}
        )
    
    print(f"Ingested {len(data)} pages")

if __name__ == '__main__':
    ingest_website_data()
```

### 3. LinkedIn Integration (Future)

Currently a placeholder. To integrate:

**Step 1: Get LinkedIn API Credentials**
- Register app at https://www.linkedin.com/developers/
- Get Client ID and Secret
- Add to `.env` file

**Step 2: Implement Integration**

```python
from linkedin_api import Linkedin

def scrape_linkedin_company():
    # Authenticate
    api = Linkedin(
        username='your_email',
        password='your_password'
    )
    
    # Get company info
    company = api.get_company('one-development')
    
    # Extract data
    data = {
        'title': company.get('name'),
        'content': f"""
        {company.get('description', '')}
        
        Industry: {company.get('industry', 'N/A')}
        Size: {company.get('companySize', 'N/A')}
        Founded: {company.get('foundedOn', 'N/A')}
        """,
        'source_type': 'linkedin',
        'source_url': company.get('url')
    }
    
    return data
```

### 4. Manual Data Entry

**Method 1: Django Admin**

1. Access admin: http://localhost:8000/admin
2. Navigate to "Knowledge Base"
3. Click "Add Knowledge Base"
4. Fill in:
   - Source Type: manual
   - Title: Your title
   - Content: Your content
   - Summary: Brief summary
   - Category: Select category

**Method 2: API Endpoint**

```bash
curl -X POST http://localhost:8000/api/knowledge/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "manual",
    "title": "New Property Launch",
    "content": "One Development is launching a new luxury villa project...",
    "summary": "New luxury villa project announcement",
    "is_active": true
  }'
```

**Method 3: Django Shell**

```python
python manage.py shell

from agent.models import KnowledgeBase
from agent.langgraph_agent import OneDevelopmentAgent

# Create knowledge entry
kb = KnowledgeBase.objects.create(
    source_type='manual',
    title='New Property Information',
    content='Detailed content about the property...',
    summary='Brief summary',
    metadata={'category': 'projects'}
)

# Add to vector store
agent = OneDevelopmentAgent()
agent.add_knowledge(
    content=kb.content,
    metadata={'source': 'manual', 'title': kb.title}
)
```

### 5. Document Upload (Future Enhancement)

**Planned Support:**
- PDF documents
- Word documents
- Excel spreadsheets
- Images (with OCR)

**Implementation Plan:**

```python
from PyPDF2 import PdfReader
from docx import Document

def ingest_pdf(file_path):
    reader = PdfReader(file_path)
    content = ""
    
    for page in reader.pages:
        content += page.extract_text()
    
    # Store in knowledge base
    KnowledgeBase.objects.create(
        source_type='document',
        title=os.path.basename(file_path),
        content=content,
        summary=content[:500]
    )

def ingest_docx(file_path):
    doc = Document(file_path)
    content = "\n".join([para.text for para in doc.paragraphs])
    
    KnowledgeBase.objects.create(
        source_type='document',
        title=os.path.basename(file_path),
        content=content,
        summary=content[:500]
    )
```

## Best Practices

### 1. Content Quality

**Do:**
- Use clear, concise language
- Include relevant keywords
- Structure content logically
- Update regularly

**Don't:**
- Add duplicate content
- Use unclear abbreviations
- Include outdated information
- Overload with technical jargon

### 2. Categorization

Tag content with appropriate categories:
- `company_info`
- `projects`
- `services`
- `investment`
- `pricing`
- `amenities`
- `location`
- `contact`

### 3. Update Frequency

**Recommended Schedule:**
- **Daily**: Check for new blog posts/news
- **Weekly**: Review and update property listings
- **Monthly**: Full website scrape
- **Quarterly**: Audit all knowledge base entries

### 4. Data Validation

Before ingesting, validate:
- Content is not empty
- URLs are accessible
- Text is properly formatted
- No sensitive information included

## Monitoring Ingestion

### Check Ingestion Status

```python
from agent.models import KnowledgeBase

# Count by source
sources = KnowledgeBase.objects.values('source_type').annotate(count=Count('id'))
print(sources)

# Recent additions
recent = KnowledgeBase.objects.order_by('-created_at')[:10]
for item in recent:
    print(f"{item.title} - {item.created_at}")

# Active entries
active_count = KnowledgeBase.objects.filter(is_active=True).count()
print(f"Active entries: {active_count}")
```

### Vector Store Statistics

```python
from agent.langgraph_agent import OneDevelopmentAgent

agent = OneDevelopmentAgent()

# Get collection info
collection = agent.collection
print(f"Total documents: {collection.count()}")
```

## Troubleshooting

### Issue: Website Scraping Fails

**Solutions:**
- Check internet connectivity
- Verify website is accessible
- Increase timeout settings
- Check for robots.txt restrictions

```python
# Increase timeout
ingestor = OneDevelopmentDataIngestor()
ingestor.headers['timeout'] = 30  # seconds
```

### Issue: Duplicate Content

**Solutions:**
- Check for existing entries before adding
- Use unique identifiers
- Implement deduplication

```python
# Check before adding
existing = KnowledgeBase.objects.filter(
    source_url=url
).exists()

if not existing:
    # Add new entry
    pass
```

### Issue: Poor Search Results

**Solutions:**
- Improve content quality
- Add more context
- Update embeddings
- Increase chunk size

```python
# Regenerate embeddings
from agent.langgraph_agent import OneDevelopmentAgent

agent = OneDevelopmentAgent()

for kb in KnowledgeBase.objects.all():
    agent.add_knowledge(
        content=kb.content,
        metadata={'id': str(kb.id)}
    )
```

## Automated Ingestion

### Setup Cron Job

```bash
# Edit crontab
crontab -e

# Add daily scrape at 2 AM
0 2 * * * cd /path/to/backend && /path/to/venv/bin/python manage.py shell < /path/to/scrape_script.py

# Add weekly full scrape on Sunday at 3 AM
0 3 * * 0 cd /path/to/backend && /path/to/venv/bin/python manage.py shell < /path/to/full_scrape_script.py
```

### Celery Task (Advanced)

```python
# In agent/tasks.py
from celery import shared_task

@shared_task
def scrape_website_task():
    from agent.data_ingestor import OneDevelopmentDataIngestor
    from agent.langgraph_agent import OneDevelopmentAgent
    from agent.models import KnowledgeBase
    
    ingestor = OneDevelopmentDataIngestor()
    agent = OneDevelopmentAgent()
    
    data = ingestor.scrape_website(max_pages=50)
    
    for item in data:
        KnowledgeBase.objects.create(
            source_type='website',
            source_url=item.get('url'),
            title=item.get('title'),
            content=item.get('content'),
            summary=item.get('content', '')[:500]
        )
        
        agent.add_knowledge(item.get('content', ''))
    
    return f"Ingested {len(data)} pages"

# Schedule in settings.py
CELERY_BEAT_SCHEDULE = {
    'scrape-website-daily': {
        'task': 'agent.tasks.scrape_website_task',
        'schedule': crontab(hour=2, minute=0),
    },
}
```

## Data Export

### Export Knowledge Base

```python
import json

# Export to JSON
knowledge = KnowledgeBase.objects.all().values()
with open('knowledge_export.json', 'w') as f:
    json.dump(list(knowledge), f, indent=2, default=str)

# Export to CSV
import csv

knowledge = KnowledgeBase.objects.all()
with open('knowledge_export.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Title', 'Source Type', 'Content', 'Created'])
    
    for kb in knowledge:
        writer.writerow([kb.title, kb.source_type, kb.content, kb.created_at])
```

## Summary

**Quick Start:**
1. Run `python manage.py init_data` for initial knowledge
2. Use API or shell to scrape website
3. Add manual entries through admin
4. Set up automated scraping with cron/Celery

**Best Results:**
- High-quality, relevant content
- Regular updates
- Proper categorization
- Monitoring and validation

---

**Your knowledge base is the foundation of your AI agent's intelligence!**

