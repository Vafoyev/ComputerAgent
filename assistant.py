import sys
import asyncio
import speech_recognition as sr
import webbrowser
import json
import os
import tempfile
import time
import threading
import subprocess

# ============================================================
#  Ovoz chiqarish: edge-tts (Microsoft - O'zbek tili uz-UZ)
# ============================================================
try:
    import edge_tts
    import pygame
    pygame.mixer.init()
    TTS_BACKEND = "edge"
except ImportError:
    try:
        import pygame
        from gtts import gTTS
        pygame.mixer.init()
        TTS_BACKEND = "gtts"
    except ImportError:
        TTS_BACKEND = "pyttsx3"

if TTS_BACKEND == "pyttsx3":
    import pyttsx3

# edge-tts ovoz: Madina (ayol) yoki Sardor (erkak)
EDGE_VOICE = "uz-UZ-MadinaNeural"   # "uz-UZ-SardorNeural" — erkak ovoz

# ============================================================
#  Gemini API  (yangi google-genai SDK)
# ============================================================
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)


class VoiceAssistant:
    def __init__(self, socketio):
        self.socketio = socketio
        self.recognizer = sr.Recognizer()
        self.is_running = False
        self._lock = threading.Lock()

        if TTS_BACKEND == "pyttsx3":
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)

    # ----------------------------------------------------------
    #  Log chiqarish (emoji xavfsiz)
    # ----------------------------------------------------------
    def emit_log(self, msg, msg_type="info"):
        try:
            ascii_msg = msg.encode('ascii', errors='replace').decode('ascii')
            print(f"[{msg_type.upper()}] {ascii_msg}", flush=True)
        except Exception:
            pass
        self.socketio.emit('log', {'msg': msg, 'type': msg_type})

    # ----------------------------------------------------------
    #  Ovoz chiqarish
    # ----------------------------------------------------------
    def speak(self, text):
        self.emit_log(f"[JARVIS] {text}", "agent")
        try:
            if TTS_BACKEND == "edge":
                self._speak_edge(text)
            elif TTS_BACKEND == "gtts":
                self._speak_gtts(text)
            else:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            self.emit_log(f"Ovoz xatoligi: {str(e)}", "error")

    def _play_mp3(self, path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        pygame.mixer.music.unload()
        try:
            os.remove(path)
        except Exception:
            pass

    def _speak_edge(self, text):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tmp_path = f.name

            async def _gen():
                communicate = edge_tts.Communicate(text, EDGE_VOICE)
                await communicate.save(tmp_path)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_gen())
            loop.close()
            self._play_mp3(tmp_path)
        except Exception as e:
            self.emit_log(f"edge-tts xatolik: {str(e)}", "error")
            self._speak_gtts(text, lang='ru')

    def _speak_gtts(self, text, lang='ru'):
        from gtts import gTTS
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tmp_path = f.name
        gTTS(text=text, lang=lang).save(tmp_path)
        self._play_mp3(tmp_path)

    # ----------------------------------------------------------
    #  Mikrofon tekshirish + Windows ruhsat so'rash
    # ----------------------------------------------------------
    def open_windows_mic_permission(self):
        try:
            subprocess.Popen(
                'start ms-settings:privacy-microphone',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            self.emit_log(f"Windows sozlama ochilmadi: {str(e)}", "error")

    def check_and_request_mic(self):
        self.emit_log("Qurilmalar tekshirilmoqda...", "info")
        for attempt in range(3):
            try:
                mics = sr.Microphone.list_microphone_names()
                if len(mics) > 0:
                    self.emit_log(f"[OK] Mikrofon topildi: {mics[0]}", "neon")
                    return True
            except Exception as e:
                self.emit_log(f"Mikrofon xatoligi: {str(e)}", "error")

            if attempt == 0:
                self.emit_log("[!] Mikrofon topilmadi!", "error")
                self.speak(
                    "Mikrofon topilmadi. "
                    "Iltimos, ochilgan Windows oynasida mikrofon ruhsatini yoqing."
                )
                self.open_windows_mic_permission()
                self.emit_log(">>> 15 soniya kutilmoqda...", "info")
                for i in range(15, 0, -1):
                    self.socketio.emit('log', {'msg': f'    {i} soniya qoldi...', 'type': 'info'})
                    time.sleep(1)
            elif attempt == 1:
                self.emit_log("Yana 5 soniya kutilmoqda...", "error")
                time.sleep(5)

        self.speak("Mikrofon topilmadi. Mikrafonni ulab, dasturni qaytadan ishga tushiring.")
        return False

    # ----------------------------------------------------------
    #  Buyruqni qayta ishlash: Ovoz → Gemini → CMD → Bajar
    # ----------------------------------------------------------
    def process_command(self, text):
        """
        1. Ovozdan kelgan matn Gemini ga yuboriladi
        2. Gemini Windows CMD buyrug'ini yozib beradi
        3. CMD avtomatik bajariladi
        4. Natija ovozda aytiladi
        """
        prompt = f"""Sen JARVIS — Windows kompyuterni boshqaruvchi o'zbek tilidagi AI yordamchisan.

Foydalanuvchi: "{text}"

Sening vazifang: nima xohlayotganini tushun va Windows CMD buyrug'ini yoz.

Javob FAQAT JSON:
{{
  "cmd": "Windows CMD buyrug'i, YOKI URL, YOKI dastur nomi",
  "response": "O'zbek tilida qisqa javob",
  "type": "cmd yoki url yoki app yoki reply"
}}

Misollar:
- "Android studioni och" → {{"cmd": "Android Studio", "response": "Android Studio ochilmoqda!", "type": "app"}}
- "Telegramni och" → {{"cmd": "Telegram", "response": "Telegram ochilmoqda!", "type": "app"}}
- "Chrome och" → {{"cmd": "Google Chrome", "response": "Chrome ochilmoqda!", "type": "app"}}
- "musiqa qo'y" → {{"cmd": "https://www.youtube.com/results?search_query=uzbek+music", "response": "Musiqa qo'yilmoqda!", "type": "url"}}
- "Youtube och" → {{"cmd": "https://www.youtube.com", "response": "YouTube ochilmoqda!", "type": "url"}}
- "Google och" → {{"cmd": "https://www.google.com", "response": "Google ochilmoqda!", "type": "url"}}
- "Toshkent ob-havosi" → {{"cmd": "https://www.google.com/search?q=Toshkent+ob-havo", "response": "Ob-havo qidirilmoqda!", "type": "url"}}
- "Kompyuterni o'chir" → {{"cmd": "shutdown /s /t 10", "response": "10 soniyadan keyin o'chiriladi!", "type": "cmd"}}
- "Salom" → {{"cmd": "", "response": "Salom! Qanday yordam kerak?", "type": "reply"}}

QOIDALAR:
- "type": "url"  → brauzerda ochiladi
- "type": "app"  → Dasturlarni (Android Studio, Word, Telegram) Windows qidiruvi orqali ochish
- "type": "cmd"  → Faqat tizim buyruqlari (shutdown, explorer, cmd)
- "type": "reply" → faqat gapiraman
- Faqat toza JSON. Markdown YO'Q.
"""
        try:
            self.emit_log("Gemini ga yuborilmoqda...", "info")
            self.socketio.emit('status', {'status': 'processing'})

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            result_text = response.text.strip()

            # Markdown tozalash
            for prefix in ["```json", "```"]:
                if result_text.startswith(prefix):
                    result_text = result_text[len(prefix):]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            data     = json.loads(result_text.strip())
            cmd      = data.get("cmd", "").strip()
            reply    = data.get("response", "Bajardim.")
            cmd_type = data.get("type", "reply")

            # Log
            if cmd:
                self.emit_log(f"[{cmd_type.upper()}] {cmd}", "neon")

            # Ovozda ayt
            self.speak(reply)

            # Bajar
            if cmd and cmd_type == "url":
                if cmd.lower().startswith("start "):
                    cmd = cmd[6:].strip()
                # Python modullari (webbrowser, os.startfile) xato bersa, to'g'ridan-to'g'ri CMD orqali ochamiz
                subprocess.Popen(f'start "" "{cmd}"', shell=True)
            elif cmd and cmd_type == "app":
                try:
                    import pyautogui
                    pyautogui.press('win')
                    time.sleep(0.8)
                    pyautogui.write(cmd, interval=0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                except Exception as e:
                    self.emit_log(f"PyAutoGUI ishlamadi: {e}, PowerShellga o'tilmoqda", "info")
                    ps_script = f"(New-Object -ComObject WScript.Shell).SendKeys('^{{ESC}}'); Start-Sleep -Milliseconds 500; (New-Object -ComObject WScript.Shell).SendKeys('{cmd}'); Start-Sleep -Milliseconds 500; (New-Object -ComObject WScript.Shell).SendKeys('{{ENTER}}')"
                    subprocess.Popen(f'powershell -c "{ps_script}"', shell=True)
            elif cmd and cmd_type == "cmd":
                subprocess.Popen(cmd, shell=True)

        except json.JSONDecodeError:
            self.emit_log("JSON parse xatoligi.", "error")
            try:
                self.speak(response.text[:200])
            except Exception:
                self.speak("Xatolik yuz berdi.")
        except Exception as e:
            self.emit_log(f"Gemini xatoligi: {str(e)}", "error")
            self.speak("Kechirasiz, xatolik yuz berdi.")

    # ----------------------------------------------------------
    #  Asosiy tinglash sikli
    # ----------------------------------------------------------
    def start(self):
        with self._lock:
            if self.is_running:
                return
            self.is_running = True

        try:
            if not self.check_and_request_mic():
                self.is_running = False
                return

            self.speak("Salom! Men Jarvisman, sizning ovozli yordamchingiz. Qanday yordam kerak? Buyuring.")
            self.emit_log("[TAYYOR] Jarvis faol! Gapiring...", "neon")

            self.emit_log("Shovqin darajasi moslanmoqda...", "info")
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            self.emit_log("[OK] Eshitish boshlandi.", "neon")

            while self.is_running:
                try:
                    self.socketio.emit('status', {'status': 'listening'})
                    self.emit_log("[ Eshityapman... ]", "info")

                    with sr.Microphone() as source:
                        audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=12)

                    self.socketio.emit('status', {'status': 'processing'})
                    self.emit_log("Ovoz tahlil qilinmoqda...", "info")

                    text = self.recognizer.recognize_google(audio, language="uz-UZ")
                    self.emit_log(f"Siz: {text}", "user")

                    # Chiqish buyruqlari
                    exit_words = ["xayr", "chiqish", "toxta", "to'xta", "stop"]
                    if any(w in text.lower() for w in exit_words):
                        self.speak("Xayr! Salomat bo'ling.")
                        self.is_running = False
                        break

                    self.process_command(text)

                except sr.WaitTimeoutError:
                    self.emit_log("Ovoz eshitilmadi, kutmoqda...", "info")
                    continue
                except sr.UnknownValueError:
                    self.emit_log("Ovoz tushunilmadi, qayta uring.", "info")
                    continue
                except sr.RequestError as e:
                    self.emit_log(f"Google ulanish xatoligi: {str(e)}", "error")
                    self.speak("Internetga ulanishda xatolik.")
                    break
                except Exception as e:
                    self.emit_log(f"Kutilmagan xatolik: {str(e)}", "error")

        except Exception as e:
            self.emit_log(f"Asosiy jarayonda xatolik: {str(e)}", "error")
        finally:
            self.is_running = False
            self.socketio.emit('status', {'status': 'idle'})
            self.emit_log("Jarvis toxtatildi.", "info")
