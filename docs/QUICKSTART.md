# 🚀 دليل البدء السريع

## نظرة عامة

هذا المشروع عبارة عن نظام احترافي لتشغيل فيديوهات YouTube بشكل آلي مع **ضمان احتساب المشاهدات 100%**.

### ✨ الميزات الرئيسية

- ✅ احتساب مشاهدات 100% باستخدام كوكيز حقيقية
- ✅ محاكاة سلوك بشري كامل (حركة ماوس، scroll، تأخيرات عشوائية)
- ✅ دعم Brave Browser الكامل
- ✅ إدارة متعددة النوافذ (حتى 4 نوافذ متزامنة)
- ✅ نظام logging محترف
- ✅ تشفير AES-256 للبيانات الحساسة
- ✅ معالجة أخطاء شاملة

---

## 📋 المتطلبات

### نظام التشغيل
- Windows 10/11
- Python 3.7 أو أحدث
- Brave Browser

### المكتبات المطلوبة
يتم تثبيتها تلقائياً من `requirements.txt`

---

## ⚡ البدء السريع (5 دقائق)

### 1️⃣ التثبيت الأولي

افتح Command Prompt (cmd) وشغّل:

```cmd
cd "c:\Users\tarik\Desktop\youtube player"

REM إنشاء بيئة افتراضية
python -m venv venv

REM تفعيل البيئة
venv\Scripts\activate

REM تثبيت المكتبات
pip install -r requirements.txt
```

### 2️⃣ إعداد ملف البيئة (.env)

#### أ) إنشاء مفتاح التشفير

```cmd
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

انسخ المفتاح الناتج (سيبدو مثل: `gAAAAAB...`)

#### ب) إنشاء ملف .env

```cmd
copy .env.example .env
notepad .env
```

ضع المفتاح في السطر:
```ini
ENCRYPTION_KEY=<المفتاح_المنسوخ>
BRAVE_BINARY_PATH=C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
```

احفظ الملف واخرج

### 3️⃣ حفظ الكوكيز من Brave

```cmd
python scripts\save_cookies.py
```

**ماذا سيحدث:**
1. سيفتح متصفح Brave تلقائياً
2. انتقل إلى YouTube.com
3. سجّل دخول بحسابك الكامل
4. تأكد من ظهور صورة حسابك (avatar)
5. ارجع للـ Terminal واضغط **Enter**

**النتيجة المتوقعة:**
```
✅ Cookies saved successfully
🔑 Important cookies found: LOGIN_INFO, __Secure-3PSID
```

### 4️⃣ اختبار الكوكيز

```cmd
python scripts\test_cookies.py
```

**النتيجة المتوقعة:**
```
✅ SUCCESS! Logged in as: اسم_حسابك
✅ Cookies are working perfectly!
✅ Views will be counted 100%!
```

إذا رأيت هذه الرسالة → الكوكيز تعمل بشكل صحيح ✅

### 5️⃣ تعديل الإعدادات

افتح `config\config.json` وعدّل:

```json
{
  "CHANNEL_URL": "https://www.youtube.com/@اسم_قناتك_هنا",
  "MAX_WINDOWS": 2,
  "USE_HEADLESS": false,
  "ENABLE_HUMAN_SIMULATION": true,
  "MIN_VIDEO_DURATION": 30
}
```

**⚠️ مهم جداً:**
- `USE_HEADLESS: false` - لا تستخدم headless (ضروري لاحتساب المشاهدات)
- `ENABLE_HUMAN_SIMULATION: true` - فعّل المحاكاة البشرية

### 6️⃣ تشغيل المشروع

```cmd
python src\app.py
```

---

## 🎯 ضمان احتساب المشاهدات 100%

### الشروط الواجب توفرها:

| الشرط | القيمة | الأهمية |
|-------|--------|---------|
| **USE_HEADLESS** | `false` | 🔴 حرج |
| **ENABLE_HUMAN_SIMULATION** | `true` | 🔴 حرج |
| **MIN_VIDEO_DURATION** | `≥ 30` ثانية | 🟡 مهم |
| **كوكيز حقيقية** | من Brave | 🔴 حرج |
| **User-Agent حقيقي** | من Brave | 🟡 مهم |

---

## 🔧 استكشاف الأخطاء وحلها

### ❌ "No cookies found"

**السبب:** لم يتم حفظ الكوكيز

**الحل:**
```cmd
python scripts\save_cookies.py
```

---

### ❌ "Brave browser not found"

**السبب:** لم يتم العثور على Brave

**الحل:**  
افتح `.env` وحدد المسار الصحيح:
```ini
BRAVE_BINARY_PATH=C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
```

---

### ❌ "User is NOT logged in"

**السبب:** الكوكيز منتهية أو غير صحيحة

**الحل:**
```cmd
REM احفظ كوكيز جديدة
python scripts\save_cookies.py

REM تأكد من تسجيل الدخول الكامل قبل الضغط على Enter
```

---

### ❌ "yt-dlp not found"

**السبب:** لم يتم تثبيت yt-dlp

**الحل:**
```cmd
pip install yt-dlp
```

---

### ❌ الفيديو لا يشتغل

**الحلول المحتملة:**

1. **تحقق من الإعدادات:**
   ```json
   "USE_HEADLESS": false
   ```

2. **اختبر الكوكيز:**
   ```cmd
   python scripts\test_cookies.py
   ```

3. **تحقق من الاتصال بالإنترنت**

4. **شاهد ملف اللوج:**
   ```cmd
   type logs\app.log
   ```

---

## 📞 الأوامر المفيدة

```cmd
REM تفعيل البيئة الافتراضية
venv\Scripts\activate

REM حفظ كوكيز جديدة
python scripts\save_cookies.py

REM اختبار الكوكيز
python scripts\test_cookies.py

REM تجربة سريعة (فيديو واحد)
python scripts\quick_test.py

REM التشغيل الكامل
python src\app.py

REM مشاهدة اللوقات
type logs\app.log

REM مسح قاعدة البيانات (إعادة تشغيل)
del data\seen_videos.sqlite
```

---

## 📊 بنية المشروع

```
youtube_player/
├── src/                       # الكود الرئيسي
│   ├── app.py                # نقطة الدخول
│   ├── config_loader.py      # تحميل الإعدادات
│   ├── cookie_manager.py     # إدارة الكوكيز
│   ├── player_worker.py      # تشغيل الفيديوهات
│   ├── video_fetcher.py      # جلب الفيديوهات
│   ├── persistence.py        # قاعدة البيانات
│   ├── logger_config.py      # نظام اللوقات
│   ├── constants.py          # الثوابت
│   └── exceptions.py         # الأخطاء المخصصة
│
├── scripts/                   # سكريبتات مساعدة
│   ├── save_cookies.py       # حفظ الكوكيز
│   ├── test_cookies.py       # اختبار الكوكيز
│   └── quick_test.py         # تجربة سريعة
│
├── config/                    # الإعدادات
│   └── config.json
│
├── data/                      # البيانات
│   └── cookies.json          # (مشفر)
│
├── logs/                      # السجلات
│   └── app.log
│
├── .env                       # المتغيرات البيئية
├── requirements.txt           # المكتبات
└── README.md                  # التوثيق الكامل
```

---

## ⚠️ ملاحظات قانونية

- استخدم هذا المشروع فقط مع قناتك الخاصة
- لا تستخدمه لتضخيم المشاهدات بشكل مصطنع
- تأكد من الالتزام بشروط خدمة YouTube
- هذا المشروع للأغراض التعليمية فقط

---

## 🎓 المزيد من المعلومات

- اقرأ `README.md` للتوثيق الكامل
- راجع `youtube_playback_algorithm.md` لفهم الخوارزمية
- تحقق من ملفات `logs/` لمتابعة الأداء

---

✅ **جاهز الآن! ابدأ باتباع الخطوات أعلاه**
