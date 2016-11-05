from enum import IntEnum


class LogType(IntEnum):
    critical = 0
    error = 1
    warning = 2
    info = 3
    always = -1


class Logger:
    __verbose = 0
    __loggers = []

    @classmethod
    def add_output(cls, output_func):
        cls.__loggers.append(output_func)

    @classmethod
    def set_verbose(cls, verbose_level):
        if verbose_level is None:
            verbose_level = 0
        cls.__verbose = verbose_level

    @classmethod
    def log(cls, message, message_type=LogType.info):
        if cls.__verbose >= int(message_type) - 1:
            message = cls.__add_prefix(message, message_type)
            for logger in cls.__loggers:
                logger(message)

    @classmethod
    def __add_prefix(cls, message, message_type):
        prefix = ''
        if message_type == LogType.critical:
            prefix = 'CRITICAL ERROR: '
        elif message_type == LogType.error:
            prefix = 'Error: '
        elif message_type == LogType.warning:
            prefix = 'Warning: '
        return prefix + message
