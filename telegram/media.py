# Пример работы с медиа-файлами

# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
import os

# подгружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')


# функция-обработчик команды /start
async def start(update: Update, _):

    # возвращаем пользователю картинку с подписью
    await update.message.reply_photo('media/start.jpg', caption = 'Вот картинка')

# функция-обработчик сообщений с изображениями
async def image(update: Update, _):
    
    # сообщение от бота
    await update.message.reply_text('Изображение сохранено в файл media/save.jpg')

    # получаем изображение из апдейта
    quality = -1 # качество -1 - высокое, 0 - низкое
    file = await update.message.photo[quality].get_file()
    
    # сохраняем изображение на диск
    await file.download_to_drive('media/save.jpg')

# функция-обработчик голосовых сообщений
async def voice(update: Update, _):
    
    # сообщение от бота
    await update.message.reply_text('Голосовое сообщение сохранено в файл media/save.mp3')

    # получаем файл голосового сообщения из апдейта
    new_file = await update.message.voice.get_file()

    # сохраняем голосовое сообщение на диск
    await new_file.download_to_drive('media/voice.mp3')

# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # добавляем обработчик сообщений с фотографиями
    application.add_handler(MessageHandler(filters.PHOTO, image))

    # добавляем обработчик голосовых сообщений
    application.add_handler(MessageHandler(filters.VOICE, voice))

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":      # если модуль запущен как основная программа

    # запуск бота
    main()