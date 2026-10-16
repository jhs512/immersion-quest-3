#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{D15DD94A-92BF-425A-B598-3DF23A159B03}
AppName=몰입 퀘스트 3
AppVersion={#AppVersion}
AppPublisher=몰입 퀘스트 3
DefaultDirName={localappdata}\Programs\MolipQuest3
DefaultGroupName=몰입 퀘스트 3
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\..\target\installers
OutputBaseFilename=molip-quest-3-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\molip-quest.exe
SetupIconFile=..\..\assets\icon\icon.ico

[Files]
Source: "..\..\target\release\molip-quest.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\requirements-learning.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\몰입 퀘스트 3"; Filename: "{app}\molip-quest.exe"
Name: "{group}\몰입 퀘스트 3 제거"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\molip-quest.exe"; Description: "몰입 퀘스트 3 실행"; Flags: nowait postinstall skipifsilent
