# Пример создания inline-клавиатуры

# кнопки которые прикрепляются к каждому сообщению они называются inline кнопки

# импорт библиотек
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os

# подгружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# создаем кнопки
buttons = [
    InlineKeyboardButton('Новая задача', callback_data = 'task'),
    InlineKeyboardButton('История', callback_data = 'history'),
    InlineKeyboardButton(
        'Документация',
        callback_data = 'docs',
        url = 'https://docs.python-telegram-bot.org/en/stable/index.html'
    )    
]  

# форма inline клавиатуры
form_ver = True # если стоит True то кнопки распологаются вертикально
if form_ver:    # если вертикальное расположение
    inline_frame = [
        [buttons[0]], [buttons[1]], [buttons[2]]
    ]
else:
    inline_frame = [
        [buttons[0], buttons[1], buttons[2]]
    ]    

# создаем inline клавиатуру
inline_keyboard = InlineKeyboardMarkup(inline_frame)

# функция-обработчик команды /start
async def start(update: Update, _):

    # прикрепляем inline клавиатуру к сообщению
    await update.message.reply_text('Выберите пункт меню:', reply_markup=inline_keyboard)

# функция-обработчик нажатий на кнопки
async def button(update: Update, context):

    # получаем callback query из update
    query = update.callback_query

    # всплывающее уведомление
    await query.answer('Это всплывающее уведомление!')
    
    # редактируем сообщение после нажатия
    await query.edit_message_text(text = f'Вы нажали на кнопку: {query.data}')
    
    # новая клавиатура
    await query.message.reply_text(text = 'Выберите пункт меню:', reply_markup=inline_keyboard)

# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем CallbackQueryHandler (для inline кнопок)
    application.add_handler(CallbackQueryHandler(button))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    print('Бот запущен...')
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":      # если модуль запущен как основная программа

    # запуск бота
    main()