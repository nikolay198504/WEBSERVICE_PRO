# Пример работы с параметром context
# в основном для закрепления сообщений
# импорт модулей
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
import time
import os

# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# функция-обработчик текстовых сообщений
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # отправка сообщения
    self_message = await context.bot.send_message(chat_id=update.message.from_user.id, text='Ваш запрос обрабатывается...')

    # пауза
    time.sleep(3)
   
    # сохраняем пользовательские данные
    if 'counter' not in context.user_data: context.user_data['counter'] = 0
    context.user_data['counter'] += 1
    
    # редактирование сообщения
    await context.bot.edit_message_text(
        chat_id = update.message.from_user.id,
        message_id = self_message.message_id,
        text = f"Сообщение {context.user_data['counter']} обработано!"
    )
    
    # закрепляем сообщение в чате
    await context.bot.pin_chat_message(chat_id=update.message.chat_id, message_id=update.message.message_id)    
    
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