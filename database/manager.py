import sqlite3
import os
from threading import Lock

class Manager:
    def __init__(self, db_path="database/users"):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        self._locks = {}
        self._global_lock = Lock()

    def _get_lock(self, bot_id):
        with self._global_lock:
            if bot_id not in self._locks:
                self._locks[bot_id] = Lock()
            return self._locks[bot_id]

    def _get_db_path(self, bot_id):
        # Sanitize bot_id to be safe for filename
        safe_id = "".join(c for c in str(bot_id) if c.isalnum() or c in ('-', '_'))
        return os.path.join(self.db_path, f"{safe_id}.db")

    def _init_db(self, bot_id):
        path = self._get_db_path(bot_id)
        try:
            with self._get_lock(bot_id):
                with sqlite3.connect(path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users_dmed (
                            user_id TEXT PRIMARY KEY
                        )
                    """)
                    conn.commit()
        except Exception as e:
            print(f"Error initializing DB for {bot_id}: {e}")

    def check_user(self, bot_id, user_id):
        """Checks if user exists in the bot's database. Returns True if exists."""
        try:
            self._init_db(bot_id)
            path = self._get_db_path(bot_id)
            with self._get_lock(bot_id):
                with sqlite3.connect(path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM users_dmed WHERE user_id = ?", (str(user_id),))
                    return cursor.fetchone() is not None
        except Exception as e:
            print(f"Database error (check): {e}")
            return False

    def add_user(self, bot_id, user_id):
        """Inserts user into the bot's database. Returns True if success."""
        try:
            self._init_db(bot_id)
            path = self._get_db_path(bot_id)
            with self._get_lock(bot_id):
                with sqlite3.connect(path) as conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO users_dmed (user_id) VALUES (?)", (str(user_id),))
                        conn.commit()
                        return True
                    except sqlite3.IntegrityError:
                        return False # Already exists
        except Exception as e:
            print(f"Database error (insert): {e}")
            return False

    def delete_user(self, bot_id, user_id):
        try:
            self._init_db(bot_id)
            path = self._get_db_path(bot_id)
            with self._get_lock(bot_id):
                with sqlite3.connect(path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users_dmed WHERE user_id = ?", (str(user_id),))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Database error (delete): {e}")
            return False
