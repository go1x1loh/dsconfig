import os
from virtual_fs import VirtualFileSystem

class ShellCommands:
    def __init__(self, virtual_fs):
        self.virtual_fs = virtual_fs

    def ls(self, path):
        """Команда ls: список файлов в директории."""
        files = self.virtual_fs.list_files(path)
        return "\n".join(files)

    def cd(self, path):
        """Команда cd: изменить текущую рабочую директорию."""
        if self.virtual_fs.change_dir(path):
            return f"Changed directory to {path}"
        else:
            return "Directory not found."

    def exit_shell(self):
        """Команда exit: выход из эмулятора."""
        return "Exiting the shell."

    def chmod(self, path, mode):
        """Команда chmod: изменить права доступа к файлу/директории."""
        try:
            mode = int(mode, 8)  # Переводим из строки в восьмеричную систему
            if self.virtual_fs.chmod(path, mode):
                return f"Changed permissions of {path} to {oct(mode)}"
            else:
                return f"Failed to change permissions for {path}"
        except ValueError:
            return "Invalid mode."

    def date(self):
        """Команда date: вывод текущей даты и времени."""
        return self.virtual_fs.get_date()

    def rev(self, text):
        """Команда rev: реверсирует строку."""
        return self.virtual_fs.reverse_text(text)
