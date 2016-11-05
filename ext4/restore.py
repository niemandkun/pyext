#!/usr/bin/env python3

import sys
from os import path
from math import ceil
from itertools import chain, groupby
from datetime import datetime

from ext4 import FileSystem
from ext4.utils import del_trailing_zeros
from ext4.structs import Inode, INODE_SIZE
from logger import Logger, LogType


INODE_FMT = '''crtime: {inode.crtime}
ctime: {inode.ctime}
atime: {inode.atime}
mtime: {inode.mtime}
flags: {inode.flags}
generation: {inode.generation}
version: {inode.version}
mode: {inode.mode}
block: {inode.block}
'''

DEFAULT_RESTORED_DIR = 'RESTORED'


# Map: {block_index -> [journal_block_indexes]}, where
# [jornal_block_indexes] is a list if indexes of block_index
# copies stored in journal.
# List is guaranteed to be sorted by actuality.
# (index of most recent copy goes first)
journal_map = {}


def print_inode(inode):
    '''OBSOLETE: Pretty print formatted inode data'''
    print(INODE_FMT.format(inode))


def inodes_are_relatives(ino1, ino2):
    '''Obsolete. Indicates that ino1 and ino2 is the same inode
    but found from different times.'''
    return ino1.ctime == ino2.ctime and \
            ino1.flags == ino2.flags and \
            ino1.mode == ino2.mode


def find_predecessors(journal, inode_block, inode_offset):
    '''Find in journal all saved non-zero copies of inode that
    was written to inode_block by inode_offset'''
    if inode_block not in journal_map:
        return

    for jrn_block in map(journal.read_block, journal_map[inode_block]):
        cmp_inode = Inode(jrn_block[inode_offset:inode_offset+INODE_SIZE])
        if cmp_inode.dtime == 0 and cmp_inode.ctime > 0:
            yield cmp_inode


def get_deleted_inodes(fs):
    '''Iterate over all inodes in fs and yield all deleted inodes'''
    for inode_index in range(fs.sb.inodes_count):
        inode = fs.open_inode(inode_index)
        if (inode.dtime != 0 or inode.links_count == 0) \
                and inode.block != b'\x00' * len(inode.block):
            yield inode_index, inode


def get_inode_params(fs, index):
    '''return inode addres, block and in block offset'''
    inode_address = fs.find_inode_addr(index)
    inode_block = inode_address // fs.sb.block_size
    inode_offset = inode_address % fs.sb.block_size
    return inode_address, inode_block, inode_offset


def try_restore_data(fs, inode, filename):
    '''Try extract data from <inode> and if data is not empty
    save it to <filename>'''
    data = b''.join(fs.extract_file_bytes(inode))
    if data:
        Logger.log('Restoring data...', LogType.info)
        with open(filename, 'wb') as f:
            f.write(del_trailing_zeros(data))
        Logger.log('Part of data restored to ' + filename, LogType.always)
    else:
        Logger.log('cannot restore data: inode is empty.', LogType.warning)


def restore_deleted_files(filesystem, restored_dir=DEFAULT_RESTORED_DIR):
    '''Restore recently deleted files from filesystem and push them
    to restore dir.'''
    global journal_map

    fs = filesystem
    Logger.log('Map filesystem to journal..', LogType.always)
    journal_map = fs.journal.create_journal_map()

    fileindex = 0
    for index, inode in get_deleted_inodes(fs):

        ino_addr, ino_block, ino_offset = get_inode_params(fs, index)
        Logger.log('Found deleted inode at ' + hex(ino_addr), LogType.always)
        predecessors = find_predecessors(fs.journal, ino_block, ino_offset)

        for restored_inode in predecessors:
            Logger.log('Found predecessor in journal!', LogType.info)
            filename = '{} - {}'.format(datetime.fromtimestamp(inode.dtime),
                                        str(fileindex))
            try_restore_data(fs, restored_inode,
                             path.join(restored_dir, filename))
            fileindex += 1
