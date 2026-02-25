import asyncio
import sys
import json
import os
import zipfile
import stat
import re
import logging
import shutil
from datetime import datetime

# ==========================================================
# 0. نظام التسجيل والمراقبة (Industrial Logging)
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("GeminiFactory")

# ==========================================================
# 1. مدير الترسانة (Arsenal & Environment Manager)
# ==========================================================
class ArsenalManager:
    """المسؤول عن إعداد بيئة التشغيل السحابية وضمان عمل المكتبات"""
    def __init__(self):
        self.cwd = os.getcwd()
        self.zip_path = os.path.join(self.cwd, "vendor_assets.zip")
        self.extract_path = os.path.join(self.cwd, "vendor_extracted")
        self.python_dir = os.path.join(self.extract_path, "python")
        self.browsers_dir = os.path.join(self.extract_path, "browsers")

    def deploy(self):
        """تشغيل الترسانة: فك، إصلاح، وحقن مسارات"""
        if os.path.exists(self.extract_path):
            logger.info("🚀 تم العثور على الترسانة جاهزة في الكاش.")
            return self._activate()

        if not os.path.exists(self.zip_path):
            logger.error("❌ ملف vendor_assets.zip مفقود!")
            return False

        try:
            logger.info("📦 جاري فك الترسانة الكبرى (هذه العملية تحدث مرة واحدة)...")
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                z.extractall(self.extract_path)
            
            self._fix_binary_permissions()
            return self._activate()
        except Exception as e:
            logger.error(f"❌ فشل نشر الترسانة: {e}")
            return False

    def _fix_binary_permissions(self):
        """منح صلاحيات التنفيذ لـ Node و Chromium وكافة السكربتات"""
        logger.info("🔑 إصلاح صلاحيات الملفات الثنائية (Execution Bits)...")
        exec_keywords = ["node", "chrome", "firefox", "ffmpeg", "manim"]
        for root, _, files in os.walk(self.extract_path):
            for name in files:
                if any(key in name for key in exec_keywords) or name.endswith(".sh"):
                    fpath = os.path.join(root, name)
                    os.chmod(fpath, os.stat(fpath).st_mode | stat.S_IEXEC)

    def _activate(self):
        """حقن المسارات في ذاكرة النظام الحالية"""
        if os.path.exists(self.python_dir):
            sys.path.insert(0, self.python_dir)
            os.environ["PYTHONPATH"] = f"{self.python_dir}:{os.environ.get('PYTHONPATH', '')}"
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = self.browsers_dir
            logger.info("✅ تم تفعيل المسارات بنجاح.")
            return True
        return False

# ==========================================================
# 2. مهندس الأتمتة (Gemini Automation Engine)
# ==========================================================
class GeminiAutomator:
    """المحرك المسؤول عن استخراج المعرفة من Gemini بصيغة برمجية"""
    def __init__(self):
        self.endpoint = "https://gemini.google.com/app"
        self.output_file = "result.json"

    def _build_system_prompt(self, user_query):
        """تغليف طلب المستخدم ببروتوكول صارم لضمان مخرجات JSON"""
        return f"""
        Objective: Generate a Manim-compatible educational video script.
        Topic: {user_query}
        Language: Arabic
        
        Strict JSON Output Required (Array of Objects):
        [
          {{"text": "الجملة العربية هنا", "duration": 6}},
          {{"text": "الجملة التالية هنا", "duration": 5}}
        ]
        
        Rules:
        - Response must be ONLY the JSON array.
        - Duration should match reading speed (approx 2-3 words per second).
        - No markdown formatting or extra talk.
        """

    def _extract_clean_json(self, raw_text):
        """تنظيف الرد من أي شوائب نصية واستخراج مصفوفة JSON"""
        try:
            # البحث عن المصفوفة بين [ ]
            match = re.search(r'\[\s*{.*}\s*\]', raw_text, re.DOTALL)
            if match:
                return match.group(0)
            return raw_text
        except:
            return raw_text

    async def run(self, prompt):
        # استيراد Camoufox بعد تأمين البيئة
        from camoufox.async_api import AsyncCamoufox
        
        wrapped_prompt = self._build_system_prompt(prompt)
        logger.info(f"📡 إرسال المهمة لـ Gemini: {prompt}")

        async with AsyncCamoufox(headless=True) as browser:
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            
            # حقن الجلسة
            cookies = os.getenv("GEMINI_COOKIES")
            if cookies:
                await context.add_cookies(json.loads(cookies))
                logger.info("🍪 تم حقن ملفات التعريف.")

            page = await context.new_page()
            # حظر الصور لتوفير الوقت
            await page.route("**/*.{{png,jpg,jpeg,svg,gif,webp,woff,ttf}}", lambda r: r.abort())

            try:
                await page.goto(self.endpoint, wait_until="domcontentloaded", timeout=60000)
                
                selector = "div[role='textbox'], [contenteditable='true']"
                await page.wait_for_selector(selector)
                await page.fill(selector, wrapped_prompt)
                await page.keyboard.press("Enter")

                # مراقبة النمو الذكي (Smart Stability Monitor)
                response_sel = ".model-response-text"
                await page.wait_for_selector(response_selector=response_sel, timeout=60000)
                
                prev_len = 0
                stable_count = 0
                for _ in range(50): # مراقبة لمدة تصل لـ 100 ثانية
                    current_content = await page.evaluate(f'''() => {{
                        const nodes = document.querySelectorAll("{response_sel}");
                        return nodes.length > 0 ? nodes[nodes.length - 1].innerText : "";
                    }}''')
                    
                    if len(current_content) > prev_len:
                        logger.info(f"✍️ Gemini يولد المحتوى... ({len(current_content)} حرف)")
                        prev_len = len(current_content)
                        stable_count = 0
                    else:
                        stable_count += 1
                    
                    if stable_count >= 5 and prev_len > 0: # استقرار لـ 10 ثواني
                        break
                    await asyncio.sleep(2)

                final_raw = await page.evaluate(f'document.querySelectorAll("{response_sel}")[document.querySelectorAll("{response_sel}").length - 1].innerText')
                clean_json = self._extract_clean_json(final_raw)

                output = {
                    "status": "success",
                    "prompt": prompt,
                    "response": clean_json,
                    "generated_at": datetime.now().isoformat()
                }
                logger.info("✅ تم استلام الرد وتنظيفه بنجاح.")

            except Exception as e:
                logger.error(f"❌ خطأ أثناء المحاكاة: {e}")
                await page.screenshot(path="debug_crash.png")
                output = {"status": "error", "message": str(e)}

            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=4)

# ==========================================================
# 3. نقطة الانطلاق (The Orchestrator)
# ==========================================================
async def main():
    # 1. المرحلة السيادية: تجهيز الترسانة
    arsenal = ArsenalManager()
    if not arsenal.deploy():
        logger.critical("🚨 فشل تفعيل البيئة الحيوية. توقف النظام.")
        sys.exit(1)

    # 2. مرحلة الذكاء: تشغيل الأتمتة
    user_query = sys.argv[1] if len(sys.argv) > 1 else "مقدمة عن علوم الحاسوب"
    automator = GeminiAutomator()
    await automator.run(user_query)

if __name__ == "__main__":
    asyncio.run(main())
