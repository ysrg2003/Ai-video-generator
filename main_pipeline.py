import os
import json
import re
import asyncio
import edge_tts
from mutagen.mp3 import MP3
from manim import *

import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# 1. إعدادات النظام وتجهيز البيئة
# ==========================================
OUTPUT_DIR = "assets"
if not os.path.exists(OUTPUT_DIR): 
    os.makedirs(OUTPUT_DIR)

# دالة معالجة النصوص العربية لتعمل مع محرك الرسوم
def ar(text):
    return get_display(arabic_reshaper.reshape(text))

# ==========================================
# 2. المخرج الذكي (Data Processor)
# ==========================================
# ملاحظة: تم تعديل هذه الدالة لتقرأ من مخرجات Gemini التي جلبها ملف main.py
def process_director_output():
    print("🎬 جاري معالجة السيناريو المستلم من Gemini...")
    try:
        with open("result.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_text = data.get("response", "")
            
        # استخراج مصفوفة JSON من رد Gemini (حتى لو أضاف نصوصاً خارجها)
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            # سيناريو احتياطي في حال فشل الاستخراج
            return [{"text": "مرحباً بكم في عرضنا التقني", "highlight": "التقني", "color": "BLUE"}]
    except Exception as e:
        print(f"⚠️ خطأ في قراءة ملف السيناريو: {e}")
        return [{"text": "خطأ في تحميل البيانات", "highlight": "خطأ", "color": "RED"}]

# ==========================================
# 3. مهندس الصوت (Edge-TTS)
# ==========================================
async def generate_audio_for_scenes(scenes):
    print("🎙️ جاري توليد التعليق الصوتي الاحترافي...")
    for i, scene in enumerate(scenes):
        audio_path = f"{OUTPUT_DIR}/audio_{i}.mp3"
        # استخدام صوت "سلمى" المميز للغة العربية
        communicate = edge_tts.Communicate(scene["text"], "ar-EG-SalmaNeural")
        await communicate.save(audio_path)
        
        # حساب مدة الصوت لضبط توقيت المشهد بدقة
        audio_info = MP3(audio_path)
        scene["duration"] = audio_info.info.length
    return scenes

# ==========================================
# 4. محرك الرسوم والمونتاج (Manim Engine)
# ==========================================
class AIVideoEngine(Scene):
    def construct(self):
        # تحميل البيانات المعالجة
        with open(f"{OUTPUT_DIR}/script_data.json", "r", encoding="utf-8") as f:
            scenes = json.load(f)

        # تأثير حركة الكاميرا المستمرة (Slow Zoom) لزيادة الاحترافية
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 - 0.01 * dt))

        previous_text_obj = None

        for i, scene in enumerate(scenes):
            duration = scene["duration"]
            full_text = scene["text"]
            highlight = scene["highlight"]
            color_name = scene.get("color", "YELLOW")
            
            # تحديد لون الكلمة المفتاحية
            highlight_color = RED if color_name == "RED" else (BLUE if color_name == "BLUE" else YELLOW)

            # تقسيم النص وتنسيقه (RTL)
            parts = full_text.split(highlight, 1) 
            
            if len(parts) == 2:
                # ترتيب النصوص من اليمين لليسار بشكل صحيح
                text_group = VGroup(
                    Text(ar(parts[1]), font="sans-serif", color=WHITE),
                    Text(ar(highlight), font="sans-serif", color=highlight_color).scale(1.2),
                    Text(ar(parts[0]), font="sans-serif", color=WHITE)
                ).arrange(RIGHT, buff=0.2)
            else:
                text_group = Text(ar(full_text), font="sans-serif", color=WHITE)

            # إضافة الصوت للمزامنة
            self.add_sound(f"{OUTPUT_DIR}/audio_{i}.mp3")

            # حساب زمن الانتظار (مدة الصوت ناقص وقت الانتقال)
            safe_wait_time = max(0.5, duration - 1.2)

            if previous_text_obj is None:
                text_group.shift(DOWN * 0.5)
                self.play(FadeIn(text_group, shift=UP), run_time=1)
                self.wait(safe_wait_time)
            else:
                # انتقال سلس بين الجمل (Morphing Effect)
                self.play(ReplacementTransform(previous_text_obj, text_group), run_time=1.2)
                self.wait(safe_wait_time)
            
            previous_text_obj = text_group

        # نهاية الفيديو
        self.play(FadeOut(previous_text_obj), run_time=1)

# ==========================================
# 5. المايسترو (التشغيل النهائي)
# ==========================================
async def main():
    # الخطوة 1: معالجة البيانات المستلمة
    scenes = process_director_output()
    
    # الخطوة 2: توليد الصوت وقياس المدد الزمنية
    scenes_with_audio = await generate_audio_for_scenes(scenes)
    
    # حفظ البيانات المكتملة للمحرك
    with open(f"{OUTPUT_DIR}/script_data.json", "w", encoding="utf-8") as f:
        json.dump(scenes_with_audio, f, ensure_ascii=False)
        
    print("🎬 جاري بدء الإنتاج البصري (Rendering)...")
    # ملاحظة: استخدمنا -ql للسرعة، و -o لتحديد اسم الملف، وحذفنا -p لأنها لا تعمل في السيرفرات
    os.system("manim -ql main_pipeline.py AIVideoEngine -o final_video.mp4")
    print("✅ تم بنجاح! الفيديو جاهز الآن.")

if __name__ == "__main__":
    asyncio.run(main())
