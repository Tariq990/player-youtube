# 🚀 دليل تشغيل المشروع على Ubuntu Server VPS

## 1️⃣ المتطلبات الأساسية

### مواصفات VPS الموصى بها:
- **نظام التشغيل:** Ubuntu Server 22.04 LTS
- **RAM:** 4GB على الأقل (8GB مفضّل)
- **CPU:** 2 cores على الأقل (4 cores مفضّل)
- **Storage:** 20GB SSD
- **Bandwidth:** Unlimited (للفيديوهات)

### مزودي VPS الموصى بهم:
- **DigitalOcean:** $24/شهر (8GB RAM, 4 vCPUs)
- **Vultr:** $24/شهر (8GB RAM, 4 vCPUs)
- **Linode:** $24/شهر (8GB RAM, 4 vCPUs)
- **Hetzner:** €16/شهر (8GB RAM, 4 vCPUs) - الأرخص

---

## 2️⃣ الاتصال بالسيرفر

```bash
# من جهازك (Windows)
ssh root@YOUR_VPS_IP

# أول مرة، راح يسألك عن fingerprint
# اكتب: yes
```

---

## 3️⃣ تحديث النظام

```bash
# تحديث قائمة الحزم
sudo apt update

# تثبيت التحديثات
sudo apt upgrade -y

# تثبيت الأدوات الأساسية
sudo apt install -y git curl wget build-essential software-properties-common
```

---

## 4️⃣ تثبيت Python 3.13

```bash
# إضافة مستودع deadsnakes للحصول على Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# تثبيت Python 3.13 مع pip
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip

# التحقق من النسخة
python3.13 --version

# تثبيت pip لـ Python 3.13
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13
```

---

## 5️⃣ تثبيت Brave Browser

```bash
# تثبيت المفاتيح والمستودعات
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg \
  https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg

# إضافة المستودع
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] \
  https://brave-browser-apt-release.s3.brave.com/ stable main" | \
  sudo tee /etc/apt/sources.list.d/brave-browser-release.list

# تحديث وتثبيت Brave
sudo apt update
sudo apt install -y brave-browser

# التحقق من التثبيت
brave-browser --version
```

---

## 6️⃣ تثبيت Xvfb (Virtual Display)

```bash
# Xvfb لتشغيل المتصفح بدون شاشة حقيقية
sudo apt install -y xvfb

# تثبيت الخطوط (لعرض النصوص بشكل صحيح)
sudo apt install -y fonts-liberation fonts-dejavu-core \
  fonts-noto-color-emoji xfonts-base xfonts-100dpi xfonts-75dpi \
  xfonts-scalable xfonts-cyrillic

# تثبيت مكتبات إضافية
sudo apt install -y libnss3 libgconf-2-4 libxss1 libasound2
```

---

## 7️⃣ استنساخ المشروع

```bash
# الانتقال للمجلد الرئيسي
cd ~

# استنساخ المشروع من GitHub
git clone https://github.com/Tariq990/player-youtube.git

# الدخول للمشروع
cd player-youtube

# التحقق من الملفات
ls -la
```

---

## 8️⃣ تثبيت متطلبات Python

```bash
# إنشاء بيئة افتراضية
python3.13 -m venv venv

# تفعيل البيئة
source venv/bin/activate

# تثبيت المتطلبات
pip install --upgrade pip
pip install -r requirements.txt

# التحقق من التثبيت
pip list
```

---

## 9️⃣ رفع ملفات Cookies

```bash
# طريقة 1: نسخ من جهازك (من Windows PowerShell)
scp "C:\Users\tarik\Desktop\youtube player\data\cookies.json" root@YOUR_VPS_IP:~/player-youtube/data/

# طريقة 2: تعديل مباشرة على السيرفر
nano data/cookies.json
# الصق محتوى ملف cookies.json
# اضغط Ctrl+O للحفظ، ثم Ctrl+X للخروج
```

---

## 🔟 ضبط الإعدادات

```bash
# تعديل config.json
nano config/config.json

# تأكد من:
# "USE_HEADLESS": true
# "MAX_WINDOWS": 4  (أو 2 إذا كان RAM محدود)

# حفظ: Ctrl+O ثم Enter
# خروج: Ctrl+X
```

---

## 1️⃣1️⃣ اختبار التشغيل

```bash
# تفعيل البيئة الافتراضية (إذا لم تكن مفعلة)
source venv/bin/activate

# اختبار بسيط
xvfb-run -a python3.13 src/app.py

# إذا عمل بنجاح، توقفه بـ Ctrl+C
```

---

## 1️⃣2️⃣ تشغيل تلقائي بـ systemd (للعمل 24/7)

```bash
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/youtube-player.service
```

**الصق هذا المحتوى:**

```ini
[Unit]
Description=YouTube Player Auto-View Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/player-youtube
Environment="DISPLAY=:99"
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 &
ExecStart=/root/player-youtube/venv/bin/python3.13 /root/player-youtube/src/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**حفظ وإغلاق** (Ctrl+O ثم Enter ثم Ctrl+X)

```bash
# تحميل الخدمة
sudo systemctl daemon-reload

# تفعيل التشغيل التلقائي عند بدء السيرفر
sudo systemctl enable youtube-player

# بدء الخدمة
sudo systemctl start youtube-player

# التحقق من الحالة
sudo systemctl status youtube-player

# مشاهدة السجلات (logs) مباشرة
sudo journalctl -u youtube-player -f
```

---

## 🔧 أوامر مفيدة للإدارة

```bash
# إيقاف الخدمة
sudo systemctl stop youtube-player

# إعادة تشغيل
sudo systemctl restart youtube-player

# مشاهدة السجلات (آخر 100 سطر)
sudo journalctl -u youtube-player -n 100

# مشاهدة السجلات المباشرة
sudo journalctl -u youtube-player -f

# إلغاء التشغيل التلقائي
sudo systemctl disable youtube-player

# تحديث المشروع من GitHub
cd ~/player-youtube
git pull origin main
sudo systemctl restart youtube-player
```

---

## 📊 مراقبة الأداء

```bash
# استهلاك RAM و CPU
htop

# أو
top

# مساحة القرص
df -h

# عمليات Brave
ps aux | grep brave

# عدد المتصفحات النشطة
pgrep -c brave
```

---

## 🔒 نصائح الأمان

```bash
# 1. إنشاء مستخدم غير root (أكثر أماناً)
adduser youtube
usermod -aG sudo youtube

# 2. تعطيل تسجيل الدخول root عبر SSH
sudo nano /etc/ssh/sshd_config
# غيّر: PermitRootLogin yes
# إلى: PermitRootLogin no
sudo systemctl restart ssh

# 3. تثبيت جدار ناري
sudo apt install -y ufw
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## ❓ حل المشاكل الشائعة

### مشكلة: Brave لا يعمل في headless
```bash
# تثبيت مكتبات إضافية
sudo apt install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
  libgbm1 libpango-1.0-0 libcairo2 libasound2
```

### مشكلة: نفذ RAM
```bash
# تقليل عدد العمال
nano config/config.json
# غيّر "MAX_WINDOWS": 2  (بدل 4)

# إعادة تشغيل
sudo systemctl restart youtube-player
```

### مشكلة: السكريبت يتوقف بعد فترة
```bash
# التحقق من السجلات
sudo journalctl -u youtube-player -n 200

# زيادة الذاكرة المؤقتة (swap)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🎉 جاهز!

الآن مشروعك يعمل 24/7 على Ubuntu Server!

- ✅ يشتغل في الخلفية بدون توقف
- ✅ يعيد التشغيل تلقائياً عند حدوث خطأ
- ✅ يبدأ تلقائياً عند إعادة تشغيل السيرفر
- ✅ Headless mode (مخفي، لا توجد نوافذ)

**للوصول للسجلات:**
```bash
ssh root@YOUR_VPS_IP
sudo journalctl -u youtube-player -f
```
