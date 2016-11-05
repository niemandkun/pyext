from ext4 import FileSystem
from shell.messages import WELCOME, COMMAND_NOT_FOUND, PROMPT
from shell.cat import Cat
from shell.cd import Cd
from shell.ls import Ls
from shell.stat import Stat
from shell.help import Help
from logger import Logger, LogType


START_DIR = '/'
APP = 'shell'
VERSION = '0.0'
UNITS = [Cat, Cd, Ls, Stat, Help]


class Shell:
    '''Simple command shell to handle user input.
    To create shell subroutine you should define class
    with methods: `process(self, command)` and `__init__(self, shell)`
    and then add it to SUBROUTINES. See `Echo` for example.
    '''
    def __init__(self, filesystem, application=None, version=None):
        self.fs = filesystem
        self.pwd = START_DIR
        self.app = application if application else APP
        self.version = version if version else VERSION
        self.units = {x.name: x for x in map(lambda x: x(self), UNITS)}
        print(WELCOME.format(app=self.app, version=self.version))

    def update_prompt(self):
        '''Render prompt message according to PROMPT format.'''
        self.prompt = PROMPT.format(app=self.app, path=self.pwd)

    def main(self):
        '''Application main cycle.'''
        command = None
        while command != 'exit':
            Logger.log('Got command: {}'.format(command), LogType.info)
            self.__resolve(command)
            self.update_prompt()
            try:
                command = input(self.prompt)
            except EOFError:
                Logger.log('Got EOF. Exiting...', LogType.info)
                break

    def __resolve(self, command):
        '''Decide what to do with command'''
        if not command:
            Logger.log('command is empty. Skip it.', LogType.warning)
            return
        self.__run(command)

    def __run(self, command):
        '''Try to process command with unit corresponding to first
        command field.
        '''
        self.invoke(lambda x: self.units[x].process(command),
                    command.split(' ')[0])

    def invoke(self, function, unit):
        '''run function(unit) if program exists'''
        if unit in self.units:
            function(unit)
        else:
            print(COMMAND_NOT_FOUND.format(command=unit))

    def print_error(self, message):
        Logger.log(message, LogType.error)
        print('error: {}'.format(message))
