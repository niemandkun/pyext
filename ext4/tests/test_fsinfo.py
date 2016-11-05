import unittest

from ext4 import FileSystem
from ext4.fsinfo import FileInfo, DirectoryInfo, FileSystemInfo
from ext4.tests.config import PATH_TO_IMAGE


class TestDirectory(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem(open(PATH_TO_IMAGE, 'rb'))
        self.root = self.fs.open('/')

    def test_metadata(self):
        self.assertTrue('d' in self.root.mode_str)
        self.assertTrue(self.root.size == 1024)
        self.assertTrue(self.root.creation_time < self.root.mod_time)

    def test_is_iterator(self):
        iterator = iter(self.root)
        self.assertTrue(hasattr(iterator, '__iter__'))
        self.assertTrue(hasattr(iterator, '__next__'))

    def test_get_all(self):
        entries = self.root.get_all()
        self.assertEqual(len(entries), 8)

    def test_get_files_and_dirs(self):
        entries = self.root.get_all()
        files = self.root.get_files()
        dirs = self.root.get_directories()
        self.assertEqual(len(entries), len(files) + len(dirs))

    def test_get_all_reusable(self):
        for x in range(10):
            entries = self.root.get_all()
        self.assertEqual(len(entries), 8)

    def test_context_manager(self):
        with self.fs.open('/dir1') as d:
            entries = set((x.path for x in d.get_all()))
            self.assertTrue('/dir1/file4' in entries)
            self.assertTrue('/dir1/file5' in entries)

    def test_directory_is_dict(self):
        with self.fs.open('/dir1') as d:
            f = d['file4']
            self.assertTrue(f is not None)
            self.assertEqual(f.name, 'file4')
            self.assertEqual(f.path, '/dir1/file4')
            self.assertEqual(f.inode_no, 14)

    def test_entry_is_fsinfo(self):
        entries = self.root.get_all()
        self.assertTrue(isinstance(entries[0], FileSystemInfo))

    def test_iterator_not_reusable(self):
        for x in range(10):
            entries = set((x.path for x in self.root))
        self.assertFalse('/lost+found' in entries)
        self.assertFalse('/dir1' in entries)
        self.assertEqual(len(entries), 0)

    def test_iterator_content(self):
        entries = set((x.path for x in self.root))
        self.assertTrue('/.' in entries)
        self.assertTrue('/..' in entries)
        self.assertTrue('/lost+found' in entries)
        self.assertTrue('/file1' in entries)
        self.assertTrue('/file2' in entries)
        self.assertTrue('/file3' in entries)
        self.assertTrue('/dir1' in entries)
        self.assertTrue('/dir2' in entries)


class TestFile(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem(open(PATH_TO_IMAGE, 'rb'))
        self.file = self.fs.open('/file1', 'utf-8')

    def test_metadata(self):
        self.assertTrue('d' not in self.file.mode_str)
        self.assertTrue('rw' in self.file.mode_str)
        self.assertEqual(self.file.size, 15)
        self.assertTrue(self.file.creation_time < self.file.mod_time)

    def test_is_iterator(self):
        iterator = iter(self.file)
        self.assertTrue(hasattr(iterator, '__iter__'))
        self.assertTrue(hasattr(iterator, '__next__'))

    def test_read(self):
        lines = self.file.read()
        self.assertEqual(lines, 'file 1 content\n')

    def test_read_reusable(self):
        for _ in range(10):
            lines = self.file.read()
        self.assertEqual(lines, 'file 1 content\n')

    def test_iterator(self):
        content = ['file 1 content', '']
        for index, line in enumerate(self.file):
            self.assertEqual(line, content[index])

    def test_iterator_bytes(self):
        file = self.fs.open('/dir1/file4')
        content = [b'file 4 content\n', ]
        for index, block in enumerate(file):
            self.assertEqual(block, content[index])

    def test_iterator_reusable(self):
        content = ['file 1 content', '']
        for x in range(10):
            for index, line in enumerate(self.file):
                self.assertEqual(line, content[index])

    def test_context_manager(self):
        with self.fs.open('/dir1/file4') as f:
            content = f.read()
            self.assertEqual(content, b'file 4 content\n')

    def test_encoding(self):
        with self.fs.open('/file1') as f:
            content = f.read()
            self.assertIsInstance(content, bytes)

            f.set_encoding('utf-8')
            content = f.read()
            self.assertIsInstance(content, str)

        with self.fs.open('/file1', 'utf-8') as f:
            content = f.read()
            self.assertIsInstance(content, str)

            f.unset_encoding()
            content = f.read()
            self.assertIsInstance(content, bytes)
