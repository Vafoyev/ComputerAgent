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
#  Ovoz chiqarish (TTS Backend Check)
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

EDGE_VOICE = "uz-UZ-MadinaNeural"  # O'zbek tili ayol ovozi

# ============================================================
#  Gemini API
# ============================================================
from google import genai

client = None

def get_genai_client():
    global client
    if client is not None:
        return client
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        try:
            client = genai.Client(api_key=key)
            return client
        except Exception:
            return None
    return None


class VoiceAssistant:
    def __init__(self, socketio):
        self.socketio = socketio
        self.recognizer = sr.Recognizer()
        self.is_running = False
        self._lock = threading.Lock()

        if TTS_BACKEND == "pyttsx3":
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)

    def emit_card(self, title, message, card_type="task", details=None):
        """
        Konsol loglari o'rniga foydalanuvchi va robot uchun chiroyli Vizual Karta yuborish
        """
        payload = {
            "title": title,
            "message": message,
            "type": card_type,  # task, success, info, error, ai, cmd, ui
            "details": details or {},
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.socketio.emit('card', payload)

    def trigger_typing_sfx(self, duration_sec=1.5):
        """Klaviatura 'tq-tq-tq' chertilish ovozi efektini UI va soket orqali ishga tushirish"""
        self.socketio.emit('typing_sfx', {'duration': duration_sec})

    def speak(self, text, silent=False):
        """Ovozda aytish (Robot API rejimida silent=True bo'lganda ovozsiz)"""
        if silent:
            return

        self.emit_card("JARVIS Ovoz", text, "ai")
        try:
            if TTS_BACKEND == "edge":
                self._speak_edge(text)
            elif TTS_BACKEND == "gtts":
                self._speak_gtts(text)
            else:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            self.emit_card("Ovoz Xatosi", str(e), "error")

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
            self.emit_card("Edge-TTS Xatosi", str(e), "error")
            self._speak_gtts(text, lang='ru')

    def _speak_gtts(self, text, lang='ru'):
        from gtts import gTTS
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tmp_path = f.name
        gTTS(text=text, lang=lang).save(tmp_path)
        self._play_mp3(tmp_path)

    def generate_dynamic_html(self, task_text, ai_response_text):
        """
        Gemini AI orqali topshiriq uchun dinamik HTML vizual WebView kartasini generatsiya qilish
        """
        self.trigger_typing_sfx(duration_sec=2.0)
        prompt = f"""Senga topshiriq: Gumanoid robot va foydalanuvchi uchun zamonaviy Cyberpunk/Glassmorphism uslubida HTML vizual sahifa yarat.
Topshiriq: "{task_text}"
AI Xulosasi: "{ai_response_text}"

Talablar:
- Faqat toza HTML code (bitta fayl, ichida CSS va JS bilan).
- Dark mode, neon ranglar (#00f3ff, #ff007f, #00ff88), zamonaviy shriftlar.
- Jonli animatsiyalar, vazifa status kartasi, robot holat vidjeti va bajarilgan ishlar paneli bo'lsin.
- Markdown va ```html teglari YO'Q, FAQAT HTML KODNI QAYTAR!
"""
        try:
            ai_client = get_genai_client()
            if ai_client:
                response = ai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                html_code = response.text.strip()
                for prefix in ["```html", "```"]:
                    if html_code.startswith(prefix):
                        html_code = html_code[len(prefix):]
                if html_code.endswith("```"):
                    html_code = html_code[:-3]
            else:
                html_code = f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8"><title>JARVIS Humanoid Dashboard</title>
<style>
body {{ background: #0a0c10; color: #00f3ff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
.card {{ background: rgba(18,22,31,0.9); border: 2px solid #00f3ff; border-radius: 16px; padding: 30px; box-shadow: 0 0 20px rgba(0,243,255,0.3); text-align: center; max-width: 500px; }}
h1 {{ color: #00ff88; font-size: 1.8rem; margin-bottom: 10px; }}
p {{ color: #e6edf3; font-size: 1.1rem; line-height: 1.5; }}
.status {{ background: rgba(0,255,136,0.15); border: 1px solid #00ff88; color: #00ff88; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-top: 15px; font-weight: bold; }}
</style>
</head>
<body>
<div class="card">
  <h1>🤖 Gumanoid Robot Dashbordi</h1>
  <p><strong>Topshiriq:</strong> {task_text}</p>
  <p><strong>AI Natijasi:</strong> {ai_response_text}</p>
  <div class="status">🟢 Tizim va Robot Holati: Faol</div>
</div>
</body>
</html>"""

            view_id = f"view_{int(time.time())}"
            views_dir = os.path.join(os.path.abspath("."), "generated_views")
            os.makedirs(views_dir, exist_ok=True)
            view_path = os.path.join(views_dir, f"{view_id}.html")

            with open(view_path, "w", encoding="utf-8") as f:
                f.write(html_code.strip())

            view_url = f"http://127.0.0.1:5000/view/{view_id}"
            self.emit_card("🎨 Dynamic HTML UI Yaratildi", f"Sahifa: {view_url}", "ui", {"url": view_url})
            return view_url
        except Exception as e:
            self.emit_card("HTML Generatsiya Xatosi", str(e), "error")
            return None

    def execute_task(self, text, silent=False, generate_ui=True):
        """
        Asosiy Vazifa Ijrochisi (Ovozli Rejim ham, Robot REST API Rejimi ham shu funksiyani ishlatadi)
        """
        start_time = time.time()
        self.emit_card("📌 Yangi Topshiriq", text, "task")
        self.trigger_typing_sfx(duration_sec=1.5)
        self.socketio.emit('status', {'status': 'processing'})

        prompt = f"""Sen JARVIS — Gumanoid robot va Windows kompyuterni boshqaruvchi o'zbek tilidagi AI yordamchisan.

Foydalanuvchi/Robot vazifasi: "{text}"

Vazifani tushun va Windows CMD/PowerShell buyrug'ini tayyorla.

Javob FAQAT JSON formatida bo'lsin:
{{
  "cmd": "Windows CMD/PowerShell buyrug'i, YOKI URL, YOKI dastur nomi",
  "response": "O'zbek tilida qisqa va tushunarli javob",
  "type": "cmd yoki url yoki app yoki reply",
  "need_visual_ui": true
}}

Misollar:
- "Chrome och va robotehnika izla" → {{"cmd": "https://www.google.com/search?q=robotehnika", "response": "Chrome ochilib, robotehnika qidirilmoqda!", "type": "url", "need_visual_ui": true}}
- "Telegramni och" → {{"cmd": "Telegram", "response": "Telegram ochilmoqda!", "type": "app", "need_visual_ui": false}}
- "Kompyuterni o'chir" → {{"cmd": "shutdown /s /t 10", "response": "Sistemani 10 soniyadan keyin o'chirish tayyorlandi", "type": "cmd", "need_visual_ui": false}}

QOIDALAR: Faqat toza JSON. Markdown YO'Q.
"""
        try:
            ai_client = get_genai_client()
            if ai_client:
                response = ai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                result_text = response.text.strip()

                for prefix in ["```json", "```"]:
                    if result_text.startswith(prefix):
                        result_text = result_text[len(prefix):]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]

                data = json.loads(result_text.strip())
                cmd = data.get("cmd", "").strip()
                reply = data.get("response", "Vazifa bajarildi.")
                cmd_type = data.get("type", "reply")
                need_visual_ui = data.get("need_visual_ui", False) or generate_ui
            else:
                # Smart fallback parse for basic commands when GEMINI_API_KEY is not set
                lower_text = text.lower()
                need_visual_ui = generate_ui
                if "chrome" in lower_text or "google" in lower_text or "izla" in lower_text:
                    cmd = "https://www.google.com"
                    cmd_type = "url"
                    reply = "Chrome ochilib, so'rovingiz bajarilmoqda!"
                elif "notepad" in lower_text or "bloknot" in lower_text:
                    cmd = "notepad"
                    cmd_type = "app"
                    reply = "Notepad (Bloknot) ochilmoqda!"
                elif "telegram" in lower_text:
                    cmd = "Telegram"
                    cmd_type = "app"
                    reply = "Telegram dasturi ochilmoqda!"
                elif "youtube" in lower_text or "musiqa" in lower_text:
                    cmd = "https://www.youtube.com"
                    cmd_type = "url"
                    reply = "YouTube ochilmoqda!"
                else:
                    cmd = ""
                    cmd_type = "reply"
                    reply = f"Topshiriq qabul qilindi: {text}"

            self.emit_card("💡 AI Tahlili", reply, "ai", {"cmd": cmd, "type": cmd_type})

            # Ovoz chiqarish (silent=True bo'lganda ovozsiz)
            self.speak(reply, silent=silent)

            view_url = None
            if need_visual_ui:
                view_url = self.generate_dynamic_html(text, reply)

            # Buyruqni Windows tizimida bajarish
            if cmd:
                self.trigger_typing_sfx(duration_sec=1.0)
                if cmd_type == "url":
                    target_url = cmd
                    if target_url.lower().startswith("start "):
                        target_url = target_url[6:].strip()
                    subprocess.Popen(f'start "" "{target_url}"', shell=True)
                    self.emit_card("🌐 URL Ochildi", target_url, "cmd")
                elif cmd_type == "app":
                    try:
                        import pyautogui
                        pyautogui.press('win')
                        time.sleep(0.5)
                        pyautogui.write(cmd, interval=0.04)
                        time.sleep(0.4)
                        pyautogui.press('enter')
                        self.emit_card("🚀 Dastur Ochildi", cmd, "cmd")
                    except Exception as e:
                        ps_script = f"(New-Object -ComObject WScript.Shell).SendKeys('^{{ESC}}'); Start-Sleep -Milliseconds 400; (New-Object -ComObject WScript.Shell).SendKeys('{cmd}'); Start-Sleep -Milliseconds 400; (New-Object -ComObject WScript.Shell).SendKeys('{{ENTER}}')"
                        subprocess.Popen(f'powershell -c "{ps_script}"', shell=True)
                        self.emit_card("🚀 PowerShell bilan ochildi", cmd, "cmd")
                elif cmd_type == "cmd":
                    subprocess.Popen(cmd, shell=True)
                    self.emit_card("⚙️ Tizim Buyrug'i Bajarildi", cmd, "cmd")

            # WebView URL bo'lsa avtomatik brauzerda ham ochish
            if view_url and not silent:
                webbrowser.open(view_url)

            elapsed_ms = int((time.time() - start_time) * 1000)
            self.socketio.emit('status', {'status': 'idle'})

            return {
                "status": "success",
                "task": text,
                "ai_response": reply,
                "command_executed": cmd,
                "command_type": cmd_type,
                "generated_view_url": view_url,
                "execution_time_ms": elapsed_ms,
                "timestamp": int(time.time())
            }

        except Exception as e:
            self.emit_card("Xatolik", str(e), "error")
            self.socketio.emit('status', {'status': 'idle'})
            return {
                "status": "error",
                "task": text,
                "error": str(e),
                "timestamp": int(time.time())
            }

    def start(self):
        """Ovozli rejim asosiy sikli"""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True

        try:
            self.emit_card("JARVIS Faol", "Ovozli muloqot tayyor!", "info")
            self.speak("Salom! Men Jarvisman, sizning ovozli yordamchingiz hamda gumanoid robot boshqaruvchisiman.")

            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)

            while self.is_running:
                try:
                    self.socketio.emit('status', {'status': 'listening'})
                    with sr.Microphone() as source:
                        audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=12)

                    self.socketio.emit('status', {'status': 'processing'})
                    text = self.recognizer.recognize_google(audio, language="uz-UZ")

                    exit_words = ["xayr", "chiqish", "toxta", "to'xta", "stop"]
                    if any(w in text.lower() for w in exit_words):
                        self.speak("Xayr! Salomat bo'ling.")
                        self.is_running = False
                        break

                    self.execute_task(text, silent=False, generate_ui=True)

                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except sr.RequestError as e:
                    self.emit_card("Google Speech Xatosi", str(e), "error")
                    break
                except Exception as e:
                    self.emit_card("Kutilmagan Xatosi", str(e), "error")
        finally:
            self.is_running = False
            self.socketio.emit('status', {'status': 'idle'})
