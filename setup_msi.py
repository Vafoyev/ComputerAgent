import os
import sys
from cx_Freeze import setup, Executable

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

bdist_msi_options = {
    "upgrade_code": "{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}",
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\JARVIS Robot Controller",
}

build_exe_options = {
    "packages": [
        "os", "sys", "threading", "webbrowser", "json", "tempfile", "time", "subprocess", "asyncio",
        "flask", "flask_socketio", "google.genai", "speech_recognition", "pygame", "edge_tts", "gtts", "pyttsx3", "pyautogui"
    ],
    "include_files": [
        ("templates", "templates"),
        ("static", "static"),
        ("generated_views", "generated_views")
    ],
}

executables = [
    Executable(
        "app.py",
        target_name="JARVIS_Robot_Controller.exe",
        base=None, # Console application
    )
]

setup(
    name="JARVIS_Robot_Controller",
    version="3.0.0",
    description="JARVIS Neural Core Humanoid Robot Controller",
    author="Vafoyev ComputerAgent AI",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables
)
