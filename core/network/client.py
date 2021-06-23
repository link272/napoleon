from napoleon.core.special.secret import Secret
from napoleon.core.special.alias import Alias
from napoleon.properties import AbstractObject, String, Integer, Float, Instance, PlaceHolder
from napoleon.core.network.netloc import NetworkLocalization


class Client(NetworkLocalization):

    user = String()
    password = Secret()


class Interface(AbstractObject):

    client = Alias(Client)
