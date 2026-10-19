#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{D15DD94A-92BF-425A-B598-3DF23A159B03}
AppName=MQ
AppVersion={#AppVersion}
AppPublisher=MQ
DefaultDirName={localappdata}\Programs\MolipQuest3
DefaultGroupName=MQ
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
Name: "{group}\MQ"; Filename: "{app}\molip-quest.exe"
Name: "{group}\MQ 제거"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\molip-quest.exe"; Description: "MQ 실행"; Flags: nowait postinstall skipifsilent
