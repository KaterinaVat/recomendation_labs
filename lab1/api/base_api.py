from abc import ABC, abstractmethod

class BaseApi(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key: str = api_key
        self.base_url: str = base_url

    @abstractmethod
    def check_spelling(self, text: str) -> dict:
        """
        Обращается к API для получения сведений о наличии ошибок в тексте
        
        Аргумент:
            text: проверяемый текст

        Возвращает:
            dict: ответ API с информацией об ошибках
        """
        pass



