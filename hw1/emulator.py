import tkinter as tk
from tkinter import scrolledtext
import xml.etree.ElementTree as ET
from virtual_fs import VirtualFileSystem


class ShellCommands:
    def __init__(self, virtual_fs):
        self.virtual_fs = virtual_fs
        self.current_dir = "."  # Текущая директория

    def ls(self, path="."):
        """
        Команда ls: список файлов в директории.
        """
        full_path = self._get_full_path(path)
        try:
            files = self.virtual_fs.list_files(full_path)
            return "\n".join(files)
        except FileNotFoundError:
            return "Директория не найдена."

    def cd(self, path):
        """
        Команда cd: изменить текущую директорию.
        """
        full_path = self._get_full_path(path)
        if self.virtual_fs.is_directory(full_path):
            self.current_dir = full_path.rstrip("/")
            return f"Перешли в директорию {self.current_dir}"
        return "Директория не найдена."

    def chmod(self, path, mode):
        """
        Команда chmod: изменить права доступа.
        """
        full_path = self._get_full_path(path)
        try:
            return self.virtual_fs.chmod(full_path, mode)
        except FileNotFoundError:
            return "Файл или директория не найдены."

    def date(self):
        """
        Команда date: текущая дата и время.
        """
        return self.virtual_fs.get_date()

    def rev(self, text):
        """
        Команда rev: реверсирует строку.
        """
        return self.virtual_fs.reverse_text(text)

    def _get_full_path(self, path):
        """
        Возвращает полный путь относительно текущей директории.
        """
        if path.startswith("/"):
            return path.lstrip("/")
        return f"{self.current_dir}/{path}".strip("/")


class EmulatorGUI:
    def __init__(self, master, virtual_fs):
        self.master = master
        self.master.title("Shell Emulator")
        self.commands = ShellCommands(virtual_fs)

        self.output_text = scrolledtext.ScrolledText(master, width=80, height=20)
        self.output_text.pack()

        self.input_entry = tk.Entry(master, width=80)
        self.input_entry.pack()
        self.input_entry.bind("<Return>", self.process_command)

    def process_command(self, event=None):
        command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.execute_command(command)

    def execute_command(self, command):
        parts = command.split(maxsplit=1)
        cmd_name = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        if cmd_name == "ls":
            result = self.commands.ls(arg)
        elif cmd_name == "cd":
            result = self.commands.cd(arg)
        elif cmd_name == "chmod":
            args = arg.split(maxsplit=1)
            if len(args) == 2:
                result = self.commands.chmod(args[0], args[1])
            else:
                result = "Неверный формат команды chmod."
        elif cmd_name == "date":
            result = self.commands.date()
        elif cmd_name == "rev":
            result = self.commands.rev(arg)
        elif cmd_name == "exit":
            result = "Выход из эмулятора."
            self.master.quit()
        else:
            result = f"Неизвестная команда: {cmd_name}"

        self.output_text.insert(tk.END, result + "\n")
        self.output_text.yview(tk.END)


def read_config(config_path):
    """
    Считывает путь к TAR-архиву из XML-конфигурации.
    """
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
        return root.find("tar_path").text
    except ET.ParseError:
        raise ValueError("Ошибка чтения конфигурации.")


def run_gui(config_path):
    tar_path = read_config(config_path)
    virtual_fs = VirtualFileSystem(tar_path)
    root = tk.Tk()
    emulator = EmulatorGUI(root, virtual_fs)
    root.mainloop()


if __name__ == "__main__":
    # Задайте путь к конфигурации:
    run_gui("config.xml")
