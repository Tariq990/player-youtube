# 🔐 نقل الكوكيز بين الأجهزة

## 📋 الهدف
حفظ الكوكيز والـ User-Agent من جهاز واحد واستخدامها على أي جهاز آخر **بدون الحاجة لتسجيل الدخول مرة أخرى**.

---

## 🖥️ الجهاز الأول (حفظ الكوكيز)

### 1. تشغيل سكريبت الحفظ:
```bash
python scripts\save_cookies.py
```

### 2. في متصفح Brave:
- سجل دخول لحساب YouTube
- تأكد من ظهور صورة البروفايل
- ارجع للـ Terminal واضغط Enter

### 3. الملفات المحفوظة:
بعد الحفظ ستجد:

```
data/
├── cookies.json                           # قاعدة البيانات الرئيسية
└── cookies_backup_20251026_223000.json    # نسخة محمولة 📦
```

**النسخة المحمولة** هي الملف المهم! يحتوي على:
- ✅ جميع الكوكيز (عادة 40-60 كوكي)
- ✅ User-Agent كامل
- ✅ بيانات المصادقة
- ✅ معلومات الحساب

---

## 📤 نقل الملف

### الطريقة 1: USB أو Cloud
```
1. انسخ الملف: cookies_backup_YYYYMMDD_HHMMSS.json
2. ضعه في USB أو Google Drive أو Dropbox
3. حمّله على الجهاز الجديد
```

### الطريقة 2: Email
```
1. أرسل الملف لنفسك عبر Email
2. حمّله على الجهاز الجديد
```

### ⚠️ تحذير أمني:
الملف يحتوي على **بيانات حساسة**! 
- ❌ لا تشاركه مع أحد
- ❌ لا ترفعه على GitHub
- ✅ احذفه بعد الاستيراد
- ✅ استخدم التشفير (الموجود في `.env`)

---

## 🖥️ الجهاز الثاني (استيراد الكوكيز)

### 1. إعداد المشروع:
```bash
# نفس الخطوات الأساسية
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# انسخ ملف .env أو أنشئ واحد جديد
copy .env.example .env
```

### 2. طريقة الاستيراد السريع:
```bash
# ضع الملف المنسوخ في مجلد data واسمه cookies.json
copy cookies_backup_20251026_223000.json data\cookies.json
```

### 3. طريقة الاستيراد المتقدم:
```bash
# استخدم السكريبت لدمج الكوكيز مع القديمة
python scripts\import_cookies.py cookies_backup_20251026_223000.json
```

### 4. اختبار الكوكيز:
```bash
python scripts\test_cookies.py
```

يجب أن ترى:
```
✅ Cookie authentication successful!
✅ User is logged in
✅ Profile avatar detected
```

### 5. تشغيل التطبيق:
```bash
python src\app.py
```

---

## 🔄 سيناريوهات الاستخدام

### السيناريو 1: جهاز كمبيوتر واحد
```
1. سجل دخول مرة واحدة
2. استخدم الكوكيز المحفوظة دائماً
3. لا حاجة لتسجيل دخول مرة أخرى
```

### السيناريو 2: عدة أجهزة (بيتي، عملي، لابتوب)
```
1. سجل دخول على جهاز واحد
2. انسخ ملف cookies_backup_*.json
3. استورده على جميع الأجهزة الأخرى
4. جميع الأجهزة تعمل بنفس الحساب
```

### السيناريو 3: عدة حسابات YouTube
```
1. سجل دخول للحساب الأول → احفظ
2. سجل خروج، ثم دخول للحساب الثاني → احفظ
3. الآن لديك cookies.json بحسابين
4. التطبيق سيستخدمهم بالتناوب (rotation)
```

---

## 📊 محتوى ملف الكوكيز

### مثال على الملف:
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "account_tag": "brave_browser_account",
    "source": "brave_selenium",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "cookies": [
      {
        "name": "LOGIN_INFO",
        "value": "AFmmF2swR...",
        "domain": ".youtube.com",
        "path": "/",
        "secure": true,
        "httpOnly": true
      },
      {
        "name": "__Secure-3PSID",
        "value": "g.a000...",
        "domain": ".google.com"
      }
      // ... 40-60 كوكي آخر
    ],
    "created_at": "2025-10-26T22:30:00",
    "status": "active",
    "usage_count": 0,
    "notes": "Saved from Brave browser with user login"
  }
]
```

### الكوكيز المهمة للمصادقة:
- `LOGIN_INFO` - معلومات تسجيل الدخول
- `__Secure-3PSID` - Session ID آمن
- `SID` - Session ID
- `SAPISID` - API Session ID
- `APISID` - API ID

---

## ⚙️ إعدادات متقدمة

### تشفير الكوكيز (موصى به):
في ملف `.env`:
```bash
ENCRYPTION_KEY=your-32-byte-base64-key-here
```

الكوكيز ستُشفر تلقائياً عند الحفظ!

### تعطيل التشفير (للاختبار فقط):
```bash
# اترك ENCRYPTION_KEY فارغ في .env
ENCRYPTION_KEY=
```

---

## 🐛 حل المشاكل

### المشكلة: "Cookies expired"
```
الحل:
1. سجل دخول مرة أخرى على الجهاز الأصلي
2. احفظ كوكيز جديدة
3. انقلها للأجهزة الأخرى
```

### المشكلة: "Not logged in"
```
الحل:
1. تأكد أن الملف cookies.json موجود في data/
2. تأكد أن User-Agent مطابق
3. جرب python scripts/test_cookies.py
```

### المشكلة: "Too many cookies"
```
الحل:
1. افتح data/cookies.json
2. احذف الكوكيز القديمة (ابقِ على آخر 2-3 فقط)
3. احفظ الملف
```

---

## ✅ التحقق من النجاح

بعد الاستيراد، شغّل:
```bash
python scripts\test_cookies.py
```

يجب أن ترى:
```
✅ Cookie authentication successful!
✅ User is logged in
✅ Profile avatar detected
✅ Browser will stay open for 5 seconds to verify
```

---

## 📝 ملاحظات مهمة

1. **صلاحية الكوكيز**: عادة تستمر لأسابيع/أشهر، لكن:
   - قد تنتهي إذا غيّرت كلمة المرور
   - قد تنتهي إذا سجلت خروج من YouTube
   
2. **الأمان**: 
   - الملف يساوي "تسجيل الدخول لحسابك"
   - لا تشاركه مع أحد أبداً
   - استخدم التشفير دائماً

3. **النسخ الاحتياطي**:
   - احتفظ بنسخة من الكوكيز في مكان آمن
   - إذا انتهت، سجل دخول واحفظ جديدة

---

## 🚀 الخلاصة

```bash
# الجهاز الأول (مرة واحدة)
python scripts\save_cookies.py  # → ينتج cookies_backup_*.json

# انسخ الملف للجهاز الثاني

# الجهاز الثاني (استيراد)
copy cookies_backup_*.json data\cookies.json

# اختبار
python scripts\test_cookies.py  # ✅ يجب أن ينجح

# تشغيل
python src\app.py  # 🎬 يعمل بدون تسجيل دخول!
```

**النتيجة**: جميع أجهزتك تستخدم نفس الكوكيز، لا حاجة لتسجيل الدخول في كل مرة! 🎉
