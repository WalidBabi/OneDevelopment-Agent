# Upgrade to Python 3.11+ for Full DeepAgents Support

## Why Upgrade?

Luna now uses **DeepAgents** architecture with:
- ✅ **Long-term memory persistence** in `/memories/` directory
- ✅ **Specialized subagents** for complex tasks (research, pricing, comparison, buyer journey)
- ✅ **FilesystemBackend** for memory that survives server restarts
- ✅ **Planning tools** for strategic thinking

**REQUIRES: Python 3.11+**

---

## Current Status

```bash
Current Python: 3.9.24
Required: 3.11+
```

Luna is now configured for DeepAgents but needs Python upgrade to activate.

---

## Upgrade Steps

### Option 1: Using pyenv (Recommended)

```bash
# Install pyenv if not already installed
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0

# Set Python 3.11 for this project
cd /home/ec2-user/OneDevelopment-Agent/backend
pyenv local 3.11.0

# Verify
python --version  # Should show 3.11.0
```

### Option 2: System-wide Python Upgrade (Amazon Linux 2023)

```bash
# Update system
sudo dnf update -y

# Install Python 3.11
sudo dnf install python3.11 python3.11-pip python3.11-devel -y

# Create symlink (optional)
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify
python3 --version  # Should show 3.11.x
```

### Option 3: Using conda/mamba

```bash
# Create new environment with Python 3.11
conda create -n luna python=3.11
conda activate luna

# Or with mamba (faster)
mamba create -n luna python=3.11
mamba activate luna
```

---

## After Upgrading Python

### 1. Recreate Virtual Environment

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend

# Remove old venv
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Verify Python version in venv
python --version  # Should show 3.11.x
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements (includes deepagents)
pip install -r requirements.txt
```

### 3. Verify DeepAgents Installation

```bash
python -c "from deepagents import create_deep_agent; print('✅ DeepAgents installed!')"
```

### 4. Initialize Memory Storage

```bash
# The /memories/ directory will be auto-created
# But you can verify:
ls -la /home/ec2-user/OneDevelopment-Agent/backend/memories/

# Should see directory created by Luna on first run
```

### 5. Restart Server

```bash
# Stop current server
pkill -f "python manage.py runserver"

# Restart with new Python
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

---

## What Changes After Upgrade

### Before (Python 3.9)
- ❌ No DeepAgents support
- ❌ No long-term memory persistence
- ❌ Using compatibility mode
- ⚠️  Memory only in database (resets on cleanup)

### After (Python 3.11+)
- ✅ Full DeepAgents architecture
- ✅ **Persistent memory** in `/memories/` directory
- ✅ **4 specialized subagents** automatically available
- ✅ **FilesystemBackend** for cross-session memory
- ✅ User information persists across refreshes
- ✅ Luna remembers your name, preferences, conversation context

---

## Testing the Upgrade

After upgrading, test Luna's memory:

```python
# Test 1: Tell Luna your name
"My name is Walid"

# Luna saves to /memories/ directory

# Test 2: Refresh page and ask
"Do you know my name?"

# Luna retrieves from /memories/ directory
# Response: "Yes! Your name is Walid."
```

Check memory files:
```bash
ls -la /home/ec2-user/OneDevelopment-Agent/backend/memories/
# Should see persistent memory files
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'deepagents'"

**Solution:**
```bash
pip install deepagents
# Or reinstall all requirements
pip install -r requirements.txt
```

### Issue: "Python version too low"

**Solution:**
```bash
python --version
# If still 3.9, activate correct venv or upgrade Python
```

### Issue: Permission errors on /memories/ directory

**Solution:**
```bash
sudo chown -R $USER:$USER /home/ec2-user/OneDevelopment-Agent/backend/memories/
chmod 755 /home/ec2-user/OneDevelopment-Agent/backend/memories/
```

### Issue: ImportError with langgraph.store.memory

**Solution:**
```bash
pip install --upgrade langgraph langchain-core
```

---

## Rollback (If Needed)

If you need to rollback to Python 3.9:

```bash
# Restore old venv
pyenv local 3.9.24  # If using pyenv

# Or recreate venv with Python 3.9
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Note: The new `luna_deepagent.py` is designed for Python 3.11+ and won't work on 3.9.

---

## Benefits Summary

| Feature | Python 3.9 | Python 3.11+ |
|---------|-----------|--------------|
| **DeepAgents** | ❌ Not available | ✅ Full support |
| **Long-term memory** | ⚠️  Database only | ✅ Persistent files |
| **Memory persistence** | ❌ Resets on cleanup | ✅ Survives restarts |
| **Subagents** | ⚠️  As tools | ✅ True subagents |
| **Filesystem backend** | ❌ Not available | ✅ Available |
| **Cross-session memory** | ❌ Limited | ✅ Full support |

---

## Questions?

After upgrading, Luna will automatically:
1. Create `/memories/` directory
2. Initialize FilesystemBackend
3. Activate all 4 subagents
4. Enable persistent long-term memory

Check server logs for confirmation:
```
💾 Memory storage: /home/ec2-user/OneDevelopment-Agent/backend/memories
✅ Using FilesystemBackend for persistent memory
✅ Luna DeepAgent initialized with 23 tools, 4 subagents (model: openai:gpt-4o)
```

Enjoy Luna's enhanced memory! 🌙🧠







