from itertools import chain, groupby

from ext4.jstructs import *
from ext4.utils import chunk


class Journal:
    def __init__(self, jfs):
        self.fs = jfs
        self.sb = JournalSuperBlock(jfs[:J_SB_LENGTH])
        self.is64bit = self.sb.feature_incompat & JBD2_FEATURE_INCOMPAT_64BIT

        if self.sb.feature_incompat & JBD2_FEATURE_INCOMPAT_CSUM_V3:
            self.descriptor = JournalDescriptorV3
            self.descriptor_size = J_DESC_V3_LENGTH
        else:
            self.descriptor = JournalDescriptorV2
            self.descriptor_size = J_DESC_V2_LENGTH

    def get_blocks(self):
        return chunk(self.fs, self.sb.blocksize)

    def read_block(self, index):
        return self.fs[index*self.sb.blocksize:(index+1)*self.sb.blocksize]

    def create_journal_map(self):
        '''Return dict where key is a block index and value is a list
        of indexes of journal blocks which are the copies of this block.
        List of copies is ordered by sequence.'''

        journal_map = {}    # {sequence -> ([disc_indexes], [journal_indexes])}
        current_sequence = 0

        # need it to prevent bugs if journal was overwritten
        previous_blocktype = None

        for index, block in enumerate(self.get_blocks()):
            header = try_read_header(block)

            if header is None:
                # print(index, 'block is a backup copy')
                if previous_blocktype == BlockType.descriptor:
                    journal_map[current_sequence][1].append(index)
                # else:
                    # print('I dont want to add it to map')
                continue

            if header.blocktype == BlockType.commit_record:
                # print(index, 'block is a commit record')
                if previous_blocktype == BlockType.descriptor:
                    assert current_sequence == header.sequence
                    assert header.sequence in journal_map

            if header.sequence not in journal_map:
                journal_map[header.sequence] = [[], []]

            if header.blocktype == BlockType.descriptor:
                # print(index, 'block is a descriptor block')
                journal_map[header.sequence][0] += [x.blocknr for x in
                                                    self.__enum_descs(block)]
                current_sequence = header.sequence

            previous_blocktype = header.blocktype

        return chain_journal_map(journal_map)

    def __enum_descs(self, block):
        '''yields all descriptors from block'''
        offset = 0
        while True:
            start = J_HEADER_LENGTH + offset
            end = start + self.descriptor_size
            desc = self.descriptor(block[start:end], self.is64bit)
            yield desc

            offset += desc.actual_size
            if desc.flags & JournalDescFlags.last_tag:
                break


def chain_journal_map(journal_map):
    disc_blks = chain(*(x[0] for x in journal_map.values()))
    jrn_blks = chain(*(x[1] for x in journal_map.values()))

    sequence = dict((jrn_block, seq)
                    for seq in journal_map
                    for jrn_block in journal_map[seq][1])

    sort_func = lambda x: x[0]
    block_pairs = sorted(zip(disc_blks, jrn_blks), key=sort_func)
    return dict((disc_blk, sorted([jrn_blk for _, jrn_blk in jrn_blks],
                           key=lambda blk: sequence[blk], reverse=True))
                for disc_blk, jrn_blks in groupby(block_pairs, sort_func))


def try_read_header(journal_block):
    '''return None if cannot create correct header'''
    try:
        return JournalBlockHeader(journal_block[:J_HEADER_LENGTH])
    except AssertionError:
        return None
