# main_sync_g4f.py
import os
import time
from ai_referat.pipeline_g4f import AIReferatManagerSync  # наш синхронный g4f менеджер
from ai_referat.config import RESULTS_JSON_DIR, RESULTS_DOCX_DIR

def main():
    start_time = time.time()

    topic = "История HTML"
    json_path = os.path.join(RESULTS_JSON_DIR, f"referat_{topic}.json")
    docx_path = os.path.join(RESULTS_DOCX_DIR, f"referat_{topic}.docx")

    # ---------------------- Настройка менеджера ----------------------
    manager = AIReferatManagerSync(
        topic=topic,
        language="RU",
        author="Иванов И.И.",
        group="БФ-101",
        discipline="Информатика",
        department="Кафедра ИТ",
        checked_by="Петров П.П.",
        year="2025",
        city="Бишкек",
        max_chapters=1,
        max_subchapters=3,
        min_pages=1,
        max_pages=3,
        chars_per_page=1000,
        json_path=json_path,
        docx_path=docx_path,
        model="gpt-4o-mini",   # Модель g4f
        api_key=None,          # Если free режим
        base_url=None,         # Если free режим
        free=True              # Используем бесплатные провайдеры g4f
    )

    # ---------------------- Генерация эссе ----------------------
    essay = manager.generate_essay()

    end_time = time.time()
    elapsed = end_time - start_time

    print("\n✅ Генерация завершена!")
    print(f"⏱ Время выполнения: {elapsed:.2f} сек.")
    print("📄 JSON:", essay.json_path)
    print("📄 DOCX:", essay.docx_path)

if __name__ == "__main__":
    main()
