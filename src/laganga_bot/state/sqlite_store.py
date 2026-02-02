import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_PATH = "state/bot_history.db"

class SQLiteStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_db()

    def _ensure_db_directory(self):
        directory = os.path.dirname(self.db_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise

    def _initialize_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posted_deals (
                    id TEXT PRIMARY KEY,
                    posted_at TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def is_posted(self, deal_id: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM posted_deals WHERE id = ?", (str(deal_id),))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking posted status: {e}")
            return False

    def mark_as_posted(self, deal_id: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO posted_deals (id, posted_at) VALUES (?, ?)",
                (str(deal_id), datetime.now())
            )
            conn.commit()
            conn.close()
            logger.info(f"Marked deal {deal_id} as posted.")
        except sqlite3.Error as e:
            logger.error(f"Error marking deal as posted: {e}")

    def clear_history(self):
        """Clears all posted deals from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM posted_deals")
            conn.commit()
            conn.close()
            logger.info("Cleared all posted deals from history.")
        except sqlite3.Error as e:
            logger.error(f"Error clearing history: {e}")
