from aiogram.types import KeyboardButtonRequestUser
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
                          InlineKeyboardMarkup, InlineKeyboardButton

from .text import EMOJI
from app.config import Settings

from typing import List, Tuple, Dict


class UI:
    
    main_menu = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=f'{EMOJI["question"]} Задать вопрос'),
                    KeyboardButton(text=f'{EMOJI["open"]} Открытые вопросы')
                ],
                [
                    KeyboardButton(text=f'{EMOJI["rating"]} Рейтинг классов'),
                    KeyboardButton(text=f'{EMOJI["help"]} Помощь')
                ],
                [
                    KeyboardButton(text=f'{EMOJI['add']} Добавить старосту'),
                ]
            ],
            resize_keyboard=True
        )
    
    admin_menu = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=f'{EMOJI["add"]} Добавить баллы'),
                    KeyboardButton(text=f'{EMOJI["rating"]} Рейтинг классов')
                ],
                [
                    KeyboardButton(text=f'{EMOJI["check"]} Проверить БД')
                ]
            ],
            resize_keyboard=True
        )
    
    cancel_button = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=f"{EMOJI['cancel']} Отмена")]
            ],
            resize_keyboard=True
        )
    
    help_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Перейти к помощнику", url=Settings.helper_bot_url)]
            ]
        )
    
    request_user = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Отправить', request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False))],
            ])    
    
    @staticmethod
    def answer_type_buttons(qid: int):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{EMOJI['online']} Ответить в Telegram", callback_data=f"answer_online_{qid}")],
                [InlineKeyboardButton(text=f"{EMOJI['offline']} Встреча", callback_data=f"answer_offline_{qid}")]
            ]
        )
    
    @staticmethod
    def question_list(questions: List[Tuple]):
        inline_keyboard = []
        for q in questions:
            text = q[1]
            if len(text) > Settings.compact_string_length:
                text = text[:Settings.compact_string_length-3] + '...'
            inline_keyboard.append(
                [InlineKeyboardButton(text=f"{EMOJI['pin']} {text}", callback_data=f"question_{q[0]}")]
            )
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    
    @staticmethod
    def format_class_rating(scores: List[Tuple]) -> str:
        text = f"{EMOJI['trophy']} <b>Рейтинг классов:</b>\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for idx, (cls, score) in enumerate(scores, 1):
            if idx <= 3 and idx <= len(medals):
                prefix = f"{medals[idx-1]} "
            else:
                prefix = f"{idx}. "
            text += f"{prefix}<b>{cls}</b>: {score} баллов\n"
        return text
    
    @staticmethod
    def format_question(question: Dict, with_author: bool = False) -> str:
        text = f"<b>{question['title']}</b>\n\n"
        if question['description']:
            text += f"{question['description']}\n\n"
        text += f"{EMOJI['status']} Статус: "
        text += f"{EMOJI['open_status']} Открыт" if question['status'] == 'open' else f"{EMOJI['closed_status']} Закрыт"
        text += f"\n{EMOJI['time']} Создан: {question['created_at']}"
        if with_author:
            text += f"\n{EMOJI['author']} Автор: {question['author']}"
        return text
