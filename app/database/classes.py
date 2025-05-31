import os
import aiosqlite

from app.config import CLASS_DB_PATH


class_db_path = CLASS_DB_PATH or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'classes.db')


class ClassRatingService:
    '''The class manages requests to the classes table.'''
    
    async def init_classes_db() -> None:
        '''Classes database initialization.'''
        dir_path = os.path.dirname(class_db_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        async with aiosqlite.connect(class_db_path) as db:
            classes_creation = '''CREATE TABLE IF NOT EXISTS class_scores (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    class_name TEXT UNIQUE,
                                    total_score INTEGER DEFAULT 0
                                    )'''
            await db.execute(classes_creation)
            await db.commit()

    @staticmethod
    async def add_class_score(class_name: str, score_to_add: int) -> None:
        '''The method adds scores to a class.'''
        async with aiosqlite.connect(class_db_path) as db:
            class_ = await ClassRatingService.get_class_by_name(class_name)
            current_score = class_[2]
            request = 'class_scores SET total_score = ? WHERE class_name = ?'
            await db.execute(request, (current_score + score_to_add, class_name))
            await db.commit()

    @staticmethod
    async def get_class_scores() -> list[tuple[int, str, int]]:
        '''The method gets all classes info in descending order of their overall score.'''
        request = 'SELECT * FROM class_scores ORDER BY total_score DESC'
        async with aiosqlite.connect(class_db_path) as db:
            cursor = await db.execute(request)
            rows = await cursor.fetchall()
            return rows
        
    @staticmethod
    async def get_class_by_id(class_id: int) -> tuple[int, str, int]:
        '''The method gets class data by its ID.'''
        request = 'SELECT * FROM class_scores WHERE id = ?'
        async with aiosqlite.connect(class_db_path) as db:
            cursor = await db.execute(request, (class_id, ))
            result = await cursor.fetchone()
            return result
    
    @staticmethod
    async def get_class_by_name(class_name: str) -> tuple[int, str, int]:
        '''The method gets class data by its unique name.'''
        request = 'SELECT * FROM class_scores WHERE class_name = ?'
        async with aiosqlite.connect(class_db_path) as db:
            cursor = await db.execute(request, (class_name, ))
            result = await cursor.fetchone()
            return result

    @staticmethod
    async def get_columns_names(table_name: str) -> list[str]:
        '''The method gets column names from the table with a particular name.'''
        request = f'PRAGMA table_info("{table_name}")'
        async with aiosqlite.connect(class_db_path) as db:
            cursor = await db.execute(request)
            column_names = [i[1] for i in cursor.fetchall()] # to get the names only
            return column_names
        

async def classes_db_exists() -> bool | int:
    '''The method checks if the `CLASS_DB_PATH` exists.\n
       If it does, returns an amount of the classes in a table.
       Otherwise returns `False`
    '''
    if not os.path.exists(CLASS_DB_PATH):
        return False
    async with aiosqlite.connect(CLASS_DB_PATH) as db:
        request = 'SELECT COUNT(*) FROM class_scores'
        cursor = await db.execute(request)
        count = await cursor.fetchone()[0]
        return count