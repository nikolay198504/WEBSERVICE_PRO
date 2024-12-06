from fastapi import FastAPI, Request
from pydantic import BaseModel  
from api.chunks import Chunk  

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}

# Функция, которая обрабатывает запрос по пути "/about"
@app.get('/about')
def about():
    return {'message': 'Страница с описанием проекта'}

# Функция-обработчик с параметрами пути
@app.get('/users/{id}')
def users(id: int):
    return {'Вы ввели user_id': id}

# POST-запрос на путь "/test"
@app.post('/test')
def post_test():
    return {'Hello'}

# Класс с типами данных параметров
class Item(BaseModel):
    name: str
    description: str
    old: int

# Функция-обработчик POST-запроса с параметрами
@app.post('/users')
def post_users(item: Item):
    return {'answer': f'Пользователь: {item.name} - {item.description}, возраст: {item.old} лет'}

# Класс с типами данных для метода api/get_answer
class ModelAnswer(BaseModel):
    text: str

chunk = Chunk()

# глобальная переменная для подсчёта запросов к /api/get_answer
get_answer_request_count = 0

@app.post('/api/get_answer')
async def get_answer(question: ModelAnswer):
    global get_answer_request_count
    get_answer_request_count += 1  
    answer = await chunk.get_answer(query=question.text)
    return {'message': answer}

#  GET-метод для получения количества обращений к /api/get_answer
@app.get('/api/request_count')
def get_request_count():
    return {'total_get_answer_requests': get_answer_request_count}
