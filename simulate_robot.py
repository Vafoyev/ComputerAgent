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
    "YouTube platformasini ochib O'zbekiston Davlat Madhiyasini ijro et",
    "Tizim diagnostikasi va kompyuter ish faoliyatini tekshirish dashboardini yarat"
]

def print_header():
    print("=" * 65)
    print("🤖 HUMANOID ROBOT SIMULATOR — ENTERPRISE ASYNC API TESTER")
    print(f"Target Server: {BASE_URL}")
    print(f"Robot Unit ID: {ROBOT_ID}")
    print("=" * 65)

def check_status():
    try:
        res = requests.get(f"{BASE_URL}/api/health", timeout=3)
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
        # Step 1: Submit Task Asynchronously (Fast response HTTP 202)
        res = requests.post(f"{BASE_URL}/api/task", json=payload, timeout=5)
        elapsed = int((time.time() - start) * 1000)
        
        print(f"⚡ [ASYNCHRONOUS SUBMISSION] Response Qaytdi (Vaqt: {elapsed}ms | HTTP {res.status_code}):")
        resp_data = res.json()
        print(json.dumps(resp_data, indent=2, ensure_ascii=False))
        
        task_id = resp_data.get("task_id")
        if not task_id:
            return
            
        # Step 2: Poll GET /api/task/status/<task_id> until completed
        print(f"\n🔍 [TASK POLLING] Task Status Tekshirilmoqda (/api/task/status/{task_id})...")
        poll_count = 0
        while poll_count < 10:
            time.sleep(1.0)
            poll_count += 1
            status_res = requests.get(f"{BASE_URL}/api/task/status/{task_id}", timeout=3)
            status_data = status_res.json()
            curr_status = status_data.get("status")
            print(f"   ↳ Poll #{poll_count} — Task Status: '{curr_status}'")
            
            if curr_status in ["success", "completed", "failed", "error"]:
                print(f"\n📥 [FINAL TASK STATUS RESULT] (Task ID: {task_id}):")
                print(json.dumps(status_data, indent=2, ensure_ascii=False))
                break

    except Exception as e:
        print(f"❌ [ROBOT ERROR] So'rov bajarilmadi: {e}")

def run_simulation(loop_count=len(ROBOT_TASKS), delay_sec=2):
    print_header()
    if not check_status():
        return

    print(f"\n🚀 Enterprise Simulyatsiya Boshlandi! ({loop_count} ta topshiriq {delay_sec}s interval bilan yuboriladi)...")
    for i, task in enumerate(ROBOT_TASKS[:loop_count], 1):
        print(f"\n--- [Vazifa {i}/{loop_count}] ---")
        send_robot_task(task)
        if i < loop_count:
            print(f"⏳ {delay_sec} soniya kutilmoqda...")
            time.sleep(delay_sec)

    print("\n✅ Simulyatsiya muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    run_simulation()
