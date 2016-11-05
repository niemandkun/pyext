# Ext4 constants.
# See official ext4 layout wiki page at
# https://ext4.wiki.kernel.org/index.php/Ext4_Disk_Layout
# for more info.

from enum import IntEnum


GROUP_0_PADDING = 1024

''' Magic numbers '''
SUPERBLOCK_MAGIC = -4269    # b'\x53\xEF'
EXTENT_MAGIC = -3318    # b'\x0A\xF3'

''' Struct sizes '''
SUPERBLOCK_SIZE = 1024
GROUP_DESC_32_SIZE = 32
GROUP_DESC_64_SIZE = 64
INODE_SIZE = 156
EXTENT_HEADER_SIZE = 12
EXTENT_IDX_SIZE = 12
EXTENT_SIZE = 12
EXTENT_TAIL_SIZE = 4
DIR_ENTRY_HEADER_SIZE = 8
DIR_ENTRY_TAIL_SIZE = 12
DIR_ENTRY_TAIL_MAGIC = 222    # b'\xDE'


class FileType(IntEnum):
    ''' Describes file type, which can be found in
    directory or inode entry
    '''
    unknown = 0x0
    regular = 0x1
    directory = 0x2
    char_dev = 0x3
    block_dev = 0x4
    fifo = 0x5
    socket = 0x6
    symlink = 0x7


''' Inode flags '''

EXT4_SECRM_FL = 0x1
EXT4_UNRM_FL = 0x2
EXT4_COMPR_FL = 0x4
EXT4_SYNC_FL = 0x8
EXT4_IMMUTABLE_FL = 0x10
EXT4_APPEND_FL = 0x20
EXT4_NODUMP_FL = 0x40
EXT4_NOATIME_FL = 0x80
EXT4_DIRTY_FL = 0x100
EXT4_COMPRBLK_FL = 0x200
EXT4_NOCOMPR_FL = 0x400
EXT4_ENCRYPT_FL = 0x800
EXT4_INDEX_FL = 0x1000
EXT4_IMAGIC_FL = 0x2000
EXT4_JOURNAL_DATA_FL = 0x4000
EXT4_NOTAIL_FL = 0x8000
EXT4_DIRSYNC_FL = 0x10000
EXT4_TOPDIR_FL = 0x20000
EXT4_HUGE_FILE_FL = 0x40000
EXT4_EXTENTS_FL = 0x80000
EXT4_EA_INODE_FL = 0x200000
EXT4_EOFBLOCKS_FL = 0x400000
EXT4_SNAPFILE_FL = 0x01000000
EXT4_SNAPFILE_DELETED_FL = 0x04000000
EXT4_SNAPFILE_SHRUNK_FL = 0x08000000
EXT4_INLINE_DATA_FL = 0x10000000
EXT4_RESERVED_FL = 0x80000000


''' Inode mode '''

S_IXOTH = 0x1       # Others may execute
S_IWOTH = 0x2       # Others may write
S_IROTH = 0x4       # Others may read
S_IXGRP = 0x8       # Group members may execute
S_IWGRP = 0x10      # Group members may write
S_IRGRP = 0x20      # Group members may read
S_IXUSR = 0x40      # Owner may execute
S_IWUSR = 0x80      # Owner may write
S_IRUSR = 0x100     # Owner may read
S_ISVTX = 0x200     # Sticky bit
S_ISGID = 0x400     # Set GID
S_ISUID = 0x800     # Set UID

S_IFIFO = 0x1000    # FIFO
S_IFCHR = 0x2000    # Character device
S_IFDIR = 0x4000    # Directory
S_IFBLK = 0x6000    # Block device
S_IFREG = 0x8000    # Regular file
S_IFLNK = 0xA000    # Symbolic link
S_IFSOCK = 0xC000   # Socket


''' Ext4 compatible feature set flags '''

# Directory preallocation.
COMPAT_DIR_PREALLOC = 0x1

# Not clear from the code what this does.
COMPAT_IMAGIC_INODES = 0x2

# Has a journal.
COMPAT_HAS_JOURNAL = 0x4

# Supports extended attributes.
COMPAT_EXT_ATTR = 0x8

# Has reserved GDT blocks for filesystem
# expansion.
COMPAT_RESIZE_INODE = 0x10

# Has directory indices.
COMPAT_DIR_INDEX = 0x20

# Not in Linux kernel.
COMPAT_LAZY_BG = 0x40

# Not used.
COMPAT_EXCLUDE_INODE = 0x80

# Seems to be used to indicate the presence of snapshot-related
# exclude bitmaps.
COMPAT_EXCLUDE_BITMAP = 0x100

# If set, sb->s_backup_bgs points to the two block groups that
# contain backup superblocks.
COMPAT_SPARSE_SUPER2 = 0x200


''' Ext4 incompatible feature set '''

# Compression.
INCOMPAT_COMPRESSION = 0x1

# Directory entries record the file type.
INCOMPAT_FILETYPE = 0x2

# Filesystem needs recovery.
INCOMPAT_RECOVER = 0x4

# Filesystem has a separate journal device.
INCOMPAT_JOURNAL_DEV = 0x8

# Meta block groups.
INCOMPAT_META_BG = 0x10

# Files in this filesystem use extents.
INCOMPAT_EXTENTS = 0x40

# Enable a filesystem size of 2^64 blocks.
INCOMPAT_64BIT = 0x80

# Multiple mount protection. Not implemented.
INCOMPAT_MMP = 0x100

# Flexible block groups.
INCOMPAT_FLEX_BG = 0x200

# Inodes can be used for extended attributes.
INCOMPAT_EA_INODE = 0x400

# Data in directory entry.
INCOMPAT_DIRDATA = 0x1000

# Never used.
INCOMPAT_BG_USE_META_CSUM = 0x2000

# Large directory >2GB or 3-level htree.
INCOMPAT_LARGEDIR = 0x4000

# Data in inode.
INCOMPAT_INLINE_DATA = 0x8000

# There are encrypted inodes.
INCOMPAT_ENCRYPT = 0x10000


''' Ext4 readonly-compatible feature set '''

# Sparse superblocks.
RO_COMPAT_SPARSE_SUPER = 0x1

# This filesystem has been used to store a file greater than 2GiB.
RO_COMPAT_LARGE_FILE = 0x2

# Not used in kernel or e2fsprogs.
RO_COMPAT_BTREE_DIR = 0x4

# This filesystem has files whose sizes are represented in units
# of logical blocks, not 512-byte sectors.
# This implies a very large file indeed!
RO_COMPAT_HUGE_FILE = 0x8


# Group descriptors have checksums. In addition to detecting
# corruption, this is useful for lazy formatting with
# uninitialized groups.
RO_COMPAT_GDT_CSUM = 0x10

# Indicates that the old ext3 32,000 subdirectory limit no longer applies.
RO_COMPAT_DIR_NLINK = 0x20

# Indicates that large inodes exist on this filesystem.
RO_COMPAT_EXTRA_ISIZE = 0x40

# This filesystem has a snapshot.
RO_COMPAT_HAS_SNAPSHOT = 0x80

# Quota.
RO_COMPAT_QUOTA = 0x100

# This filesystem supports "bigalloc".
RO_COMPAT_BIGALLOC = 0x200

# This filesystem supports metadata checksumming.
RO_COMPAT_METADATA_CSUM = 0x400

# Filesystem supports replicas.
RO_COMPAT_REPLICA = 0x800

# Read-only filesystem image.
RO_COMPAT_READONLY = 0x1000
