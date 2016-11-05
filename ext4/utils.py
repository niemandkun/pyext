import os
from math import ceil

from ext4.consts import S_IFDIR, S_IRUSR, S_IWUSR, S_IXUSR, S_IRGRP, \
                        S_IWGRP, S_IXGRP, S_IROTH, S_IWOTH, S_IXOTH


def format_file_mode(mode):
    '''Returns rwx-style string described file mode'''
    str_mode = ""
    str_mode += 'd' if mode & S_IFDIR else '-'

    str_mode += 'r' if mode & S_IRUSR else '-'
    str_mode += 'w' if mode & S_IWUSR else '-'
    str_mode += 'x' if mode & S_IXUSR else '-'

    str_mode += 'r' if mode & S_IRGRP else '-'
    str_mode += 'w' if mode & S_IWGRP else '-'
    str_mode += 'x' if mode & S_IXGRP else '-'

    str_mode += 'r' if mode & S_IROTH else '-'
    str_mode += 'w' if mode & S_IWOTH else '-'
    str_mode += 'x' if mode & S_IXOTH else '-'

    return str_mode


def format_file_mode_num(mode):
    '''Return octal-syle string described file mode'''
    num_mode = 0

    num_mode += 4 * 8**2 if mode & S_IRUSR else 0
    num_mode += 2 * 8**2 if mode & S_IWUSR else 0
    num_mode += 1 * 8**2 if mode & S_IXUSR else 0

    num_mode += 4 * 8 if mode & S_IRGRP else 0
    num_mode += 2 * 8 if mode & S_IWGRP else 0
    num_mode += 1 * 8 if mode & S_IXGRP else 0

    num_mode += 4 if mode & S_IROTH else 0
    num_mode += 2 if mode & S_IWOTH else 0
    num_mode += 1 if mode & S_IXOTH else 0

    return num_mode


def convert_ints_to_long(low, high):
    '''Low - lower bits of result, high - higher bits of result'''
    if low < 0:
        low += 2**32
    if high < 0:
        high += 2**32
    return low + (high << 32)


def padded_with_zeroes(data, length):
    '''Add zeros at the end of the data'''
    if len(data) > length:
        return data[:length]
    return data + b'\x00' * (length - len(data))


def del_trailing_zeros(data):
    '''Delete zeroes at the end of the data'''
    i = _find_trailing_zeros_index(data)
    if i == -1:
        return data
    return data[:i + 1]


def _find_trailing_zeros_index(data):
    for i in range(len(data) - 1, -1, -1):
        if data[i] != 0:
            return i
    return -1


def running_windows():
    '''True if current OS is MS Windows'''
    return os.name == 'nt'


def disassemble_path(full_path):
    '''yields parts of path'''
    if isinstance(full_path, bytes):
        full_path = full_path.decode()
    delimiter = '\\' if running_windows() else '/'
    path = os.path.normpath(full_path).split(delimiter)
    return (x for x in filter(bool, path))


def chunk(iterable, chunk_size):
    '''split iterable to chunks with specified size'''
    for x in range(ceil(len(iterable) / chunk_size)):
        yield iterable[x*chunk_size : (x+1)*chunk_size]
