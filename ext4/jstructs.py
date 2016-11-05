from enum import IntEnum
import struct

from ext4.structs import ExtStruct
from cmapping.typedef import *
from cmapping.endianness import big_endian
from ext4.utils import convert_ints_to_long


JBD2_MAGIC = 0xC03B3998

J_HEADER_LENGTH = 12

J_SB_LENGTH = 1024
J_DESC_V2_LENGTH = 28
J_DESC_V3_LENGTH = 32
J_COMMIT_LENGTH = 32


JBD2_FEATURE_INCOMPAT_64BIT = 0x2
JBD2_FEATURE_INCOMPAT_CSUM_V2 = 0x8
JBD2_FEATURE_INCOMPAT_CSUM_V3 = 0x10


class BlockType(IntEnum):
    descriptor = 1
    commit_record = 2
    journal_sb_v1 = 3
    journal_sb_v2 = 4
    revocation_record = 5


class JournalDescFlags(IntEnum):
    escaped = 0x1
    uuid_omitted = 0x2
    data_deleted = 0x4
    last_tag = 0x8


class JournalBlockHeader(ExtStruct):
    endianness = big_endian
    magic = UnsignedInteger()
    blocktype = Integer()
    sequence = Integer()

    def __init__(self, data):
        super().__init__(data, J_HEADER_LENGTH)
        assert self.magic == JBD2_MAGIC
        self.blocktype = BlockType(self.blocktype)


class JournalStruct(ExtStruct):
    endianness = big_endian
    header = CString(12)

    def __init__(self, data, length=None):
        super().__init__(data, length)
        self.header = JournalBlockHeader(self.header)


class JournalSuperBlock(JournalStruct):
    blocksize = Integer()
    maxlen = Integer()
    first = Integer()
    sequence = Integer()
    start = Integer()
    errno = Integer()
    feature_compat = Integer()
    feature_incompat = Integer()
    feature_ro_compat = Integer()
    uuid = CString(16)
    nr_users = Integer()
    dynsuper = Integer()
    max_transaction = Integer()
    max_trans_data = Integer()
    checksum_type = UnsignedChar()
    padding = Padding(3 + 42 * 4)
    checksum = Integer()
    users = UnsignedChar(16*48)

    def __init__(self, data):
        super().__init__(data, J_SB_LENGTH)


class JournalDescriptorV3:
    '''Use if JDB_FEATURE_INCOMPAT_CSUM_V3 is set.'''
    def __init__(self, data, is64bit):
        self.actual_size = 16
        blocknr_lo, self.flags, blocknr_hi, self.checksum = \
        struct.unpack('>4i', data[:self.actual_size])

        self.blocknr = convert_ints_to_long(blocknr_lo, blocknr_hi)

        if not self.flags & JournalDescFlags.uuid_omitted:
            start = self.actual_size
            self.actual_size += 16
            uuid = struct.unpack('>16s', data[start:self.actual_size])[0]


class JournalDescriptorV2:
    '''Use if JDB_FEATURE_INCOMPAT_CSUM_V3 is NOT set.'''
    def __init__(self, data, is64bit):
        self.actual_size = 8
        self.blocknr, self.checksum, \
        self.flags = struct.unpack('>ihh', data[:self.actual_size])

        if is64bit:
            start = self.actual_size
            self.actual_size += 4
            blocknr_hi = struct.unpack('>i', data[start:self.actual_size])[0]
            self.blocknr = convert_ints_to_long(self.blocknr, blocknr_hi)

        if not self.flags & JournalDescFlags.uuid_omitted:
            start = self.actual_size
            self.actual_size += 16
            self.uuid = struct.unpack('>16s', data[start:self.actual_size])[0]


class JournalCommitBlock(JournalStruct):
    chksum_type = UnsignedChar()
    chksum_size = UnsignedChar()
    padding = Padding(2)
    chksum = CString(28)
    commit_sec = Long()
    commit_nsec = Integer()

    def __init__(self, data):
        super().__init__(data, J_COMMIT_LENGTH)
