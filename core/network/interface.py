from napoleon.core.network.client import Client
from napoleon.properties import AbstractObject, Alias
from napoleon.core.application import Application


class Interface(AbstractObject):

    client = Alias(Client, lambda: Application().clients)
