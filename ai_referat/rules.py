class RulesManager:
    def __init__(
        self,
        language: str = "русский",
        min_pages: int = 2,
        max_pages: int = 5,
        chars_per_page: int = 2000,
        description: str = None
    ):
        self.language = language
        self.min_pages = min_pages
        self.max_pages = max_pages
        self.chars_per_page = chars_per_page
        self._description = description

    def set_rules(
        self,
        language: str = None,
        min_pages: int = None,
        max_pages: int = None,
        chars_per_page: int = None,
        description: str = None
    ):
        """Обновить правила"""
        if language is not None:
            self.language = language
        if min_pages is not None:
            self.min_pages = min_pages
        if max_pages is not None:
            self.max_pages = max_pages
        if chars_per_page is not None:
            self.chars_per_page = chars_per_page
        if description is not None:
            self._description = description

    def get_rules(self) -> str:
        """Получить текущие правила"""
        if self._description:
            return self._description
        return f"""
1. Отвечай только на {self.language}.
2. Не добавляй комментариев, рекомендаций, советов, предупреждений и пояснений.
3. Следуй строго запрошенной структуре, не добавляй ничего лишнего.
4. Не используй маркированные списки (•, —, 1)) если они не предусмотрены структурой.
5. Для каждой главы пиши от {self.min_pages} до {self.max_pages} страниц текста
   (≈ {self.min_pages*self.chars_per_page}–{self.max_pages*self.chars_per_page} символов с пробелами)
6. Соблюдай переносы строк и формат заголовков из задания.
7. Используй научно-популярный стиль, избегай «воды» и повторов.
"""

    def add_rules(self, extra_description: str):
        """Добавить текст к текущим правилам"""
        if self._description:
            self._description += "\n" + extra_description
        else:
            self._description = extra_description
