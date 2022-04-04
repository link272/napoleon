from napoleon.core.shared.application import Application
from napoleon.properties import String
from napoleon.tools.singleton import Undefined


class Secret(String):
    """
    secret field
    """
    __slots__ = ("vault_name",)

    def __init__(self, vault_name="default", description=Undefined):
        super().__init__(default=None,
                         description=description,
                         nullable=True)
        self.vault_name = vault_name

    def to_primitive(self, value):
        return Application().vault[self.vault_name].encrypt(value)

    def from_primitive(self, value):
        return Application().vault[self.vault_name].decrypt(value)
