import time
import threading
import pyperclip  # pip install pyperclip
import keyboard   # pip install keyboard
from PyQt6.QtCore import QObject, pyqtSignal

class ClipboardWorker(QObject):
    # UI 스레드와 통신하기 위한 커스텀 이벤트(Signal) 정의
    # 7년 차 개발자라면 '커스텀 이벤트 발송' 개념으로 이해하시면 됩니다.
    show_window_signal = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.last_content = ""
        self.running = True

    def start(self):
        """백그라운드 스레드에서 모니터링 시작"""
        # 1. 클립보드 감시 스레드
        monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        monitor_thread.start()

        # 2. 글로벌 단축키 등록 (Ctrl + Alt + V)
        # 윈도우 기본 Win + V와 충돌을 피하기 위해 임시로 설정했습니다.
        keyboard.add_hotkey('ctrl+alt+v', self._on_hotkey_pressed)

    def _monitor_clipboard(self):
        """실제 클립보드 변경을 감지하는 루프"""
        while self.running:
            try:
                # 현재 클립보드 텍스트 가져오기
                current_content = pyperclip.paste()

                # 내용이 비어있지 않고, 이전과 다를 때만 저장
                if current_content and current_content != self.last_content:
                    self.last_content = current_content
                    self.db.save_content(current_content)
                    print(f"[Log] 새 클립보드 저장됨: {current_content[:20]}...")

            except Exception as e:
                print(f"[Error] 클립보드 감시 중 오류: {e}")

            # CPU 점유율 과부하 방지를 위한 짧은 휴식 (Polling 방식의 한계)
            time.sleep(0.5)

    def _on_hotkey_pressed(self):
        """단축키가 눌렸을 때 실행"""
        print("[Log] 단축키 감지됨!")
        self.show_window_signal.emit() # UI 스레드에 "창 띄워라!"라고 신호 보냄

    def stop(self):
        self.running = False
        keyboard.unhook_all()