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

    manager = AIReferatManagerSync(
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
