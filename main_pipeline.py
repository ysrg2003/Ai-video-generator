import os
import sys
import json
import re
import asyncio
import stat
import shutil

# ==========================================
# 0. حقن الترسانة المتقدم (Advanced Arsenal Injection)
# ==========================================
def activate_arsenal():
    """ربط السكربت بمجلد المكتبات والمتصفحات المستخرج"""
    extract_base = os.path.join(os.getcwd(), "vendor_extracted")
    v_python = os.path.join(extract_base, "python")
    v_browsers = os.path.join(extract_base, "browsers")

    if os.path.exists(v_python):
        sys.path.insert(0, v_python)
        # تحديث PATH للوصول للأدوات التنفيذية داخل الترسانة
        bin_dir = os.path.join(v_python, "bin")
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    
    if os.path.exists(v_browsers):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = v_browsers

activate_arsenal()

# استيراد المكتبات بعد الحقن
try:
    import edge_tts
    from mutagen.mp3 import MP3
    from manim import *
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError as e:
    print(f"⚠️ تحذير: نقص في المكتبات، قد يعتمد النظام على البيئة المحلية: {e}")

# ==========================================
# 1. إعدادات الإنتاج (Production Config)
# ==========================================
ASSETS_DIR = "production_assets"
if os.path.exists(ASSETS_DIR):
    shutil.rmtree(ASSETS_DIR) # تنظيف لضمان إنتاج جديد تماماً
os.makedirs(ASSETS_DIR, exist_ok=True)

def ar(text):
    """إصلاح عرض اللغة العربية"""
    if not text: return ""
    return get_display(arabic_reshaper.reshape(text))

# ==========================================
# 2. معالج السيناريو (Script Processor)
# ==========================================
def load_script():
    print("📖 جاري تحليل السيناريو من Gemini...")
    try:
        with open("result.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            content = raw_data.get("response", str(raw_data))

        # تنظيف النص من أي علامات Markdown قد يضيفها Gemini
        json_pattern = r'\[\s*{.*}\s*\]'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            # محاولة تحويل المحتوى مباشرة إذا كان نصاً نظيفاً
            return json.loads(content.strip())
    except Exception as e:
        print(f"⚠️ خطأ في JSON: {e}. يتم استخدام سيناريو الطوارئ.")
        return [{"text": "نعتذر، حدث خطأ في معالجة البيانات", "highlight": "خطأ", "color": "RED"}]

# ==========================================
# 3. مهندس الصوت (Audio Engineer)
# ==========================================
async def build_audio_track(scenes):
    print("🎙️ توليد التعليق الصوتي لكل مشهد...")
    for i, scene in enumerate(scenes):
        path = os.path.join(ASSETS_DIR, f"s_{i}.mp3")
        # صوت سلمى Neural يتميز بالوضوح والاحترافية
        tts = edge_tts.Communicate(scene["text"], "ar-EG-SalmaNeural")
        await tts.save(path)
        
        # قياس المدة الزمنية بدقة للمزامنة البصرية
        scene["duration"] = MP3(path).info.length
    return scenes

# ==========================================
# 4. محرك الرسوميات السينمائي (Cinematic Engine)
# ==========================================
class AIVideoProduction(MovingCameraScene):
    def construct(self):
        # تحميل البيانات المجهزة
        data_file = os.path.join(ASSETS_DIR, "processed_script.json")
        with open(data_file, "r", encoding="utf-8") as f:
            scenes = json.load(f)

        # 1. إعداد الخلفية السينمائية (Gradient Background)
        bg = FullScreenRectangle().set_fill(
            LinearGradient(direction=DOWN, colors=[DARK_GRAY, BLACK]), opacity=1
        )
        self.add(bg)

        # 2. تأثير حركة الكاميرا (Constant Slow Zoom Out)
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 + 0.03 * dt))

        prev_obj = None

        for i, scene in enumerate(scenes):
            txt = scene["text"]
            hl = scene.get("highlight", "")
            clr = scene.get("color", "YELLOW").upper()
            
            # لوحة ألوان الإنتاج
            palette = {"RED": RED, "BLUE": BLUE, "GREEN": GREEN, "YELLOW": YELLOW, "PURPLE": PURPLE, "ORANGE": ORANGE}
            hl_clr = palette.get(clr, YELLOW)

            # بناء مصفوفة النص العربي (VGroup لضمان المحاذاة)
            if hl and hl in txt:
                parts = txt.split(hl, 1)
                main_txt = VGroup(
                    Text(ar(parts[1]), font="sans-serif", font_size=34, color=WHITE),
                    Text(ar(hl), font="sans-serif", font_size=40, color=hl_clr, weight=BOLD),
                    Text(ar(parts[0]), font="sans-serif", font_size=34, color=WHITE)
                ).arrange(RIGHT, buff=0.18)
            else:
                main_txt = Text(ar(txt), font="sans-serif", font_size=36, color=WHITE)

            # إضافة ظل خفيف للنص لزيادة العمق
            main_txt.add_background_rectangle(color=BLACK, opacity=0.2, buff=0.2)

            # تشغيل الصوت المرتبط بالمشهد
            audio_file = os.path.join(ASSETS_DIR, f"s_{i}.mp3")
            self.add_sound(audio_file)

            # حساب توقيت المشهد (مدة الصوت ناقص وقت الانتقال)
            scene_duration = scene.get("duration", 3)
            wait_time = max(0.5, scene_duration - 1.0)

            # أنيميشن الانتقالات
            if prev_obj is None:
                self.play(Write(main_txt), run_time=1)
                self.wait(wait_time)
            else:
                self.play(
                    ReplacementTransform(prev_obj, main_txt),
                    run_time=0.8,
                    rate_func=smooth
                )
                self.wait(wait_time)
            
            prev_obj = main_txt

        # الخاتمة
        self.play(FadeOut(prev_obj, scale=0.8), run_time=1.5)

# ==========================================
# 5. المايسترو (Orchestrator)
# ==========================================
async def start_production():
    # المرحلة 1: السيناريو
    scenes = load_script()
    
    # المرحلة 2: الصوتيات
    scenes = await build_audio_track(scenes)
    
    # المرحلة 3: التوقيتات
    with open(os.path.join(ASSETS_DIR, "processed_script.json"), "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=4)
        
    print("🎬 بدء الرندر النهائي (High Quality Mode)...")
    
    # تمرير PYTHONPATH للمتطلبات الفرعية
    p_path = os.path.join(os.getcwd(), "vendor_extracted", "python")
    os.environ["PYTHONPATH"] = f"{p_path}:{os.environ.get('PYTHONPATH', '')}"
    
    # أمر الرندر الاحترافي (إلغاء أشرطة التقدم لعدم تلويث سجلات GitHub)
    cmd = "manim -ql main_pipeline.py AIVideoProduction -o final_video.mp4 --progress_bar none"
    os.system(cmd)
    
    print("\n✨ اكتمل الإنتاج! ابحث عن الفيديو في مجلد media.")

if __name__ == "__main__":
    asyncio.run(start_production())
