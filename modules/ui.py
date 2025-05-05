from telebot import types
from typing import List, Tuple, Dict, Any

from modules.config import EMOJI, TEXT

class UI:
    @staticmethod
    def main_menu():
        # Создание главного меню с кнопками для пользователя
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            types.KeyboardButton(f'{EMOJI["question"]} Задать вопрос'),
            types.KeyboardButton(f'{EMOJI["open"]} Открытые вопросы')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["rating"]} Рейтинг классов'),
            types.KeyboardButton(f'{EMOJI["help"]} Помощь')
        )
        return kb

    @staticmethod
    def admin_menu():
        # Создание меню администратора с дополнительными функциями
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            types.KeyboardButton(f'{EMOJI["add"]} Добавить баллы'),
            types.KeyboardButton(f'{EMOJI["contact"]} Управление контактами')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["rating"]} Рейтинг классов'),
            types.KeyboardButton(f'{EMOJI["check"]} Проверить БД')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["back"]} Вернуться')
        )
        return kb

    @staticmethod
    def contact_management_menu():
        # Создание меню для управления контактами
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            types.KeyboardButton(f'{EMOJI["add"]} Добавить контакт'),
            types.KeyboardButton(f'{EMOJI["cancel"]} Удалить контакт')
        )
        kb.add(
            types.KeyboardButton(f'{EMOJI["check"]} Список контактов'),
            types.KeyboardButton(f'{EMOJI["back"]} Назад')
        )
        return kb

    @staticmethod
    def cancel_button():
        # Кнопка отмены текущего действия
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton(f"{EMOJI['cancel']} Отмена"))
        return kb

    @staticmethod
    def back_button():
        # Кнопка возврата назад
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton(f"{EMOJI['back']} Назад"))
        return kb

    @staticmethod
    def answer_type_buttons(qid: int):
        # Кнопки выбора типа ответа на вопрос
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton(
                f"{EMOJI['online']} Ответить в Telegram", 
                callback_data=f"answer_online_{qid}"
            ),
            types.InlineKeyboardButton(
                f"{EMOJI['offline']} Личная встреча(в школе)", 
                callback_data=f"answer_offline_{qid}"
            )
        )
        return kb

    @staticmethod
    def question_list(questions: List[Tuple]):
        # Создание списка вопросов с кнопками
        kb = types.InlineKeyboardMarkup(row_width=1)
        for q in questions:
            text = q[1]
            if len(text) > 40:
                text = text[:37] + '...'
            kb.add(types.InlineKeyboardButton(
                f"{EMOJI['pin']} {text}", 
                callback_data=f"question_{q[0]}"
            ))
        return kb

    @staticmethod
    def help_button():
        # Кнопка перехода к помощнику
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            f"{EMOJI['sos']} Перейти к помощнику", 
            url="https://t.me/AcadeMix_Support_bot"
        ))
        return kb

    @staticmethod
    def format_welcome_message() -> str:
        # Форматирование приветственного сообщения
        return f"""
{TEXT['welcome']}

<b>Возможности бота:</b>
• {EMOJI['question']} Задавайте учебные вопросы
• {EMOJI['open']} Отвечайте на вопросы других учеников
• {EMOJI['rating']} Следите за рейтингом классов

<b>Используйте меню для навигации</b>
"""

    @staticmethod
    def format_admin_welcome() -> str:
        # Форматирование приветствия для администратора
        return f"""
{TEXT['admin_welcome']}

<b>Доступные функции:</b>
• {EMOJI['add']} Добавление баллов классам
• {EMOJI['contact']} Управление авторизованными контактами
• {EMOJI['rating']} Просмотр рейтинга классов
• {EMOJI['check']} Проверка состояния базы данных

<b>Используйте меню для навигации</b>
"""

    @staticmethod
    def format_help_message() -> str:
        # Форматирование справочного сообщения
        return f"""
{TEXT['help_title']}

<b>Основные функции:</b>
{EMOJI['question']} <b>Задать вопрос</b> - создать новый вопрос
{EMOJI['open']} <b>Открытые вопросы</b> - список активных вопросов
{EMOJI['rating']} <b>Рейтинг классов</b> - текущий рейтинг

<b>Команды:</b>
/start - перезапустить бота
/help - показать эту справку
"""

    @staticmethod
    def format_class_rating(scores: List[Tuple]) -> str:
        # Форматирование рейтинга классов с медалями
        if not scores:
            return TEXT['empty_rating']
            
        text = f"{TEXT['rating_title']}\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, (cls, score) in enumerate(scores, 1):
            if idx <= 3 and idx <= len(medals):
                prefix = f"{medals[idx-1]} "
            else:
                prefix = f"{idx}. "
            text += f"{prefix}<b>{cls}</b>: {score} {EMOJI['points']}\n"
            
        return text

    @staticmethod
    def format_question(question: Dict[str, Any], with_author: bool = False) -> str:
        # Форматирование информации о вопросе
        text = f"<b>{question['title']}</b>\n\n"
        
        if question['description'] and question['description'] != 'Нет описания':
            text += f"{question['description']}\n\n"
        
        text += f"{EMOJI['status']} <b>Статус:</b> "
        text += f"{EMOJI['open_status']} Открыт" if question['status'] == 'open' else f"{EMOJI['closed_status']} Закрыт"
        text += f"\n{EMOJI['time']} <b>Создан:</b> {question['created_at']}"
        
        if with_author:
            text += f"\n{EMOJI['author']} <b>Автор:</b> {question['author']}"
            
        return text

    @staticmethod
    def format_authorized_contacts(contacts: List[str]) -> str:
        # Форматирование списка авторизованных контактов
        if not contacts:
            return f"{EMOJI['empty']} <b>Список авторизованных контактов пуст</b>"
            
        text = f"{EMOJI['authorized']} <b>Авторизованные контакты:</b>\n\n"
        for idx, contact in enumerate(contacts, 1):
            text += f"{idx}. {contact}\n"
            
        return text