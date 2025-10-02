# client_g4f.py
import asyncio
import time

from g4f import Provider
from g4f.client import AsyncClient, Client


class AIClientBase:
    def __init__(self, model="gpt-4o-mini", api_key=None, base_url=None, free=True):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.free = free
        self.content = ""
        self.rules = ""
        self.history = [{"role": "user", "content": f"{self.content}\n{self.rules}"}]

        if self.free:
            # Берём все доступные провайдеры автоматически
            self.providers = [
                p for p in Provider.__dict__.values() if isinstance(p, type)
            ]
        else:
            # Если платный провайдер (например OpenRouter), можно передавать конкретно
            self.providers = []

    def _prepare(self, content, rules):
        self.content = content
        self.rules = rules
        self.history = [{"role": "user", "content": f"{self.content}\n{self.rules}"}]

# ===================== СИНХРОННЫЙ =====================
class AIClientSync(AIClientBase):
    def __init__(self, model="gpt-4o-mini", api_key=None, base_url=None, free=True):
        super().__init__(model=model, api_key=api_key, base_url=base_url, free=free)
        self.client = Client()

    def get_response_sync(self, content, rules, min_length=500, max_retries=10, delay=2.0):
        self._prepare(content, rules)
        for attempt in range(max_retries):
            for provider in self.providers:
                self.client.provider = provider
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.history,
                        web_search=False
                    )
                    text = response.choices[0].message.content
                    print(text)
                    # Если текст подходит, сразу возвращаем
                    if len(text) >= min_length:
                        return text
                except Exception as e:
                    if "Ratelimit" not in str(e):
                        print(f"Ошибка у {provider.__name__}: {e}")
            # Ждём перед следующей попыткой
            time.sleep(delay)
        # Если все попытки и провайдеры не дали результат
        return "LIMIT: текст не получен или все провайдеры перегружены"


# ===================== АСИНХРОННЫЙ =====================
class AIClientAsync(AIClientBase):
    def __init__(self, model="gpt-4o-mini", api_key=None, base_url=None, free=True):
        super().__init__(model=model, api_key=api_key, base_url=base_url, free=free)
        self.client = AsyncClient()

    async def get_response_async(self, content, rules, min_length=500, max_retries=10, delay=2.0):
        self._prepare(content, rules)
        for attempt in range(max_retries):
            for provider in self.providers:
                self.client.provider = provider
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=self.history,
                        web_search=False
                    )
                    text = response.choices[0].message.content
                    if len(text) >= min_length:
                        print("_"*40)
                        print(self.history)      
                        print(":"*20)                  
                        print(text)
                        print("_"*40)
                        
                        return text  # сразу возвращаем текст
                except Exception as e:
                    if "Ratelimit" not in str(e):
                        print(f"Ошибка у {provider.__name__}: {e}")
            await asyncio.sleep(delay)
        return "LIMIT: текст не получен или все провайдеры перегружены"

