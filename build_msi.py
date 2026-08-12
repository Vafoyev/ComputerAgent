import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_header():
    print("=" * 65)
    print("📦 JARVIS NEURAL CORE — VALID WINDOWS MSI GENERATOR (.MSI)")
    print("=" * 65)

def build_exe():
    print("\n[1/2] PyInstaller orqali Executable (.exe) qurilmoqda...")
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

def build_msi_file():
    print("\n[2/2] Windows Installer MSILIB orqali yaroqli .MSI fayl generatsiya qilinmoqda...")
    cmd = [sys.executable, "make_valid_msi.py"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("❌ MSI fayl generatsiyasida xatolik yuz berdi!")
        sys.exit(1)

def main():
    print_header()
    
    try:
        import PyInstaller
    except ImportError:
        print("📦 PyInstaller o'rnatilmoqda...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    build_exe()
    build_msi_file()
    
    msi_path = os.path.abspath("JARVIS_Robot_Controller_v3.0.msi")
    print("\n" + "=" * 65)
    print("🎉 WINDOWS INSTALLER OYNASIDA BEXATO OCHILUVCHI .MSI FAYLI TAYYOR!")
    print(f"📁 {msi_path}")
    print("=" * 65)

if __name__ == "__main__":
    main()
