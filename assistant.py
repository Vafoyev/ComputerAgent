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
import urllib.parse
import urllib.request
import re

# ============================================================
#  Ovoz chiqarish (TTS Backend)
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

EDGE_VOICE = "uz-UZ-MadinaNeural"

# ============================================================
#  Gemini API Neural Core
# ============================================================
from google import genai

client = None

DEFAULT_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if not DEFAULT_GEMINI_KEY:
    DEFAULT_GEMINI_KEY = "AQ." + "Ab8RN6K5h6dqjTcKAwlMZAckUaTyonaxoTxqah0VfHmbXx_1FA"

def get_genai_client():
    global client
    if client is not None:
        return client
    key = os.getenv("GEMINI_API_KEY", DEFAULT_GEMINI_KEY).strip()
    if key:
        try:
            client = genai.Client(api_key=key)
            return client
        except Exception:
            return None
    return None

# ============================================================
#  PROFESSIONAL SYSTEM PROMPTS
# ============================================================
COMMAND_DISPATCHER_SYSTEM_PROMPT = """Sen JARVIS Neural Core — Gumanoid Robot va Windows Operatsion Tizimining yuqori darajadagi Avtonom Muhandisisan.

Sening vazifang: Gumanoid robot yoki foydalanuvchidan kelgan har qanday tabiiy tildagi vazifani chuqur tahlil qilib, Windows CMD yoki PowerShell uchun 100% aniq va ishlaydigan terminal buyrug'ini shakllantirishdir.

JAVOB FAQAT TOZA JSON FORMATIDA BO'LISHI SHART (Markdown va har qanday ortiqcha matnsiz):
{
  "cmd": "Windows CMD/PowerShell buyrug'i (masalan: start chrome https://google.com, tasklist, shutdown, explorer va h.k.)",
  "response": "Gumanoid robot va foydalanuvchi uchun o'zbek tilidagi professional va tushunarli javob xulosasi",
  "type": "cmd | app | url | reply",
  "need_visual_ui": true,
  "confidence_score": 0.99
}

BUYRUQ TURLARI (TYPE):
- "url"  -> Brauzerda ochilishi kerak bo'lgan veb havolalar va qidiruvlar (start "" "URL")
- "app"  -> Windows ish stoli dasturlari (Telegram, Android Studio, Code, Notepad, Calc, Word, Excel)
- "cmd"  -> Tizim buyruqlari (PowerShell, CMD, fayl boshqaruvi, diagnostika, jarayonlar)
- "reply" -> Faqat ma'lumot beruvchi matnli javoblar

QOIDALAR:
1. Windows muhitiga mos keluvchi sintaksis ishlatilsin.
2. Markdown syntax (```json ...) umuman bo'lmasin. Faqat toza parse bo'ladigan JSON qaytar.
"""

HTML_GENERATOR_SYSTEM_PROMPT = """Sen Ultra-Modern UI/UX Muhandisisan. Gumanoid robot va foydalanuvchi uchun davrining eng yetakchi Cyberpunk, Futuristic Glassmorphism uslubida HTML Dashboard / WebView sahifalarini generate qilasan.

TALABLAR:
1. Faqat bitta toza HTML fayl (ichida CSS <style> va JS <script> bilan).
2. Vizual dizayn: Dark theme (#06080e), Neon Cyber ko'k (#00f3ff), Neon Pushti (#ff007f), Neon Yashil (#00ff88), Glassmorphism backdrop blur effect.
3. Sahifada quyidagi modullar bo'lsin:
   - Header: Gumanoid Robot telemetry statusi (Online, CPU Load, Sync State).
   - Vazifa kartasi: Topshiriq matni va AI tahlili.
   - Bajarilish progress-bari (animated loader / glowing meter).
   - Real-vaqtli interaktiv tugmalar (Refresh, Task Details, Robot HUD toggle).
4. Markdown teglari (```html) bo'lmasin, toza HTML kodini ber!
"""

def get_youtube_autoplay_url(query):
    """YouTube-da so'ralgan qo'shiq/videoni avtomatik qidirib, birinchi videoni avto-ijro (&autoplay=1) bilan ochadi"""
    try:
        clean_query = query.lower().replace("youtube", "").replace("youtubeda", "").replace("youtube'da", "").replace("qo'yib ber", "").replace("qoyib ber", "").replace("qo'y", "").replace("qoy", "").replace("eshitaylik", "").replace("ijro et", "").replace("ochib ber", "").replace("och", "").strip()
        if not clean_query:
            clean_query = "O'zbekiston madhiyasi"
            
        encoded_query = urllib.parse.quote_plus(clean_query)
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=3).read().decode()
        vids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
        if vids:
            return f"https://www.youtube.com/watch?v={vids[0]}&autoplay=1"
        return search_url
    except Exception:
        return f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"

class VoiceAssistant:
    def __init__(self, socketio):
        self.socketio = socketio
        self.is_running = False
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self._lock = threading.Lock()

    def emit_card(self, title, content, card_type="info", details=None):
        """Web UI uchun real-vaqt rejimida karta xabari yuborish"""
        payload = {
            "title": title,
            "content": content,
            "type": card_type,
            "details": details or {},
            "timestamp": time.strftime("%H:%M:%S")
        }
        if self.socketio:
            self.socketio.emit('card', payload)

    def emit_stage(self, stage_name, description, progress_pct=0):
        """Bosqichma-bosqich jarayon telemetriyasi"""
        if self.socketio:
            self.socketio.emit('stage_update', {
                "stage": stage_name,
                "description": description,
                "progress": progress_pct,
                "timestamp": time.strftime("%H:%M:%S")
            })

    def trigger_typing_sfx(self, duration_sec=1.5):
        """Klaviatura 'tq-tq-tq' sado efektini ishga tushirish"""
        if self.socketio:
            self.socketio.emit('typing_sfx', {'duration': duration_sec})

    def speak(self, text, silent=False):
        """Ovozda aytish (Asinxron background thread — HTTP so'rovlarini to'sib qo'ymaydi)"""
        if silent:
            return

        self.emit_card("JARVIS Ovoz", text, "ai")
        def _do_speak():
            try:
                if TTS_BACKEND == "edge":
                    self._speak_edge(text)
                elif TTS_BACKEND == "gtts":
                    self._speak_gtts(text)
                else:
                    self._speak_pyttsx3(text)
            except Exception as e:
                self.emit_card("Ovoz Chiqarish Xatosi", str(e), "warning")
        
        threading.Thread(target=_do_speak, daemon=True).start()

    def _speak_edge(self, text):
        try:
            async def _main():
                communicate = edge_tts.Communicate(text, EDGE_VOICE)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    tmp_path = f.name
                await communicate.save(tmp_path)
                return tmp_path

            tmp_mp3 = asyncio.run(_main())
            self._play_mp3(tmp_mp3)
        except Exception as e:
            self.emit_card("Edge-TTS Xatosi", str(e), "error")
            self._speak_gtts(text, lang='ru')

    def _speak_gtts(self, text, lang='ru'):
        from gtts import gTTS
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tmp_path = f.name
        gTTS(text=text, lang=lang).save(tmp_path)
        self._play_mp3(tmp_path)

    def _speak_pyttsx3(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def _play_mp3(self, file_path):
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            os.remove(file_path)
        except Exception:
            pass

    def _call_gemini_models(self, prompt):
        ai_client = get_genai_client()
        if not ai_client:
            return None
        models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-flash"]
        for m in models_to_try:
            try:
                res = ai_client.models.generate_content(model=m, contents=prompt)
                if res and res.text:
                    return res.text.strip()
            except Exception:
                continue
        return None

    def generate_dynamic_html(self, task_text, ai_response_text):
        """AI orqali gumanoid robot uchun dinamik HTML5 HUD yaratadi"""
        try:
            prompt = f"""Sen Cyberpunk va Sci-Fi gumanoid robot interfeyslari bo'yicha ekspert dizaynersan.
Vazifa: "{task_text}"
AI javobi: "{ai_response_text}"

Gumanoid robot interfeysi uchun faqat toza, muxtasar HTML va inline CSS tayyorla. Hech qanday markdown belgilari ko'rsatma. FAQAT <html> bilan boshlanib </html> bilan tugaydigan kod qaytar."""
            
            result_text = self._call_gemini_models(prompt)
            if result_text:
                html_code = result_text
                for prefix in ["```html", "```"]:
                    if html_code.startswith(prefix):
                        html_code = html_code[len(prefix):]
                if html_code.endswith("```"):
                    html_code = html_code[:-3]
            else:
                html_code = f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8"><title>JARVIS Humanoid HUD</title>
<style>
body {{ background: #06080e; color: #00f3ff; font-family: 'Segoe UI', Tahoma, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
.card {{ background: rgba(14, 20, 32, 0.85); border: 2px solid rgba(0, 243, 255, 0.3); border-radius: 20px; padding: 35px; box-shadow: 0 10px 40px rgba(0,243,255,0.25); text-align: center; max-width: 550px; width: 90%; backdrop-filter: blur(20px); }}
h1 {{ color: #00ff88; font-size: 2rem; margin-bottom: 12px; letter-spacing: 2px; text-transform: uppercase; }}
p {{ color: #e6edf3; font-size: 1.1rem; line-height: 1.6; margin: 10px 0; }}
.status-badge {{ background: rgba(0,255,136,0.15); border: 1px solid #00ff88; color: #00ff88; padding: 10px 20px; border-radius: 30px; display: inline-block; margin-top: 20px; font-weight: bold; text-shadow: 0 0 8px rgba(0,255,136,0.5); }}
.meter {{ width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; margin-top: 20px; }}
.meter-bar {{ width: 100%; height: 100%; background: linear-gradient(90deg, #00f3ff, #00ff88); animation: pulse 2s infinite; }}
@keyframes pulse {{ 0% {{ opacity: 0.6; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.6; }} }}
</style>
</head>
<body>
<div class="card">
  <h1>🤖 HUMANOID ROBOT HUD</h1>
  <p><strong>Topshiriq:</strong> {task_text}</p>
  <p><strong>AI Tahlil:</strong> {ai_response_text}</p>
  <div class="meter"><div class="meter-bar"></div></div>
  <div class="status-badge">🟢 Tizim va Robot Holati: Sinxronizatsiyada</div>
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
        """Professional Multi-Stage Task Executor with Full Process Logging"""
        start_time = time.time()
        process_logs = []

        def log_step(msg):
            ts = time.strftime("%H:%M:%S")
            log_entry = f"[{ts}] {msg}"
            process_logs.append(log_entry)
            print(f"🔹 [JARVIS CORE TELEMETRY] {log_entry}")

        log_step(f"Vazifa qabul qilindi: '{text}'")
        self.emit_stage("received", f"So'rov qabul qilindi: '{text}'", 10)
        self.emit_card("📌 Yangi Topshiriq", text, "task")
        self.trigger_typing_sfx(duration_sec=1.5)
        if self.socketio:
            self.socketio.emit('status', {'status': 'processing'})

        prompt = f"""{COMMAND_DISPATCHER_SYSTEM_PROMPT}

Foydalanuvchi/Robot vazifasi: "{text}"
"""
        cmd = ""
        reply = ""
        cmd_type = "cmd"
        need_visual_ui = generate_ui

        try:
            log_step("Gemini AI Neural Core tahlili boshlandi")
            self.emit_stage("ai_analysis", "Gemini AI Neural Core buyruqni tahlil qilmoqda...", 35)
            lower_text = text.lower().strip()

            # YouTube / Music Autoplay Detection
            if any(k in lower_text for k in ["youtube", "madhiya", "musiqa", "qo'shiq", "muzika", "video", "kuy", "qo'yib ber", "qoyib ber"]):
                log_step("YouTube / Audio ijro rejimi aniqlandi")
                yt_url = get_youtube_autoplay_url(text)
                cmd = f'start "" "{yt_url}"'
                cmd_type = "cmd"
                reply = "YouTube platformasida audio va video avtomatik ravishda ijro etilmoqda!"
                log_step(f"YouTube Avto-ijro URL shakllantirildi: {yt_url}")
            else:
                result_text = self._call_gemini_models(prompt)
                if result_text:
                    for prefix in ["```json", "```"]:
                        if result_text.startswith(prefix):
                            result_text = result_text[len(prefix):]
                    if result_text.endswith("```"):
                        result_text = result_text[:-3]

                    data = json.loads(result_text.strip())
                    cmd = data.get("cmd", "").strip()
                    reply = data.get("response", "Vazifa bajarildi.")
                    cmd_type = data.get("type", "cmd")
                    need_visual_ui = data.get("need_visual_ui", False) or generate_ui
                    log_step(f"AI Model Natijasi: cmd='{cmd}', type='{cmd_type}'")
                else:
                    log_step("AI Modellari band, tezkor algoritmlar ishga tushdi")
                    if "chrome" in lower_text or "google" in lower_text or "browser" in lower_text:
                        cmd = "start https://www.google.com"
                        cmd_type = "cmd"
                        reply = "Chrome va Google brauzeri ochilmoqda!"
                    elif "notepad" in lower_text or "bloknot" in lower_text:
                        cmd = "start notepad"
                        cmd_type = "cmd"
                        reply = "Notepad (Bloknot) dasturi ochilmoqda!"
                    elif "kalkulyator" in lower_text or "calc" in lower_text:
                        cmd = "start calc"
                        cmd_type = "cmd"
                        reply = "Kalkulyator dasturi ochilmoqda!"
                    elif "telegram" in lower_text:
                        cmd = "start Telegram"
                        cmd_type = "cmd"
                        reply = "Telegram dasturi ochilmoqda!"
                    elif "cmd" in lower_text or "terminal" in lower_text or "command" in lower_text:
                        cmd = "start cmd"
                        cmd_type = "cmd"
                        reply = "Windows Command Prompt (CMD) ochilmoqda!"
                    elif "explorer" in lower_text or "papka" in lower_text or "fayl" in lower_text:
                        cmd = "explorer"
                        cmd_type = "cmd"
                        reply = "Windows Fayl Explorer papkasi ochilmoqda!"
                    else:
                        cmd = text.strip()
                        cmd_type = "cmd"
                        reply = f"Topshiriq bajarilmoqda: {text}"

            self.emit_card("💡 AI Tahlili", reply, "ai", {"cmd": cmd, "type": cmd_type})
            self.speak(reply, silent=silent)
            log_step("Ovozli bildirishnoma asinxron ishga tushirildi")

            view_url = None
            if need_visual_ui:
                log_step("Dinamik HTML5 HUD generatsiyasi boshlandi")
                view_url = self.generate_dynamic_html(text, reply)
                log_step(f"HUD sahifa URL: {view_url}")

            # Command execution with output & exit code capture
            cmd_output = ""
            exit_code = 0
            if cmd:
                log_step(f"Terminal buyrug'i ijrosi: '{cmd}'")
                self.emit_stage("execution", f"Windows tizim buyrug'i bajarilmoqda: {cmd}", 80)
                self.trigger_typing_sfx(duration_sec=1.0)
                
                # Direct subprocess execution for Windows CMD / PowerShell
                try:
                    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    try:
                        stdout, stderr = proc.communicate(timeout=5)
                        cmd_output = stdout.strip() or stderr.strip()
                        exit_code = proc.returncode
                    except subprocess.TimeoutExpired:
                        cmd_output = "Buyruq orqa fonda ishga tushirildi."
                    log_step(f"Buyruq bajarildi (Exit code: {exit_code})")
                    self.emit_card("⚙️ Tizim Buyrug'i Bajarildi", cmd, "cmd", {"output": cmd_output, "exit_code": exit_code})
                except Exception as ex:
                    log_step(f"Xatolik buyruq bajarishda: {str(ex)}")
                    self.emit_card("⚠️ Buyruq Bajarish Xatosi", str(ex), "error")

            if view_url and not silent:
                webbrowser.open(view_url)

            elapsed_ms = int((time.time() - start_time) * 1000)
            log_step(f"Vazifa muvaffaqiyatli yakunlandi ({elapsed_ms}ms)")
            self.emit_stage("completed", "Vazifa muvaffaqiyatli yakunlandi", 100)
            if self.socketio:
                self.socketio.emit('status', {'status': 'idle'})

            return {
                "status": "success",
                "robot_id": "gumanoid_robot",
                "task": text,
                "ai_response": reply,
                "command_executed": cmd,
                "command_type": cmd_type,
                "command_output": cmd_output,
                "exit_code": exit_code,
                "generated_view_url": view_url,
                "execution_time_ms": elapsed_ms,
                "process_logs": process_logs,
                "timestamp": int(time.time())
            }

        except Exception as e:
            log_step(f"Kritik Xatolik: {str(e)}")
            self.emit_card("Xatolik", str(e), "error")
            self.emit_stage("failed", f"Xatolik: {str(e)}", 100)
            if self.socketio:
                self.socketio.emit('status', {'status': 'idle'})
            return {
                "status": "error",
                "task": text,
                "error": str(e),
                "process_logs": process_logs,
                "timestamp": int(time.time())
            }

    def start(self):
        """Ovozli rejim asosiy sikli"""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True

        try:
            self.emit_card("JARVIS Neural Core Faol", "Ovozli va Robot API muloqot tayyor!", "info")
            self.speak("Salom! Men Jarvis Neural Core — sizning ovozli yordamchingiz hamda gumanoid robot boshqaruvchisiman.")

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
