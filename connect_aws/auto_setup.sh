#!/bin/bash
# ========================================
# YouTube Player - Auto Setup Script
# تثبيت تلقائي كامل (مرة واحدة)
# ========================================

set -e  # Stop on any error

echo "========================================="
echo "  YouTube Player - Auto Setup"
echo "  تثبيت تلقائي كامل"
echo "========================================="
echo ""

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    echo "⚠️  يرجى تشغيل السكريبت كمستخدم ubuntu"
    echo "   ssh -i meeee.pem ubuntu@<server-ip>"
    exit 1
fi

# 1. System Update
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 [1/7] تحديث النظام..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo apt update && sudo apt upgrade -y

# 2. Add Python Repository
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 [2/7] إضافة مستودع Python 3.13..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3-pip

# 3. Install Brave Browser
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🦁 [3/7] تثبيت Brave Browser..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Download and add Brave GPG key
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg \
  https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg

# Add Brave repository
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | \
  sudo tee /etc/apt/sources.list.d/brave-browser-release.list

# Install Brave
sudo apt update
sudo apt install -y brave-browser

# Verify installation
if command -v brave-browser &> /dev/null; then
    echo "✅ Brave installed: $(brave-browser --version)"
else
    echo "❌ Brave installation failed!"
    exit 1
fi

# 4. Install Xvfb and Dependencies
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🖥️  [4/7] تثبيت Xvfb والمكتبات..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo apt install -y \
    xvfb \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2

# 5. Clone/Update Project
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 [5/7] تنزيل المشروع من GitHub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd ~
if [ -d "player-youtube" ]; then
    echo "📂 المشروع موجود، جاري التحديث..."
    cd player-youtube
    git pull origin main
else
    echo "📥 استنساخ المشروع..."
    git clone https://github.com/Tariq990/player-youtube.git
    cd player-youtube
fi

# 6. Setup Python Environment
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 [6/7] إعداد البيئة الافتراضية..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Setup Systemd Service
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  [7/7] إعداد خدمة 24/7..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo tee /etc/systemd/system/youtube-player.service > /dev/null <<EOF
[Unit]
Description=YouTube Player Auto-View Service (24/7)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/player-youtube
Environment="DISPLAY=:99"
ExecStartPre=/bin/sh -c 'Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &'
ExecStart=/home/ubuntu/player-youtube/venv/bin/python3.13 /home/ubuntu/player-youtube/src/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable youtube-player

echo ""
echo "========================================="
echo "  ✅ التثبيت اكتمل بنجاح!"
echo "========================================="
echo ""
echo "📋 الخطوات التالية:"
echo ""
echo "1️⃣  ارفع ملف cookies.json من جهازك:"
echo "   scp -i meeee.pem data/cookies.json ubuntu@SERVER_IP:~/player-youtube/data/"
echo ""
echo "2️⃣  ابدأ الخدمة:"
echo "   sudo systemctl start youtube-player"
echo ""
echo "3️⃣  تحقق من الحالة:"
echo "   sudo systemctl status youtube-player"
echo ""
echo "4️⃣  شاهد السجلات:"
echo "   sudo journalctl -u youtube-player -f"
echo ""
echo "========================================="
