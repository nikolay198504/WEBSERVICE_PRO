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
    # получаем язык пользователя
    user_language = update.effective_user.language_code

    # задаем текст сообщения в зависимости от языка
    if user_language == "ru":
        message = "Фотография сохранена!"
    else:
        message = "Photo saved!"

    # получаем изображение из апдейта (с максимальным качеством)
    file = await update.message.photo[-1].get_file()

    # путь для сохранения изображения
    save_path = f'photos/{file.file_id}.jpg'

    # сохраняем изображение на диск
    await file.download_to_drive(save_path)

    # отправляем сообщение пользователю
    await update.message.reply_text(message)

# функция-обработчик голосовых сообщений
# функция-обработчик голосовых сообщений
async def voice(update: Update, _):
    # получаем язык пользователя
    user_language = update.effective_user.language_code

    # задаем подписи в зависимости от языка
    if user_language == "ru":
        caption = "Голосовое сообщение получено!"
    else:
        caption = "We've received a voice message from you!"

    # отправляем картинку с подписью
    await update.message.reply_photo(
        'media/voice_response.png',  # путь к изображению
        caption=caption  # подпись на выбранном языке
    )

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