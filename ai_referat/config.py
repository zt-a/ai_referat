# ai_referat/config.py
from dotenv import load_dotenv
import os

# Загружаем переменные из .env (если файл существует)
load_dotenv()

# === Основные настройки ===
LANGUAGE = os.getenv("LANGUAGE", "русский")
MIN_PAGES = int(os.getenv("MIN_PAGES", 2))
MAX_PAGES = int(os.getenv("MAX_PAGES", 5))
MAX_CHAPTERS = int(os.getenv("MAX_CHAPTERS", 3))
MAX_SUBCHAPTERS = int(os.getenv("MAX_SUBCHAPTERS", 2))
MAX_CHARS_PER_PAGE = int(os.getenv("MAX_CHARS_PER_PAGE", 1800))

# === Шрифты для DOCX ===
FONT = os.getenv("FONT", "Times New Roman")
FONT_SIZE = int(os.getenv("FONT_SIZE", 14))

# === API ключи для AIClient ===
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")  # или другой

# === Директории по умолчанию ===
RESULTS_JSON_DIR = os.getenv("RESULTS_JSON_DIR", "./results/json")
RESULTS_DOCX_DIR = os.getenv("RESULTS_DOCX_DIR", "./results/docx")

# Убедимся, что директории для результатов существуют
os.makedirs(RESULTS_JSON_DIR, exist_ok=True)
os.makedirs(RESULTS_DOCX_DIR, exist_ok=True)
