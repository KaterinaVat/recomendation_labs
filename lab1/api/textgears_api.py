from typing import Dict, Any

import requests
from requests import Response

from api.base_api import BaseApi


class TextGrearsApi(BaseApi):

    def __init__(self, api_key: str, base_url: str) -> None:
        super().__init__(api_key, base_url)

    def check_spelling(self, text: str, language: str = "") -> Dict[str, Any]:
        """
        Отправляет запрос к api для проверки текста 
        на наличие ошибок через TextGears API.

        На вход:
            text: входной текст
            language: код языка (необязательно)

        Возвращает:
            json с ответом API и информацией об ошибках
        """
        data: Dict[str, str] = {
            "text": text,
        }
        if language:
            data["language"] = language
        try:
            response: Response = requests.post(
                url=f"https://{self.base_url}/spelling",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-RapidAPI-Host": self.base_url,
                    "X-RapidAPI-Key": self.api_key,
                },
                data=data,
            )
            print(data)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"TextGears API request failed: {str(e)}"
            ) from e
        if response.status_code != 200:
            raise RuntimeError(
                f"TextGears API error {response.status_code}: {response.text}"
            )
        return response.json()

    def parse_json(self, file: Dict[str, any]) -> list[str]:
        """
        Парсит JSON ответ API проверки орфографии и форматирует результат

        На взод:
            file: Словарь с ответом от API
        
        Возвращает:
            Строка со списком ошибок
        
        """
        print(file)
        if 'response' not in file:
            raise ValueError("Wrong json structure")
        response: Dict[str, any] = file['response']
        if 'errors' not in response:
            return []
        errors: list[Dict[str, any]] = response['errors']
        result: list[str] = []
        for e in errors:
            wrong_word: str = e.get('bad', 'Unknown')
            result.append(wrong_word)
        return result
