import aiohttp
import json
import re
from models.utils import build_prompt


class LlamaModelClient:
    """
    Клиент для работы с Llama моделью через API.
    
    """

    def __init__(self, url: str, model: str) -> None:
        """
        Инициализация Llama модели.

        На вход:
            url str: Базовый URL API сервера
            model str: Название модели для использования
        """
        self.url = url
        self.model = model

    async def get_model_response(self, task: str, mode: str, language: str) -> str:
        """
        Отправляет промт модели и возвращает её ответ.

        Формирует промт на основе задачи, режима и языка, отправляет запрос
        к API модели и обрабатывает ответ, очищая его от HTML-тегов.

        На вход:
            task str: Текст задачи для решения
            mode str: Режим работы ('e' - обучение, 'c' - проверка)
            language str: Язык программирования для решения

        На выход:
            str: ответ от модели 
        """
        prompt = build_prompt(task, language, mode)
        print(prompt)

        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        url = f"{self.url}/api/generate"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                try:
                    response_json = await resp.json()
                except json.JSONDecodeError:
                    text = await resp.text()
                    raise RuntimeError(f"json некорректный: {text}")

                try:
                    response_text = response_json['response']
                    clean_response = re.sub(r'<[^>]+>', '', response_text)
                    return clean_response
                
                except (KeyError, IndexError):
                    return f"Неожиданный ответ модели: {resp.text}"