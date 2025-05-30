from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from app.ui import UI
from ..config import CLASS_DB_PATH
from ..text import UserText, DatabaseText, EMOJI
from ..fsm_states import PointsStates, HeadmanContactStates

from ..exceptions import InvalidPointsException
from ..utils import PermissionCheck, ExcelSheets, check_points, process_into_dict

from ..database.users import UsersTable
from ..database.classes import ClassRatingService, classes_db_exists

from ..middlewares.admin_middleware import AdminMiddleware

import os
import aiosqlite


admin_router = Router()
admin_router.message.middleware(AdminMiddleware())


@admin_router.message(F.text == f"{EMOJI['add']} Добавить старосту")
async def add_headman(message: Message, state: FSMContext):
    await message.answer(UserText.send_contact, reply_markup=UI.request_user)
    await state.set_state(HeadmanContactStates.contact)


@admin_router.message(HeadmanContactStates.contact)
async def process_headman(bot: Bot, message: Message, state: FSMContext):
    data = await state.update_data(user_id=message.contact.user_id)
    await state.clear()
    try:
        await UsersTable.register_user(data['user_id'], data)
        await UsersTable.set_headman(data['user_id'])
    except Exception as e:
        await message.answer(await UserText.some_error_occurred(e))
    else: 
        await message.answer(UserText.headman_added_successfully)


@admin_router.message(F.text == f"{EMOJI['add']} Добавить баллы")
async def add_points(message: Message, state: FSMContext):
    await message.answer(UserText.input_points, reply_markup=UI.cancel_button)
    await state.set_state(PointsStates.points)


@admin_router.message(PointsStates.points)
async def process_score(message: Message, state: FSMContext):
    if message.text == f"{EMOJI['cancel']} Отмена":
        await state.clear()
        await message.answer(UserText.cancelled, reply_markup=UI.admin_menu)
    else:
        try:
            data = await check_points(message)
        except InvalidPointsException as e:
            await message.answer(e)
            await state.clear()
        else:
            success = await ClassRatingService.add_class_score(data['class_name'], data['score'])
            if success:
                await message.answer(await UserText.process_scores_text(data['class_name'], data['score']), reply_markup=UI.admin_menu())
            else:
                await message.answer(UserText.adding_points_error, reply_markup=UI.admin_menu())
                await state.clear()


@admin_router.message(F.text == f"{EMOJI['check']} Проверить БД")
async def admin_check_db(message: Message):
    result = await classes_db_exists()
    if isinstance(result, int):
        await message.answer(await DatabaseText.classes_db_checked(result, CLASS_DB_PATH))
        await message.answer(DatabaseText.classes_db_excel_sent)
        columns = await ClassRatingService.get_columns_names('class_scores')
        rows = await ClassRatingService.get_class_scores()
        data = await process_into_dict(columns, rows)
        file = await ExcelSheets.to_excel(data, 'classes_db.xlsx')
        await message.answer_document(FSInputFile(path=file))
    else: 
        await message.answer(await DatabaseText.classes_db_not_found_on_path(CLASS_DB_PATH))