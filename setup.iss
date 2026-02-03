[Setup]
; 앱 기본 정보
AppName=Paste Manager
AppVersion=1.0
DefaultDirName={autopf}\PasteManager
DefaultGroupName=Paste Manager
; 설치 후 실행 파일 이름
OutputBaseFilename=PasteManager_Setup
Compression=lzma
SolidCompression=yes
; 관리자 권한 필요 시 (권장)
PrivilegesRequired=admin

[Files]
; PyInstaller가 만든 exe 파일 위치 (경로는 본인 환경에 맞게 수정)
Source: "E:\projects\pasteManager\dist\PasteManager.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 시작 메뉴 및 바탕화면 아이콘
Name: "{group}\Paste Manager"; Filename: "{app}\PasteManager.exe"
Name: "{autodesktop}\Paste Manager"; Filename: "{app}\PasteManager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "runatstartup"; Description: "윈도우 시작 시 자동 실행"; GroupDescription: "기타 설정:"; Flags: unchecked

[Registry]
; 윈도우 시작 시 자동 실행 등록 로직
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "PasteManager"; ValueData: """{app}\PasteManager.exe"""; \
    Flags: uninsdeletevalue; Tasks: runatstartup

[Run]
; 설치 완료 후 바로 앱 실행하기
Filename: "{app}\PasteManager.exe"; Description: "{cm:LaunchProgram,Paste Manager}"; Flags: nowait postinstall skipifsilent