# Пример работы с параметром update
#Цель кода
#Этот пример демонстрирует:

#Как обрабатывать сообщения от пользователей.
#Как отправлять и редактировать сообщения.
#Как работать с объектом Update, чтобы получить данные о сообщении, пользователе и контексте.

# импорт библиотек
from telegram.ext import Application, MessageHandler, filters
from telegram import Update
from pprint import pprint
from dotenv import load_dotenv
import time
import os

# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# функция-обработчик текстовых сообщений
async def text(update: Update, context):
    
    # выведем в консоль содержимое update
    print(update)
    print()
    pprint(update.to_dict())
    print()

    # update.message - новое входящее сообщение любого типа - текст, фотография, наклейка и т. д.
    print(update.message.text)
    print(update.message.message_id)
    print(update.message.date)
    print(update.message.from_user.first_name)
    print(update.message.from_user.id)
    print()

    # update.callback_query - новый входящий запрос обратного вызова (используется при нажатии кнопок)
    print(update.callback_query)
    print()

    # update.update_id - уникальный id входящего сообщения
    print(update.update_id)

    # выводим первоначальное сообщение
    reply_message = await update.message.reply_text('Ваш запрос обрабатывается...')
    
    # задержка 3 секунды
    time.sleep(3)
    
    # пример редактирования первоначального сообщения
    await reply_message.edit_text('Обработка завершена')
    

# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

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