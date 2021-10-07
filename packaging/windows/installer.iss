#define MyAppName "Wingman"
#define MyAppVersion "5.0"
#define MyAppPublisher "biqqles"
#define MyAppURL "https://github.com/biqqles/wingman"
#define MyAppExeName "Wingman.exe"

[Setup]
AppId={{5A098D11-2FE3-4A52-9F1A-95AFB7CF3440}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=.\dist\Wingman\LICENSE.txt
InfoBeforeFile=.\dist\Wingman\README.md
OutputDir=.\dist
OutputBaseFilename=wingman-setup
SetupIconFile=..\..\icons\general\wingman.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: ".\dist\Wingman\Wingman.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\dist\Wingman\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: runascurrentuser nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\wingman\navmap"
Type: filesandordirs; Name: "{localappdata}\wingman\QtWebEngine"
Type: files; Name: "{localappdata}\wingman\debug.log"
Type: files; Name: "{localappdata}\wingman\wingman.cfg"
Type: files; Name: "{localappdata}\wingman\wingman.log"
