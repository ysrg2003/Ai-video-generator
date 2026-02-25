import os
import subprocess
import shutil

def setup():
    if os.path.exists("vendor"): shutil.rmtree("vendor")
    os.makedirs("vendor/python", exist_ok=True)
    os.makedirs("vendor/browsers", exist_ok=True)
    
    print("⏳ جاري تحميل الترسانة الكاملة (فيديو + نصوص)...")
    
    # إضافة كل المكتبات اللازمة لإنتاج الفيديو
    libs = [
        "playwright", "camoufox", "orjson", 
        "manim", "edge-tts", "mutagen", 
        "arabic-reshaper", "python-bidi"
    ]
    
    # تحميل المكتبات داخل مجلد vendor/python
    subprocess.run(["pip", "install", *libs, "--target", "vendor/python"])
    
    # تحميل المتصفح وإعداده
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.abspath("vendor/browsers")
    subprocess.run(["python3", "-m", "playwright", "install", "chromium"])
    
    # ملاحظة: camoufox fetch قد لا يكون ضرورياً إذا تم تثبيت المتصفح عبر playwright
    # لكن سنبقيه لضمان عمل camoufox بشكل مستقر
    subprocess.run(["python3", "-m", "camoufox", "fetch"])

    print("📦 جاري ضغط المجلد (هذا الملف سيعيش للأبد)...")
    shutil.make_archive("vendor_assets", 'zip', "vendor")
    
    shutil.rmtree("vendor")
    print("✅ تم إنشاء vendor_assets.zip بنجاح!")

if __name__ == "__main__":
    setup()
