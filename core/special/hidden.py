from napoleon.properties import String, Bytes
from napoleon.tools.singleton import Nothing


class HiddenString(String):

    def to_string(self, value): # noqa
        return Nothing


class HiddenBytes(Bytes):

    def to_string(self, value): # noqa
        return Nothing

    def to_bytes(self, value): # noqa
        return Nothing
