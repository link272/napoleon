from napoleon.properties import String
from napoleon.tools.singleton import Nothing, Intrinsic, Undefined

from pathlib import Path


class FilePath(String):

    _type = Path

    def __init__(self, default=Intrinsic, description=Undefined, nullable=False):
        default = Path(default) if isinstance(default, str) else default
        super().__init__(
            default=default,
            description=description,
            nullable=nullable,
        )

    def system_default(self):
        return Nothing

    def to_primitive(self, value):
        return str(value)

    def from_primitive(self, value):
        return Path(value) if value else Nothing

    def from_string(self, value):
        return self.from_primitive(value)

    def to_string(self, value):
        return self.to_primitive(value)