import sys


class _Log:
    @staticmethod
    def info(msg):
        print(msg, file=sys.stderr)

    @staticmethod
    def error(msg):
        print(msg, file=sys.stderr)

    @staticmethod
    def debug(msg):
        print(msg, file=sys.stderr)


log = _Log()
