EMOJI = {
    'welcome': '🎉', 'question': '❓', 'open': '📚', 'help': '❔',
    'rating': '📊', 'cancel': '❌', 'success': '✅', 'warning': '⚠️', 
    'error': '🚫', 'add': '➕', 'check': '📋', 'pin': '📌', 
    'description': '📝', 'author': '👤', 'time': '⏳', 'status': '🔮', 
    'open_status': '✅', 'closed_status': '❌', 'online': '💻', 'offline': '🏫', 
    'mail': '✉️', 'target': '🎯', 'trophy': '🏆', 'empty': '📥',
    'calendar': '📅', 'info': 'ℹ️', 'sos': '🆘', 'open_questions': '📚',
    'hammer' : '🛠',
}

class UserText:
    start_message               = f"{EMOJI['welcome']} Добро пожаловать!"
    about                       = f"{EMOJI['sos']} <b>Справка по боту</b>\n\n" \
                                  f"{EMOJI['question']} Задать вопрос — создать новый вопрос;\n" \
                                  f"{EMOJI['open_questions']} Открытые вопросы — список активных вопросов;\n" \
                                  f"{EMOJI['rating']} Рейтинг классов — просмотр рейтинга классов;\n\n" \
                                  f"Для связи с поддержкой: /help или кнопка ниже"
    admin_panel                 = f"{EMOJI['hammer']} <b>Админ-меню</b>"
    command_not_found           = "Похоже, такая команда не существует... Чтобы получить список всех доступных команд, введите /help"

    empty_rating                = f"{EMOJI['rating']} Рейтинг пуст!"

    input_points                = f"{EMOJI['description']} Введите в формате: <code>Класс Баллы</code>\nПример: 10A 50"
    invalid_points_error        = f"{EMOJI['cancel']} Неверный формат. Нужно ввести класс и количество баллов!"
    points_are_not_int_instance = f"{EMOJI['cancel']} Баллы должны быть числом!"
    adding_points_error         = f"{EMOJI['warning']} Произошла ошибка при добавлении баллов"

    input_question_title        = f"{EMOJI['pin']} Введите краткий заголовок вопроса (до 100 символов):"
    question_title_too_long     = f"{EMOJI['warning']} Слишком длинный заголовок! Максимум 100 символов. Попробуйте еще раз:"
    input_question_desc         = f"{EMOJI['description']} Введите подробное описание вопроса (или отправьте '-', чтобы пропустить):"
    question_creation_cancelled = f"{EMOJI['info']} Создание вопроса отменено!"
    question_sent_successfully  = f"{EMOJI['success']} Ваш вопрос отправлен!"
    opened_questions            = f"{EMOJI['open']} <b>Открытые вопросы:</b>"
    no_opened_questions         = f"{EMOJI['empty']} Нет открытых вопросов!"
    select_question             = f"Выберите вопрос для просмотра:"
    question_not_found          = f"{EMOJI['error']} Вопрос не найден."

    input_username              = f"{EMOJI['mail']} Введите ваш Telegram-контакт (например, @username):"
    invalid_username            = "Пожалуйста, введите корректный Telegram-контакт (например, @username):"

    answer_sent                 = f"{EMOJI['success']} Ваш ответ отправлен автору вопроса!"
    input_meeting_datetime      = f"{EMOJI['calendar']} Введите дату и время встречи (например, 12.05 15:00):"

    cancelled = "Отменено"

    @staticmethod
    async def process_scores_text(class_name: str, score: int):
        return f"{EMOJI['open_status']} Класс {class_name} получил +{score} баллов!"
