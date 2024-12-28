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
