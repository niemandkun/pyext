#!/usr/bin/env python3

from argparse import ArgumentParser
from os import path, makedirs

from shell import Shell
from ext4 import FileSystem
from ext4.restore import restore_deleted_files, DEFAULT_RESTORED_DIR
from logger import Logger, LogType


APPLICATION = 'pyext'
VERSION = '0.0-prealpha2'

description = '''{application} {version} -
traverse ext4 filesystem and restore recently deleted files
'''

parser = ArgumentParser(description=description.format(application=APPLICATION,
                                                       version=VERSION))

parser.add_argument('image', metavar='SOURCE', type=str,
                    help='path to ext4 disk image')

parser.add_argument('--restore', action='store_true',
                    help='restore deleted files')

parser.add_argument('--output', '-o', type=str, default=DEFAULT_RESTORED_DIR,
                    help='path to restored files')

parser.add_argument('--version', action='version', version=VERSION)

parser.add_argument('--verbose', '-v', action='count')

if __name__ == '__main__':
    args = parser.parse_args()

    Logger.set_verbose(args.verbose)
    Logger.add_output(print)

    if not (path.exists(args.image) and path.isfile(args.image)):
        Logger.log('no such file: {}'.format(args.image), LogType.error)
        exit(1)

    with open(args.image, 'rb') as disk_image:
        fs = FileSystem(disk_image)
        if args.restore:
            if not path.exists(args.output):
                Logger.log(args.output + ' does not exist. I created it.',
                           LogType.warning)
                makedirs(args.output)
            restore_deleted_files(fs, args.output)

        else:
            shell = Shell(fs, APPLICATION, VERSION)
            shell.main()
