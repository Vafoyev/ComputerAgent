import threading
import webbrowser
import time
from flask import Flask, render_template
from flask_socketio import SocketIO
from assistant import VoiceAssistant

import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(__name__, template_folder=resource_path('templates'), static_folder=resource_path('static'))
app.config['SECRET_KEY'] = 'jarvis-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

assistant = VoiceAssistant(socketio)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("[SYSTEM] UI ulandi.")
    socketio.emit('log', {'msg': '🟢 Jarvis web interfeysi ulandi!', 'type': 'neon'})
    socketio.emit('log', {'msg': '⚙️  Tizim ishga tushmoqda...', 'type': 'info'})
    # Ovozli assistantni alohida threadda ishga tushir
    t = threading.Thread(target=assistant.start, daemon=True)
    t.start()

@socketio.on('disconnect')
def handle_disconnect():
    print("[SYSTEM] UI uzildi.")

def open_browser():
    """Serverga vaqt berish uchun bir oz kuting, keyin browserni oching"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("=" * 50)
    print("  JARVIS - Ovozli Yordamchi")
    print("  http://127.0.0.1:5000")
    print("=" * 50)

    # Browserni orqa fonda oching
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Flask-SocketIO serverni ishga tushiring
    socketio.run(
        app,
        host='127.0.0.1',
        port=5000,
        allow_unsafe_werkzeug=True,
        debug=False,
        use_reloader=False
    )
