from g4f import Provider
from g4f.client import Client, AsyncClient
import asyncio
import time


class AIClientBase:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.content = ""
        self.rules = ""
        self.history = [
            {"role": "user", "content": f"{self.content}\n{self.rules}"}
        ]
        # автоматически берём все доступные провайдеры
        self.providers = [
            p for p in Provider.__dict__.values() if isinstance(p, type)
        ]

    # -------------------- Методы состояния --------------------
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
        self.history = [
            {"role": "user", "content": f"{self.content}\n{self.rules}"}
        ]
        return self.get_history()

    def get_history(self):
        return self.history

    def _prepare(self, content, rules):
        self.set_content(content)
        self.set_rules(rules)
        self.update_history()


# ===================== СИНХРОННЫЙ КЛАСС =====================
class AIClientSync(AIClientBase):
    def __init__(self, model="gpt-4o-mini"):
        super().__init__(model=model)
        self.client = Client()

    def get_response_sync(
        self, content: str, rules: str, min_length: int = 200,
        max_retries: int = 30, delay: float = 2.0
    ) -> str:
        self._prepare(content, rules)
        last_text = ""

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
                    last_text = text
                    if len(text) >= min_length and "Ratelimit Exceeded" not in text:
                        return text
                except Exception as e:
                    if "Ratelimit" not in str(e):
                        print(f"Ошибка у {provider.__name__}: {e}")

            time.sleep(delay)

        return "LIMIT: " + last_text


# ===================== АСИНХРОННЫЙ КЛАСС =====================
class AIClientAsync(AIClientBase):
    def __init__(self, model="gpt-4o-mini"):
        super().__init__(model=model)
        self.client = AsyncClient()

    async def get_response_async(
        self, content: str, rules: str, min_length: int = 200,
        max_retries: int = 30, delay: float = 2.0
    ) -> str:
        self._prepare(content, rules)
        last_text = ""

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
                    last_text = text
                    if len(text) >= min_length and "Ratelimit Exceeded" not in text:
                        return text
                except Exception as e:
                    if "Ratelimit" not in str(e):
                        print(f"Ошибка у {provider.__name__}: {e}")

            await asyncio.sleep(delay)

        return "LIMIT: " + last_text
