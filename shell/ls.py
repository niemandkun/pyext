import re
import os
from datetime import datetime

from ext4.fsinfo import DirectoryInfo
from shell.messages import FILE_NOT_FOUND, IS_FILE


FORMAT = '{mode} {links:>2} {owner} {group} {size:>6} {time} {name}'


class Ls:
    '''print directory content'''

    help = '''usage: ls [directory]
    List all entries in directory.
    '''

    def __init__(self, shell):
        self.shell = shell
        self.name = 'ls'
        self.command_re = re.compile(r'^ls *(?P<path>.*)$')

    def process(self, command):
        match = self.command_re.match(command)
        path = match.groupdict()['path']
        if path == '':
            path = self.shell.pwd
        if not path.startswith('/'):
            path = os.path.join(self.shell.pwd, path)
        self.__print_content(os.path.normpath(path))

    def __print_content(self, abspath):
        try:
            d = self.shell.fs.open(abspath, 'utf-8')
        except FileNotFoundError as e:
            self.shell.print_error(FILE_NOT_FOUND.format(path=e.filename))
            return

        if not isinstance(d, DirectoryInfo):
            self.shell.print_error(IS_FILE.format(path=abspath))
            return

        for entry in d:
            mod_time = datetime.fromtimestamp(entry.mod_time)
            print(FORMAT.format(mode=entry.mode_str, links=entry.links,
                                owner=entry.owner, group=entry.group,
                                size=entry.size, time=mod_time,
                                name=entry.name))
