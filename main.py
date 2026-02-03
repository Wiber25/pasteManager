import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

# 우리가 만든 파일들 불러오기
from database import ClipboardDatabase
from clipboard_worker import ClipboardWorker
from ui.main_window import MainWindow

def main():
    # 1. PyQt 앱 인스턴스 생성
    app = QApplication(sys.argv)
    
    # 윈도우 작업표시줄 아이콘 중복 방지 (선택 사항)
    app.setQuitOnLastWindowClosed(False)

    # 2. 각 모듈 초기화
    db = ClipboardDatabase()
    window = MainWindow(db)
    worker = ClipboardWorker(db)

    # 3. 비즈니스 로직 연결 (이벤트 바인딩)
    # Worker가 단축키 신호를 쏘면(Signal), UI 창을 띄웁니다(Slot)
    worker.show_window_signal.connect(window.show_at_cursor)

    # 4. 백그라운드 스레드 시작
    worker.start()

    # 5. 시스템 트레이 아이콘 설정 (앱이 백그라운드에서 돌고 있음을 표시)
    tray_icon = QSystemTrayIcon(QIcon.fromTheme("edit-paste"), app) # 기본 아이콘 사용
    tray_menu = QMenu()
    
    show_action = QAction("열기", app)
    show_action.triggered.connect(window.show_at_cursor)
    
    quit_action = QAction("종료", app)
    quit_action.triggered.connect(app.quit)
    
    tray_menu.addAction(show_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    # 6. 앱 실행 루프 진입
    sys.exit(app.exec())

if __name__ == "__main__":
    main()