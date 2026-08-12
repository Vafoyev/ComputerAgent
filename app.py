import threading
import webbrowser
import time
import os
import sys
import platform
import random
from flask import Flask, render_template, request, jsonify, send_from_directory
import engineio.async_drivers.threading
from flask_socketio import SocketIO
from assistant import VoiceAssistant

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(__name__, template_folder=resource_path('templates'), static_folder=resource_path('static'))
app.config['SECRET_KEY'] = 'jarvis-robot-neural-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

START_TIME = time.time()
assistant = VoiceAssistant(socketio)

TASKS_STORE = {}
tasks_lock = threading.Lock()

# ------------------------------------------------------------
#  Veb Interfeys Sahifalari
# ------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view/<view_id>')
def view_generated_page(view_id):
    """AI tomonidan yaratilgan dinamik HTML5 HUD sahifalarini ko'rsatish"""
    views_dir = os.path.join(os.path.abspath("."), "generated_views")
    filename = f"{view_id}.html"
    file_path = os.path.join(views_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(views_dir, filename)
    return "<h1>404 — Vizual Dashboard Topilmadi</h1>", 404

# ------------------------------------------------------------
#  GUMANOID ROBOT API ENDPOINTLARI (ENTERPRISE ASYNC)
# ------------------------------------------------------------
@app.route('/api/health', methods=['GET'])
def api_health():
    """Robot va Tizim Salomatlik Statusi"""
    views_dir = os.path.join(os.path.abspath("."), "generated_views")
    total_views = len(os.listdir(views_dir)) if os.path.exists(views_dir) else 0

    return jsonify({
        "status": "online",
        "service": "JARVIS Neural Core Robot Controller",
        "version": "3.0.0-Enterprise",
        "mode": "headful/silent_api",
        "os": platform.system(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "dynamic_html_generator": "active",
        "total_generated_views": total_views,
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": int(time.time())
    }), 200

@app.route('/api/task', methods=['POST'])
def api_task():
    """
    Asinxron Enterprise Robot Task Submission Endpoint
    
    Vazifani qabul qilib, zudlik bilan HTTP 202 status va task_id qaytaradi.
    Tizim vazifani orqa fonda (background thread) xavfsiz bajaradi.
    """
    data = request.get_json(force=True, silent=True) or {}
    task_text = data.get("task", "").strip()
    robot_id = data.get("robot_id", "gumanoid_robot_default")
    silent = data.get("silent", True)
    generate_ui = data.get("generate_ui", True)

    if not task_text:
        return jsonify({
            "status": "error",
            "message": "Task parameter is required in JSON body"
        }), 400

    task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"
    now_ts = int(time.time())

    initial_task_data = {
        "task_id": task_id,
        "robot_id": robot_id,
        "task": task_text,
        "status": "processing",
        "process_logs": [f"[{time.strftime('%H:%M:%S')}] Task qabul qilindi va asinxron navbatga qo'yildi"],
        "timestamp": now_ts
    }

    with tasks_lock:
        TASKS_STORE[task_id] = initial_task_data

    print(f"[ROBOT API v3.0] Async Task Queued ({task_id}): {task_text}")
    assistant.emit_card("🤖 Gumanoid Robot So'rovi", f"Task ID: {task_id} | Robot ID: {robot_id} | Vazifa: {task_text}", "info")

    def _worker():
        res = assistant.execute_task(task_text, silent=silent, generate_ui=generate_ui)
        res["task_id"] = task_id
        res["robot_id"] = robot_id
        with tasks_lock:
            TASKS_STORE[task_id] = res

    threading.Thread(target=_worker, daemon=True).start()

    return jsonify({
        "status": "processing",
        "task_id": task_id,
        "robot_id": robot_id,
        "task": task_text,
        "message": "Task queued and executing asynchronously in background",
        "status_url": f"/api/task/status/{task_id}",
        "timestamp": now_ts
    }), 202

@app.route('/api/task/status/<task_id>', methods=['GET'])
def api_task_status(task_id):
    """
    Task id bo'yicha vazifaning joriy statusi va natijalarini qaytaruvchi endpoint
    """
    with tasks_lock:
        task_info = TASKS_STORE.get(task_id)

    if not task_info:
        return jsonify({
            "status": "not_found",
            "task_id": task_id,
            "message": f"Task ID '{task_id}' topilmadi",
            "timestamp": int(time.time())
        }), 404

    return jsonify(task_info), 200

@app.route('/api/cmd', methods=['POST'])
def api_cmd():
    """To'g'ridan-to'g'ri CMD/PowerShell buyruqlarini ishga tushirish"""
    data = request.get_json(force=True, silent=True) or {}
    cmd = data.get("cmd", "").strip()
    robot_id = data.get("robot_id", "gumanoid_robot_default")

    if not cmd:
        return jsonify({"status": "error", "message": "cmd parameter is required"}), 400

    assistant.emit_card("⚙️ Robot Direct CMD", cmd, "cmd")
    import subprocess
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        stdout, stderr = proc.communicate(timeout=5)
        output = stdout.strip() or stderr.strip()
    except Exception:
        output = "Executed in background"

    return jsonify({
        "status": "success",
        "robot_id": robot_id,
        "command_executed": cmd,
        "output": output,
        "exit_code": proc.returncode,
        "timestamp": int(time.time())
    }), 200

# ------------------------------------------------------------
#  SocketIO Voqealari
# ------------------------------------------------------------
@socketio.on('connect')
def handle_connect():
    print("[SYSTEM] UI ulandi.")
    assistant.emit_card("🟢 Web UI Ulandi", "JARVIS Neural Core & Gumanoid Robot Boshqaruv Markazi tayyor!", "success")

@socketio.on('disconnect')
def handle_disconnect():
    print("[SYSTEM] UI uzildi.")

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("=" * 65)
    print("  JARVIS NEURAL CORE — HUMANOID ROBOT CONTROLLER v3.0")
    print("  Local Server: http://127.0.0.1:5000")
    print("  Robot REST API Endpoint: http://127.0.0.1:5000/api/task")
    print("=" * 65)

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        allow_unsafe_werkzeug=True,
        debug=False,
        use_reloader=False
    )
