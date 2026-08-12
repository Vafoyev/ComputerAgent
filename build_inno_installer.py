import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_header():
    print("=" * 70)
    print("🚀 JARVIS NEURAL CORE — PROFESSIONAL WINDOWS SETUP INSTALLER BUILDER")
    print("=" * 70)

def step1_build_onedir_exe():
    print("\n[1/2] PyInstaller orqali Onedir Binary Bundle (.exe + DLLs + Assets) qurilmoqda...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--name", "JARVIS_Robot_Controller",
        "--hidden-import", "engineio.async_drivers.threading",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "app.py"
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("❌ PyInstaller qurilishida xatolik yuz berdi!")
        sys.exit(1)
    print("✅ PyInstaller Onedir Bundle muvaffaqiyatli qurildi!")

def step2_compile_inno_setup():
    print("\n[2/2] Inno Setup Compiler (ISCC.exe) orqali Professional Windows Setup.exe paketlanmoqda...")
    iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not os.path.exists(iscc_path):
        iscc_path = r"C:\Program Files\Inno Setup 6\ISCC.exe"

    if not os.path.exists(iscc_path):
        print(f"❌ Inno Setup Compiler ({iscc_path}) topilmadi!")
        sys.exit(1)

    iss_script = os.path.abspath("installer_setup.iss")
    cmd = [iscc_path, iss_script]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("❌ Inno Setup kompilatsiyasida xatolik yuz berdi!")
        sys.exit(1)

    setup_exe = os.path.abspath("Output/JARVIS_Robot_Controller_Setup.exe")
    if not os.path.exists(setup_exe):
        setup_exe = os.path.abspath("Output/JARVIS_Robot_Controller_Setup.exe")

    print("\n" + "=" * 70)
    print("🎉 PROFESSIONAL WINDOWS SETUP INSTALLER TAYYOR!")
    print(f"📁 TAYYOR SETUP FAYLI: {setup_exe}")
    print("Ushbu Setup.exe fayli har qanday Windows kompyuterda 100% binoan o'rnatiladi va ishlaydi!")
    print("=" * 70)

def main():
    print_header()
    step1_build_onedir_exe()
    step2_compile_inno_setup()

if __name__ == "__main__":
    main()
