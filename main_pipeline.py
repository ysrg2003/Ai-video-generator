import os
import sys
import json
import re
import asyncio
import stat
import shutil
import subprocess
import logging
from datetime import datetime

# ==========================================
# 0. نظام التسجيل وحقن البيئة (The Arsenal Core)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger("VideoFactory")

class ArsenalSystem:
    """المسؤول السيادي عن تفعيل الترسانة وربط الأدوات التنفيذية"""
    @staticmethod
    def activate():
        cwd = os.getcwd()
        extract_base = os.path.join(cwd, "vendor_extracted")
        v_python = os.path.join(extract_base, "python")
        v_bin = os.path.join(v_python, "bin")
        v_browsers = os.path.join(extract_base, "browsers")

        if os.path.exists(v_python):
            # 1. حقن المكتبات
            sys.path.insert(0, v_python)
            os.environ["PYTHONPATH"] = f"{v_python}:{os.environ.get('PYTHONPATH', '')}"
            
            # 2. حقن المسارات التنفيذية (FFmpeg & Manim)
            os.environ["PATH"] = f"{v_bin}:{os.environ.get('PATH', '')}"
            
            # 3. تفعيل المتصفحات
            if os.path.exists(v_browsers):
                os.environ["PLAYWRIGHT_BROWSERS_PATH"] = v_browsers
            
            # 4. إصلاح الصلاحيات (chmod +x)
            if os.path.exists(v_bin):
                for file in os.listdir(v_bin):
                    fpath = os.path.join(v_bin, file)
                    try:
                        os.chmod(fpath, os.stat(fpath).st_mode | stat.S_IEXEC)
                    except: pass
            
            logger.info("✅ تم تفعيل الترسانة: جميع المسارات والروابط التنفيذية جاهزة.")
            return True
        return False

# تفعيل البيئة قبل أي استيراد
ArsenalSystem.activate()

try:
    import edge_tts
    from mutagen.mp3 import MP3
    from manim import *
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError as e:
    logger.critical(f"🚨 خطأ في الترسانة: مكتبة أساسية مفقودة: {e}")

# ==========================================
# 1. مدير الأصول والبيانات (Asset & Logic Manager)
# ==========================================
class AssetManager:
    """المسؤول عن معالجة النصوص، الصوت، والبيانات الوسيطة"""
    def __init__(self, output_dir="production_assets"):
        self.output_dir = output_dir
        self._setup()

    def _setup(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def ar(text):
        """معالجة النصوص العربية لـ Manim"""
        if not text: return ""
        return get_display(arabic_reshaper.reshape(text))

    def load_and_clean_script(self, source="result.json"):
        """استخراج JSON نظيف من رد Gemini باستخدام التعبيرات النمطية"""
        logger.info(f"📖 جاري فحص ملف: {source}")
        try:
            with open(source, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                content = raw_data.get("response", str(raw_data))

            # البحث عن مصفوفة JSON [ ... ]
            json_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            if json_match:
                scenes = json.loads(json_match.group(0))
            else:
                # محاولة تنظيف الماركدوان يدوياً إذا فشل الريجيكس
                clean_txt = re.sub(r'```json|```', '', content).strip()
                scenes = json.loads(clean_txt)
            
            logger.info(f"🎯 تم استخراج {len(scenes)} مشهد بنجاح.")
            return scenes
        except Exception as e:
            logger.error(f"⚠️ فشل استخراج JSON: {e}. سيتم استخدام مشهد طوارئ.")
            return [{"text": "خطأ في معالجة البيانات من الذكاء الاصطناعي", "duration": 5}]

    async def build_audio_track(self, scenes):
        """توليد الصوت ومزامنة التوقيت لكل مشهد"""
        logger.info("🎙️ جاري بناء المسارات الصوتية (Neural TTS)...")
        for i, scene in enumerate(scenes):
            audio_path = os.path.join(self.output_dir, f"s_{i}.mp3")
            text = scene.get("text", "نص مفقود")
            
            # توليد الصوت
            communicate = edge_tts.Communicate(text, "ar-EG-SalmaNeural")
            await communicate.save(audio_path)
            
            # استخراج المدة الحقيقية للملف الصوتي
            audio_info = MP3(audio_path).info
            scene["duration"] = audio_info.length
            scene["audio_file"] = audio_path
        return scenes

# ==========================================
# 2. محرك الرندر السينمائي (Manim Cinematic Engine)
# ==========================================
class AIVideoProduction(MovingCameraScene):
    def construct(self):
        # تحميل البيانات التي تم إعدادها
        data_json = os.path.join("production_assets", "data.json")
        with open(data_json, "r") as f:
            scenes = json.load(f)

        # 1. إعداد الخلفية السينمائية
        bg = FullScreenRectangle().set_fill(
            LinearGradient(direction=DOWN, colors=["#0f0f10", "#000000"]), opacity=1
        )
        self.add(bg)

        # 2. تأثير حركة الكاميرا البطيئة (Dynamic Breathing)
        self.camera.frame.save_state()
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 + 0.02 * dt))

        current_vgroup = None

        for i, scene in enumerate(scenes):
            # تحضير النص
            raw_text = scene.get("text", "")
            display_text = AssetManager.ar(raw_text)
            
            # تصميم النص الاحترافي
            text_obj = Text(
                display_text, 
                font_size=40, 
                color=WHITE, 
                weight=BOLD
            ).set_stroke(BLACK, width=2, background=True)

            # إضافة "هالة" أو خلفية زجاجية للنص
            text_bg = RoundedRectangle(
                corner_radius=0.1,
                width=text_obj.width + 1,
                height=text_obj.height + 0.6
            ).set_fill(BLACK, opacity=0.3).set_stroke(WHITE, opacity=0.1)

            scene_group = VGroup(text_bg, text_obj)
            
            # تشغيل الصوت المتزامن
            self.add_sound(scene["audio_file"])

            # الأنيميشن (Smooth Morphing)
            if current_vgroup is None:
                self.play(FadeIn(scene_group, shift=UP), run_time=1.5)
            else:
                self.play(
                    ReplacementTransform(current_vgroup, scene_group),
                    run_time=1.2
                )

            # وقت الانتظار بناءً على طول الصوت
            wait_time = max(0.2, scene["duration"] - 1.2)
            self.wait(wait_time)
            current_vgroup = scene_group

        # مشهد الختام
        self.play(FadeOut(current_vgroup, scale=0.5), run_time=2)

# ==========================================
# 3. المايسترو التنفيذي (The Orchestrator)
# ==========================================
async def orchestrate_production():
    logger.info("🎬 بدء عملية الإنتاج الكبرى...")
    
    manager = AssetManager()
    
    # المرحلة 1: معالجة البيانات
    raw_scenes = manager.load_and_clean_script("result.json")
    final_scenes = await manager.build_audio_track(raw_scenes)
    
    # حفظ البيانات للرندر
    with open(os.path.join(manager.output_dir, "data.json"), "w") as f:
        json.dump(final_scenes, f, indent=4)

    # المرحلة 2: تشغيل الرندر (Native Module Mode)
    logger.info("⚙️ استدعاء محرك Manim من داخل الترسانة...")
    
    # تأمين متغيرات البيئة للعملية الفرعية (لضمان رؤية FFmpeg)
    render_env = os.environ.copy()
    
    render_command = [
        "python3", "-m", "manim",
        "-ql", # الجودة: -ql (Low), -qh (High)
        "main_pipeline.py",
        "AIVideoProduction",
        "-o", f"video_{datetime.now().strftime('%H%M%S')}.mp4",
        "--progress_bar", "display",
        "--disable_caching"
    ]

    try:
        process = subprocess.run(
            render_command, 
            env=render_env, 
            capture_output=True, 
            text=True
        )
        
        if process.returncode == 0:
            logger.info("✨ اكتمل الإنتاج بنجاح! الفيديو جاهز في مجلد media/videos.")
            print(process.stdout)
        else:
            logger.error(f"❌ فشل الرندر: {process.stderr}")
    except Exception as e:
        logger.error(f"🚨 خطأ فادح في نظام التشغيل: {e}")

if __name__ == "__main__":
    asyncio.run(orchestrate_production())

