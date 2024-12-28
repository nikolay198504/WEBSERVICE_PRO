# Пример распознавания изображения

# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update                    
from dotenv import load_dotenv
import os
import requests
import aiohttp
import base64

# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# функция-обработчик команды /start
async def start(update, context):

    # сообщение пользователю
    await update.message.reply_text("Привет! Это пример распознавания изображения")

# функция-обработчик сообщений с изображениями
async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # первоначальное сообщение
    first_message = await update.message.reply_text('Изображение в обработке...')  

    # преобразование изображение в Base64
    image_base64 = await photo_to_base64(update)
    if image_base64 == '':
        self.setUserProp(update.message.from_user.id, 'button_index', -1)
        await first_message.edit_text('Ошибка при скачивании изображения')
        return

    # подготовка данных
    data = {
        'user_id'   : update.message.from_user.id,
        'image'     : image_base64,
        'text'      : update.message.caption if update.message.caption else 'Распознай текст на изображении'
    }
        
    # обращение к RestAPI
    try:
        # отправка данных на указанный URL
        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:8000/api/image_ocr', json = data) as response:

                # обработка ответа от API
                answer = await response.json()
                response_message = answer['message']

    except Exception as e:

        # обработка ошибок
        response_message = f'Произошла ошибка: {e}'

    # ответ пользователю
    await first_message.edit_text(response_message, parse_mode = 'Markdown')

# Функция преобразования файла в Base64
# Возвращает строку Base64 или пустую строку в случае неудачи
async def photo_to_base64(update: Update):

    # получение файла изображения из сообщения
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Скачивание файла и преобразование в Base64
    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as response:
            if response.status == 200:
                img_bytes = await response.read()
                
                # Преобразование изображения в base64
                return base64.b64encode(img_bytes).decode('utf-8')
            else:
                return ''            

# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик изображений
    application.add_handler(MessageHandler(filters.PHOTO, image))    

    # запускаем бота (нажать Ctrl-C для остановки бота)
    print('Бот запущен...')    
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":      # если модуль запущен как основная программа

    # запуск бота
    main()