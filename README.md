# 🎬 YouTube Player

نظام احترافي لتشغيل فيديوهات YouTube بشكل آلي مع **ضمان احتساب المشاهدات 100%**.

## 🚀 البدء السريع

### استخدم السكريبت التفاعلي:
```cmd
start.bat
```

### أو اتبع الخطوات اليدوية:

```cmd
# 1. إنشاء البيئة الافتراضية
python -m venv venv
venv\Scripts\activate

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. إعداد ملف .env
copy .env.example .env
# عدّل .env وضع ENCRYPTION_KEY

# 4. حفظ الكوكيز من Brave
python scripts\save_cookies.py

# 5. اختبار الكوكيز
python scripts\test_cookies.py

# 6. التشغيل
python src\app.py
```

## 📚 التوثيق الكامل

- **[دليل البدء السريع](docs/QUICKSTART.md)** - ابدأ في 5 دقائق
- **[التوثيق الكامل](docs/README.md)** - شرح تفصيلي
- **[بنية المشروع](docs/PROJECT_STRUCTURE.md)** - هيكل الملفات
- **[الخوارزمية التقنية](docs/ARCHITECTURE.md)** - التفاصيل الفنية
- **[التحسينات الأخيرة](docs/IMPROVEMENTS.md)** - آخر التحديثات ✨
- **[نقل الكوكيز بين الأجهزة](docs/COOKIE_TRANSFER.md)** - استخدام نفس الحساب على أجهزة متعددة 🔐
- **[التوثيق التقني](docs/ARCHITECTURE.md)** - الخوارزمية والتصميم

## ✨ الميزات

- ✅ احتساب مشاهدات 100%
- ✅ محاكاة سلوك بشري
- ✅ دعم Brave Browser
- ✅ تشفير AES-256
- ✅ Logging محترف

## ⚠️ ملاحظة قانونية

هذا المشروع للأغراض التعليمية فقط. استخدمه فقط مع قناتك الخاصة.

---

**المزيد من المعلومات في مجلد [docs/](docs/)**
