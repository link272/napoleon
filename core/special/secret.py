from napoleon.core.application import Application
from napoleon.properties import String


class Secret(String):

    def from_string(self, value): # noqa
        return Application().vault.decrypt(value)

    def to_string(self, value): # noqa
        return Application().vault.encrypt(value)
