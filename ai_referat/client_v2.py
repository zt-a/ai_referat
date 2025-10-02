from g4f import Provider
from g4f.client import Client, AsyncClient
import asyncio
import time


class AIClientBase:
    def __init__(self, base_url="https://openrouter.ai/api/v1", api_key="", model="deepseek/deepseek-chat-v3.1:free"):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.content = ""
        self.rules = ""
        self.history = [{"role": "user", "content": f"{self.content}\n{self.rules}"}]

        # Используем конкретный провайдер OpenRouter
        self.provider = Provider.OpenRouter

    def clear_content(self):
        self.content = ""
        return self.get_content()

    def get_content(self):
        return self.content

    def set_content(self, content):
        self.content = content
        return self.get_content()

    def add_content(self, content):
        self.content += content
        return self.get_content()

    def add_rules(self, rules):
        self.rules += rules
        return self.get_rules()

    def set_rules(self, rules):
        self.rules = rules
        return self.get_rules()

    def get_rules(self):
        return self.rules

    def update_history(self):
        self.history = [{"role": "user", "content": f"{self.content}\n{self.rules}"}]
        return self.get_history()

    def get_history(self):
        return self.history

    def _prepare(self, content, rules):
        self.set_content(content)
        self.set_rules(rules)
        self.update_history()


# ===================== СИНХРОННЫЙ КЛАСС =====================
class AIClientSync(AIClientBase):
    def __init__(self, base_url="https://openrouter.ai/api/v1", api_key="", model="deepseek/deepseek-chat-v3.1:free"):
        super().__init__(base_url=base_url, api_key=api_key, model=model)
        self.client = Client(provider=self.provider, api_key=self.api_key, base_url=self.base_url)

    def get_response_sync(self, content: str, rules: str, min_length: int = 200,
                          max_retries: int = 10, delay: float = 2.0) -> str:
        self._prepare(content, rules)
        last_text = ""

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.history,
                    web_search=False
                )
                text = response.choices[0].message.content
                last_text = text
                if len(text) >= min_length:
                    return text
            except Exception as e:
                print(f"Ошибка: {e}")

            time.sleep(delay)

        return "LIMIT: " + last_text


# ===================== АСИНХРОННЫЙ КЛАСС =====================
class AIClientAsync(AIClientBase):
    def __init__(self, base_url="https://openrouter.ai/api/v1", api_key="", model="deepseek/deepseek-chat-v3.1:free"):
        super().__init__(base_url=base_url, api_key=api_key, model=model)
        self.client = AsyncClient(provider=self.provider, api_key=self.api_key, base_url=self.base_url)

    async def get_response_async(self, content: str, rules: str, min_length: int = 200,
                                 max_retries: int = 10, delay: float = 2.0) -> str:
        self._prepare(content, rules)
        last_text = ""

        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.history,
                    web_search=False
                )
                text = response.choices[0].message.content
                last_text = text
                if len(text) >= min_length:
                    return text
            except Exception as e:
                print(f"Ошибка: {e}")

            await asyncio.sleep(delay)

        return "LIMIT: " + last_text
