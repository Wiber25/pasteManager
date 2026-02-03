import sqlite3
import os
import logging
from datetime import datetime

class ClipboardDatabase:
    def __init__(self, db_name="clipboard_history.db"):
        # 로깅 설정
        self.setup_logging()
        
        try:
            # 1. 유저의 홈 디렉토리 하위 .PasteManager 폴더 사용 (안정성 향상)
            # 예: C:\Users\User\.PasteManager
            app_data_path = os.path.join(os.path.expanduser("~"), '.PasteManager')
            logging.info(f"AppData Path: {app_data_path}")
            
            # 2. 폴더가 없으면 생성
            if not os.path.exists(app_data_path):
                logging.info("Creating AppData directory...")
                os.makedirs(app_data_path, exist_ok=True)
                logging.info("AppData directory created successfully.")
            
            # 3. 전체 DB 경로 설정
            self.db_path = os.path.join(app_data_path, db_name)
            logging.info(f"Database Path: {self.db_path}")
            
            self.init_db()
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}", exc_info=True)
            raise e

    def setup_logging(self):
        # 로그 파일 경로 설정 (홈 디렉토리/.PasteManager 폴더 내)
        try:
            log_dir = os.path.join(os.path.expanduser("~"), '.PasteManager')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'db_debug.log')
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                encoding='utf-8' # 한글 로그 지원
            )
            logging.info("Logging initialized.")
        except Exception as e:
            # 로깅 설정 실패 시 콘솔에 출력 (예비책)
            print(f"Failed to setup logging: {e}")

    def get_connection(self):
        """절대 경로를 사용하여 연결"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        # ... (이전과 동일한 테이블 생성 로직) ...
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_pinned INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def save_content(self, content):
        """새로운 클립보드 내용을 저장합니다. (중복 방지 로직 포함)"""
        if not content.strip():
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. 가장 최근 저장된 내용과 똑같은지 확인 (중복 저장 방지)
            cursor.execute("SELECT content FROM clipboard_history ORDER BY id DESC LIMIT 1")
            last_item = cursor.fetchone()
            
            if last_item and last_item[0] == content:
                return # 내용이 같으면 저장하지 않음

            # 2. 새로운 내용 삽입
            cursor.execute(
                "INSERT INTO clipboard_history (content, created_at) VALUES (?, ?)",
                (content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            
            # 3. 최적화: 너무 오래된 기록 삭제 (예: 최신 100개만 유지)
            cursor.execute("""
                DELETE FROM clipboard_history 
                WHERE id NOT IN (
                    SELECT id FROM clipboard_history 
                    ORDER BY id DESC LIMIT 100
                ) AND is_pinned = 0
            """)
            
            conn.commit()

    def get_history(self, limit=20):
        """최근 클립보드 내역을 가져옵니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 고정된 항목(pinned)을 먼저 보여주고, 그 다음 최신순으로 정렬
            cursor.execute("""
                SELECT id, content, created_at, is_pinned 
                FROM clipboard_history 
                ORDER BY is_pinned DESC, id DESC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()

    def delete_item(self, item_id):
        """특정 항목 삭제"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clipboard_history WHERE id = ?", (item_id,))
            conn.commit()

    def toggle_pin(self, item_id):
        """항목 고정/해제"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE clipboard_history SET is_pinned = 1 - is_pinned WHERE id = ?", (item_id,))
            conn.commit()