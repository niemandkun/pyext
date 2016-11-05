import os
import mmap
from math import ceil

from ext4.structs import *
from ext4.consts import *
from ext4.journal import Journal
from ext4.utils import padded_with_zeroes, del_trailing_zeros, \
                       disassemble_path
from ext4.fsinfo import DirectoryInfo, FileInfo


class FileSystem:
    '''File System abstraction to operate ext4 image.'''
    def __init__(self, image_file):
        '''image_file -> file object with fileno() method'''
        self.image_file = image_file
        self.image = self.__create_mmap(image_file)
        self.sb = SuperBlock(self.read(GROUP_0_PADDING, SUPERBLOCK_SIZE))
        self.sb.last_mounted = self.sb.last_mounted.decode()
        self.size = self.sb.blocks_count * self.sb.block_size

    def __create_mmap(self, image_file):
        '''Create platform depended mmap object'''
        return mmap.mmap(image_file.fileno(), 0, access=mmap.ACCESS_READ)

    def __del__(self):
        '''Closes mmap and file with filesystem image'''
        self.image.close()
        self.image_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def is64(self):
        return self.sb.feature_incompat & INCOMPAT_64BIT

    @property
    def desc_size(self):
        return self.sb.desc_size if self.is64 else 32

    def open(self, path, encoding=None):
        '''Open file or directory as FileSystemInfo.'''
        path = disassemble_path(path)
        current_path = '/'

        current = self.__open_entry(2, '/', '.')
        for _next in filter(lambda x: x, path):
            _next_entry = [e for e in current.get_entries() if e.name == _next]
            if len(_next_entry) == 0:
                error = FileNotFoundError('Not found file or firectory!')
                error.filename = _next
                raise error
            e = _next_entry[0]
            current = self.__open_entry(e.inode, e.name,
                                        current_path, encoding)
            current_path = os.path.join(current_path, e.name)

        return current

    def open_descriptor(self, descriptor, encoding=None):
        '''Open file or directory as FileSystemInfo by its descriptor.'''
        inode = self.open_inode(descriptor)
        return self.__open_entry(descriptor, b'', b'', encoding=encoding)

    def __open_entry(self, inode_no, name, path, encoding=None):
        '''Open directory entry directly (without checking path)'''
        inode = self.open_inode(inode_no)
        try:
            data = self.extract_file_bytes(inode)
        except AssertionError:
            data = [b'']

        if inode.mode & S_IFLNK == S_IFLNK:
            return self.__open_symlink(inode, data, path, name, encoding)

        path = os.path.join(path, name)
        decode = None if encoding is None else lambda x: x.decode(encoding)

        def open_entry(inode, name, path):
            return self.__open_entry(inode, name, path)

        if inode.mode & S_IFDIR:
            return DirectoryInfo(data, inode, inode_no, path, open_entry)
        return FileInfo(data, inode, inode_no, path, decode)

    def __open_symlink(self, inode, data, path, name, encoding):
        '''Create fileinfo with path to symlink but resolved content'''
        real_path = del_trailing_zeros(b''.join(data)).decode()
        if not real_path.startswith('/'):
            real_path = os.path.join(path, real_path)
        fsinfo = self.open(real_path, encoding)
        fsinfo.path = os.path.join(path, name)
        return fsinfo

    def read(self, start, length):
        '''Read [length] bytes with offset [start] from self.image.'''
        return self.image[start:start+length]

    def read_blocks(self, start_block, length=1):
        '''Read [length] block(s) starting from [start_block].'''
        for i in range(length):
            start = (start_block + i) * self.sb.block_size
            yield self.image[start:start+self.sb.block_size]

    def open_inode(self, index):
        '''Find and open inode with specified index.'''
        start = self.find_inode_addr(index)
        data = self.read(start, self.sb.inode_size)
        return Inode(padded_with_zeroes(data, INODE_SIZE))

    def find_inode_addr(self, index):
        '''Find address of inode with specified index.'''
        group_index = (index - 1) // self.sb.inodes_per_group
        inode_index = (index - 1) % self.sb.inodes_per_group
        desc = self.open_group_desc(group_index)
        table_offset = desc.inode_table * self.sb.block_size
        inode_offset = inode_index * self.sb.inode_size
        return table_offset + inode_offset

    def open_group_desc(self, index):
        '''Find and open group descriptor with specified index.'''
        table = max(GROUP_0_PADDING + SUPERBLOCK_SIZE, self.sb.block_size)
        start = table + self.desc_size * index
        return GroupDescriptor(self.read(start, self.desc_size))

    def extract_file_bytes(self, inode):
        '''Find blocks where inode points and return iterable file bytes.'''
        if self.sb.feature_incompat & INCOMPAT_INLINE_DATA and \
                inode.flags & EXT4_INLINE_DATA_FL or \
                inode.mode & S_IFLNK == S_IFLNK:
            return [inode.block]
        else:
            return (block
                    for start, length
                    in self.read_extent_blocks(Extent(inode.block))
                    for block
                    in self.read_blocks(start, length))

    def read_extent_blocks(self, extent):
        '''Return iterable sequence of pairs, where first element is block
        number where file bytes are stored, second element is count of
        blocks in this segment.
        Sequence is already sorted by in-file blocks order.
        I.e., [(start, length), (start, length), ...]
        '''
        leafs = self.__find_extent_leafs(extent)
        leafs.sort(key=lambda e: e.block)
        return ((x.start, x.length) for x in leafs)

    def __find_extent_leafs(self, extent):
        '''Runs recursively through extent tree and collects leafs.'''
        if extent.header.depth == 0:
            return extent.entries

        leafs = (Extent(b''.join(self.read_blocks(e.leaf)))
                 for e in extent.entries)
        return [x for leaf in leafs
                for x in self.__find_extent_leafs(leaf)]

    @property
    def journal(self):
        if not hasattr(self, '_journal'):
            journal_inode = self.open_inode(self.sb.journal_inum)
            journal_bytes = b''.join(self.extract_file_bytes(journal_inode))
            self._journal = Journal(journal_bytes)
        return self._journal
