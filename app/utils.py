from aiogram.types import Message

from .text import UserText
from .config import ADMIN_IDS
from .exceptions import InvalidPointsException
from .database.users import UsersTable

import dotenv, os
import pandas as pd
from typing import Any


class PermissionCheck:
    @staticmethod
    async def is_bot_admin(event: Message) -> bool:
        return event.from_user.id in ADMIN_IDS

    @staticmethod
    async def is_bot_headman(event: Message) -> bool:
        return await UsersTable.is_headman(event.from_user.id)
    

class ExcelSheets:  
    async def to_excel(values: dict[str, list], path: str) -> str:
        '''The function converts dataframes into excel file. Returns the path to this file.'''
        dataframe = pd.DataFrame(values)
        dataframe.to_excel(path, sheet_name='Классы', index=False)
        return path

    
async def check_points(points: str):
    parts = points.split()
    if len(parts)!= 2:
        raise InvalidPointsException(UserText.invalid_points_error)
    class_name, score = parts 
    try:
        score = int(score)
    except ValueError:
        raise InvalidPointsException(UserText.points_are_not_int_instance)
    else:
        return {'class_name' : class_name, 'score' : score}
    

async def process_into_dict(columns: list[str], rows: list[tuple[Any]]) -> dict[str, list[Any]]:
    '''The function converts a list of column names (param `columns`) 
        and a list of tuples with data from db table rows (param `rows`)
        into a dictionary with keys as column names and values as tuples 
        items ordered as dict keys.\n

        Parameters
        ----------
        columns : list[str] 
        rows : list[tuple[Any]]

        <b>NOTE</b> here is an easy example:\n
        
        Input
        -----
        `columns = ['name', 'surname', 'age']`

        `rows = [('Elon', 'Musk', 53), ('Bill', 'Gates', 69), ('Pavel', 'Durov', 40)]`

        Output
        -----
        `values = {'name' : ['Elon', 'Bill', 'Pavel'], 'surname' : ['Musk', 'Gates', 'Durov'], 'age' : [53, 69, 40]]}`
        '''
    values = {}
    for i in range(len(columns)):
        values[columns[i]] = []
    dict_lst = list(values.values())
    for lst in dict_lst:
        for row in rows:
            lst.append(row[dict_lst.index(lst)])
    return values
