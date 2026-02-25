import os
import subprocess
import shutil

def setup():
    # تنظيف البيئة قبل البدء لضمان عدم وجود ملفات قديمة
    if os.path.exists("vendor"): shutil.rmtree("vendor")
    if os.path.exists("vendor_assets.zip"): os.remove("vendor_assets.zip")
    
    os.makedirs("vendor/python", exist_ok=True)
    os.makedirs("vendor/browsers", exist_ok=True)
    
    print("⏳ جاري تجهيز بيئة البناء (Wheel & Setuptools)...")
    subprocess.run(["pip", "install", "wheel", "setuptools", "--target", "vendor/python"])

    # قائمة المكتبات المطلوبة
    libs = [
        "playwright", 
        "camoufox", 
        "orjson", 
        "manim",      
        "edge-tts", 
        "mutagen", 
        "arabic-reshaper", 
        "python-bidi"
    ]
    
    print("🚀 جاري تحميل المكتبات (استخدام النسخ الجاهزة Binary لتوفير الوقت)...")
    # إضافة --prefer-binary تجعل pip يبحث عن نسخ محملة مسبقاً بدلاً من محاولة بناء manim من الصفر
    # مما يقلل فرص حدوث أخطاء Compile بشكل كبير
    subprocess.run([
        "pip", "install", 
        "--prefer-binary", 
        *libs, 
        "--target", "vendor/python"
    ])
    
    print("🌐 جاري تحميل محركات المتصفحات (Chromium & Camoufox)...")
    # ضبط المسار ليكون داخل مجلد الترسانة حصراً
    target_browser_path = os.path.abspath("vendor/browsers")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = target_browser_path
    
    # تثبيت المتصفحات المطلوبة
    subprocess.run(["python3", "-m", "playwright", "install", "chromium"])
    subprocess.run(["python3", "-m", "camoufox", "fetch"])

    print("📦 جاري ضغط الترسانة (حجم الملف المتوقع > 200MB)...")
    # الضغط بصيغة zip ليتم رفعه لاحقاً كـ Release
    shutil.make_archive("vendor_assets", 'zip', "vendor")
    
    # تنظيف المجلد الأصلي لتوفير مساحة في الـ Runner
    shutil.rmtree("vendor")
    print("✅ تم إنشاء vendor_assets.zip بنجاح وجاهز للرفع إلى Release!")

if __name__ == "__main__":
    setup()
