import os
import sys
import json
import re
import asyncio
import stat
import shutil
import subprocess

# ==========================================
# 0. نظام حقن البيئة الشامل (Industrial Environment Injection)
# ==========================================
def activate_arsenal():
    """تجهيز المسارات والروابط التنفيذية لضمان عمل Manim و FFmpeg"""
    cwd = os.getcwd()
    extract_base = os.path.join(cwd, "vendor_extracted")
    v_python = os.path.join(extract_base, "python")
    v_bin = os.path.join(v_python, "bin")
    v_browsers = os.path.join(extract_base, "browsers")

    if os.path.exists(v_python):
        # 1. حقن مكتبات بايثون في مقدمة المسارات
        sys.path.insert(0, v_python)
        os.environ["PYTHONPATH"] = f"{v_python}:{os.environ.get('PYTHONPATH', '')}"
        
        # 2. جعل الأدوات التنفيذية (مثل manim و ffmpeg) مرئية للنظام
        os.environ["PATH"] = f"{v_bin}:{os.environ.get('PATH', '')}"
        
        # 3. منح صلاحيات التنفيذ لكافة الملفات في مجلد bin
        for file in os.listdir(v_bin):
            fpath = os.path.join(v_bin, file)
            st = os.stat(fpath)
            os.chmod(fpath, st.st_mode | stat.S_IEXEC)
        print(f"✅ Arsenal Active: Python libs and Binaries linked.")

    if os.path.exists(v_browsers):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = v_browsers

activate_arsenal()

# استيراد المكتبات بعد تجهيز البيئة
try:
    import edge_tts
    from mutagen.mp3 import MP3
    from manim import *
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError as e:
    print(f"⚠️ Warning: Library missing in Arsenal, trying system fallback: {e}")

# ==========================================
# 1. إدارة الأصول والبيانات (Data & Asset Management)
# ==========================================
ASSETS_DIR = "production_assets"
if os.path.exists(ASSETS_DIR): shutil.rmtree(ASSETS_DIR)
os.makedirs(ASSETS_DIR, exist_ok=True)

def ar(text):
    """المعالج الاحترافي للنصوص العربية"""
    if not text: return ""
    return get_display(arabic_reshaper.reshape(text))

def load_script_safely():
    """محرك استخراج JSON ذكي يتجاوز أخطاء التنسيق"""
    print("📖 Searching for Gemini output (result.json)...")
    path = "result.json"
    if not os.path.exists(path):
        # البحث في المجلدات الفرعية في حال قام الأكشن بتحميله في مجلدArtifact
        for r, d, f in os.walk("."):
            if "result.json" in f:
                path = os.path.join(r, "result.json")
                break
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            text_to_parse = raw.get("response", str(raw))

        # تنظيف بلوكات الماركداون والتعليقات الجانبية
        text_to_parse = re.sub(r'```json|```', '', text_to_parse).strip()
        
        # محاولة العثور على أول مصفوفة [ ] في النص
        json_match = re.search(r'\[.*\]', text_to_parse, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(text_to_parse)
    except Exception as e:
        print(f"❌ JSON Critical Error: {e}. Using Emergency Script.")
        return [{"text": "نعتذر عن الخطأ التقني، جاري بدء العرض الاحتياطي", "highlight": "التقني", "color": "RED"}]

# ==========================================
# 2. محرك الصوت والرسوميات (Production Engines)
# ==========================================
async def prepare_assets(scenes):
    print("🎙️ Generating High-Fidelity Audio Tracks...")
    for i, scene in enumerate(scenes):
        audio_path = os.path.join(ASSETS_DIR, f"s_{i}.mp3")
        tts = edge_tts.Communicate(scene["text"], "ar-EG-SalmaNeural")
        await tts.save(audio_path)
        scene["duration"] = MP3(audio_path).info.length
    return scenes

class AIVideoProduction(MovingCameraScene):
    def construct(self):
        # تحميل البيانات الوسيطة
        with open(os.path.join(ASSETS_DIR, "data.json"), "r") as f:
            scenes = json.load(f)

        # خلفية سينمائية مع تدرج لوني عميق
        bg = FullScreenRectangle().set_fill(
            LinearGradient(direction=DOWN, colors=[DARK_GRAY, BLACK]), opacity=1
        )
        self.add(bg)

        # حركة كاميرا "تتنفس" (Slow Dynamic Zoom)
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 + 0.04 * dt))

        current_obj = None
        for i, scene in enumerate(scenes):
            # تنسيق النص مع الكلمات المفتاحية
            txt, hl = scene["text"], scene.get("highlight", "")
            clr = getattr(sys.modules[__name__], scene.get("color", "YELLOW").upper(), YELLOW)

            if hl and hl in txt:
                p1, p2 = txt.split(hl, 1)
                m_txt = VGroup(
                    Text(ar(p2), font_size=34),
                    Text(ar(hl), font_size=42, color=clr, weight=BOLD).scale(1.1),
                    Text(ar(p1), font_size=34)
                ).arrange(RIGHT, buff=0.15)
            else:
                m_txt = Text(ar(txt), font_size=36)

            # إضافة ظل (Shadow) للنص لزيادة المقروئية
            m_txt.add_background_rectangle(color=BLACK, opacity=0.3, buff=0.2)

            self.add_sound(os.path.join(ASSETS_DIR, f"s_{i}.mp3"))
            
            # الأنيميشن (Morphing Transition)
            if current_obj is None:
                self.play(Write(m_txt), run_time=1.2)
            else:
                self.play(ReplacementTransform(current_obj, m_txt), run_time=1)
            
            self.wait(max(0.5, scene["duration"] - 1.2))
            current_obj = m_txt

        self.play(FadeOut(current_obj, scale=0.5), run_time=1.5)

# ==========================================
# 3. المايسترو التنفيذي (Executive Orchestrator)
# ==========================================
async def main():
    # 1. معالجة البيانات والصوت
    scenes = await prepare_assets(load_script_safely())
    with open(os.path.join(ASSETS_DIR, "data.json"), "w") as f:
        json.dump(scenes, f, indent=4)

    print("🎬 Initializing Cinematic Render...")
    
    # الحل النهائي لمشكلة "Command Not Found":
    # استدعاء مانيم كـ Module تابع لنسخة بايثون الحالية التي تملك الترسانة
    render_args = [
        "python3", "-m", "manim",
        "-ql",                      # جودة منخفضة للسرعة (استخدم -qh للنهائي)
        "main_pipeline.py",        # اسم الملف الحالي
        "AIVideoProduction",       # اسم الكلاس
        "-o", "final_video.mp4",
        "--progress_bar", "none"
    ]
    
    # تنفيذ العملية ومراقبة المخرجات
    process = subprocess.run(render_args, capture_output=True, text=True)
    print(process.stdout)
    if process.returncode != 0:
        print(f"❌ Render Failed: {process.stderr}")
    else:
        print("✨ Production Complete! Video is ready.")

if __name__ == "__main__":
    asyncio.run(main())
