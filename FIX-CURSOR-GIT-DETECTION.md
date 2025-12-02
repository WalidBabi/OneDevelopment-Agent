# 🔧 Fix: Cursor Not Detecting Git Repository

## 🐛 Problem
Cursor shows "Open a Git repository" even though you're already in a Git repository folder.

## ✅ Quick Fix (Try These in Order)

### **Solution 1: Re-open the Folder in Cursor** ⭐ RECOMMENDED

1. **Click the "Open Folder" button** in the Cloud Agents tab
2. Navigate to: `/home/ec2-user/OneDevelopment-Agent`
3. Select the folder and click "Open"
4. Wait for Cursor to reload
5. Go back to Cloud Agents tab - it should now detect the Git repository

**Why this works:** Sometimes Cursor needs the folder to be explicitly opened through its file picker to properly detect Git repositories.

---

### **Solution 2: Reload Cursor Window**

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Developer: Reload Window`
3. Press Enter
4. Wait for Cursor to reload
5. Check Cloud Agents tab again

---

### **Solution 3: Close and Reopen Cursor**

1. **Close Cursor completely** (not just the window)
2. **Reopen Cursor**
3. **File → Open Folder** → Select `/home/ec2-user/OneDevelopment-Agent`
4. Wait for it to load
5. Go to Cloud Agents tab

---

### **Solution 4: Verify Git Repository**

Run this command to ensure Git is properly initialized:

```bash
cd /home/ec2-user/OneDevelopment-Agent
git rev-parse --git-dir
```

Should output: `.git`

If it doesn't, there might be a Git issue. But based on our check, your Git repo is fine.

---

### **Solution 5: Check Cursor Workspace Settings**

1. Press `Ctrl+Shift+P`
2. Type: `Preferences: Open Workspace Settings (JSON)`
3. Check if there's a workspace file that might be interfering
4. If you see a `.code-workspace` file, try opening the folder directly instead

---

## 🎯 Most Likely Solution

**Click "Open Folder" and select the same folder again.** This forces Cursor to re-scan and detect the Git repository.

---

## 📋 After Git is Detected

Once Cursor detects your Git repository, you should see:

- ✅ "New Agent" button appears
- ✅ Cloud Agents setup options become available
- ✅ Your snapshot should be recognized

---

## 🔍 Verification

After trying Solution 1, verify it worked:

1. Go to Cloud Agents tab
2. You should see options like:
   - "New Agent" button
   - Setup options
   - Agent management

If you still see "Open a Git repository", try Solution 2 or 3.

---

## 💡 Why This Happens

Cursor sometimes doesn't detect Git repositories when:
- The folder was opened via command line
- Cursor was opened before the Git repo was initialized
- There's a workspace configuration conflict
- Cursor needs to refresh its file system watchers

Re-opening the folder forces Cursor to re-scan everything.

---

## ✅ Expected Result

After clicking "Open Folder" and selecting your repository:

```
Cloud Agents
├── Get Started
├── [New Agent] button ← Should appear
├── Your existing snapshot
└── Agent management options
```

Instead of:
```
Cloud Agents
├── Get Started
└── [Open Folder] button ← This should disappear
```

---

**Try Solution 1 first - it's the quickest fix!** 🚀


