from napoleon.properties import AbstractObject


class BaseVault(AbstractObject):

    def decrypt(self, data):
        raise NotImplementedError

    def encrypt(self, data):
        raise NotImplementedError
