class EssayPrompts:
    def __init__(
        self,
        topic: str,
        language: str,
        max_chapters: int = 3,
        max_subchapters: int = 2,
        chars_per_page: int = 1800,
        min_pages: int = 1,
        max_pages: int = 2,
        rules: str = ""
    ):
        self.topic = topic
        self.language = language
        self.max_chapters = max_chapters
        self.max_subchapters = max_subchapters
        self.chars_per_page = chars_per_page
        self.min_pages = min_pages
        self.max_pages = max_pages
        self.rules = rules


    def plan(self) -> str:
        return f"""
Ты — помощник для написания рефератов.

Составь план реферата на тему "{self.topic}" на {self.language}.
Формат:
- Первая строка: "Введение"
- Далее до {self.max_chapters} глав: "Глава 1: Название главы"
- У каждой главы до {self.max_subchapters} подглав: "1.1: Название подглавы"
- Последние две строки: "Заключение" и "Использованные литературы"

{self.rules}

Ответ — только сам план в указанном формате, без комментариев и пояснений.
"""

    def intro(self) -> str:
        return f"""
Напиши раздел "Введение" для реферата на тему "{self.topic}" на {self.language}.

{self.rules}

Объем текста: примерно {self.min_pages}–{self.max_pages} страниц
(≈ {self.min_pages * self.chars_per_page}–{self.max_pages * self.chars_per_page} символов с пробелами).
"""

    def chapter(self, chapter_title: str) -> str:
        return f"""
Напиши раздел по теме "{chapter_title}" для реферата на тему "{self.topic}" на {self.language}.

{self.rules}

Объем текста: примерно {self.min_pages}–{self.max_pages} страниц
(≈ {self.min_pages * self.chars_per_page}–{self.max_pages * self.chars_per_page} символов с пробелами).
"""

    def subchapter(self, chapter_title: str, subchapter_title: str) -> str:
        return f"""
Напиши текст для раздела "{chapter_title}" на подтему "{subchapter_title}"
для реферата на тему "{self.topic}" на {self.language}.

{self.rules}

Объем текста: примерно {self.min_pages}–{self.max_pages} страниц
(≈ {self.min_pages * self.chars_per_page}–{self.max_pages * self.chars_per_page} символов с пробелами).
"""

    def conclusion(self) -> str:
        return f"""
Составь заключение для реферата на тему "{self.topic}" на {self.language}.

{self.rules}

Объем текста: примерно {self.min_pages}–{self.max_pages} страниц
(≈ {self.min_pages * self.chars_per_page}–{self.max_pages * self.chars_per_page} символов с пробелами).
"""

    def references(self) -> str:
        return f"""
Составь раздел "Использованные литературы" для реферата на тему "{self.topic}" на {self.language}.

{self.rules}

Выведи список из 5–8 источников в академическом стиле:
1. Автор. Название. Год.
2. ...

Объем текста: примерно {self.min_pages}–{self.max_pages} страниц
(≈ {self.min_pages * self.chars_per_page}–{self.max_pages * self.chars_per_page} символов с пробелами).
"""



"""examples
prompts = EssayPrompts(
    topic="История HTML",
    language="русском языке",
    max_chapters=3,
    max_subchapters=2,
    chars_per_page=1800,
    min_pages=1,
    max_pages=2,
    rules="Пиши научным стилем."
)

print(prompts.plan())         # Получить план
print(prompts.intro())        # Введение
print(prompts.chapter("Глава 1: Истоки HTML"))
print(prompts.subchapter("Глава 1", "Создание первых спецификаций"))
print(prompts.conclusion())   # Заключение
print(prompts.references())   # Литература


"""