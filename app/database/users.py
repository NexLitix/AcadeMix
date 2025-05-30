import os
import sqlite3, aiosqlite
from datetime import datetime
from typing import Dict, Any, Optional

from ..text import DatabaseText
from app.config import USER_DB_PATH
from .settings import UsersTableSettings


class UsersDatabaseManager:
    def __init__(self, path: str = None):
        if not path: # Default to a local path if none provided
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

        users_creation = '''CREATE TABLE IF NOT EXISTS users (
                                user_id INTEGER PRIMARY KEY,
                                username TEXT,
                                points INTEGER DEFAULT 0,
                                registration_date TEXT,
                                is_headman BOOLEAN NOT NULL CHECK (is_headman IN (0, 1)) DEFAULT 0
                                )'''
        
        questions_creation = '''CREATE TABLE IF NOT EXISTS questions (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    author_id INTEGER,
                                    title TEXT,
                                    description TEXT,
                                    is_closed BOOLEAN NOT NULL CHECK (is_closed IN (0, 1)) DEFAULT 0,
                                    created_at TEXT,
                                    FOREIGN KEY (author_id) REFERENCES users (id)
                                    )'''
        
        answers_creation = '''CREATE TABLE IF NOT EXISTS answers (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                question_id INTEGER,
                                responder_id INTEGER,
                                answer_type TEXT,
                                contact_info TEXT,
                                meeting_time TEXT,
                                created_at TEXT,
                                FOREIGN KEY (question_id) REFERENCES users (id),
                                FOREIGN KEY (responder_id) REFERENCES users (id)
                                )'''
        
        battles_creation = '''CREATE TABLE IF NOT EXISTS battles (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                initiator_id INTEGER,
                                receiver_id INTEGER,
                                points INTEGER,
                                is_accepted BOOLEAN NOT NULL CHECK (is_accepted IN (0, 1)) DEFAULT 0,
                                comment TEXT,
                                winner INTEGER DEFAULT NULL,
                                created_at TEXT,
                                over_at TEXT DEFAULT NULL, 
                                FOREIGN KEY (initiator_id) REFERENCES users (id),
                                FOREIGN KEY (receiver_id) REFERENCES users (id)
                                )'''

        cursor.execute(users_creation)
        cursor.execute(questions_creation)
        cursor.execute(answers_creation)
        cursor.execute(battles_creation)
        conn.commit()
        conn.close()


db_manager = UsersDatabaseManager(USER_DB_PATH)
USER_DB_PATH = db_manager.path


class UsersTable:
    '''The class manages requests to the users table.'''

    @staticmethod
    async def register_user(user_id: int, username: str) -> None:
        '''The method adds a new user into the users table or ignores a 
           request if a user with such an ID already exists.\n
           <b>NOTE:</b> `is_headman` flag in this operation has a default value (`0`, or `False`)
        '''
        reg_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
        request = 'INSERT OR IGNORE INTO users(user_id, username, registration_date) VALUES(?,?,?)'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (user_id, username, reg_datetime))
            await db.commit()

    @staticmethod
    async def set_headman(user_id: int) -> None:
        '''The method updates a user's `is_headman` status to `1` (`True`).
           It is normally called after `register_user()` method      
        '''
        request = 'UPDATE users SET is_headman = ? WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (1, user_id))
            await db.commit()

    @staticmethod
    async def set_regular_user(user_id: int) -> None:
        '''The method updates a user's `is_headman` status to `0` (`False`).'''
        request = 'UPDATE users SET is_headman = ? WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (0, user_id))
            await db.commit()

    @staticmethod
    async def is_headman(user_id: int) -> bool:
        '''The method checks if a user is a headman.'''
        request = 'SELECT is_headman FROM users WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute(request, (user_id, ))
            result = await cursor.fetchone()
            if result[0] == UsersTableSettings.is_headman_flag:
                return True
            return False

    
class QuestionsTable:
    '''The class manages requests to the questions table.'''

    @staticmethod
    async def save_question(user_id: int, title: str, desc: str) -> None:
        '''The method adds a new question.\n
           <b>NOTE:</b> `is_closed` flag in this operation has a default value (`0`, or `False`)
        '''
        request = 'INSERT INTO questions(author_id, title, description, created_at) VALUES(?,?,?,?,?)'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (user_id, title, desc, datetime.now().strftime('%Y-%m-%d %H:%M')))
            await db.commit()

    @staticmethod
    async def close_question(qid: int) -> None:
        '''The method updates question `is_closed` status to `1` (`True`), i.e. closes the question.'''
        request = 'UPDATE questions SET is_closed = ? WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (1, qid))
            await db.commit()

    @staticmethod
    async def open_question(qid: int) -> None:
        '''The method updates question `is_closed` status to `0` (`False`), i.e. opens the question.'''
        request = 'UPDATE questions SET is_closed = ? WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (0, qid))
            await db.commit()

    @staticmethod
    async def get_question(qid: int) -> Optional[Dict[str, Any]]:
        '''The method gets a question info by its ID.'''
        request = 'SELECT q.id, q.title, q.description, q.status, q.created_at, u.username FROM questions q LEFT JOIN users u ON q.author_id=u.user_id WHERE q.id=?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute(request, (qid, ))
            result = await cursor.fetchone()
            if result:
                return {'id': result[0], 'title': result[1], 'description': result[2],
                        'status': result[3], 'created_at': result[4], 'author': result[5] or 'Аноним'}
            return None
    
    @staticmethod
    async def get_opened() -> list[tuple[int, str]]:
        '''The method gets all unanswered questions.'''
        request = 'SELECT id, title FROM questions WHERE is_closed = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute(request, (0, ))
            rows = await cursor.fetchall()
            return rows
    

class AnswersTable:
    '''The class manages requests to the answers table.'''

    @staticmethod
    async def get_qid_by_aid(aid: int) -> int:
        '''The method gets a question ID by answer ID.'''
        request = 'SELECT question_id FROM answers WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute(request, (aid, ))
            result = await cursor.fetchone()
            return result[0]

    @staticmethod
    async def get_answers_for_question(qid: int) -> list[tuple[int, int, int, str, str, str, str]]:
        '''The method gets all answers for a question by its ID.'''
        request = 'SELECT * FROM answers WHERE question_id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            cursor = await db.execute(request, (qid, ))
            rows = await cursor.fetchall()
            return rows

    @staticmethod
    async def save_online_answer(qid: int, uid: int, contact: str) -> None:
        '''The method saves an online answer for a question.'''
        request = 'INSERT INTO answers(question_id, responder_id, answer_type, contact_info, created_at) VALUES(?,?,?,?,?)'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (qid, uid, 'online', contact, datetime.now().strftime('%Y-%m-%d %H:%M')))
            await QuestionsTable.close_question(qid)
            await db.commit()

    @staticmethod
    async def save_offline_answer(qid: int, uid: int, mt: str) -> None:
        '''The method saves an offline answer for a question.'''
        request = 'INSERT INTO answers(question_id, responder_id, answer_type, meeting_time, created_at) VALUES(?,?,?,?,?)'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (qid, uid, 'offline', mt, datetime.now().strftime('%Y-%m-%d %H:%M')))
            await QuestionsTable.close_question(qid)
            await db.commit()

    @staticmethod 
    async def reject_answer_by_aid(aid: int) -> None:
        '''The method deletes an answer for a question by answer ID.\n
            <b>NOTE:</b> having deleted an answer, a method checks the amount of other 
                         answers for this question, and in case it equals to 0, it sets
                         the question status `is_closed` to `0`, i.e. opens the question again.
        '''
        request = 'DELETE * FROM answers WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (aid, ))
            await db.commit()
            qid = await AnswersTable.get_qid_by_aid(aid)
            answers = await AnswersTable.get_answers_for_question(qid)
            if len(answers) == 0:
                await QuestionsTable.open_question(qid)
            

class BattlesTable:
    '''The class manages requests to the battles table.'''

    @staticmethod
    async def start_battle(initiator_id: int, receiver_id: int, points: int, comment: str) -> None:
        '''The method adds a new battle.\n
           <b>NOTE:</b> fields `is_accepted`, `winner`, `over_at` have default values!
        '''
        if await UsersTable.is_headman(initiator_id) and await UsersTable.is_headman(initiator_id):
            request = 'INSERT OR IGNORE INTO battles(initiator_id, receiver_id, points, comment, created_at) VALUES(?,?,?,?,?)'
            async with aiosqlite.connect(USER_DB_PATH) as db:
                await db.execute(request, (initiator_id, receiver_id, points, comment, datetime.now().strftime('%Y-%m-%d %H:%M')))
                await db.commit()
        else:
            raise ValueError

    @staticmethod
    async def set_accepted_status(bid: int) -> None:
        '''The method updates battle status `is_accepted` to `1` (`True`). This action is supposed to be irreversible.'''
        request = 'UPDATE battles SET is_accepted = ? WHERE id = ?'
        async with aiosqlite.connect(USER_DB_PATH) as db:
            await db.execute(request, (1, bid))
            await db.commit()