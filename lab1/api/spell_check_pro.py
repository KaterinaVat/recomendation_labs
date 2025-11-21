from typing import Dict, Any

import requests
from requests import Response

from api.base_api import BaseApi


class SpellCheckProApi(BaseApi):
    
    def __init__(self, api_key: str, base_url: str) -> None:
        super().__init__(api_key, base_url)

    def check_spelling(self, text: str, language: str = "") -> Dict[str, Any]:
        """
        Отправляет запрос к api для проверки текста 
        на наличие ошибок через SpellCheckPro API.

        На вход:
            text: входной текст
            language: код языка (необязательно)

        Вызвращает:
            json с ответом API и информацией об ошибках
        """
        data: Dict[str, str] = {
            "text": text,
        }
        if language:
            data["lang_code"] = language
        try:
            response: Response = requests.post(
                url=f"https://{self.base_url}/check_spelling",
                headers={
                    "Content-Type": "application/json",
                    "X-RapidAPI-Host": self.base_url,
                    "X-RapidAPI-Key": self.api_key,
                },
                json=data,
            )
            print(data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"SpellCheckPro API request failed: {str(e)}"
            ) from e
        if response.status_code != 200:
            raise RuntimeError(
                f"SpellCheckPro API error {response.status_code}: {response.text}"
            )
        
        return response.json()
    
    def parse_json(self, file: list[str]) -> list[str]:
        """
        Парсит JSON ответ API проверки орфографии и форматирует результат

        На взод:
            file: Словарь с ответом от API
        
        Возвращает:
            Строка со списком ошибок
        
        """
        print(file)
        if file.__len__ == 0:
            return []
        else:
            return file
            