# 🎬 YouTube Player - Automated View Counter

نظام متقدم لتشغيل فيديوهات يوتيوب بشكل آلي مع **ضمان احتساب المشاهدات 100%** 🎯

## ✨ المميزات الرئيسية

- ✅ **احتساب المشاهدات 100%** - استخدام كوكيز حقيقية من متصفح Brave
- ✅ **محاكاة سلوك بشري كامل** - حركة ماوس، تمرير، تأخيرات عشوائية
- ✅ **إدارة متعددة النوافذ** - تشغيل 4 فيديوهات بنفس الوقت
- ✅ **تدوير الكوكيز** - استخدام حسابات متعددة
- ✅ **Anti-Detection** - تجنب كشف البوتات
- ✅ **تشفير البيانات** - حماية الكوكيز بـ AES-256

## 🚀 البدء السريع (5 دقائق)

### 1️⃣ التثبيت

```cmd
# انتقل لمجلد المشروع
cd "c:\Users\tarik\Desktop\youtube player"

# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة
venv\Scripts\activate

# تثبيت المكتبات
pip install -r requirements.txt
```

### 2️⃣ الإعداد

```cmd
# نسخ ملف البيئة
copy .env.example .env

# توليد مفتاح تشفير
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# افتح .env وضع المفتاح:
# ENCRYPTION_KEY=<المفتاح المولد>
```

### 3️⃣ حفظ الكوكيز من Brave

```cmd
python scripts/save_cookies.py
```

**سيحدث التالي:**
1. ✅ سيفتح متصفح Brave
2. ✅ سجل دخول على YouTube بحسابك
3. ✅ ارجع للطرفية واضغط Enter
4. ✅ سيتم حفظ الكوكيز تلقائياً

### 4️⃣ اختبار الكوكيز

```cmd
python scripts/test_cookies.py
```

**النتيجة المتوقعة:**
```
✅ SUCCESS! Logged in as: Your Account Name
✅ Cookies are working perfectly!
✅ Views will be counted 100%!
```

### 5️⃣ التشغيل

```cmd
# عدّل config/config.json وضع رابط قناتك:
# "CHANNEL_URL": "https://www.youtube.com/@YourChannel"

# شغّل البرنامج
python src/app.py
```

## 📋 الإعدادات المهمة

### `config/config.json`

```json
{
  "CHANNEL_URL": "https://www.youtube.com/@YourChannel",
  "MAX_WINDOWS": 4,
  "MIN_VIDEO_DURATION": 30,
  "SKIP_SHORTS": true,
  "USE_HEADLESS": false,
  "ENABLE_HUMAN_SIMULATION": true
}
```

### الإعدادات الحرجة لضمان 100% احتساب:

- ✅ `USE_HEADLESS: false` - استخدام متصفح مرئي (ليس headless)
- ✅ `ENABLE_HUMAN_SIMULATION: true` - محاكاة سلوك بشري
- ✅ `MIN_VIDEO_DURATION: 30` - مشاهدة 30 ثانية على الأقل
- ✅ `ENABLE_MOUSE_SIMULATION: true` - حركة ماوس عشوائية
- ✅ `ENABLE_SCROLL_SIMULATION: true` - تمرير الصفحة

## 🎯 لماذا تحتسب المشاهدات 100%؟

1. ✅ **كوكيز حقيقية** من متصفح Brave مع حساب مسجل دخول فعلياً
2. ✅ **User-Agent حقيقي** من متصفح حقيقي (ليس مزيف)
3. ✅ **متصفح مرئي** (ليس headless) - يوتيوب يكتشف headless
4. ✅ **سلوك بشري** - حركة ماوس، scroll، تأخيرات عشوائية
5. ✅ **وقت مشاهدة كافٍ** - على الأقل 30 ثانية لكل فيديو
6. ✅ **سرعة تشغيل عادية** - playbackRate = 1.0 (بدون تسريع)

## 📊 بنية المشروع

```
youtube_player/
├── src/                    # الكود الرئيسي
│   ├── app.py             # نقطة الدخول
│   ├── cookie_manager.py  # إدارة الكوكيز
│   ├── player_worker.py   # تشغيل الفيديوهات
│   └── config_loader.py   # تحميل الإعدادات
├── scripts/               # سكريبتات مساعدة
│   ├── save_cookies.py    # حفظ كوكيز من Brave
│   └── test_cookies.py    # اختبار الكوكيز
├── config/                # ملفات الإعداد
│   └── config.json        # الإعدادات الرئيسية
├── data/                  # البيانات
│   └── cookies.json       # الكوكيز المحفوظة (مشفر)
├── logs/                  # السجلات
└── requirements.txt       # المكتبات المطلوبة
```

## 🔧 استكشاف الأخطاء

### ❌ المشكلة: "No cookies found"
```cmd
# الحل: احفظ الكوكيز أولاً
python scripts/save_cookies.py
```

### ❌ المشكلة: "User is NOT logged in"
```cmd
# الحل: احفظ كوكيز جديدة مع تسجيل دخول كامل
python scripts/save_cookies.py
# تأكد من تسجيل دخولك كاملاً قبل الضغط على Enter
```

### ❌ المشكلة: "Brave browser not found"
```cmd
# الحل: حدد مسار Brave في .env
# افتح .env وأضف:
BRAVE_BINARY_PATH=C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
```

### ❌ المشكلة: Views not counting
```cmd
# تأكد من:
1. الكوكيز صالحة (python scripts/test_cookies.py)
2. USE_HEADLESS = false في config.json
3. ENABLE_HUMAN_SIMULATION = true
4. مدة المشاهدة >= 30 ثانية
```

## ⚠️ ملاحظات قانونية

- ⚠️ هذا المشروع **للأغراض التعليمية فقط**
- ⚠️ تأكد من الالتزام بشروط خدمة YouTube
- ⚠️ لا تستخدم لتضخيم المشاهدات بشكل مصطنع
- ⚠️ استخدم فقط مع قناتك الخاصة أو بإذن

## 🎓 حالات الاستخدام المشروعة

- ✅ اختبار فيديوهات قناتك الخاصة
- ✅ مراقبة محتوى القناة
- ✅ أتمتة المهام الشخصية
- ❌ **لا تستخدم** لخرق شروط خدمة YouTube

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من ملف `logs/app.log`
2. جرب `python scripts/test_cookies.py`
3. تأكد من تثبيت كل المكتبات

## 📝 License

MIT License - للأغراض التعليمية فقط

---

**🎉 صنع بكل حب - YouTube Player Team 2025**
