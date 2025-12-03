# AWS GPU Setup for Luna Avatar Service

## Quick Overview

Deploy Luna's avatar service on AWS GPU for fast video generation:
- **Recommended:** g4dn.xlarge (NVIDIA T4 - 16GB VRAM) - ~$0.526/hour
- **Budget:** g4dn.medium (NVIDIA T4 - 16GB VRAM, less CPU) - ~$0.38/hour
- **Premium:** g5.xlarge (NVIDIA A10G - 24GB VRAM) - ~$1.006/hour

---

## Step 1: Launch AWS GPU Instance

### Using AWS Console

1. Go to **EC2 Dashboard** → **Launch Instance**

2. **Name:** `luna-avatar-gpu`

3. **AMI:** Choose **Deep Learning AMI GPU PyTorch 2.0 (Ubuntu 20.04)**
   - This comes with CUDA, cuDNN, and PyTorch pre-installed!
   - Search: "Deep Learning AMI GPU PyTorch"

4. **Instance Type:** `g4dn.xlarge`
   - 4 vCPUs, 16GB RAM, 1 NVIDIA T4 GPU (16GB VRAM)
   - Good balance of cost and performance

5. **Key Pair:** Create or select existing key pair

6. **Network Settings:**
   - Create security group with:
     - SSH (22) - Your IP only
     - Custom TCP (8001) - Anywhere (0.0.0.0/0) for avatar API
     - Custom TCP (8002) - Anywhere (for health checks)

7. **Storage:** 100GB gp3 (for models and video cache)

8. **Launch!**

### Using AWS CLI

```bash
# Create security group
aws ec2 create-security-group \
  --group-name luna-avatar-sg \
  --description "Luna Avatar Service GPU"

# Add rules
aws ec2 authorize-security-group-ingress \
  --group-name luna-avatar-sg \
  --protocol tcp --port 22 --cidr YOUR_IP/32

aws ec2 authorize-security-group-ingress \
  --group-name luna-avatar-sg \
  --protocol tcp --port 8001 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id ami-0xxxxxxxx \  # Deep Learning AMI ID for your region
  --instance-type g4dn.xlarge \
  --key-name your-key-pair \
  --security-groups luna-avatar-sg \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=luna-avatar-gpu}]'
```

---

## Step 2: Connect and Setup

### SSH into the instance

```bash
ssh -i your-key.pem ubuntu@YOUR_GPU_INSTANCE_IP
```

### Run the setup script

```bash
# Clone the repository
git clone https://github.com/WalidBabi/OneDevelopment-Agent.git
cd OneDevelopment-Agent/avatar_service

# Run setup
chmod +x aws_gpu_setup.sh
./aws_gpu_setup.sh
```

---

## Step 3: Configure Main Backend

On your main EC2 instance (where Luna runs):

```bash
# Edit environment
sudo nano /home/ec2-user/OneDevelopment-Agent/.env

# Add:
AVATAR_SERVICE_URL=http://YOUR_GPU_INSTANCE_IP:8001

# Restart backend
cd /home/ec2-user/OneDevelopment-Agent
bash restart-backend.sh
```

---

## Step 4: Test

```bash
# Health check
curl http://YOUR_GPU_INSTANCE_IP:8001/health

# Test generation
curl -X POST http://YOUR_GPU_INSTANCE_IP:8001/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am Luna!", "quality": "fast"}'
```

---

## Cost Estimates

| Instance | GPU | Hourly | Monthly (24/7) | Monthly (8hrs/day) |
|----------|-----|--------|----------------|---------------------|
| g4dn.xlarge | T4 16GB | $0.526 | ~$378 | ~$126 |
| g4dn.medium | T4 16GB | $0.38 | ~$274 | ~$91 |
| g5.xlarge | A10G 24GB | $1.006 | ~$724 | ~$241 |

**Tip:** Use Spot Instances for 60-70% savings!

---

## Performance Expectations

| Quality | g4dn.xlarge (T4) | g5.xlarge (A10G) |
|---------|------------------|-------------------|
| Fast | 10-15 seconds | 5-8 seconds |
| Standard | 20-30 seconds | 12-18 seconds |
| High | 45-60 seconds | 25-35 seconds |

Much faster than CPU generation (2-5+ minutes)!



