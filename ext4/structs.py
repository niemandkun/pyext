#!/usr/bin/env python3

import struct

from ext4.consts import *
from ext4.utils import convert_ints_to_long

from cmapping import CStruct
from cmapping.endianness import little_endian
from cmapping.typedef import *


class ExtStruct(CStruct):
    '''Base for ext4 structures. It can resolve two fields with same name
    that end with '_ho' and '_lo' and create one without suffix filled
    with correct value.
    '''
    def __init__(self, data, length=None):
        if length is not None and len(data) != length:
            raise ValueError('Expected {} bytes.'.format(length))

        super().__init__(data)
        self.resolve_long_data()

    def resolve_long_data(self):
        '''Finds attrs with same name that end with '_ho' and '_lo' and
        create one without suffix filled with correct value.
        '''
        lo_attrs = (x for x in dir(self) if x.endswith('lo'))
        for lo_attr in lo_attrs:
            self.join_attrs(lo_attr, lo_attr[:-2] + 'hi')

    def join_attrs(self, lo_attr, hi_attr):
        ''' Merge attrs ended with '_ho' and '_lo' into one '''
        low = getattr(self, lo_attr)
        if hasattr(self, hi_attr):
            high = getattr(self, hi_attr)
            setattr(self, lo_attr[:-3], convert_ints_to_long(low, high))
        else:
            setattr(self, lo_attr[:-3], low)


class SuperBlock(ExtStruct):
    ''' The superblock records various information about the enclosing
    filesystem, such as block counts, inode counts, supported features,
    maintenance information, and more.
    :param data: 1024 bytes long
    '''
    endianness = little_endian

    inodes_count = Integer()
    blocks_count_lo = Integer()
    r_blocks_count_lo = Integer()
    free_blocks_count_lo = Integer()
    free_inodes_count = Integer()
    first_data_block = Integer()
    log_block_size = Integer()
    log_cluster_size = Integer()
    blocks_per_group = Integer()
    clusters_per_group = Integer()
    inodes_per_group = Integer()
    mtime = Integer()
    wtime = Integer()
    mnt_count = Short()
    max_mnt_count = Short()
    magic = Short()
    state = Short()
    errors = Short()
    minor_rev_level = Short()
    lastcheck = Integer()
    checkinterval = Integer()
    creator_os = Integer()
    rev_level = Integer()
    def_resuid = Short()
    def_resgid = Short()
    first_ino = Integer()
    inode_size = Short()
    block_group_nr = Short()
    feature_compat = Integer()
    feature_incompat = Integer()
    feature_ro_compat = Integer()
    uuid = CString(16)
    volume_name = CString(16)
    last_mounted = CString(64)
    algorithm_usage_bitmap = Integer()
    prealloc_blocks = UnsignedChar()
    prealloc_dir_blocks = UnsignedChar()
    reserved_gdt_blocks = Short()
    journal_uuid = CString(16)
    journal_inum = Integer()
    journal_dev = Integer()
    last_orphan = Integer()
    hash_seed = Integer(4)
    def_hash_version = UnsignedChar()
    jnl_backup_type = UnsignedChar()
    desc_size = Short()
    default_mount_opts = Integer()
    first_meta_bg = Integer()
    mkfs_time = Integer()
    jnl_blocks = Integer(17)
    blocks_count_hi = Integer()
    r_blocks_count_hi = Integer()
    free_blocks_count_hi = Integer()
    min_extra_isize = Short()
    want_extra_isize = Short()
    flags = Integer()
    raid_stride = Short()
    mmp_interval = Short()
    mmp_block = LongLong()
    raid_stripe_width = Integer()
    log_groups_per_flex = UnsignedChar()
    checksum_type = UnsignedChar()
    reserved_pad = Short()
    kbytes_written = LongLong()
    snapshot_inum = Integer()
    snapshot_id = Integer()
    snapshot_r_blocks_count = LongLong()
    snapshot_list = Integer()
    error_count = Integer()
    first_error_time = Integer()
    first_error_ino = Integer()
    first_error_block = LongLong()
    first_error_func = CString(32)
    first_error_line = Integer()
    last_error_time = Integer()
    last_error_ino = Integer()
    last_error_line = Integer()
    last_error_block = LongLong()
    last_error_func = CString(32)
    mount_opts = CString(64)
    usr_quota_inum = Integer()
    grp_quota_inum = Integer()
    overhead_blocks = Integer()
    backup_bgs = UnsignedChar(2)
    encrypt_algos = UnsignedChar(4)
    reserved = Padding(426)
    checksum = Integer()

    def __init__(self, data):
        super().__init__(data, SUPERBLOCK_SIZE)
        assert self.magic == SUPERBLOCK_MAGIC
        self.block_size = 2 ** (10 + self.log_block_size)
        self.cluster_size = 2 ** self.log_cluster_size


class GroupDescriptor(ExtStruct):
    '''Each block group on the filesystem has one of these
    descriptors associated with it.
    :param data: 32 or 64 bytes long
    '''
    endianness = little_endian

    # 32x-descriptor
    block_bitmap_lo = Integer()
    inode_bitmap_lo = Integer()
    inode_table_lo = Integer()
    free_blocks_count_lo = Short()
    free_inodes_count_lo = Short()
    used_dirs_count_lo = Short()
    flags = Short()
    exclude_bitmap_lo = Integer()
    block_bitmap_csum_lo = Short()
    inode_bitmap_csum_lo = Short()
    itable_unused_lo = Short()
    checksum = Short()

    # 64x-descriptor
    block_bitmap_hi = Integer()
    inode_bitmap_hi = Integer()
    inode_table_hi = Integer()
    free_blocks_count_hi = Short()
    free_inodes_count_hi = Short()
    used_dirs_count_hi = Short()
    itable_unused_hi = Short()
    exclude_bitmap_hi = Integer()
    block_bitmap_csum_hi = Short()
    inode_bitmap_csum_hi = Short()
    reserved = Padding(4)

    def __init__(self, data):
        if len(data) == GROUP_DESC_32_SIZE:
            super().__init__(data + b'\x00' * 32)
            self.is64 = False
        elif len(data) == GROUP_DESC_64_SIZE:
            super().__init__(data)
            self.is64 = True
        else:
            raise ValueError("Data should be 32 or 64 bytes long.")


class Inode(ExtStruct):
    ''' Inode stores all the metadata pertaining to the file
    (time stamps, block maps, extended attributes, etc), not the
    directory entry.
    :param data: 256 bytes long
    '''
    endianness = little_endian

    mode = Short()
    uid_lo = Short()
    size_lo = Integer()
    atime = Integer()
    ctime = Integer()
    mtime = Integer()
    dtime = Integer()
    gid_lo = Short()
    links_count = Short()
    blocks_lo = Integer()
    flags = Integer()
    version_lo = Integer()
    block = CString(60)
    generation = Integer()
    file_acl_lo = Integer()
    size_hi = Integer()
    obso_faddr = Integer()
    blocks_hi = Short()
    file_acl_hi = Short()
    uid_hi = Short()
    gid_hi = Short()
    checksum_lo = Short()
    reserved = Short()
    extra_isize = Short()
    checksum_hi = Short()
    ctime_extra = Integer()
    mtime_extra = Integer()
    atime_extra = Integer()
    crtime = Integer()
    crtime_extra = Integer()
    version_hi = Integer()

    def __init__(self, data):
        super().__init__(data, INODE_SIZE)


class ExtentHeader(ExtStruct):
    ''' The extent tree header.
    :param data: 12 bytes long
    '''
    endianness = little_endian

    magic = Short()
    entries = Short()
    max_entries = Short()
    depth = Short()
    generation = Integer()

    def __init__(self, data):
        super().__init__(data, EXTENT_HEADER_SIZE)
        assert self.magic == EXTENT_MAGIC


class ExtentLeaf(ExtStruct):
    ''' Leaf nodes of the extent tree.
    :param data: 12 bytes long
    '''
    endianness = little_endian

    block = Integer()
    length = Short()
    start_hi = Short()
    start_lo = Integer()

    def __init__(self, data):
        super().__init__(data, EXTENT_SIZE)
        if self.length > 32768:
            # then extent is uninitialized and the actual length is:
            self.length = self.length - 32768

    def __str__(self):
        return '<ExtentLeaf: at {s.start} - {s.length} blocks>'.format(s=self)


class ExtentBranch(ExtStruct):
    ''' Internal nodes of the extent tree, also known as index nodes.
    :param data: 12 bytes long
    '''
    endianness = little_endian

    block = Integer()
    leaf_lo = Integer()
    leaf_hi = Short()
    unused = Padding(2)

    def __init__(self, data):
        super().__init__(data, EXTENT_IDX_SIZE)

    def __str__(self):
        return '<ExtentBranch: leaf at {s.leaf}>'.format(s=self)


class ExtentTail(ExtStruct):
    ''' Extent tail containing checksum
    :param data: 4 bytes long (one little endian int32)
    '''
    endianness = little_endian
    checksum = Integer()

    def __init__(self, data):
        super().__init__(data, EXTENT_TAIL_SIZE)


class Extent:
    ''' Full extent structure, contains ExtentHeader, [header.entries]
    number of entries and ExtentTail.
    Entries are instances of ExtentLeaf if header.depth == 0, else
    they are ExtentBranches.
    :param data: at least 26 bytes long
    '''
    def __init__(self, data):
        self.check_data(data)
        self.header = ExtentHeader(data[:EXTENT_HEADER_SIZE])
        self.entries = [self.parse_entry(data, i)
                        for i in range(self.header.entries)]

    def parse_entry(self, data, index):
        offset = EXTENT_SIZE * (index + 1)
        if self.header.depth == 0:
            return ExtentLeaf(data[offset:offset+EXTENT_SIZE])
        return ExtentBranch(data[offset:offset+EXTENT_SIZE])

    def __getitem__(self, index):
        return self.entries[index]

    def check_data(self, data):
        if len(data) < EXTENT_HEADER_SIZE + EXTENT_SIZE + EXTENT_TAIL_SIZE:
            raise ValueError('Data is too short!')


class Directory:
    ''' Ext4 directory. It contains set of entries. '''
    def __init__(self, data):
        self.entries = set()
        start = 0
        while start < len(data):
            entry = self.parse_entry(data, start)
            self.entries.add(entry)
            start += entry.rec_len

    def parse_entry(self, data, start):
        header = DIR_ENTRY_HEADER_SIZE
        entry = DirectoryEntry(data[start:end+header])
        entry.name = data[start+header:start+header+entry.name_len]
        return entry


class DirectoryEntry(ExtStruct):
    ''' Struct of new format for directory entry with file type.
    To find out file type see enum FileType in ext4.consts.
    This structure does not contain name, though you'll need to parse it
    by you own hands for sure.
    '''
    inode = Integer()
    rec_len = Short()
    name_len = UnsignedChar()
    file_type = UnsignedChar()

    def __init__(self, data):
        super().__init__(data, DIR_ENTRY_HEADER_SIZE)


class DirectoryEntryTail(DirectoryEntry):
    ''' Regular directory entry, but most of the fields are set to 0.
    It stores checksum instead of name. '''
    checksum = Integer()

    def __init__(self, data):
        super(DirectoryEntry).__init__(data, DIR_ENTRY_TAIL_SIZE)
        assert self.inode == 0
        assert self.rec_len == DIR_ENTRY_TAIL_SIZE
        assert self.name_len == 0
        assert self.file_type == DIR_ENTRY_TAIL_MAGIC
