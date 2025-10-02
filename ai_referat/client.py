import asyncio
import time
from typing import Optional
import openai


# ------------------ Базовый класс ------------------
class AIClientBase:
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.content = ""
        self.rules = ""
        self.history = [{"role": "user", "content": f"{self.content}\n{self.rules}"}]

        if self.api_key:
            openai.api_key = self.api_key
        if self.base_url:
            openai.api_base = self.base_url  # можно указать OpenAI Enterprise / прокси / OpenRouter

    # ---------------- Методы состояния ----------------
    def clear_content(self):
        self.content = ""
        return self.get_content()

    def get_content(self):
        return self.content

    def set_content(self, content: str):
        self.content = content
        return self.get_content()

    def add_content(self, content: str):
        self.content += content
        return self.get_content()

    def set_rules(self, rules: str):
        self.rules = rules
        return self.rules

    def add_rules(self, rules: str):
        self.rules += rules
        return self.rules

    def update_history(self):
        self.history = [{"role": "user", "content": f"{self.content}\n{self.rules}"}]
        return self.history

    def _prepare(self, content: str, rules: str):
        self.set_content(content)
        self.set_rules(rules)
        self.update_history()


# ===================== СИНХРОННЫЙ КЛАСС =====================
class AIClientSync(AIClientBase):
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(model=model, api_key=api_key, base_url=base_url)

    def get_response_sync(
        self, content: str, rules: str, min_length: int = 500,
        max_retries: int = 5, delay: float = 2.0
    ) -> str:
        self._prepare(content, rules)
        last_text = ""

        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.history
                )
                text = response.choices[0].message["content"]
                last_text = text
                if len(text) >= min_length:
                    return text
            except Exception as e:
                print(f"Ошибка: {e}")

            time.sleep(delay)

        return "LIMIT: " + last_text


# ===================== АСИНХРОННЫЙ КЛАСС =====================
class AIClientAsync(AIClientBase):
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(model=model, api_key=api_key, base_url=base_url)

    async def get_response_async(
        self, content: str, rules: str, min_length: int = 500,
        max_retries: int = 5, delay: float = 2.0
    ) -> str:
        self._prepare(content, rules)
        last_text = ""

        for attempt in range(max_retries):
            try:
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=self.history
                )
                text = response.choices[0].message["content"]
                last_text = text
                if len(text) >= min_length:
                    return text
            except Exception as e:
                print(f"Ошибка: {e}")

            await asyncio.sleep(delay)

        return "LIMIT: " + last_text
