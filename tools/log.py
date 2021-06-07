class PrintLogger: # noqa

    def debug(self, msg): # noqa
        print(f"DEBUG: {msg}")

    def info(self, msg): # noqa
        print(f"INFO: {msg}")

    def warning(self, msg): # noqa
        print(f"WARNING: {msg}")

    def error(self, msg, exc_info=None): # noqa
        print(f"ERROR: {msg}")


LOGGERS = dict()
