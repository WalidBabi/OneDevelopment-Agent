# 🚀 Quick Start - Luna with HeyGen

**Get Luna talking in 3 minutes!**

---

## Step 1: Get HeyGen API Key (2 minutes)

1. Go to: https://app.heygen.com/settings?nav=API
2. Sign up (free trial available)
3. Copy your API key

---

## Step 2: Configure (30 seconds)

```bash
# Edit .env file
nano /home/ec2-user/OneDevelopment-Agent/backend/.env

# Add this line:
HEYGEN_API_KEY=your_actual_api_key_here

# Save and exit (Ctrl+X, Y, Enter)
```

---

## Step 3: Restart Backend (30 seconds)

```bash
cd /home/ec2-user/OneDevelopment-Agent/backend
source venv/bin/activate
pkill -f "manage.py runserver"
python manage.py runserver 0.0.0.0:8000 &
```

---

## Step 4: Test Luna! (30 seconds)

1. Open: http://13.62.188.127:3000/
2. Click Luna's avatar
3. Say: **"Hello Luna!"**
4. Watch Luna respond with professional lip-sync! 🎬

---

## ✅ That's It!

Luna now uses **HeyGen** for professional talking avatars:
- ✅ No laptop GPU needed
- ✅ No SadTalker setup
- ✅ No ElevenLabs
- ✅ Just cloud-based HeyGen!

**Video generation takes 20-60 seconds - be patient!**

---

## 🐛 Issues?

See full documentation: `HEYGEN_SETUP.md`

Or check:
- HeyGen API key is correct
- Backend is running
- Luna.png exists in frontend/public/



