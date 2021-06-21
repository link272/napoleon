from napoleon.core.application import app
from napoleon.properties import String


class Secret(String):

    def from_string(self, value): # noqa
        return app.vault.decrypt(value)

    def to_string(self, value): # noqa
        return app.vault.encrypt(value)
