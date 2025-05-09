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

# Use default path if DB_PATH is None
db_manager = DatabaseManager(DB_PATH)
USER_DB_PATH = db_manager.path

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

class ClassRatingService:
    @staticmethod
    async def get_class_scores():
        class_db_path = CLASS_DB_PATH or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'classes.db')
        if not os.path.exists(class_db_path):
            return []
        async with aiosqlite.connect(class_db_path) as conn:
            cursor = await conn.execute("SELECT class_name, total_score FROM class_scores ORDER BY total_score DESC")
            rows = await cursor.fetchall()
            return rows

    @staticmethod
    async def save_online_answer(qid: int, uid: int, contact: str):
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(
                'INSERT INTO answers(question_id, responder_id, answer_type, contact_info, created_at) VALUES(?,?,?,?,?)',
                (qid, uid, 'online', contact, datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
            await db.execute('UPDATE questions SET status = ? WHERE id = ?', ('closed', qid))
            await db.commit()

    @staticmethod
    async def save_offline_answer(qid: int, uid: int, mt: str):
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(
                'INSERT INTO answers(question_id, responder_id, answer_type, meeting_time, created_at) VALUES(?,?,?,?,?)',
                (qid, uid, 'offline', mt, datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
            await db.execute('UPDATE questions SET status = ? WHERE id = ?', ('closed', qid))
            await db.commit()

    @staticmethod
    async def register_user(uid: int, uname: str):
        reg = datetime.now().strftime('%Y-%m-%d %H:%M')
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(
                'INSERT OR IGNORE INTO users(user_id, username, registration_date) VALUES(?,?,?)',
                (uid, uname, reg)
            )
            await db.commit()

    @staticmethod
    async def save_question(uid: int, title: str, desc: str):
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(
                'INSERT INTO questions(author_id, title, description, status, created_at) VALUES(?,?,?,?,?)',
                (uid, title, desc, 'open', datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
            await db.commit()

    @staticmethod
    async def get_open():
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute('SELECT q.id, q.title FROM questions q WHERE q.status = ?', ('open',))
            rows = await cursor.fetchall()
            return rows

    @staticmethod
    async def get_question(qid: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute(
                'SELECT q.id, q.title, q.description, q.status, q.created_at, u.username FROM questions q LEFT JOIN users u ON q.author_id=u.user_id WHERE q.id=?',
                (qid,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0], 'title': row[1], 'description': row[2],
                'status': row[3], 'created_at': row[4], 'author': row[5] or 'Аноним'
            }

    @staticmethod
    async def add_class_score(class_name: str, score: int) -> bool:
        class_db_path = CLASS_DB_PATH or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'classes.db')
        async with aiosqlite.connect(class_db_path) as conn:
            cursor = await conn.execute(
                "SELECT total_score FROM class_scores WHERE class_name = ?", 
                (class_name,)
            )
            result = await cursor.fetchone()
            if result:
                new_score = result[0] + score
                await conn.execute(
                    "UPDATE class_scores SET total_score = ? WHERE class_name = ?",
                    (new_score, class_name)
                )
            else:
                await conn.execute(
                    "INSERT INTO class_scores (class_name, total_score) VALUES (?, ?)",
                    (class_name, score)
                )
            await conn.commit()
            return True
