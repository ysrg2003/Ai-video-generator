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
# 0. نظام التشغيل وحقن البيئة (The Core Engine)
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("IndustrialVideoFactory")

class ArsenalEngine:
    """المسؤول عن تفعيل البيئة وضمان رؤية FFmpeg و Manim لبعضهما"""
    @staticmethod
    def initialize():
        cwd = os.getcwd()
        extract_base = os.path.join(cwd, "vendor_extracted")
        v_python = os.path.join(extract_base, "python")
        v_bin = os.path.join(v_python, "bin")

        if os.path.exists(v_python):
            # حقن المسارات في ذاكرة النظام
            sys.path.insert(0, v_python)
            os.environ["PYTHONPATH"] = f"{v_python}:{os.environ.get('PYTHONPATH', '')}"
            os.environ["PATH"] = f"{v_bin}:{os.environ.get('PATH', '')}"
            
            # إصلاح صلاحيات التنفيذ للمحركات الثنائية
            for root, _, files in os.walk(v_bin):
                for name in files:
                    fpath = os.path.join(root, name)
                    os.chmod(fpath, os.stat(fpath).st_mode | stat.S_IEXEC)
            
            # الربط الصريح لـ FFmpeg
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                os.environ["FFMPEG_BINARY"] = ffmpeg_path
            
            logger.info(f"✅ Arsenal Initialized. FFmpeg found at: {ffmpeg_path}")
            return True
        return False

# تفعيل المحرك فوراً
ArsenalEngine.initialize()

try:
    from manim import *
    import arabic_reshaper
    from bidi.algorithm import get_display
    from mutagen.mp3 import MP3
    import edge_tts
    # إعدادات Manim العالمية للرندر الاحترافي
    config.background_color = "#0a0a0c"
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
except ImportError as e:
    logger.error(f"🚨 Missing Libraries: {e}")

# ==========================================
# 1. معالج النصوص والأصول (Data Orchestrator)
# ==========================================
class AssetOrchestrator:
    def __init__(self, dir_name="prod_assets"):
        self.dir = dir_name
        if os.path.exists(self.dir): shutil.rmtree(self.dir)
        os.makedirs(self.dir, exist_ok=True)

    @staticmethod
    def process_ar(text):
        """تحويل النص العربي ليناسب محركات الرندر"""
        if not text: return ""
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    def parse_script(self, path="result.json"):
        """محرك استخراج البيانات مع نظام تصحيح الأخطاء الذاتي"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                content = raw.get("response", str(raw))
            
            # استخراج المصفوفة وتجاهل أي نصوص جانبية من Gemini
            match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            data = json.loads(match.group(0)) if match else json.loads(content)
            return data
        except Exception as e:
            logger.warning(f"⚠️ Script Parse Error: {e}. Using fallback.")
            return [{"text": "جاري التحميل...", "duration": 5}]

    async def generate_assets(self, scenes):
        """توليد الصوت ومزامنة التوقيت بدقة الميلي ثانية"""
        logger.info("🎙️ Synthesizing Neural Audio Tracks...")
        for i, scene in enumerate(scenes):
            audio_path = os.path.join(self.dir, f"audio_{i}.mp3")
            communicate = edge_tts.Communicate(scene["text"], "ar-EG-SalmaNeural")
            await communicate.save(audio_path)
            
            scene["audio"] = audio_path
            scene["duration"] = MP3(audio_path).info.length
        return scenes

# ==========================================
# 2. محرك الرندر السينمائي (Cinematic Visualizer)
# ==========================================
class HighEndProduction(MovingCameraScene):
    def construct(self):
        # تحميل البيانات المعالجة
        with open("prod_assets/metadata.json", "r") as f:
            scenes = json.load(f)

        # خلفية متدرجة (Gradient Background) ثنائية الألوان
        background = FullScreenRectangle().set_fill(
            color=[DARK_GRAY, BLACK], opacity=1
        ).set_z_index(-10)
        self.add(background)

        # إعداد حركة الكاميرا "تأثير التنفس"
        self.camera.frame.save_state()
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 + 0.04 * dt))

        last_obj = None

        for i, scene in enumerate(scenes):
            txt_content = AssetOrchestrator.process_ar(scene["text"])
            
            # إنشاء النص مع تأثير الظل (Shadow) لعمق بصري
            main_text = Text(txt_content, font_size=44, color=WHITE, weight=BOLD)
            shadow = Text(txt_content, font_size=44.5, color=BLACK, opacity=0.5).shift(0.05*DOWN + 0.05*RIGHT)
            
            # صندوق نص زجاجي (Frosted Glass Effect)
            frame = RoundedRectangle(
                corner_radius=0.2, 
                width=main_text.width + 1.2, 
                height=main_text.height + 0.8
            ).set_fill(color=BLACK, opacity=0.4).set_stroke(color=BLUE_E, opacity=0.3)
            
            current_scene_group = VGroup(shadow, frame, main_text)
            
            # تشغيل الصوت الملاحق
            self.add_sound(scene["audio"])

            # الانتقالات السينمائية (Transitions)
            if last_obj is None:
                self.play(FadeIn(current_scene_group, shift=UP), run_time=1.5)
            else:
                self.play(
                    ReplacementTransform(last_obj, current_scene_group),
                    run_time=1.2,
                    rate_func=smooth
                )

            # الانتظار حتى انتهاء الصوت
            self.wait(max(0.1, scene["duration"] - 1.2))
            last_obj = current_scene_group

        # الختام (Outro)
        self.play(FadeOut(last_obj, scale=0.3), run_time=1.5)

# ==========================================
# 3. المايسترو (The Master Orchestrator)
# ==========================================
async def start_production():
    logger.info("🚀 Starting Master Video Pipeline...")
    
    orchestrator = AssetOrchestrator()
    scenes = orchestrate_scenes = orchestrator.parse_script()
    final_data = await orchestrator.generate_assets(scenes)
    
    with open("prod_assets/metadata.json", "w") as f:
        json.dump(final_data, f, indent=4)

    # تشغيل رندر Manim كعملية فرعية مع حقن البيئة بالكامل
    logger.info("🎬 Rendering Frames (High Fidelity)...")
    render_env = os.environ.copy()
    
    cmd = [
        "python3", "-m", "manim",
        "-ql", # استخدم -qh للجودة العالية جداً
        "main_pipeline.py",
        "HighEndProduction",
        "-o", "final_masterpiece.mp4",
        "--disable_caching",
        "--progress_bar", "display"
    ]
    
    proc = subprocess.run(cmd, env=render_env, capture_output=True, text=True)
    
    if proc.returncode == 0:
        logger.info("✨ Production Complete. File: final_masterpiece.mp4")
        print(proc.stdout)
    else:
        logger.error(f"❌ Render Crashed: {proc.stderr}")

if __name__ == "__main__":
    asyncio.run(start_production())
