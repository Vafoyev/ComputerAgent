# 🤖 Humanoid Robot & JARVIS Assistant - Foydalanuvchi Qo'llanmasi (User Manual)

Ushbu hujjat **JARVIS Voice Assistant & Humanoid Robot Integration Service** loyihasidan foydalanish, uni gumanoid robotga ulash, REST API so'rovlarini yuborish, **Dinamik HTML UI Generator** va mahalliy muhitda sozlash bo'yicha to'liq qo'llanmadir.

---

## 📌 1. Tizim haqida umumiy ma'lumot

Ushbu servis 3 ta asosiy funksional qismdan iborat:

1. **Ovozli Yordamchi Rejimi (Voice Mode):** Mikrofon orqali o'zbekcha ovozli buyruqlarni eshitib, Gemini AI yordamida Windows tizimini boshqaradi va javobni ovozda (`edge-tts`) aytadi.
2. **Gumanoid Robot API Rejimi (Headless/Silent Mode):** Robot mahalliy tarmoq (IP:Port) orqali HTTP REST API so'rovlarini yuboradi. Servis vazifani bajaradi, dinamikdan ovoz chiqarmaydi (ovozsiz rejim) va to'liq bajarilish holati haqida JSON formatida robotga javob qaytaradi.
3. **Dinamik AI HTML Generator (Dynamic WebView Generator):** Robot yoki foydalanuvchi murakkab topshiriq (vizual panel, grafik, status dashboard) yuborganida, Gemini AI avtomatik tarzda chiroyli HTML/CSS/JS vizual interfeys kodini yaratadi va uni brauzer/webview oynasida namoyish etadi.

---

## 🚀 2. Ishga tushirish (Getting Started)

### Muhitni sozlash (Environment Variables)

```bash
# Windows PowerShell:
$env:GEMINI_API_KEY="Sizning_Gemini_API_Kalitingiz"

# Windows CMD:
set GEMINI_API_KEY=Sizning_Gemini_API_Kalitingiz
```

### Servisni ishga tushirish

```bash
python app.py
```

Dastur ishga tushgach:
- Veb-interfeys: `http://127.0.0.1:5000`
- Gumanoid Robot API porti: `5000`

---

## 🎨 3. Dinamik AI HTML WebView Generator Qanday Ishlaydi?

1. **Topshiriq Qabul Qilish:** Robot yoki foydalanuvchi vizual interfeys yoki statistik ma'lumot talab qiluvchi vazifa yuboradi.
2. **HTML Generatsiya:** Gemini AI avtomatik ravishda zamonaviy (glassmorphism, neon, animatsiyali) HTML/CSS/JS kodini shakllantiradi.
3. **Avto-WebView / Brauzer:** Yaratilgan HTML fayl `generated_views/` papkasida saqlanib, brauzerda (yoki WebView oynasida) `http://127.0.0.1:5000/view/<view_id>` manzili orqali avtomatik ochiladi va ko'rsatiladi.

---

## 📡 4. Gumanoid Robot uchun REST API Hujjatlari

### 4.1. Robot Vazifa Yuborishi (Task Execution)

- **Endpoint:** `POST /api/task`
- **Header:** `Content-Type: application/json`
- **Request Body:**

```json
{
  "task": "Gumanoid robot monitoring paneli uchun HTML UI yarat va Chrome brauzerini och",
  "robot_id": "gumanoid_robot_01",
  "silent": true,
  "generate_ui": true
}
```

- **Response Body:**

```json
{
  "status": "success",
  "robot_id": "gumanoid_robot_01",
  "task": "Gumanoid robot monitoring paneli uchun HTML UI yarat va Chrome brauzerini och",
  "ai_response": "HTML monitoring UI yaratildi va ochildi!",
  "generated_view_url": "http://127.0.0.1:5000/view/view_83921",
  "command_executed": "start \"\" \"http://127.0.0.1:5000/view/view_83921\"",
  "command_type": "url",
  "execution_time_ms": 450,
  "timestamp": 1723425123
}
```

---

### 4.2. Servis Holatini Tekshirish (Health Check)

- **Endpoint:** `GET /api/status`
- **Response Body:**

```json
{
  "status": "online",
  "service": "JARVIS Robot Controller",
  "active_mode": "headful/silent_api",
  "html_generator": "enabled",
  "uptime_seconds": 1240,
  "system": "Windows 11"
}
```

---

## 📝 5. Hujjatlashtirish Qoidasi

Ushbu `USER_GUIDE.md` hujjati loyihaga kiritiladigan har bir yangi funksiya bilan **doimiy ravishda yangilanib boriladi**.
