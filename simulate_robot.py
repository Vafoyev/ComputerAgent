import requests
import json
import time
import sys

# Windows console UTF-8 support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"
ROBOT_ID = "HUMANOID_UNIT_ALPHA_01"

ROBOT_TASKS = [
    "Gumanoid robot batareya va sensorlar holati vizual monitoring dashboardini och",
    "Chrome brauzerida Sun'iy intellekt va humanoid robotehnika yangiliklarini izla",
    "Notepad dasturini ochib robot topshiriqlar daftarchasini tayyorla",
    "YouTube platformasini ochib robot texnologiyalari videolarini izla",
    "Tizim diagnostikasi va kompyuter ish faoliyatini tekshirish dashboardini yarat"
]

def print_header():
    print("=" * 65)
    print("🤖 HUMANOID ROBOT SIMULATOR — LOCAL API TESTER")
    print(f"Target Server: {BASE_URL}")
    print(f"Robot Unit ID: {ROBOT_ID}")
    print("=" * 65)

def check_status():
    try:
        res = requests.get(f"{BASE_URL}/api/status", timeout=3)
        print("\n🟢 [HEALTH CHECK] Server Status Response:")
        print(json.dumps(res.json(), indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"\n❌ [ERROR] Server bilan ulanib bo'lmadi: {e}")
        print("Iltimos, oldin 'python app.py' yoki 'start_robot_agent.bat'ni ishga tushiring!")
        return False

def send_robot_task(task_text):
    print("\n------------------------------------------------------------")
    print(f"🤖 [ROBOT -> SERVER] Task Yuborilmoqda: '{task_text}'")
    
    payload = {
        "task": task_text,
        "robot_id": ROBOT_ID,
        "silent": True,
        "generate_ui": True
    }
    
    start = time.time()
    try:
        res = requests.post(f"{BASE_URL}/api/task", json=payload, timeout=15)
        elapsed = int((time.time() - start) * 1000)
        
        print(f"📥 [SERVER -> ROBOT] Response Qaytdi (Vaqt: {elapsed}ms | HTTP {res.status_code}):")
        print(json.dumps(res.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ [ROBOT ERROR] So'rov bajarilmadi: {e}")

def run_simulation(loop_count=len(ROBOT_TASKS), delay_sec=4):
    if not check_status():
        return

    print(f"\n🚀 Simulyatsiya boshlandi! ({loop_count} ta topshiriq {delay_sec}s interval bilan yuboriladi)...")
    for i, task in enumerate(ROBOT_TASKS[:loop_count], 1):
        print(f"\n--- [Vazifa {i}/{loop_count}] ---")
        send_robot_task(task)
        if i < loop_count:
            print(f"⏳ {delay_sec} soniya kutilmoqda...")
            time.sleep(delay_sec)

    print("\n✅ Simulyatsiya muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        if check_status():
            send_robot_task(ROBOT_TASKS[0])
    else:
        run_simulation()
