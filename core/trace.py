from napoleon.properties import String, Integer, AbstractObject
from napoleon.core.paths import Paths, FilePath, Path

import logging
import logging.handlers


class Logger(AbstractObject):

    level: str = String("INFO", enum=["DEBUG", "INFO", "WARNING", "ERROR"])
    formatting: str = String("%(asctime)s :: %(levelname)s :: %(message)s")
    name: str = String("default")

    def _clean_internal(self):
        logger = logging.getLogger(self.name)
        while logger.hasHandlers():
            logger.removeHandler(logger.handlers[0])


class FileLogger(Logger):

    max_size_in_bytes: int = Integer(2097152)
    nb_backup: int = Integer(2)
    file_mode: str = String("w", enum=["w", "a"])
    filepath: Path = FilePath(lambda: Paths().log / Path("artemis.log"))

    def _build_internal(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        formatter = logging.Formatter(self.formatting)
        file_handler = logging.handlers.RotatingFileHandler(self.filepath, # noqa
                                                            self.file_mode,
                                                            self.max_size_in_bytes,
                                                            self.nb_backup)
        file_handler.setLevel(self.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


class StreamLogger(Logger):

    def _build_internal(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        formatter = logging.Formatter(self.formatting)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
