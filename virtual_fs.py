import tarfile
import os

class VirtualFileSystem:
    def __init__(self, tar_path):
        self.tar_path = tar_path
        self.extract_path = "/tmp/virtual_fs"
        self._extract_tar()

    def _extract_tar(self):
        """Извлекает архив TAR в указанную директорию."""
        if not os.path.exists(self.extract_path):
            os.makedirs(self.extract_path)
        with tarfile.open(self.tar_path, "r") as tar:
            tar.extractall(path=self.extract_path)

    def list_files(self, path="."):
        """Возвращает список файлов в указанной директории."""
        full_path = os.path.join(self.extract_path, path)
        if os.path.exists(full_path):
            return os.listdir(full_path)
        else:
            return []

    def change_dir(self, path):
        """Проверяет существование директории и изменяет текущую рабочую директорию."""
        full_path = os.path.join(self.extract_path, path)
        if os.path.isdir(full_path):
            return True
        return False

    def get_file_stat(self, path):
        """Возвращает информацию о файле или директории (права, дата и т.д.)."""
        full_path = os.path.join(self.extract_path, path)
        if os.path.exists(full_path):
            stat = os.stat(full_path)
            return stat
        return None

    def chmod(self, path, mode):
        """Изменяет права доступа для файла или директории."""
        full_path = os.path.join(self.extract_path, path)
        if os.path.exists(full_path):
            os.chmod(full_path, mode)
            return True
        return False

    def get_date(self):
        """Возвращает текущую дату и время."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def reverse_text(self, text):
        """Реверсирует строку."""
        return text[::-1]
