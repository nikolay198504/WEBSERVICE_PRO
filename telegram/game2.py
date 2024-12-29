# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import requests
import aiohttp
import base64
import json

# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# создание клавиатуры "Продолжить"
buttons_cont = [
    InlineKeyboardButton('Продолжить', callback_data='cont')
]
frame_cont = [[buttons_cont[0]]]
inline_cont = InlineKeyboardMarkup(frame_cont)

# создание клавиатуры ответа
buttons_menu = [
    InlineKeyboardButton('Правда', callback_data='yes'),
    InlineKeyboardButton('Не правда', callback_data='no')
]
frame_menu = [[buttons_menu[0], buttons_menu[1]]]
inline_menu = InlineKeyboardMarkup(frame_menu)

# функция-обработчик команды /start
async def start(update, context):
    message  = 'Привет! Это игра, в которой бот задает вопрос,'
    message += ' участник отвечает - правда это или нет.'
    message += ' Для начала игры введите /game.'
    await update.message.reply_text(message)

# функция-обработчик команды /game
async def game(update, context):
    user_id = update.message.from_user.id
    
    # Очищаем историю пользователя
    context.bot_data[user_id] = {}
    context.bot_data[user_id]['answers'] = []
    context.bot_data[user_id]['history'] = []
    
    # -- Выводим в консоль, чтобы видеть текущее состояние истории
    print(f"[DEBUG] /game: История до формирования вопроса: {context.bot_data[user_id]}")
    
    first_message = await update.message.reply_text('Минуту...')
    
    # формируем вопрос, передавая текущую историю
    quest = await query_api(context.bot_data[user_id]['history'])
    
    # Добавляем полученный вопрос и правильный ответ в словари
    context.bot_data[user_id]['answers'].append(quest['answer'])
    context.bot_data[user_id]['history'].append(quest['question'])
    
    # ограничение истории до последних 5 вопросов
    if len(context.bot_data[user_id]['history']) > 5:
        context.bot_data[user_id]['history'] = context.bot_data[user_id]['history'][-5:]
    
    # -- Выводим в консоль, чтобы видеть состояние истории после добавления
    print(f"[DEBUG] /game: История после формирования вопроса: {context.bot_data[user_id]}")
    
    # редактируем сообщение пользователю с новым вопросом
    await first_message.edit_text(quest['question'], reply_markup=inline_menu)

# Функция обращается к API с запросом
#   history - история диалога в виде списка
# Возвращает ответ от API в виде словаря {'question': str, 'answer': bool}
async def query_api(history):
    system = 'Ты задаешь вопросы участникам чата'
    hist = ' '.join(history)
    user = (
        'Придумай один шуточный или серьезный вопрос для викторины '
        'на предмет "правда или ложь". Пользователи чата должны угадать, правда это или нет. '
        'Но вопросы не должны быть слишком очевидными (например, очевидный: "человек умеет летать?").\n'
        'Не начинай вопрос с "В некоторых странах". '
        'Верни результат в формате JSON: {"question": str, "answer": bool}. '
        f'Не повторяй слова из истории: {hist}.\n'
    )

    param = {
        'system': system,
        'user': user,
        'temperature': 0.5,
        'format': { "type": "json_object" }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8000/api/request', json=param) as response:
            # получение ответа от API
            answer = await response.json()
            # внутри 'message' у нас лежит JSON-строка {"question": "...", "answer": ...}
            return json.loads(answer['message'])

# функция-обработчик нажатий на кнопки
async def button(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id

    # обработка кнопок "Правда", "Не правда"
    if query.data in {'yes', 'no'}:
        answer_user = (query.data == 'yes')  # True, если 'yes', иначе False
        answer_right = context.bot_data[user_id]['answers'][-1]
        message = 'Вы совершенно правы!' if answer_user == answer_right else 'Вы не угадали'
        
        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=inline_cont)
        await query.answer()
        return

    # обработка кнопки "Продолжить"
    if query.data == 'cont':
        # -- Выводим текущую историю до добавления нового вопроса
        print(f"[DEBUG] (cont): История до формирования нового вопроса: {context.bot_data[user_id]}")
        
        first_message = await context.bot.send_message(chat_id=user_id, text='Минуту...')
        
        quest = await query_api(context.bot_data[user_id]['history'])
        context.bot_data[user_id]['answers'].append(quest['answer'])
        context.bot_data[user_id]['history'].append(quest['question'])
        
        # ограничение истории
        if len(context.bot_data[user_id]['history']) > 5:
            context.bot_data[user_id]['history'] = context.bot_data[user_id]['history'][-5:]
        
        # -- Выводим текущую историю после формирования нового вопроса
        print(f"[DEBUG] (cont): История после формирования нового вопроса: {context.bot_data[user_id]}")

        await first_message.edit_text(quest['question'], reply_markup=inline_menu)
        await query.answer()
        return

# функция "Запуск бота"
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('game', game))
    application.add_handler(CallbackQueryHandler(button))

    print('Бот запущен...')
    application.run_polling()
    print('Бот остановлен')

if __name__ == "__main__":
    main()
