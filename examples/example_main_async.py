# main_async.py
import asyncio
import os
import time
from ai_referat.client import AIClientAsync
from ai_referat.pipeline import AIReferatManagerAsync
from ai_referat.config import RESULTS_JSON_DIR, RESULTS_DOCX_DIR
from ai_referat.config import (
    AI_API_KEY,
    AI_BASE_URL,
    AI_MODEL
)


async def main():
    start_time = time.time()

    topic = "История HTML"
    json_path = os.path.join(RESULTS_JSON_DIR, f"referat_{topic}.json")
    docx_path = os.path.join(RESULTS_DOCX_DIR, f"referat_{topic}.docx")

    manager = AIReferatManagerAsync(
        topic=topic,
        author="Иван Иванов",
        group="CS-22",
        discipline="Информатика",
        department="Кафедра информационных технологий",
        checked_by="Доцент Петров П.П.",
        year="2025",
        city="Бишкек",
        json_path=json_path,
        docx_path=docx_path,
        free=True
    )

    essay = await manager.generate_essay()

    end_time = time.time()
    elapsed = end_time - start_time

    print("\n✅ Генерация завершена!")
    print(f"⏱ Время выполнения: {elapsed:.2f} сек.")
    print("📄 JSON:", essay.json_path)
    print("📄 DOCX:", essay.docx_path)

if __name__ == "__main__":
    asyncio.run(main())
