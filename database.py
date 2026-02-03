import sqlite3
from datetime import datetime

class ClipboardDatabase:
    def __init__(self, db_name="clipboard_history.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """데이터베이스 연결 객체를 반환합니다."""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """앱 실행 시 필요한 테이블을 생성합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # id: 고유 식별자
            # content: 복사된 내용
            # created_at: 복사된 시간
            # is_pinned: Win+V처럼 중요한 항목 고정 기능용
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