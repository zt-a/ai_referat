# ai_referat/pipeline.py
import asyncio
from typing import Optional
from tqdm.asyncio import tqdm as tqdm_async
from tqdm import tqdm as tqdm_sync
from pprint import pprint as pp

from ai_referat.client import AIClientAsync, AIClientSync
from ai_referat.models import (
    Essay,
    Chapter,
    Subchapter,
    Introduction,
    Conclusion,
    References,
    EssayMetadata,
)
from ai_referat.parser import parse_plan
from ai_referat.json_writer import save_json
from ai_referat.docx_writer import create_docx_file
from ai_referat.prompts import EssayPrompts
from ai_referat.rules import RulesManager
from ai_referat.config import (
    LANGUAGE as CFG_LANGUAGE,
    MIN_PAGES as CFG_MIN_PAGES,
    MAX_PAGES as CFG_MAX_PAGES,
    MAX_CHAPTERS as CFG_MAX_CHAPTERS,
    MAX_SUBCHAPTERS as CFG_MAX_SUBCHAPTERS,
    MAX_CHARS_PER_PAGE as CFG_CHARS_PER_PAGE,
    FONT as CFG_FONT,
    FONT_SIZE as CFG_FONT_SIZE,
)

# -------------------------------------------------------
# Базовый класс с общей логикой (наследники переопределяют client и вызовы)
# -------------------------------------------------------

class _BaseReferatManager:
    def __init__(
        self,
        topic: str,
        language: str = CFG_LANGUAGE,
        author: str = "Автор",
        group: str = "Группа",
        discipline: str = "Дисциплина",
        department: str = "Кафедра",
        checked_by: str = "",
        year: str = "2024",
        city: str = "Бишкек",
        max_chapters: int = CFG_MAX_CHAPTERS,
        max_subchapters: int = CFG_MAX_SUBCHAPTERS,
        min_pages: int = CFG_MIN_PAGES,
        max_pages: int = CFG_MAX_PAGES,
        chars_per_page: int = CFG_CHARS_PER_PAGE,
        json_path: Optional[str] = None,
        docx_path: Optional[str] = None,
    ):
        self.topic = topic
        self.language = language

        self.metadata = EssayMetadata(
            author=author,
            group=group,
            discipline=discipline,
            department=department,
            checked_by=checked_by,
            year=str(year),
            city=city,
            topic_name=topic,
        )

        # клиент назначается в наследниках
        self.client = None

        self.rules_manager = RulesManager(
            language=language,
            min_pages=min_pages,
            max_pages=max_pages,
            chars_per_page=chars_per_page,
        )

        self.prompts = EssayPrompts(
            topic=topic,
            language=language,
            max_chapters=max_chapters,
            max_subchapters=max_subchapters,
            chars_per_page=chars_per_page,
            min_pages=min_pages,
            max_pages=max_pages,
            rules=self.rules_manager.get_rules(),
        )

        self.max_chapters = max_chapters
        self.max_subchapters = max_subchapters

        self.essay: Optional[Essay] = None
        self.default_json_path = json_path
        self.default_docx_path = docx_path

    def _save_results(self, essay: Essay, json_path: Optional[str], docx_path: Optional[str]):
        """Сохранение JSON и DOCX"""
        if json_path:
            save_json(essay, json_path=json_path)

        if docx_path:
            create_docx_file(
                docx_path=docx_path,
                json_data=essay.dict(),
                discipline=self.metadata.discipline,
                department=self.metadata.department,
                topic_name=self.metadata.topic_name,
                author=self.metadata.author,
                group=self.metadata.group,
                checked_by=self.metadata.checked_by,
                year=self.metadata.year,
                city=self.metadata.city,
                content_font=CFG_FONT,
                content_size=CFG_FONT_SIZE,
            )

# -------------------------------------------------------
# Асинхронный менеджер
# -------------------------------------------------------

class AIReferatManagerAsync(_BaseReferatManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = AIClientAsync()

    async def generate_plan(self):
        prompt = self.prompts.plan()
        raw_plan = await self.client.get_response_async(content=prompt, rules="")
        plan = parse_plan(raw_plan)
        pp(plan, indent=4)
        return plan

    async def generate_content(self, plan):
        async def gen_intro():
            text = await self.client.get_response_async(self.prompts.intro(), "")
            return Introduction(text=text)

        async def gen_conclusion():
            text = await self.client.get_response_async(self.prompts.conclusion(), "")
            return Conclusion(text=text)

        async def gen_references():
            text = await self.client.get_response_async(self.prompts.references(), "")
            items = [line.strip() for line in text.split("\n") if line.strip()]
            return References(items=items)

        async def gen_chapter(plan_chapter):
            chap_text = await self.client.get_response_async(
                self.prompts.chapter(plan_chapter.title), ""
            )
            subchapters = []
            if plan_chapter.subchapters:
                sub_tasks = [
                    self.client.get_response_async(
                        self.prompts.subchapter(plan_chapter.title, sub), ""
                    )
                    for sub in plan_chapter.subchapters
                ]
                sub_results = []
                for future in tqdm_async(asyncio.as_completed(sub_tasks),
                                         total=len(sub_tasks),
                                         desc=f"{plan_chapter.title} -> подглавы"):
                    text = await future
                    sub_results.append(text)
                subchapters = [
                    Subchapter(title=sub, text=text)
                    for sub, text in zip(plan_chapter.subchapters, sub_results)
                ]
            return Chapter(title=plan_chapter.title, text=chap_text, subchapters=subchapters)

        chapter_tasks = [gen_chapter(ch) for ch in plan.chapters]
        chapters = []
        for i, chapter in enumerate(await asyncio.gather(*chapter_tasks)):
            chapters.append(chapter)
            tqdm_async.write(f"Глава {i + 1}/{len(plan.chapters)} готова: {chapter.title}")

        intro, conclusion, references = await asyncio.gather(
            gen_intro(), gen_conclusion(), gen_references()
        )
        return intro, chapters, conclusion, references

    async def generate_essay(self, json_path: Optional[str] = None, docx_path: Optional[str] = None):
        json_path = json_path or self.default_json_path
        docx_path = docx_path or self.default_docx_path

        plan = await self.generate_plan()
        intro, chapters, conclusion, references = await self.generate_content(plan)

        self.essay = Essay(
            topic=self.topic,
            language=self.language,
            plan=plan,
            introduction=intro,
            chapters=chapters,
            conclusion=conclusion,
            references=references,
            metadata=self.metadata,
            json_path=json_path,
            docx_path=docx_path,
        )
        self._save_results(self.essay, json_path, docx_path)
        return self.essay


# -------------------------------------------------------
# Синхронный менеджер
# -------------------------------------------------------

class AIReferatManagerSync(_BaseReferatManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = AIClientSync()

    def generate_plan(self):
        prompt = self.prompts.plan()
        raw_plan = self.client.get_response_sync(content=prompt, rules="")
        plan = parse_plan(raw_plan)
        pp(plan, indent=4)
        return plan

    def generate_content(self, plan):
        def gen_intro():
            text = self.client.get_response_sync(self.prompts.intro(), "")
            return Introduction(text=text)

        def gen_conclusion():
            text = self.client.get_response_sync(self.prompts.conclusion(), "")
            return Conclusion(text=text)

        def gen_references():
            text = self.client.get_response_sync(self.prompts.references(), "")
            items = [line.strip() for line in text.split("\n") if line.strip()]
            return References(items=items)

        def gen_chapter(plan_chapter):
            chap_text = self.client.get_response_sync(
                self.prompts.chapter(plan_chapter.title), ""
            )
            subchapters = []
            if plan_chapter.subchapters:
                sub_results = []
                for sub in tqdm_sync(plan_chapter.subchapters,
                                     desc=f"{plan_chapter.title} -> подглавы"):
                    text = self.client.get_response_sync(
                        self.prompts.subchapter(plan_chapter.title, sub), ""
                    )
                    sub_results.append(text)
                subchapters = [
                    Subchapter(title=sub, text=text)
                    for sub, text in zip(plan_chapter.subchapters, sub_results)
                ]
            return Chapter(title=plan_chapter.title, text=chap_text, subchapters=subchapters)

        chapters = []
        for i, ch in enumerate(plan.chapters):
            chapter = gen_chapter(ch)
            chapters.append(chapter)
            print(f"Глава {i + 1}/{len(plan.chapters)} готова: {chapter.title}")

        intro = gen_intro()
        conclusion = gen_conclusion()
        references = gen_references()

        return intro, chapters, conclusion, references

    def generate_essay(self, json_path: Optional[str] = None, docx_path: Optional[str] = None):
        json_path = json_path or self.default_json_path
        docx_path = docx_path or self.default_docx_path

        plan = self.generate_plan()
        intro, chapters, conclusion, references = self.generate_content(plan)

        self.essay = Essay(
            topic=self.topic,
            language=self.language,
            plan=plan,
            introduction=intro,
            chapters=chapters,
            conclusion=conclusion,
            references=references,
            metadata=self.metadata,
            json_path=json_path,
            docx_path=docx_path,
        )
        self._save_results(self.essay, json_path, docx_path)
        return self.essay
