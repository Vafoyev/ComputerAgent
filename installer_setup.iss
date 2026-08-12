[Setup]
AppName=JARVIS Neural Core Humanoid Controller
AppVersion=3.0.0
DefaultDirName={autopf}\JARVIS_Robot_Controller
DefaultGroupName=JARVIS Controller
OutputBaseFilename=JARVIS_Robot_Controller_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\JARVIS_Robot_Controller\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\JARVIS Robot Controller"; Filename: "{app}\JARVIS_Robot_Controller.exe"
Name: "{autodesktop}\JARVIS Robot Controller"; Filename: "{app}\JARVIS_Robot_Controller.exe"

[Run]
Filename: "{app}\JARVIS_Robot_Controller.exe"; Description: "JARVIS Controller-ni ishga tushirish"; Flags: nowait postinstall skipifsilent
