# 📄 Luna PDF Upload Admin Guide

## Overview
This guide explains how to upload and manage PDF documents for Luna (formerly Nova) using the Django admin panel. PDFs are automatically indexed into ChromaDB for the AI agent to use.

---

## 🌙 Luna Rebranding Complete!
✅ **Name Changed**: Nova → Luna  
✅ **Avatar Updated**: Luna.png (🌙 moon theme)  
✅ **All references updated** in code and frontend

---

## 📤 Uploading PDFs via Django Admin

### Step 1: Access Django Admin Panel
1. Navigate to: `http://your-domain:8000/admin/`
2. Log in with your admin credentials
3. Look for **"PDF Documents"** section under **AGENT**

### Step 2: Upload a New PDF
1. Click **"+ Add"** next to "PDF documents"
2. Fill in the form:
   - **Title**: Give your PDF a descriptive name
   - **Description**: Optional - brief description of the content
   - **File**: Click "Choose File" and select your PDF
   - **Is active**: Keep checked (uncheck to temporarily disable)
3. Click **"Save"**

### Step 3: Automatic Processing
When you save, the system automatically:
- ✅ Extracts all text from the PDF
- ✅ Counts pages and file size
- ✅ Splits content into chunks for better semantic search
- ✅ Indexes all chunks into ChromaDB
- ✅ Makes content available to Luna immediately

---

## 🔍 What Happens Behind the Scenes

### Text Extraction
- Uses PyPDF2 to extract text from all pages
- Preserves paragraph structure and formatting
- Stores extracted text in the database

### Intelligent Chunking
- Splits text into ~1000 character chunks
- 200 character overlap between chunks for context continuity
- Breaks at sentence boundaries when possible

### ChromaDB Indexing
Each chunk is indexed with metadata:
```json
{
  "source": "pdf_document",
  "document_id": "uuid",
  "title": "Your PDF Title",
  "chunk_index": 0,
  "total_chunks": 15,
  "page_count": 5
}
```

### Vector Embeddings
- Uses sentence-transformers (all-MiniLM-L6-v2)
- Enables semantic search (meaning-based, not keyword matching)
- Luna can find relevant information even with different wording

---

## 🎯 Using the Admin Interface

### Viewing PDF Documents
1. Go to **Admin → Agent → PDF documents**
2. You'll see a list with:
   - Title
   - Page count
   - Indexing status (✓ if indexed)
   - Active status
   - Upload date

### Managing Documents

#### Reindex a Single PDF
1. Click on the PDF document
2. Scroll down and click **"Reindex"** button
3. Useful if the original indexing failed

#### Deactivate a PDF
1. Click on the PDF document
2. Uncheck **"Is active"**
3. Click **"Save"**
4. PDF content will no longer be used by Luna

#### Delete a PDF
1. Click on the PDF document
2. Click **"Delete"** at bottom left
3. Confirm deletion
4. Note: Vector embeddings in ChromaDB will remain until collection is reset

---

## 🔧 API Endpoints (for Developers)

### List All PDFs
```bash
GET /api/pdf-documents/
```

### Upload PDF via API
```bash
POST /api/pdf-documents/
Content-Type: multipart/form-data

{
  "title": "Document Title",
  "description": "Optional description",
  "file": <PDF file>
}
```

### Reindex Single PDF
```bash
POST /api/pdf-documents/{id}/reindex/
```

### Reindex All PDFs
```bash
POST /api/pdf-documents/reindex_all/
```

---

## 📊 Best Practices

### PDF Format
- ✅ Text-based PDFs (extractable text)
- ✅ Well-formatted documents with clear structure
- ❌ Scanned images (OCR not currently supported)
- ❌ Password-protected PDFs

### File Size
- Recommended: Under 50MB per file
- Large files are supported but take longer to process
- Consider splitting very large documents

### Content Organization
- Use descriptive titles
- Group related documents
- Add descriptions to help admins understand content
- Keep documents up-to-date

### Naming Conventions
```
✅ Good: "One Development - Property Portfolio 2024.pdf"
✅ Good: "Dubai Marina Tower - Technical Specifications.pdf"
❌ Bad: "document1.pdf"
❌ Bad: "temp.pdf"
```

---

## 🚨 Troubleshooting

### PDF Not Indexing
**Symptom**: "Is indexed" shows ❌

**Solutions**:
1. Check if PDF is text-based (not scanned image)
2. Try manually reindexing
3. Check error logs in Django admin messages
4. Verify ChromaDB is running

### Luna Can't Find PDF Content
**Symptom**: Luna doesn't seem to know information from uploaded PDFs

**Solutions**:
1. Verify PDF shows "Is indexed" ✓
2. Check "Is active" is ✓
3. Try asking Luna specifically about the document topic
4. Reindex the PDF
5. Check extracted text in admin (should not be empty)

### Upload Fails
**Symptom**: Error when uploading PDF

**Solutions**:
1. Check file size (very large files may timeout)
2. Verify PDF is not corrupted
3. Ensure media directory exists and is writable
4. Check disk space

---

## 🔐 Security Considerations

### Admin Access
- Only trusted users should have admin access
- Use strong passwords
- Consider IP whitelisting for admin panel
- Enable 2FA if available

### PDF Content
- Review PDFs before uploading (they become searchable)
- Don't upload confidential information
- PDFs are stored on server (not encrypted)
- Consider data privacy regulations

### File Validation
- System validates file type (must be .pdf)
- File size limits prevent DoS attacks
- Malicious PDFs could contain harmful content

---

## 📈 Monitoring & Maintenance

### Regular Checks
- [ ] Review uploaded PDFs monthly
- [ ] Remove outdated documents
- [ ] Verify indexing status
- [ ] Monitor disk space usage

### ChromaDB Management
- Collection name: `onedevelopment_knowledge`
- Location: `backend/chroma_db/`
- Persistent storage (survives restarts)
- Can be backed up by copying directory

### Database Cleanup
```python
# Remove inactive PDFs older than 6 months
PDFDocument.objects.filter(
    is_active=False,
    updated_at__lt=timezone.now() - timedelta(days=180)
).delete()
```

---

## 🎓 Example Use Cases

### Real Estate Documentation
Upload property documents, and Luna can answer:
- "What are the specifications of Dubai Marina Tower?"
- "Tell me about payment plans for Al Barsha project"
- "What amenities are included in The Address Residences?"

### Company Policies
Upload HR documents, and Luna can answer:
- "What is the vacation policy?"
- "How do I submit an expense report?"
- "What are the working hours?"

### Technical Manuals
Upload maintenance guides, and Luna can answer:
- "How do I troubleshoot the HVAC system?"
- "What's the recommended maintenance schedule?"
- "Where are the emergency shutoff valves?"

---

## 📞 Support

### Getting Help
- Check Django admin error messages
- Review server logs: `backend/logs/`
- Test PDF extraction manually
- Contact development team

### Useful Commands
```bash
# Activate virtual environment
cd backend && source venv/bin/activate

# Run migrations
python manage.py migrate

# Create admin user (if needed)
python manage.py createsuperuser

# Check ChromaDB status
python manage.py shell
>>> from agent.langgraph_agent import OneDevelopmentAgent
>>> agent = OneDevelopmentAgent()
>>> print(agent.collection.count())
```

---

## ✨ Features

✅ Automatic text extraction  
✅ Intelligent chunking  
✅ Semantic search indexing  
✅ Real-time availability to Luna  
✅ Admin panel management  
✅ Reindexing capability  
✅ Metadata tracking  
✅ File management  

---

**Last Updated**: November 20, 2025  
**Version**: 1.0  
**Status**: Production Ready 🚀

