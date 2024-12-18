# Пример создания reply-клавиатуры
#общая клавиатура которая распологается внизу называется reply
# импорт модулей
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv
import os

# подгружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# кнопки reply-клавиатуры
buttons = ['Москва', 'Санкт-Петербург', 'Екатеринбург', 'Уфа']

# форма reply-клавиатуры
form_ver = False    # если True - вертикальное расположение кнопок
if form_ver:
    reply_frame = [
        [buttons[0]], [buttons[1]], [buttons[2]]
    ]
else:
    reply_frame = [
        [buttons[0], buttons[1], buttons[2]]
    ]    
        
# создаем reply клавиатуру
reply_keyboard = ReplyKeyboardMarkup(
    reply_frame,
    resize_keyboard = True,   # автоматический размер кнопок
    one_time_keyboard = True  # скрыть коавиатуру после нажатия
)    

# функция-обработчик команды /city
async def city(update: Update, _):

    # прикрепляем reply клавиатуру к сообщению
    await update.message.reply_text('Пример reply клавиатуры:', reply_markup = reply_keyboard)
    
# функция-обработчик команды /hidden
async def hidden(update: Update, _):

    # прикрепляем reply клавиатуру к сообщению
    await update.message.reply_text('Клавиатуры скрыта', reply_markup = ReplyKeyboardRemove())    

# функция-обработчик нажатий на кнопки
async def button(update: Update, _):

    # получаем callback query из update
    query = update.callback_query

    # всплывающее уведомление
    await query.answer('Это всплывающее уведомление!')
    
    # редактируем сообщение после нажатия
    await query.edit_message_text(text=f"Вы нажали на кнопку: {query.data}")

# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

    # добавляем обработчик команды /city
    application.add_handler(CommandHandler('city', city))

    # добавляем обработчик команды /hidden
    application.add_handler(CommandHandler('hidden', hidden))    

    # запускаем бота (нажать Ctrl-C для остановки бота)
    print('Бот запущен...')    
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":      # если модуль запущен как основная программа

    # запуск бота
    main()