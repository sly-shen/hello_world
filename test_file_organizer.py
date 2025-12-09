import unittest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import os

import file_organizer

class TestFileOrganizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_file(self, path_parts, content=""):
        p = self.test_dir / Path(*path_parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return p

    def test_no_duplicates(self):
        self.create_file(["a.txt"], "a")
        self.create_file(["b.txt"], "b")

        file_organizer.resolve_duplicates(self.test_dir)

        self.assertTrue((self.test_dir / "a.txt").exists())
        self.assertTrue((self.test_dir / "b.txt").exists())
        self.assertEqual(len(list(self.test_dir.rglob("*.txt"))), 2)

    def test_simple_duplicates(self):
        # dir1/a.txt, dir2/a.txt
        self.create_file(["dir1", "a.txt"], "content1")
        self.create_file(["dir2", "a.txt"], "content2")

        file_organizer.resolve_duplicates(self.test_dir)

        # Expect one a.txt and one a(1).txt
        # Since sorted by path, dir1/a.txt comes before dir2/a.txt
        self.assertTrue((self.test_dir / "dir1" / "a.txt").exists())
        self.assertFalse((self.test_dir / "dir2" / "a.txt").exists())
        self.assertTrue((self.test_dir / "dir2" / "a(1).txt").exists())

    def test_collision_handling(self):
        # dir1/a.txt
        # dir2/a.txt
        # dir1/a(1).txt  <-- collision for renaming
        self.create_file(["dir1", "a.txt"], "content1")
        self.create_file(["dir2", "a.txt"], "content2")
        self.create_file(["dir1", "a(1).txt"], "existing")

        file_organizer.resolve_duplicates(self.test_dir)

        # dir1/a.txt keeps name
        self.assertTrue((self.test_dir / "dir1" / "a.txt").exists())
        # dir1/a(1).txt keeps name (it was unique stem "a(1)" initially)
        self.assertTrue((self.test_dir / "dir1" / "a(1).txt").exists())
        # dir2/a.txt must become a(2) because a(1) is used
        self.assertTrue((self.test_dir / "dir2" / "a(2).txt").exists())
        self.assertFalse((self.test_dir / "dir2" / "a.txt").exists())

    def test_dry_run(self):
        self.create_file(["dir1", "a.txt"])
        self.create_file(["dir2", "a.txt"])

        file_organizer.resolve_duplicates(self.test_dir, dry_run=True)

        self.assertTrue((self.test_dir / "dir1" / "a.txt").exists())
        self.assertTrue((self.test_dir / "dir2" / "a.txt").exists())
        self.assertFalse((self.test_dir / "dir2" / "a(1).txt").exists())

    def test_csv_generation(self):
        self.create_file(["test.txt"], "content")
        csv_path = self.test_dir / "report.csv"

        file_organizer.generate_csv(self.test_dir, csv_path)

        self.assertTrue(csv_path.exists())
        content = csv_path.read_text()
        self.assertIn("Absolute Path,Filename,Extension", content)
        self.assertIn("test.txt,test,.txt", content)

    @patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w'))
    def test_main_cli(self, mock_stdout):
        # Integration test for main()
        self.create_file(["dir1", "a.txt"])
        self.create_file(["dir2", "a.txt"])

        test_args = ["file_organizer.py", str(self.test_dir)]
        with patch.object(sys, 'argv', test_args):
            file_organizer.main()

        self.assertTrue((self.test_dir / "dir1" / "a.txt").exists())
        self.assertTrue((self.test_dir / "dir2" / "a(1).txt").exists())
        self.assertTrue((self.test_dir / "file_report.csv").exists())

if __name__ == "__main__":
    unittest.main()
