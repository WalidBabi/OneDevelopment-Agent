#!/bin/bash
# =============================================================================
# Luna Avatar - Deploy to AWS GPU Instance
# Run this from your main EC2 instance
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║          Luna Avatar - AWS GPU Deployment                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
REGION="${AWS_REGION:-eu-north-1}"
INSTANCE_TYPE="${GPU_INSTANCE_TYPE:-g4dn.xlarge}"
KEY_NAME="${KEY_NAME:-}"
SECURITY_GROUP_NAME="luna-avatar-sg"

# Check for required tools
echo -e "${YELLOW}Checking requirements...${NC}"
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not installed. Please install it first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured.${NC}"
    echo "Run: aws configure"
    exit 1
fi
echo -e "${GREEN}✅ AWS CLI configured${NC}"

# Get key pair
if [ -z "$KEY_NAME" ]; then
    echo ""
    echo -e "${YELLOW}Available key pairs:${NC}"
    aws ec2 describe-key-pairs --query 'KeyPairs[*].KeyName' --output table
    echo ""
    read -p "Enter key pair name: " KEY_NAME
fi

# Find Deep Learning AMI
echo -e "\n${YELLOW}Finding Deep Learning AMI...${NC}"
AMI_ID=$(aws ec2 describe-images \
    --region $REGION \
    --owners amazon \
    --filters "Name=name,Values=Deep Learning AMI GPU PyTorch*Ubuntu 20.04*" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

if [ "$AMI_ID" == "None" ] || [ -z "$AMI_ID" ]; then
    # Fallback to Ubuntu 22.04 Deep Learning AMI
    AMI_ID=$(aws ec2 describe-images \
        --region $REGION \
        --owners amazon \
        --filters "Name=name,Values=Deep Learning AMI*Ubuntu 22.04*" \
        --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
        --output text)
fi

echo -e "${GREEN}✅ AMI: $AMI_ID${NC}"

# Create security group
echo -e "\n${YELLOW}Creating security group...${NC}"
SG_ID=$(aws ec2 describe-security-groups \
    --region $REGION \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "None")

if [ "$SG_ID" == "None" ] || [ -z "$SG_ID" ]; then
    SG_ID=$(aws ec2 create-security-group \
        --region $REGION \
        --group-name $SECURITY_GROUP_NAME \
        --description "Luna Avatar GPU Service" \
        --query 'GroupId' \
        --output text)
    
    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --region $REGION \
        --group-id $SG_ID \
        --protocol tcp --port 22 --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --region $REGION \
        --group-id $SG_ID \
        --protocol tcp --port 8001 --cidr 0.0.0.0/0
    
    echo -e "${GREEN}✅ Security group created: $SG_ID${NC}"
else
    echo -e "${GREEN}✅ Security group exists: $SG_ID${NC}"
fi

# Launch instance
echo -e "\n${YELLOW}Launching GPU instance ($INSTANCE_TYPE)...${NC}"
echo "This may take a few minutes..."

INSTANCE_ID=$(aws ec2 run-instances \
    --region $REGION \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=luna-avatar-gpu}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo -e "${GREEN}✅ Instance launched: $INSTANCE_ID${NC}"

# Wait for instance to be running
echo -e "\n${YELLOW}Waiting for instance to be running...${NC}"
aws ec2 wait instance-running \
    --region $REGION \
    --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --region $REGION \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo -e "${GREEN}✅ Instance running at: $PUBLIC_IP${NC}"

# Create user data script
echo -e "\n${YELLOW}Generating setup script...${NC}"
cat > /tmp/gpu_setup.sh << 'SETUP_SCRIPT'
#!/bin/bash
cd /home/ubuntu

# Clone repository
git clone https://github.com/WalidBabi/OneDevelopment-Agent.git
cd OneDevelopment-Agent/avatar_service

# Run setup
chmod +x aws_gpu_setup.sh
./aws_gpu_setup.sh
SETUP_SCRIPT

# Print next steps
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 GPU Instance Launched Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Instance Details:${NC}"
echo "  Instance ID: $INSTANCE_ID"
echo "  Public IP:   $PUBLIC_IP"
echo "  Type:        $INSTANCE_TYPE"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo ""
echo "1. Wait ~2 minutes for instance to fully boot"
echo ""
echo "2. SSH into the GPU instance:"
echo -e "   ${YELLOW}ssh -i ~/.ssh/$KEY_NAME.pem ubuntu@$PUBLIC_IP${NC}"
echo ""
echo "3. Run the setup script:"
echo -e "   ${YELLOW}git clone https://github.com/WalidBabi/OneDevelopment-Agent.git${NC}"
echo -e "   ${YELLOW}cd OneDevelopment-Agent/avatar_service${NC}"
echo -e "   ${YELLOW}chmod +x aws_gpu_setup.sh && ./aws_gpu_setup.sh${NC}"
echo ""
echo "4. Start the avatar service:"
echo -e "   ${YELLOW}cd ~/luna-avatar && ./start-screen.sh${NC}"
echo ""
echo "5. Test the service:"
echo -e "   ${YELLOW}curl http://$PUBLIC_IP:8001/health${NC}"
echo ""
echo "6. Update your main backend:"
echo -e "   ${YELLOW}export AVATAR_SERVICE_URL=http://$PUBLIC_IP:8001${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

# Save instance info
cat > /tmp/gpu_instance_info.txt << EOF
INSTANCE_ID=$INSTANCE_ID
PUBLIC_IP=$PUBLIC_IP
AVATAR_SERVICE_URL=http://$PUBLIC_IP:8001
KEY_NAME=$KEY_NAME
EOF

echo ""
echo -e "Instance info saved to: /tmp/gpu_instance_info.txt"

