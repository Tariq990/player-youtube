#!/bin/bash
# ========================================
# Complete Setup Script for YouTube Player on Ubuntu EC2
# ========================================

set -e  # Exit on any error

echo "========================================="
echo "  YouTube Player - AWS EC2 Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Update system
echo -e "${GREEN}[1/9] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install basic tools
echo -e "${GREEN}[2/9] Installing basic tools...${NC}"
sudo apt install -y git curl wget build-essential software-properties-common \
    ca-certificates gnupg lsb-release unzip

# Install Python 3.13
echo -e "${GREEN}[3/9] Installing Python 3.13...${NC}"
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip

# Verify Python installation
echo -e "${YELLOW}Python version:${NC}"
python3.13 --version

# Install pip for Python 3.13
echo -e "${GREEN}[4/9] Installing pip for Python 3.13...${NC}"
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.13

# Install Brave Browser
echo -e "${GREEN}[5/9] Installing Brave Browser...${NC}"
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg \
  https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] \
  https://brave-browser-apt-release.s3.brave.com/ stable main" | \
  sudo tee /etc/apt/sources.list.d/brave-browser-release.list

sudo apt update
sudo apt install -y brave-browser

# Install Xvfb and dependencies
echo -e "${GREEN}[6/9] Installing Xvfb and display dependencies...${NC}"
sudo apt install -y xvfb \
    fonts-liberation fonts-dejavu-core fonts-noto-color-emoji \
    xfonts-base xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic \
    libnss3 libgconf-2-4 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2

# Clone repository
echo -e "${GREEN}[7/9] Cloning YouTube Player repository...${NC}"
cd ~
if [ -d "player-youtube" ]; then
    echo -e "${YELLOW}Repository already exists, pulling latest changes...${NC}"
    cd player-youtube
    git pull origin main
else
    git clone https://github.com/Tariq990/player-youtube.git
    cd player-youtube
fi

# Create Python virtual environment
echo -e "${GREEN}[8/9] Setting up Python virtual environment...${NC}"
python3.13 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${GREEN}[9/9] Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Upload your cookies.json file"
echo "2. Configure config/config.json if needed"
echo "3. Run the application"
echo ""
echo -e "${YELLOW}To upload cookies.json from your local machine:${NC}"
echo "   scp -i meeee.pem data/cookies.json ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com:~/player-youtube/data/"
echo ""
echo -e "${YELLOW}To run the application:${NC}"
echo "   cd ~/player-youtube"
echo "   source venv/bin/activate"
echo "   xvfb-run -a python3.13 src/app.py"
echo ""
