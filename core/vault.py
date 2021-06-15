from napoleon.core.special.hidden import HiddenBytes
from napoleon.properties import MutableSingleton, AbstractObject, String

import os
from cryptography.fernet import Fernet
import hashlib
import base64


class Vault(AbstractObject, metaclass=MutableSingleton):

    key: bytes = HiddenBytes(Fernet.generate_key)

    @classmethod
    def from_password(cls, password: str,
                      salt="3pbXWxkVxUV7K5Uq1rGqhQ==",
                      iterations=1000000,
                      algorithm="sha256"):
        key = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac(algorithm,
                                                           password.encode(),
                                                           base64.urlsafe_b64decode(salt.encode()),
                                                           iterations,
                                                           dklen=32))
        return cls(key=key)

    @classmethod
    def from_base64_key(cls, base64_key):
        return cls(key=base64.urlsafe_b64decode(base64_key.encode()))

    @property
    def cipher(self):
        return Fernet(self.key)

    def decrypt(self, data):
        return self.cipher.decrypt(data.encode()).decode()

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()

    @staticmethod
    def generate_salt(salt_size=16):
        return base64.urlsafe_b64encode(os.urandom(salt_size)).decode()


class Secret(String):

    def from_string(self, value):
        return Vault().decrypt(value)

    def to_string(self, value):
        return Vault().encrypt(value)
