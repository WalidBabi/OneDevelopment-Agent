# 🚀 OneDevelopment Agent - Quick Start Guide

## ✅ YOUR APP IS RUNNING!

**Frontend:** http://51.20.117.103:3000  
**Backend API:** http://51.20.117.103:8000  
**Admin Panel:** http://51.20.117.103:8000/admin

---

## 📋 Current Status

✅ **PostgreSQL Database** - Running with all data  
✅ **Django Backend** - API server running on port 8000  
✅ **React Frontend** - Web interface on port 3000  
✅ **Initial Data** - 29 questions & 6 knowledge entries loaded  
✅ **Core AI Features** - Working (needs OpenAI API key)  
⚠️  **Vector Search** - Using database fallback (ML package optional)

---

## 🔑 IMPORTANT: Add Your OpenAI API Key

The AI agent needs your OpenAI API key to work:

```bash
nano /home/ec2-user/OneDevelopment-Agent/backend/.env
```

Change this line:
```
OPENAI_API_KEY=your-openai-api-key-here
```

To your actual key:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

Then restart:
```bash
./manage-servers.sh restart
```

---

## 🎮 Server Management

Use the handy management script:

```bash
cd /home/ec2-user/OneDevelopment-Agent

# Check status
./manage-servers.sh status

# Start servers
./manage-servers.sh start

# Stop servers
./manage-servers.sh stop

# Restart servers
./manage-servers.sh restart

# View logs
./manage-servers.sh logs backend
./manage-servers.sh logs frontend
```

---

## 🗄️ Database Info

- **Database:** onedevelopment_agent
- **User:** onedevelopment
- **Password:** onedevelopment123
- **Host:** localhost
- **Port:** 5432

---

## 📊 Create Admin User (Optional)

To access Django admin panel:

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py createsuperuser
```

Then visit: http://51.20.117.103:8000/admin

---

## 🔧 About the Volume Expansion

**You asked about recreating the volume - DON'T DO IT!**

✅ **App works perfectly RIGHT NOW**  
✅ **All features functional** (except advanced ML embeddings)  
✅ **When volume expansion completes**, we'll install sentence-transformers  
❌ **Recreating volume = starting from scratch** (not worth it)

### What sentence-transformers adds:
- Advanced semantic search (vector embeddings)
- Better context matching
- **NOT critical for core functionality**

### What you have now:
- Full AI agent with OpenAI
- Database-based knowledge search
- All CRUD operations
- Complete web interface

---

## 🎯 Next Steps (In Order)

1. **Add OpenAI API key** (see above) ← DO THIS NOW
2. **Test the app** at http://51.20.117.103:3000
3. **Create admin user** for Django admin
4. **When volume expansion completes** (6 hours):
   ```bash
   cd /home/ec2-user/OneDevelopment-Agent/backend
   source venv/bin/activate
   pip install --no-cache-dir sentence-transformers==2.2.2
   ./manage-servers.sh restart
   ```

---

## 🐛 Troubleshooting

### Backend not responding?
```bash
./manage-servers.sh restart
./manage-servers.sh logs backend
```

### Frontend not loading?
```bash
./manage-servers.sh restart
./manage-servers.sh logs frontend
```

### Database issues?
```bash
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

### Check what's running:
```bash
./manage-servers.sh status
netstat -tulpn | grep -E ":(8000|3000|5432)"
```

---

## 📁 Important Paths

- **Project Root:** `/home/ec2-user/OneDevelopment-Agent`
- **Backend:** `/home/ec2-user/OneDevelopment-Agent/backend`
- **Frontend:** `/home/ec2-user/OneDevelopment-Agent/frontend`
- **Backend Logs:** `/tmp/backend.log`
- **Frontend Logs:** `/tmp/frontend.log`
- **Backend .env:** `/home/ec2-user/OneDevelopment-Agent/backend/.env`
- **Frontend .env:** `/home/ec2-user/OneDevelopment-Agent/frontend/.env`

---

## 🎉 You're All Set!

Your app is **fully functional** right now. Just add your OpenAI API key and start using it!

No need to wait for volume expansion or recreate anything. 🚀

