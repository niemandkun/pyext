import re
import os
from datetime import datetime

from shell.messages import MISSING_OPERAND, FILE_NOT_FOUND
from ext4.utils import format_file_mode_num


FORMAT = '''File: `{f.name}`
Size: {f.size}\tBlocks: {f.blocks}
Inode: {f.inode_no}\tLinks: {f.links}
Access: ({mode_oct}/{f.mode_str})\t\
Uid: ( {f.uid}/{f.owner})\tGid: ( {f.gid}/{f.group})
Access: {access_time}
Modify: {mod_time}
Change: {change_time}
Birth: {creation_time}\
'''

FS_FORMAT = '''Filesystem: `ext4-{sb.rev_level}.{sb.minor_rev_level}`

/// FILESYSTEM ///
UUID: {sb.uuid}
Label: {sb.volume_name}
Last mounted at: {sb.last_mounted}
Last mount time: {mtime}
Last write time: {wtime}
Last check: {lastcheck}
Number of mounts since the last fsck: {sb.mnt_count}
Max number of mounts without fsck: {sb.max_mnt_count}
Size: {size} bytes\t\
KiB written: {sb.kbytes_written}\t\
Errors seen: {sb.error_count}

/// BLOCKS ///
Total blocks: {sb.blocks_count}\t\
Free blocks: {sb.free_blocks_count}\t\
Reserved blocks: {sb.r_blocks_count}
Block size: {sb.block_size} bytes\t\
Cluster size: {sb.cluster_size} blocks

/// INODES ///
Total inodes: {sb.inodes_count}\t\
Free inodes: {sb.free_inodes_count}
Inode size: {sb.inode_size} bytes\t\
First non-reserved inode: {sb.first_ino}

/// GROUP DESCRIPTORS ///
Blocks per group: {sb.blocks_per_group}\t\
Clusters per group: {sb.clusters_per_group}
Inodes per group: {sb.inodes_per_group}\t\
Descriptor size: {desc_size} bytes
'''


class Stat:
    '''print filesystem info'''

    help = '''usage: stat [file]
    Print file status. If no arguments given, display filesystem info.
    '''

    def __init__(self, shell):
        self.shell = shell
        self.name = 'stat'
        self.command_re = re.compile(r'^stat *(?P<path>.*)$')

    def process(self, command):
        match = self.command_re.match(command)
        path = match.groupdict()['path']

        if not path:
            self.__print_fs_stat()
            return

        if not path.startswith('/'):
            path = os.path.join(self.shell.pwd, path)

        self.__print_file_stat(path)

    def __print_file_stat(self, abspath):
        try:
            with self.shell.fs.open(abspath, 'utf-8') as f:
                mode_oct = oct(format_file_mode_num(f.mode))
                access_time = datetime.fromtimestamp(f.access_time)
                mod_time = datetime.fromtimestamp(f.mod_time)
                change_time = datetime.fromtimestamp(f.change_time)
                creation_time = datetime.fromtimestamp(f.creation_time)
                print(FORMAT.format(**locals()))
        except FileNotFoundError as e:
            self.shell.print_error(FILE_NOT_FOUND.format(path=e.filename))

    def __print_fs_stat(self):
        fs = self.shell.fs
        mtime = datetime.fromtimestamp(fs.sb.mtime)
        wtime = datetime.fromtimestamp(fs.sb.wtime)
        lastcheck = datetime.fromtimestamp(fs.sb.lastcheck)
        print(FS_FORMAT.format(sb=fs.sb, desc_size=fs.desc_size,
                               size=fs.size, **locals()))
