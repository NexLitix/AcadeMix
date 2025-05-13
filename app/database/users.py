import os
import aiosqlite
from datetime import datetime
from .manager import DatabaseManager
from typing import List, Tuple, Dict, Any, Optional
from app.config import DB_PATH, CLASS_DB_PATH, ADMIN_IDS


db_manager = DatabaseManager(DB_PATH)
USER_DB_PATH = db_manager.path

class UsersTable:

    @staticmethod
    async def register_user(user_id: int, username: str) -> None:
        '''The method adds a new user into the users table or ignores the'''

        reg_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
        request = 'INSERT OR IGNORE INTO users(user_id, username, registration_date) VALUES(?,?,?)',
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (user_id, username, reg_datetime))
            await db.commit()



class QuestionsTable:
    
    @staticmethod
    async def get_open():
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute('SELECT q.id, q.title FROM questions q WHERE q.status = ?', ('open',))
            rows = await cursor.fetchall()
            return rows


    @staticmethod
    async def save_question(user_id: int, title: str, desc: str):
        request = 'INSERT INTO questions(author_id, title, description, status, created_at) VALUES(?,?,?,?,?)'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (user_id, title, desc, 'open', datetime.now().strftime('%Y-%m-%d %H:%M')))
            await db.commit()

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




class AnswersTable:
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





