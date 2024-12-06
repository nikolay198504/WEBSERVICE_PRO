from dotenv import load_dotenv
import os
import openai
import asyncio  # Импортируем asyncio для асинхронных операций
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # Используем langchain_openai
from langchain_openai import ChatOpenAI  # Используем ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Загрузка переменных окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Chunk:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Ключ API OpenAI не найден. Проверьте переменные окружения.")
        self.base_load()

    def base_load(self):
        # Чтение базы знаний
        with open(os.path.join(os.path.dirname(__file__), 'base', 'Rules.txt'), 'r', encoding='utf-8') as file:
            document = file.read()


        # Создание чанков
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        source_chunks = splitter.split_text(document)
        docs = [Document(page_content=chunk) for chunk in source_chunks]

        # Создание векторной базы
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
        self.db = FAISS.from_documents(docs, embeddings)

        # Формирование инструкции
        self.system = '''
            Ты - нейро-консультант компании АльфаСтрахование.
            Отвечай на вопросы клиентов на основе предоставленных Правил страхования.
            Не придумывай информацию, отвечай строго согласно документу.
            Не упоминай документ с информацией в ответах.
        '''

    async def get_answer(self, query: str):
        # Поиск в базе
        docs = self.db.similarity_search(query, k=4)
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

        # Получение ответа (асинхронный вызов)
        response = await chat.agenerate([messages])

        # Возвращаем ответ ассистента
        return response.generations[0][0].text

# Запуск асинхронного метода get_answer
if __name__ == "__main__":
    chunk = Chunk()
    query = 'Какие исключения предусмотрены в страховом договоре?'

    # Запускаем асинхронную функцию
    result = asyncio.run(chunk.get_answer(query))
    print(result)
