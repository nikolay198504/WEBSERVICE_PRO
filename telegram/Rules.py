# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update                    
from dotenv import load_dotenv
import os
import requests
import aiohttp

# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# функция-обработчик команды /start
async def start(update, context):
    # сообщение пользователю
    await update.message.reply_text("Привет! Я консультант компании Rules!")

# функция-обработчик команды /status
async def status(update, context):
    # новая функция для команды /status, чтобы пользователь мог узнать, сколько запросов осталось
    # получение ID пользователя
    user_id = update.message.from_user.id

    # проверяем наличие пользователя в базе
    if user_id in context.bot_data:
        remaining_requests = context.bot_data[user_id]
    else:
        remaining_requests = 3  # если пользователь еще не делал запросов

    # отправляем сообщение пользователю
    await update.message.reply_text(f"Осталось запросов: {remaining_requests}")

# функция-обработчик текстовых сообщений
async def text(update, context):
    # создание счётчика у пользователя
    user_id = update.message.from_user.id
    if user_id not in context.bot_data:
        context.bot_data[user_id] = 3

    # обращение к API база Simble
    if context.bot_data[user_id] > 0:
        param = {
            'text': update.message.text
        }    
        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:8000/api/get_answer_async', json=param) as response:
                # получение ответа от API
                answer = await response.json()
                # уменьшаем количество оставшихся запросов
                context.bot_data[user_id] -= 1
                # добавление информации о количестве оставшихся запросов в сообщение пользователю
                # answer['message'] += f'\n-\nУ вас осталось обращений: {context.bot_data[user_id]}'
                await update.message.reply_text(answer['message'])
    else:
        await update.message.reply_text('Ваш лимит 3 обращения в минуту. На текущий момент исчерпан!')

# Функция срабатывает через заданный интервал времени
async def task(context: ContextTypes.DEFAULT_TYPE):
    # сброс счетчиков у всех пользователей
    if context.bot_data:
        for key in context.bot_data:
            context.bot_data[key] = 3
        print('Запросы пользователей обновлены')

# функция "Запуск бота"
def main():
    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

    # запуск планировщика
    schedule = application.job_queue
    if not schedule:
        schedule = application.job_queue = application.create_job_queue()  # Создаем `JobQueue`, если не создан

    interval = 60  # интервал 60 секунд = 1 минута
    schedule.run_repeating(task, interval=interval) 

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler('start', start))

    # добавляем обработчик команды /status
    application.add_handler(CommandHandler('status', status))  # добавлен новый обработчик для команды /status

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    print('Бот запущен...')    
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":      # если модуль запущен как основная программа
    # запуск бота
    main()
