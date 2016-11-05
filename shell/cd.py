import re
import os

from ext4.fsinfo import DirectoryInfo
from shell.messages import FILE_NOT_FOUND, IS_FILE


class Cd:
    '''change working directory'''

    help = '''usage: cd [directory]
    Change current working directory. If no arguments given,
    change working directory to /.
    '''

    def __init__(self, shell):
        self.shell = shell
        self.name = 'cd'
        self.command_re = re.compile(r'^cd *(?P<path>.*)$')

    def process(self, command):
        match = self.command_re.match(command)
        path = match.groupdict()['path']
        if not path:
            self.shell.pwd = '/'
            return
        if not path.startswith('/'):
            path = os.path.join(self.shell.pwd, path)
        self.__change_pwd(os.path.normpath(path))

    def __change_pwd(self, abspath):
        try:
            d = self.shell.fs.open(abspath, 'utf-8')
            if isinstance(d, DirectoryInfo):
                self.shell.pwd = abspath
            else:
                self.shell.print_error(IS_FILE.format(path=abspath))
        except FileNotFoundError as e:
            self.shell.print_error(FILE_NOT_FOUND.format(path=e.filename))
