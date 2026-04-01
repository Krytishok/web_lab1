# storage.py
import os
from config import STORAGE_DIR

class StorageService:
    """Сервис для управления файлами в директории хранения."""

    def __init__(self):
        self._ensure_directory()

    def _ensure_directory(self):
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)

    def list_files(self) -> list:
        """Возвращает список файлов."""
        try:
            return os.listdir(STORAGE_DIR)
        except Exception:
            return []

    def get_safe_path(self, filename: str) -> str:
        """Возвращает полный путь, предотвращая выход за пределы директории."""
        # os.path.basename защищает от путей вида ../../etc/passwd
        safe_name = os.path.basename(filename)
        return os.path.join(STORAGE_DIR, safe_name)

    def file_exists(self, filename: str) -> bool:
        path = self.get_safe_path(filename)
        return os.path.exists(path) and os.path.isfile(path)

    def get_file_size(self, filename: str) -> int:
        path = self.get_safe_path(filename)
        return os.path.getsize(path)

    def save_file(self, filename: str, content: bytes):
        path = self.get_safe_path(filename)
        with open(path, 'wb') as f:
            f.write(content)

    def read_file(self, filename: str) -> bytes:
        path = self.get_safe_path(filename)
        with open(path, 'rb') as f:
            return f.read()