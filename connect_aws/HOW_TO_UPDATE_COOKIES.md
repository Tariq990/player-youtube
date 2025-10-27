# 🔄 تحديث الكوكيز أثناء التشغيل

## ✅ **الجواب: لا تحتاج إيقاف السيرفر!**

التطبيق يحتوي على **Cookie Watcher** يراقب ملف `cookies.json` تلقائياً.

---

## 📋 **كيف يعمل Auto-Reload:**

عندما تضيف كوكيز جديدة:

1. ✅ **ترفع الملف الجديد** من جهازك
2. ✅ **Cookie Watcher يكتشف التغيير** خلال ثانيتين
3. ✅ **يعيد تحميل الكوكيز تلقائياً** بدون إيقاف
4. ✅ **التطبيق يستمر بالعمل** مع الكوكيز الجديدة

**في السجلات راح تشوف:**
```
🔄 Cookies reloaded: 5 active sets
```

---

## 🚀 **خطوات التحديث:**

### **الطريقة 1: استخدام الملف الجاهز (الأسهل)**

1. احفظ كوكيز جديدة في:
   ```
   C:\Users\tarik\Desktop\youtube player\data\cookies.json
   ```

2. دبل كليك على:
   ```
   connect_aws\update_cookies.bat
   ```

3. انتهى! السيرفر راح يحدّث الكوكيز تلقائياً ✅

---

### **الطريقة 2: يدوياً (PowerShell)**

```powershell
scp -i "C:\Users\tarik\Desktop\meeee.pem" "C:\Users\tarik\Desktop\youtube player\data\cookies.json" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com:~/player-youtube/data/
```

---

## 🔍 **التحقق من التحديث:**

في نافذة SSH على السيرفر، راقب السجلات:

```bash
# إذا التطبيق شغّال كخدمة systemd
sudo journalctl -u youtube-player -f

# إذا شغّال في الطرفية مباشرة
# راح تشوف الرسالة في نفس النافذة
```

**راح تشوف:**
```
🔄 Cookies reloaded: 5 active sets
```

---

## ⚠️ **متى تحتاج إعادة تشغيل؟**

**لا تحتاج إعادة تشغيل عند:**
- ✅ إضافة كوكيز جديدة
- ✅ تعديل كوكيز موجودة
- ✅ حذف كوكيز

**تحتاج إعادة تشغيل فقط عند:**
- ⚠️ تغيير `config.json` (مثل MAX_WINDOWS)
- ⚠️ تحديث الكود من GitHub
- ⚠️ تثبيت مكتبات جديدة

---

## 🎯 **مثال عملي:**

```cmd
REM 1. احفظ كوكيز جديدة (من Brave Browser)
python scripts\save_cookies.py

REM 2. ارفع للسيرفر
connect_aws\update_cookies.bat

REM 3. انتهى! السيرفر راح يستخدم الكوكيز الجديدة تلقائياً
```

---

## 💡 **نصيحة:**

احفظ `update_cookies.bat` في المفضلة، لأنك راح تستخدمه كثير! 😊
