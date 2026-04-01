# config.py
import os

# Сетевые настройки
HOST = '0.0.0.0'  # Слушать все интерфейсы (для LAN)
PORT = 65432
BUFFER_SIZE = 4096

# Настройки хранения
# По умолчанию создаем папку html_storage, так как сервер ориентирован на HTML
STORAGE_DIR_NAME = 'html_storage'
STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), STORAGE_DIR_NAME)

# Таймауты и лимиты
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB лимит для безопасности
ENCODING = 'utf-8'