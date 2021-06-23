from napoleon.core.abstract import AbstractVault


class OpenVault(AbstractVault):

    def decrypt(self, data):
        return data

    def encrypt(self, data):
        return data