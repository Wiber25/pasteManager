📋 Paste Manager (Windows Clipboard Manager)
Win + V 스타일의 사용자 경험을 제공하는 가볍고 강력한 윈도우 클립보드 히스토리 관리자입니다.

!

🚀 주요 기능 (Key Features)
실시간 모니터링: 백그라운드에서 시스템 클립보드를 감시하여 텍스트 데이터를 자동으로 저장합니다.

Win+V 스타일 UI: 테두리 없는 프레임과 반투명 배경을 사용한 현대적인 오버레이 UI를 제공합니다.

글로벌 단축키: Ctrl + Alt + V를 통해 어떤 화면에서든 즉시 히스토리를 호출할 수 있습니다.

즉시 붙여넣기 (Instant Paste): 리스트 항목 클릭 시, 해당 텍스트를 현재 포커스된 창에 즉시 입력합니다.

북마크 (Pinned Items): 자주 사용하는 문구는 상단에 고정하여 관리할 수 있습니다.

로컬 스토리지: SQLite를 활용하여 앱을 종료해도 데이터가 유실되지 않으며, %AppData% 경로를 사용하여 보안 권한 문제를 해결했습니다.

🛠 기술 스택 (Tech Stack)
Language: Python 3.10+

GUI Framework: PyQt6

Database: SQLite3

Libraries:

pyperclip: 클립보드 데이터 핸들링

keyboard: 글로벌 핫키 이벤트 감지

pywin32: 윈도우 시스템 API 제어

📂 프로젝트 구조 (Architecture)
Plaintext
.
├── main.py              # 앱 엔트리 포인트 및 모듈 오케스트레이션
├── database.py          # SQLite CRUD 로직 (AppData 경로 최적화)
├── clipboard_worker.py  # 백그라운드 이벤트 리스너 (스레딩 처리)
└── ui/
    └── main_window.py   # PyQt6 기반 오버레이 UI 및 QSS 스타일링
⚙️ 실행 방법 (Getting Started)
1. 환경 설치
Bash
pip install PyQt6 pyperclip keyboard pywin32
2. 앱 실행
Bash
python main.py
3. 빌드 (Executable)
Bash
pyinstaller --noconsole --onefile --add-data "ui;ui" --name "PasteManager" main.py
💡 구현 디테일 (Engineering Notes)
Focus Management: WindowDoesNotAcceptFocus 플래그를 사용하여 UI 호출 시 기존 작업 중인 창의 포커스를 유지하도록 설계했습니다.

Thread Safety: UI 스레드와 백그라운드 리스너 스레드 간의 통신을 위해 PyQt의 pyqtSignal 시스템을 활용했습니다.

UX Optimization: 클릭 시 창을 즉시 숨기고 비동기로 Ctrl + V 이벤트를 주입하여 네이티브 앱과 같은 사용자 경험을 구현했습니다.

📝 라이선스 (License)
이 프로젝트는 MIT 라이선스를 따릅니다.
