import os
import sys
import json
import re
import asyncio
import stat

# ==========================================
# 0. ميكانيكية حقن الترسانة (Arsenal Injection)
# ==========================================
def activate_arsenal():
    """تفعيل المكتبات والمتصفحات من الترسانة دون تثبيتها"""
    current_dir = os.getcwd()
    vendor_python = os.path.join(current_dir, "python")
    vendor_browsers = os.path.join(current_dir, "browsers")

    if os.path.exists(vendor_python):
        sys.path.insert(0, vendor_python)
    
    if os.path.exists(vendor_browsers):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = vendor_browsers

# تفعيل الترسانة في أول سطر في البرنامج
activate_arsenal()

# استيراد المكتبات (الآن ستعمل من الترسانة)
try:
    import edge_tts
    from mutagen.mp3 import MP3
    from manim import *
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError as e:
    print(f"❌ خطأ: لم يتم العثور على المكتبات في الترسانة! {e}")
    # لا نخرج من البرنامج، ربما المكتبات مثبتة عالمياً
    pass

# ==========================================
# 1. الإعدادات والوظائف المساعدة
# ==========================================
OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ar(text):
    """إصلاح عرض اللغة العربية (Bidi + Reshaper)"""
    return get_display(arabic_reshaper.reshape(text))

# ==========================================
# 2. معالج البيانات المستلمة (Director Output)
# ==========================================
def process_director_output():
    print("🎬 جاري استخراج السيناريو من JSON...")
    try:
        # قراءة النتيجة من المرحلة الأولى (Gemini API Service)
        with open("result.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # ندعم استخراج النص سواء كان رداً مباشراً أو JSON مغلف
            raw_text = data.get("response", str(data))
            
        # محاولة استخراج مصفوفة الـ JSON من داخل النص (Regex)
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            # سيناريو احتياطي احترافي في حال فشل الاستخراج
            print("⚠️ لم يتم العثور على JSON، استخدام سيناريو افتراضي.")
            return [{"text": "مرحباً بكم في نظام الإنتاج الآلي", "highlight": "الآلي", "color": "BLUE"}]
    except Exception as e:
        print(f"❌ خطأ في معالجة البيانات: {e}")
        return [{"text": "خطأ في تحميل البيانات", "highlight": "خطأ", "color": "RED"}]

# ==========================================
# 3. محرك الصوت (Voice Engineer)
# ==========================================
async def generate_audio_for_scenes(scenes):
    print("🎙️ جاري توليد التعليق الصوتي (Edge-TTS)...")
    for i, scene in enumerate(scenes):
        audio_path = f"{OUTPUT_DIR}/audio_{i}.mp3"
        # استخدام سلمى - صوت احترافي ومستقر
        communicate = edge_tts.Communicate(scene["text"], "ar-EG-SalmaNeural")
        await communicate.save(audio_path)
        
        # حساب التوقيت بدقة بالملي ثانية للمزامنة
        audio_info = MP3(audio_path)
        scene["duration"] = audio_info.info.length
    return scenes

# ==========================================
# 4. محرك الرسوميات (The Manim Engine)
# ==========================================
# استخدمنا MovingCameraScene لضمان عمل الـ Zoom بدون أخطاء
class AIVideoEngine(MovingCameraScene):
    def construct(self):
        # 1. قراءة البيانات المجهزة
        script_path = os.path.join(OUTPUT_DIR, "script_data.json")
        with open(script_path, "r", encoding="utf-8") as f:
            scenes = json.load(f)

        # 2. تأثير الخلفية المتحركة والزووم (Slow Cinematic Zoom)
        # هذا يضيف لمسة احترافية للفيديو لكي لا يكون جامداً
        self.camera.frame.save_state()
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 - 0.008 * dt))

        previous_text_obj = None

        for i, scene in enumerate(scenes):
            duration = scene["duration"]
            full_text = scene["text"]
            highlight = scene["highlight"]
            color_name = scene.get("color", "YELLOW")
            
            # خريطة الألوان المتاحة
            colors_map = {"RED": RED, "BLUE": BLUE, "GREEN": GREEN, "YELLOW": YELLOW, "PURPLE": PURPLE}
            hl_color = colors_map.get(color_name.upper(), YELLOW)

            # 3. بناء النص العربي المنسق
            # تقسيم النص حول الكلمة المفتاحية (Highlight)
            if highlight in full_text:
                parts = full_text.split(highlight, 1)
                text_group = VGroup(
                    Text(ar(parts[1]), font="sans-serif", color=WHITE, font_size=36),
                    Text(ar(highlight), font="sans-serif", color=hl_color, font_size=42).scale(1.1),
                    Text(ar(parts[0]), font="sans-serif", color=WHITE, font_size=36)
                ).arrange(RIGHT, buff=0.15)
            else:
                text_group = Text(ar(full_text), font="sans-serif", color=WHITE, font_size=38)

            # 4. إضافة الصوت وتوقيت المشهد
            self.add_sound(f"{OUTPUT_DIR}/audio_{i}.mp3")
            
            # المزامنة: طرح وقت التحول (1.2 ثانية) من مدة الصوت
            wait_time = max(0.2, duration - 1.2)

            # 5. التحريك (Animations)
            if previous_text_obj is None:
                # أول مشهد: ظهور من الأسفل
                self.play(FadeIn(text_group, shift=UP), run_time=1)
                self.wait(wait_time)
            else:
                # المشاهد التالية: تحول سلس (Morphing)
                self.play(
                    ReplacementTransform(previous_text_obj, text_group),
                    run_time=1.2,
                    rate_func=smooth
                )
                self.wait(wait_time)
            
            previous_text_obj = text_group

        # 6. الخروج النهائي
        self.play(FadeOut(previous_text_obj, scale=0.5), run_time=1.5)

# ==========================================
# 5. المايسترو (The Main Orchestrator)
# ==========================================
async def run_pipeline():
    # الخطوة 1: معالجة البيانات
    scenes = process_director_output()
    
    # الخطوة 2: توليد الصوت وقياس المدد
    scenes_with_audio = await generate_audio_for_scenes(scenes)
    
    # الخطوة 3: حفظ البيانات الوسيطة لـ Manim
    with open(os.path.join(OUTPUT_DIR, "script_data.json"), "w", encoding="utf-8") as f:
        json.dump(scenes_with_audio, f, ensure_ascii=False, indent=4)
        
    print("🎬 جاري بدء الرندر البصري (Manim)...")
    
    # تشغيل Manim برمجياً مع تمرير PYTHONPATH لضمان رؤية الترسانة
    python_path = os.path.join(os.getcwd(), "python")
    os.environ["PYTHONPATH"] = f"{python_path}:{os.environ.get('PYTHONPATH', '')}"
    
    # الأمر النهائي للرندر (جودة منخفضة للسرعة، غيرها لـ -qh للجودة العالية)
    render_command = "manim -ql main_pipeline.py AIVideoEngine -o final_video.mp4"
    os.system(render_command)
    
    print("\n✅ تم الإنتاج بنجاح! الملف النهائي: media/videos/main_pipeline/480p15/final_video.mp4")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
