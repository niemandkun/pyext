import re
import os

from ext4.fsinfo import FileInfo
from shell.messages import FILE_NOT_FOUND, IS_DIRECTORY, MISSING_OPERAND


class Cat:
    '''print file content'''

    help = '''usage: cat [file]
    Print content of file.
    '''

    def __init__(self, shell):
        self.shell = shell
        self.name = 'cat'
        self.command_re = re.compile(r'^cat *(?P<path>.*)$')

    def process(self, command):
        match = self.command_re.match(command)
        path = match.groupdict()['path']

        if not path:
            self.shell.print_error(MISSING_OPERAND)
            return

        if not path.startswith('/'):
            path = os.path.join(self.shell.pwd, path)

        target = self.__open_file(path, 'utf-8')
        if not target:
            return

        try:
            print(target.read())
        except UnicodeDecodeError:
            target = self.__open_file(path, None)
            print(target.read())

    def __open_file(self, path, encoding):
        try:
            f = self.shell.fs.open(path, encoding)
        except FileNotFoundError as e:
            self.shell.print_error(FILE_NOT_FOUND.format(path=e.filename))
            return None

        if not isinstance(f, FileInfo):
            self.shell.print_error(IS_DIRECTORY.format(path=path))
            return None

        return f
