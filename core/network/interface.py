from napoleon.core.network.client import Client, CLIENTS
from napoleon.properties import AbstractObject, Alias


class Interface(AbstractObject):

    client = Alias(Client, CLIENTS)
