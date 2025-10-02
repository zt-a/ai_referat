# ai_referat/pipeline_g4f.py
import asyncio
from typing import Optional

from ai_referat.client_g4f import (AIClientAsync,  # твой новый g4f клиент
                                   AIClientSync)
from ai_referat.config import FONT as CFG_FONT
from ai_referat.config import FONT_SIZE as CFG_FONT_SIZE
from ai_referat.config import LANGUAGE as CFG_LANGUAGE
from ai_referat.config import MAX_CHAPTERS as CFG_MAX_CHAPTERS
from ai_referat.config import MAX_CHARS_PER_PAGE as CFG_CHARS_PER_PAGE
from ai_referat.config import MAX_PAGES as CFG_MAX_PAGES
from ai_referat.config import MAX_RETRIES
from ai_referat.config import MAX_SUBCHAPTERS as CFG_MAX_SUBCHAPTERS
from ai_referat.config import MIN_LENGTH
from ai_referat.config import MIN_PAGES as CFG_MIN_PAGES
from ai_referat.docx_writer import create_docx_file
from ai_referat.json_writer import save_json
from ai_referat.models import (Chapter, Conclusion, Essay, EssayMetadata,
                               Introduction, References, Subchapter)
from ai_referat.parser import parse_plan
from ai_referat.prompts import EssayPrompts
from ai_referat.rules import RulesManager


# ----------------- Базовый менеджер -----------------
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


# ----------------- Асинхронный менеджер -----------------
class AIReferatManagerAsync(_BaseReferatManager):
    def __init__(
        self,
        topic: str,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        free: bool = True,
        **kwargs
    ):
        super().__init__(topic, **kwargs)
        self.client = AIClientAsync(model=model, api_key=api_key, base_url=base_url, free=free)

    async def generate_plan(self):
        prompt = self.prompts.plan()
        raw_plan = await self.client.get_response_async(prompt, rules="")
        plan = parse_plan(raw_plan)
        return plan

    async def generate_content(self, plan):
        async def gen_intro():
            text = await self.client.get_response_async(self.prompts.intro(), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Introduction(text=text)

        async def gen_conclusion():
            text = await self.client.get_response_async(self.prompts.conclusion(), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Conclusion(text=text)

        async def gen_references():
            text = await self.client.get_response_async(self.prompts.references(), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            items = [line.strip() for line in text.split("\n") if line.strip()]
            return References(items=items)

        async def gen_chapter(plan_chapter):
            chap_text = await self.client.get_response_async(self.prompts.chapter(plan_chapter.title), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            subchapters = []
            if plan_chapter.subchapters:
                sub_texts = await asyncio.gather(*[
                    self.client.get_response_async(self.prompts.subchapter(plan_chapter.title, sub), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
                    for sub in plan_chapter.subchapters
                ])
                subchapters = [Subchapter(title=sub, text=sub_texts[i]) for i, sub in enumerate(plan_chapter.subchapters)]
            return Chapter(title=plan_chapter.title, text=chap_text, subchapters=subchapters)

        chapters = await asyncio.gather(*[gen_chapter(ch) for ch in plan.chapters])
        introduction, conclusion, references = await asyncio.gather(gen_intro(), gen_conclusion(), gen_references())
        return introduction, chapters, conclusion, references

    async def generate_essay(self, json_path: Optional[str] = None, docx_path: Optional[str] = None):
        json_path = json_path or self.default_json_path
        docx_path = docx_path or self.default_docx_path
        plan = await self.generate_plan()
        intro, chapters, conclusion, references = await self.generate_content(plan)
        self.essay = Essay(
            topic=self.topic, language=self.language, plan=plan,
            introduction=intro, chapters=chapters, conclusion=conclusion,
            references=references, metadata=self.metadata,
            json_path=json_path, docx_path=docx_path
        )
        self._save_results(self.essay, json_path, docx_path)
        return self.essay


# ----------------- Синхронный менеджер -----------------
class AIReferatManagerSync(_BaseReferatManager):
    def __init__(
        self,
        topic: str,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        free: bool = True,
        **kwargs
    ):
        super().__init__(topic, **kwargs)
        self.client = AIClientSync(model=model, api_key=api_key, base_url=base_url, free=free)

    def generate_plan(self):
        prompt = self.prompts.plan()
        raw_plan = self.client.get_response_sync(prompt, rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
        plan = parse_plan(raw_plan)
        return plan

    def generate_content(self, plan):
        def gen_intro():
            text = self.client.get_response_sync(self.prompts.intro(), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Introduction(text=text)

        def gen_conclusion():
            text = self.client.get_response_sync(self.prompts.conclusion(), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Conclusion(text=text)

        def gen_references():
            text = self.client.get_response_sync(self.prompts.references(), rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            items = [line.strip() for line in text.split("\n") if line.strip()]
            return References(items=items)

        def gen_chapter(plan_chapter):
            # Генерация текста главы
            chap_text = self.client.get_response_sync(
                self.prompts.chapter(plan_chapter.title),
                rules="",
                min_length=MIN_LENGTH,
                max_retries=MAX_RETRIES
            )

            subchapters = []
            if plan_chapter.subchapters:
                sub_results = []
                for sub in plan_chapter.subchapters:
                    print(f"▶ Генерация подглавы: {sub} ...")
                    text = self.client.get_response_sync(
                        self.prompts.subchapter(plan_chapter.title, sub),
                        rules="",
                        min_length=MIN_LENGTH,
                        max_retries=MAX_RETRIES
                    )
                    sub_results.append(text)

                # Формируем список подглав
                subchapters = [
                    Subchapter(title=sub, text=text)
                    for sub, text in zip(plan_chapter.subchapters, sub_results)
                ]

            return Chapter(
                title=plan_chapter.title,
                text=chap_text,
                subchapters=subchapters
            )

        chapters = [gen_chapter(ch) for ch in plan.chapters]
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
            topic=self.topic, language=self.language, plan=plan,
            introduction=intro, chapters=chapters, conclusion=conclusion,
            references=references, metadata=self.metadata,
            json_path=json_path, docx_path=docx_path
        )
        self._save_results(self.essay, json_path, docx_path)
        return self.essay
