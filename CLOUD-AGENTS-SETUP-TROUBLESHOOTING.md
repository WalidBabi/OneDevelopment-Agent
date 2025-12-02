# 🔧 Cloud Agents Setup Troubleshooting Guide

## 🐛 Issue: "Resume Setup" Restarts from Beginning

**Problem:** After clicking "Everything Works" in the validation step, the setup window closes. When you click "Resume Setup" in Cloud Agents, it restarts from the beginning instead of recognizing that setup is complete.

---

## ✅ **Solution: Verify Setup State**

The setup might actually be complete, but Cursor isn't recognizing it. Follow these steps to verify and fix:

### **Step 1: Check Current Snapshot Status**

Your snapshot is stored in `.cursor/environment.json`:
```json
{
  "snapshot": "snapshot-20251202-ff503364-668b-4b4a-97dd-c501ebf3d58d",
  "terminals": []
}
```

**If you see a snapshot ID, your snapshot was created successfully!**

### **Step 2: Verify GitHub Connection**

1. Go to your GitHub repository
2. Navigate to: **Settings → Integrations → Installed GitHub Apps**
3. Verify that **Cursor** is installed and has access to your repository
4. If not installed:
   - Go back to Cursor Cloud Agents setup
   - Click "Connect GitHub" and complete the installation
   - Grant access to your repository

### **Step 3: Verify Snapshot Completion**

Run this command to check if your snapshot exists:
```bash
# Check if snapshot is referenced
cat .cursor/environment.json
```

If you see a snapshot ID (like `snapshot-20251202-...`), the snapshot step completed.

### **Step 4: Verify Runtime Settings**

Check if environment variables are configured:
```bash
# Check for environment files
ls -la backend/.env* 2>/dev/null || echo "No .env files found"
```

### **Step 5: Test the Environment**

If the snapshot exists, you can test if everything works:

```bash
# Test Python environment
python3 --version
python3 -c "import django; print('Django:', django.get_version())"

# Test Node.js environment  
node --version
npm --version

# Test PostgreSQL client
psql --version

# Test if dependencies are installed
python3 -c "import langchain; print('LangChain installed')" 2>/dev/null || echo "LangChain not found"
```

---

## 🔄 **Workaround: Skip "Resume Setup"**

If your snapshot exists and GitHub is connected, you might be able to skip the setup:

1. **Don't click "Resume Setup"** - Instead:
   - Go directly to Cloud Agents tab
   - Try creating a new agent or task
   - The agent should use your existing snapshot

2. **If that doesn't work**, try:
   - Close and reopen Cursor
   - Open your repository folder again
   - Check if Cloud Agents recognizes the setup

---

## 🛠️ **Manual Fix: Re-validate Setup**

If you need to restart the setup properly:

### **Option A: Complete Setup Fresh**

1. Go to **Cloud Agents** tab
2. Click **"New Agent"** or **"Setup Cloud Agent"**
3. Complete all steps:
   - ✅ Connect GitHub (verify app is installed)
   - ✅ Create Machine Snapshot (wait for completion)
   - ✅ Configure Runtime Settings (add any required env vars)
   - ✅ Validate Setup (test everything works)

4. **Important:** At each step, wait for confirmation before proceeding
5. Don't close the window until you see "Setup Complete" or similar message

### **Option B: Verify Each Step Manually**

1. **GitHub Connection:**
   ```bash
   # Verify GitHub access
   git remote -v
   git fetch origin
   ```

2. **Snapshot:**
   ```bash
   # Check snapshot file
   cat .cursor/environment.json
   ```

3. **Runtime Settings:**
   ```bash
   # Check environment
   echo $OPENAI_API_KEY | head -c 10  # Should show first 10 chars if set
   ```

4. **Validation:**
   ```bash
   # Run a quick test
   cd backend
   python manage.py check
   ```

---

## 📋 **Checklist: Is Setup Actually Complete?**

Use this checklist to verify your setup:

- [ ] **GitHub App Installed:** Check GitHub repo → Settings → Installed Apps → Cursor
- [ ] **Snapshot Created:** `.cursor/environment.json` contains a snapshot ID
- [ ] **Dockerfile Present:** `Dockerfile` exists in project root
- [ ] **Environment Variables:** `backend/.env` exists (if needed)
- [ ] **Dependencies Installed:** Python and Node packages are installed
- [ ] **Git Repository:** Repository is initialized and connected to GitHub

**If all are checked ✅, your setup is likely complete!**

---

## 🚨 **Common Causes**

1. **GitHub App Not Fully Installed**
   - Solution: Reinstall Cursor GitHub app and grant full access

2. **Snapshot Not Saved**
   - Solution: Recreate snapshot and wait for confirmation

3. **Cursor State Not Persisted**
   - Solution: Restart Cursor after completing setup
   - Check `.cursor/environment.json` to verify snapshot ID is saved

4. **Repository Not Detected**
   - Solution: Make sure you're in a Git repository folder
   - Run `git status` to verify

---

## 💡 **Prevention Tips**

1. **Don't close the setup window** until you see explicit completion message
2. **Wait for each step** to fully complete before proceeding
3. **Take screenshots** of each completed step for reference
4. **Check `.cursor/environment.json`** after each step to verify state is saved

---

## 🔍 **Debugging: Check Cursor Logs**

If the issue persists, check Cursor's logs:

**On Linux:**
```bash
# Check Cursor logs (location may vary)
~/.config/Cursor/logs/
# or
~/.cursor/logs/
```

Look for errors related to:
- Cloud Agents setup
- Snapshot creation
- GitHub connection
- State persistence

---

## 📞 **Still Having Issues?**

If none of the above works:

1. **Report to Cursor Support** - This appears to be a Cursor IDE bug
2. **Try Alternative Approach:**
   - Use the snapshot ID directly if you have it
   - Manually configure Cloud Agents settings
   - Use Cursor's API/CLI if available

3. **Workaround:**
   - Complete setup in one session without closing windows
   - Don't use "Resume Setup" - start fresh if needed
   - Document your snapshot ID for reference

---

## ✅ **Quick Verification Script**

Run this script to check your setup status:

```bash
#!/bin/bash
echo "🔍 Checking Cloud Agents Setup Status..."
echo ""

# Check snapshot
if [ -f ".cursor/environment.json" ]; then
    SNAPSHOT=$(grep -o '"snapshot": "[^"]*"' .cursor/environment.json | cut -d'"' -f4)
    if [ ! -z "$SNAPSHOT" ]; then
        echo "✅ Snapshot found: $SNAPSHOT"
    else
        echo "❌ No snapshot ID found"
    fi
else
    echo "❌ .cursor/environment.json not found"
fi

# Check Dockerfile
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile exists"
else
    echo "❌ Dockerfile not found"
fi

# Check Git
if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    REMOTE=$(git remote get-url origin 2>/dev/null || echo "No remote")
    echo "   Remote: $REMOTE"
else
    echo "❌ Not a Git repository"
fi

# Check GitHub connection
if git ls-remote origin &>/dev/null; then
    echo "✅ GitHub connection working"
else
    echo "⚠️  GitHub connection may have issues"
fi

echo ""
echo "📋 Setup Status Check Complete"
```

Save this as `check-setup.sh` and run: `bash check-setup.sh`

---

**Last Updated:** Based on snapshot ID `snapshot-20251202-ff503364-668b-4b4a-97dd-c501ebf3d58d`


