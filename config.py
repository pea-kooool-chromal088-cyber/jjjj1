import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота из задания
TELEGRAM_BOT_TOKEN = "8436269209:AAEYFDNXZmM1DZ5PlfL5_nsOYHsQvQv4Qkw"

# Путь к базе данных
DATABASE_PATH = os.getenv("DATABASE_PATH", "registrations.db")

# ID администраторов (через запятую в .env файле)
ADMIN_IDS = []
if os.getenv("ADMIN_IDS"):
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS").split(",")]