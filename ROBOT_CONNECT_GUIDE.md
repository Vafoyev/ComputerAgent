# 🤖 Gumanoid Robotni JARVIS Neural Core Portiga Ulash Qo'llanmasi (Robot Integration Protocol)

Ushbu hujjat **Gumanoid Robot (ROS, ROS2, Raspberry Pi, NVIDIA Jetson, Python, C++, Node.js)** va kompyuteringizdagi **JARVIS Neural Core** servisini mahalliy tarmoq (Local Network IP:Port) orqali ulash bo'yicha to'liq va amaliy ko'rsatmadir.

---

## 🌐 1. Ulanish Porti va IP Manzilini Aniqlash

JARVIS servisi Windows kompyuteringizda **`0.0.0.0:5000`** portida barcha mahalliy tarmoq so'rovlarini tinglaydi.

### Kompyuter IP manzilini topish (Windows):
Terminalda (CMD yoki PowerShell):
```cmd
ipconfig
```
"IPv4 Address" qatoriga qarang (masalan: `192.168.1.150` yoki `172.20.10.3`).

- **Gumanoid Robot uchun Asosiy API Endpoint:**
  `http://<KOMPYUTER_IP>:5000/api/task`
- **Lokal Test uchun Endpoint:**
  `http://127.0.0.1:5000/api/task`

---

## 📡 2. Gumanoid Robot Dasturiy Kodlari (Ulash Namunalari)

### 🐍 2.1. Python (ROS2 / Jetson Nano / Raspberry Pi)

Gumanoid robot bortidagi Python skriptidan so'rov yuborish:

```python
import requests
import json
import time

# Kompyuteringiz IP manzili va porti
JARVIS_API_URL = "http://192.168.1.150:5000/api/task"
ROBOT_ID = "HUMANOID_UNIT_01"

def send_task_to_jarvis(task_description):
    payload = {
        "task": task_description,
        "robot_id": ROBOT_ID,
        "silent": True,        # Dinamikdan ovoz chiqarishni o'chirish (ovozsiz rejim)
        "generate_ui": True    # Dinamik HTML WebView yaratish
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        start_time = time.time()
        response = requests.post(JARVIS_API_URL, json=payload, headers=headers, timeout=10)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ [SUCCESS] Natija olindi ({elapsed_ms}ms):")
            print(f"   AI Javobi: {data.get('ai_response')}")
            print(f"   Bajarilgan CMD: {data.get('command_executed')}")
            print(f"   Generated View URL: {data.get('generated_view_url')}")
            return data
        else:
            print(f"❌ [ERROR] HTTP Xatolik: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ [CONNECTION ERROR] JARVIS serveriga ulanib bo'lmadi: {e}")
        return None

# Ishlatib ko'rish:
if __name__ == "__main__":
    send_task_to_jarvis("Chrome brauzerida robotehnika va AI yangiliklarini izla")
```

---

### ⚡ 2.2. C++ (ROS / ROS2 Node)

ROS/ROS2 C++ tugunidan (`libcurl` yordamida) so'rov yuborish:

```cpp
#include <iostream>
#include <string>
#include <curl/curl.h>

void sendRobotTask(const std::string& taskText) {
    CURL* curl = curl_easy_init();
    if(curl) {
        std::string url = "http://192.168.1.150:5000/api/task";
        std::string jsonPayload = "{\"task\":\"" + taskText + "\",\"robot_id\":\"HUMANOID_CPP_NODE\",\"silent\":true,\"generate_ui\":true}";

        struct curl_slist* headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, jsonPayload.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            std::cerr << "CURL Error: " << curl_easy_strerror(res) << std::endl;
        }

        curl_easy_cleanup(curl);
    }
}
```

---

### 🌐 2.3. Node.js / JavaScript (Robot Web Interface)

```javascript
const axios = require('axios');

async function sendRobotTask(taskText) {
    try {
        const response = await axios.post('http://192.168.1.150:5000/api/task', {
            task: taskText,
            robot_id: 'HUMANOID_NODEJS_UNIT',
            silent: true,
            generate_ui: true
        });

        console.log('✅ Status:', response.data.status);
        console.log('💡 AI Response:', response.data.ai_response);
        console.log('🌐 Generated UI:', response.data.generated_view_url);
    } catch (error) {
        console.error('❌ Connection Error:', error.message);
    }
}

sendRobotTask("Notepad dasturini och va robot topshiriqlarini yoz");
```

---

### 💻 2.4. Linux Bash / cURL (Terminal orqali)

```bash
curl -X POST http://192.168.1.150:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{
        "task": "Chrome brauzerini ochib robotehnika izla",
        "robot_id": "humanoid_terminal_01",
        "silent": true,
        "generate_ui": true
      }'
```

---

## 📊 3. API So'rov va Javob (JSON Specification)

### Robot Yuboradigan JSON (Request):
| Parametr | Turi | Tavsif |
|---|---|---|
| `task` | String (Required) | Gumanoid robot bajarishi kerak bo'lgan tabiiy tildagi vazifa |
| `robot_id` | String (Optional) | Robotning unikal identifikatori (masalan: `humanoid_unit_01`) |
| `silent` | Boolean (Optional) | `true` bo'lsa, dinamikdan ovoz chiqmaydi (ovozsiz rejim) |
| `generate_ui` | Boolean (Optional) | `true` bo'lsa, Dinamik HTML WebView yaratadi |

### JARVIS Server Qaytaradigan JSON (Response):
```json
{
  "status": "success",
  "robot_id": "HUMANOID_UNIT_01",
  "task": "Chrome brauzerida robotehnika izla",
  "ai_response": "Chrome ochilib, robotehnika qidirilmoqda!",
  "command_executed": "https://www.google.com",
  "command_type": "url",
  "command_output": "",
  "exit_code": 0,
  "generated_view_url": "http://127.0.0.1:5000/view/view_1786489762",
  "execution_time_ms": 32,
  "timestamp": 1786489762
}
```

---

## 📋 4. Servis Diagnostikasi (Health Check)

Gumanoid robot servis tayyor va faol ekanligini bilish uchun:

- **HTTP GET:** `http://<KOMPYUTER_IP>:5000/api/status`

Javob:
```json
{
  "status": "online",
  "service": "JARVIS Neural Core Robot Controller",
  "version": "3.0.0-Enterprise",
  "mode": "headful/silent_api",
  "os": "Windows",
  "platform": "Windows-11",
  "total_generated_views": 4,
  "uptime_seconds": 320
}
```
