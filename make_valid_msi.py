import os
import sys
import msilib
import msilib.schema

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build_valid_msi():
    msi_path = os.path.abspath("JARVIS_Robot_Controller_v3.0.msi")
    if os.path.exists(msi_path):
        try:
            os.remove(msi_path)
        except Exception:
            pass

    print(f"📦 Haqiqiy Windows MSI Fayli Yaratilmoqda: {msi_path}")
    db = msilib.OpenDatabase(msi_path, msilib.MSIDBOPEN_CREATE)
    
    # 1. Standard Windows Installer Table Schema
    for table_obj in msilib.schema.tables:
        table_obj.create(db)

    # 2. Summary Information Stream (Windows Installer muloqot oynasi to'g'ri ochilishi uchun SHART!)
    si = db.GetSummaryInformation(20)
    si.SetProperty(msilib.PID_TITLE, "JARVIS Neural Core Humanoid Controller")
    si.SetProperty(msilib.PID_SUBJECT, "JARVIS Robot Controller Setup")
    si.SetProperty(msilib.PID_AUTHOR, "Vafoyev ComputerAgent AI")
    si.SetProperty(msilib.PID_KEYWORDS, "Installer, JARVIS, Humanoid Robot, Controller")
    si.SetProperty(msilib.PID_COMMENTS, "JARVIS Neural Core Humanoid Robot Controller Windows MSI Package")
    si.SetProperty(msilib.PID_PAGECOUNT, 200) # Minimum Windows Installer 2.0
    si.SetProperty(msilib.PID_WORDCOUNT, 2)   # Long file names flag
    si.SetProperty(msilib.PID_REVNUMBER, "{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}") # GUID Package Code
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

    # 4. Cab Cabinet file for bundling executable
    cab = msilib.CAB("data.cab")

    # 5. Directory hierarchy & file packaging
    target_dir = msilib.Directory(db, cab, None, "TARGETDIR", "SourceDir", "ProgramFilesFolder|PFiles")
    install_dir = msilib.Directory(db, cab, target_dir, "INSTALLDIR", "JARVIS|JARVIS Robot Controller", "JARVIS")
    
    # 6. Feature & FeatureComponents
    feature = msilib.Feature(db, "MainFeature", "JARVIS Core", "JARVIS Robot Controller Engine", 1)
    install_dir.start_component("MainComponent", feature)

    # Executable faylni paketga joylash
    exe_src = os.path.abspath("dist/JARVIS_Robot_Controller/JARVIS_Robot_Controller.exe")
    if os.path.exists(exe_src):
        install_dir.add_file("JARVIS_R.EXE|JARVIS_Robot_Controller.exe", src=exe_src)
    else:
        install_dir.add_file("app.py", src=os.path.abspath("app.py"))
    install_dir.glob(feature, "*.*")

    # Commit Database
    db.Commit()
    cab.commit(db)
    
    print("\n" + "=" * 65)
    print("🎉 WINDOWS INSTALLER OYNAIDA OCHILUVCHI HAAIQIY .MSI FAYLI TAYYOR!")
    print(f"📁 {msi_path}")
    print("=" * 65)
    return msi_path

if __name__ == "__main__":
    build_valid_msi()
