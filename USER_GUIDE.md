# 🤖 Humanoid Robot & JARVIS Assistant - Foydalanuvchi Qo'llanmasi (User Manual)

Ushbu hujjat **JARVIS Voice Assistant & Humanoid Robot Integration Service** loyihasidan foydalanish, uni gumanoid robotga ulash, REST API so'rovlarini yuborish, **Dinamik HTML UI Generator** va **Klaviatura Klavish Ovoz Effekti ("tq tq tq")** bo'yicha to'liq qo'llanmadir.

---

## 📌 1. Tizim haqida umumiy ma'lumot

Ushbu servis 4 ta asosiy foydalanuvchi tajribasiga (UX) ega:

1. **Vizual Kartalar va Interfeys (Clean UI Cards):** Quruq konsol loglari o'rniga, foydalanuvchiga faqat kerakli bo'lgan chiroyli vizual kartalar, status widgetlari va natija panellari ko'rsatiladi.
2. **Klaviatura Ovoz Effekti ("Tq-Tq-Tq" Typing SFX):** AI HTML generatsiya qilayotganda va kompyuterda buyruqlar yozilayotganda orqa fonda mexanik klaviatura bosilish ovozi (`tq tq tq`) eshitilib turadi.
3. **Gumanoid Robot API Rejimi (Headless/Silent Mode):** Robot mahalliy tarmoq (IP:Port) orqali HTTP REST API so'rovlarini yuboradi. Servis vazifani bajaradi, dinamikdan javobni ovozda aytmaydi (ovozsiz rejim) va to'liq bajarilish holati haqida JSON formatida robotga javob qaytaradi.
4. **Dinamik AI HTML Generator (Dynamic WebView Generator):** Murakkab topshiriqlar uchun Gemini AI avtomatik tarzda HTML/CSS/JS vizual interfeys kodini yaratadi va uni brauzer/webview oynasida namoyish etadi.

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

## 📡 3. Gumanoid Robot uchun REST API Hujjatlari

### 3.1. Robot Vazifa Yuborishi (Task Execution)

- **Endpoint:** `POST /api/task`
- **Header:** `Content-Type: application/json`
- **Request Body:**

```json
{
  "task": "Chrome brauzerini ochib robotehnika bo'yicha izla",
  "robot_id": "gumanoid_robot_01",
  "silent": true
}
```

- **Response Body:**

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

## 📝 4. Hujjatlashtirish Qoidasi

Ushbu `USER_GUIDE.md` hujjati loyihaga kiritiladigan har bir yangi funksiya bilan **doimiy ravishda yangilanib boriladi**.
