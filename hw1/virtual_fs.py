import tarfile
from io import BytesIO


class VirtualFileSystem:
    def __init__(self, tar_path):
        """
        Инициализация виртуальной файловой системы из tar-архива.
        """
        self.tar_path = tar_path
        self.files = {}  # Словарь для хранения файловой структуры
        self._load_tar_to_memory()

    def _load_tar_to_memory(self):
        """
        Загружает содержимое tar-архива в память.
        """
        try:
            with tarfile.open(self.tar_path, "r") as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        # Сохраняем содержимое файла
                        file_content = tar.extractfile(member).read()
                        self.files[member.name] = file_content
                    elif member.isdir():
                        # Добавляем директорию как ключ с пустым значением
                        self.files[member.name] = None
        except tarfile.ReadError as e:
            raise ValueError(f"Ошибка чтения tar-архива: {e}")

    def list_files(self, path="."):
        """
        Возвращает список файлов и директорий в указанном пути.
        """
        path = path.rstrip("/") + "/"
        return [
            name[len(path) :] for name in self.files.keys()
            if name.startswith(path) and name != path
        ]

    def get_file_content(self, path):
        """
        Возвращает содержимое файла.
        """
        if path in self.files and self.files[path] is not None:
            return self.files[path].decode("utf-8")
        raise FileNotFoundError(f"Файл {path} не найден или это директория.")

    def chmod(self, path, mode):
        """
        Эмулирует изменение прав доступа для файла или директории.
        """
        if path in self.files:
            # Просто эмулируем, не изменяя реальных файлов
            return f"Права доступа {mode} установлены для {path}"
        raise FileNotFoundError(f"Файл {path} не найден.")

    def is_directory(self, path):
        """
        Проверяет, является ли путь директорией.
        """
        return path in self.files and self.files[path] is None

    def get_date(self):
        """
        Возвращает текущую дату и время.
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def reverse_text(self, text):
        """
        Реверсирует строку.
        """
        return text[::-1]
