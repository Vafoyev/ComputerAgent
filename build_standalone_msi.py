import os
import sys
import subprocess
import msilib
import msilib.schema

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_header():
    print("=" * 70)
    print("📦 JARVIS NEURAL CORE — SINGLE-FILE STANDALONE MSI BUILDER (.MSI)")
    print("=" * 70)

def build_exe():
    print("\n[1/2] PyInstaller --onefile orqali Bitta Standalone .exe qurilmoqda...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name", "JARVIS_Robot_Controller",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "app.py"
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("❌ PyInstaller qurilishida xatolik yuz berdi!")
        sys.exit(1)
    print("✅ Bitta Standalone .exe muvaffaqiyatli qurildi!")

def build_standalone_msi():
    print("\n[2/2] Standalone .exe ni bitta .MSI Installer ichiga joylash...")
    
    msi_path = os.path.abspath("JARVIS_Robot_Controller_v3.0.msi")
    exe_path = os.path.abspath("dist/JARVIS_Robot_Controller.exe")

    if not os.path.exists(exe_path):
        print(f"❌ '{exe_path}' fayli topilmadi!")
        sys.exit(1)

    if os.path.exists(msi_path):
        try:
            os.remove(msi_path)
        except Exception:
            pass

    db = msilib.OpenDatabase(msi_path, msilib.MSIDBOPEN_CREATE)

    # 1. Standard Schema Tables
    for table_obj in msilib.schema.tables:
        table_obj.create(db)

    # 2. Summary Information Stream (Windows Installer oynasida ochilishi uchun MAJBURIY)
    si = db.GetSummaryInformation(20)
    si.SetProperty(msilib.PID_TITLE, "JARVIS Neural Core Humanoid Controller")
    si.SetProperty(msilib.PID_SUBJECT, "JARVIS Robot Controller Standalone Installer")
    si.SetProperty(msilib.PID_AUTHOR, "Vafoyev ComputerAgent AI")
    si.SetProperty(msilib.PID_KEYWORDS, "Installer, JARVIS, Humanoid Robot, Controller, Standalone")
    si.SetProperty(msilib.PID_COMMENTS, "All-in-One Standalone Windows Installer Package")
    si.SetProperty(msilib.PID_PAGECOUNT, 200) # Minimum Windows Installer 2.0
    si.SetProperty(msilib.PID_WORDCOUNT, 2)   # Long file names flag
    si.SetProperty(msilib.PID_REVNUMBER, "{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}") # Upgrade/Package GUID
    si.Persist()

    # 3. Standard Properties
    msilib.add_data(db, "Property", [
        ("ProductName", "JARVIS Neural Core Humanoid Controller"),
        ("ProductCode", "{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}"),
        ("ProductVersion", "3.0.0"),
        ("Manufacturer", "Vafoyev ComputerAgent AI"),
        ("ProductLanguage", "1033"),
        ("ALLUSERS", "1")
    ])

    # 4. Cab Cabinet file for embedding executable
    cab = msilib.CAB("data.cab")
    feature = msilib.Feature(db, "MainFeature", "JARVIS Core Engine", "JARVIS Robot Controller System", 1)

    # 5. Directory hierarchy
    target_dir = msilib.Directory(db, cab, None, "TARGETDIR", "SourceDir", "ProgramFilesFolder|PFiles")
    install_dir = msilib.Directory(db, cab, target_dir, "INSTALLDIR", "JARVIS|JARVIS Robot Controller", "JARVIS")
    
    install_dir.start_component("MainComponent", feature)
    install_dir.add_file("JARVIS_R.EXE|JARVIS_Robot_Controller.exe", src=exe_path)

    # Commit Database & Compressed Cabinet Stream
    db.Commit()
    cab.commit(db)
    
    print("\n" + "=" * 70)
    print("🎉 BOSHQA ISTALGAN KOMPYUTERDA ISHLAYDIGAN BITTA FAYLLI .MSI TAYYOR!")
    print(f"📁 MSI Fayl: {msi_path}")
    print("Faqat ushbu bitta .msi faylini olib borib istalgan kompyuterda bosishingiz kifoya!")
    print("=" * 70)

def main():
    print_header()
    build_exe()
    build_standalone_msi()

if __name__ == "__main__":
    main()
