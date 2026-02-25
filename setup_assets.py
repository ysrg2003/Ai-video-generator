import os
import subprocess
import shutil

def setup():
    if os.path.exists("vendor"): shutil.rmtree("vendor")
    os.makedirs("vendor/python", exist_ok=True)
    os.makedirs("vendor/browsers", exist_ok=True)
    
    print("⏳ جاري تحميل الترسانة الكاملة...")
    
    # يفضل تثبيت wheel أولاً لمساعدة pip في البناء
    subprocess.run(["pip", "install", "wheel", "setuptools", "--target", "vendor/python"])

    libs = [
        "playwright", 
        "camoufox", 
        "orjson", 
        "manim",      # هنا قد تحدث المشكلة لو لم تثبت apt-get أعلاه
        "edge-tts", 
        "mutagen", 
        "arabic-reshaper", 
        "python-bidi"
    ]
    
    # استخدام --only-binary قد يساعد إذا أردت تجنب البناء، 
    # لكن في حالة Manim، التثبيت العادي مع وجود مكتبات النظام هو الأضمن.
    subprocess.run(["pip", "install", *libs, "--target", "vendor/python"])
    
    # تحميل المتصفح
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.abspath("vendor/browsers")
    subprocess.run(["python3", "-m", "playwright", "install", "chromium"])
    subprocess.run(["python3", "-m", "camoufox", "fetch"])

    print("📦 جاري ضغط المجلد...")
    shutil.make_archive("vendor_assets", 'zip', "vendor")
    shutil.rmtree("vendor")
    print("✅ تم إنشاء vendor_assets.zip بنجاح!")

if __name__ == "__main__":
    setup()
