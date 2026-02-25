import asyncio
import sys
import json
import os
import shutil
import zipfile
import stat

# ==========================================================
# 1. نظام إدارة البيئة الذكية (Smart Environment Manager)
# ==========================================================
current_dir = os.getcwd()
zip_path = os.path.join(current_dir, "vendor_assets.zip")
extract_path = os.path.join(current_dir, "vendor_extracted")

def prepare_environment():
    """تجهيز البيئة سواء من الكاش أو من ملف Zip"""
    # الحالة أ: المجلد موجود مسبقاً (بفضل GitHub Actions Cache)
    if os.path.exists(extract_path):
        print("🚀 تم العثور على الترسانة جاهزة (عبر Cache)، جاري تخطي مرحلة الفك.")
        return True

    # الحالة ب: المجلد غير موجود ولكن ملف الـ Zip موجود (تحميل جديد من Release)
    if os.path.exists(zip_path):
        print("📦 مجلد الترسانة غير موجود، جاري الفك من vendor_assets.zip...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            print("🔑 جاري إصلاح صلاحيات الملفات التنفيذية...")
            for root, dirs, files in os.walk(extract_path):
                for name in files:
                    # منح صلاحية التنفيذ لملفات المتصفح و node
                    if any(key in name for key in ["node", "chrome", "firefox"]) or name.endswith(".sh"):
                        file_path = os.path.join(root, name)
                        try:
                            st = os.stat(file_path)
                            os.chmod(file_path, st.st_mode | stat.S_IEXEC)
                        except:
                            pass
            print("✅ تم فك الترسانة وتجهيز الصلاحيات بنجاح.")
            return True
        except Exception as e:
            print(f"❌ فشل فك ضغط الترسانة: {e}")
            return False

    # الحالة ج: لا يوجد كاش ولا يوجد ملف Zip
    print("❌ خطأ فادح: لم يتم العثور على المجلد المستخرج ولا ملف vendor_assets.zip!")
    return False

# تنفيذ التحقق من البيئة قبل أي استيراد للمكتبات الخارجية
if not prepare_environment():
    sys.exit(1)

# ==========================================================
# 2. حقن المسارات المخصصة (Path Redirection)
# ==========================================================
# حقن المكتبات (مجلد python) والمتصفحات (مجلد browsers)
vendor_python = os.path.join(extract_path, "python")
vendor_browsers = os.path.join(extract_path, "browsers")

if os.path.exists(vendor_python):
    sys.path.insert(0, vendor_python) 
    
if os.path.exists(vendor_browsers):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = vendor_browsers

# ==========================================================
# 3. الاستيراد الآمن لمحرك التخفي (Stealth Engine)
# ==========================================================
try:
    from camoufox.async_api import AsyncCamoufox
    print("✅ تم تحميل محرك Camoufox بنجاح.")
except ImportError as e:
    print(f"❌ خطأ فادح: المكتبات غير موجودة في المسار المحدد. {e}")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

# ==========================================================
# 4. المحرك الأساسي للأتمتة (Core Engine)
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🚀 بدء المهمة... السؤال: {prompt}")
    
    # استخدام المتصفح في وضع Headless مع إعدادات التخفي
    async with AsyncCamoufox(headless=True) as browser:
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # استعادة الجلسة عبر الكوكيز من إعدادات GitHub Secrets
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                await context.add_cookies(json.loads(cookies_json))
                print("✅ تم استعادة الجلسة (Cookies) بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()
        
        # حظر الصور والخطوط لتسريع العملية وتقليل استهلاك البيانات
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            print("⏳ جاري الدخول إلى Gemini...")
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # البحث عن مربع إدخال النص
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            print("✍️ كتابة السؤال وإرساله...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            print("📡 بانتظار الرد (مراقبة النمو)...")
            response_selector = ".model-response-text"
            
            # انتظار ظهور بداية الرد
            await page.wait_for_selector(response_selector, timeout=60000)
            
            previous_length = 0
            stable_checks = 0
            
            # حلقة لمراقبة استقرار النص (للتأكد من اكتمال الإجابة الطويلة)
            for i in range(40): 
                current_text = await page.evaluate(f'''() => {{
                    const res = document.querySelectorAll("{response_selector}");
                    return res.length > 0 ? res[res.length - 1].innerText : "";
                }}''')
                
                current_length = len(current_text)
                
                if current_length > previous_length:
                    print(f"✍️ Gemini يكتب... ({current_length} حرف)")
                    # تمرير تلقائي للأسفل لمواكبة النص
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    previous_length = current_length
                    stable_checks = 0 
                else:
                    stable_checks += 1
                
                # إذا استقر النص لـ 3 دورات فحص، نعتبره انتهى
                if stable_checks >= 3 and current_length > 0:
                    print("✅ توقف النص عن النمو، تم اكتمال الإجابة.")
                    break
                
                await asyncio.sleep(2)

            # استخراج النص النهائي
            final_text = await page.evaluate('''() => {
                const responses = document.querySelectorAll(".model-response-text");
                return responses.length > 0 ? responses[responses.length - 1].innerText : "فشل استخراج النص.";
            }''')

            output = {
                "status": "success",
                "prompt": prompt,
                "response": final_text
            }
            print("✅ المهمة اكتملت بنجاح.")

        except Exception as e:
            print(f"❌ خطأ تشغيلي: {str(e)}")
            # حفظ لقطة شاشة للخطأ للتشخيص
            await page.screenshot(path="error_debug.png")
            output = {"status": "error", "message": str(e)}

        # حفظ النتيجة النهائية في ملف JSON
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # الحصول على البرومبت من مدخلات GitHub Action
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hi Gemini"
    asyncio.run(run_gemini_automation(user_prompt))
