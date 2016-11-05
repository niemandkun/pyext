import unittest
from math import ceil

from ext4.structs import *
from ext4.consts import *
from ext4.tests.config import PATH_TO_IMAGE, IMAGE_SIZE, SUPERBLOCK_OFFSET, \
                              GROUP_DESC_OFFSET


def test_hi_and_lo_attributes(struct, asserter):
    for attr in struct.__dict__:
        if attr.endswith('_lo') or attr.endswith('_hi'):
            asserter.assertTrue(hasattr(struct, attr[:-3]))
        if attr.endswith('_lo'):
            asserter.assertTrue(hasattr(struct, attr[:-3] + '_hi'))
        if attr.endswith('_hi'):
            asserter.assertTrue(hasattr(struct, attr[:-3] + '_lo'))


class TestSuperBlock(unittest.TestCase):
    def setUp(self):
        with open(PATH_TO_IMAGE, 'rb') as fs:
            fs.seek(SUPERBLOCK_OFFSET)
            self.sb = SuperBlock(fs.read(1024))

    def test_sb_attrs(self):
        test_hi_and_lo_attributes(self.sb, self)

    def test_sb_attr_values(self):
        sb = self.sb
        # check magic signature:
        self.assertEqual(sb.magic, -4269)
        # check default block size:
        self.assertEqual(sb.block_size, 1024)
        # 10MB image should have 1024 * 10 blocks per 1024 bytes:
        self.assertEqual(sb.blocks_count, 1024 * 10)
        # traditional first non-reserved inode:
        self.assertEqual(sb.first_ino, 11)
        # inode size:
        self.assertEqual(sb.inode_size, 128)
        # not 64
        self.assertFalse(sb.feature_incompat & INCOMPAT_64BIT)

    def test_groups_count(self):
        sb = self.sb
        groups_count = ceil(sb.blocks_count / sb.blocks_per_group)
        self.assertEqual(sb.inodes_count, sb.inodes_per_group * groups_count)

    def test_image_size(self):
        sb = self.sb
        self.assertEqual(sb.block_size * sb.blocks_count, IMAGE_SIZE)

    def test_read_only(self):
        sb = self.sb
        self.assertTrue(sb.feature_ro_compat & RO_COMPAT_READONLY)


class TestGroupDescriptor(unittest.TestCase):
    def setUp(self):
        with open(PATH_TO_IMAGE, 'rb') as fs:
            fs.seek(GROUP_DESC_OFFSET)
            self.first = GroupDescriptor(fs.read(32))
            self.second = GroupDescriptor(fs.read(32))

    def test_gd_attrs(self):
        test_hi_and_lo_attributes(self.first, self)
        test_hi_and_lo_attributes(self.second, self)

    def test_gd_attr_values(self):
        first, second = self.first, self.second
        # should be 32 bit:
        self.assertFalse(first.is64 or second.is64)
        # checksum of descriptors:
        self.assertEqual(first.checksum, -31428)
        self.assertEqual(second.checksum, 18245)
        # I've created 5 dirs (root, dir1, dir2, dir3, lost+found), so
        # they should be there:
        self.assertEqual(first.used_dirs_count + second.used_dirs_count, 5)
