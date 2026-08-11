# 🤖 Humanoid Robot & JARVIS Assistant - Foydalanuvchi Qo'llanmasi (User Manual)

Ushbu hujjat **JARVIS Voice Assistant & Humanoid Robot Integration Service** loyihasidan foydalanish, uni gumanoid robotga ulash, REST API so'rovlarini yuborish va mahalliy (local) muhitda sozlash bo'yicha to'liq qo'llanmadir.

---

## 📌 1. Tizim haqida umumiy ma'lumot

Ushbu servis 2 xil rejimda ishlashga mo'ljallangan:

1. **Ovozli Yordamchi Rejimi (Voice Mode):** Mikrofon orqali o'zbekcha ovozli buyruqlarni eshitib, Gemini AI yordamida Windows tizimini boshqaradi va javobni ovozda (`edge-tts`) aytadi.
2. **Gumanoid Robot API Rejimi (Headless/Silent Mode):** Robot mahalliy tarmoq (IP:Port) orqali HTTP REST API so'rovlarini yuboradi. Servis vazifani bajaradi, dinamikdan ovoz chiqarmaydi (ovozsiz rejim) va to'liq bajarilish holati (status, javob, CMD buyrug'i, bajarilish vaqti) haqida JSON formatida robotga javob qaytaradi.

---

## 🚀 2. Ishga tushirish (Getting Started)

### Muhitni sozlash (Environment Variables)

Dasturni ishga tushirishdan oldin Gemini API kalitini o'rnatish lozim:

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
- Veb-interfeys: `http://127.0.0.1:5000` (yoki mahalliy tarmoqdagi IP `http://192.168.x.x:5000`)
- Gumanoid Robot API porti: `5000`

---

## 📡 3. Gumanoid Robot uchun REST API Hujjatlari

Robot servisga HTTP POST va GET so'rovlari orqali ulanadi.

### 3.1. Robot Vazifa Yuborishi (Task Execution)

- **Endpoint:** `POST /api/task`
- **Header:** `Content-Type: application/json`
- **Request Body (So'rov formati):**

```json
{
  "task": "Chrome brauzerini ochib robotehnika bo'yicha izla",
  "robot_id": "gumanoid_robot_01",
  "silent": true
}
```

- **Response Body (Javob formati):**

```json
{
  "status": "success",
  "robot_id": "gumanoid_robot_01",
  "task": "Chrome brauzerini ochib robotehnika bo'yicha izla",
  "ai_response": "Chrome ochilib, robotehnika bo'yicha qidirilmoqda!",
  "command_executed": "start \"\" \"https://www.google.com/search?q=robotehnika\"",
  "command_type": "url",
  "execution_time_ms": 320,
  "timestamp": 1723425123
}
```

---

### 3.2. Servis Holatini Tekshirish (Health Check)

Robot servis onlayn va tayyor ekanligini bilish uchun foydalanadi.

- **Endpoint:** `GET /api/status`
- **Response Body:**

```json
{
  "status": "online",
  "service": "JARVIS Robot Controller",
  "active_mode": "headful/silent_api",
  "uptime_seconds": 1240,
  "system": "Windows 11"
}
```

---

### 3.3. To'g'ridan-to'g'ri Tizim Buyrug'i Yuborish (Direct Command Execution)

Agarda robot Gemini AI tahlilisiz to'g'ridan-to'g'ri CMD/PowerShell buyrug'ini ishga tushirmoqchi bo'lsa:

- **Endpoint:** `POST /api/cmd`
- **Request Body:**

```json
{
  "cmd": "notepad.exe",
  "robot_id": "gumanoid_robot_01"
}
```

---

## 🖥 4. Veb Terminal va Telemetriya Monitoringi

Brauzerda `http://127.0.0.1:5000` sahifasi ochilganda:
- Robotdan kelgan har bir so mezon va vazifa real vaqtda neon ranglarda aks etadi.
- Ulanish holati (`Online`/`Offline`) va bajarilgan buyruqlar soni ko'rsatiladi.

---

## 📝 5. Hujjatlashtirish Qoidasi

Ushbu `USER_GUIDE.md` hujjati loyihaga kiritiladigan har bir yangi funksiya, yangi API endpoint yoki o'zgarish bilan **doimiy ravishda yangilanib boriladi**.
