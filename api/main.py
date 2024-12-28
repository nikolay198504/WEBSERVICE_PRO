from fastapi import FastAPI  # Импортируем FastAPI для создания приложения
from pydantic import BaseModel  # Импортируем BaseModel для работы со структурами данных
from api.chunks import Chunk  # Импортируем модуль для взаимодействия с OpenAI (или другим API)
from fastapi.middleware.cors import CORSMiddleware  # Для настройки CORS (междоменного взаимодействия)
from fastapi.responses import JSONResponse  # Для отправки кастомных JSON-ответов

# Создаем объект FastAPI
app = FastAPI()

# Добавляем middleware для настройки CORS (междоменного взаимодействия)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых доменов
    allow_credentials=True,  # Разрешаем передачу cookie
    allow_methods=["*"],  # Разрешаем любые HTTP-методы
    allow_headers=["*"]  # Разрешаем любые заголовки
)

# Создаем объект для взаимодействия с OpenAI (или другой логикой)
chunk = Chunk()

# Определяем модель данных для пользователя
class Item(BaseModel):
    name: str  # Имя пользователя
    description: str  # Описание пользователя
    old: int  # Возраст пользователя

# Определяем модель данных для калькулятора
class ModelCalc(BaseModel):
    a: float  # Первое число
    b: float  # Второе число

# Определяем модель данных для распознавания изображения
class ModelOcr(BaseModel):
    image: str  # Путь или ссылка на изображение
    text: str  # Описание текста на изображении

# Определяем модель данных для обработки текстовых запросов
class ModelAnswer(BaseModel):
    text: str  # Вопрос или текст для обработки

# Определяем модель данных для взаимодействия с OpenAI
class ModelRequest(BaseModel):
    system: str = ''  # Системное сообщение для настройки модели
    user: str = ''  # Пользовательский ввод
    temperature: float = 0.5  # Температура для контроля генерации текста
    format: dict = None  # Форматирование ответа (необязательно)

# Главная страница
@app.get("/")
def root():
    return {"message": "Hello FastAPI"}  # Возвращаем простой JSON-ответ

# Страница "О проекте"
@app.get("/about")
def about():
    return {"message": "Страница с описанием проекта"}  # Текстовое описание

# Получение информации о пользователе по ID
@app.get("/users/{id}")
def users(id: int):
    return {"Вы ввели user_id": id}  # Возвращаем ID пользователя

# Обработка POST-запроса с информацией о пользователе
@app.post('/users')
def post_users(item: Item):
    return {'answer': f'Пользователь {item.name} - {item.description}, возраст {item.old} лет'}

# Обработка POST-запроса для калькуляции
@app.post('/add')
def post_add(item: ModelCalc):
    result = item.a + item.b  # Складываем два числа
    return {'result': result}  # Возвращаем результат сложения

# Асинхронная обработка текста через OpenAI
@app.post('/api/get_answer_async')
async def get_answer_async(question: ModelAnswer):
    answer = await chunk.get_answer_async(query=question.text)  # Асинхронный вызов API
    return {'message': answer}  # Возвращаем результат

# Обработка распознавания изображений
@app.post('/api/image_ocr')
async def post_ocr(question: ModelOcr):
    answer = await chunk.ocr_image({
        'image': question.image,  # Передаем изображение
        'text': question.text  # Передаем текст для сопоставления
    })
    return {'message': answer}  # Возвращаем результат

# Асинхронное обращение к OpenAI с дополнительными параметрами
@app.post('/api/request')
async def post_request(question: ModelRequest):
    answer = await chunk.request(
        system=question.system,  # Передаем системное сообщение
        user=question.user,  # Передаем пользовательский запрос
        temp=question.temperature,  # Контролируем температуру генерации текста
        format=question.format  # Указываем формат ответа (если есть)
    )
    return {'message': answer}  # Возвращаем результат
