import logging
import logging.handlers
from pathlib import Path

from napoleon.core.log.base import BaseLogger
from napoleon.core.path.property import FilePath
from napoleon.core.shared.application import Application
from napoleon.properties import String, Integer


class FileLogger(BaseLogger):
    """File logger"""

    max_size_in_bytes: int = Integer(default=2097152)
    nb_backup: int = Integer(default=2)
    file_mode: str = String(default="w", enum=["w", "a"])
    filepath: Path = FilePath(lambda: Application().paths.log / Path("napoleon.log"))

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


class StreamLogger(BaseLogger):
    """Console logger"""

    def _build_internal(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        formatter = logging.Formatter(self.formatting)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
