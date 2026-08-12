import os
import sys
import ctypes
from ctypes import wintypes

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

msi = ctypes.windll.msi

MSIDBOPEN_CREATE = ctypes.cast(3, ctypes.c_wchar_p)

def create_msi_file(msi_path):
    h_db = wintypes.HANDLE()
    res = msi.MsiOpenDatabaseW(
        ctypes.c_wchar_p(msi_path),
        MSIDBOPEN_CREATE,
        ctypes.byref(h_db)
    )
    if res != 0:
        print(f"MsiOpenDatabaseW error code: {res}")
        return False

    def exec_sql(sql_str):
        h_view = wintypes.HANDLE()
        r = msi.MsiDatabaseOpenViewW(h_db, ctypes.c_wchar_p(sql_str), ctypes.byref(h_view))
        if r == 0:
            msi.MsiViewExecute(h_view, 0)
            msi.MsiViewClose(h_view)
            msi.MsiCloseHandle(h_view)
            return True
        else:
            print(f"SQL Error ({r}): {sql_str}")
            return False

    exec_sql("CREATE TABLE `Property` (`Property` CHAR(72) NOT NULL, `Value` CHAR(255) NOT NULL PRIMARY KEY `Property`)")
    
    props = [
        ("ProductName", "JARVIS Neural Core Humanoid Controller"),
        ("ProductCode", "{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}"),
        ("ProductVersion", "3.0.0"),
        ("Manufacturer", "Vafoyev ComputerAgent AI"),
        ("ProductLanguage", "1033"),
        ("ALLUSERS", "1")
    ]
    for k, v in props:
        exec_sql(f"INSERT INTO `Property` (`Property`, `Value`) VALUES ('{k}', '{v}')")

    msi.MsiDatabaseCommit(h_db)
    msi.MsiCloseHandle(h_db)
    print(f"✅ Native Windows MSI Installer fayli (.msi) muvaffaqiyatli yaratildi: {msi_path}")
    return True

if __name__ == "__main__":
    out_path = os.path.abspath("JARVIS_Robot_Controller_v3.0.msi")
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception:
            pass
    create_msi_file(out_path)
