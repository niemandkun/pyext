import unittest

from ext4 import FileSystem
from ext4.fsinfo import FileInfo, DirectoryInfo
from ext4.consts import *
from ext4.tests.config import PATH_TO_IMAGE
from ext4.tests.test_structs import test_hi_and_lo_attributes


def disable_incompat_feature(super_block, feature):
    super_block.feature_incompat &= ~feature


def enable_incompat_feature(super_block, feature):
    super_block.feature_incompat |= feature


class TestUsage(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem(open(PATH_TO_IMAGE, 'rb'))

    def is_context_manager(self, obj):
        self.assertTrue(hasattr(obj, '__enter__'))
        self.assertTrue(hasattr(obj, '__exit__'))

    def test_fs_is_context_manager(self):
        self.is_context_manager(self.fs)

    def test_fs_open_context_manager(self):
        f = self.fs.open('/file1')
        self.is_context_manager(f)

    def test_fs_open_directory(self):
        d = self.fs.open('/')
        self.assertIsInstance(d, DirectoryInfo)

    def test_fs_open_file(self):
        f = self.fs.open('/file1')
        self.assertIsInstance(f, FileInfo)


class TestInternals(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem(open(PATH_TO_IMAGE, 'rb'))

    def test_correct_reading_group_desc(self):
        gd = self.fs.open_group_desc(0)
        self.assertEqual(gd.inode_table, 46)
        gd = self.fs.open_group_desc(1)
        self.assertEqual(gd.inode_table, 206)

    def test_correct_64_explaining(self):
        self.assertFalse(self.fs.is64)

    def test_root_inode(self):
        root = self.fs.open_inode(2)
        self.assertEqual(root.mtime, 1440521940)
        self.assertEqual(root.ctime, 1440521940)
        self.assertTrue(root.ctime < root.atime)
        self.assertTrue(root.mode & S_IFDIR)

    def test_regular_inode(self):
        inode = self.find_regular_inode()
        self.assertIsNotNone(inode)
        self.assertTrue(inode.block[0] != b'\x00')

    def find_regular_inode(self):
        for index in range(11, 15):
            inode = self.fs.open_inode(index)
            if inode.mode & S_IFREG:
                return inode
        return None

    def test_inode_attrs(self):
        test_hi_and_lo_attributes(self.fs.open_inode(2), self)

    def test_inline_data_extracting(self):
        enable_incompat_feature(self.fs.sb, INCOMPAT_INLINE_DATA)
        root = self.fs.open_inode(2)
        root.block = test_data = b'test_data' + b'\x00'*51
        root.flags |= EXT4_INLINE_DATA_FL
        self.assertEqual(self.fs.extract_file_bytes(root), [test_data])

    def test_extent_data_extracting(self):
        disable_incompat_feature(self.fs.sb, INCOMPAT_INLINE_DATA)

        # read root directory
        root = self.fs.open_inode(2)
        data = list(self.fs.extract_file_bytes(root))[0]

        # check content stored at /
        self.assertTrue(b'lost+found' in data)
        self.assertTrue(b'file1' in data)
        self.assertTrue(b'file2' in data)
        self.assertTrue(b'file3' in data)
