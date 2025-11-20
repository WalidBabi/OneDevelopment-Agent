# 🚀 Quick Start - Luna PDF Upload

## 🌙 What Changed?
✅ **Nova** is now **Luna**  
✅ Admin panel can upload PDFs  
✅ PDFs are auto-indexed into ChromaDB  
✅ Luna uses PDF content in responses  

---

## ⚡ 3-Minute Setup

### 1. Access Admin Panel
```
URL: http://your-domain:8000/admin/
```

If you don't have an admin account yet:
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py createsuperuser
```

### 2. Upload Your First PDF
1. Log into admin panel
2. Click **"Agent"** → **"PDF documents"** → **"Add PDF document"**
3. Fill in:
   - **Title**: "Property Catalog 2024" (example)
   - **File**: Upload your PDF
   - **Description**: Optional
4. Click **"Save"**
5. Wait for processing (shows ✓ when indexed)

### 3. Test with Luna
1. Open the chat interface (user page)
2. Notice it says **"Luna"** now (not Nova)
3. Ask Luna about content from your PDF
4. Luna will use the PDF knowledge in responses!

---

## 📋 What You Need to Know

### For Admins:
- **Admin Panel**: Upload PDFs at `http://your-domain:8000/admin/`
- **File Types**: Only text-based PDFs (not scanned images)
- **Processing**: Automatic on save (takes 2-30 seconds depending on size)
- **Status**: Check "Is indexed" column to verify

### For Users:
- **No Changes**: Users don't see any upload interface
- **Better Answers**: Luna is smarter with PDF knowledge
- **New Name**: "Luna" instead of "Nova" (with moon emoji 🌙)

---

## 🎯 Example Use Case

**Upload**: Property specifications PDF

**Luna Before**: "I don't have specific details about that property."

**Luna After**: "According to our property specifications, Dubai Marina Tower features 3-bedroom units with 2,150 sq ft, marble flooring, and panoramic sea views..."

---

## 🔧 Troubleshooting

### PDF Not Indexing?
1. Check if "Is indexed" shows ✓
2. Try clicking the PDF and clicking "Reindex"
3. Verify PDF is text-based (not a scanned image)

### Luna Doesn't Use PDF Content?
1. Confirm PDF is indexed (✓)
2. Confirm "Is active" is checked
3. Ask more specific questions related to PDF content
4. Check extracted text in admin (should not be empty)

### Can't Access Admin?
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py createsuperuser
```

---

## 📁 File Locations

```
PDFs Stored:     /home/ec2-user/OneDevelopment-Agent/backend/media/pdfs/
ChromaDB:        /home/ec2-user/OneDevelopment-Agent/backend/chroma_db/
Admin URL:       http://your-domain:8000/admin/
User Interface:  http://your-domain:3000/ (or :8000)
```

---

## 📖 Full Documentation

- **PDF-ADMIN-GUIDE.md** - Complete admin guide with API docs
- **LUNA-REBRANDING-AND-PDF-UPLOAD-SUMMARY.md** - Technical details

---

## ✅ Quick Checklist

- [ ] Admin account created
- [ ] Can access admin panel
- [ ] Uploaded test PDF
- [ ] PDF shows "Is indexed" ✓
- [ ] Tested Luna with PDF content
- [ ] Verified Luna responds with PDF info

---

**That's it!** You're ready to use Luna with PDF knowledge! 🎉

**Need Help?** Check the full guides or contact the development team.

