from typing import List, Optional

from pydantic import BaseModel, Field


# --- Подглава ---
class Subchapter(BaseModel):
    title: str = Field(..., description="Название подглавы")
    text: str = Field(..., description="Текст подглавы")

# --- Глава с подглавами ---
class Chapter(BaseModel):
    title: str = Field(..., description="Название главы")
    text: str = Field(..., description="Текст главы")
    subchapters: List[Subchapter] = Field(default_factory=list, description="Список подглав")

# --- План главы ---
class PlanChapter(BaseModel):
    title: str = Field(..., description="Название главы в плане")
    subchapters: List[str] = Field(default_factory=list, description="Список названий подглав в плане")

# --- План всего реферата ---
class EssayPlan(BaseModel):
    introduction: str = Field("Введение", description="Название раздела введения")
    chapters: List[PlanChapter] = Field(default_factory=list, description="Главы и подглавы плана")
    conclusion: str = Field("Заключение", description="Название раздела заключения")
    references: str = Field("Использованные литературы", description="Название раздела литературы")

# --- Введение ---
class Introduction(BaseModel):
    text: str = Field(..., description="Текст введения")

# --- Заключение ---
class Conclusion(BaseModel):
    text: str = Field(..., description="Текст заключения")

# --- Литература ---
class References(BaseModel):
    items: List[str] = Field(default_factory=list, description="Список литературы")

# --- Метаданные реферата ---
class EssayMetadata(BaseModel):
    discipline: str = Field("_______________", description="Дисциплина")
    department: str = Field("________________________", description="Кафедра")
    topic_name: str = Field("____________________________________________", description="Тема")
    author: str = Field("______________________", description="Автор")
    group: str = Field("_____________________________", description="Группа")
    checked_by: str = Field("_________________________", description="Проверил")
    year: str = Field("2024", description="Год")
    city: str = Field("Бишкек", description="Город")

# --- Полный реферат ---
class Essay(BaseModel):
    topic: str = Field(..., description="Тема реферата")
    language: str = Field(..., description="Язык реферата")
    plan: EssayPlan = Field(default_factory=EssayPlan, description="План реферата")
    introduction: Introduction = Field(default_factory=Introduction, description="Введение")
    chapters: List[Chapter] = Field(default_factory=list, description="Список глав с текстом")
    conclusion: Conclusion = Field(default_factory=Conclusion, description="Заключение")
    references: References = Field(default_factory=References, description="Литература")
    metadata: EssayMetadata = Field(default_factory=EssayMetadata, description="Метаданные реферата")
    json_path: Optional[str] = Field(None, description="Путь для сохранения JSON")
    docx_path: Optional[str] = Field(None, description="Путь для сохранения DOCX")
