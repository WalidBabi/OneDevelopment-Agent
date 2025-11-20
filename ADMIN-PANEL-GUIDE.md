# 🏢 One Development Database Admin Panel

## ✨ Your Custom Branded PostgreSQL Admin Panel is Ready!

---

## 🌐 **Access Your Admin Panel**

### **URL:** http://51.20.117.103:8000/admin

### **Login Credentials:**
```
Username: admin
Password: OneDev2024!
```

> 🔒 **Important:** Change this password after first login!

---

## 🎨 **What's Customized?**

✅ **Your One Development Logo** - Displayed in the header  
✅ **Brand Colors** - Purple gradient theme (#341a60 to #966bfc)  
✅ **Custom Styling** - Beautiful, modern interface  
✅ **Branded Header** - Professional look matching your identity  
✅ **Database Info** - Clear display of PostgreSQL connection details  

---

## 📊 **What Can You Manage?**

In the admin panel, you can view and edit:

### **Agent Models:**
- 💬 **Conversations** - All chat sessions
- 📝 **Messages** - Individual chat messages
- 📚 **Knowledge Base** - Your AI's knowledge entries
- ❓ **Suggested Questions** - Pre-configured questions
- 🧠 **Agent Memory** - Stored context and memory

### **User Management:**
- 👥 **Users** - Admin users
- 🔐 **Groups** - User groups and permissions

### **PostgreSQL Database:**
- **Database:** onedevelopment_agent
- **Server:** localhost:5432
- **User:** onedevelopment
- **Total Tables:** 10+ Django models

---

## 🔧 **Change Your Admin Password**

After logging in:

1. Click **"CHANGE PASSWORD"** in the top right
2. Enter current password: `OneDev2024!`
3. Enter your new secure password (twice)
4. Click **"CHANGE MY PASSWORD"**

---

## 📈 **Common Admin Tasks**

### **View All Conversations:**
1. Login to admin panel
2. Click **"Conversations"** under **AGENT**
3. See all chat sessions with timestamps

### **Add Knowledge Base Entries:**
1. Go to **"Knowledge Bases"**
2. Click **"ADD KNOWLEDGE BASE"** (top right)
3. Fill in:
   - Title
   - Content
   - Source type
   - Summary (optional)
4. Check **"Is active"**
5. Click **"SAVE"**

### **Manage Suggested Questions:**
1. Go to **"Suggested Questions"**
2. Edit existing or **"ADD SUGGESTED QUESTION"**
3. Set category and priority
4. Users will see these on the frontend

### **View Database Tables Directly:**
All your PostgreSQL tables are accessible through Django's ORM interface. You can:
- Filter records
- Search data
- Export to CSV
- Edit entries
- Delete records (⚠️ be careful!)

---

## 🔍 **Admin Features**

### **Search & Filter:**
- Every table has search functionality
- Filter by date, status, category, etc.
- Date range selectors for time-based queries

### **Bulk Actions:**
- Select multiple entries
- Delete selected items
- Custom bulk operations

### **Data Export:**
- Export filtered results
- Download as CSV/JSON
- Great for backups

---

## 🎨 **Your Brand Colors in Action**

The admin panel uses your identity colors:
- **Primary:** #341a60 (Deep Purple)
- **Secondary:** #966bfc (Light Purple)
- **Font:** #e6dafe (Light Text)
- **Background:** White with purple accents

---

## 🔐 **Security Best Practices**

1. **Change the default password immediately**
2. **Use a strong password** (12+ characters, mixed case, numbers, symbols)
3. **Don't share admin credentials**
4. **Only open port 8000 to trusted IPs** (optional: restrict in security group)
5. **Regular backups** of the PostgreSQL database

---

## 💾 **Database Backup Commands**

### **Backup Database:**
```bash
pg_dump -U onedevelopment -h localhost onedevelopment_agent > backup_$(date +%Y%m%d).sql
```

### **Restore Database:**
```bash
psql -U onedevelopment -h localhost onedevelopment_agent < backup_YYYYMMDD.sql
```

---

## 📱 **Direct PostgreSQL Access (Advanced)**

If you want to access PostgreSQL directly via command line:

```bash
# Connect to database
psql -U onedevelopment -h localhost -d onedevelopment_agent

# List all tables
\dt

# View table structure
\d agent_knowledgebase

# Query data
SELECT * FROM agent_knowledgebase LIMIT 10;

# Exit
\q
```

**Password:** onedevelopment123

---

## 🎯 **Quick Links**

- **Admin Panel:** http://51.20.117.103:8000/admin
- **API Docs:** http://51.20.117.103:8000/api/
- **Frontend:** http://51.20.117.103:3000
- **Health Check:** http://51.20.117.103:8000/api/health/

---

## 🐛 **Troubleshooting**

### **Can't access admin panel?**
```bash
# Check if backend is running
./manage-servers.sh status

# Restart backend
./manage-servers.sh restart

# View logs
./manage-servers.sh logs backend
```

### **Forgot admin password?**
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py changepassword admin
```

### **Need to create another admin user?**
```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
python manage.py createsuperuser
```

---

## 📸 **What You'll See**

When you login, you'll see:

1. **✨ One Development Logo** in the header with purple gradient
2. **🎨 Beautiful Dashboard** with your brand colors
3. **📊 Database Stats** showing record counts
4. **🔧 Management Tools** for all your data
5. **💬 Real-time Data** from your live application

---

## 🎉 **You're All Set!**

Your custom-branded PostgreSQL admin panel is ready!

**Go to:** http://51.20.117.103:8000/admin  
**Login and explore your database!** 🚀

---

**Need help?** All your data is safely stored in PostgreSQL and accessible through this beautiful interface!

