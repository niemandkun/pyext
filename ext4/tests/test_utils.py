import unittest
import re

from ext4.utils import *
from ext4.consts import *


class TestFormatFileMode(unittest.TestCase):
    def test_directory_flag(self):
        fmt = format_file_mode(S_IFDIR)
        self.assertTrue('d' in fmt)

    def test_one_read_flag(self):
        fmt = format_file_mode(S_IRUSR)
        self.assertEqual(len(re.findall('r', fmt)), 1)

    def test_three_read_flags(self):
        fmt = format_file_mode(S_IRUSR | S_IRGRP | S_IROTH)
        self.assertEqual(len(re.findall('r', fmt)), 3)

    def test_one_rwx(self):
        fmt = format_file_mode(S_IRUSR | S_IWUSR | S_IXUSR)
        self.assertEqual(len(re.findall('rwx', fmt)), 1)

    def test_three_rwxs(self):
        fmt = format_file_mode(S_IRUSR | S_IWUSR | S_IXUSR |
                               S_IRGRP | S_IWGRP | S_IXGRP |
                               S_IROTH | S_IWOTH | S_IXOTH)
        self.assertEqual(len(re.findall('rwx', fmt)), 3)


class TestFormatFileModeNum(unittest.TestCase):
    def test_one_read_flag(self):
        fmt = format_file_mode_num(S_IRUSR)
        self.assertEqual(fmt, 0o400)

    def test_three_read_flags(self):
        fmt = format_file_mode_num(S_IRUSR | S_IRGRP | S_IROTH)
        self.assertEqual(fmt, 0o444)

    def test_one_rwx(self):
        fmt = format_file_mode_num(S_IRUSR | S_IWUSR | S_IXUSR)
        self.assertEqual(fmt, 0o700)

    def test_three_rwxs(self):
        fmt = format_file_mode_num(S_IRUSR | S_IWUSR | S_IXUSR |
                                   S_IRGRP | S_IWGRP | S_IXGRP |
                                   S_IROTH | S_IWOTH | S_IXOTH)
        self.assertEqual(fmt, 0o777)

    def test_default_file_mode(self):
        fmt = format_file_mode_num(S_IRUSR | S_IWUSR | S_IXUSR |
                                   S_IRGRP | S_IXGRP |
                                   S_IROTH | S_IXOTH)
        self.assertEqual(fmt, 0o755)


class TestUtils(unittest.TestCase):
    def test_padded_with_zeroes(self):
        data = b'asdf'
        padded = padded_with_zeroes(data, 5)
        self.assertEqual(len(padded), 5)
        self.assertEqual(padded[:-1], data)
        self.assertEqual(padded[-1], 0)

    def test_del_trailing_zeroes(self):
        data = b'asdf'
        padded = data + b'\x00' * 100
        handled = del_trailing_zeros(padded)
        self.assertEqual(len(handled), len(data))
        self.assertEqual(handled, data)


class TestDisassemblePath(unittest.TestCase):
    def test_disassemble_path(self):
        path = list(disassemble_path('/a/b/c/d/'))
        self.assertEqual(path, ['a', 'b', 'c', 'd'])

    def test_disassemble_back(self):
        path = list(disassemble_path('/a/b/c/../d/'))
        self.assertEqual(path, ['a', 'b', 'd'])

    def test_disassemble_root(self):
        path = list(disassemble_path('/'))
        self.assertEqual(len(path), 0)

    def test_disassemble_point(self):
        path = list(disassemble_path('/a/./b/./././././c/./d/'))
        self.assertEqual(path, ['a', 'b', 'c', 'd'])

    def test_disassemble_without_slash(self):
        path = list(disassemble_path('a/b/c/d'))
        self.assertEqual(path, ['a', 'b', 'c', 'd'])
