import os
import sqlite3
import aiosqlite
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from app.config import DB_PATH, CLASS_DB_PATH, ADMIN_IDS


class DatabaseManager:
    def __init__(self, path: str = None):
        # Default to a local path if none provided
        if not path:
            self.path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.db')
        else:
            self.path = path

        dir_path = os.path.dirname(self.path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        self._create_tables_sync()

    def _create_tables_sync(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                points INTEGER DEFAULT 0,
                registration_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'open',
                created_at TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                responder_id INTEGER,
                answer_type TEXT,
                contact_info TEXT,
                meeting_time TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()


async def init_classes_db():
    class_db_path = CLASS_DB_PATH or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'classes.db')
    dir_path = os.path.dirname(class_db_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    async with aiosqlite.connect(class_db_path) as db_conn:
        await db_conn.execute('''
            CREATE TABLE IF NOT EXISTS class_scores (
                class_name TEXT PRIMARY KEY,
                total_score INTEGER DEFAULT 0
            )
        ''')
        await db_conn.commit()
