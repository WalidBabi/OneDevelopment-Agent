# 🚀 Quick AWS GPU Setup for Luna Avatar

## Option 1: Via AWS Console (Easiest - 5 mins)

### Step 1: Launch GPU Instance

1. Go to **AWS Console** → **EC2** → **Launch Instance**

2. Configure:
   - **Name:** `luna-avatar-gpu`
   - **AMI:** Search for "Deep Learning AMI GPU PyTorch" → Select Ubuntu version
   - **Instance type:** `g4dn.xlarge` (~$0.53/hour)
   - **Key pair:** Select your existing key or create new
   - **Network settings:** 
     - Allow SSH (port 22)
     - Add rule: Custom TCP, port **8001**, source 0.0.0.0/0
   - **Storage:** 100GB gp3

3. Click **Launch Instance**

### Step 2: SSH & Setup (after instance is running)

```bash
# SSH into the GPU instance
ssh -i your-key.pem ubuntu@GPU_INSTANCE_IP

# Quick setup (copy-paste this entire block):
sudo apt update && sudo apt install -y ffmpeg git screen
git clone https://github.com/[YOUR-USERNAME]/OneDevelopment-Agent.git
cd OneDevelopment-Agent/avatar_service
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip3 install fastapi uvicorn edge-tts pydantic python-multipart pillow imageio opencv-python librosa soundfile pydub scipy

# Start the service
python3 avatar_server_aws.py
```

### Step 3: Update Main Backend

On your main EC2 (<YOUR_SERVER_IP>):

```bash
# Add to .env or export
export AVATAR_SERVICE_URL=http://GPU_INSTANCE_IP:8001

# Restart backend
cd /home/ec2-user/OneDevelopment-Agent
bash restart-backend.sh
```

### Step 4: Test

```bash
curl http://GPU_INSTANCE_IP:8001/health
```

---

## Option 2: Via AWS CLI (Automated)

### Step 1: Configure AWS CLI

```bash
aws configure
# Enter:
# - AWS Access Key ID: (from IAM)
# - AWS Secret Access Key: (from IAM)
# - Default region: eu-north-1 (or your preferred)
# - Default output: json
```

### Step 2: Run Deploy Script

```bash
cd /home/ec2-user/OneDevelopment-Agent/avatar_service
export KEY_NAME=your-key-pair-name
./deploy_aws_gpu.sh
```

---

## Cost Comparison

| Instance | GPU | Cost/Hour | Cost/Month (8hrs/day) |
|----------|-----|-----------|----------------------|
| g4dn.xlarge | T4 16GB | $0.53 | ~$126 |
| g4dn.medium | T4 16GB | $0.38 | ~$91 |
| g5.xlarge | A10G 24GB | $1.01 | ~$241 |

**💡 Tip:** Use Spot Instances for 60-70% savings!

---

## Performance

| Quality | Current (CPU) | AWS GPU (T4) | Speedup |
|---------|--------------|--------------|---------|
| Fast | 2-5 min | 10-15 sec | ~10-20x |
| Standard | 5-10 min | 20-30 sec | ~15-20x |
| High | 10+ min | 45-60 sec | ~10-15x |

---

## Quick Reference

```bash
# SSH to GPU instance
ssh -i ~/.ssh/your-key.pem ubuntu@GPU_IP

# Start avatar service (in screen)
cd OneDevelopment-Agent/avatar_service
screen -S avatar
python3 avatar_server_aws.py
# Ctrl+A, D to detach

# Check logs
screen -r avatar

# Test
curl http://GPU_IP:8001/health
curl -X POST http://GPU_IP:8001/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am Luna!", "quality": "fast"}'
```

---

## Troubleshooting

### "CUDA not available"
```bash
# Verify NVIDIA driver
nvidia-smi

# If missing, install:
sudo apt install nvidia-driver-525
sudo reboot
```

### "Port 8001 not accessible"
- Check security group allows inbound port 8001
- Verify instance has public IP

### "Model not found"
```bash
# The simplified version doesn't need SadTalker models
# It uses a basic lip-sync approach
# For full quality, download SadTalker checkpoints
```



