import unittest
from virtual_fs import VirtualFileSystem
from commands import ShellCommands

class TestShellCommands(unittest.TestCase):
    def setUp(self):
        self.virtual_fs = VirtualFileSystem("/home/artem/work/dsconfig/virtual_fs.tar")
        self.commands = ShellCommands(self.virtual_fs)

    def test_ls(self):
        result = self.commands.ls(".")
        self.assertIn("file1.txt", result)
        self.assertIn("dir1", result)

    def test_cd(self):
        result = self.commands.cd("dir1")
        self.assertEqual(result, "Changed directory to dir1")

    def test_chmod(self):
        result = self.commands.chmod("file1.txt", "755")
        self.assertIn("Changed permissions", result)

    def test_date(self):
        result = self.commands.date()
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_rev(self):
        result = self.commands.rev("hello")
        self.assertEqual(result, "olleh")

if __name__ == "__main__":
    unittest.main()
