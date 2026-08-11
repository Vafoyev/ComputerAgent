import speech_recognition as sr
import google.generativeai as genai
import webbrowser
import json
import os
import tempfile
import pygame
import time
from gtts import gTTS

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

pygame.mixer.init()

def speak(text):
    print(f"Agent: {text}")
    try:
        # Bepul Google ovozini o'rnatish
        tts = gTTS(text=text, lang='uz')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_filename = f.name
            
        tts.save(temp_filename)
        
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.music.unload()
        try:
            os.remove(temp_filename)
        except:
            pass
    except Exception as e:
        print(f"Ovoz chiqarishda xatolik: {e}")

def process_command(text):
    prompt = f"""
    Foydalanuvchi shunday dedi: "{text}"
    Agar foydalanuvchi qaysidir veb-saytni ochishni yoki qaysidir saytga kirishni xohlasa (masalan, "Youtubega kir", "Google och"), quyidagi JSON formatida javob qaytar:
    {{"action": "open_url", "url": "https://www.youtube.com", "response": "Xo'p, Youtubeni ochaman."}}
    Agar u oddiy savol bersa yoki suhbatlashsa, faqatgina o'zbek tilida qisqa javobni JSON formatida qaytar:
    {{"action": "reply", "response": "Sizning javobingiz"}}
    Javob faqat toza JSON bo'lishi shart, markdown kod bloklarisiz.
    """
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        data = json.loads(result_text.strip())
        
        if data.get("action") == "open_url":
            speak(data.get("response", "Sayt ochilmoqda."))
            webbrowser.open(data.get("url"))
        else:
            speak(data.get("response", "Tushunarsiz javob."))
    except Exception as e:
        print(f"Gemini API xatoligi: {e}")
        speak("Kechirasiz, xatolik yuz berdi. Internetni yoki API ni tekshiring.")

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    speak("Salom, men sizning bepul ovozli yordamchingizman. Menga buyruq bering.")
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        
    while True:
        try:
            print("\nEshitmoqdaman...")
            with microphone as source:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Ovozni tanib olish...")
            text = recognizer.recognize_google(audio, language="uz-UZ")
            print(f"Siz dedingiz: {text}")
            
            if "xayr" in text.lower() or "chiqish" in text.lower() or "to'xta" in text.lower():
                speak("Xayr, salomat bo'ling.")
                break
                
            process_command(text)
            
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Google xizmati bilan ulanishda xatolik: {e}")
            break
        except Exception as e:
            print(f"Kutilmagan xatolik: {e}")

if __name__ == "__main__":
    main()
