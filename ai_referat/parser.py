import re
from typing import List, Optional
from ai_referat.models import EssayPlan, PlanChapter

def parse_plan(text: str) -> EssayPlan:
    """
    Парсит текст плана реферата в структуру EssayPlan.

    Ожидаемый формат:
    Введение
    Глава 1: Название
    1.1: Подглава
    1.2: Подглава
    Глава 2: Название
    Заключение
    Использованные литературы
    """
    chapter_pattern = re.compile(r"Глава \d+: [^\n]+")
    subsection_pattern = re.compile(r"\d+\.\d+: [^\n]+")

    chapters: List[PlanChapter] = []
    current_chapter: Optional[PlanChapter] = None

    lines: List[str] = [line.strip() for line in text.split("\n") if line.strip()]
    intro_title: str = "Введение"
    conclusion_title: str = "Заключение"
    references_title: str = "Использованные литературы"

    for line in lines:
        if line.startswith(intro_title) or line.startswith(conclusion_title) or line.startswith(references_title):
            continue

        if chapter_pattern.match(line):
            if current_chapter:
                chapters.append(current_chapter)
            current_chapter = PlanChapter(title=line, subchapters=[])
        elif subsection_pattern.match(line) and current_chapter:
            current_chapter.subchapters.append(line)

    if current_chapter:
        chapters.append(current_chapter)

    return EssayPlan(
        introduction=intro_title,
        chapters=chapters,
        conclusion=conclusion_title,
        references=references_title
    )
