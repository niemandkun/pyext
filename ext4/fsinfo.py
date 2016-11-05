import os
from itertools import tee

from ext4.structs import DirectoryEntry
from ext4.consts import DIR_ENTRY_HEADER_SIZE
from ext4.utils import format_file_mode, del_trailing_zeros, \
                       running_windows


if not running_windows():
    import grp
    import pwd


class FileSystemInfo:
    ''' FileSytemInfo defines attributes common for DirectoryInfo
    and FileInfo. It is used as a parent class for DirInfo and FileInfo.
    '''
    def __init__(self, inode, path, inode_no):
        self.path = path
        self.inode_no = inode_no
        self.mode = inode.mode
        self.blocks = inode.blocks
        self.links = inode.links_count
        self.mode_str = format_file_mode(inode.mode)
        self.size = inode.size
        self.uid = inode.uid
        self.gid = inode.gid
        self.access_time = inode.atime
        self.mod_time = inode.mtime
        self.change_time = inode.ctime
        self.creation_time = inode.crtime
        self.extended_attrs = inode.file_acl

        if running_windows():
            self.owner = inode.uid
            self.group = inode.gid
            return

        try:
            self.owner = pwd.getpwuid(self.uid).pw_name
        except KeyError:
            self.owner = inode.uid
        try:
            self.group = grp.getgrgid(self.gid).gr_name
        except KeyError:
            self.group = inode.gid

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.name = os.path.split(self.path)[-1]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class DirectoryInfo(FileSystemInfo):
    '''Ext4 directory. It contains set of ext4.structs.DirectoryEntry.'''
    def __init__(self, data, inode, inode_no, path, open_entry):
        ''' open_entry(DirectoryEntry) -> FileInfo/DirectoryInfo '''
        super().__init__(inode, path, inode_no)
        self.__data_origin, self.__data = tee(data)
        self.__block = next(self.__data)
        self.__start = 0
        self.__open_entry = open_entry

    def get_all(self):
        '''Get all files from this directory.'''
        return [x for x in self.__create_fsinfo(self.__read_entries())]

    def get_files(self):
        '''Get all regular files from this directory.'''
        return [x for x in self.__create_fsinfo(self.__read_entries())
                if isinstance(x, FileInfo)]

    def get_directories(self):
        '''Get all directories from this directory.'''
        return [x for x in self.__create_fsinfo(self.__read_entries())
                if isinstance(x, DirectoryInfo)]

    def get_entries(self):
        '''Get all directory entries'''
        return self.__read_entries()

    def __getitem__(self, item):
        '''Get item from directory by filename'''
        items = [x for x in self.get_entries() if x.name == item]
        if len(items) >= 1:
            e = items[0]
            return self.__open_entry(e.inode, e.name, self.path)
        raise FileNotFoundError('{} not found'.format(item))

    def __read_entries(self):
        '''Returns generator of FileSystemInfos.'''
        self.__data_origin, data = tee(self.__data_origin)

        entries = []
        for block in data:
            start = 0
            while start < len(block):
                entry = self.__parse_entry(block, start)
                start += entry.rec_len
                entries.append(entry)

        return entries

    def __parse_entry(self, data, start):
        '''Parse DirectoryEntry struct beginning at [start] from [data].'''
        header_end = start + DIR_ENTRY_HEADER_SIZE
        entry = DirectoryEntry(data[start:header_end])
        entry.name = data[header_end:header_end+entry.name_len].decode()
        return entry

    def __create_fsinfo(self, entries):
        '''Returns generator to make fsinfo from each entry'''
        return (self.__open_entry(e.inode, e.name, self.path) for e in entries)

    def __iter__(self):
        return self

    def __next__(self):
        if self.__start == len(self.__block):
            try:
                self.__block = next(self.__data)
            except StopIteration:
                raise
            self.__start = 0
        entry = self.__parse_entry(self.__block, self.__start)
        self.__start += entry.rec_len
        return self.__open_entry(entry.inode, entry.name, self.path)

    def __str__(self):
        return "<DirectoryInfo: {path}>".format(path=self.path)


class FileInfo(FileSystemInfo):
    def __init__(self, data, inode, inode_no, path, decode=None):
        super().__init__(inode, path, inode_no)
        self.__data_origin, _ = tee(data)
        self.__decode = decode

    def __iter__(self):
        self.__data_origin, data = tee(self.__data_origin)
        if self.__decode is not None:
            return (line for block in data
                    for line
                    in self.__decode(del_trailing_zeros(block)).split('\n'))
        return (del_trailing_zeros(block) for block in data)

    def set_encoding(self, encoding):
        self.__decode = lambda x: x.decode(encoding)

    def unset_encoding(self):
        self.__decode = None

    def read(self):
        self.__data_origin, data = tee(self.__data_origin)
        content = del_trailing_zeros(b''.join(data))
        if self.__decode is not None:
            return self.__decode(content)
        else:
            return content

    def __str__(self):
        return "<FileInfo: {path}>".format(path=self.path)
