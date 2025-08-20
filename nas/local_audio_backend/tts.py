from gtts import gTTS
import os
from playsound import playsound

def speak_test(text, lang='zh-CN'):
    try:
        print(f"正在朗读 ({lang}): {text}")
        tts_filename = "temp_tts_test.mp3"
        tts = gTTS(text=text, lang=lang)
        tts.save(tts_filename)
        playsound(tts_filename)
        os.remove(tts_filename)
        print("朗读完成。")
    except Exception as e:
        print(f"朗读失败: {e}")

speak_test("你好，这是一个中文语音测试。")
speak_test("Hello, this is an English voice test.", lang='en')