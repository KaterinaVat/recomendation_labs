import aiohttp
import json
import re
from models.utils import build_prompt


class GPTClient:
    def __init__(self, model: str, token: str, url: str ) -> None:
        """
        Инициализация гпт модели.

        На вход:
            url str: Базовый URL API сервера
            model str: Название модели для использования
        """
        self.model = model
        self.token = token
        self.url = url


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

        prompt = build_prompt(task, mode, language)
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt 
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, json=payload) as resp:
                try:
                    response_json = await resp.json()
                except json.JSONDecodeError:
                    text = await resp.text()
                    raise RuntimeError(f"json некорректный: {text}")
                
                try:
                    response_text = response_json["choices"][0]["message"]["content"]
                    clean_text = re.sub(r'<[^>]+>', '', response_text)
                    return clean_text
                
                except (KeyError, IndexError):
                    return f"Неожиданный ответ модели: {resp.text}"



    
    