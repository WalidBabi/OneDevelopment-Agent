#!/bin/bash
# =============================================================================
# Luna Avatar Service - AWS GPU Setup Script
# Run this on a fresh AWS Deep Learning AMI GPU instance
# =============================================================================

set -e  # Exit on error

echo "🚀 Luna Avatar Service - AWS GPU Setup"
echo "======================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on GPU instance
echo -e "\n${YELLOW}Checking GPU...${NC}"
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ NVIDIA driver not found. Are you on a GPU instance?${NC}"
    exit 1
fi

nvidia-smi
echo -e "${GREEN}✅ GPU detected${NC}"

# Check CUDA
echo -e "\n${YELLOW}Checking CUDA...${NC}"
if ! command -v nvcc &> /dev/null; then
    echo -e "${YELLOW}⚠️ nvcc not in PATH, checking CUDA installation...${NC}"
    if [ -d "/usr/local/cuda" ]; then
        export PATH=/usr/local/cuda/bin:$PATH
        export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
        echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
        echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
        echo -e "${GREEN}✅ CUDA configured${NC}"
    fi
else
    echo -e "${GREEN}✅ CUDA available: $(nvcc --version | grep release)${NC}"
fi

# Create working directory
echo -e "\n${YELLOW}Setting up directories...${NC}"
WORK_DIR="$HOME/luna-avatar"
mkdir -p $WORK_DIR
cd $WORK_DIR

# Install system dependencies
echo -e "\n${YELLOW}Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libportaudio2 \
    git-lfs \
    screen \
    htop

# Create Python virtual environment
echo -e "\n${YELLOW}Creating Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA (if not using Deep Learning AMI)
echo -e "\n${YELLOW}Installing PyTorch with CUDA...${NC}"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install avatar service requirements
echo -e "\n${YELLOW}Installing avatar service requirements...${NC}"
pip install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    edge-tts==6.1.10 \
    gTTS==2.5.1 \
    librosa==0.10.1 \
    soundfile==0.12.1 \
    pydub==0.25.1 \
    opencv-python==4.8.1.78 \
    pillow==10.1.0 \
    imageio==2.33.0 \
    imageio-ffmpeg==0.4.9 \
    numpy==1.24.3 \
    scipy==1.11.4 \
    requests==2.31.0

# Clone SadTalker for video generation
echo -e "\n${YELLOW}Setting up SadTalker model...${NC}"
if [ ! -d "SadTalker" ]; then
    git clone https://github.com/OpenTalker/SadTalker.git
    cd SadTalker
    pip install -r requirements.txt
    
    # Download pretrained models
    echo -e "\n${YELLOW}Downloading SadTalker models (this may take a while)...${NC}"
    mkdir -p checkpoints
    cd checkpoints
    
    # Download models using gdown or wget
    pip install gdown
    
    # Main checkpoints
    gdown --folder https://drive.google.com/drive/folders/1Wd88VDoLhVzYsQ30_qDVluQr_Xm46yHT -O .
    
    cd ../..
fi

# Copy avatar service files
echo -e "\n${YELLOW}Setting up avatar service...${NC}"
REPO_DIR="$HOME/OneDevelopment-Agent"
if [ -d "$REPO_DIR/avatar_service" ]; then
    cp $REPO_DIR/avatar_service/avatar_server_final.py $WORK_DIR/
    cp $REPO_DIR/avatar_service/sadtalker_generator.py $WORK_DIR/
    cp $REPO_DIR/avatar_service/tts_manager.py $WORK_DIR/ 2>/dev/null || true
    cp $REPO_DIR/avatar_service/luna_base.png $WORK_DIR/
    echo -e "${GREEN}✅ Avatar service files copied${NC}"
else
    echo -e "${YELLOW}⚠️ Repository not found. Will need to copy files manually.${NC}"
fi

# Create directories
mkdir -p $WORK_DIR/generated_videos
mkdir -p $WORK_DIR/temp_audio

# Create systemd service
echo -e "\n${YELLOW}Creating systemd service...${NC}"
sudo tee /etc/systemd/system/luna-avatar.service > /dev/null << EOF
[Unit]
Description=Luna Avatar GPU Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$WORK_DIR/venv/bin:/usr/local/cuda/bin:\$PATH"
Environment="LD_LIBRARY_PATH=/usr/local/cuda/lib64"
ExecStart=$WORK_DIR/venv/bin/python avatar_server_final.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable luna-avatar

# Create startup script
echo -e "\n${YELLOW}Creating startup scripts...${NC}"
cat > $WORK_DIR/start.sh << 'EOF'
#!/bin/bash
cd ~/luna-avatar
source venv/bin/activate
python avatar_server_final.py
EOF
chmod +x $WORK_DIR/start.sh

cat > $WORK_DIR/start-screen.sh << 'EOF'
#!/bin/bash
screen -dmS avatar bash -c 'cd ~/luna-avatar && source venv/bin/activate && python avatar_server_final.py'
echo "Avatar service started in screen session 'avatar'"
echo "To attach: screen -r avatar"
EOF
chmod +x $WORK_DIR/start-screen.sh

# Get instance public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_IP")

# Print summary
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "📁 Working Directory: $WORK_DIR"
echo "🐍 Python Environment: $WORK_DIR/venv"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start the service:"
echo "   cd $WORK_DIR && ./start-screen.sh"
echo ""
echo "2. Or use systemd:"
echo "   sudo systemctl start luna-avatar"
echo "   sudo systemctl status luna-avatar"
echo ""
echo "3. Test health:"
echo "   curl http://localhost:8001/health"
echo ""
echo "4. Configure your main backend:"
echo "   AVATAR_SERVICE_URL=http://$PUBLIC_IP:8001"
echo ""
echo "=============================================="
echo "Instance Public IP: $PUBLIC_IP"
echo "Avatar Service URL: http://$PUBLIC_IP:8001"
echo "=============================================="

