# Pyext v0.0-prealpha2

Pyext allows to open Ext4 image, traverse directories tree and restore deleted files.
For more info about Ext4 see [Ext4 page](https://ext4.wiki.kernel.org/index.php)
at [Ext Wiki](https://ext4.wiki.kernel.org/index.php/Main_Page).

## Launch shell
Run in terminal: `python3 pyext.py PATH_TO_IMAGE` to launch shell.
You should have Python 3.4 or greater to be installed.
No additional dependencies are required.

To get help in pyext shell:
* Enter `help` to see a list of all available commands.
* Enter `help [command]` to get detailed help about command.

## Restore files

To restore deleted files run `python pyext.py --restore PATH_TO_IMAGE`.
To specify output directory where rescued files will be stored use
`--output PATH_TO_RESTORED` or `-o PATH_TO_RESTORED`.
All files that script can restore will be saved to this directory. Pyext can not restore original file name for deleted files, therefore it uses deletion time as filename. So, you can find your file content by the time when file was deleted from disk.

## Tests
To run tests enter in terminal: `python3 run_tests.py`
To check code coverage, you can use `coverage` tool:
```
coverage run run_tests.py
coverage report
```

## Shell commands
* __cd__ - change working directory
* __ls__ - print directory content
* __cat__ - print file content
* __stat__ - print filesystem or file info
* __help__ - print help
* __exit__ - close shell and exit

### cd
```
usage: cd [directory]
```
Change current working directory. If no arguments given,
change working directory to `/`.

### ls
```
usage: ls [directory]
```
List all entries in directory. Same as \*nix's `ls`.

### cat
```
usage: cat [file]
```
Print content of file. It will try to read file as utf-8 encoded by default. If it fails, file will be shown as a  byte stream.

### stat
```
usage: stat [file]
```
Print file status. If no arguments given, display file system info.

### help
```
usage: help [command]
```
Print help for command. If no arguments given, shows all
available commands.

### exit
```
usage: exit
```
Close pyext and return to system shell.
