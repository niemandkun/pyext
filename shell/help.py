from shell.messages import HELP


class Help:
    '''print help'''

    help = '''usage: help [command]
    Print help for command. If no arguments given, shows all
    available commands.
    '''

    def __init__(self, shell):
        self.shell = shell
        self.name = 'help'

    def process(self, command):
        args = command.split(' ')[1:]
        if len(args) != 1:
            self.__print_short_help()
        else:
            self.__print_long_help(args[0])

    def __print_long_help(self, unit):
        '''Print help reference for specified unit'''
        self.shell.invoke(lambda x: print(self.shell.units[x].help), unit)

    def __print_short_help(self):
        '''Print short help for each shell unit'''
        for u in self.shell.units:
            print(HELP.format(name=u, help=self.shell.units[u].__doc__))
        print(HELP.format(name='exit', help='close shell and exit'))
