from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
import pyperclip
import keyboard
import time
import threading

# 각 클립보드 항목을 나타내는 '컴포넌트' (프론트엔드의 리스트 아이템)
class ClipboardItem(QFrame):
    def __init__(self, item_id, content, is_pinned, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.content = content
        self.is_pinned = is_pinned # 북마크 상태 추가
        self.init_ui()

    def init_ui(self):
        self.setObjectName("ItemFrame")
        
        # --- 추가된 부분: Pinned 속성 부여 ---
        if self.is_pinned:
            self.setProperty("pinned", "true")
        else:
            self.setProperty("pinned", "false")
        # -----------------------------------

        from PyQt6.QtWidgets import QHBoxLayout, QPushButton
        layout = QHBoxLayout(self)
        
        # 텍스트 라벨
        display_text = (self.content[:80] + '...') if len(self.content) > 80 else self.content
        self.label = QLabel(display_text)
        self.label.setWordWrap(True)
        layout.addWidget(self.label, 8)

        # 북마크 버튼
        pin_text = "📌" if self.is_pinned else "📍" # 📍은 예시입니다.
        self.pin_btn = QPushButton(pin_text)
        self.pin_btn.setFixedSize(30, 30)
        # ... (이하 버튼 스타일 동일) ...
        self.pin_btn.clicked.connect(self.toggle_bookmark)
        layout.addWidget(self.pin_btn, 1)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def toggle_bookmark(self):
        """북마크 상태 토글"""
        main_win = self.window()
        main_win.db.toggle_pin(self.item_id) # DB 업데이트
        main_win.refresh_list() # 리스트 새로고침

    def mousePressEvent(self, event):
        # 텍스트 영역을 클릭했을 때만 즉시 붙여넣기 실행
        if event.button() == Qt.MouseButton.LeftButton:
            pyperclip.copy(self.content)
            main_win = self.window()
            main_win.hide()
            
            def instant_paste():
                time.sleep(0.08)
                keyboard.press_and_release('ctrl+v')
            
            threading.Thread(target=instant_paste, daemon=True).start()
# 메인 오버레이 창
class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        # 1. 창 설정: 테두리 제거, 항상 위, 작업표시줄 제외
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 배경 투명 허용
        self.setFixedSize(350, 500)

        # 2. 메인 컨테이너 및 스크롤 영역 (CSS의 overflow-y: scroll 역할)
        self.container = QWidget()
        self.container.setObjectName("MainContainer")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(10, 20, 10, 10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(self.scroll)

        # 3. 스타일시트 (QSS - CSS와 거의 동일합니다)
        self.setStyleSheet("""
            #MainContainer {
                background-color: rgba(30, 30, 30, 240); /* 아크릴 느낌의 다크 모드 */
                border: 1px solid #444;
                border-radius: 12px;
            }
            #ItemFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                margin-bottom: 5px;
                padding: 5px;
            }
            #ItemFrame:hover {
                background-color: #3d3d3d;
                border: 1px solid #0078d4; /* 윈도우 포인트 컬러 */
            }
            QLabel {
                color: #e0e0e0;
                font-family: "Segoe UI", sans-serif;
                font-size: 13px;
            }
        """)

    def refresh_list(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # DB에서 데이터 가져오기 (is_pinned가 1인게 먼저 나옴)
        history = self.db.get_history(20)
        
        for item_id, content, date, is_pinned in history:
            # ClipboardItem 생성 시 is_pinned 값 전달
            item_widget = ClipboardItem(item_id, content, is_pinned)
            self.main_layout.addWidget(item_widget)
        
        self.main_layout.addStretch()

    def show_at_cursor(self):
        self.refresh_list()
        screen = self.screen().geometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 60)
        
        # 핵심: 포커스를 뺏지 않고 보여주기 (Show Without Activating)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.show()
        # self.activateWindow() # 이 줄은 삭제하거나 주석 처리하세요!

    def changeEvent(self, event):
        """포커스를 잃으면(바탕화면 클릭 등) 자동으로 숨기기"""
        if event.type() == event.Type.ActivationChange and not self.isActiveWindow():
            self.hide()