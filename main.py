import asyncio
import sys
import json
import os
import shutil
import zipfile
import stat

# ==========================================================
# 1. نظام إدارة المسارات الذكي (Arsenal Integration)
# ==========================================================
# ملاحظة: في GitHub Actions، الترسانة تُفك الآن في المجلد الرئيسي مباشرة
current_dir = os.getcwd()

# المسارات المباشرة للمكتبات والمتصفحات بعد فك الترسانة بواسطة الأكشن
vendor_python = os.path.join(current_dir, "python")
vendor_browsers = os.path.join(current_dir, "browsers")

# ميزة: التحقق والربط التلقائي بالمكتبات (Persistence)
if os.path.exists(vendor_python):
    sys.path.insert(0, vendor_python)
    print(f"✅ تم ربط مكتبات الترسانة بنجاح من المسار: {vendor_python}")
else:
    print(f"⚠️ تنبيه: لم يتم العثور على مجلد 'python' في {current_dir}")

# ميزة: توجيه Playwright لاستخدام المتصفحات الموجودة في الترسانة
if os.path.exists(vendor_browsers):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = vendor_browsers
    print(f"✅ تم توجيه المحرك لمتصفحات الترسانة: {vendor_browsers}")
    
    # ميزة: تأمين صلاحيات التنفيذ للمحركات (Double-Check Permissions)
    # لضمان عدم حدوث Permission Denied حتى لو فك الأكشن الضغط بشكل غير كامل الصلاحيات
    for root, dirs, files in os.walk(vendor_browsers):
        for name in files:
            if "chrome" in name or "firefox" in name or "node" in name or name.endswith(".sh"):
                file_path = os.path.join(root, name)
                try:
                    st = os.stat(file_path)
                    os.chmod(file_path, st.st_mode | stat.S_IEXEC)
                except:
                    pass

# ==========================================================
# 2. الاستيراد الآمن لمحرك التخفي (Stealth Engine)
# ==========================================================
try:
    from camoufox.async_api import AsyncCamoufox
    print("✅ تم استيراد محرك Camoufox بنجاح.")
except ImportError as e:
    print(f"❌ خطأ فادح: فشل الوصول للمكتبات (Camoufox). تأكد من وجود ملف vendor_assets.zip وفكه بنجاح. {e}")
    sys.exit(1)

GEMINI_URL = "https://gemini.google.com/app"

# ==========================================================
# 3. المحرك الأساسي للأتمتة والذكاء (Core Engine)
# ==========================================================
async def run_gemini_automation(prompt):
    print(f"🚀 بدء المهمة العملاقة... السؤال: {prompt}")
    
    # ميزة: التخفي الكامل (Stealth Mode) عبر Camoufox
    # نستخدم المتصفح في وضع headless للعمل داخل السيرفرات
    async with AsyncCamoufox(headless=True) as browser:
        
        # ميزة: بصمة جهاز حقيقية (Fingerprinting) لمحاكاة البشر وتجنب الحظر
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        # ميزة: تجاوز تسجيل الدخول (Session Persistence) عبر الكوكيز
        cookies_json = os.getenv("GEMINI_COOKIES")
        if cookies_json:
            try:
                # الكوكيز غالباً ما تكون مصفوفة JSON
                loaded_cookies = json.loads(cookies_json)
                await context.add_cookies(loaded_cookies)
                print("✅ تم استعادة الجلسة (Cookies) بنجاح.")
            except Exception as e:
                print(f"⚠️ فشل تحميل الكوكيز: {e}")

        page = await context.new_page()

        # ميزة صواريخ السرعة (Turbo Speed): حظر الصور والخطوط لتقليل استهلاك الرام والوقت
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,woff,woff2,ttf}", lambda route: route.abort())
        
        try:
            print("⏳ جاري الدخول إلى Gemini...")
            # ميزة: الانتظار السريع لهيكل الصفحة (DOM) فقط دون انتظار الصور الثقيلة
            await page.goto(GEMINI_URL, wait_until="domcontentloaded", timeout=60000)

            # ميزة: المحدد الذكي (Smart Selector) لمربع النص الخاص بجيمناي
            input_selector = "div[role='textbox'], [contenteditable='true']"
            await page.wait_for_selector(input_selector, timeout=30000)
            
            print("✍️ كتابة السؤال وإرساله...")
            await page.fill(input_selector, prompt)
            await page.keyboard.press("Enter")
            
            # --- ميزة: مراقب التدفق والتمرير الذكي (Streaming & Auto-Scroll) ---
            print("📡 بانتظار الرد (مراقبة النمو + التمرير التلقائي)...")
            response_selector = ".model-response-text"
            
            # ننتظر ظهور أول إشارة لاستجابة الموديل
            await page.wait_for_selector(response_selector, timeout=60000)
            
            previous_length = 0
            stable_checks = 0
            
            # حلقة مراقبة الردود (تتعامل مع الردود الطويلة جداً التي تستغرق وقتاً في الكتابة)
            for i in range(50): 
                # استخراج النص الحالي للمشهد الأخير (الرد الأحدث)
                current_text = await page.evaluate(f'''() => {{
                    const res = document.querySelectorAll("{response_selector}");
                    return res.length > 0 ? res[res.length - 1].innerText : "";
                }}''')
                
                current_length = len(current_text)
                
                if current_length > previous_length:
                    print(f"✍️ Gemini يكتب... ({current_length} حرف)")
                    
                    # ميزة الـ Scroll التلقائي لضمان بقاء المحتوى في نطاق "الرؤية" برمجياً
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    
                    previous_length = current_length
                    stable_checks = 0 # إعادة تصفير العداد لأن النص ما زال ينمو
                else:
                    stable_checks += 1
                
                # إذا استقر طول النص لـ 4 فحوصات (8 ثوانٍ)، نعتبر أن Gemini انتهى تماماً
                if stable_checks >= 4 and current_length > 0:
                    print("✅ توقف النص عن النمو، تم اكتمال الإجابة.")
                    break
                
                await asyncio.sleep(2)

            # ميزة: استخراج النص النهائي بدقة (Deep Scrape)
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
            # ميزة: التقاط صورة للمتصفح عند الخطأ للتشخيص (Debug Screenshot)
            await page.screenshot(path="error_debug_gemini.png")
            output = {"status": "error", "message": str(e), "trace": "راجع screenshot لبيان الحالة"}

        # ميزة: حفظ النتيجة بتنسيق JSON مهيكل ليكون مدخلاً لمراحل الفيديو التالية
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # استلام السؤال من الوسائط المرسلة عبر GitHub Action
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hi Gemini"
    asyncio.run(run_gemini_automation(user_prompt))
