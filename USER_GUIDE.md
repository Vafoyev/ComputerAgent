# 🤖 Humanoid Robot & JARVIS Assistant - Foydalanuvchi va Integratsiya Qo'llanmasi (User & Integration Manual)

Ushbu hujjat **JARVIS Humanoid Robot Controller & Voice Assistant** servisidan foydalanish, uni gumanoid robotga ulash, REST API so'rovlarini yuborish, **Dinamik HTML UI Generator** va **Klaviatura Klavish Ovoz Effekti ("tq tq tq")** bo'yicha to'liq qo'llanmadir.

---

## 📌 1. Tizim Arxitekturasi va Ishlash Prinsipi

```
 ┌──────────────────────┐         HTTP REST API            ┌───────────────────────────────────┐
 │   Humanoid Robot     │ ───────────────────────────────> │  JARVIS Backend Controller        │
 └──────────────────────┘  POST /api/task ("silent": true) └─────────────────┬─────────────────┘
                                                                             │
                                                           ┌─────────────────┴─────────────────┐
                                                           │   Gemini AI Intelligence Engine   │
                                                           └─────────────────┬─────────────────┘
                                                                             │
                                            ┌────────────────────────────────┴────────────────────────────────┐
                                            ▼                                                                 ▼
                             ┌─────────────────────────────┐                                   ┌─────────────────────────────┐
                             │  System Command Execution   │                                   │ Dynamic HTML UI Generator   │
                             │   (PowerShell / CMD / App)  │                                   │   (Responsive HTML/CSS/JS) │
                             └──────────────┬──────────────┘                                   └──────────────┬──────────────┘
                                            │                                                                 │
                                            ▼                                                                 ▼
                             ┌─────────────────────────────┐                                   ┌─────────────────────────────┐
                             │ JSON Response to Robot      │                                   │ Auto WebView / Browser      │
                             │ (Status, Output, Log data)  │                                   │ (Real-time Task Dashboard)  │
                             └─────────────────────────────┘                                   └─────────────────────────────┘
```

---

## 📡 2. Gumanoid Robotni Ulash va API Endpointlar

### 2.1. Robot Vazifa API Endpoint (`POST /api/task`)

Gumanoid robot har qanday vazifani (matn ko'rinishida) ushbu portga yuboradi.

- **URL:** `http://127.0.0.1:5000/api/task` (yoki local IP `http://192.168.x.x:5000/api/task`)
- **Method:** `POST`
- **Header:** `Content-Type: application/json`

#### Request Payload (Robot Yuboradigan JSON):
```json
{
  "task": "Robot holatini tekshir, Chrome'da robotehnika yangiliklarini och va dinamik UI yarat",
  "robot_id": "humanoid_robot_01",
  "silent": true,
  "generate_ui": true
}
```

#### Response Payload (Robotga Qaytadigan JSON):
```json
{
  "status": "success",
  "robot_id": "humanoid_robot_01",
  "task": "Robot holatini tekshir, Chrome'da robotehnika yangiliklarini och va dinamik UI yarat",
  "ai_response": "Chrome ochilib, robotehnika yangiliklari qidirilmoqda!",
  "command_executed": "start \"\" \"https://www.google.com/search?q=robotehnika+news\"",
  "command_type": "url",
  "generated_view_url": "http://127.0.0.1:5000/view/view_1723425123",
  "execution_time_ms": 340,
  "timestamp": 1723425123
}
```

---

### 2.2. Health Check Endpoint (`GET /api/status`)

Robot servis faol ekanligini tekshirish uchun ishlatiladi.

- **URL:** `http://127.0.0.1:5000/api/status`
- **Response:**
```json
{
  "status": "online",
  "service": "JARVIS Humanoid Robot Controller",
  "mode": "headful/silent_api",
  "dynamic_html_generator": "active",
  "system": "nt",
  "timestamp": 1723425123
}
```

---

### 2.3. To'g'ridan-to'g'ri Tizim Buyrug'i API (`POST /api/cmd`)

- **URL:** `http://127.0.0.1:5000/api/cmd`
- **Request Body:**
```json
{
  "cmd": "notepad.exe",
  "robot_id": "humanoid_robot_01"
}
```

---

## 🎨 3. Dinamik AI HTML WebView Generator va Klaviatura Sado Effekti

1. **Clean Visual Cards (Vizual Kartalar):** Konsol loglari o'rniga Veb Interfeysda faqat tartibli **Task Card**, **AI Card**, **CMD Action Card** va **Dynamic UI Link Card** lari ko'rsatiladi.
2. **"Tq-Tq-Tq" Typing SFX:** AI kod yaratganda hamda buyruqlar yozilayotganda Web Audio API va Python orqali mexanik klaviatura ovozi o'ynaydi.
3. **Avto-WebView:** Yaratilgan HTML fayllar `http://127.0.0.1:5000/view/<view_id>` yo'nalishida avtomatik brauzerda ochiladi.
