import os
import aiosqlite
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from app.config import DB_PATH, CLASS_DB_PATH, ADMIN_IDS


class ClassRatingService:
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

    @staticmethod
    async def get_class_scores():
        class_db_path = CLASS_DB_PATH or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'classes.db')
        if not os.path.exists(class_db_path):
            return []
        async with aiosqlite.connect(class_db_path) as conn:
            cursor = await conn.execute("SELECT class_name, total_score FROM class_scores ORDER BY total_score DESC")
            rows = await cursor.fetchall()
            return rows
