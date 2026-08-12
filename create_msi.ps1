# ============================================================
#  JARVIS NEURAL CORE — NATIVE WINDOWS MSI GENERATOR (.MSI)
# ============================================================
$ErrorActionPreference = "Stop"

$MsiPath = Join-Path $PSScriptRoot "JARVIS_Robot_Controller_v3.0.msi"
$DistDir = Join-Path $PSScriptRoot "dist\JARVIS_Robot_Controller"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  📦 NATIVE WINDOWS MSI GENERATOR (.MSI)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path $DistDir)) {
    Write-Host "❌ 'dist\JARVIS_Robot_Controller' topilmadi!" -ForegroundColor Red
    exit 1
}

if (Test-Path $MsiPath) {
    Remove-Item $MsiPath -Force
}

$Installer = New-Object -ComObject WindowsInstaller.Installer
$Database = $Installer.OpenDatabase($MsiPath, 1)

$q1 = 'CREATE TABLE Property (Property CHAR(72) NOT NULL, Value CHAR(255) NOT NULL PRIMARY KEY Property)'
$q2 = 'CREATE TABLE Directory (Directory CHAR(72) NOT NULL, Directory_Parent CHAR(72), DefaultDir CHAR(255) NOT NULL PRIMARY KEY Directory)'
$q3 = 'CREATE TABLE Component (Component CHAR(72) NOT NULL, ComponentId CHAR(38), Directory_ CHAR(72) NOT NULL, Attributes SHORT NOT NULL, Condition CHAR(255), KeyPath CHAR(72) PRIMARY KEY Component)'
$q4 = 'CREATE TABLE Feature (Feature CHAR(38) NOT NULL, Feature_Parent CHAR(38), Title CHAR(64), Description CHAR(255), Display SHORT, Level SHORT NOT NULL, Directory_ CHAR(72), Attributes SHORT NOT NULL PRIMARY KEY Feature)'
$q5 = 'CREATE TABLE File (File CHAR(72) NOT NULL, Component_ CHAR(72) NOT NULL, FileName CHAR(255) NOT NULL, FileSize LONG NOT NULL, Version CHAR(72), Language CHAR(20), Attributes SHORT, Sequence SHORT NOT NULL PRIMARY KEY File)'
$q6 = 'CREATE TABLE FeatureComponents (Feature_ CHAR(38) NOT NULL, Component_ CHAR(72) NOT NULL PRIMARY KEY Feature_, Component_)'
$q7 = 'CREATE TABLE InstallExecuteSequence (Action CHAR(72) NOT NULL, Condition CHAR(255), Sequence SHORT PRIMARY KEY Action)'

$Queries = @($q1, $q2, $q3, $q4, $q5, $q6, $q7)

foreach ($q in $Queries) {
    $View = $Database.OpenView($q)
    $View.Execute()
    $View.Close()
}

$Props = @(
    @("ProductName", "JARVIS Neural Core Humanoid Controller"),
    @("ProductCode", "{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}"),
    @("ProductVersion", "3.0.0"),
    @("Manufacturer", "Vafoyev ComputerAgent AI"),
    @("ProductLanguage", "1033"),
    @("ALLUSERS", "1")
)

foreach ($p in $Props) {
    $k = $p[0]
    $v = $p[1]
    $sql = "INSERT INTO Property (Property, Value) VALUES ('{0}', '{1}')" -f $k, $v
    $View = $Database.OpenView($sql)
    $View.Execute()
    $View.Close()
}

$Database.Commit()
$msg1 = "✅ Native Windows MSI Installer (.msi) Fayli Yaratildi!"
$msg2 = "   Fayl: " + $MsiPath
Write-Host $msg1 -ForegroundColor Green
Write-Host $msg2 -ForegroundColor Yellow
