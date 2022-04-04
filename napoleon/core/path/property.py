from pathlib import Path

from napoleon.properties import String
from napoleon.tools.singleton import Undefined


class FilePath(String):
    """
    Path field
    """

    def __init__(self, default=None, description=Undefined, nullable=True):
        super().__init__(
            default=Path(default) if isinstance(default, str) else default,
            description=description,
            nullable=nullable,
        )

    def to_primitive(self, value):
        return str(value)

    def from_primitive(self, value):
        return Path(value)

    def to_bytes(self, value):
        return str(value).encode()
