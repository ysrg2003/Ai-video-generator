import os
import subprocess
import shutil

def setup():
    # تنظيف أي محاولات سابقة
    if os.path.exists("vendor"): shutil.rmtree("vendor")
    
    os.makedirs("vendor/python", exist_ok=True)
    os.makedirs("vendor/browsers", exist_ok=True)
    
    print("⏳ جاري تحميل المكتبات والمتصفح...")
    # 1. تحميل المكتبات
    subprocess.run(["pip", "install", "playwright", "camoufox", "--target", "vendor/python"])
    
    # 2. تحميل المتصفح
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "vendor/browsers"
    subprocess.run(["python3", "-m", "playwright", "install", "chromium"])
    subprocess.run(["python3", "-m", "camoufox", "fetch"])

    print("📦 جاري ضغط المجلد لتجاوز حدود GitHub...")
    # ضغط المجلد بالكامل في ملف واحد
    shutil.make_archive("vendor_assets", 'zip', "vendor")
    
    # مسح المجلد الأصلي ليبقى ملف الـ Zip فقط
    shutil.rmtree("vendor")
    print("✅ تم إنشاء vendor_assets.zip بنجاح!")

if __name__ == "__main__":
    setup()
