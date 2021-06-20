from napoleon.core.network.client import Client
from napoleon.properties import AbstractObject, Alias
from napoleon.core.application import Application
from napoleon.core.interface.base import Interface


class Service(Interface):

    client = Alias(Client, lambda: Application().clients)
