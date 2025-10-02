# main_sync.py
import os
import time
from ai_referat.pipeline import AIReferatManagerSync
from ai_referat.config import RESULTS_JSON_DIR, RESULTS_DOCX_DIR

def main():
    start_time = time.time()

    topic = "История HTML"
    json_path = os.path.join(RESULTS_JSON_DIR, f"referat_{topic}.json")
    docx_path = os.path.join(RESULTS_DOCX_DIR, f"referat_{topic}.docx")

    manager_sync = AIReferatManagerSync(
        topic="Искусственный интеллект",
        language="RU",
        author="Иванов И.И.",
        group="БФ-101",
        discipline="Информатика",
        department="Кафедра ИТ",
        checked_by="Петров П.П.",
        year="2025",
        city="Бишкек",
        max_chapters=5,
        max_subchapters=5,
        min_pages=10,
        max_pages=20,
        chars_per_page=1800,
        json_path="essay.json",
        docx_path="essay.docx",
        api_key="твой_openai_api_key",
        model="gpt-4",
        base_url="https://api.openai.com/v1"
    )

    essay = manager.generate_essay()

    end_time = time.time()
    elapsed = end_time - start_time

    print("\n✅ Генерация завершена!")
    print(f"⏱ Время выполнения: {elapsed:.2f} сек.")
    print("📄 JSON:", essay.json_path)
    print("📄 DOCX:", essay.docx_path)

if __name__ == "__main__":
    main()
