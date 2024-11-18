import tkinter as tk
from tkinter import scrolledtext
from virtual_fs import VirtualFileSystem
from commands import ShellCommands

class EmulatorGUI:
    def __init__(self, master, virtual_fs):
        self.master = master
        self.master.title("Shell Emulator")
        self.virtual_fs = virtual_fs
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
        parts = command.split()
        cmd_name = parts[0]

        if cmd_name == "ls":
            result = self.commands.ls(parts[1] if len(parts) > 1 else ".")
        elif cmd_name == "cd":
            result = self.commands.cd(parts[1])
        elif cmd_name == "exit":
            result = self.commands.exit_shell()
            self.master.quit()
        elif cmd_name == "chmod":
            result = self.commands.chmod(parts[1], parts[2])
        elif cmd_name == "date":
            result = self.commands.date()
        elif cmd_name == "rev":
            result = self.commands.rev(parts[1])
        else:
            result = f"Unknown command: {cmd_name}"

        self.output_text.insert(tk.END, result + "\n")
        self.output_text.yview(tk.END)

def run_gui(tar_path):
    virtual_fs = VirtualFileSystem(tar_path)
    root = tk.Tk()
    emulator = EmulatorGUI(root, virtual_fs)
    root.mainloop()

if __name__ == "__main__":
    run_gui("/home/artem/work/dscomfig/1/dsconfig/virtual_fs.tar")
