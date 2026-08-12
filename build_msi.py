import os
import sys
import subprocess
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_header():
    print("=" * 65)
    print("📦 JARVIS NEURAL CORE — WINDOWS INSTALLER GENERATOR")
    print("=" * 65)

def build_exe():
    print("\n[1/2] PyInstaller orqali Standalone Windows Executable (.exe) qurilmoqda...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--name", "JARVIS_Robot_Controller",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "app.py"
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("❌ PyInstaller qurilishida xatolik yuz berdi!")
        sys.exit(1)
    print("✅ PyInstaller .exe muvaffaqiyatli qurildi!")

def generate_inno_setup_script():
    print("\n[2/2] Inno Setup / WiX Installer ssenariysi generatsiya qilinmoqda...")
    iss_content = f"""[Setup]
AppName=JARVIS Neural Core Humanoid Controller
AppVersion=3.0.0
DefaultDirName={{autopf}}\\JARVIS_Robot_Controller
DefaultGroupName=JARVIS Controller
OutputBaseFilename=JARVIS_Robot_Controller_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\\JARVIS_Robot_Controller\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autoprograms}}\\JARVIS Robot Controller"; Filename: "{{app}}\\JARVIS_Robot_Controller.exe"
Name: "{{autodesktop}}\\JARVIS Robot Controller"; Filename: "{{app}}\\JARVIS_Robot_Controller.exe"

[Run]
Filename: "{{app}}\\JARVIS_Robot_Controller.exe"; Description: "JARVIS Controller-ni ishga tushirish"; Flags: nowait postinstall skipifsilent
"""
    with open("installer_setup.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)
    
    print("✅ 'installer_setup.iss' Inno Setup fayli yaratildi!")

def main():
    print_header()
    
    try:
        import PyInstaller
    except ImportError:
        print("📦 PyInstaller o'rnatilmoqda...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    build_exe()
    generate_inno_setup_script()
    
    print("\n" + "=" * 65)
    print("🎉 Windows Installer Paketi Tayyor!")
    print("Executable Joylashuvi: dist/JARVIS_Robot_Controller/JARVIS_Robot_Controller.exe")
    print("Inno Setup Fayli: installer_setup.iss")
    print("=" * 65)

if __name__ == "__main__":
    main()
