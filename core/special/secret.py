from napoleon.core.application import Application
from napoleon.properties import String


class Secret(String):

    def from_primitive(self, value): # noqa
        return Application().vault.decrypt(value)

    def to_primitive(self, value): # noqa
        return Application().vault.encrypt(value)
