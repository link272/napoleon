from ..tools.singleton import Nothing
from .base import Property


class Descriptor(Property):

    def __str__(self):
        return "@" + self.__class__.__name__.lower()

    def build_descriptor(self, name):
        raise NotImplementedError

    def system_default(self):
        return Nothing

    def to_string(self, value):
        raise NotImplementedError

    def from_string(self, value):
        raise NotImplementedError
