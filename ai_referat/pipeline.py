# ai_referat/pipeline.py
import asyncio
from pprint import pprint as pp
from typing import Optional

from ai_referat.client import AIClientAsync, AIClientSync
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


# -------------------------------------------------------
# Базовый класс с общей логикой
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
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        base_url: Optional[str] = None,
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

        self.api_key = api_key
        self.model = model
        self.base_url = base_url

        self.client = None

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

# -------------------------------------------------------
# Асинхронный менеджер
# -------------------------------------------------------
class AIReferatManagerAsync(_BaseReferatManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = AIClientAsync(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def generate_plan(self):
        prompt = self.prompts.plan()
        raw_plan = await self.client.get_response_async(content=prompt, rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
        plan = parse_plan(raw_plan)
        pp(plan, indent=4)
        return plan

    async def generate_content(self, plan):
        async def gen_intro():
            text = await self.client.get_response_async(self.prompts.intro(), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Introduction(text=text)

        async def gen_conclusion():
            text = await self.client.get_response_async(self.prompts.conclusion(), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Conclusion(text=text)

        async def gen_references():
            text = await self.client.get_response_async(self.prompts.references(), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            items = [line.strip() for line in text.split("\n") if line.strip()]
            return References(items=items)

        async def gen_chapter(plan_chapter):
            chap_text = await self.client.get_response_async(self.prompts.chapter(plan_chapter.title), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            subchapters = []
            if plan_chapter.subchapters:
                sub_texts = await asyncio.gather(*[
                    self.client.get_response_async(self.prompts.subchapter(plan_chapter.title, sub), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
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
        self.client = AIClientSync(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate_plan(self):
        prompt = self.prompts.plan()
        raw_plan = self.client.get_response_sync(content=prompt, rules="", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
        plan = parse_plan(raw_plan)
        pp(plan, indent=4)
        return plan

    def generate_content(self, plan):
        def gen_intro():
            text = self.client.get_response_sync(self.prompts.intro(), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Introduction(text=text)

        def gen_conclusion():
            text = self.client.get_response_sync(self.prompts.conclusion(), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            return Conclusion(text=text)

        def gen_references():
            text = self.client.get_response_sync(self.prompts.references(), "", min_length=MIN_LENGTH, max_retries=MAX_RETRIES)
            items = [line.strip() for line in text.split("\n") if line.strip()]
            return References(items=items)

        def gen_chapter(plan_chapter):
            # Генерация текста для самой главы
            chap_text = self.client.get_response_sync(
                self.prompts.chapter(plan_chapter.title),
                "",
                min_length=MIN_LENGTH,
                max_retries=MAX_RETRIES
            )

            subchapters = []
            if plan_chapter.subchapters:
                sub_results = []

                # Перебор подглав
                for sub in plan_chapter.subchapters:
                    print(f"▶ Генерация подглавы: {sub} ...")
                    text = self.client.get_response_sync(
                        self.prompts.subchapter(plan_chapter.title, sub),
                        "",
                        min_length=MIN_LENGTH,
                        max_retries=MAX_RETRIES
                    )
                    sub_results.append(text)

                # Создаём список подглав
                subchapters = [
                    Subchapter(title=sub, text=text)
                    for sub, text in zip(plan_chapter.subchapters, sub_results)
                ]

            return Chapter(
                title=plan_chapter.title,
                text=chap_text,
                subchapters=subchapters
            )


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
