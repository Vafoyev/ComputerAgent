# 🤖 JARVIS Neural Core & Humanoid Robot Controller — Qo'llanma va Enterprise API Hujjati

Ushbu hujjat **JARVIS Neural Core Humanoid Robot Controller** tizimidan foydalanish, uni gumanoid robotlarga ulash, Enterprise Asinxron REST API so'rovlarini yuborish, **Task ID va Polling Status API**, **Dinamik HTML5 HUD Generator** hamda **O'rnatish Paketi (Setup.exe)** bo'yicha to'liq va rasmiy qo'llanmadir.

---

## 📌 1. Tizim Arxitekturasi va Ishlash Prinsipi

```
 ┌──────────────────────┐        POST /api/task (Instant HTTP 202)         ┌───────────────────────────────────┐
 │   Humanoid Robot     │ ───────────────────────────────────────────────> │  JARVIS Backend Controller        │
 └──────────┬───────────┘ <─────────────────────────────────────────────── └─────────────────┬─────────────────┘
            │               Task ID + Status URL (Fast Sub-10ms)                             │
            │                                                                ┌───────────────┴───────────────┐
            │  GET /api/task/status/<task_id> (Polling)                      │ Background Async Daemon Thread│
            └──────────────────────────────────────────────────────────────> └───────────────┬───────────────┘
                                                                                             │
                                                                             ┌───────────────┴───────────────┐
                                                                             │  Gemini AI Intelligence Engine│
                                                                             └───────────────┬───────────────┘
                                                                                             │
                                            ┌────────────────────────────────────────────────┴────────────────────────────────┐
                                            ▼                                                                                 ▼
                             ┌─────────────────────────────┐                                                   ┌─────────────────────────────┐
                             │  System Command Execution   │                                                   │ Dynamic HTML UI Generator   │
                             │   (PowerShell / CMD / App)  │                                                   │   (Responsive HTML/CSS/JS) │
                             └──────────────┬──────────────┘                                                   └──────────────┬──────────────┘
                                            │                                                                                 │
                                            ▼                                                                                 ▼
                             ┌─────────────────────────────┐                                                   ┌─────────────────────────────┐
                             │ Process Logs & Status Store │                                                   │ Auto WebView / Browser      │
                             │ (Task Telemetry History)    │                                                   │ (Real-time Task Dashboard)  │
                             └─────────────────────────────┘                                                   └─────────────────────────────┘
```

---

## 📡 2. Gumanoid Robot Enterprise Asinxron REST API

### 2.1. Asinxron Robot Vazifa Topshirish Endpoint (`POST /api/task`)

Gumanoid robot har qanday vazifani ushbu endpointga yuboradi. Tizim vazifani qabul qilib, **5-10ms ichida HTTP 202 Accepted** statusi hamda unikal `task_id` va `status_url` qaytaradi. Robot hech qachon "Timeout" xatosiga uchramaydi.

- **URL:** `http://127.0.0.1:5000/api/task` (yoki tarmoq IP `http://192.168.x.x:5000/api/task`)
- **Method:** `POST`
- **Header:** `Content-Type: application/json`

#### Request Payload (Robot Yuboradigan JSON):
```json
{
  "task": "YouTube'da O'zbekiston Davlat Madhiyasini ijro et va monitoring dashboardini och",
  "robot_id": "HUMANOID_UNIT_ALPHA_01",
  "silent": true,
  "generate_ui": true
}
```

#### Tezkor Response Payload (5-10ms ichida Qaytadigan JSON):
```json
{
  "status": "processing",
  "task_id": "task_1786510800_9281",
  "robot_id": "HUMANOID_UNIT_ALPHA_01",
  "task": "YouTube'da O'zbekiston Davlat Madhiyasini ijro et va monitoring dashboardini och",
  "message": "Task queued and executing asynchronously in background",
  "status_url": "/api/task/status/task_1786510800_9281",
  "timestamp": 1786510800
}
```

---

### 2.2. Task Statusini Tekshirish Endpoint (`GET /api/task/status/<task_id>`)

Robot yoki tashqi tizim `task_id` bo'yicha vazifaning joriy bajarilish holatini tekshiradi.

- **URL:** `http://127.0.0.1:5000/api/task/status/<task_id>`
- **Method:** `GET`

#### Response Payload (Vazifa Bajarilganidan So'ng Qaytadigan Natija):
```json
{
  "status": "success",
  "task_id": "task_1786510800_9281",
  "robot_id": "HUMANOID_UNIT_ALPHA_01",
  "task": "YouTube'da O'zbekiston Davlat Madhiyasini ijro et va monitoring dashboardini och",
  "ai_response": "YouTube platformasida audio va video avtomatik ravishda ijro etilmoqda!",
  "command_executed": "start \"\" \"https://www.youtube.com/watch?v=rdOw_VSXbU4&autoplay=1\"",
  "command_type": "cmd",
  "command_output": "",
  "exit_code": 0,
  "generated_view_url": "http://127.0.0.1:5000/view/view_1786510402",
  "execution_time_ms": 1250,
  "process_logs": [
    "[10:00:15] Vazifa qabul qilindi va asinxron navbatga qo'yildi",
    "[10:00:15] Gemini AI Neural Core tahlili boshlandi",
    "[10:00:15] YouTube / Audio ijro rejimi aniqlandi",
    "[10:00:15] YouTube Avto-ijro URL shakllantirildi: https://www.youtube.com/watch?v=rdOw_VSXbU4&autoplay=1",
    "[10:00:15] Ovozli bildirishnoma asinxron ishga tushirildi",
    "[10:00:15] Dinamik HTML5 HUD generatsiyasi boshlandi",
    "[10:00:15] HUD sahifa URL: http://127.0.0.1:5000/view/view_1786510402",
    "[10:00:15] Terminal buyrug'i ijrosi: 'start \"\" \"https://www.youtube.com/watch?v=rdOw_VSXbU4&autoplay=1\"'",
    "[10:00:15] Buyruq bajarildi (Exit code: 0)",
    "[10:00:15] Vazifa muvaffaqiyatli yakunlandi (1250ms)"
  ],
  "timestamp": 1786510800
}
```

---

### 2.3. Tizim Diagnostikasi Endpoint (`GET /api/health`)

Servis faoliyatini va tizim ko'rsatkichlarini olish.

- **URL:** `http://127.0.0.1:5000/api/health`
- **Method:** `GET`
- **Response:**
```json
{
  "status": "online",
  "service": "JARVIS Neural Core Robot Controller",
  "version": "3.0.0-Enterprise",
  "mode": "headful/silent_api",
  "os": "Windows",
  "platform": "Windows-11-10.0.26200-SP0",
  "python_version": "3.13.3",
  "dynamic_html_generator": "active",
  "total_generated_views": 18,
  "uptime_seconds": 21450,
  "timestamp": 1786510800
}
```

---

### 2.4. To'g'ridan-to'g'ri Terminal Buyrug'i API (`POST /api/cmd`)

- **URL:** `http://127.0.0.1:5000/api/cmd`
- **Request Payload:**
```json
{
  "cmd": "notepad.exe",
  "robot_id": "HUMANOID_UNIT_ALPHA_01"
}
```

---

## 🎵 3. YouTube Avto-ijro (`&autoplay=1`) va Audio Boshqaruvi

1. **Avtomatik Video Topish va Ijro Etish:** Foydalanuvchi yoki robot "YouTube'da madhiya/qo'shiq qo'yib ber" degan so'rov berganda, tizim YouTube API/Search mexanizmi orqali tegishli video ID-ni topadi va `&autoplay=1` parametri bilan Ochadi.
2. **Tugmani Bosmasdan Eshitish:** `&autoplay=1` brauzerda video ochilishi bilanoq musiqani Play tugmasini bosmasdan avtomatik ijro etadi.
3. **Asinxron Ovozli TTS:** Ovozli javoblar background threadda aytiladi, bu esa REST API tezligini to'sib qo'ymaydi.

---

## 🛠️ 4. Professional Windows Installer (`Setup.exe`)

Loyiha ildizida joylashgan **`Output/JARVIS_Robot_Controller_Setup.exe`** dasturi Inno Setup 6 orqali yig'ilgan bo'lib, quyidagi qulayliklarni beradi:
- Kompyuterga Python o'rnatilgan bo'lishi shart emas (barcha DLL va kutubxonalar paketlangan).
- Ish stolida va Start menyuda **JARVIS Robot Controller** yorlig'ini yaratadi.
- Windows qayta tushganda avtomatik fonda ishlash rejimi.
