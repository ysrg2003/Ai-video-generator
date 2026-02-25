
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
# 1. إعدادات النظام
# ==========================================
TOPIC = "ما هو الذكاء الاصطناعي؟"  # جعلت الموضوع بالعربية ليتوافق مع الإعدادات
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
OUTPUT_DIR = "assets"
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# دالة لإصلاح الحروف العربية
def ar(text):
    return get_display(arabic_reshaper.reshape(text))

# ==========================================
# 2. المخرج الذكي (Gemini)
# ==========================================
def generate_director_script(topic):
    print("🎬 جاري كتابة السيناريو والإخراج بواسطة Gemini...")
    client = Gemini(token=GEMINI_TOKEN)
    
    # إصلاح البرومبت ليطلب نصاً عربياً يتوافق مع التعليق الصوتي
    prompt = f"""
    أنت مخرج فيديوهات Motion Graphics محترف. موضوع الفيديو هو: "{topic}".
    أريد منك كتابة سكريبت من 3 مشاهد قصيرة جداً ومثيرة باللغة العربية.
    أخرج النتيجة حصرياً بصيغة JSON كالتالي، ولا تكتب أي كلمة خارج المصفوفة:
    [
      {{"text": "الجملة باللغة العربية", "highlight": "أهم كلمة في الجملة لتلوينها", "color": "RED"}},
      ...
    ]
    """
    
    response = client.generate_content(prompt)
    
    match = re.search(r'\[.*\]', response.text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    else:
        return [{"text": "مرحباً بك في عالم التقنية", "highlight": "التقنية", "color": "BLUE"}]

# ==========================================
# 3. مهندس الصوت (Edge-TTS)
# ==========================================
async def generate_audio_for_scenes(scenes):
    print("🎙️ جاري توليد التعليق الصوتي...")
    for i, scene in enumerate(scenes):
        audio_path = f"{OUTPUT_DIR}/audio_{i}.mp3"
        communicate = edge_tts.Communicate(scene["text"], "ar-EG-SalmaNeural")
        await communicate.save(audio_path)
        
        audio_info = MP3(audio_path)
        scene["duration"] = audio_info.info.length
    return scenes

# ==========================================
# 4. محرك الرسوم والمونتاج (Manim)
# ==========================================
class AIVideoEngine(Scene):
    def construct(self):
        with open(f"{OUTPUT_DIR}/script_data.json", "r", encoding="utf-8") as f:
            scenes = json.load(f)

        self.camera.frame.add_updater(lambda m, dt: m.scale(1 - 0.01 * dt))

        previous_text_obj = None

        for i, scene in enumerate(scenes):
            duration = scene["duration"]
            full_text = scene["text"]
            highlight = scene["highlight"]
            color_name = scene.get("color", "YELLOW")
            
            highlight_color = RED if color_name == "RED" else (BLUE if color_name == "BLUE" else YELLOW)

            # إصلاح: التأكد من الانقسام لجزئين فقط حتى لو تكررت الكلمة
            parts = full_text.split(highlight, 1) 
            
            if len(parts) == 2:
                text_group = VGroup(
                    Text(ar(parts[1]), font="Arial", color=WHITE),
                    Text(ar(highlight), font="Arial", color=highlight_color).scale(1.2),
                    Text(ar(parts[0]), font="Arial", color=WHITE)
                ).arrange(RIGHT, buff=0.1)
            else:
                text_group = Text(ar(full_text), font="Arial", color=WHITE)

            self.add_sound(f"{OUTPUT_DIR}/audio_{i}.mp3")

            # إصلاح: حماية المونتاج من التوقيت السالب
            safe_wait_time = max(0.2, duration - 1)

            if previous_text_obj is None:
                text_group.shift(DOWN * 0.5)
                self.play(FadeIn(text_group, shift=UP), run_time=1)
                self.wait(safe_wait_time)
            else:
                self.play(ReplacementTransform(previous_text_obj, text_group), run_time=1)
                self.wait(safe_wait_time)
            
            previous_text_obj = text_group

        self.play(FadeOut(previous_text_obj), run_time=1)

# ==========================================
# 5. المايسترو (التشغيل التلقائي)
# ==========================================
async def main():
    scenes = generate_director_script(TOPIC)
    scenes_with_audio = await generate_audio_for_scenes(scenes)
    
    with open(f"{OUTPUT_DIR}/script_data.json", "w", encoding="utf-8") as f:
        json.dump(scenes_with_audio, f, ensure_ascii=False)
        
    print("🎬 جاري عمل الرندر النهائي (Rendering)...")
    os.system("manim -pqh --resolution 1080,1920 --pixel_ratio 1 main_pipeline.py AIVideoEngine -o final_video.mp4")
    print("✅ تم الانتهاء من صناعة الفيديو بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
