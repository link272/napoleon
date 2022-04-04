import os
from pathlib import Path

from napoleon.core.path.property import FilePath
from napoleon.properties import AbstractObject, iter_properties


class BasePath(AbstractObject):

    root = FilePath(default=Path(__file__).parent.parent)
    templates = FilePath()
    data = FilePath(default=os.getcwd)
    temporary = FilePath(default="/tmp")
    log = FilePath()
    config = FilePath()

    def _build_internal(self):
        for key, prop in iter_properties(self.__class__):
            if isinstance(prop, FilePath):
                path = getattr(self, key)
                if path is not None and not path.exists():
                    path.mkdir(parents=True)
