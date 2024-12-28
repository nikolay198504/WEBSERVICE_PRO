from dotenv import load_dotenv
import os
import openai
import asyncio
import aiofiles
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import aiohttp
import time
import json
from fastapi import HTTPException

# Загрузка переменных окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Chunk:
    def __init__(self):
        # Установка API-ключа
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Ключ API OpenAI не найден. Проверьте переменные окружения.")
        # Инициализация асинхронной загрузки базы данных
        loop = asyncio.get_event_loop()
        loop.create_task(self.base_load())

    async def base_load(self):
        # Чтение базы знаний
        rules_path = os.path.join(os.path.dirname(__file__), 'base', 'Rules.txt')
        if not os.path.exists(rules_path):
            raise FileNotFoundError(f"Файл {rules_path} не найден.")
        
        async with aiofiles.open(rules_path, 'r', encoding='utf-8') as file:
            document = await file.read()

        # Разбиение текста на чанки
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        source_chunks = splitter.split_text(document)
        docs = [Document(page_content=chunk) for chunk in source_chunks]

        # Создание векторной базы
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
        self.db = FAISS.from_documents(docs, embeddings)

        # Формирование системного сообщения
        self.system = '''
            Ты - нейро-консультант компании АльфаСтрахование.
            Отвечай на вопросы клиентов на основе предоставленных Правил страхования.
            Не придумывай информацию, отвечай строго согласно документу.
            Не упоминай документ с информацией в ответах.
        '''

    async def get_answer(self, query: str):
        # Поиск в базе
        docs = self.db.similarity_search(query, k=4)
        if not docs:
            return "Извините, я не смог найти информацию для ответа на ваш вопрос."

        message_content = '\n'.join([doc.page_content for doc in docs])

        # Формирование промпта
        user = f'''
            Ответь на вопрос клиента. Не упоминай документ с информацией в ответе.
            Контекст для ответа: {message_content}

            Вопрос клиента:
            {query}
        '''

        # Создание сообщений
        messages = [
            SystemMessage(content=self.system),
            HumanMessage(content=user)
        ]

        # Инициализация ChatOpenAI
        chat = ChatOpenAI(model_name='gpt-4', temperature=0, openai_api_key=openai.api_key)

        try:
            # Получение ответа
            response = await chat.agenerate([messages])
            return response.generations[0][0].text.strip()
        except Exception as e:
            return f"Произошла ошибка: {e}"

    async def get_answer_async(self, query: str):
        # Асинхронный вызов
        return await self.get_answer(query)

    # МЕТОД: распознавание изображения
    #   param = {
    #       image  - картинка в формате base64
    #       text   - текст для роли 'user'
    #   }    
    # Возвращает текст
    async def ocr_image(self, param: dict):

        # заголовок
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.environ.get("OPENAI_API_KEY")}'
        }
        
        # промпт
        payload = {
            'model': 'gpt-4o-mini',
            'messages': [
                {
                    'role': 'user', 
                    'content': [
                        { 'type': 'text', 'text': param['text'] },
                        {
                            'type': 'image_url', 'image_url': {
                                'url': f'data:image/jpeg;base64, {param["image"]}'
                            }
                        }
                    ]
                }
            ]
        }

        # выполнение запроса
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers = headers,
                json = payload
            ) as response:
                try:
                    # получение результата
                    result = await response.json()
                    
                    # обработка заголовков ограничения скорости
                    rate_limit_headers = {
                        'limit_requests': int(response.headers.get('x-ratelimit-limit-requests')),
                        'limit_tokens': int(response.headers.get('x-ratelimit-limit-tokens')),
                        'remaining_requests': int(response.headers.get('x-ratelimit-remaining-requests')),
                        'remaining_tokens': int(response.headers.get('x-ratelimit-remaining-tokens')),
                        'reset_tokens': int(response.headers.get('x-ratelimit-reset-tokens').replace('ms', '')),
                        'reset_requests': int(float(response.headers.get('x-ratelimit-reset-requests').replace('s', '')) * 1000)
                    }
                    
                    # проверка оставшихся запросов и токенов
                    if rate_limit_headers['remaining_requests'] and rate_limit_headers['remaining_requests'] <= 0:
                        reset_time = rate_limit_headers['reset_requests']
                        time.sleep(reset_time)  # Задержка до сброса лимита

                    if rate_limit_headers['remaining_tokens'] and rate_limit_headers['remaining_tokens'] <= 0:
                        reset_time = rate_limit_headers['reset_tokens']
                        time.sleep(reset_time)  # Задержка до сброса лимита

                    # проверка на наличие ошибок в ответе
                    if 'error' in result:
                        message = result['error']['message']
                        print(message)
                        raise HTTPException(status_code = 400, detail = message)

                    # получение ответа
                    if 'choices' in result:                                           
                        # ответ в формате текста
                        return result['choices'][0]['message']['content']
                    else:
                        message = 'Response does not contain "choices"'
                        print(message)
                        raise HTTPException(status_code = 500, detail = message)

                except aiohttp.ContentTypeError as e:
                    message = f'ContentTypeError: {str(e)}'
                    print(message)
                    raise HTTPException(status_code = 500, detail = message)
                except json.JSONDecodeError as e:
                    message = f'JSONDecodeError: {str(e)}'
                    print(message)
                    raise HTTPException(status_code = 500, detail = message)

# Запуск программы
if __name__ == "__main__":
    chunk = Chunk()
    query = 'Какие исключения предусмотрены в страховом договоре?'

    try:
        # Запускаем асинхронную функцию
        result = asyncio.run(chunk.get_answer(query))
        print(result)
    except Exception as e:
        print(f"Ошибка: {e}")
