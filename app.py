import threading
import webbrowser
import time
import os
import sys
import platform
from flask import Flask, render_template, request, jsonify, send_from_directory
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

# ------------------------------------------------------------
#  Veb Interfeys Sahifalari
# ------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view/<view_id>')
def serve_generated_view(view_id):
    """Gemini AI tomonidan yaratilgan Dinamik HTML sahifani namoyish etish"""
    views_dir = os.path.join(os.path.abspath("."), "generated_views")
    filename = f"{view_id}.html"
    if not filename.endswith('.html'):
        filename += '.html'
    if os.path.exists(os.path.join(views_dir, filename)):
        return send_from_directory(views_dir, filename)
    return jsonify({"error": "Dynamic view not found", "view_id": view_id}), 404

# ------------------------------------------------------------
#  🤖 ENTERPRISE HUMANOID ROBOT REST API ENDPOINTS
# ------------------------------------------------------------
@app.route('/api/status', methods=['GET'])
def api_status():
    """Gumanoid robot servis diagnostikasi (Extended Health Check)"""
    uptime_sec = int(time.time() - START_TIME)
    views_dir = os.path.join(os.path.abspath("."), "generated_views")
    total_views = len([f for f in os.listdir(views_dir) if f.endswith('.html')]) if os.path.exists(views_dir) else 0

    return jsonify({
        "status": "online",
        "service": "JARVIS Neural Core Robot Controller",
        "version": "3.0.0-Enterprise",
        "mode": "headful/silent_api",
        "dynamic_html_generator": "active",
        "os": platform.system(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "total_generated_views": total_views,
        "uptime_seconds": uptime_sec,
        "timestamp": int(time.time())
    }), 200

@app.route('/api/task', methods=['POST'])
def api_task():
    """
    Gumanoid robotdan vazifani qabul qilish uchun asosiy REST API.
    JSON Payload:
    {
       "task": "Chrome och va robotehnika izla",
       "robot_id": "gumanoid_robot_01",
       "silent": true,
       "generate_ui": true
    }
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

    print(f"[ROBOT API v3.0] Robot ({robot_id}) Vazifasi: {task_text}")
    assistant.emit_card("🤖 Gumanoid Robot So'rovi", f"Robot ID: {robot_id} | Vazifa: {task_text}", "info")

    result = assistant.execute_task(task_text, silent=silent, generate_ui=generate_ui)
    result["robot_id"] = robot_id

    return jsonify(result), 200

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
